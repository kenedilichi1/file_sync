import cmd
import sys
import os
import time
from getpass import getpass
from typing import Optional

from .auth import AuthManager
from .discovery import DeviceDiscovery
from .groups import GroupManager
from .transfer import FileTransfer, CompressionMethod
from .utils.progress import TransferProgress, ProgressBar
from .menu import MenuSystem


class LocalSyncCLI(cmd.Cmd):
    def __init__(self, menu_mode=True):
        super().__init__()
        self.auth_manager = AuthManager()
        self.device_discovery = None
        self.group_manager = GroupManager()
        self.file_transfer = FileTransfer()
        self.current_user = None
        self.download_dir = os.path.expanduser("~/Downloads")
        self.menu_mode = menu_mode
        
        # Start file receiver
        self.file_transfer.start_receiver(self.download_dir)
        
        # Initialize menu system if in menu mode
        if menu_mode:
            self.menu_system = MenuSystem(self)
            self.prompt = ""  # No prompt in menu mode
        else:
            self.prompt = "localsync> "
            self.intro = "Welcome to LocalSync. Type 'help' for commands.\n"
    
    def _create_discovery_manager(self):
        """Create and return a discovery manager instance"""
        return DeviceDiscovery()
    
    def _create_progress_bar(self, filename, total_size):
        """Create a progress bar instance"""
        return TransferProgress(filename, total_size)
    
    def _calculate_folder_size(self, folder_path):
        """Calculate total size of a folder"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def cmdloop(self, intro=None):
        """Override cmdloop to support menu mode"""
        if self.menu_mode:
            self._run_menu_system()
        else:
            super().cmdloop(intro)
    
    def _run_menu_system(self):
        """Run the menu-based interface"""
        try:
            while True:
                result = self.menu_system.display_menu("main")
                if result == 'exit':
                    print("Goodbye! 👋")
                    break
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.device_discovery:
            self.device_discovery.stop_discovery()
        self.file_transfer.stop_receiver()
    
    # ==================== LEGACY COMMANDS (for backward compatibility) ====================
    
    def do_menu(self, arg):
        """Switch to menu mode"""
        self.menu_mode = True
        print("Switching to menu mode...")
        time.sleep(1)
        self._run_menu_system()
        return True
    
    def do_cmd(self, arg):
        """Switch to command mode"""
        self.menu_mode = False
        print("Switching to command mode...")
        return False
    
    def do_register(self, arg):
        """Register a new user: register [username]"""
        if not arg:
            print("Username required")
            return
            
        password = getpass("Password: ")
        confirm_password = getpass("Confirm Password: ")
        
        if password != confirm_password:
            print("Passwords do not match")
            return
            
        success, message = self.auth_manager.register(arg, password)
        print(message)
    
    def do_login(self, arg):
        """Login: login [username]"""
        if not arg:
            print("Username required")
            return
            
        password = getpass("Password: ")
        success, message = self.auth_manager.login(arg, password)
        if success:
            self.current_user = arg
            print("Login successful")
            # Start device discovery
            device_name = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'Unknown')
            self.device_discovery = self._create_discovery_manager()
            self.device_discovery.start_discovery(arg, device_name)
            print("Device discovery started")
        else:
            print(f"Login failed: {message}")
    
    def do_devices(self, arg):
        """List online devices: devices [--refresh]"""
        if not self.current_user:
            print("Please login first")
            return
            
        if not self.device_discovery:
            print("Device discovery not active")
            return
            
        if arg == "--refresh":
            print("Refreshing device list...")
            time.sleep(2)
            
        devices = self.device_discovery.get_online_devices()
        if not devices:
            print("No devices online")
            return
            
        print("Online devices:")
        for i, (username, info) in enumerate(devices.items(), 1):
            if username != self.current_user:
                last_seen = time.time() - info['last_seen']
                status = "Online" if last_seen < 30 else "Away"
                print(f"{i}. {username} ({info['device_name']}) - {info['ip_address']} [{status}]")
    
    def do_send(self, arg):
        """Send a file: send [file_path] [username] [--encrypt] [--compress]"""
        # ... existing send implementation ...
        pass
    
    def do_exit(self, arg):
        """Exit the application"""
        self._cleanup()
        print("Goodbye!")
        return True
    
    def preloop(self):
        """Run before command loop starts"""
        if not self.menu_mode:
            print("LocalSync - Secure file transfer over local network")
            print("Type 'menu' for interactive mode or 'help' for commands")


def main():
    """Main entry point with menu mode by default"""
    # Check if command mode is requested
    menu_mode = True
    if len(sys.argv) > 1 and sys.argv[1] in ['--cmd', '-c']:
        menu_mode = False
    
    cli = LocalSyncCLI(menu_mode=menu_mode)
    
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        cli._cleanup()
    except Exception as e:
        print(f"Error: {e}")
        cli._cleanup()


if __name__ == "__main__":
    main()