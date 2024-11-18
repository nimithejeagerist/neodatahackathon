import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# Configure Streamlit page
st.set_page_config(page_title="MedicalRAG Chat", page_icon="💬", layout="wide")
st.title("💬 MedicalRAG")
st.caption("🚀 A Streamlit chatbot powered by FastAPI")

load_dotenv()

# Backend API URL
API_URL = "http://127.0.0.1:8000/query"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state for conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = {"Conversation 1": []}  # Default conversation
if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = "Conversation 1"

# Sidebar for selecting or adding conversations
st.sidebar.title("Conversations")
conversation_names = list(st.session_state.conversations.keys())

# Add new conversation
if st.sidebar.button("➕ Start New Conversation"):
    new_name = f"Conversation {len(st.session_state.conversations) + 1}"
    st.session_state.conversations[new_name] = []
    st.session_state.active_conversation = new_name

# Display all conversation names in the sidebar
for name in conversation_names:
    if st.sidebar.button(name):
        st.session_state.active_conversation = name

# Get the current active conversation
active_conversation = st.session_state.active_conversation

# Display current conversation history
st.subheader(f"🗨️ {active_conversation}")
for role, text in st.session_state.conversations[active_conversation]:
    if role == "user":
        st.markdown(f"**User:** {text}")
    else:
        st.markdown(f"**MedicalRAG:** {text}")

# Text input for user message
if "user_input" not in st.session_state:
    st.session_state.user_input = ""  # Initial value for user input

user_input = st.text_input("Type your symptoms (comma-separated):", key="user_input")

def extract_symptoms(user_input):
    try:
        prompt = (
            "Extract relevant medical symptoms from the following user input. "
            "Provide a comma-separated list of symptoms and do not include any unrelated terms:\n"
            f"User input: \"{user_input}\""
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        extracted_symptoms = response.choices[0].message.content.strip()
        
        # Convert to a list of symptoms
        symptoms = [symptom.strip().lower() for symptom in extracted_symptoms.split(",")]
        return symptoms
    except Exception as e:
        st.error(f"Error extracting symptoms: {e}")
        return []

# Handle message submission
if st.button("Send") and user_input:
    # Append user message to the conversation
    st.session_state.conversations[active_conversation].append(("user", user_input))

    # Tokenize the input symptoms
    symptoms = extract_symptoms(user_input)

    # Make a POST request to the FastAPI backend
    try:
        response = requests.post(API_URL, json={"symptoms": symptoms})
        if response.status_code == 200:
            # Get the response from the backend
            backend_response = response.json().get("response", "No response received.")
            st.session_state.conversations[active_conversation].append(("MedicalRAG", backend_response))
            st.markdown(f"**MedicalRAG:** {backend_response}")
        else:
            st.error(f"Error from backend: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception occurred while calling backend API: {e}")