import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from database import hash_password

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Admin user credentials
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_NAME = os.getenv("ADMIN_NAME")

def setup_database():
    if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
        logger.error("Missing database credentials in .env")
        return

    # Encode password for URL
    encoded_password = quote_plus(MYSQL_PASSWORD)
    
    # URL for creating the database if it doesn't exist
    BASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}"
    DATABASE_URL = f"{BASE_URL}/{MYSQL_DATABASE}"

    try:
        # Create database if it doesn't exist
        temp_engine = create_engine(BASE_URL)
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"))
            logger.info(f"Database '{MYSQL_DATABASE}' ensured.")
        
        # Connect to the specific database
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            conn.execute(text(create_users_table))
            logger.info("Users table ensured.")

            # Seed admin user
            if all([ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME]):
                # Check if user already exists
                check_user = text("SELECT id FROM users WHERE email = :email")
                result = conn.execute(check_user, {"email": ADMIN_EMAIL}).fetchone()

                if not result:
                    # Hash the password securely
                    hashed_password = hash_password(ADMIN_PASSWORD)
                    insert_user = text("""
                    INSERT INTO users (name, email, password) 
                    VALUES (:name, :email, :password)
                    """)
                    conn.execute(insert_user, {
                        "name": ADMIN_NAME,
                        "email": ADMIN_EMAIL,
                        "password": hashed_password
                    })
                    conn.commit()
                    logger.info(f"Admin user '{ADMIN_EMAIL}' seeded successfully with a secure hashed password.")
                else:
                    # If the admin user exists, verify if their password is raw and migrate it to a secure hash if so
                    get_pw = text("SELECT password FROM users WHERE email = :email")
                    current_pw = conn.execute(get_pw, {"email": ADMIN_EMAIL}).fetchone()[0]
                    if not current_pw.startswith("pbkdf2_sha256$"):
                        hashed_password = hash_password(ADMIN_PASSWORD)
                        update_pw = text("UPDATE users SET password = :password WHERE email = :email")
                        conn.execute(update_pw, {
                            "password": hashed_password,
                            "email": ADMIN_EMAIL
                        })
                        conn.commit()
                        logger.info(f"Existing admin user '{ADMIN_EMAIL}' password successfully migrated to a secure hash.")
                    else:
                        logger.info(f"Admin user '{ADMIN_EMAIL}' already exists with a secure hashed password.")
            else:
                logger.warning("Admin credentials not found in .env. Skipping seeding.")

    except Exception as e:
        logger.error(f"Setup failed: {e}")

if __name__ == "__main__":
    setup_database()
