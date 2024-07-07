import streamlit as st
import google.generativeai as geminiai
from jinja2 import Template
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
import json 
import boto3
load_dotenv()
geminiai.configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["OPENAI_API_KEY"]= os.getenv("OPENAI_API_KEY")

session_state=st.session_state
def convert_pdf_to_text(uploaded_file):
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def get_response(input):
    model= geminiai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def get_response_openai(input):
    model=ChatOpenAI(temperature=0)
    response=model(input)
    print(response.content)
    return output_parser.parse(response.content)

def get_response_gemini(input):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    response = llm.invoke(input)    
    return (response.content)
# def extract_text_pdf(uploaded_file):
#     reader = pdf.PdfReader(uploaded_file)
#     text=""
#     for page in reader(len(reader.pages)):
#         page = reader.pages[page]
#         text=+str(page.extract_text())


match_schema = ResponseSchema(
    name="JD Match",
    description="Evaluate the percentage value of  that how well the resume matches the job description requirements and  keywords."
)
MissingKeywords_schema = ResponseSchema(
    name="Missing Keywords",
    description="Identify any key skills, technologies, or qualifications mentioned in the job description that are missing from the resume."
)

Summary_schema = ResponseSchema(
    name="Summary",
    description="Provide a concise summary highlighting the candidate's strengths, weaknesses, and overall suitability for the job."
)

candidate_name_schema=ResponseSchema(
    name="candidate name",
    description="name of the candidate"
)

Rank_Schema = ResponseSchema(
    name="Rank",
    description="Rank the following list of resumes based on their fit with the given job description. Each resume is provided in JSON format with fields JD Match, Missing Keywords, Summary, and candidate name. Also, include the provided job description for context.Assign the rank in ascending order of numbers in string format."
)

response_schemas=[match_schema,MissingKeywords_schema,Summary_schema]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instrctions = output_parser.get_format_instructions()


response_schemas2=[candidate_name_schema,Rank_Schema]
output_parser2 = StructuredOutputParser.from_response_schemas(response_schemas2)
format_instrctions2 = output_parser2.get_format_instructions()

#Prompt
prompt=""" 
    Hello Assistant,

You are an expert in resume screening and evaluation, with a comprehensive understanding of Information Technology, 
Software Engineering, and the latest technologies, programming languages, frameworks, and cloud services. 
Your role is to assist Hiring Managers by meticulously evaluating resumes based on specific job descriptions. 
Given the competitive job market, your evaluation should be precise, detailed, and highly accurate. 
Most importantly you need to find out if the candidate position in resume matches with job description or not. If they
dont match give jd Match 0%.
Please analyze the provided resume and job description, then return the following details:

1)Percentage match : Evaluate the percentage value of match that how well the resume matches the job description requirements.
2)Missing keywords: Identify any key skills, technologies, or qualifications mentioned in the job description that are missing from the resume.
3)Overall summary of the resume: Provide a concise summary highlighting the candidate's strengths, weaknesses, and overall suitability for the job.
Here are the details:

Resume: {resume}
Job Description: {jd}
{format_instrctions}

"""

ranking_prompt="""
    You are an excellent assistant of hiring manager. Your task is to rank parsed resumes.
    Rank the following list of resumes based on their fit with the given job description. Each resume is provided in JSON format with fields
      JD Match, Missing Keywords, Summary, and candidate name. Also, include the provided job description for context.
      Assign the rank in ascending order
    Please analyze the provided parsed_resumes and job description, then return the following details of parsed_resumes:

    1)Candidate name: name of the candidate
    2)Rank:Rank the following list of resumes based on their fit with the given job description. Each resume is provided in JSON format with fields
      JD Match, Missing Keywords, Summary, and candidate name. Also, include the provided job description for context.
      Assign the rank in ascending order of numbers in string format.
List of Resumes:
{parsed_resumes}

Job Description:
{jd}

{format_instrctions2}
"""

st.title("Intelligent ATS")
jd=st.text_area("Enter your job description")
uploaded_files = st.file_uploader("Upload your resume",type="pdf",accept_multiple_files=True)
s3=boto3.client(
    's3',
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY")
    
    )
submit = st.button("Submit")
bucket_name="ats-resume-results"
file_name="jd2"
if submit:
    json_objects=[]
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            candidate_name=uploaded_file.name
            resume=convert_pdf_to_text(uploaded_file)
            template = ChatPromptTemplate.from_template(prompt)
            final_prompt = template.format_messages(resume=resume,jd=jd,format_instrctions=format_instrctions)
            response=get_response_openai(final_prompt)
            response['candidate_name']=candidate_name
            
            st.write()
            json_objects.append(response)
        # st.write(json_objects) 
        session_state.parsed_resumes=json_objects 
        
        st.write(json_objects)
        with open('combined_output.json', 'w') as outfile:
            json.dump(json_objects, outfile, indent=2)
        #Saving Parsed Resumes to S3 Bucket
        key="ATS Results"
        with open('combined_output.json', 'rb') as data:
                s3.upload_fileobj(data, bucket_name, key)
Rank = st.button("Rank Resumes")
if(Rank):
    # *** Template when using Google Gemini with out Langchin
    # template = Template(ranking_prompt)
    # final_prompt2 = template.render(parsed_resumes=session_state.parsed_resumes,jd=jd)
    #response=get_response_gemini(final_prompt2)
    template = ChatPromptTemplate.from_template(ranking_prompt)
    final_prompt2 = template.format_messages(parsed_resumes=session_state.parsed_resumes,jd=jd,format_instrctions2=format_instrctions2)
    response=get_response_gemini(final_prompt2)
    
    st.write(response)
    