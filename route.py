import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

@st.cache
def generate_response(user_input, answers):
    # Combine the answers from the knowledge graph into a single string
    answers_str = "; ".join(answers)

    # New prompt that includes the user input and the relevant answers
    prompt = (
        f"You received the following input from a user: \"{user_input}\".\n"
        f"Based on their input, you found the following relevant information:\n"
        f"\"{answers_str}\".\n\n"
        "Please craft a detailed response for the user. Make sure to:\n"
        "State that the results were obtained from the National Institute of Health databases. This is IMPORTANT"
        "- Directly address the user's input and explain how it relates to the retrieved information.\n"
        "- You must relate it to the retrieved options. This is not optional."
        "- Avoid providing ambiguous or unrelated information.\n"
        "- If any terms seem complex, give a brief explanation in simple language.\n"
        "- End the message with advice to consult a healthcare professional if needed.\n\n"
        "Respond in this structured format:\n"
        "Related Findings: [Summarize the main conditions or issues based on the input]\n"
        "Treatment Suggestions: [Provide recommended actions based on the findings]\n"
        "Clarifications: [Explain any complex terms, if necessary]\n"
        "Final Advice: [Encourage the user to seek professional help if symptoms persist]"
    )

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()