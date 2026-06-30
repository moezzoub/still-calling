import os
from pydantic import ValidationError
from typing import Any
from llm_sdk import Small_LLM_Model
from .models import PromptItem, FunctionDefinition, FunctionCall


MODEL_NAME = os.getenv("CALLMEMAYBE_MODEL", "Qwen/Qwen3-0.6B")
LLM = Small_LLM_Model(model_name=MODEL_NAME)

DEBUG_MODE = os.getenv("CALLMEMAYBE_DEBUG", "0") == "1"
DEBUG_LOG_PATH = "data/output/generation_debug.log"


def debug_log(message: str) -> None:
    """Log a debug message when debug mode is enabled."""
    if not DEBUG_MODE:
        return
    os.makedirs("data/output", exist_ok=True)
    with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(message + "\n")


def generate_text(prompt: str, max_tokens: int) -> str | Any:
    """Generate only the model output suffix and stop early when a full JSON
    object appears complete."""
    input_ids = LLM.encode(prompt).tolist()[0]
    prompt_len = len(input_ids)
    generated_text = ""

    for _ in range(max_tokens):
        logits = LLM.get_logits_from_input_ids(input_ids)
        next_token_id = logits.index(max(logits))
        input_ids.append(next_token_id)

        generated_text = LLM.decode(input_ids[prompt_len:])
        generated_text = generated_text.replace("```json", "")
        generated_text = generated_text.replace("```", "").strip()

        try:
            extract_first_json_object(generated_text)
            return generated_text
        except ValueError:
            continue
    return generated_text


def build_llm_prompt(one_prompt: PromptItem,
                     function_definitions: list[FunctionDefinition],
                     ) -> str:
    """Build the prompt sent to the LLM."""
    prompt = "You have to select the correct function "
    prompt += "based on a user request.\n"
    prompt += "MUST return ONLY valid JSON.\n"
    prompt += "If the request asks to replace, substitute, or transform "
    prompt += "matching parts of a string, choose the regex substitution "
    prompt += "function, not a math function.\n"
    prompt += "- If the request asks to replace numbers inside a string, "
    prompt += "use fn_substitute_string_with_regex, not a math function.\n"
    prompt += "For square root request, do NOT split one number into numbers."

    prompt += "\nAvailable functions:\n"
    for index, func in enumerate(function_definitions, start=1):
        param_str = ", ".join(
            f"{name}: {parameter.type}"
            for name, parameter in func.parameters.items()
        )
        prompt += f"{index} - {func.name}({param_str}) - {func.description}\n"

    prompt += "\nUser request:\n"
    prompt += one_prompt.prompt + "\n"

    prompt += "\nReturn only one JSON object with two fields:\n"
    prompt += "- function: the function name\n"
    prompt += "- arguments: an object containing the arguments\n"
    return prompt


def extract_first_json_object(text: str) -> str:
    """Extract the first complete JSON object from text."""
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM response.")

    brace_count = 0
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
            brace_count += 1
        elif char == "}":
            brace_count -= 1

            if brace_count == 0:
                end = start + index + 1
                return text[start:end]

    raise ValueError("No complete JSON object found in LLM response.")


def generate_function_call(
     prompt: PromptItem, fd: list[FunctionDefinition]) -> FunctionCall | Any:
    """Generate, extract, and validate a function call."""
    raw_model_prompt = build_llm_prompt(prompt, fd)
    raw_output = generate_text(raw_model_prompt, max_tokens=50)

    debug_log("=" * 80)
    debug_log(f"PROMPT: {prompt.prompt}")
    debug_log("RAW OUTPUT:")
    debug_log(raw_output)

    generated_only = raw_output.strip()
    generated_only = generated_only.replace("```json", "").replace("```", "")

    answer_pos = generated_only.rfind("Answer:")
    if answer_pos != -1:
        search_zone = generated_only[answer_pos + len("Answer:"):].strip()
    else:
        search_zone = generated_only

    json_text = extract_first_json_object(search_zone)

    debug_log("EXTRACTED JSON:")
    debug_log(json_text)

    try:
        return FunctionCall.model_validate_json(json_text)
    except ValidationError as exc:
        raise ValueError(
            "No valid JSON output found in LLM response.") from exc
