import streamlit as st


quiz={'questions': [{'question': 'What is the primary language used for programming in artificial intelligence?', 'options': {'a': 'Python', 'b': 'Java', 'c': 'C++', 'd': 'Ruby'}, 'correct_answer': 'a'}, {'question': 'Which of the following is not a machine learning algorithm?', 'options': {'a': 'Linear Regression', 'b': 'Decision Trees', 'c': 'Quick Sort', 'd': 'Support Vector Machines'}, 'correct_answer': 'c'}, {'question': 'What is the purpose of activation functions in neural networks?', 'options': {'a': 'To reduce overfitting', 'b': 'To introduce non-linearity', 'c': 'To normalize the input data', 'd': 'To optimize the learning rate'}, 'correct_answer': 'b'}, {'question': 'Which technique is used to minimize the error in a neural network during training?', 'options': {'a': 'Gradient Descent', 'b': 'K-means Clustering', 'c': 'Regression Analysis', 'd': 'Principal Component Analysis'}, 'correct_answer': 'a'}, {'question': 'What is the purpose of a loss function in machine learning?', 'options': {'a': "To measure the model's performance", 'b': 'To regularize the model', 'c': 'To preprocess the data', 'd': 'To visualize the data'}, 'correct_answer': 'a'}, {'question': 'Which type of neural network architecture is commonly used for image recognition?', 'options': {'a': 'Feedforward Neural Network', 'b': 'Convolutional Neural Network', 'c': 'Recurrent Neural Network', 'd': 'Radial Basis Function Network'}, 'correct_answer': 'b'}, {'question': 'What is the purpose of dropout regularization in neural networks?', 'options': {'a': 'To reduce the number of neurons in each layer', 'b': 'To prevent overfitting', 'c': 'To increase the learning rate', 'd': 'To add noise to the input data'}, 'correct_answer': 'b'}, {'question': 'Which of the following is an unsupervised learning algorithm?', 'options': {'a': 'Linear Regression', 'b': 'K-means Clustering', 'c': 'Support Vector Machines', 'd': 'Random Forest'}, 'correct_answer': 'b'}, {'question': 'What is the purpose of data preprocessing in machine learning?', 'options': {'a': 'To reduce the dimensionality of the data', 'b': 'To standardize the data', 'c': 'To extract features from the data', 'd': 'To prepare the data for model training'}, 'correct_answer': 'd'}, {'question': 'Which algorithm is commonly used for collaborative filtering in recommendation systems?', 'options': {'a': 'K-nearest Neighbors', 'b': 'Decision Trees', 'c': 'Logistic Regression', 'd': 'SVM'}, 'correct_answer': 'a'}]}

questions=quiz['questions']

# for i in range(10):
#     print(questions[i]['question'])
#     print("options:",questions[i]['options']['a'],questions[i]['options']['b'],questions[i]['options']['c'],questions[i]['options']['d'])


def create_quiz():
    st.title("Priliminary Test")
    questions_container = st.container()
    if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if not st.session_state.quiz_submitted:
        with questions_container:
            for i in range(10):
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
    for i in range(10):
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