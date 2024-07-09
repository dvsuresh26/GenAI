from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import uvicorn
load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI()
question_schema = ResponseSchema(
    name="question",
    description="provide your question"
)
options_schema = ResponseSchema(
    name="options",
    description="""
        {
            {'key':'a', 'value':'<option1>'},
            {'key':'b', 'value':'<option2>'},
            {'key':'c', 'value':'<option3>'},
            {'key':'d', 'value':'<option4>'},
        }
    """
)

answer_schema = ResponseSchema(
    name="answer",
    description="Correct answer for the question"
)


question_item_schema = ResponseSchema(
    name="question_item",
    description="A single question item with question, options, and answer",
    sub_schemas=[question_schema, options_schema, answer_schema]
)

questions_list_schema = ResponseSchema(
    name="questions",
    description="List of question items",
    sub_schemas=[question_item_schema]
)


response_schemas=[questions_list_schema]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

app=FastAPI()
class QuizRequest(BaseModel):
    num_questions:int
    topic:str
    kind:str

class Person(BaseModel):
    name:str



@app.post("/greetings")
async def greetings(request:Person):
    return {"message": f"Welcome to { request.name}"}

@app.post("/generate_questions")
async def generate_questions(request:QuizRequest):
    prompt=f"""
            Generate {{num_questions}} multiple-choice question with options and specify the correct answer.
            These questions are for {{kind}} knowledge person. 
            These questions are used for preliminary test.
            Question are for {{topic}}.
            Please return each question with the following format:
            Strictly follows below format.
            {{format_instructions}}
            
            
    """
    prompt_template = ChatPromptTemplate.from_template(prompt)
    
    # Please return each question with the following format:
    #         {format_instructions}
    # Format the prompt with input text

    final_prompt=prompt_template.format_messages(format_instructions=format_instructions,num_questions=request.num_questions,topic=request.topic,kind=request.kind)
    # Get the response from the model
    response = llm(final_prompt)
    global questionss
    questionss = output_parser.parse(response.content)
    print(type(questionss))
    return {"message": f"{request.num_questions} questions generated successfully"}

@app.get("/get_questions")
async def get_questions():
    if not questionss:
        raise HTTPException(status_code=404,detail="No Questions available")
    return questionss


if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8090)

