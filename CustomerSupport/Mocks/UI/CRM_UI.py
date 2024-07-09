import streamlit as st
import requests


URL1="http://localhost:8080/customer/"
URL2="http://localhost:8080/tickets/"
st.title("Mock CRM Interface")
st.sidebar.title("Customer Details:")
customer_id = st.sidebar.text_input("Enter Customer ID")
if customer_id:
    response= requests.get(f"{URL1}{customer_id}")
    customer=response.json()
    st.sidebar.write("Customer Details:",customer)

st.subheader("Create New Ticket")
with st.form("ticket_form"):
    customer_id=st.text_input("Customer ID")
    subject = st.text_input("Subject")
    description= st.text_area("Description")
    priority = st.selectbox("Priority",["Low","Medium","High"])
    submit_button=st.form_submit_button("Create Ticket")
    if submit_button:
        ticket_data={
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
        }
        response=requests.post(URL2,json=ticket_data)
        ticket=response.json()
        print(ticket)
        print(response)
        st.write(ticket)