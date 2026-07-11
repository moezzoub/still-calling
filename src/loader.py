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

    functions_definition = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"Error: the function item #{index + 1}"
                  f"is not a object, skip")
            continue
        try:
            functions_definition.append(
                FunctionDefinition.model_validate(item)
                )
        except ValidationError as f:
            print(f"Error : the function item #{index + 1}"
                  f" is invalid: {f}. skip.")
            continue
    return functions_definition


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

    prompt_items = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"Error: prompt item #{index + 1}"
                  f"is not an object, skip.")
            continue
        try:
            prompt_items.append(PromptItem.model_validate(item))
        except ValidationError as e:
            print(f"Error: prompt item #{index + 1} is invalid: {e}. skip.")
            continue
    return prompt_items
