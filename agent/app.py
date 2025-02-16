from typing import List, Dict, Any, Tuple, Optional
import anthropic
import yaml
import os 
import json
from dotenv import load_dotenv
from dataclasses import dataclass

from agent.services import MedicalService
from agent.tools import Tool


@dataclass
class UserInfo:
    age: int
    gender: str
    described_symptoms: List[str]


@dataclass
class DiagnosisStep:
    symptom_ids: List[int]
    specializations: List[Dict]
    final_recommendation: Optional[str] = None


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
        """Execute a tool and return its result along with error status."""
        try:
            if tool_name == "get_symptoms":
                result = await self.service.get_symptoms()
                return {"symptoms": result}, False
                
            elif tool_name == "get_specializations":
                # Parse and validate arguments
                symptom_ids = tool_args.get('symptom_ids', [])
                age = tool_args.get('age')
                gender = tool_args.get('gender')
                
                if not all([symptom_ids, age, gender]):
                    return {
                        "error": "Missing required arguments: symptom_ids, age, and gender are required"
                    }, True
                
                result = await self.service.get_specializations(
                    symptom_ids=symptom_ids,
                    age=int(age),
                    gender=str(gender).lower()
                )
                return {"specializations": result}, False
                
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
    
    async def _chain_tool_calls(self, initial_response: Any, messages: List[Dict]) -> str:
        """
        Chain multiple tool calls and their responses together.
        
        Args:
            initial_response: Initial response from Claude
            messages: Current conversation messages
        
        Returns:
            str: Final response after all tool calls are completed
        """
        try:
            current_response = initial_response
            
            while current_response.stop_reason == 'tool_use':
                for content in current_response.content:
                    if content.type == 'tool_use':
                        # Get the assistant's reasoning
                        reasoning = next(
                            (c.text for c in current_response.content if c.type == 'text'),
                            "Processing your request..."
                        )
                        
                        # Execute the tool
                        tool_result, is_error = await self._execute_tool(
                            content.name,
                            content.input
                        )

                        print(len(tool_result))

                        messages.extend([
                            {
                                "role": "assistant",
                                "content": reasoning
                            },
                            {
                                "role": "assistant",
                                "content": str(len(tool_result))
                            }
                        ])
                        
                        # Get next response from Claude
                        current_response = self.client.messages.create(
                            model=self.MODEL,
                            max_tokens=1024,
                            system=self.system_prompt,
                            messages=messages,
                            tools=Tool.get_all_tools(),
                        )
                        
                        # If this response doesn't require a tool, it's our final response
                        if current_response.stop_reason != 'tool_use':
                            return current_response.content[0].text
                        
                        # Otherwise, continue the loop for more tool calls
            
            # Return the final response text
            return current_response.content[0].text
            
        except Exception as e:
            print(f"Error in tool chain: {str(e)}")
            raise

    async def process_message(self, user_input: str) -> str:
        """
        Process a single user message and return assistant's response
        """
        try:
            messages = [
                *self.conversation_history,
                {
                    "role": "user",
                    "content": user_input
                }
            ]

            # Step 1: Call get_symptoms to retrieve the list of standardized symptoms
            symptoms_result, is_error = await self._execute_tool("get_symptoms", {})
            if is_error:
                return f"Error retrieving symptoms: {symptoms_result.get('error')}"
            string_representation = json.dumps(symptoms_result, indent=2)
            # Get response from Claude
            matching_response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1024,
                # system=self.system_prompt,  # Pass the prompt string directly
                system=f"Match the user's symptoms with the available symptoms list {symptoms_result} and prepare symptom_ids for specialization lookup.",
                messages=messages,
                tools=Tool.get_all_tools(),
                tool_choice={"type": "auto"},
            )

            # Extract matched symptom IDs from Claude's analysis
            # matched_symptom_ids = self._extract_symptom_ids(matching_response)
            # if not matched_symptom_ids:
            #     return "Error: Could not match symptoms with available list."

            # # Step 3: Call get_specializations with matched symptom IDs
            # spec_result, is_error = await self._execute_tool(
            #     "get_specializations",
            #     {
            #         "symptom_ids": matched_symptom_ids,
            #         "age": 30,  # Default age if not provided
            #         "gender": "male"  # Default gender if not provided
            #     }
            # )
            # if is_error:
            #     return f"Error retrieving specializations: {spec_result.get('error')}"

            # # Add specialization results to context
            # messages.extend([
            #     {"role": "assistant", "content": matching_response.content[0].text},
            #     {"role": "tool", "content": str(spec_result)}
            # ])

            # Get final recommendation
            # final_response = self.client.messages.create(
            #     model=self.MODEL,
            #     max_tokens=1024,
            #     system="Provide a final recommendation based on the matched symptoms and specialization results.",
            #     messages=messages,
            # )

            # final_answer = final_response.content[0].text

            # # Update conversation history
            # self.conversation_history.extend([
            #     {"role": "user", "content": user_input},
            #     {"role": "assistant", "content": final_answer}
            # ])

            return matching_response
            # return final_answer

            
            # If specialization recommendation is requested
            # if response.stop_reason == 'tool_use':
            #     tool_call = next(
            #         (c for c in response.content if c.type == 'tool_use'),
            #         None
            #     )
            #     if tool_call and tool_call.name == 'get_specializations':
            #         # Execute get_specializations
            #         spec_result, is_error = await self._execute_tool(
            #             "get_specializations",
            #             tool_call.input
            #         )
                    
                    # Add specialization result to conversation
                    # messages.extend([
                    #     {"role": "assistant", "content": response.content[0].text},
                    #     {"role": "tool", "content": str(spec_result)}
                    # ])

            # Update conversation history
            # self.conversation_history.extend([
            #     {"role": "user", "content": user_input},
            #     {"role": "assistant", "content": response}
            # ])

            # return response

        except Exception as e:
            print(f"Detailed error: {str(e)}")  
            return f"Error processing message: {str(e)}"
    

async def main():
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    assistant = MedicalAssistantLLM(
        anthropic_api_key=api_key,
        prompt_path="agent/prompt.yaml" 
    )

    try:
        print("\nQuerying about symptoms...")
        response = await assistant.process_message(
            "I have fever, and stomachache. I am a female and 26."
        )
        print(f"{response}")
        
        # for message in assistant.get_conversation_history():
        #     print(f"{message['role']}: {message['content']}\n")
          
    except Exception as e:
        print(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
