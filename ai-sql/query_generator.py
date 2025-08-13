import os 
from groq import Groq
import sqlparse
import re
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, list_databases, get_table_names, get_columns

load_dotenv()

# Configure Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Use a model that's good at code/SQL generation - Llama models work well for SQL
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")  # or "mixtral-8x7b-32768", "llama3-8b-8192"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

#Limit to avoid excessive token usage
MAX_TABLES = 50
MAX_COLUMN_PER_TABLE = 100


def clean_sql_output(sql):
    """Remove markdown formatting and extract the raw SQL query."""

    # Remove markdown code block formatting
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", sql, flags=re.DOTALL)
    clean_query = re.sub(r"```\n(.*?)\n```", r"\1", clean_query, flags=re.DOTALL)

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
    """Convert natural language query to an optimized SQL query using Groq"""
    schema = get_limited_schema(database)

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
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for more consistent SQL generation
            max_tokens=1024,
            top_p=0.95
        )
        raw_sql_query = response.choices[0].message.content.strip()

        # Clean the response to extract the SQL query
        clean_sql = clean_sql_output(raw_sql_query) 
        return clean_sql
    
    except Exception as e:
        print(f"Error generating SQL query with Groq: {e}")
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

        # Enhanced index suggestion using Groq
        return generate_index_suggestions(sql, execution_plan)
    except Exception as e:
        return f"Could not generate execution plan: {e}"

def generate_index_suggestions(sql, execution_plan=None):
    """Generate index suggestions using Groq based on the SQL query."""
    
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
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate index suggestions: {e}"
    
def execution_query(sql):
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
        index_suggestion = suggest_index(sql)

        return {
            "results": fetched_results,
            "optimization_suggestion": index_suggestion
        }
    except SQLAlchemyError as e:
        print(f"Error executing SQL query: {e}")
        return None

def explain_query(sql):
    """Get detailed explanation of what the SQL query does using Groq."""
    
    system_prompt = """You are a SQL expert. Explain what SQL queries do in plain English, breaking down each part of the query."""
    
    user_prompt = f"""Explain this SQL query in simple terms:
{sql}

Break down:
- What data it retrieves
- Which tables it uses
- Any joins or conditions
- What the result will look like"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
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