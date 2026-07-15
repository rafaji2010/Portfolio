# Contact Book

A simple interactive CLI-based contact book application implemented in Python using Pydantic for schema validation.

## Features

- Add, view, edit, search, and delete contacts
- Import and export contacts from/to CSV files (with automatic support for Google Contacts format)
- Schema and email validation using Pydantic
- Persistent storage using JSON

## Setup & Running

This project uses `uv` for python environment and dependency management.

To run the application in development:
```bash
# Using run.sh
./run.sh

# Or directly using uv
uv run python app/cli.py
```

## Running Tests

To run the test suite:
```bash
uv run pytest
```

To run the type checker:
```bash
uv run mypy .
```
