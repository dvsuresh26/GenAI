from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app=FastAPI()

#MockData
customers={
    "1":{
        "name":"Suresh","email":"suresh@abc.com","phone":"123-456-7890"
    },
    "2":{
        "name":"Nani","email":"nani@xyz.com","phone":"012-456-7090"
    },
    "3":{
        "name":"Chinni","email":"chinni@lmn.com","phone":"012-123-7090"
    },
    "4":{
        "name":"Nikku","email":"nikku@pqr.com","phone":"012-123-0000"
    }
}

tickets=[]

class Ticket(BaseModel):
    customer_id:str
    subject:str
    description:str
    priority:str
    status:str="open"

@app.get("/customer/{customer_id}")
async def get_customer(customer_id:str):
    return customers.get(customer_id,{})

@app.post("/tickets/")
async def create_ticket(ticket:Ticket):
    tickets.append(ticket)
    return {"status":"Ticket created","ticket":ticket}

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8080)