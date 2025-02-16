from typing import Any, Dict, List, get_type_hints
from functools import wraps
import inspect


class Tool:
    """
    Decorator to create tool schemas for Claude.
    
    Usage:
        @Tool(
            name="get_weather",
            description="Get the current weather in a given location"
        )
        async def get_weather(location: str) -> Dict:
            '''
            :param location: The city and state, e.g. San Francisco, CA
            '''
            ...
    """
    _registry: List['Tool'] = []

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.function = None
        self.schema = None

    def __call__(self, func):
        self.function = func
        self.schema = self._generate_schema()
        Tool._registry.append(self)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper

    def _generate_schema(self) -> Dict[str, Any]:
        """Generate the tool schema based on function signature"""
        sig = inspect.signature(self.function)
        type_hints = get_type_hints(self.function)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter for class methods
            if param_name == 'self':
                continue
                
            param_type = type_hints.get(param_name, str)
            
            # Get parameter description from docstring
            param_doc = ""
            if self.function.__doc__:
                for line in self.function.__doc__.split('\n'):
                    if f":param {param_name}:" in line:
                        param_doc = line.split(f":param {param_name}:")[1].strip()
            
            # Map Python types to JSON schema types
            type_map = {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean"
            }
            
            properties[param_name] = {
                "type": type_map.get(param_type, "string"),
                "description": param_doc
            }
            
            # Add to required list if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    @classmethod
    def get_all_tools(cls) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools"""
        return [tool.schema for tool in cls._registry]