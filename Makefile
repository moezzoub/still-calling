
install:
	uv venv
	uv sync --all-groups

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf src/__pycache__ llm_sdk/__pycache__
	find . -name "*.pyc" -delete

lint:
	uv run flake8 src
	uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude '/llm_sdk/'

lint-strict:
	uv run flake8 src
	uv run mypy src --strict


.PHONY: install run debug clean lint lint-strict
