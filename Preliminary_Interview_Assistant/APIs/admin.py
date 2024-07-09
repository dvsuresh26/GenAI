import streamlit as st
import requests
import time
API_URL = "http://localhost:8090"

st.title("Admin- Generate Exam Questions")
num_questions = st.number_input("Number of questions",min_value=2,max_value=30,value=5)
options=["Basic","Intermediate","Advanced"]
kind=st.selectbox("Choose Complexity",options)
topic = st.text_input("Enter Position")

if st.button("Generate Questions"):
    with st.spinner("Genearing Questions..."):
        response = requests.post(f"{API_URL}/generate_questions",json={
            "num_questions":num_questions,
            "topic":topic,
            "kind":kind
        })
    

    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.1)
        progress_bar.progress(percent_complete + 1)
    if response.status_code == 200:
        st.success(response.json()["message"])