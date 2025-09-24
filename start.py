#!/usr/bin/env python3
"""
LocalSync Starter - Simple click-to-run for Windows users
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from localsync.cli import main
    print("🚀 Starting LocalSync...")
    print("⏳ Please wait...")
    main()
except ImportError as e:
    print(f"❌ Error: {e}")
    print("\n📋 Please run the installer first:")
    print("   python install.py")
    input("\nPress Enter to exit...")
except KeyboardInterrupt:
    print("\n👋 Goodbye!")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    input("\nPress Enter to exit...")