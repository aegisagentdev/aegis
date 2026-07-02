.PHONY: install dev lint format test check clean docs

install:
	pip install -e .

dev:
	pip install -e '.[ai,dev]'

lint:
	ruff check src tests

format:
	ruff format src tests

test:
	pytest -q

check: lint test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache

docs:
	@echo "Docs are in docs/ — no build step needed (plain Markdown)."
