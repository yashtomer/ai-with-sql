import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time

# Configuration
API_URL = "http://localhost:8080"  # Update with your FastAPI URL

# Set page configuration
st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = None
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = ""
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = ""
if 'llm_api_key' not in st.session_state:
    st.session_state.llm_api_key = ""

# Helper functions
def make_api_request(endpoint, method="GET", data=None, timeout=30):
    """Make API request with error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return None, "Request timeout. Please check if the API server is running."
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Please check if the API server is running."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def add_to_history(nl_query, sql_query, success=True):
    """Add query to history"""
    st.session_state.query_history.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'nl_query': nl_query,
        'sql_query': sql_query,
        'success': success
    })
    # Keep only last 10 queries
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[-10:]

def get_runtime_llm_config():
    """Return runtime LLM config from current Streamlit session."""
    provider = (st.session_state.llm_provider or "").strip().lower()
    model = (st.session_state.llm_model or "").strip()
    api_key = (st.session_state.llm_api_key or "").strip()

    if not provider or not model or not api_key:
        return None

    return {
        "provider": provider,
        "model": model,
        "api_key": api_key
    }

def require_llm_config():
    """Enforce runtime LLM configuration before AI calls."""
    llm_config = get_runtime_llm_config()
    if not llm_config:
        st.error("Please update API key, provider, and model in AI Provider Settings.")
        return None
    return llm_config

# Main title
st.markdown('<h1 class="main-header">🚀 AI SQL Query Generator</h1>', unsafe_allow_html=True)
st.markdown("Configure your own provider and API key for this session only.")
st.markdown("Supported: OpenAI, Groq, Gemini, Anthropic")

# API Health Check
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Check API Status", key="health_check"):
            with st.spinner("Checking API health..."):
                health_data, error = make_api_request("/api/health")
                if health_data:
                    if health_data.get("status") == "ok":
                        st.markdown(f'<div class="success-box">✅ API is healthy and ready!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ API issues detected</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Cannot connect to API: {error}</div>', unsafe_allow_html=True)

# LLM Runtime Configuration
with st.expander("🤖 AI Provider Settings", expanded=True):
    provider_options = ["None", "OpenAI", "Groq", "Gemini", "Anthropic"]
    model_options_map = {
        "OpenAI": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "gpt-4o"],
        "Groq": ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
        "Gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "Anthropic": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-latest"]
    }

    current_provider_label = next(
        (label for label in provider_options if label.lower() == (st.session_state.llm_provider or "").lower()),
        "None"
    )

    selected_provider_label = st.selectbox(
        "Provider",
        provider_options,
        index=provider_options.index(current_provider_label),
        key="provider_selector"
    )

    provider_models = model_options_map.get(selected_provider_label, [])
    default_model_value = st.session_state.llm_model or (provider_models[0] if provider_models else "")

    selected_model = st.selectbox(
        "Model",
        options=provider_models + ["Custom"],
        index=0 if default_model_value in provider_models else (len(provider_models) if provider_models else 0),
        key="model_selector"
    ) if selected_provider_label != "None" else "Custom"

    custom_model = st.text_input(
        "Custom Model (optional)",
        value=default_model_value if selected_model == "Custom" else "",
        placeholder="Enter model id if not listed",
        key="custom_model_input"
    )

    entered_api_key = st.text_input(
        "API Key",
        value=st.session_state.llm_api_key,
        type="password",
        placeholder="Paste API key for selected provider",
        key="api_key_input"
    )

    save_col, clear_col = st.columns(2)
    with save_col:
        if st.button("💾 Save Session Config"):
            provider_value = "" if selected_provider_label == "None" else selected_provider_label.lower()
            model_value = custom_model.strip() if selected_model == "Custom" else selected_model
            st.session_state.llm_provider = provider_value
            st.session_state.llm_model = model_value
            st.session_state.llm_api_key = entered_api_key.strip()

            if get_runtime_llm_config():
                st.success("AI configuration saved for this session.")
            else:
                st.warning("Configuration cleared. Add provider, model, and API key to enable AI features.")

    with clear_col:
        if st.button("🧹 Clear Session Config"):
            st.session_state.llm_provider = ""
            st.session_state.llm_model = ""
            st.session_state.llm_api_key = ""
            st.success("Session AI configuration removed.")

    active_config = get_runtime_llm_config()
    if active_config:
        st.info(f"Active: {active_config['provider'].title()} • {active_config['model']}")
    else:
        st.warning("No AI provider configured. Generate/Explain/Optimize actions will fail until you save one.")

# Sidebar for database exploration
st.sidebar.header("🗄️ Database Explorer")

# Database listing
if st.sidebar.button("📋 List All Databases"):
    with st.spinner("Fetching databases..."):
        db_data, error = make_api_request("/api/databases")
        if db_data:
            databases = db_data.get("databases", [])
            st.sidebar.success(f"Found {len(databases)} database(s)")
            for db in databases:
                st.sidebar.write(f"• {db}")
        else:
            st.sidebar.error(f"Failed to fetch databases: {error}")

# Database selection
selected_database = st.sidebar.text_input("🎯 Enter Database Name", value="", placeholder="e.g., myapp_db")

if selected_database:
    # Table listing
    if st.sidebar.button("📊 List Tables"):
        with st.spinner("Fetching tables..."):
            table_data, error = make_api_request(f"/api/databases/{selected_database}/tables")
            if table_data:
                tables = table_data.get("tables", [])
                st.sidebar.success(f"Found {len(tables)} table(s)")
                for table in tables:
                    st.sidebar.write(f"• {table}")
            else:
                st.sidebar.error(f"Failed to fetch tables: {error}")

    # Table selection and column exploration
    selected_table = st.sidebar.text_input("🎯 Enter Table Name", value="", placeholder="e.g., users")
    
    if selected_table:
        if st.sidebar.button("🔍 Show Columns"):
            with st.spinner("Fetching columns..."):
                column_data, error = make_api_request(f"/api/tables/{selected_table}/columns?database={selected_database}")
                if column_data:
                    columns = column_data.get("columns", [])
                    st.sidebar.success(f"Found {len(columns)} column(s)")
                    for column in columns:
                        st.sidebar.write(f"• {column}")
                else:
                    st.sidebar.error(f"Failed to fetch columns: {error}")

# Main query interface
st.header("💬 Natural Language Query")

# Query input with example
query_input = st.text_area(
    "Enter your natural language query:",
    height=100,
    placeholder="Example: Get all users who placed orders in the last 30 days with their total order amount",
    help="Describe what data you want to retrieve in plain English"
)

# Quick example queries
st.subheader("🎯 Quick Examples")
example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    if st.button("👥 User Statistics"):
        query_input = "Show me the total number of users and their average age"
        st.rerun()

with example_col2:
    if st.button("📈 Sales Report"):
        query_input = "Get top 10 products by sales revenue this month"
        st.rerun()

with example_col3:
    if st.button("🔍 Recent Activity"):
        query_input = "Find all orders placed in the last 7 days with customer details"
        st.rerun()

# Query generation and execution
if st.button("✨ Generate SQL Query", key="generate_btn"):
    if query_input.strip():
        llm_config = require_llm_config()
        if not llm_config:
            st.stop()

        with st.spinner("🤖 AI is crafting your SQL query..."):
            start_time = time.time()
            
            request_data = {
                "nl_query": query_input,
                "database": selected_database if selected_database else None,
                "llm_config": llm_config
            }
            
            response_data, error = make_api_request("/api/generate", "POST", request_data)
            
            if response_data:
                execution_time = time.time() - start_time
                st.session_state.generated_sql = response_data.get("sql_query", "")
                explanation = response_data.get("explanation", "")
                
                st.markdown(f'<div class="success-box">✅ SQL generated in {execution_time:.2f} seconds!</div>', unsafe_allow_html=True)
                
                # Display generated SQL
                st.subheader("🔧 Generated SQL Query")
                st.code(st.session_state.generated_sql, language='sql')
                
                # Display explanation
                if explanation:
                    st.subheader("📝 Query Explanation")
                    st.markdown(f'<div class="info-box">{explanation}</div>', unsafe_allow_html=True)
                
                # Add to history
                add_to_history(query_input, st.session_state.generated_sql, True)
                
            else:
                st.markdown(f'<div class="error-box">❌ Failed to generate SQL: {error}</div>', unsafe_allow_html=True)
                add_to_history(query_input, "", False)
    else:
        st.warning("⚠️ Please enter a natural language query first.")

# SQL execution section
if st.session_state.generated_sql:
    st.header("⚡ Execute Query")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Execute Query", key="execute_btn"):
            llm_config = require_llm_config()
            if not llm_config:
                st.stop()

            with st.spinner("🔍 Executing query..."):
                request_data = {
                    "sql_query": st.session_state.generated_sql,
                    "llm_config": llm_config
                }
                result_data, error = make_api_request("/api/execute", "POST", request_data)
                
                if result_data:
                    st.session_state.last_results = result_data
                    results = result_data.get("results", [])
                    row_count = result_data.get("row_count", 0)
                    optimization = result_data.get("optimization_suggestion", "")
                    
                    st.markdown(f'<div class="success-box">✅ Query executed successfully! Found {row_count} row(s)</div>', unsafe_allow_html=True)
                    
                else:
                    st.markdown(f'<div class="error-box">❌ Execution failed: {error}</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🔍 Validate Query", key="validate_btn"):
            with st.spinner("Validating SQL syntax..."):
                request_data = {"sql_query": st.session_state.generated_sql}
                validation_data, error = make_api_request("/api/validate", "POST", request_data)
                
                if validation_data:
                    if validation_data.get("valid"):
                        st.markdown('<div class="success-box">✅ SQL syntax is valid!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ SQL syntax error: {validation_data.get("error")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Validation failed: {error}</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🎯 One-Step Execute", key="onestep_btn"):
            llm_config = require_llm_config()
            if not llm_config:
                st.stop()

            with st.spinner("🚀 Generating and executing..."):
                request_data = {
                    "nl_query": query_input,
                    "database": selected_database if selected_database else None,
                    "llm_config": llm_config
                }
                result_data, error = make_api_request("/api/generate-and-execute", "POST", request_data)
                
                if result_data:
                    st.session_state.last_results = result_data
                    results = result_data.get("results", [])
                    row_count = result_data.get("row_count", 0)
                    
                    st.markdown(f'<div class="success-box">✅ Generated and executed! Found {row_count} row(s)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ One-step execution failed: {error}</div>', unsafe_allow_html=True)

# Results display
if st.session_state.last_results:
    results = st.session_state.last_results.get("results", [])
    row_count = st.session_state.last_results.get("row_count", 0)
    optimization = st.session_state.last_results.get("optimization_suggestion", "")
    
    st.header("📊 Query Results")
    
    if results:
        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", row_count)
        with col2:
            st.metric("Columns", len(results[0].keys()) if results else 0)
        with col3:
            st.metric("Data Size", f"{len(str(results))} bytes")
        
        # Results table
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download option
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data returned from the query.")
    
    # Optimization suggestions
    if optimization:
        st.subheader("🚀 Performance Optimization")
        st.markdown(f'<div class="info-box"><strong>Suggestions:</strong><br>{optimization}</div>', unsafe_allow_html=True)

# Query History
with st.expander("📚 Query History", expanded=False):
    if st.session_state.query_history:
        for i, query in enumerate(reversed(st.session_state.query_history)):
            status_icon = "✅" if query['success'] else "❌"
            st.markdown(f"**{status_icon} {query['timestamp']}**")
            st.markdown(f"**Query:** {query['nl_query']}")
            if query['sql_query']:
                st.code(query['sql_query'], language='sql')
            st.markdown("---")
    else:
        st.info("No query history yet. Generate some queries to see them here!")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using **Streamlit** • "
    "[API Documentation](http://localhost:8001/docs) • "
    f"Connected to: `{API_URL}`"
)
