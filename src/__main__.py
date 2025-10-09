#!/usr/bin/env python3
"""
LocalSync - Secure File Sharing Over Local Network
Main entry point for cross-platform execution
"""

import sys
import os
import platform

def main():
    """Main entry point with cross-platform support"""
    
    # Add current directory to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        from src.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've installed the required dependencies:")
        print("   pip install -e .")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()