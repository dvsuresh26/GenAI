from fastapi import FastAPI
import uvicorn
import requests
from transformers import pipeline


app=FastAPI()
pipe = pipeline("text2text-generation", model="google/flan-t5-small")

@app.get("/")
async def home():
    return "Welcome"

@app.get("/getResponse")
async def getResponse(input:str):
    response = pipe(input)
    return response

# if __name__=="__main__":
#     uvicorn.run(app,host="localhost",port=8088)