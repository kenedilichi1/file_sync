import sys
import os
from typing import Optional
import cmd



from .auth import AuthManager
from .discovery import DeviceDiscovery
from .groups import GroupManager
from .transfer import FileTransfer
from .menu import MenuSystem
from .new_gui import LocalSyncGUI 



class LocalSyncCLI(cmd.Cmd):
    def __init__(self, menu_mode=True, gui_mode=False):
        super().__init__()
        self.auth_manager: AuthManager = AuthManager()
        self.device_discovery: DeviceDiscovery = None
        self.group_manager: GroupManager = GroupManager()
        self.file_transfer: FileTransfer = FileTransfer()
        self.current_user: str = None
        self.download_dir: str = os.path.expanduser("~/Downloads")
        self.menu_mode: bool = menu_mode
        self.gui_mode: bool = gui_mode

        # Start file receiver
        self.file_transfer.start_receiver(self.download_dir)
        
        # Initialize appropriate interface
        if gui_mode:
            # Create QApplication instance for PyQt6
            from PyQt6.QtWidgets import QApplication
            self.qt_app = QApplication.instance() or QApplication(sys.argv)
            self.gui = LocalSyncGUI(self)
            self.prompt = ""
        elif menu_mode:
            self.menu_system = MenuSystem(self)
            self.prompt = ""
        else:
            self.prompt = "localsync> "
            self.intro = "Welcome to LocalSync. Type 'help' for commands.\n"
    
    def cmdloop(self, intro=None):
        """Override cmdloop to support GUI and menu modes"""
        if self.gui_mode:
            return self._run_gui()
        elif self.menu_mode:
            self._run_menu_system()
        else:
            super().cmdloop(intro)
    
    def _run_gui(self):
        """Run the PyQt6 GUI interface"""
        try:
            self.gui.show()
            return self.qt_app.exec()
        except Exception as e:
            print(f"GUI Error: {e}")
            # Fall back to menu mode
            self.gui_mode = False
            self.menu_mode = True
            self._run_menu_system()
    
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
    
    def _create_discovery_manager(self):
        """Create device discovery manager"""
        # This method should be implemented based on your discovery module
        class DiscoveryManager:
            def __init__(self):
                self.online_devices = {}
            
            def start_discovery(self, username, device_name):
                print(f"Discovery started for {username} on {device_name}")
            
            def stop_discovery(self):
                print("Discovery stopped")
            
            def get_online_devices(self):
                return self.online_devices
        
        return DiscoveryManager()
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.device_discovery:
            self.device_discovery.stop_discovery()
        if self.file_transfer:
            self.file_transfer.stop_receiver()
        # Add a small delay to ensure everything is cleaned up
        import time
        time.sleep(0.1)


def main():
    """Main entry point with multiple interface options"""
    # Check command line arguments
    gui_mode = '--gui' in sys.argv or '-g' in sys.argv
    menu_mode = '--menu' in sys.argv or '-m' in sys.argv
    cmd_mode = '--cmd' in sys.argv or '-c' in sys.argv
    
    # Default to GUI if no arguments, otherwise respect arguments
    if gui_mode or (not menu_mode and not cmd_mode):
        # Use PyQt6 GUI
        cli = LocalSyncCLI(gui_mode=True)
        sys.exit(cli.cmdloop())
    
    # Use menu mode or command mode
    cli = LocalSyncCLI(menu_mode=not cmd_mode)
    
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