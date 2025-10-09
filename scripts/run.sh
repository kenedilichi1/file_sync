#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/filesync_env" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/filesync_env/bin/activate"

echo "🚀 Starting FileSync..."

# Run FileSync as a Python module (so relative imports work)
cd "$PROJECT_ROOT"
python -m src.cli "$@"
