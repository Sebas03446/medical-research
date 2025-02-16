import os
import json
import streamlit as st
import anthropic
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=API_KEY)

# Streamlit UI
st.set_page_config(page_title="MainPage", page_icon="🤖")
st.title("🤖 Chat with HeyDoc")

# Define system prompt with strict JSON output format
SYSTEM_PROMPT = (
    "You are HeyDoc, a personal medical assistant chatbot. "
    "For every response, return exactly two doctors' details **only in JSON format** without additional text. "
    "The JSON format must be as follows:\n\n"
    "```\n"
    "[\n"
    "  {\n"
    '    "name": "Dr. Jane Smith",\n'
    '    "description": "Experienced cardiologist specializing in heart disease prevention.",\n'
    '    "picture": "https://example.com/dr-jane-smith.jpg",\n'
    '    "phone_number": "+1 123-456-7890",\n'
    '    "time_slots": ["Monday 9 AM - 11 AM", "Wednesday 2 PM - 4 PM"],\n'
    '    "price": 150,\n'
    '    "website": "https://drjanesmith.com"\n'
    "  },\n"
    "  {\n"
    '    "name": "Dr. John Doe",\n'
    '    "description": "General practitioner with expertise in preventive medicine.",\n'
    '    "picture": "https://example.com/dr-john-doe.jpg",\n'
    '    "phone_number": "+1 987-654-3210",\n'
    '    "time_slots": ["Tuesday 10 AM - 12 PM", "Thursday 1 PM - 3 PM"],\n'
    '    "price": 120,\n'
    '    "website": "https://drjohndoe.com"\n'
    "  }\n"
    "]\n"
    "```\n\n"
    "Make sure to return **only** valid JSON output without any explanations or formatting."
)

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
            model="claude-3-opus-20240229",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        )

        assistant_reply = response.content[0].text  # Claude's response

        # Attempt to parse the response as JSON
        try:
            doctors = json.loads(assistant_reply.strip())  # Ensure valid JSON
            if isinstance(doctors, list) and len(doctors) >= 2:
                col1, col2 = st.columns(2)  # Create two columns for doctor profiles
                
                for i, doctor in enumerate(doctors[:2]):  # Display two doctors
                    with (col1 if i == 0 else col2):  # Assign to column 1 or 2
                        st.image(doctor["picture"], width=150)
                        st.subheader(doctor["name"])
                        st.write(doctor["description"])
                        st.write(f"📞 **Phone:** {doctor['phone_number']}")
                        st.write(f"💰 **Price:** ${doctor['price']}")
                        st.write("🕒 **Available Slots:**")
                        for slot in doctor["time_slots"]:
                            st.write(f"- {slot}")
                        st.markdown(f"[🌐 Visit Website]({doctor['website']})", unsafe_allow_html=True)

                # Store response in chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

            else:
                st.error("Failed to extract doctor information. Please try again.")

        except json.JSONDecodeError:
            st.error("Error parsing the response. The assistant did not return valid JSON.")
