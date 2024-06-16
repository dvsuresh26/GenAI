from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

import streamlit as st
from fastapi import FastAPI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import Ollama
from langserve import add_routes
import uvicorn
load_dotenv()
os.environ["OPEN_API_KEY"]=os.getenv("OPENAI_API_KEY")

app= FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Hands-on with API Server"
)

add_routes(
    app,
    ChatOpenAI(),
    path="/openai"
)
#model 1
model = ChatOpenAI()
#model 2
llm= Ollama(model="llama3")
prompt1= ChatPromptTemplate.from_template("Write me an essay on {topic} with 100 words")
prompt2= ChatPromptTemplate.from_template("Write me a poem on {poem} for 5 years old child")

add_routes(
    app,
    prompt1|model,
    path="/essay"
)

add_routes(
    app,
    prompt2|llm,
    path="/poem"
) 

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8090)
