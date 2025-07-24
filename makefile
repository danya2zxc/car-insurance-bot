# ===============================
# Constants
# ===============================
PYTHON := poetry run python
RUFF := poetry run ruff

# ===============================
# Phony targets
# ===============================
.PHONY: run start lint fix

# ===============================
# Development
# ===============================

# Run the bot once
run:
	$(PYTHON) -m app.main

# Run the bot with automatic restart on file changes
start:
	poetry run watchmedo auto-restart --patterns="*.py" --recursive -- $(PYTHON) -m app.main

# ===============================
# Code Quality
# ===============================

# Check code for errors and style issues
lint:
	$(RUFF) check .

# Automatically fix errors and format code
fix:
	$(RUFF) check . --fix
	$(RUFF) format .


# Run tests 
test:
	poetry run pytest


# Run linters and tests
check:
	make lint
	make test
