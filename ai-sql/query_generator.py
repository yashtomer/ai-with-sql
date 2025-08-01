import os 
import openai
import sqlparse
import re
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, list_databases, get_table_names, get_columns

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

#Limit to avoid excessive token usage
MAX_TABLES = 10
MAX_COLUMN_PER_TABLE = 10


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
        tables = get_table_names(database).get("tables", [])
        for table in tables:
            columns = get_columns(table, database).get("columns", [])
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
    You are an expert SQL query generator for a MySQL database. Your primary goal is to accurately translate natural language requests into optimized SQL queries, strictly adhering to the provided database schema.

    Key Guidelines:
    - Always use the most appropriate table for the requested data. For example, if the user asks about 'users', refer to the 'users' table.
    - For questions like "How many X?", use COUNT(*) on the relevant table.
    - Ensure SQL is valid, optimized, and uses efficient joins.
    - Do NOT include any explanations or additional text, only the SQL query.

    Database Schema:
    {schema_text}

    Examples:
    User Request: How many total users are registered?
    SQL Query: SELECT COUNT(*) AS total_registered_users FROM users;

    User Request: {nl_query}
    SQL Query:
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL query generation expert. Only respond with the SQL query."},
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