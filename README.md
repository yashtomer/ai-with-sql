# AI-Powered SQL Query Generator (Aeologic Edition)

This project is a sophisticated enterprise-grade solution that leverages Large Language Models (LLMs) to convert natural language questions into precise SQL queries. Featuring a high-fidelity "Dark Luxe" React interface and a robust FastAPI backend, it enables seamless interaction with MySQL databases through plain English.

## 🚀 Key Features

*   **Natural Language to SQL:** Effortlessly transform complex questions into optimized SQL.
*   **Dynamic AI Configuration:** Switch between providers (**OpenAI, Groq, Gemini, Anthropic**) and models at runtime via the UI.
*   **High-Fidelity React UI:** A premium, responsive dashboard built with Vite, React, and Framer Motion.
*   **Database Schema Discovery:** Automatically maps your database schema to ensure accurate query generation.
*   **One-Step Execution:** Generate and execute queries in a single click with real-time result visualization.
*   **Performance Insights:** Receive AI-driven optimization suggestions for every query executed.

## 🏗️ Project Architecture

1.  **Backend (`/ai-sql`):** 
    *   **FastAPI:** High-performance Python backend managing LLM bridges and database connections.
    *   **SQLAlchemy:** Secure ORM for database introspection and query execution.
2.  **Frontend (`/frontend`):**
    *   **React + Vite:** Modern, ultra-fast frontend framework.
    *   **TailwindCSS:** Premium styling with a custom "Dark Luxe" design system.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   MySQL Server
*   PM2 (Global: `npm install -g pm2`)

### 1. Backend Setup
```bash
cd ai-sql
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file in `/ai-sql`:
```env
MYSQL_USER="your_user"
MYSQL_PASSWORD="your_password"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env` file in `/frontend`:
```env
VITE_API_BASE_URL="http://localhost:8080"
```

---

## 🌐 Production Deployment with PM2

PM2 is the recommended process manager for maintaining both the backend and frontend in a production environment.

### 1. Deploy Backend
From the root directory:
```bash
cd ai-sql
pm2 start ecosystem.config.cjs
```
The backend will run on `http://localhost:8080`.

### 2. Deploy Frontend
First, create a production build:
```bash
cd frontend
npm run build
```
Then, start the frontend server using PM2:
```bash
pm2 start ecosystem.config.cjs
```
The frontend will be served on `http://localhost:5173` (or your configured port).

### 3. Monitoring
Use these commands to manage your services:
```bash
pm2 status          # View running processes
pm2 logs            # View real-time logs
pm2 restart all     # Restart both services
pm2 stop all        # Stop all services
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/databases` | List all available databases |
| `GET` | `/api/databases/{db}/tables` | List tables in a specific database |
| `POST` | `/api/generate` | Generate SQL from NL with explanation |
| `POST` | `/api/execute` | Execute SQL and return results |
| `POST` | `/api/generate-and-execute` | One-step NL to Results |
| `GET` | `/api/health` | System health and LLM info |

---

## 🛠️ Technologies Used

*   **Backend:** FastAPI, SQLAlchemy, Uvicorn, PM2
*   **Frontend:** React, Vite, Framer Motion, Lucide Icons, TailwindCSS
*   **AI:** OpenAI-compatible API Bridge (Supports multi-provider configuration)

---

Developed with ❤️ by [Yash(Aeologic)](https://www.linkedin.com/in/yash-tomar-sr-manager-technology-97380417)
