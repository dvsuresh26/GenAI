import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage,HumanMessage
import bs4
st.markdown(
    """
    <style>
    .title-container {
        position: fixed;
        padding: 10px 0;
        top:0.5cm;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .title-text {
        text-align: center; /* Center align the title text */
        margin: 0; /* Remove default margin */
        padding: 0; /* Remove any padding */
    }
    .ip{
        position:fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)
store={}

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
# st.markdown("<div class='fixed-title'>Chat Application</div>", unsafe_allow_html=True)

# st.title("Your own Chit-Chat GPT")
st.write("""
    <div class="title-container">
        <h1 style="text-align: center;">Your own Chit-Chat GPT</h1>
    </div>
""", unsafe_allow_html=True)

# Layout of the Streamlit app

def get_llm_ready():
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
    #Loading
    loader = WebBaseLoader(
        web_path=(st.session_state.url,),
        
        # bs_kwargs=dict(
        #     parse_only=bs4.SoupStrainer(
        #         class_=("post-content","post-header","post-content")
        #     )
        # )
    )
    docs= loader.load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=200).split_documents(docs)
    #Store Embeddings into Vector DB
    embeddings = OpenAIEmbeddings()
    vectorDB= Chroma.from_documents(chunks,embeddings)
    #create a retriever for this DB
    retriever = vectorDB.as_retriever()
    return retriever,llm,docs
    # create a system prompt
def get_final_rag(retriever,llm,input):
        system_prompt= " You are acting as an assistant to Question-Answering Tasks. Use the context given in triple backticks to answer the question.```{context}``` If you dont know answer jut say Dont know. Keep the answer as short using only 4 sentences  "
        #prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",system_prompt),
                ("human","{input}"),
            ]
        )
        stuff_chain = create_stuff_documents_chain(llm,prompt)
        context_based_system_prompt =(
            "Latest question and Chat History has been given"
            "This latest questin might reference the context in the chat history"
            "Formuate a standalone question in a undestandable way with out the chat history"
            "Do not Answer the question just reformulate it if needed, else, return as it is"
            )
        context_based_prompt = ChatPromptTemplate.from_messages(
        [
                ("system",context_based_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human","{input}"),
        ] 
            
        )
        history_retriever = create_history_aware_retriever(llm,retriever,context_based_prompt)
        chat_qa_prompt=ChatPromptTemplate.from_messages(
                [
                    ("system",system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human","{input}"),
                ]
            
        )
        stuff_qa_chain = create_stuff_documents_chain(llm,chat_qa_prompt)

        final_rag_chain = create_retrieval_chain(history_retriever,stuff_qa_chain)
        return final_rag_chain

#to get session
def get_SessionHistory(session_id:str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id]=ChatMessageHistory()
    return store[session_id]

# Initialize session state for messages and URL
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'url' not in st.session_state:
    st.session_state.url = ""

# Function to handle URL input
def handle_url_input():
    st.sidebar.header("Upload URL")
    url = st.sidebar.text_input("Enter URL")
    if st.sidebar.button("Submit URL"):
        st.session_state.url = url
        st.sidebar.success(f"URL '{url}' has been processed.")
    return "success"

# Function to display chat messages
def display_chat():
    
    chat_container = st.container()
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            with chat_container:
                st.markdown(f"<div style='background-color: #1e1e1e; padding: 10px; border-radius: 5px; text-align: left; color: white;'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            with chat_container:
                st.markdown(f"<div style='background-color: #333333; padding: 10px; border-radius: 5px; text-align: left; color: white;'>{msg['content']}</div>", unsafe_allow_html=True)

# Function to handle user input
def handle_user_input(retriever,llm):
    st.session_state.user_input = st.text_input("You:", key="input")
    if st.button("Send"):
        if st.session_state.user_input:
            st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})
            # Here you should call your RAG model to get the assistant's response
            final_rag_chain=get_final_rag(retriever,llm,st.session_state.user_input)
            stateful_rag_chain = RunnableWithMessageHistory(
                final_rag_chain,
                get_SessionHistory,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
                )

            response =stateful_rag_chain.invoke(
            {"input":st.session_state.user_input},
            config={
                "configurable":{"session_id":"xyz123"}
            }, )
            assistant_response = response["answer"]  # Replace with actual model response
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            display_chat()
            st.session_state.user_input = ""  # Clear the input field

# Layout of the Streamlit app
status =handle_url_input()
if(st.session_state.url):
    retriever,llm,docs= get_llm_ready()
    handle_user_input(retriever,llm)
