import os
from typing import Any
import json


def write_function_calls(path: str, results: list[dict[str, Any]]) -> None:
    """Writes the generated function calls to a JSON file, it creates the
    output directory if it does not exist, and handles any potential
    IO errors, it also formats the JSON output with indentation for better
    readability."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing to file {path}: {e}")
