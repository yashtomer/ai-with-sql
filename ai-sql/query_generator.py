import os 
from openai import OpenAI
import sqlparse
import re
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, list_databases, get_table_names, get_columns

load_dotenv()

# Configure OpenAI-compatible client (supports OpenAI, Ollama, LM Studio, etc.)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Default to Together AI (OpenAI-compatible) so we use an open-source model hosted in the cloud by default
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.together.xyz/v1")
# Default open-source instruct model name (Together naming). Override via LLM_MODEL env if desired
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Always construct the client with an explicit base_url for consistency across providers
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

#Limit to avoid excessive token usage
MAX_TABLES = 5
MAX_COLUMN_PER_TABLE = 5


def clean_sql_output(sql):
    """Remove markdown formatting and extract the raw SQL query."""

    # Remove markdown code block formatting
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", sql, flags=re.DOTALL)

    # Extract only valid SQL (handle AI explanations)
    sql_match = re.search(r"SELECT .*?;", clean_query, re.DOTALL | re.IGNORECASE)

    return sql_match.group(0) if sql_match else clean_query.strip()

def get_limited_schema(database=None):
    """Get a limited schema with a maximum number of tables and columns."""
    schema = {}
    databases = [database] if database else list_databases().get("databases", [])

    for database in databases:
        schema[database] = {}
        tables = get_table_names(database).get("tables", [])[:MAX_TABLES]
        for table in tables:
            columns = get_columns(table, database).get("columns", [])[:MAX_COLUMN_PER_TABLE]
            schema[database][table] = columns

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

def generate_sql_query(nl_query, database=None):
    """Convert natural language query to an optimized SQL query"""
    schema = get_limited_schema(database)

    schema_text = "\n".join([f"{db}.{table}: {', '.join(columns)}" for db, tables in schema.items() for table, columns in tables.items()])

    prompt = f"""
    You are an expert SQL query generator. Convert the following user request into an optimized SQL query.
    Ensure:
      - Proper use of indexing where applicable.
      - Use of efficient joins instead of nested queries.
      - Use GROUP BY when aggregating are needed.
      - Ensure SQL is valid and optimized for execution.
    
    Database Schema:
    {schema_text}

    User Request: {nl_query}

    SQL Query:
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a SQL optimization expert."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_sql_query = response.choices[0].message.content.strip()

        # Clean the response to extract the SQL query
        clean_sql = clean_sql_output(raw_sql_query) 
        return clean_sql
    
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None

def suggest_index(sql):
    """Suggest indexes for the given SQL query."""
    
    try:
        with engine.connect() as connection:
            explain_query = f"EXPLAIN {sql}"
            result = connection.execute(text(explain_query))
            execution_plan = result.fetchall()

        print("\nExecution Plan:")
        for row in execution_plan:
            print(row)

        return "Consider adding indexe on frequenty used WHERE condition."
    except Exception as e:
        return (f"Could not generate execution plan : {e}")
    
def execution_query(sql):
    """Execute a validate and optimized SQL query."""
    
    is_valid, error = validate_sql_query(sql)
    if not is_valid:
        print(f"Invalid SQL query: {error}")
        return None
    
    try:
        # Open a separate connection for query execution
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            fetched_results = result.fetchall()

        #Open a new connection for query optimization (avoid "command out of sync" error)
        index_suggestion = suggest_index(sql)

        return {
            "results": fetched_results,
            "optimization_suggestion": index_suggestion
        }
    except SQLAlchemyError as e:
        print(f"Error executing SQL query: {e}")
        return None
    
if __name__ == "__main__":
    # Example usage
    nl_query = "Get all users with their email addresses and the number of orders they have made."
    sql_query = generate_sql_query(nl_query)
    
    if sql_query:
        print(f"Generated SQL Query: {sql_query}")
        
        execution_result = execution_query(sql_query)
        
        if execution_result:
            print("Execution Results:")
            for row in execution_result["results"]:
                print(row)
            print("Optimization Suggestion:", execution_result["optimization_suggestion"])
        else:
            print("Failed to execute the SQL query.")
    else:
        print("Failed to generate SQL query.")