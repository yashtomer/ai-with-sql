import os
import sqlparse
import re
import requests
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, list_databases, get_table_names, get_columns

load_dotenv()

# Limit to avoid excessive token usage (66k token overhead issue)
MAX_TABLES = 15
MAX_COLUMN_PER_TABLE = 30
SUPPORTED_PROVIDERS = {"openai", "groq", "gemini", "anthropic"}


def clean_sql_output(sql):
    """Remove markdown formatting and extract the raw SQL query."""

    # Remove markdown code block formatting
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", sql, flags=re.DOTALL)
    clean_query = re.sub(r"```\n(.*?)\n```", r"\1", clean_query, flags=re.DOTALL)

    # Extract only valid SQL (handle AI explanations)
    sql_match = re.search(r"SELECT .*?;", clean_query, re.DOTALL | re.IGNORECASE)

    return sql_match.group(0) if sql_match else clean_query.strip()

def get_limited_schema(database=None, nl_query=None):
    """Get a limited schema prioritizing query-relevant tables."""
    schema = {}
    databases = [database] if database else list_databases().get("databases", [])
    
    # Exclude massive system databases that balloon the token size
    system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
    databases = [db for db in databases if db not in system_dbs]

    total_tables_added = 0

    for db in databases:
        if total_tables_added >= MAX_TABLES:
            break
            
        schema[db] = {}
        tables = get_table_names(db).get("tables", [])
        
        if nl_query:
            query_lower = nl_query.lower()
            # Prioritize tables whose exact name or space-replaced name appears in query
            matched = [t for t in tables if t.lower() in query_lower or t.replace('_', ' ').lower() in query_lower]
            unmatched = [t for t in tables if t not in matched]
            tables = matched + unmatched

        for table in tables:
            if total_tables_added >= MAX_TABLES:
                break
                
            columns = get_columns(table, db).get("columns", [])
            # Filter out standard boilerplate columns to save tokens
            ignored_cols = {'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by'}
            columns = [c for c in columns if c.lower() not in ignored_cols][:MAX_COLUMN_PER_TABLE]
            
            schema[db][table] = columns
            total_tables_added += 1

    return schema

def validate_sql_query(sql):
    """Validate the SQL query syntax before execution."""
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
           return False, "Invalid SQL syntax."
        return True, None
    except Exception as e:
        return False, str(e)

def _require_llm_config(llm_config):
    """Validate runtime LLM configuration sent from UI."""
    if not llm_config:
        raise ValueError("Please update API key, provider, and model in the UI.")

    provider = (llm_config.get("provider") or "").strip().lower()
    model = (llm_config.get("model") or "").strip()
    api_key = (llm_config.get("api_key") or "").strip()

    if not provider or not model or not api_key:
        raise ValueError("Please update API key, provider, and model in the UI.")

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'. Supported providers: OpenAI, Groq, Gemini, Anthropic.")

    return {
        "provider": provider,
        "model": model,
        "api_key": api_key
    }

def _call_llm(system_prompt, user_prompt, llm_config, temperature=0.2, max_tokens=512, top_p=0.95):
    """Call the configured LLM provider and return plain text."""
    cfg = _require_llm_config(llm_config)
    provider = cfg["provider"]
    model = cfg["model"]
    api_key = cfg["api_key"]

    if provider == "groq":
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        return response.choices[0].message.content.strip()

    if provider == "openai":
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        return response.choices[0].message.content.strip()

    if provider == "anthropic":
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            },
            timeout=45
        )
        response.raise_for_status()
        payload = response.json()
        parts = payload.get("content", [])
        text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        return "\n".join([t for t in text_parts if t]).strip()

    if provider == "gemini":
        combined_prompt = f"System instructions:\n{system_prompt}\n\nUser request:\n{user_prompt}"
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            headers={"content-type": "application/json"},
            json={
                "contents": [{"parts": [{"text": combined_prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            },
            timeout=45
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join([p.get("text", "") for p in parts if p.get("text")]).strip()

    raise ValueError(f"Unsupported provider '{provider}'.")

def generate_sql_query(nl_query, database=None, llm_config=None):
    """Convert natural language query to an optimized SQL query."""
    schema = get_limited_schema(database, nl_query)

    schema_text = "\n".join([f"{db}.{table}: {', '.join(columns)}" for db, tables in schema.items() for table, columns in tables.items()])

    # Enhanced prompt for better SQL generation
    system_prompt = """You are an expert SQL query generator specialized in creating optimized, production-ready SQL queries. 
    
    Guidelines:
    - Generate only valid, executable SQL
    - Use proper indexing strategies
    - Prefer JOINs over subqueries when possible
    - Use appropriate aggregate functions and GROUP BY
    - Include proper WHERE clause filtering
    - Return only the SQL query without explanations
    - End queries with semicolon"""

    user_prompt = f"""Database Schema:
{schema_text}

Convert this natural language request to an optimized SQL query:
{nl_query}

Return only the SQL query:"""

    try:
        raw_sql_query = _call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm_config=llm_config,
            temperature=0.1,  # Low temperature for more consistent SQL generation
            max_tokens=1024,
            top_p=0.95
        )

        # Clean the response to extract the SQL query
        clean_sql = clean_sql_output(raw_sql_query)
        if not clean_sql:
            raise RuntimeError("LLM returned an empty response. Check provider, model, and API key.")
        return clean_sql
    
    except ValueError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"LLM request failed: {str(e)}")

def suggest_index(sql, llm_config=None):
    """Suggest indexes for the given SQL query."""
    
    try:
        with engine.connect() as connection:
            explain_query = f"EXPLAIN {sql}"
            result = connection.execute(text(explain_query))
            execution_plan = result.fetchall()

        print("\nExecution Plan:")
        for row in execution_plan:
            print(row)

        # Enhanced index suggestion using selected provider
        return generate_index_suggestions(sql, execution_plan, llm_config)
    except ValueError:
        raise
    except Exception as e:
        return f"Could not generate execution plan: {e}"

def generate_index_suggestions(sql, execution_plan=None, llm_config=None):
    """Generate index suggestions using configured LLM based on the SQL query."""
    
    system_prompt = """You are a database optimization expert. Analyze SQL queries and suggest appropriate indexes to improve performance.
    
    Focus on:
    - WHERE clause columns
    - JOIN columns
    - ORDER BY columns
    - GROUP BY columns
    - Foreign key relationships"""

    plan_text = "\n".join([str(row) for row in execution_plan]) if execution_plan else "No execution plan available"
    
    user_prompt = f"""SQL Query:
{sql}

Execution Plan:
{plan_text}

Suggest specific indexes to improve this query's performance. Return only the index suggestions:"""

    try:
        return _call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm_config=llm_config,
            temperature=0.2,
            max_tokens=512
        )
    except ValueError:
        raise
    except Exception as e:
        return f"Could not generate index suggestions: {e}"
    
def execution_query(sql, llm_config=None):
    """Execute a validated and optimized SQL query."""
    
    is_valid, error = validate_sql_query(sql)
    if not is_valid:
        print(f"Invalid SQL query: {error}")
        return None
    
    try:
        # Open a separate connection for query execution
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            fetched_results = result.fetchall()

        # Open a new connection for query optimization (avoid "command out of sync" error)
        index_suggestion = suggest_index(sql, llm_config)

        return {
            "results": fetched_results,
            "optimization_suggestion": index_suggestion
        }
    except SQLAlchemyError as e:
        print(f"Error executing SQL query: {e}")
        return None

def explain_query(sql, llm_config=None):
    """Get detailed explanation of what the SQL query does using configured LLM."""
    
    system_prompt = """You are a SQL expert. Explain what SQL queries do in plain English, breaking down each part of the query."""
    
    user_prompt = f"""Explain this SQL query in simple terms:
{sql}

Break down:
- What data it retrieves
- Which tables it uses
- Any joins or conditions
- What the result will look like"""

    try:
        return _call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm_config=llm_config,
            temperature=0.3,
            max_tokens=512
        )
    except ValueError:
        raise
    except Exception as e:
        return f"Could not explain query: {e}"
    
if __name__ == "__main__":
    # Example usage
    nl_query = "Get all users with their email addresses and the number of orders they have made."
    
    print("Generating SQL query...")
    sql_query = generate_sql_query(nl_query)
    
    if sql_query:
        print(f"\nGenerated SQL Query:\n{sql_query}")
        
        # Get explanation
        explanation = explain_query(sql_query)
        print(f"\nQuery Explanation:\n{explanation}")
        
        # Execute query
        execution_result = execution_query(sql_query)
        
        if execution_result:
            print(f"\nExecution Results ({len(execution_result['results'])} rows):")
            for i, row in enumerate(execution_result["results"][:5]):  # Show first 5 rows
                print(f"  {i+1}: {row}")
            
            if len(execution_result["results"]) > 5:
                print(f"  ... and {len(execution_result['results']) - 5} more rows")
                
            print(f"\nOptimization Suggestions:\n{execution_result['optimization_suggestion']}")
        else:
            print("Failed to execute the SQL query.")
    else:
        print("Failed to generate SQL query.")
