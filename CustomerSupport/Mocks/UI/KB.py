import streamlit as st
import requests


URL="http://localhost:8081"
st.title("Mock Knowledge Base")
query=st.text_input("Search Knowledge")
if query:
    response= requests.get(f"{URL}/search/", params={"query":query})
    query_results=response.json()
    st.write(query_results)
article_id=st.text_input("Enter Article ID to view content")
if article_id:
    response=requests.get(f"{URL}/articles/{article_id}")
    article=response.json()
    st.write(article)