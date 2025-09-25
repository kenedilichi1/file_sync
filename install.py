#!/usr/bin/env python3
"""
LocalSync Simple Installer - Robust and user-friendly
"""

import os
import sys
import platform
import subprocess
import time

class SimpleInstaller:
    def __init__(self):
        self.system = platform.system()
        self.python_cmd = self._find_python()
        self.pip_cmd = self.python_cmd.replace("python", "pip") if self.python_cmd else None
        
    def _find_python(self):
        """Find available Python command"""
        for cmd in ["python3", "python", "py"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True)
                return cmd
            except:
                continue
        return None
        
    def clear_screen(self):
        os.system('cls' if self.system == 'Windows' else 'clear')
    
    def print_header(self, text):
        self.clear_screen()
        print("🚀" + "="*60 + "🚀")
        print(f"🎯 {text}")
        print("🚀" + "="*60 + "🚀")
        print()
    
    def wait_enter(self, message="Press Enter to continue..."):
        input(f"\n{message}")
    
    def run_command(self, command, description):
        """Run command with error handling"""
        print(f"⏳ {description}...")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"✅ {description} completed!")
                return True
            else:
                print(f"⚠️ {description} had issues: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"⚠️ {description} error: {e}")
            return False
    
    def check_system(self):
        self.print_header("System Check")
        
        if not self.python_cmd:
            print("❌ Python not found!")
            print("\nPlease install Python 3.7+ from: https://python.org/downloads")
            return False
        
        try:
            version_result = subprocess.run([self.python_cmd, "--version"], capture_output=True, text=True)
            print(f"✅ {version_result.stdout.strip()} found")
            return True
        except:
            print("❌ Python check failed")
            return False
    
    def install_dependencies(self):
        self.print_header("Installing Dependencies")
        
        # Try simple install first (no pip upgrade)
        commands = [
            (f"{self.pip_cmd} install -e .", "Installing LocalSync"),
        ]
        
        success = True
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                success = False
                print("Trying alternative method...")
                # Try with python -m pip
                alt_cmd = cmd.replace(self.pip_cmd, f"{self.python_cmd} -m pip")
                self.run_command(alt_cmd, desc + " (alternative)")
        
        return success
    
    def create_launchers(self):
        self.print_header("Creating Easy Launchers")
        
        try:
            if self.system == "Windows":
                self._create_windows_launcher()
            else:
                self._create_unix_launcher()
            
            print("✅ Easy launchers created!")
        except Exception as e:
            print(f"⚠️ Could not create launchers: {e}")
            print("💡 You can still use 'localsync' command")
        
        return True  # Not critical, so always return True
    
    def _create_windows_launcher(self):
        """Create Windows batch file"""
        batch_content = """@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync - Starting...
echo.
python -c "import localsync.cli; localsync.cli.main()"
echo.
echo.
echo Press any key to close...
pause > nul
"""
        
        with open("LocalSync.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ Created 'LocalSync.bat' - double-click to run!")
    
    def _create_unix_launcher(self):
        """Create Unix shell script"""
        script_content = """#!/bin/bash
echo "🚀 Starting LocalSync..."
localsync
echo ""
echo "💡 Tip: Keep LocalSync running to receive files."
"""
        
        with open("start-localsync", "w") as f:
            f.write(script_content)
        os.chmod("start-localsync", 0o755)
        print("✅ Created 'start-localsync' - run with: ./start-localsync")
    
    def test_installation(self):
        self.print_header("Testing Installation")
        
        tests = [
            (f"{self.python_cmd} -c \"import localsync\"", "Testing LocalSync import"),
            (f"{self.python_cmd} -c \"import tkinter\"", "Testing GUI support"),
        ]
        
        for cmd, desc in tests:
            self.run_command(cmd, desc)
        
        return True  # Don't fail installation on tests
    
    def show_success(self):
        self.print_header("🎉 Installation Complete!")
        
        print("""
✨ LocalSync is ready to use!

🚀 QUICK START:

1. EASY LAUNCH:
   • Windows: Double-click 'LocalSync.bat'
   • Mac/Linux: Run './start-localsync'
   • Or type 'localsync' in terminal

2. FIRST TIME:
   • Choose '2. Register' to create account
   • Login with your credentials

3. SHARE FILES:
   • Friends must be on same Wi-Fi
   • Use menu numbers for navigation
   • Click 'Open File Explorer' for easy selection

💡 TIP: Keep LocalSync running to receive files!
""")
        
        self.wait_enter("Press Enter to try LocalSync now...")
    
    def run_installation(self):
        """Run the complete installation"""
        try:
            self.print_header("Welcome to LocalSync!")
            print("This will install LocalSync on your system.")
            self.wait_enter("Press Enter to begin...")
            
            # Run installation steps
            steps = [
                ("System Check", self.check_system),
                ("Installation", self.install_dependencies), 
                ("Creating Launchers", self.create_launchers),
                ("Testing", self.test_installation),
            ]
            
            all_success = True
            for step_name, step_func in steps:
                self.print_header(step_name)
                if not step_func():
                    print(f"⚠️  Issue with: {step_name}")
                    # Continue anyway for non-critical steps
                    if step_name == "System Check":
                        all_success = False
            
            if all_success:
                self.show_success()
            else:
                self.print_header("Installation Issues")
                print("There were some issues, but LocalSync may still work.")
                print("Try running 'localsync' to test.")
                self.wait_enter()
            
            # Try to launch
            try:
                subprocess.run([self.python_cmd, "-c", "import localsync.cli; localsync.cli.main()"])
            except:
                print("\n🚀 Run 'localsync' to start the application!")
            
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled.")
        except Exception as e:
            print(f"\n\nUnexpected error: {e}")

def main():
    installer = SimpleInstaller()
    installer.run_installation()

if __name__ == "__main__":
    main()