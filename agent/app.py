from typing import List, Dict, Optional
import anthropic
import yaml
import os 
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from backend.app.services.medical_api import get_symptoms, get_specialisations
from dotenv import load_dotenv
import os

load_dotenv() 

class MedicalAssistantLLM:
    def __init__(self, anthropic_api_key: str, prompt_path: str = "prompt.yaml"):
        """
        Initialize the Medical Assistant LLM component
        """
        self.client = anthropic.Client(api_key=anthropic_api_key)
        self.conversation_history = []
        self.system_prompt = self._load_system_prompt(prompt_path)

    def _load_system_prompt(self, prompt_path: str) -> str:
        """
        Load system prompt from YAML file
        
        Returns:
            str: The system prompt content
        """
        try:
            with open(prompt_path, 'r') as file:
                prompts = yaml.safe_load(file)
                return prompts['system_prompt']  # Return just the content string
        except Exception as e:
            raise Exception(f"Error loading prompt file: {str(e)}")

    def process_message(self, user_input: str) -> str:
        """
        Process a single user message and return assistant's response
        """
        try:
            # Get response from Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=self.system_prompt,  # Pass the prompt string directly
                messages=[
                    *self.conversation_history,
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )

            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response.content[0].text}
            ])

            return response.content[0].text

        except Exception as e:
            print(f"Detailed error: {str(e)}")  # Added detailed error logging
            return f"Error processing message: {str(e)}"

    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """Return the current conversation history"""
        return self.conversation_history

    def reload_prompt(self, prompt_path: str = "prompt.yaml"):
        """Reload the system prompt from the YAML file"""
        self.system_prompt = self._load_system_prompt(prompt_path)


def main():
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    try:
        # Initialize the LLM component
        medical_llm = MedicalAssistantLLM(
            anthropic_api_key=api_key,
            prompt_path="prompt.yaml"
        )
        
        # First interaction - Symptoms
        print("Sending first message...")
        response = medical_llm.process_message(
            "I have a severe headache and fever for 2 days"
        )
        print("Response 1:", response)
        print("-" * 50)
        
        # Second interaction - Patient Info
        print("Sending second message...")
        response = medical_llm.process_message(
            "I'm a 35 year old male in Paris"
        )
        print("Response 2:", response)
        print("-" * 50)
            
    except Exception as e:
        print(f"Error during conversation: {str(e)}")

 
if __name__ == "__main__":
    #main()
    #print(get_symptoms())
    print(get_specialisations([101],"male",1990))
