import os
import sys
import time
from getpass import getpass
from typing import Dict, Callable, Any

from .file_dialog import FileDialog

class MenuSystem:
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.current_menu = "main"
        self.menu_history = []
        self.menus = {
            "main": self._main_menu,
            "file_operations": self._file_operations_menu,
            "device_management": self._device_management_menu,
            "settings": self._settings_menu,
            "send_file": self._send_file_menu,
            "send_folder": self._send_folder_menu,
        }
    
    def display_menu(self, menu_name: str):
        """Display a specific menu"""
        self.current_menu = menu_name
        if menu_name in self.menus:
            return self.menus[menu_name]()
        else:
            print(f"Unknown menu: {menu_name}")
            return self._main_menu()
    
    def navigate_to(self, menu_name: str):
        """Navigate to a new menu"""
        self.menu_history.append(self.current_menu)
        return self.display_menu(menu_name)
    
    def go_back(self):
        """Go back to previous menu"""
        if self.menu_history:
            previous_menu = self.menu_history.pop()
            return self.display_menu(previous_menu)
        else:
            return self._main_menu()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a consistent header"""
        self.clear_screen()
        print("=" * 60)
        print(f"🚀 LocalSync - {title}")
        print("=" * 60)
        print()
    
    def get_user_choice(self, options: Dict[str, str]) -> str:
        """Display options and get user choice"""
        for key, description in options.items():
            print(f"{key}. {description}")
        
        print("\n0. Back" if self.menu_history else "\n0. Exit")
        print("-" * 40)
        
        while True:
            choice = input("Enter your choice: ").strip()
            if choice == '0':
                if self.menu_history:
                    return 'back'
                else:
                    return 'exit'
            elif choice in options:
                return choice
            else:
                print("Invalid choice. Please try again.")
    
    
    # ==================== MENU DEFINITIONS ====================
    def _send_file_menu(self):
        """Send file menu with file dialog"""
        self.print_header("Send File")
        
        # Get online devices
        devices = self.cli.device_discovery.get_online_devices() if self.cli.device_discovery else {}
        
        if not devices:
            print("❌ No devices online. Please check device list first.")
            input("Press Enter to continue...")
            return self.go_back()
        
        # Display devices
        print("Select recipient:")
        print("-" * 40)
        device_list = []
        for i, (username, info) in enumerate(devices.items(), 1):
            if username != self.cli.current_user:
                device_list.append((username, info))
                print(f"{i}. {username} ({info['device_name']})")
        
        print()
        print("Select file to send:")
        print("1. 📁 Open file explorer")
        print("2. ⌨️  Enter file path manually")
        print("0. ↩️  Back")
        print("-" * 40)
        
        file_choice = input("Enter your choice: ").strip()
        
        file_path = None
        if file_choice == '1':
            # Open file dialog
            print("Opening file explorer...")
            file_path = FileDialog.select_file("Select file to send")
        elif file_choice == '2':
            # Manual path entry
            file_path = input("Enter file path: ").strip()
        elif file_choice == '0':
            return self.go_back()
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")
            return self.navigate_to("send_file")
        
        if not file_path or not os.path.exists(file_path):
            print("❌ File does not exist or selection cancelled.")
            input("Press Enter to continue...")
            return self.navigate_to("send_file")
        
        if os.path.isdir(file_path):
            print("❌ Selected path is a folder. Use 'Send Folder' instead.")
            input("Press Enter to continue...")
            return self.navigate_to("send_file")
        
        # Get recipient choice
        try:
            recipient_choice = int(input("Select recipient (number): ")) - 1
            if 0 <= recipient_choice < len(device_list):
                recipient_username, recipient_info = device_list[recipient_choice]
                recipient_ip = recipient_info['ip_address']
                
                # Ask for encryption
                encrypt = input("Encrypt file? (y/n): ").lower().strip() in ['y', 'yes']
                
                # Perform transfer
                return self._perform_file_transfer(file_path, recipient_ip, recipient_username, encrypt)
            else:
                print("❌ Invalid recipient selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
        
        input("Press Enter to continue...")
        return self.navigate_to("send_file")
    
    def _send_folder_menu(self):
        """Send folder menu with folder dialog"""
        self.print_header("Send Folder")
        
        devices = self.cli.device_discovery.get_online_devices() if self.cli.device_discovery else {}
        
        if not devices:
            print("❌ No devices online.")
            input("Press Enter to continue...")
            return self.go_back()
        
        # Display devices
        print("Select recipient:")
        print("-" * 40)
        device_list = []
        for i, (username, info) in enumerate(devices.items(), 1):
            if username != self.cli.current_user:
                device_list.append((username, info))
                print(f"{i}. {username} ({info['device_name']})")
        
        print()
        print("Select folder to send:")
        print("1. 📁 Open folder explorer")
        print("2. ⌨️  Enter folder path manually")
        print("0. ↩️  Back")
        print("-" * 40)
        
        folder_choice = input("Enter your choice: ").strip()
        
        folder_path = None
        if folder_choice == '1':
            # Open folder dialog
            print("Opening folder explorer...")
            folder_path = FileDialog.select_folder("Select folder to send")
        elif folder_choice == '2':
            # Manual path entry
            folder_path = input("Enter folder path: ").strip()
        elif folder_choice == '0':
            return self.go_back()
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")
            return self.navigate_to("send_folder")
        
        if not folder_path or not os.path.isdir(folder_path):
            print("❌ Folder does not exist or selection cancelled.")
            input("Press Enter to continue...")
            return self.navigate_to("send_folder")
        
        if os.path.isfile(folder_path):
            print("❌ Selected path is a file. Use 'Send File' instead.")
            input("Press Enter to continue...")
            return self.navigate_to("send_folder")
        
        # Get recipient choice
        try:
            recipient_choice = int(input("Select recipient (number): ")) - 1
            if 0 <= recipient_choice < len(device_list):
                recipient_username, recipient_info = device_list[recipient_choice]
                recipient_ip = recipient_info['ip_address']
                
                encrypt = input("Encrypt folder? (y/n): ").lower().strip() in ['y', 'yes']
                
                return self._perform_folder_transfer(folder_path, recipient_ip, recipient_username, encrypt)
            else:
                print("❌ Invalid recipient selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
        
        input("Press Enter to continue...")
        return self.navigate_to("send_folder")
    
    def _check_dialog_dependencies(self):
        """Check and display available dialog options"""
        available, tools = FileDialog.check_dependencies()
        
        self.print_header("File Dialog Dependencies")
        print("Available file dialog methods:")
        print("-" * 40)
        
        if available:
            for tool in tools:
                print(f"✅ {tool}")
            print(f"\nTotal methods available: {len(tools)}")
        else:
            print("❌ No graphical dialog methods available.")
            print("Falling back to text-based selection.")
        
        input("\nPress Enter to continue...")
    
    def _main_menu(self):
        """Main menu displayed after login"""
        if not self.cli.current_user:
            return self._login_menu()
        
        self.print_header("Main Menu")
        print(f"Welcome, {self.cli.current_user}!")
        print()
        
        options = {
            "1": "View Online Devices",
            "2": "File Operations",
            "3": "Device Management", 
            "4": "Settings",
            "5": "Logout"
        }
        
        choice = self.get_user_choice(options)
        
        if choice == 'back' or choice == 'exit':
            return choice
        elif choice == '1':
            return self.navigate_to("device_management")
        elif choice == '2':
            return self.navigate_to("file_operations")
        elif choice == '3':
            return self.navigate_to("device_management")
        elif choice == '4':
            return self.navigate_to("settings")
        elif choice == '5':
            self.cli.current_user = None
            if self.cli.device_discovery:
                self.cli.device_discovery.stop_discovery()
            print("Logged out successfully.")
            time.sleep(1)
            return self.navigate_to("main")
    
    def _login_menu(self):
        """Login/registration menu"""
        self.print_header("LocalSync Login")
        
        options = {
            "1": "Login",
            "2": "Register",
            "3": "Exit"
        }
        
        choice = self.get_user_choice(options)
        
        if choice == 'back' or choice == 'exit':
            return 'exit'
        elif choice == '1':
            return self._perform_login()
        elif choice == '2':
            return self._perform_registration()
    
    def _file_operations_menu(self):
        """File operations menu"""
        self.print_header("File Operations")
        
        options = {
            "1": "Send File",
            "2": "Send Folder", 
            "3": "Set Download Directory",
            "4": "View Recent Transfers"
        }
        
        choice = self.get_user_choice(options)
        
        if choice == 'back':
            return self.go_back()
        elif choice == '1':
            return self.navigate_to("send_file")
        elif choice == '2':
            return self.navigate_to("send_folder")
        elif choice == '3':
            return self._set_download_directory()
        elif choice == '4':
            return self._view_recent_transfers()
    
    def _device_management_menu(self):
        """Device management menu"""
        self.print_header("Online Devices")
        
        # Get online devices
        devices = self.cli.device_discovery.get_online_devices() if self.cli.device_discovery else {}
        
        if devices:
            print("📱 Online Devices:")
            print("-" * 40)
            for i, (username, info) in enumerate(devices.items(), 1):
                if username != self.cli.current_user:
                    last_seen = time.time() - info['last_seen']
                    status = "🟢 Online" if last_seen < 30 else "🟡 Away"
                    print(f"{i}. {username} ({info['device_name']})")
                    print(f"   IP: {info['ip_address']} | Status: {status}")
                    print()
        else:
            print("No devices online. Make sure other users are logged in.")
            print()
        
        options = {
            "1": "Refresh Device List",
            "2": "Add to Trusted Devices",
            "3": "View Trusted Devices"
        }
        
        choice = self.get_user_choice(options)
        
        if choice == 'back':
            return self.go_back()
        elif choice == '1':
            print("Refreshing device list...")
            time.sleep(2)
            return self.navigate_to("device_management")
        elif choice == '2':
            return self._add_trusted_device(devices)
        elif choice == '3':
            return self._view_trusted_devices()
    
    def _settings_menu(self):
        """Settings menu"""
        self.print_header("Settings")
    
        config = self.cli.file_transfer.transfer_config.config
    
        print("Current Settings:")
        print("-" * 40)
        print(f"Auto-accept: {'🟢 Enabled' if config['auto_accept'] else '🔴 Disabled'}")
        print(f"Download Directory: {config['default_download_dir']}")
        print(f"Request Timeout: {config['request_timeout']} seconds")
        print(f"Large File Threshold: {self._format_size(config['large_file_threshold'])}")
    
        # Show available dialog methods
        available, tools = FileDialog.check_dependencies()
        dialog_status = f"🟢 {len(tools)} methods" if available else "🔴 Text-only"
        print(f"File Dialogs: {dialog_status}")
        print()
    
        options = {
            "1": "Toggle Auto-accept",
            "2": "Manage Trusted Senders", 
            "3": "Change Download Directory",
            "4": "Security Settings",
            "5": "Check Dialog Dependencies"  # New option
        }
    
        choice = self.get_user_choice(options)
    
        if choice == 'back':
            return self.go_back()
        elif choice == '1':
            return self._toggle_auto_accept()
        elif choice == '2':
            return self._manage_trusted_senders()
        elif choice == '3':
            return self._change_download_directory()
        elif choice == '4':
            return self._security_settings()
        elif choice == '5':
            return self._check_dialog_dependencies()
    
    def _send_file_menu(self):
        """Send file menu"""
        self.print_header("Send File")
        
        # Get online devices
        devices = self.cli.device_discovery.get_online_devices() if self.cli.device_discovery else {}
        
        if not devices:
            print("❌ No devices online. Please check device list first.")
            input("Press Enter to continue...")
            return self.go_back()
        
        # Display devices
        print("Select recipient:")
        print("-" * 40)
        device_list = []
        for i, (username, info) in enumerate(devices.items(), 1):
            if username != self.cli.current_user:
                device_list.append((username, info))
                print(f"{i}. {username} ({info['device_name']})")
        
        print()
        file_path = input("Enter file path: ").strip()
        
        if not file_path or not os.path.exists(file_path):
            print("❌ File does not exist.")
            input("Press Enter to continue...")
            return self.navigate_to("send_file")
        
        # Get recipient choice
        try:
            recipient_choice = int(input("Select recipient (number): ")) - 1
            if 0 <= recipient_choice < len(device_list):
                recipient_username, recipient_info = device_list[recipient_choice]
                recipient_ip = recipient_info['ip_address']
                
                # Ask for encryption
                encrypt = input("Encrypt file? (y/n): ").lower().strip() in ['y', 'yes']
                
                # Perform transfer
                return self._perform_file_transfer(file_path, recipient_ip, recipient_username, encrypt)
            else:
                print("❌ Invalid recipient selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
        
        input("Press Enter to continue...")
        return self.navigate_to("send_file")
    
    def _send_folder_menu(self):
        """Send folder menu"""
        self.print_header("Send Folder")
        
        devices = self.cli.device_discovery.get_online_devices() if self.cli.device_discovery else {}
        
        if not devices:
            print("❌ No devices online.")
            input("Press Enter to continue...")
            return self.go_back()
        
        print("Select recipient:")
        print("-" * 40)
        device_list = []
        for i, (username, info) in enumerate(devices.items(), 1):
            if username != self.cli.current_user:
                device_list.append((username, info))
                print(f"{i}. {username} ({info['device_name']})")
        
        print()
        folder_path = input("Enter folder path: ").strip()
        
        if not folder_path or not os.path.isdir(folder_path):
            print("❌ Folder does not exist.")
            input("Press Enter to continue...")
            return self.navigate_to("send_folder")
        
        try:
            recipient_choice = int(input("Select recipient (number): ")) - 1
            if 0 <= recipient_choice < len(device_list):
                recipient_username, recipient_info = device_list[recipient_choice]
                recipient_ip = recipient_info['ip_address']
                
                encrypt = input("Encrypt folder? (y/n): ").lower().strip() in ['y', 'yes']
                
                return self._perform_folder_transfer(folder_path, recipient_ip, recipient_username, encrypt)
            else:
                print("❌ Invalid recipient selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
        
        input("Press Enter to continue...")
        return self.navigate_to("send_folder")
    
    # ==================== ACTION METHODS ====================
    
    def _perform_login(self):
        """Handle user login"""
        self.print_header("Login")
        
        username = input("Username: ").strip()
        password = getpass("Password: ")
        
        success, message = self.cli.auth_manager.login(username, password)
        
        if success:
            self.cli.current_user = username
            # Start device discovery
            device_name = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'Unknown')
            self.cli.device_discovery = self.cli._create_discovery_manager()
            self.cli.device_discovery.start_discovery(username, device_name)
            
            print("✅ Login successful!")
            time.sleep(1)
            return self.navigate_to("main")
        else:
            print(f"❌ Login failed: {message}")
            input("Press Enter to continue...")
            return self.navigate_to("main")
    
    def _perform_registration(self):
        """Handle user registration"""
        self.print_header("Register")
        
        username = input("Username: ").strip()
        password = getpass("Password: ")
        confirm_password = getpass("Confirm Password: ")
        
        if password != confirm_password:
            print("❌ Passwords do not match.")
            input("Press Enter to continue...")
            return self.navigate_to("main")
        
        success, message = self.cli.auth_manager.register(username, password)
        
        if success:
            print("✅ Registration successful! Please login.")
            time.sleep(1)
            return self.navigate_to("main")
        else:
            print(f"❌ Registration failed: {message}")
            input("Press Enter to continue...")
            return self.navigate_to("main")
    
    def _perform_file_transfer(self, file_path: str, recipient_ip: str, recipient_username: str, encrypt: bool = False):
        """Perform file transfer with progress"""
        self.print_header(f"Sending File to {recipient_username}")
        
        print(f"📤 Sending: {os.path.basename(file_path)}")
        print(f"👤 To: {recipient_username}")
        print(f"🔒 Encryption: {'🟢 Enabled' if encrypt else '🔴 Disabled'}")
        print()
        
        # Set up progress tracking
        file_size = os.path.getsize(file_path)
        progress = self.cli._create_progress_bar(os.path.basename(file_path), file_size)
        
        def progress_callback(transferred, total, stage):
            if stage == "Sending":
                progress.update(transferred)
            else:
                print(f"{stage}...")
        
        # Perform transfer
        encryption_password = None
        if encrypt:
            encryption_password = getpass("Enter encryption password: ")
            confirm_password = getpass("Confirm password: ")
            if encryption_password != confirm_password:
                print("❌ Passwords do not match.")
                input("Press Enter to continue...")
                return self.navigate_to("file_operations")
        
        success, message = self.cli.file_transfer.send_file(
            file_path, recipient_ip, progress_callback,
            encryption_password
        )
        
        progress.close()
        print(f"\n{'✅' if success else '❌'} {message}")
        input("Press Enter to continue...")
        return self.navigate_to("file_operations")
    
    def _perform_folder_transfer(self, folder_path: str, recipient_ip: str, recipient_username: str, encrypt: bool = False):
        """Perform folder transfer"""
        self.print_header(f"Sending Folder to {recipient_username}")
        
        print(f"📁 Sending: {os.path.basename(folder_path)}")
        print(f"👤 To: {recipient_username}")
        print(f"🔒 Encryption: {'🟢 Enabled' if encrypt else '🔴 Disabled'}")
        print()
        
        # Calculate folder size for progress
        total_size = self.cli._calculate_folder_size(folder_path)
        progress = self.cli._create_progress_bar(os.path.basename(folder_path), total_size)
        
        def progress_callback(transferred, total, stage):
            if stage == "Sending":
                progress.update(transferred)
            else:
                print(f"{stage}...")
        
        # Perform transfer
        encryption_password = None
        if encrypt:
            encryption_password = getpass("Enter encryption password: ")
            confirm_password = getpass("Confirm password: ")
            if encryption_password != confirm_password:
                print("❌ Passwords do not match.")
                input("Press Enter to continue...")
                return self.navigate_to("file_operations")
        
        success, message = self.cli.file_transfer.send_folder(
            folder_path, recipient_ip, progress_callback,
            encryption_password
        )
        
        progress.close()
        print(f"\n{'✅' if success else '❌'} {message}")
        input("Press Enter to continue...")
        return self.navigate_to("file_operations")
    
    def _set_download_directory(self):
        """Set download directory"""
        self.print_header("Set Download Directory")
        
        current_dir = self.cli.file_transfer.transfer_config.get_setting('default_download_dir')
        print(f"Current directory: {current_dir}")
        print()
        
        new_dir = input("Enter new directory (or press Enter to keep current): ").strip()
        
        if new_dir:
            if os.path.isdir(new_dir):
                self.cli.file_transfer.transfer_config.update_setting('default_download_dir', new_dir)
                self.cli.download_dir = new_dir
                self.cli.file_transfer.stop_receiver()
                self.cli.file_transfer.start_receiver(new_dir)
                print("✅ Download directory updated!")
            else:
                print("❌ Directory does not exist.")
        
        input("Press Enter to continue...")
        return self.navigate_to("file_operations")
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"