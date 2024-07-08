import streamlit as st
import requests
API_URL = "http://localhost:8090"

st.title("Generate Preliminary Exam Questions")
num_questions = st.number_input("Number of questions",min_value=2,max_value=30,value=5)
topic = st.text_input("Enter Position")

if st.button("Generate Questions"):
    with st.spinner("Genearing Questions..."):
        response = requests.post(f"{API_URL}/generate_questions",json={
            "num_questions":num_questions,
            "topic":topic
        })

    if response.status_code == 200:
        st.success(response.json()["message"])