import streamlit as st
import openai
import os
import time

# Set your OpenAI API key securely as an environment variable or load it here
openai.api_key = "API KEY HERE"

# Configure Streamlit page
st.set_page_config(page_title="MedicalRAG Chat", page_icon="💬", layout="wide")

st.title("💬 MedicalRAG")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

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

user_input = st.text_input("Type your message:", key="user_input")

# Handle message submission
if st.button("Send") and user_input:
    # Append user message to the conversation
    st.session_state.conversations[active_conversation].append(("user", user_input))
    
    # Define context for the assistant
    context = (
        "Possible diseases and treatments based on the symptoms provided:\n"
        "1. COVID-19: The recommended treatment is to see a doctor for proper testing and guidance.\n"
        "2. Common Cold: The recommended treatment is to drink warm fluids to help alleviate symptoms.\n"
    )

    # Prepare prompt
    prompt = (
        f"{context}\n"
        "Using only the information above, craft a message for the user. "
        "Do not add any extra information or make any assumptions. "
        "Follow this format:\n"
        "Possible Conditions: bulleted list[List the conditions]\n"
        "Recommended Actions: bulleted list [List the actions based on the treatments provided]\n"
        "Final Advice: [Encourage consulting a doctor if symptoms persist]"
    )

    # Placeholder to show the response
    response_placeholder = st.empty()
    full_response = ""

    # Call OpenAI API to get response in streaming mode
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" or "gpt-4-turbo" if available and needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True  # Enable streaming
        )
        
        # Stream the response chunks and display them in real time without extra formatting
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    # Append content to full_response
                    text_chunk = delta["content"]
                    full_response += text_chunk
                    
                    # Display the response as it comes without additional bullet formatting
                    response_placeholder.markdown(f"**MedicalRAG:**\n\n{full_response}")

        # Append the full response to the conversation as received
        st.session_state.conversations[active_conversation].append(("MedicalRAG", full_response))
        
    except Exception as e:
        st.error(f"Error in API call: {e}")