from pydantic import ValidationError
import json
from .models import FunctionDefinition, PromptItem


def load_function_definitions(path: str) -> list[FunctionDefinition]:
    """Loads function definitions from a JSON file, it handles potential errors
    such as file not found, invalid JSON, and validation errors, it also
    checks that the loaded data is a list of dictionaries before attempting to
    validate it against the FunctionDefinition model."""
    try:
        with open(path, 'r') as e:

            try:
                data = json.load(e)
            except json.JSONDecodeError:
                raise ValueError(
                    f"Error: The file {path} contains invalid JSON.")

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: The file {path} was not found.")
    if not isinstance(data, list):
        raise ValueError(f"Error: The file {path} does not contain a list of "
                         "function definitions.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"Error: The file {path} contains invalid function "
                         "definitions.")
    try:
        function_definitions = [
            FunctionDefinition.model_validate(item) for item in data]
    except ValidationError as f:
        raise ValueError(f"Error: The file {path} contains invalid function "
                         f"definitions: {f}")
    return function_definitions


def load_prompt_items(path: str) -> list[PromptItem]:
    """Loads prompt items from a JSON file, it handles potential errors such as
    file not found, invalid JSON, and validation errors, it also checks that
    the loaded data is a list of dictionaries before attempting to validate it
    against the PromptItem model."""
    try:
        with open(path, 'r') as e:

            try:
                data = json.load(e)
            except json.JSONDecodeError:
                raise ValueError(
                    f"Error: The file {path} contains invalid JSON.")

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: The file {path} was not found.")
    if not isinstance(data, list):
        raise ValueError(f"Error: The file {path} does not contain a "
                         "list of prompts.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"Error: The file {path} contains invalid "
                         "prompt items.")
    try:
        prompt_items = [
            PromptItem.model_validate(item) for item in data]
    except ValidationError as f:
        raise ValueError(f"Error: The file {path} contains invalid "
                         f"prompt items: {f}")
    return prompt_items
