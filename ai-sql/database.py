import hashlib
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

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256 and a random salt."""
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${pw_hash.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (supporting PBKDF2 and raw fallback)."""
    if not hashed_password:
        return False
    
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed_password.split('$')
            if len(parts) == 4:
                _, iterations, salt_hex, hash_hex = parts
                iterations = int(iterations)
                salt = bytes.fromhex(salt_hex)
                pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
                return pw_hash.hex() == hash_hex
        except Exception as e:
            logging.error(f"Error verifying password hash: {e}")
            return False
            
    return hashed_password == password

# Function to verify user credentials
def verify_user(email, password):
    try:
        with engine.connect() as connection:
            query = text("SELECT id, name, email, password FROM users WHERE email = :email")
            result = connection.execute(query, {"email": email}).fetchone()
            
            if result:
                db_id, db_name, db_email, db_password = result
                if verify_password(password, db_password):
                    return {
                        "id": db_id,
                        "name": db_name,
                        "email": db_email
                    }
            return None
    except Exception as e:
        logging.error(f"Error verifying user: {e}")
        return None






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
