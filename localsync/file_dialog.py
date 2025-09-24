import os
import platform
import subprocess
from typing import Optional

class FileDialog:
    """Cross-platform file dialog using tkinter as primary method"""
    
    @staticmethod
    def select_file(title: str = "Select File", initial_dir: str = None) -> Optional[str]:
        """Open file selection dialog using best available method"""
        return FileDialog._universal_dialog(title, initial_dir, False)
    
    @staticmethod
    def select_folder(title: str = "Select Folder", initial_dir: str = None) -> Optional[str]:
        """Open folder selection dialog using best available method"""
        return FileDialog._universal_dialog(title, initial_dir, True)
    
    @staticmethod
    def _universal_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Try multiple dialog methods in order of preference"""
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        
        # Try methods in order of preference
        methods = [
            FileDialog._try_tkinter_dialog,
            FileDialog._try_linux_native_dialog,
            FileDialog._fallback_text_dialog
        ]
        
        for method in methods:
            try:
                result = method(title, initial_dir, folder_mode)
                if result:
                    return result
            except Exception as e:
                continue
        
        return None
    
    @staticmethod
    def _try_tkinter_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Try tkinter dialog (works on Windows, macOS, Linux)"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create and hide root window
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)  # Bring to front
            
            if folder_mode:
                path = filedialog.askdirectory(title=title, initialdir=initial_dir)
            else:
                path = filedialog.askopenfilename(title=title, initialdir=initial_dir)
            
            root.destroy()
            return path if path else None
            
        except ImportError:
            return None
    
    @staticmethod
    def _try_linux_native_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Try Linux-native dialogs (zenity, kdialog)"""
        if platform.system() != "Linux":
            return None
        
        tools = [
            ('zenity', FileDialog._run_zenity_dialog),
            ('kdialog', FileDialog._run_kdialog_dialog),
            ('yad', FileDialog._run_yad_dialog)
        ]
        
        for tool_name, tool_func in tools:
            if FileDialog._command_exists(tool_name):
                try:
                    result = tool_func(title, initial_dir, folder_mode)
                    if result:
                        return result
                except Exception:
                    continue
        
        return None
    
    @staticmethod
    def _run_zenity_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Run zenity dialog"""
        if folder_mode:
            cmd = ['zenity', '--file-selection', '--directory', '--title', title]
        else:
            cmd = ['zenity', '--file-selection', '--title', title]
        
        if initial_dir:
            cmd.extend(['--filename', initial_dir])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    
    @staticmethod
    def _run_kdialog_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Run kdialog dialog"""
        if folder_mode:
            cmd = ['kdialog', '--getexistingdirectory', initial_dir or '', '--title', title]
        else:
            cmd = ['kdialog', '--getopenfilename', initial_dir or '', '--title', title]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    
    @staticmethod
    def _run_yad_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Run yad dialog"""
        if folder_mode:
            cmd = ['yad', '--file', '--directory', '--title', title]
        else:
            cmd = ['yad', '--file', '--title', title]
        
        if initial_dir:
            cmd.extend(['--filename', initial_dir])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    
    @staticmethod
    def _fallback_text_dialog(title: str, initial_dir: str, folder_mode: bool) -> Optional[str]:
        """Text-based fallback dialog"""
        print(f"\n{'📁' if folder_mode else '📄'} {title}")
        print("=" * 50)
        
        current_dir = initial_dir if os.path.exists(initial_dir) else os.getcwd()
        
        while True:
            print(f"\nCurrent directory: {current_dir}")
            print("\nOptions:")
            print("1. List contents")
            print("2. Change directory")
            print("3. Select current directory" if folder_mode else "3. Enter file path")
            print("0. Cancel")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == '0':
                return None
            elif choice == '1':
                FileDialog._list_directory(current_dir, folder_mode)
            elif choice == '2':
                new_dir = input("Enter new directory path: ").strip()
                if os.path.isdir(new_dir):
                    current_dir = new_dir
                else:
                    print("❌ Invalid directory")
            elif choice == '3':
                if folder_mode:
                    return current_dir
                else:
                    file_path = input("Enter file path: ").strip()
                    if os.path.isfile(file_path):
                        return file_path
                    else:
                        print("❌ File does not exist")
            else:
                print("❌ Invalid choice")
    
    @staticmethod
    def _list_directory(path: str, folder_mode: bool):
        """List directory contents"""
        try:
            items = os.listdir(path)
            print(f"\nContents of {path}:")
            print("-" * 40)
            
            for i, item in enumerate(items, 1):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    print(f"{i}. 📁 {item}/")
                elif not folder_mode and os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    size_str = FileDialog._format_size(size)
                    print(f"{i}. 📄 {item} ({size_str})")
            
        except PermissionError:
            print("❌ Permission denied")
        except OSError as e:
            print(f"❌ Error reading directory: {e}")
    
    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, '--version'], capture_output=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    @staticmethod
    def _format_size(size_bytes):
        """Format file size human-readably"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"