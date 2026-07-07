import json
import os
from typing import Any

from llm_sdk import Small_LLM_Model

from .models import FunctionCall, FunctionDefinition, PromptItem


MODEL_NAME = os.getenv("CALLMEMAYBE_MODEL", "Qwen/Qwen3-0.6B")
LLM = Small_LLM_Model(model_name=MODEL_NAME)


def encode_text(text: str) -> list[int]:
    return LLM.encode(text).tolist()[0]


def decode_tokens(tokens: list[int]) -> str:
    return LLM.decode(tokens)


def generate_text(prompt: str, max_tokens: int = 80) -> str:
    input_ids = encode_text(prompt)
    start = len(input_ids)

    for _ in range(max_tokens):
        logits = LLM.get_logits_from_input_ids(input_ids)
        next_token = logits.index(max(logits))
        input_ids.append(next_token)

        text = decode_tokens(input_ids[start:])
        if "}" in text:
            return text.replace("```json", "").replace("```", "").strip()

    return decode_tokens(input_ids[start:]).strip()


def extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found.")

    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(text[start:]):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:start + index + 1]

    raise ValueError("No complete JSON object found.")


def build_function_prompt(
    prompt: PromptItem,
    functions: list[FunctionDefinition],
) -> str:
    text = "Choose the best function for the user request.\n"
    text += "Return only the function name.\n\n"
    text += "Available functions:\n"

    for function in functions:
        params = ", ".join(
            f"{name}: {param.type}"
            for name, param in function.parameters.items()
        )
        text += f"- {function.name}({params}): {function.description}\n"

    text += f"\nUser request: {prompt.prompt}\n"
    text += "Function name:"
    return text


def choose_function_name(
    prompt: PromptItem,
    functions: list[FunctionDefinition],
) -> str:
    input_tokens = encode_text(build_function_prompt(prompt, functions))
    candidates = [encode_text(function.name) for function in functions]
    answer: list[int] = []
    position = 0

    while candidates and position < max(len(item) for item in candidates):
        allowed = {
            item[position]
            for item in candidates
            if position < len(item)
        }

        if len(allowed) == 1:
            chosen = next(iter(allowed))
        else:
            logits = LLM.get_logits_from_input_ids(input_tokens + answer)
            masked = [-float("inf")] * len(logits)
            for token_id in allowed:
                masked[token_id] = logits[token_id]
            chosen = masked.index(max(masked))

        answer.append(chosen)
        candidates = [
            item for item in candidates
            if position < len(item) and item[position] == chosen
        ]
        position += 1

        if len(candidates) == 1 and position == len(candidates[0]):
            break

    function_name = decode_tokens(answer).strip()
    valid_names = {function.name for function in functions}

    if function_name not in valid_names:
        raise ValueError(f"Invalid function selected: {function_name}")

    return function_name


def find_function(
    function_name: str,
    functions: list[FunctionDefinition],
) -> FunctionDefinition:
    for function in functions:
        if function.name == function_name:
            return function

    raise ValueError(f"Function not found: {function_name}")


def build_arguments_prompt(
    prompt: PromptItem,
    function: FunctionDefinition,
) -> str:
    text = "Extract the arguments for the selected function.\n"
    text += "Return only one JSON object.\n\n"
    text += f"User request: {prompt.prompt}\n"
    text += f"Function name: {function.name}\n"
    text += f"Function description: {function.description}\n"
    text += "Required arguments:\n"

    for name, param in function.parameters.items():
        text += f"- {name}: {param.type}\n"

    text += "\nJSON arguments:"
    return text

def fallback_arguments(
    prompt: PromptItem,
    function: FunctionDefinition,
) -> dict[str, Any]:
    text = prompt.prompt
    lower = text.lower()
    params = list(function.parameters.keys())

    if function.name == "fn_format_template":
        if "format template:" in lower:
            template = text.split(":", 1)[1].strip()
        else:
            template = text.strip()

        result = {}

        for param in params:
            if (
                "template" in param
                or "format" in param
                or "text" in param
                or "string" in param
            ):
                result[param] = template

        if not result and len(params) == 1:
            result[params[0]] = template

        if set(result.keys()) == set(params):
            return result

    raise ValueError("Fallback could not extract arguments.")


def extract_arguments(
    prompt: PromptItem,
    function: FunctionDefinition,
) -> dict[str, Any]:
    raw = generate_text(build_arguments_prompt(prompt, function), max_tokens=80)

    try:
        json_text = extract_first_json_object(raw)
        arguments = json.loads(json_text)

        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a JSON object.")

        return arguments
    except (ValueError, json.JSONDecodeError):
        return fallback_arguments(prompt, function)


def convert_value(value: Any, expected_type: str) -> Any:
    if expected_type == "number":
        return float(value)
    if expected_type == "integer":
        return int(value)
    if expected_type == "boolean":
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes"}
    if expected_type == "string":
        return str(value)
    return value


def normalize_arguments(
    arguments: dict[str, Any],
    function: FunctionDefinition,
) -> dict[str, Any]:
    expected = set(function.parameters.keys())
    received = set(arguments.keys())

    if expected != received:
        raise ValueError(
            f"Bad arguments for {function.name}: "
            f"expected {expected}, got {received}"
        )

    return {
        name: convert_value(arguments[name], param.type)
        for name, param in function.parameters.items()
    }


def generate_function_call(
    prompt: PromptItem,
    fd: list[FunctionDefinition],
) -> FunctionCall:
    function_name = choose_function_name(prompt, fd)
    function = find_function(function_name, fd)
    raw_arguments = extract_arguments(prompt, function)
    arguments = normalize_arguments(raw_arguments, function)

    return FunctionCall(function=function_name, arguments=arguments)
