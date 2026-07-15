#!/bin/bash
# Get directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Run the CLI using uv run to handle dependencies
uv run python app/cli.py
