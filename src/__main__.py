from .loader import load_function_definitions, load_prompt_items
from .models import FunctionCall, PromptItem # noqa
from .generator import generate_function_call
from .writer import write_function_calls
import argparse


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments for the program."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition", type=str,
                        default="data/input/functions_definition.json")
    parser.add_argument("--input", type=str,
                        default="data/input/function_calling_tests.json")
    parser.add_argument("--output", type=str,
                        default="data/output/function_calling_results.json")
    args = parser.parse_args()
    return args


def main() -> None:
    """Main function to execute the program."""
    args = parse_args()
    try:
        funcD = load_function_definitions(args.functions_definition)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading function definitions: {e}")
        exit(1)

    try:
        prompt = load_prompt_items(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading prompt items: {e}")
        exit(1)

    results = []
    for prompt1 in prompt:
        try:
            result = generate_function_call(prompt1, funcD)
        except ValueError as e:
            print(f"Error generating FC for prompt '{prompt1.prompt}':{e}")
            continue

        matched_function = None
        for function in funcD:
            if result.function == function.name:
                matched_function = function
                break

        if matched_function is None:
            print(f"Warning: Generated function '{result.function}' "
                  "does not match any defined function for prompt: "
                  f"{prompt1.prompt}")
        else:
            expected_keys = set(matched_function.parameters.keys())
            result_keys = set(result.arguments.keys())

            if expected_keys != result_keys:
                print(f"Warning: Bad arguments for prompt: "
                      f"{prompt1.prompt}")
                print(result)

        results.append({
            "prompt": prompt1.prompt,
            "name": result.function,
            "parameters": result.arguments,
        })
    try:
        write_function_calls(args.output, results)
    except OSError as e:
        print(f"Error writing function calls: {e}")
        exit(1)


if __name__ == "__main__":
    main()
