import streamlit as st
import random

st.set_page_config(layout="centered", init_sidebar=False)

messages = [
    "Hello there! 👋 Welcome to our chat app.",
    "We're glad to have you here. 😊",
    "Feel free to ask us anything, we're always happy to help.",
    "What's on your mind today?"
]

colors = ["#4286f4", "#34a853"]  # You can customize these colors as you wish
chat_bubbles = st.empty()

for i, msg in enumerate(messages):
    color = colors[i % len(colors)]  # Alternate colors
chat_bubbles.markdown(f"<span style='background-color: {color}; padding: 10px; border-radius: 15px;'>{msg}</span>",
                         unsafe_allow_html=True)

# Dummy input field for demonstration purposes
st.text_input(label="Type your message...", key="input")

st.button("Send")
