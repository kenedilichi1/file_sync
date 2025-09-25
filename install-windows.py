# windows-installer.py
import os
import sys
import subprocess
import time

def clear_screen():
    os.system('cls')

def print_header(text):
    clear_screen()
    print("🚀" + "="*60 + "🚀")
    print(f"🎯 {text}")
    print("🚀" + "="*60 + "🚀")
    print()

def wait_enter(message="Press Enter to continue..."):
    input(f"\n{message}")

def check_windows():
    """Check if we're running on Windows"""
    if os.name != 'nt':
        print("❌ This installer is for Windows only.")
        print("Please use the appropriate installer for your system.")
        wait_enter()
        return False
    return True

def find_python_windows():
    """Find Python on Windows - comprehensive search"""
    print("🔍 Looking for Python...")
    
    # Try command-line Python commands first
    commands_to_try = [
        ["python", "--version"],
        ["py", "--version"], 
        ["python3", "--version"],
    ]
    
    # Common Python installation paths
    common_paths = [
        r"C:\Python39\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Program Files\Python39\python.exe",
        r"C:\Program Files\Python310\python.exe", 
        r"C:\Program Files\Python311\python.exe",
    ]
    
    # Add user-specific paths
    username = os.getenv('USERNAME')
    if username:
        user_paths = [
            rf"C:\Users\{username}\AppData\Local\Programs\Python\Python39\python.exe",
            rf"C:\Users\{username}\AppData\Local\Programs\Python\Python310\python.exe",
            rf"C:\Users\{username}\AppData\Local\Programs\Python\Python311\python.exe",
        ]
        common_paths.extend(user_paths)
    
    # Add path-based commands
    for path in common_paths:
        if os.path.exists(path):
            commands_to_try.append([path, "--version"])
    
    # Test each command
    for cmd in commands_to_try:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                python_version = result.stdout.strip()
                print(f"✅ Found Python: {cmd[0]} ({python_version})")
                return cmd[0]
        except:
            continue
    
    print("❌ Python not found automatically")
    return None

def install_localsync(python_cmd):
    """Install LocalSync with multiple fallback methods"""
    print_header("Installing LocalSync")
    
    installation_methods = [
        # Method 1: pip install (recommended)
        {
            "name": "pip install",
            "command": [python_cmd, "-m", "pip", "install", "-e", "."],
            "timeout": 120
        },
        # Method 2: pip install without editable
        {
            "name": "pip install (simple)",
            "command": [python_cmd, "-m", "pip", "install", "."],
            "timeout": 120
        },
        # Method 3: setup.py install
        {
            "name": "setup.py install", 
            "command": [python_cmd, "setup.py", "install"],
            "timeout": 120
        },
        # Method 4: pip with --user flag
        {
            "name": "pip install (user)",
            "command": [python_cmd, "-m", "pip", "install", "--user", "-e", "."],
            "timeout": 120
        }
    ]
    
    for method in installation_methods:
        print(f"🔄 Trying {method['name']}...")
        try:
            result = subprocess.run(
                method["command"], 
                capture_output=True, 
                text=True, 
                timeout=method["timeout"]
            )
            
            if result.returncode == 0:
                print(f"✅ Success with {method['name']}!")
                return True
            else:
                print(f"⚠️ {method['name']} failed: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {method['name']} timed out")
        except Exception as e:
            print(f"❌ {method['name']} error: {e}")
    
    print("❌ All installation methods failed")
    return False

def create_windows_launcher(python_cmd):
    """Create easy-to-use batch file"""
    print_header("Creating Easy Launcher")
    
    current_dir = os.getcwd()
    
    # Simple batch file content
    batch_content = f"""@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync - Starting...
echo.
cd /D "{current_dir}"
"{python_cmd}" -c "import localsync.cli; localsync.cli.main()"
echo.
echo.
echo Press any key to exit...
pause >nul
"""
    
    try:
        with open("Run-LocalSync.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ Created 'Run-LocalSync.bat'")
        print("   📍 Location: " + os.path.join(current_dir, "Run-LocalSync.bat"))
        print("   💡 Double-click this file to run LocalSync!")
        return True
    except Exception as e:
        print(f"❌ Could not create launcher: {e}")
        return False

def create_desktop_shortcut(python_cmd):
    """Create desktop shortcut using VBS"""
    print_header("Creating Desktop Shortcut")
    
    current_dir = os.getcwd()
    
    vbs_script = f'''
Set WshShell = WScript.CreateObject("WScript.Shell")
shortcutPath = WshShell.SpecialFolders("Desktop") & "\\LocalSync.lnk"
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = "{python_cmd}"
shortcut.Arguments = "-c ""import localsync.cli; localsync.cli.main()"""
shortcut.WorkingDirectory = "{current_dir}"
shortcut.Description = "LocalSync - Easy File Sharing"
shortcut.Save
WScript.Echo "Desktop shortcut created successfully!"
'''
    
    try:
        # Write VBS script
        vbs_file = "create_shortcut.vbs"
        with open(vbs_file, "w") as f:
            f.write(vbs_script)
        
        # Run VBS script silently
        result = subprocess.run(
            ["cscript", "//B", "//Nologo", vbs_file], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        # Clean up VBS file
        try:
            os.remove(vbs_file)
        except:
            pass
        
        if result.returncode == 0:
            print("✅ Desktop shortcut created!")
            print("   📍 Look for 'LocalSync' on your desktop")
            return True
        else:
            print("⚠️ Could not create desktop shortcut")
            return False
            
    except Exception as e:
        print(f"⚠️ Desktop shortcut creation failed: {e}")
        return False

def test_installation(python_cmd):
    """Test if installation was successful"""
    print_header("Testing Installation")
    
    tests = [
        ("LocalSync import", f'"{python_cmd}" -c "import localsync; print(\\"✅ LocalSync works!\\")"'),
        ("GUI support", f'"{python_cmd}" -c "import tkinter; print(\\"✅ GUI available\\")"'),
        ("Command line", f'"{python_cmd}" -c "import subprocess; result = subprocess.run([\\"localsync\\", \\"--help\\"], capture_output=True); print(\\"✅ Command works\\") if result.returncode == 0 else print(\\"⚠️ Command issue\\")"'),
    ]
    
    all_passed = True
    for test_name, test_cmd in tests:
        print(f"🧪 Testing {test_name}...")
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Passed")
            else:
                print("⚠️ Issues detected")
                all_passed = False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            all_passed = False
    
    return all_passed

def show_success():
    """Show success message with instructions"""
    print_header("🎉 Installation Complete!")
    
    print("""
✨ LocalSync has been successfully installed!

🚀 HOW TO START:

EASY OPTIONS (recommended):
1. Double-click 'Run-LocalSync.bat' (in this folder)
2. Use the 'LocalSync' shortcut on your desktop

COMMAND LINE OPTION:
• Open Command Prompt and type: localsync

📖 QUICK START GUIDE:

1. FIRST LAUNCH:
   • Choose '2. Register' to create your account
   • Enter a username and password
   • Login with your credentials

2. FIND FRIENDS:
   • Make sure friends are on the same Wi-Fi
   • They need to run LocalSync too
   • Check 'View Online Devices' in the menu

3. SEND FILES:
   • Use menu numbers (1, 2, 3...) to navigate
   • Click 'Open File Explorer' for easy file selection
   • No typing required - just click and choose!

💡 IMPORTANT TIPS:
• Keep LocalSync running to receive files
• All users must be on the same Wi-Fi network  
• Use encryption for sensitive files
• The menu system guides you through everything

❓ NEED HELP?
• Every screen has clear instructions
• Press '0' or 'Back' to return to previous menus
• Error messages tell you exactly what to do
""")

def main():
    """Main installation process"""
    try:
        print_header("LocalSync Windows Installer")
        
        # Check if we're on Windows
        if not check_windows():
            return  # Exit if not Windows
        
        print("This installer will set up LocalSync on your Windows system.")
        print("The process is automatic and user-friendly!")
        print()
        print("📋 What will be installed:")
        print("• LocalSync application")
        print("• Easy-to-use launchers") 
        print("• Desktop shortcut (optional)")
        print("• Everything needed for file sharing")
        
        wait_enter("Press Enter to begin installation...")
        
        # Step 1: Find Python
        print_header("Step 1: Finding Python")
        python_cmd = find_python_windows()
        
        if not python_cmd:
            print("❌ Python not found on your system!")
            print()
            print("Please install Python 3.7 or higher from:")
            print("📥 https://python.org/downloads")
            print()
            print("IMPORTANT: During installation, check 'Add Python to PATH'")
            print("After installing Python, run this installer again.")
            wait_enter()
            return
        
        # Step 2: Install LocalSync
        if not install_localsync(python_cmd):
            print("❌ Installation failed!")
            print()
            print("Please try these solutions:")
            print("1. Run this installer as Administrator")
            print("2. Make sure you have internet connection")
            print("3. Check if Python is properly installed")
            wait_enter()
            return
        
        # Step 3: Create launchers
        create_windows_launcher(python_cmd)
        create_desktop_shortcut(python_cmd)  # This is optional
        
        # Step 4: Test installation
        test_installation(python_cmd)
        
        # Show success message
        show_success()
        
        wait_enter("Press Enter to try LocalSync now...")
        
        # Try to launch LocalSync
        try:
            print("🚀 Launching LocalSync...")
            subprocess.run([python_cmd, "-c", "import localsync.cli; localsync.cli.main()"])
        except Exception as e:
            print(f"⚠️ Could not launch automatically: {e}")
            print("💡 You can start LocalSync using the methods mentioned above.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("Please try running the installer again.")

if __name__ == "__main__":
    main()