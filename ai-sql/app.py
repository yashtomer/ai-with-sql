from fastapi import FastAPI
import logging
from database import list_databases, get_table_names, get_columns
from query_generator import generate_sql_query, execution_query
from fastapi import FastAPI, Query, HTTPException #Add Query here


from pydantic import BaseModel
from query_generator import generate_sql_query, validate_sql_query, suggest_index, execution_query

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)


#class QueryRequest(BaseModel):
#    nl_query: str


#API: List all databases
@app.get("/list_databases")
def api_list_databases():
    """API endpoint to list all databases."""
    logging.debug("Listing all databases.")
    return list_databases()

#API: Get table names in a database
@app.get("/get_tables/{database}")
def api_get_tables(database: str):
    """API endpoint to get table names in a specified database."""
    logging.debug(f"Fetching tables for database: {database}")
    return get_table_names(database)

#API: Get columns in a table
@app.get("/get_columns")
def api_get_columns(table_name: str, database: str = None): 
    """API endpoint to get columns in a specified table."""
    logging.debug(f"Fetching columns for table: {table_name} in database: {database}")
    return get_columns(table_name, database)    


class QueryRequest(BaseModel):
    nl_query: str
    database: str = None

@app.post("/generate_sql")
def generate_query(request: QueryRequest):
    """Generate SQL query from natural language input."""
    sql_query = generate_sql_query(request.nl_query, request.database)
    if not sql_query:
        return {"error": "Failed to generate SQL query."}
    return {"sql_query": sql_query} 

@app.post("/execute_sql")
def execute_query(request: QueryRequest):
    """Execute the SQL query and return results."""
    result = execution_query(request.nl_query)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to execute SQL query.")
    #Ensure proper json serialization
    serial_result = [dict(row._mapping) for row in result["results"]]
    
    return {"result": serial_result, "optimization_suggestion": result["optimization_suggestion"]}


# #Run the FastAPI app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    