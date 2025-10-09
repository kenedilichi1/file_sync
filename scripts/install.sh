#!/bin/bash

set -e

echo "🚀 Installing FileSync..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.0"

if [ $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) -ne 1 ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv filesync_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source filesync_env/bin/activate

# Install package in development mode
echo "📥 Installing FileSync..."
pip install -e .

echo "✅ Installation complete!"
echo ""
echo "To run FileSync:"
echo "  source filesync_env/bin/activate"
echo "  filesync --gui"
echo ""
echo "Or use the run script:"
echo "  ./scripts/run.sh"