import streamlit as st
import requests
import os
import threading
import uvicorn
from dotenv import load_dotenv
from openai import OpenAI
from api import app as fastapi_app
from multiprocessing import Process

# Load environment variables
load_dotenv()
API_URL = "http://127.0.0.1:8000/query"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to start the FastAPI server
def start_fastapi():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

# Start FastAPI in a separate process
thread = threading.Thread(target=start_fastapi, daemon=True)
thread.start()

# Configure Streamlit page
st.set_page_config(page_title="MedicalRAG Chat", page_icon="💬", layout="wide")
st.title("💬 MedicalRAG")
st.caption("🚀 A Streamlit chatbot powered by FastAPI")

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations = {"Conversation 1": []}
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
user_input = st.text_input("Type your symptoms (comma-separated):")

# Function to extract symptoms
def extract_symptoms(user_input):
    try:
        prompt = (
            "The following user input contains a description of a health condition. "
            "Identify any specific medical symptoms, explicitly mentioned disease names, and any treatments described. "
            "Provide a comma-separated list of symptoms, diseases, and treatments mentioned in the input. "
            "If the input includes a disease name (e.g., 'COVID-19', 'flu') or a treatment (e.g., 'antibiotics', 'Tylenol'), include them as well:\n"
            f"User input: \"{user_input}\""
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        extracted_symptoms = response.choices[0].message.content.strip()
        symptoms = [symptom.strip().lower() for symptom in extracted_symptoms.split(",")]
        return symptoms
    except Exception as e:
        st.error(f"Error extracting symptoms: {e}")
        return []

# Handle message submission
if st.button("Send") and user_input:
    st.session_state.conversations[active_conversation].append(("user", user_input))
    symptoms = extract_symptoms(user_input)

    # Make a POST request to the FastAPI backend    
    try:
        # Include both symptoms and the original user input in the payload
        payload = {
            "symptoms": symptoms,
            "user_input": user_input
        }
        
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            backend_response = response.json().get("response", "No response received.")
            st.session_state.conversations[active_conversation].append(("MedicalRAG", backend_response))
            st.markdown(f"**MedicalRAG:** {backend_response}")
        else:
            st.error(f"Error from backend: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception occurred while calling backend API: {e}")

# Main app function
def main():
    print("App is running!")

if __name__ == "__main__":
    main()