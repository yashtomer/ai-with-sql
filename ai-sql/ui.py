import streamlit as st
import requests
import pandas as pd


API_URL = "http://localhost:8000"  # Update with your FastAPI URL

#Set page title
st.title("AI SQL Query Generator")
st.markdown("This app allows you to generate and execute SQL queries from natural language input.")

#Input text box for user query 
query_input = st.text_area("Enter your natural language query:")



# Show active LLM configuration
with st.expander("Active LLM Configuration", expanded=True):
    try:
        info = requests.get(f"{API_URL}/llm_info", timeout=10).json()
        st.write({
            "Model": info.get("model"),
            "Base URL": info.get("base_url"),
            "Custom base URL": info.get("using_custom_base_url"),
        })
    except Exception as e:
        st.warning(f"Could not fetch LLM info: {e}")

#Fetch avialable databases
st.sidebar.header("Database Selection")
if st.sidebar.button("List Databases"):
    response = requests.get(f"{API_URL}/list_databases")

    if response.status_code == 200:
        database = response.json().get("databases", [])
        st.sidebar.write("Available Databases:")
        st.sidebar.write(database)
    else:
        st.sidebar.error("Failed to fetch databases.")


#Select a database
selected_database = st.sidebar.text_input("Enter Database Name", value="")
if selected_database:
    if st.sidebar.button("List Tables"):
        response = requests.get(f"{API_URL}/get_tables/{selected_database}")
        if response.status_code == 200:
            tables = response.json().get("tables", [])
            st.sidebar.write("Tables in Database:")
            st.sidebar.write(tables)
        else:
            st.sidebar.error("Failed to fetch tables.")

    #Select a table
    selected_table = st.sidebar.text_input("Enter Table Name", value="")
    if selected_table:
        if st.sidebar.button("List Columns"):
            response = requests.get(f"{API_URL}/get_columns?table_name={selected_table}&database={selected_database}")
            if response.status_code == 200:
                columns = response.json().get("columns", [])
                st.sidebar.write("Columns in Table:")
                st.sidebar.write(columns)
            else:
                st.sidebar.error("Failed to fetch columns.")
    
    

if st.button("Generate SQL Query"):
    if query_input:
        #Send request to FastAPI endpoint
        response = requests.post("http://localhost:8000/generate_sql", json={"nl_query": query_input, "database": selected_database})
        sql_query = response.json().get("sql_query")
        st.code(sql_query, language='sql')

        st.session_state["generated_sql"] = sql_query

if "generated_sql" in st.session_state:
    if st.button("Execute SQL Query"):
        #Send request to execute the generated SQL query
        response = requests.post("http://localhost:8000/execute_sql", json={"nl_query": st.session_state["generated_sql"]})
        result = response.json().get("result", [])

        optimization_tips = response.json().get("optimization_suggestion", "No message returned.")

        st.subheader("Query Results:")
        if result:
            df = pd.DataFrame(result)
            st.dataframe(df)

        st.subheader("Optimization Tips:")
        st.write(optimization_tips)
else:
    st.warning("Please generate a SQL query first by entering a natural language query.") 
