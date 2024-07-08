import streamlit as st
import requests
API_URL = "http://localhost:8090"



def create_quiz():
    st.title("Priliminary Test")

    response = requests.get(f"{API_URL}/get_questions")
    if response.status_code != 200:
        st.warning("No questions available. Please ask the admin to generate questions.")
        return

    global questions 
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
if __name__ == "__main__":
     create_quiz()