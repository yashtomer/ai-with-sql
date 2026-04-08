from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from database import list_databases, get_table_names, get_columns
from query_generator import (
    generate_sql_query,
    validate_sql_query,
    suggest_index,
    execution_query,
    explain_query,
    SUPPORTED_PROVIDERS
)
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Initialize FastAPI app
app = FastAPI(
    title="SQL Query Generator",
    description="Natural language to SQL converter with runtime provider selection",
    version="2.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pydantic models
class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str

class QueryRequest(BaseModel):
    nl_query: str
    database: Optional[str] = None
    llm_config: Optional[LLMConfig] = None

class SQLExecuteRequest(BaseModel):
    sql_query: str
    llm_config: Optional[LLMConfig] = None

class QueryResponse(BaseModel):
    sql_query: str
    explanation: Optional[str] = None
    
class ExecutionResponse(BaseModel):
    results: List[Dict[str, Any]]
    row_count: int
    optimization_suggestion: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

def _llm_config_to_dict(llm_config: Optional[LLMConfig]) -> Optional[Dict[str, str]]:
    if llm_config is None:
        return None
    if hasattr(llm_config, "model_dump"):
        return llm_config.model_dump()
    return llm_config.dict()

# Database endpoints
@app.get("/api/databases")
def api_list_databases():
    """API endpoint to list all databases."""
    logger.debug("Listing all databases.")
    try:
        return list_databases()
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")

@app.get("/api/databases/{database}/tables")
def api_get_tables(database: str):
    """API endpoint to get table names in a specified database."""
    logger.debug(f"Fetching tables for database: {database}")
    try:
        return get_table_names(database)
    except Exception as e:
        logger.error(f"Error getting tables for database {database}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@app.get("/api/tables/{table_name}/columns")
def api_get_columns(table_name: str, database: Optional[str] = None): 
    """API endpoint to get columns in a specified table."""
    logger.debug(f"Fetching columns for table: {table_name} in database: {database}")
    try:
        return get_columns(table_name, database)
    except Exception as e:
        logger.error(f"Error getting columns for table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get columns: {str(e)}")

# Query generation endpoints
@app.post("/api/generate", response_model=QueryResponse)
def generate_query(request: QueryRequest):
    """Generate SQL query from natural language input with explanation."""
    logger.debug(f"Generating SQL for: {request.nl_query}")
    
    try:
        # Generate SQL query
        llm_config = _llm_config_to_dict(request.llm_config)
        sql_query = generate_sql_query(request.nl_query, request.database, llm_config)
        if not sql_query:
            raise HTTPException(
                status_code=400, 
                detail="Failed to generate SQL query. Please check your natural language input."
            )
        
        # Get explanation
        explanation = explain_query(sql_query, llm_config)
        
        return QueryResponse(
            sql_query=sql_query,
            explanation=explanation
        )
    
    except ValueError as e:
        logger.error(f"LLM configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"LLM runtime error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

@app.post("/api/validate")
def validate_query(request: SQLExecuteRequest):
    """Validate SQL query syntax."""
    logger.debug(f"Validating SQL query: {request.sql_query[:100]}...")
    
    try:
        is_valid, error_message = validate_sql_query(request.sql_query)
        return {
            "valid": is_valid,
            "error": error_message if not is_valid else None
        }
    except Exception as e:
        logger.error(f"Error validating SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/api/execute", response_model=ExecutionResponse)
def execute_query(request: SQLExecuteRequest):
    """Execute the SQL query and return results with optimization suggestions."""
    logger.debug(f"Executing SQL query: {request.sql_query[:100]}...")
    
    try:
        result = execution_query(request.sql_query, _llm_config_to_dict(request.llm_config))
        
        if result is None:
            raise HTTPException(
                status_code=400, 
                detail="Failed to execute SQL query. Please check the query syntax and database connection."
            )
        
        # Ensure proper JSON serialization
        serialized_results = []
        for row in result["results"]:
            if hasattr(row, '_mapping'):
                serialized_results.append(dict(row._mapping))
            elif hasattr(row, '_asdict'):
                serialized_results.append(row._asdict())
            else:
                # Handle different SQLAlchemy result types
                serialized_results.append(dict(row))
        
        return ExecutionResponse(
            results=serialized_results,
            row_count=len(serialized_results),
            optimization_suggestion=result["optimization_suggestion"]
        )
    
    except ValueError as e:
        logger.error(f"LLM configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"LLM runtime error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.post("/api/generate-and-execute", response_model=ExecutionResponse)
def generate_and_execute(request: QueryRequest):
    """Generate SQL from natural language and execute it in one step."""
    logger.debug(f"Generate and execute for: {request.nl_query}")
    
    try:
        llm_config = _llm_config_to_dict(request.llm_config)
        # Generate SQL query
        sql_query = generate_sql_query(request.nl_query, request.database, llm_config)
        if not sql_query:
            raise HTTPException(
                status_code=400, 
                detail="Failed to generate SQL query from natural language input."
            )
        
        # Execute the generated query
        result = execution_query(sql_query, llm_config)
        
        if result is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to execute generated SQL query: {sql_query}"
            )
        
        # Serialize results
        serialized_results = []
        for row in result["results"]:
            if hasattr(row, '_mapping'):
                serialized_results.append(dict(row._mapping))
            elif hasattr(row, '_asdict'):
                serialized_results.append(row._asdict())
            else:
                serialized_results.append(dict(row))
        
        return ExecutionResponse(
            results=serialized_results,
            row_count=len(serialized_results),
            optimization_suggestion=result["optimization_suggestion"]
        )
    
    except ValueError as e:
        logger.error(f"LLM configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate and execute: {e}")
        raise HTTPException(status_code=500, detail=f"Generate and execute failed: {str(e)}")

@app.post("/api/explain")
def explain_sql_query(request: SQLExecuteRequest):
    """Get plain English explanation of SQL query."""
    logger.debug(f"Explaining SQL query: {request.sql_query[:100]}...")
    
    try:
        explanation = explain_query(request.sql_query, _llm_config_to_dict(request.llm_config))
        return {"explanation": explanation}
    except ValueError as e:
        logger.error(f"LLM configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error explaining SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Query explanation failed: {str(e)}")

@app.post("/api/optimize")
def optimize_query(request: SQLExecuteRequest):
    """Get optimization suggestions for SQL query."""
    logger.debug(f"Getting optimization suggestions for: {request.sql_query[:100]}...")
    
    try:
        suggestions = suggest_index(request.sql_query, _llm_config_to_dict(request.llm_config))
        return {"optimization_suggestions": suggestions}
    except ValueError as e:
        logger.error(f"LLM configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization analysis failed: {str(e)}")

# System information endpoints
@app.get("/api/llm/info")
def llm_info():
    """Return supported runtime LLM providers."""
    try:
        return {
            "request_scoped": True,
            "default_provider": None,
            "default_model": None,
            "supported_providers": sorted(list(SUPPORTED_PROVIDERS))
        }
    except Exception as e:
        logger.error(f"Error getting LLM info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LLM info: {str(e)}")

@app.get("/api/health")
def health():
    """Health check for API availability."""
    try:
        return {
            "status": "ok",
            "llm_provider": None,
            "llm_model": None,
            "requires_runtime_config": True,
            "endpoints": {
                "generate": "/api/generate",
                "execute": "/api/execute",
                "validate": "/api/validate",
                "explain": "/api/explain",
                "optimize": "/api/optimize",
                "generate_and_execute": "/api/generate-and-execute"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "SQL Query Generator API (runtime LLM provider selection)",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/api/health",
        "llm_info": "/api/llm/info"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc)
        }
    )

# Uncomment to run directly
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
