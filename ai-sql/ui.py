import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8080"  # Update with your FastAPI URL

# Add Aeologic logo
st.sidebar.image("https://www.aeologic.com/images/aeologo.png", width=200)

#Set page title
st.title("AI SQL Query Generator")
st.markdown("This app allows you to generate and execute SQL queries from natural language input.")






#Fetch available databases
st.sidebar.header("Database Selection")
databases = []
try:
    response = requests.get(f"{API_URL}/list_databases")
    if response.status_code == 200:
        databases = response.json().get("databases", [])
except requests.exceptions.ConnectionError:
    st.sidebar.error("Could not connect to the FastAPI backend. Please ensure it's running.")

selected_database = st.sidebar.selectbox("Select a Database", [""] + databases, index=([""] + databases).index("getlicense") if "getlicense" in databases else 0)

if selected_database:
    st.session_state["selected_database"] = selected_database
    tables = []
    try:
        response = requests.get(f"{API_URL}/get_tables/{selected_database}")
        if response.status_code == 200:
            tables = response.json().get("tables", [])
    except requests.exceptions.ConnectionError:
        st.sidebar.error("Could not connect to the FastAPI backend. Please ensure it's running.")

    selected_table = st.sidebar.selectbox("Select a Table", [""] + tables)

    if selected_table:
        st.session_state["selected_table"] = selected_table
        columns = []
        try:
            response = requests.get(f"{API_URL}/get_columns?table_name={selected_table}&database={selected_database}")
            if response.status_code == 200:
                columns = response.json().get("columns", [])
                st.sidebar.write("Columns in Table:")
                st.sidebar.write(columns)
            else:
                st.sidebar.error("Failed to fetch columns.")
        except requests.exceptions.ConnectionError:
            st.sidebar.error("Could not connect to the FastAPI backend. Please ensure it's running.")
else:
    st.session_state["selected_database"] = ""
    st.session_state["selected_table"] = ""

# Display sample questions based on selected database
if st.session_state.get("selected_database"):
    st.subheader(f"Sample Questions for {st.session_state.selected_database}:")
    try:
        response = requests.get(f"{API_URL}/get_sample_questions/{st.session_state.selected_database}")
        if response.status_code == 200:
            sample_questions = response.json().get("sample_questions", [])
            if sample_questions:
                for q in sample_questions:
                    st.markdown(f"* {q}")
            else:
                st.info("No sample questions available for this database.")
        else:
            st.error("Failed to fetch sample questions.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI backend to fetch sample questions. Please ensure it's running.")


#Input text box for user query 
query_input = st.text_area("Enter your natural language query:", key="nl_query_input_main")



if st.button("Generate SQL Query"):
    if query_input:
        #Send request to FastAPI endpoint
        response = requests.post(f"{API_URL}/generate_sql", json={"nl_query": query_input, "database": st.session_state.get("selected_database")})
        sql_query = response.json().get("sql_query")
        st.code(sql_query, language='sql')

        st.session_state["generated_sql"] = sql_query

if "generated_sql" in st.session_state:
    if st.button("Execute SQL Query"):
        #Send request to execute the generated SQL query
        response = requests.post(f"{API_URL}/execute_sql", json={"nl_query": st.session_state["generated_sql"]})
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