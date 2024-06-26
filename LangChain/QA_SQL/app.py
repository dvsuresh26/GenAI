import streamlit as st
import os
import pandas as pd
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from langchain.chat_models import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
import json
st.markdown(
    """
    <style>
    .wide-text-area {
        width: 100%;
    }
    .stTextArea {
        width: 100%; /* Adjust width as needed */
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stColumn:first-child {
        margin-right: 1rem !important;
    }
    .css-1lcbmhc, .css-1d391kg {
        padding-left: 0;
        padding-right: 0;
    }
    .css-1d391kg {
        margin-left: 0rem;
    }
    .stHorizontal {
        display: flex;
        justify-content: space-between;
    }
    .stColumn {
        flex: 1;
        margin-right: 1rem;
    }
    .stColumn:last-child {
        margin-right: 0;
    }
    .stColumn-left {
        margin-left: 0;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


st.title("Ask Questions on Your DB")
col1,col2 = st.columns(2)

def get_executor(df,uploaded_file):
    file_name, file_extension = os.path.splitext(uploaded_file.name)
    database=f"sqlite:///{file_name}.db"
    engine =  create_engine(database)
    df.to_sql(file_name,engine,index=False)
    db=SQLDatabase(engine=engine)
    llm=ChatOpenAI(temperature=0)
    agent_executor1 = create_sql_agent(llm,db=db,agent_type='openai-tools',verbose=True)
    st.session_state['agent_executor1']=agent_executor1
    return agent_executor1

def get_executor2(uploaded_file):
    file_name, file_extension = os.path.splitext(uploaded_file.name)
    connection=f"sqlite:///{file_name}.db"
    db = SQLDatabase.from_uri(connection)

    llm=ChatOpenAI(temperature=0)
    agent_executor2 = create_sql_agent(llm,db=db,agent_type='openai-tools',verbose=True)
    st.session_state['agent_executor2']=agent_executor2
    return agent_executor2


save_path=""
with col1:
    file_type=st.selectbox("Select File type",options=["db","csv"])
    st.session_state['file_type']=file_type
    uploaded_file=""
    if file_type == "csv":
        uploaded_file=st.file_uploader("Choose a CSV file",type="csv")
        st.session_state['uploaded_file']=uploaded_file 
        if uploaded_file is not None:
            save_path =os.path.join("uploaded_files",uploaded_file.name)
            with open(save_path,"wb") as file:
                file.write(uploaded_file.getbuffer())
            st.success("File saved successfully")
            #st.write(uploaded_file)
        if not os.path.exists("uploaded_files"):
            os.makedirs("uploaded_files")
    if file_type =="db":
        uploaded_file=st.file_uploader("Choose a DB file",type="db")
        st.session_state['uploaded_file']=uploaded_file 
        if uploaded_file is not None:
            save_path =os.path.join("uploaded_files",uploaded_file.name)
            with open(save_path,"wb") as file:
                file.write(uploaded_file.getbuffer())
            st.success("File saved successfully")
            #st.write(uploaded_file)
        if not os.path.exists("uploaded_files"):
            os.makedirs("uploaded_files")

with col2:
    input = st.text_area("Enter your question here")
    if st.session_state['file_type'] == "csv":
        if os.path.exists(save_path):
            df=pd.read_csv(save_path)
            # st.write(df[:5])
            # if not os.path.exists("./titanic.db"):
            if 'agent_executor1' not in st.session_state:
                agent_executor1=get_executor(df,st.session_state['uploaded_file'])  
            response = st.session_state['agent_executor1'].invoke({"input":{input}})        
            st.text_area("Output:", value=response["output"], height=200,max_chars=None, key=None)
    if st.session_state['file_type'] =='db':
        if os.path.exists(save_path):
        
            # st.write(df[:5])
            # if not os.path.exists("./titanic.db"):
            if 'agent_executor2' not in st.session_state:
                agent_executor2=get_executor2(st.session_state['uploaded_file'])  
            response = st.session_state['agent_executor2'].invoke({"input":{input}})        
            # st.write(response["output"])
            st.text_area("Output:", value=response["output"], height=200, max_chars=None, key=None)
#until here