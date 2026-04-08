# AI-Powered SQL Query Generator with Groq

This project is a web-based application that leverages Groq's fast inference capabilities to convert natural language questions into SQL queries. It provides a user-friendly interface to interact with your databases, generate queries, execute them, and receive optimization suggestions.

## Features

*   **Natural Language to SQL:** Convert plain English questions into complex SQL queries using Groq.
*   **Database Agnostic:** Connects to your MySQL database.
*   **Web-Based UI:** An intuitive interface built with Streamlit for easy interaction.
*   **API-Driven:** A robust backend built with FastAPI provides a clear separation of concerns and allows for other clients to be built on top of it.
*   **SQL Validation:** Ensures that the generated SQL is syntactically correct before execution.
*   **Query Optimization:** Provides suggestions for indexing to improve query performance.
*   **Database Schema Discovery:** Automatically discovers and uses the schema of your database to generate accurate queries.

## Project Architecture

The application is composed of two main parts:

1.  **Backend API (FastAPI):**
    *   Exposes endpoints for listing databases, tables, and columns.
    *   Handles the logic for generating SQL queries using Groq.
    *   Executes the generated queries against the database.
    *   Provides optimization suggestions.

2.  **Frontend UI (Streamlit):**
    *   A simple and interactive web interface.
    *   Allows users to input natural language queries.
    *   Displays the generated SQL query.
    *   Shows the results of the executed query in a clean, tabular format.

## Setup and Installation

To get the application up and running, follow these steps:

**1. Clone the Repository:**

```bash
git clone <repository-url>
cd ai-sql
```

**2. Create a Virtual Environment:**

It is recommended to use a virtual environment to manage the project's dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies:**

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables:**

Create a `.env` file in the root of the project directory and add the following environment variables. This file will store your database credentials and Groq API key.

```
MYSQL_USER="your_mysql_user"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_DATABASE="your_mysql_database"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"

GROQ_API_KEY="your_groq_api_key"
LLM_MODEL="llama3-70b-8192"
```

Replace the placeholder values with your actual credentials.

## Usage

The application consists of a backend server and a frontend UI. You'll need to run both to use the application.

**1. Run the Backend API:**

The backend is a FastAPI application. You can run it using `uvicorn`.

```bash
uvicorn app:app --reload --port 8001
```

The API will be available at `http://localhost:8001`.

**2. Run the Frontend UI:**

The frontend is a Streamlit application. Open a new terminal window and run the following command:

```bash
streamlit run ui.py
```

The user interface will be available at `http://localhost:8501`.

## API Endpoints

The FastAPI backend provides the following endpoints:

*   `GET /api/databases`: Lists all available databases.
*   `GET /api/databases/{database}/tables`: Lists all tables in a specified database.
*   `GET /api/tables/{table_name}/columns`: Lists all columns in a specified table.
*   `POST /api/generate`: Generates a SQL query from a natural language query.
*   `POST /api/validate`: Validates a SQL query.
*   `POST /api/execute`: Executes a SQL query and returns the results.
*   `POST /api/generate-and-execute`: Generates and executes a SQL query in one step.
*   `POST /api/explain`: Explains a SQL query in plain English.
*   `POST /api/optimize`: Provides optimization suggestions for a SQL query.
*   `GET /api/llm/info`: Returns information about the active LLM.
*   `GET /api/health`: Checks the health of the API.

## Technologies Used

*   **Backend:** FastAPI, Uvicorn
*   **Frontend:** Streamlit
*   **Database:** SQLAlchemy, MySQL Connector
*   **AI:** Groq
*   **Other:** python-dotenv, sqlparse

---

Developed by [Yash](https://www.linkedin.com/in/yash-tomar-sr-manager-technology-97380417)