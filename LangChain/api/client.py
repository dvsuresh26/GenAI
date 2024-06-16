import streamlit as st

import requests


def get_OpenAI_response(input_text):
    response = requests.post(
        "http://localhost:8090/essay/invoke",
        json={'input':{'topic':input_text}}
    )
    return response.json()['output']['content']


def get_Ollama_response(input_text1):
    response = requests.post(
        "http://localhost:8090/poem/invoke",
        json={'input':{'topic':input_text}}
    )
    return response.json()['output']

#Streamlit UI

input_text = st.text_input("Write an Essay Topic on")
input_text1 = st.text_input("Write an Poem on")

if input_text:
    st.write(get_OpenAI_response(input_text))

if input_text1:
    st.write(get_Ollama_response(input_text))