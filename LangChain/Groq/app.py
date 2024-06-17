import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_cohere import CohereEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
import time 
from dotenv import load_dotenv
groq_api = os.getenv("GROQ_API_KEY")
os.environ["COHERE_API_KEY"]=os.getenv("COHERE_API_KEY")


if "vecotrs" not in st.session_state:

    st.session_state.embeddings = CohereEmbeddings()
    st.session_state.loader = WebBaseLoader("https://docs.smith.langchain.com/")
    st.session_state.docs = st.session_state.loader.load()
    st.session_state.chunks = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200).split_documents(st.session_state.docs)
    st.session_state.vectors = FAISS.from_documents(st.session_state.chunks[:40],st.session_state.embeddings)

st.title("Groq Demo")
llm = ChatGroq(groq_api_key=groq_api,
               model="Gemma-7b-It")
prompt = ChatPromptTemplate.from_template(
    """
        Please answer the question based in given context only which is in triple backticks
        ```{context} ```
        question:{input}
    """
)

document_chain = create_stuff_documents_chain(llm,prompt)
retriever = st.session_state.vectors.as_retriever()
retrieval_chain = create_retrieval_chain(retriever,document_chain)

query = st.text_input("Ask your quer here!")

if query:
    start = time.process_time()
    response =retrieval_chain.invoke({"input":query})
    st.write("Respone time:", time.process_time()-start)
    st.write(response['answer'])

    # Streamlit Expander
    with st.expander("Document Similarity Search"):
        for i,doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("---------------------------------------------------------------------------------------------------------------")
