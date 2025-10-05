#!/usr/bin/env python3
"""
LocalSync GUI Launcher
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing from the main module
    from localsync import main
    
    # Force GUI mode
    sys.argv.append('--gui')
    main()
    
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install LocalSync first:")
    print("pip install -e .")
    input("\nPress Enter to exit...")
except Exception as e:
    print(f"Unexpected error: {e}")
    input("\nPress Enter to exit...")