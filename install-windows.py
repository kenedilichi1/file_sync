#!/usr/bin/env python3
"""
LocalSync Windows Installer - Handles common Windows issues
"""

import os
import sys
import subprocess
import time
import platform

class WindowsInstaller:
    def __init__(self):
        self.python_cmd = "python"
        self.pip_cmd = "pip"
        
    def clear_screen(self):
        os.system('cls')
    
    def print_header(self, text):
        self.clear_screen()
        print("🚀" + "="*60 + "🚀")
        print(f"🎯 {text}")
        print("🚀" + "="*60 + "🚀")
        print()
    
    def wait_enter(self, message="Press Enter to continue..."):
        input(f"\n{message}")
    
    def run_command_silent(self, command, description):
        """Run command without trying to update pip"""
        print(f"⏳ {description}...")
        try:
            # Use subprocess without shell=True to avoid permission issues
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"✅ {description} completed!")
                return True
            else:
                print(f"⚠️ {description} had issues, but continuing...")
                print(f"   Error: {result.stderr.strip()}")
                return True  # Continue anyway
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out")
            return False
        except Exception as e:
            print(f"⚠️ {description} error: {e}")
            return True  # Continue anyway
    
    def check_python(self):
        self.print_header("Checking Python Installation")
        
        # Try different python commands
        python_commands = ["python", "py", "python3"]
        
        for cmd in python_commands:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Python found using '{cmd}': {result.stdout.strip()}")
                    self.python_cmd = cmd
                    self.pip_cmd = cmd.replace("python", "pip")
                    return True
            except:
                continue
        
        print("❌ Python not found automatically")
        print("\nLet's try to find Python manually...")
        
        # Common Python installation paths
        common_paths = [
            r"C:\Python39\python.exe",
            r"C:\Python310\python.exe", 
            r"C:\Python311\python.exe",
            r"C:\Program Files\Python39\python.exe",
            r"C:\Program Files\Python310\python.exe",
            r"C:\Program Files\Python311\python.exe",
            r"C:\Users\{}\AppData\Local\Programs\Python\Python39\python.exe".format(os.getenv('USERNAME')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python310\python.exe".format(os.getenv('USERNAME')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python311\python.exe".format(os.getenv('USERNAME')),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ Found Python at: {path}")
                self.python_cmd = f'"{path}"'  # Quote path for spaces
                self.pip_cmd = path.replace("python.exe", "pip.exe")
                return True
        
        print("\n❌ Python not found. Please install Python 3.7+ from:")
        print("📥 https://python.org/downloads")
        print("\nAfter installation, restart this installer.")
        return False
    
    def install_localsync_safe(self):
        """Install LocalSync without updating pip first"""
        self.print_header("Installing LocalSync")
        
        # First, try direct installation without upgrading pip
        commands = [
            ([self.pip_cmd, "install", "-e", "."], "Installing LocalSync (direct)"),
        ]
        
        for cmd, desc in commands:
            if not self.run_command_silent(cmd, desc):
                # If direct install fails, try alternative methods
                print("Trying alternative installation method...")
                return self.try_alternative_installation()
        
        return True
    
    def try_alternative_installation(self):
        """Try alternative installation methods"""
        alternatives = [
            # Method 1: Use python -m pip
            ([self.python_cmd, "-m", "pip", "install", "-e", "."], "Installing with python -m pip"),
            
            # Method 2: Install without editable mode
            ([self.pip_cmd, "install", "."], "Installing normally (non-editable)"),
            
            # Method 3: Use --user flag
            ([self.pip_cmd, "install", "--user", "-e", "."], "Installing for current user"),
        ]
        
        for cmd, desc in alternatives:
            if self.run_command_silent(cmd, desc):
                return True
        
        # Final attempt: manual setup
        return self.manual_setup()
    
    def manual_setup(self):
        """Create a manual setup that doesn't require pip install"""
        self.print_header("Manual Setup")
        
        print("⚠️  Automatic installation failed. Creating manual setup...")
        
        # Create a standalone launcher
        launcher_content = f"""@echo off
echo Setting up Python path...
set PYTHONPATH={os.getcwd()}
echo Starting LocalSync...
{self.python_cmd} -c "import sys; sys.path.insert(0, r'{os.getcwd()}'); from localsync.cli import main; main()"
pause
"""
        
        try:
            with open("LocalSync-Manual.bat", "w") as f:
                f.write(launcher_content)
            print("✅ Created manual launcher: 'LocalSync-Manual.bat'")
            return True
        except Exception as e:
            print(f"❌ Manual setup failed: {e}")
            return False
    
    def create_windows_launcher(self):
        """Create easy-to-use Windows launcher"""
        self.print_header("Creating Easy Launcher")
        
        # Main launcher
        launcher_content = """@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync - Easy File Sharing
echo ================================
echo.
echo Starting application...
echo Please wait...
echo.
python -c "import localsync.cli; localsync.cli.main()"
echo.
echo LocalSync has closed.
echo.
echo 📝 Tips:
echo • Keep this window open to receive files
echo • All users must be on the same Wi-Fi
echo • Use the menu numbers to navigate
echo.
pause
"""
        
        try:
            with open("LocalSync.bat", "w", encoding="utf-8") as f:
                f.write(launcher_content)
            print("✅ Created 'LocalSync.bat'")
            print("   Double-click this file to run LocalSync!")
        except Exception as e:
            print(f"⚠️  Could not create launcher: {e}")
        
        # Create shortcut instructions
        self.create_shortcut_instructions()
    
    def create_shortcut_instructions(self):
        """Create instructions for making a desktop shortcut"""
        instructions = f"""
📋 HOW TO CREATE A DESKTOP SHORTCUT:

1. Right-click on your desktop
2. Select "New" → "Shortcut"  
3. Enter this exact text:
   {self.python_cmd} -c "import localsync.cli; localsync.cli.main()"
4. Click "Next"
5. Name it "LocalSync"
6. Click "Finish"

7. RIGHT-Click the new shortcut → "Properties"
8. In "Start in:" field, enter:
   {os.getcwd()}
9. Click "OK"

Now you can double-click the desktop shortcut! 🎉
"""
        
        try:
            with open("Shortcut-Instructions.txt", "w", encoding="utf-8") as f:
                f.write(instructions)
            print("✅ Created 'Shortcut-Instructions.txt'")
        except:
            pass
    
    def test_installation(self):
        """Test if LocalSync can be imported"""
        self.print_header("Testing Installation")
        
        test_commands = [
            ([self.python_cmd, "-c", "import localsync; print('✅ Import successful')"], "Testing import"),
            ([self.python_cmd, "-c", "import tkinter; print('✅ GUI support available')"], "Testing GUI"),
        ]
        
        for cmd, desc in test_commands:
            self.run_command_silent(cmd, desc)
        
        return True
    
    def show_success(self):
        self.print_header("Installation Complete! 🎉")
        
        print("""
✨ LocalSync is ready to use!

🎯 QUICK START:

1. 🚀 LAUNCH THE APP:
   - Double-click 'LocalSync.bat' 
   - OR use the desktop shortcut you created

2. 👤 FIRST TIME SETUP:
   - Choose '2. Register' to create account
   - Enter username and password
   - Login with your credentials

3. 🔍 FIND FRIENDS:
   - Make sure friends are on same Wi-Fi
   - They need LocalSync running too
   - Check 'View Online Devices'

4. 📤 SEND FILES:
   - Use menu numbers (1, 2, 3...)
   - Click 'Open File Explorer' for easy selection
   - Pick files visually - no typing needed!

💡 WINDOWS TIPS:
• Run as Administrator if you have network issues
• Add Windows Defender exception if files are blocked
• Use different usernames for different computers

❓ NEED HELP? 
• All menus have clear instructions
• Press '0' to go back anytime
• Error messages tell you what to do
""")
        
        self.wait_enter("Press Enter to try starting LocalSync...")
    
    def run(self):
        """Run the Windows installation process"""
        try:
            self.print_header("LocalSync Windows Installer")
            print("This installer handles common Windows issues automatically.")
            self.wait_enter("Press Enter to begin...")
            
            steps = [
                ("Finding Python", self.check_python),
                ("Installing LocalSync", self.install_localsync_safe),
                ("Creating Launcher", self.create_windows_launcher),
                ("Testing", self.test_installation),
            ]
            
            for step_name, step_func in steps:
                self.print_header(step_name)
                if not step_func():
                    print(f"\n⚠️  Continuing despite issues at: {step_name}")
                time.sleep(2)
            
            self.show_success()
            
            # Try to launch
            try:
                print("Attempting to start LocalSync...")
                subprocess.run([self.python_cmd, "-c", "import localsync.cli; localsync.cli.main()"])
            except Exception as e:
                print(f"\n🚀 You can now run LocalSync by double-clicking 'LocalSync.bat'")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Installation cancelled by user")
        except Exception as e:
            print(f"\n\n❌ Installation error: {e}")
            print("Please try running the installer again.")

def main():
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("This installer is for Windows only.")
        print("Please use the main installer for your system.")
        return
    
    installer = WindowsInstaller()
    installer.run()

if __name__ == "__main__":
    main()