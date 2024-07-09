import base64
import io
import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
API_URL = "http://localhost:8090"

def login():
    st.title("Exam Login")
    if 'user_name'  not in st.session_state:
        st.session_state.user_name=''
    user_name=st.text_input("Enter your name",st.session_state.user_name)
    pwd=st.text_input("Enter your password",type='password')
    if st.button("Login"):
        if user_name =='Suresh' and pwd=='password':
            st.session_state.logged_in=True
            st.session_state.user_name=user_name
            st.experimental_rerun()
        else: 
            st.warning("Incorrect Username or Password")

def create_quiz():
    st.title("Priliminary Test")

    response = requests.get(f"{API_URL}/get_questions")
    if response.status_code != 200:
        st.warning("No questions available. Please ask the admin to generate questions.")
        return

    global questions 
    print(type(response))
    pre_questions=response.json()
    questions=pre_questions['questions']
    questions_container = st.container()
    if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if not st.session_state.quiz_submitted:
        with questions_container:
            for i in range(len(questions)):
                st.subheader(f"Question{i+1}")
                st.write(questions[i]['question'])
                # for key, value in questions[i]['options'].items():
                #     st.write(f" {key}: {value}")
                # st.write(questions[i]['options'].items())
                options = list(questions[i]['options'].items())
                selected_option = st.radio(
                    "Select your answer:",
                    options,
                    format_func=lambda x: f"{x[0]}: {x[1]}",
                    key=f"question_{i}"
                )
                st.session_state.user_answers[i] = selected_option[0]
        if st.button("Submit"):
            st.session_state.quiz_submitted = True
            st.experimental_rerun()
    else:
        display_results()
        


def calculated_score():
    # st.write(st.session_state.user_answers)
    count=0
    for i in range(len(questions)):
         if st.session_state.user_answers[i]==questions[i]['correct_answer'] :
              count+=1
    # st.write(f"Your Score :{count}")
    return count

def display_results():
    score=calculated_score()
    total_questions = len(questions)
    
    st.success("Congratulations on completing the quiz!")
    st.balloons()  # This adds a nice visual effect
    
    st.header(f"Your Score: {score}/{total_questions}")
    
    percentage = (score / total_questions) * 100
    st.write(f"You got {percentage:.2f}% of the questions correct.")
    
    if percentage == 100:
        st.write("Perfect score! Excellent job!")
    elif percentage >= 80:
        st.write("Great job! You did very well.")
    elif percentage >= 60:
        st.write("Good effort! There's room for improvement.")
    else:
        st.write("Keep practicing! You'll do better next time.")
    
    report=[]
    for i in range(len(questions)):
        report.append({
            "Questions":questions[i]['question'],
            "Options":questions[i]['options'],
            "Selected Option":st.session_state.user_answers[i],
            "Correct Answer":questions[i]['correct_answer']
        })
    df = pd.DataFrame(report)

    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15,style='B')
    pdf.cell(0,10,txt="Test Report",ln=True,align='C')
    pdf.set_font("Arial", size=13,style='B')
    pdf.cell(200,10,txt=f"Candidate Name:{st.session_state.user_name}",ln=True)
    # Add questions to the PDF
    
    for index, row in df.iterrows():
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"{index+1}) {row['Questions']}", ln=True)
        options=row['Options']
        for key,value in options.items():
            pdf.cell(200,10,txt=f"{key}:{value}",ln=True)
        pdf.set_font("Arial", size=12,style='B')
        pdf.cell(200,10,txt=f"Correct Option:{row['Correct Answer']}",ln=True)
        if row['Correct Answer'] == row['Selected Option']:
            pdf.set_text_color(0,128,0)
        else:
            pdf.set_text_color(255,0,0)
        
        pdf.cell(200,10,txt=f"Selected Option:{row['Selected Option']}",ln=True)


    pdf.ln()  # Example: Add a blank line as a separator

    # Add results section
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial", style='B', size=14)  # Larger and bold font for results
    pdf.cell(200, 10, txt="Quiz Results", ln=True)
       
    pdf.cell(200,10,txt=f"Your Score: {score}/{total_questions}",ln=True)
    pdf.cell(200,10,txt=f"You got {percentage:.2f}% of the questions correct.",ln=True)
    # Create a BytesIO buffer
    pdf_buffer = io.BytesIO()


    temp_pdf_path = "/tmp/temp_report.pdf"
    # Output the PDF to the buffer
    pdf.output(temp_pdf_path)  # Pass pdf_buffer as an argument
   # Read the temporary file into a BytesIO buffer
    with open(temp_pdf_path, "rb") as f:
        pdf_buffer = io.BytesIO(f.read())

    # Create a download button for the PDF
    b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')  # Use getvalue() method
    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="quiz_report.pdf">Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True) 
    


if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in=False
    if not st.session_state.logged_in:
        login()
    else:
        create_quiz()