from groq import Groq
import streamlit as st

client = Groq(api_key="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")

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

def genRoadmap(user_interest):
    system_prompt = "Based on the user's interest given by the user, generate a comprehensive learning roadmap. The roadmap should include key milestones, starting from basic concepts to more advanced topics, presented in a logical order. Each milestone or point in the roadmap should be separated by a comma."
    roadmap = interact_with_llm(user_interest, system_prompt, client)
    return roadmap

def genPlacementTest(userPos, field_of_interest):
    system_prompt = (
        f"Generate a placement test to evaluate the overall knowledge of a user in the field of {field_of_interest}. "
        "Based on the test results, determine where the user should start in the learning roadmap. "
        "Include questions that assess basic, intermediate, and advanced concepts, and provide a suggestion on where the user should continue from."
    )
    test = interact_with_llm(userPos, system_prompt, client)
    return test

# Streamlit UI
def main():
    st.title("Learning Roadmap & Placement Test Generator")
    
    # Roadmap Generator
    st.header("Generate Learning Roadmap")
    user_interest = st.text_input("Enter the field you're interested in (e.g., 'Convolutional Neural Networks'):")
    if st.button("Generate Roadmap"):
        if user_interest:
            roadmap = genRoadmap(user_interest)
            st.write("### Learning Roadmap:")
            st.write(roadmap)
        else:
            st.error("Please enter a field of interest.")

    st.header("Generate Placement Test")
    field_of_interest = st.text_input("Enter the field for the placement test:")
    if st.button("Generate Placement Test"):
        if field_of_interest:
            user_position = "User's current understanding level" 
            placement_test = genPlacementTest(user_position, field_of_interest)
            st.write("### Placement Test:")
            st.write(placement_test)
        else:
            st.error("Please enter a field for the placement test.")

if __name__ == "__main__":
    main()
