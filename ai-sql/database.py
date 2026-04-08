from multiprocessing import context
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)


MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")  


# Encode the password for the URL
encoded_password = quote_plus(MYSQL_PASSWORD)


# Construct the database URL
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"


print(f"Connected to database: {DATABASE_URL}")

# Create the SQLAlchemy engine
try:
    logging.debug(f"Connecting to database at {MYSQL_HOST}:{MYSQL_PORT} as user {MYSQL_USER}")
    logging.debug(f"Using database: {MYSQL_DATABASE}")
    engine = create_engine(DATABASE_URL, echo=True)
    logging.info("Database engine created successfully.")
except Exception as e:
    logging.error(f"Error creating database engine: {e}")
    exit()

# Function to list databases
def list_databases():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES;")).fetchall()
            return {"databases": [row[0] for row in result]}
    except Exception as e:
        logging.error(f"Error fetching databases: {e}")
        return {"error": str(e)}

# Function to get the current table names
def get_table_names(database=None):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SHOW TABLES FROM {database};")).fetchall()
            return {"tables": [row[0] for row in result]}
    except Exception as e:
        logging.error(f"Error fetching table names: {e}")
        return {"error": str(e)}
    
# Function to LIST ALL columns in a table
def get_columns(table_name, database=None):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SHOW COLUMNS FROM `{table_name}` FROM `{database}`;")).fetchall()
            return {"columns": [row[0] for row in result]}
    except Exception as e:
        logging.error(f"Error fetching columns for table {table_name}: {e}")
        return {"error": str(e)}    






# Function to test connection
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE();"))
            print(f"Connected to database: {result.fetchone()[0]}")
    except Exception as e:
        print(f"Error connecting to database: {e}")



if __name__ == "__main__":
   test_connection()
