import os
import streamlit as st
import anthropic
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=API_KEY)

# Streamlit UI
st.set_page_config(page_title="Claude AI Chatbot", page_icon="🤖")
st.title("🤖 Chat with HeyDoc")

# Store chat history
if "messages" not in st.session_state:
 st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
 with st.chat_message(message["role"]):
  st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...")
if user_input:
 # Add user message to history
 st.session_state.messages.append({"role": "user", "content": user_input})
 with st.chat_message("user"):
  st.markdown(user_input)
 
 # Get response from Claude
 with st.chat_message("assistant"):
  response = client.messages.create(
 model="claude-3-opus-20240229", # Use the latest Claude model
 max_tokens=300,
 messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
 )
 
 assistant_reply = response.content[0].text
 st.markdown(assistant_reply)
 
 # Store response in chat history
 st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
