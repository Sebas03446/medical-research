from typing import List, Dict, Any, Tuple
import anthropic
import yaml
import os 
from dotenv import load_dotenv
from backend.app.services.medical_api import get_symptoms, get_specialisations

from agent.services import MedicalService
from agent.tools import Tool


class MedicalAssistantLLM:
    def __init__(self, anthropic_api_key: str, prompt_path: str = "prompt.yaml"):
        """
        Initialize the Medical Assistant LLM component
        """
        self.client = anthropic.Client(api_key=anthropic_api_key)
        self.service = MedicalService()
        self.MODEL = "claude-3-5-sonnet-20241022"
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
    
    async def _execute_tool(
        self, 
        tool_name: str, 
        tool_args: Dict[str, Any]
    ) -> Tuple[Dict, bool]:
        """
        Execute a tool and return its result along with error status.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            
        Returns:
            Tuple[Dict, bool]: (result, is_error)
                - result: Tool execution result or error message
                - is_error: True if an error occurred, False otherwise
        """
        try:
            if tool_name == "get_symptoms":
                result = await self.service.get_symptoms()
                return result, False
                
            elif tool_name == "get_specializations":
                result = await self.service.get_specializations(**tool_args)
                return result, False
                
            else:
                return {
                    "error": f"Unknown tool: {tool_name}"
                }, True
                
        except Exception as e:
            return {
                "error": f"Tool execution failed: {str(e)}"
            }, True

    async def _handle_tool_calls(
        self, 
        tool_calls: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Handle multiple tool calls and collect their results.
        
        Args:
            tool_calls: List of tool calls from Claude's response
            
        Returns:
            List[Dict]: List of tool results to be added to conversation history
        """
        tool_results = []
        
        for tool_call in tool_calls:
            # Execute the tool
            result, is_error = await self._execute_tool(
                tool_call.function.name,
                tool_call.function.arguments
            )
            
            # Format the tool result
            tool_results.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": str(result),
                    "is_error": is_error
                }]
            })
            
        return tool_results
    
    async def process_message(self, user_input: str) -> str:
        """
        Process a single user message and return assistant's response
        """
        try:
            # Get response from Claude
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1024,
                system=self.system_prompt,  # Pass the prompt string directly
                messages=[
                    *self.conversation_history,
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                tools=Tool.get_all_tools(),
                tool_choice={"type": "auto"},
            )

            if response.tool_calls:
                tool_results = await self._handle_tool_calls(response.tool_calls)
                self.conversation_history.extend(tool_results)

            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response.content[0].text}
            ])

            return response.content[0].text

        except Exception as e:
            print(f"Detailed error: {str(e)}")  
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

 
if __name__ == "__main__":
    #main()
    #print(get_symptoms())
    print(get_specialisations([101],"male",1990))
