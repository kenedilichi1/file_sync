#!/usr/bin/env python3
"""
LocalSync Easy Installer - Simple cross-platform version
"""

import os
import sys
import platform
import subprocess
import time

class SimpleInstaller:
    def __init__(self):
        self.system = platform.system()
        
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
        print(f"⏳ {description}...")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} completed!")
                return True
            else:
                print(f"❌ {description} failed")
                return False
        except Exception as e:
            print(f"❌ {description} error: {e}")
            return False
    
    def check_python(self):
        self.print_header("Checking Python")
        
        # Try python3 first, then python
        for cmd in ["python3", "python"]:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Python found: {result.stdout.strip()}")
                    self.python_cmd = cmd
                    self.pip_cmd = cmd.replace("python", "pip")
                    return True
            except:
                continue
        
        print("❌ Python not found")
        print("\nPlease install Python 3.7+ from: https://python.org/downloads")
        return False
    
    def install_localsync(self):
        self.print_header("Installing LocalSync")
        
        commands = [
            (f"{self.pip_cmd} install --upgrade pip", "Updating pip"),
            (f"{self.pip_cmd} install -e .", "Installing LocalSync"),
        ]
        
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                return False
        return True
    
    def create_easy_launchers(self):
        self.print_header("Creating Easy Launchers")
        
        # Create platform-specific launcher
        if self.system == "Windows":
            self._create_windows_launcher()
        else:
            self._create_unix_launcher()
        
        print("✅ Easy launchers created!")
    
    def _create_windows_launcher(self):
        """Create Windows batch file"""
        batch_content = """@echo off
echo Starting LocalSync...
echo.
python -c "import localsync.cli; localsync.cli.main()"
echo.
echo LocalSync has closed.
echo You can run it again by double-clicking this file.
pause
"""
        
        try:
            with open("Start-LocalSync.bat", "w") as f:
                f.write(batch_content)
            print("✅ Created 'Start-LocalSync.bat'")
            print("   Double-click this file to run LocalSync!")
        except Exception as e:
            print(f"⚠️  Could not create launcher: {e}")
    
    def _create_unix_launcher(self):
        """Create Unix shell script"""
        script_content = """#!/bin/bash
echo "🚀 Starting LocalSync..."
echo "⏳ Please wait..."
localsync
echo ""
echo "👋 LocalSync closed. To restart, run this file again!"
echo "💡 Keep it running to receive files from others."
read -p "Press Enter to close..."
"""
        
        try:
            with open("start-localsync.sh", "w") as f:
                f.write(script_content)
            os.chmod("start-localsync.sh", 0o755)
            print("✅ Created 'start-localsync.sh'")
            print("   Double-click or run this file to start!")
        except Exception as e:
            print(f"⚠️  Could not create launcher: {e}")
    
    def show_success(self):
        self.print_header("Installation Complete! 🎉")
        
        print("""
✨ LocalSync is ready to use!

📖 QUICK START:

1. 🚀 START THE APP:
   - Windows: Double-click 'Start-LocalSync.bat'
   - Mac/Linux: Double-click 'start-localsync.sh'
   - Or type 'localsync' in terminal

2. 👤 CREATE ACCOUNT:
   - Choose '2. Register' in the menu
   - Enter username and password
   - Login with your account

3. 🔍 FIND FRIENDS:
   - Make sure friends are on same Wi-Fi
   - They need to run LocalSync too
   - Go to 'View Online Devices'

4. 📤 SEND FILES:
   - Use the easy menu system
   - Click 'Open File Explorer' to pick files
   - Select friend and send!

💡 TIP: Keep LocalSync running to receive files automatically.
""")
        
        self.wait_enter("Press Enter to start LocalSync now...")
    
    def run(self):
        """Run the complete installation"""
        try:
            self.print_header("Welcome to LocalSync!")
            self.wait_enter("Press Enter to begin easy installation...")
            
            steps = [
                ("Checking Requirements", self.check_python),
                ("Installing", self.install_localsync),
                ("Creating Launchers", self.create_easy_launchers),
            ]
            
            for step_name, step_func in steps:
                self.print_header(step_name)
                if not step_func():
                    print(f"\n❌ Installation failed at: {step_name}")
                    self.wait_enter()
                    return False
                time.sleep(1)
            
            self.show_success()
            
            # Try to launch
            try:
                subprocess.run([self.python_cmd, "-c", "import localsync.cli; localsync.cli.main()"])
            except:
                print("\n🚀 Run 'localsync' to start the application!")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Installation cancelled")
        except Exception as e:
            print(f"\n\n❌ Installation error: {e}")

def main():
    installer = SimpleInstaller()
    installer.run()

if __name__ == "__main__":
    main()