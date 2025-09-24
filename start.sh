#!/bin/bash
# LocalSync Easy Starter for Linux/macOS

echo "🚀 Starting LocalSync..."
echo "⏳ Please wait..."

# Check if installed
if ! command -v localsync &> /dev/null; then
    echo "❌ LocalSync not found. Running installer..."
    python3 install.py
    exit 1
fi

# Run LocalSync
localsync

# If closed, show message
echo ""
echo "👋 LocalSync closed. To restart, just run 'localsync' again!"
echo "💡 Keep it running in the background to receive files."