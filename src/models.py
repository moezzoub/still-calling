from pydantic import BaseModel
from typing import Dict, Any


class Parameter(BaseModel):
    """Represents a parameter for a function, it has a name,
    a description, and a type."""
    type: str


class FunctionDefinition(BaseModel):
    """Represents a function definition, it has a name, a description,
    a dictionary of parameters, and a return type."""
    name: str
    description: str
    parameters: Dict[str, Parameter]
    returns: Parameter


class PromptItem(BaseModel):
    """Represents a prompt item, it has a prompt string."""
    prompt: str


class FunctionCall(BaseModel):
    """Represents a function call, it has a function name and a dictionary
    of arguments."""
    function: str
    arguments: Dict[str, Any]
