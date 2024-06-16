from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"

#Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","You are a user assistant. Please help with user queries"),
        ("user","{query}")
    ]
)

#UI with Streamlit
st.title('LangChain Demo with OpenAI')
input_text= st.text_input("Ask what you want!")
#OpenAI LLM
llm=ChatOpenAI(model="gpt-3.5-turbo")
output_parser= StrOutputParser()
chain=prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({'query':input_text}))
