*This project has been created as part of the 42 curriculum by moezzoub.*

# CallMeMaybe

## Description

CallMeMaybe is a function-calling system powered by a local Large Language Model (LLM).  
The goal of the project is to transform natural language prompts into structured function calls using constrained decoding and validation.

The program:
- Reads function definitions from a JSON file
- Reads natural language prompts
- Uses an LLM to select the correct function and arguments
- Extracts and validates the generated JSON
- Outputs a strictly formatted JSON file matching the required schema

This project focuses on **LLM control**, **structured generation**, and **robust validation**.

---

## Instructions

### Installation

```bash
uv sync
```

### Run the program
```bash
uv run python -m src
```

### Lint
```bash
make lint
```

### Example Usage
```bash
uv run python -m src
```
OR
```bash
uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json
```

---

## Algorithm Explanation (Constrained Decoding)

The main challenge is forcing the LLM to produce valid structured JSON.

The approach used:

1. Build a structured prompt including:
- clear instructions
- available functions and parameters
- the user request
2. Generate tokens step by step using:
```python
get_logits_from_input_ids
```
3. the generation process is guided toward structured JSON output and validated against the expected schema before writing results
4. Stop generation early when a complete JSON object is detected:
- detect {
- track braces ({ / })
- stop when balanced
5. Extract only the JSON part from the raw output
6. Validate the result using a strict schema (FunctionCall)

This ensures:
- minimal extra text
- valid JSON extraction
- correct structure

---

## Design Decisions

1. Manual JSON extraction

Instead of trusting the LLM output, the program:
- scans for { ... }
- extracts only valid JSON

Reason:
LLMs often produce extra text or invalid formatting.

2. Validation with Pydantic

All outputs are validated against a strict model:
- function name
- parameters
- types

Reason:
Guarantees compliance with the subject and prevents invalid outputs.


3. Environment-based configuration

The model can be changed via environment variable:
```bash
CALLMEMAYBE_MODEL=Qwen/Qwen3-0.6B
```

Reason:
Supports multiple models without modifying the code.

---

## Performance Analysis

### Speed

Initial implementation:
- ~38 minutes

Optimized version:
- ~5 minutes

Optimizations:
- early stopping when JSON is complete
- reduced token generation
- minimal prompt size

### Accuracy

Accuracy is ensured through:
- strict validation
- controlled decoding
- strict argument validation

### Reliability

The system is robust against:
- extra LLM text
- malformed JSON
- incorrect arguments

Invalid outputs are detected and handled safely.

---

## Challenges Faced

1. Enforcing strict JSON output

Problem:
LLM generates text + JSON + noise

Solution:
- extract JSON manually
- ignore everything else

2. Matching function parameters exactly

Problem:
LLM may use wrong keys

Solution:
- compare expected vs generated keys
- correct specific cases when needed

3. Performance issues

Problem:
Generation was too slow (~38 minutes)

Solution:
- stop generation early when JSON is complete
- reduce max tokens

4. LLM inconsistency

Problem:
Same prompt → different outputs

Solution:
- constrained function selection
- deterministic validation
---

## Testing Strategy

Validation is done at multiple levels:
1. JSON structure validation
2. Function existence check
3. Parameter key matching
4. Type consistency

Additionally:
- moulinette tests used as final validation
- manual tests for edge cases

---

## Resources
- LLM tokenization and decoding concepts
- Pydantic documentation
- JSON specification
- LLM function calling concepts

---

## Use of AI

AI was used to:
- understand constrained decoding concepts
- debug edge cases
- improve prompt design

Core logic and decisions were implemented and validated manually.

---
## Project Structure
```
src/
├── __main__.py
├── generator.py
├── loader.py
├── models.py
└── writer.py

data/
├── input/
└── output/ (Generated at runtime)
```

## Final Notes
- The core logic was stabilized before adding bonuses
- All bonuses were added without modifying grading behavior
- The project focuses on correctness, robustness, and control over LLM output

---
