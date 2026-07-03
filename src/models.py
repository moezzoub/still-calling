from pydantic import BaseModel, field_validator
from typing import Dict, Any


class Parameter(BaseModel):
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        allowed = {"string", "number", "integer", "boolean"}
        if value not in allowed:
            raise ValueError(f"Invalid parameter type: {value}")
        return value


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
