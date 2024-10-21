from groq import Groq
import streamlit as st
import csv
import os

client = Groq(api_key="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")

# Function to interact with the LLM
def interact_with_llm(user_query, system_prompt, client):
    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None,
    )

    llm_response = ""
    for chunk in completion:
        llm_response += chunk.choices[0].delta.content or ""
    
    return llm_response

# Generate Roadmap
def genRoadmap(user_interest):
    system_prompt = "Based on the user's interest, generate a comprehensive learning roadmap. The roadmap should include key milestones, starting from basic concepts to more advanced topics, presented in a logical order. Each milestone or point in the roadmap should be separated by a comma."
    roadmap = interact_with_llm(user_interest, system_prompt, client)
    return roadmap

# Save user data to a CSV file
def save_user_data(username, roadmap, field_of_interest, placement_level):
    filename = "user_data.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Username", "Field of Interest", "Roadmap", "Placement Level"])
        writer.writerow([username, field_of_interest, roadmap, placement_level])

# Fetch user data based on username
def get_user_data(username):
    filename = "user_data.csv"
    if os.path.isfile(filename):
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if row[0].lower() == username.lower():
                    return {
                        "username": row[0],
                        "field_of_interest": row[1],
                        "roadmap": row[2],
                        "placement_level": row[3]
                    }
    return None

# Generate Placement Test
def genPlacementTest(field_of_interest):
    system_prompt = (
        f"Generate a placement test to evaluate the overall knowledge of a user in the field of {field_of_interest}. "
        "Each question should be straightforward without any answer options or multiple-choice format. "
        "Questions should assess basic, intermediate, and advanced concepts. Avoid prefixing questions with 'Question 1:' or similar formats."
    )
    test = interact_with_llm("Create questions", system_prompt, client)
    return test

def main():
    global user_field
    st.title("Learning Roadmap & Placement Test Generator")
    
    st.header("Generate Learning Roadmap")
    user_interest = st.text_input("Enter the field you're interested in (e.g., 'Convolutional Neural Networks'):")
    user_field = user_interest
    if st.button("Generate Roadmap"):
        if user_interest:
            roadmap = genRoadmap(user_interest)
            roadmap_items = [item.strip() for item in roadmap.split(",")]
            st.write("### Learning Roadmap:")
            st.write("Here is your roadmap presented as a structured list:")
            st.markdown("<ul>" + "".join([f"<li>{item}</li>" for item in roadmap_items]) + "</ul>", unsafe_allow_html=True)
        else:
            st.error("Please enter a field of interest.")
    
    st.header("Generate Placement Test")
    field_of_interest = user_field
    username = st.text_input("Enter your name:")

    if 'placement_test_started' not in st.session_state:
        st.session_state['placement_test_started'] = False
    if 'current_question_index' not in st.session_state:
        st.session_state['current_question_index'] = 0
    if 'total_score' not in st.session_state:
        st.session_state['total_score'] = 0
    if 'questions' not in st.session_state:
        st.session_state['questions'] = []
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    if st.button("Start Placement Test", key="start_test"):
        if field_of_interest and username:
            placement_test = genPlacementTest(field_of_interest)
            st.session_state['questions'] = [q.strip() for q in placement_test.split("\n") if q.strip()]
            st.session_state['placement_test_started'] = True
            st.session_state['current_question_index'] = 0
            st.session_state['total_score'] = 0
            st.session_state['user_answers'] = {}

    # If the placement test is started, show the questions one by one
    if st.session_state['placement_test_started']:
        total_questions = len(st.session_state['questions'])
        current_index = st.session_state['current_question_index']

        if current_index < total_questions:
            st.write(f"Question {current_index + 1}/{total_questions}")
            question = st.session_state['questions'][current_index]
            sanitized_question = question.split("?")[0] + "?" if "?" in question else question
            answer = st.text_input(f"Q{current_index + 1}: {sanitized_question}", key=f"q{current_index + 1}")

            if st.button("Submit Answer", key=f"submit_{current_index}"):
                st.session_state['user_answers'][current_index] = answer
                if answer:
                    system_prompt = (
                        f"Evaluate the answer given by the user for the question: '{sanitized_question}' and give a rating between 0 and 10 for relevance to the field of '{field_of_interest}'. "
                        "Only return a number between 0 and 10 as the score."
                    )
                    a = interact_with_llm(answer, system_prompt, client)
                    try:
                        score = int(a) / 10
                        st.session_state['total_score'] += score
                    except ValueError:
                        st.write("Error in score evaluation. Please check your input.")
                
                st.session_state['current_question_index'] += 1

        if st.session_state['current_question_index'] >= total_questions:
            total_score = int(st.session_state['total_score'])
            posn = interact_with_llm(str(total_score), "Analyse the score, the score is out of 10 and also give the user a position in the roadmap based on his score, here is the roadmap {roadmap_items}", client)
            placement_level = posn

            st.write(f"Based on your answers, your total score is {total_score}/{total_questions}.")
            st.write(f"Your recommended starting level is: **{placement_level}**")
            
            roadmap = genRoadmap(field_of_interest)
            save_user_data(username, roadmap, field_of_interest, placement_level)
            st.write("Your progress and placement have been saved.")
            
            st.session_state['placement_test_started'] = False
            st.session_state['current_question_index'] = 0

    # Section to check user level and field
    st.header("Check User Level & Field")
    search_username = st.text_input("Enter a username to check their level and field:")
    if st.button("Search User"):
        user_info = get_user_data(search_username)
        if user_info:
            st.write(f"**Username:** {user_info['username']}")
            st.write(f"**Field of Interest:** {user_info['field_of_interest']}")
            st.write(f"**Placement Level:** {user_info['placement_level']}")
            st.write("**Learning Roadmap:**")
            roadmap_items = [item.strip() for item in user_info['roadmap'].split(",")]
            st.markdown("<ul>" + "".join([f"<li>{item}</li>" for item in roadmap_items]) + "</ul>", unsafe_allow_html=True)
        else:
            st.error("User not found.")

if __name__ == "__main__":
    main()
