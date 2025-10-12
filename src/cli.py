import sys
import os
import argparse
from typing import Optional
import cmd



from auth import AuthManager
from discovery import DeviceDiscovery
from groups import GroupManager
from src import discovery
from transfer import FileTransfer
from .menu import MenuSystem
from .new_gui import LocalSyncGUI




class LocalSyncCLI(cmd.Cmd):
    def __init__(self, interface_mode='auto', config=None):
        super().__init__()
        self.auth_manager: AuthManager = AuthManager()
        self.device_discovery: DeviceDiscovery = None
        self.group_manager: GroupManager = GroupManager()
        
        # Configuration
        self.config = config or {}
        self.port = self.config.get('port', 8889)
        self.debug = self.config.get('debug', False)
        
        # Set up file transfer with config
        self.file_transfer: FileTransfer = FileTransfer(port=self.port)
        self.current_user: str = None
        self.download_dir: str = self.config.get('download_dir') or os.path.expanduser("~/Downloads")
        
        # Determine interface mode
        self.interface_mode = interface_mode
        self.gui_mode = False
        self.menu_mode = False
        self.cmd_mode = False
        
        self._setup_interface_mode()
        
        # Start file receiver
        self.file_transfer.start_receiver(self.download_dir)
        
    def _setup_interface_mode(self):
        """Setup the appropriate interface based on mode"""
        if self.interface_mode == 'gui' or self.interface_mode == 'auto':
            # Try to setup GUI
            try:
                from PyQt6.QtWidgets import QApplication
                self.qt_app = QApplication.instance() or QApplication(sys.argv)
                self.gui = LocalSyncGUI(self)
                self.gui_mode = True
                self.prompt = ""
                if self.debug:
                    print("✅ GUI mode initialized")
                return
            except ImportError as e:
                if self.interface_mode == 'gui':
                    print(f"❌ GUI requested but not available: {e}")
                    print("🔄 Falling back to menu mode...")
                # Continue to try menu mode
                
        if self.interface_mode == 'menu' or (self.interface_mode == 'auto' and not self.gui_mode):
            # Setup menu mode
            try:
                self.menu_system = MenuSystem(self)
                self.menu_mode = True
                self.prompt = ""
                if self.debug:
                    print("✅ Menu mode initialized")
                return
            except ImportError as e:
                if self.interface_mode == 'menu':
                    print(f"❌ Menu system not available: {e}")
                # Fall through to command mode
        
        # Default to command mode
        self.cmd_mode = True
        self.prompt = "filesync> "
        self.intro = "Welcome to fileSync. Type 'help' for commands.\n"
        if self.debug:
            print("✅ Command line mode initialized")
    
    def cmdloop(self, intro=None):
        """Override cmdloop to support different interface modes"""
        if self.gui_mode:
            return self._run_gui()
        elif self.menu_mode:
            return self._run_menu_system()
        else:
            # Original cmd.Cmd behavior
            if intro is not None:
                self.intro = intro
            super().cmdloop(intro)
    
    def _run_gui(self):
        """Run the PyQt6 GUI interface safely"""
        try:
            if hasattr(self, 'gui') and hasattr(self.gui, 'show'):
                self.gui.show()
                exit_code = self.qt_app.exec()
            else:
                exit_code = self.gui.run()

            # Ensure background threads stop after GUI closes
            self._cleanup()
            return exit_code

        except Exception as e:
            print(f"GUI Error: {e}")
            import traceback; traceback.print_exc()
            self._cleanup()
            return 1
    
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
        """Initialize the actual DeviceDiscovery system"""
        device_discovery = discovery.DeviceDiscovery()
        return device_discovery

    def _cleanup(self):
        """Cleanup resources and stop threads safely"""
        try:
            if self.device_discovery:
                self.device_discovery.stop_discovery()
                self.device_discovery = None

            if self.file_transfer:
                self.file_transfer.stop_receiver()
                self.file_transfer = None

            if hasattr(self, "auth_manager"):
                self.auth_manager = None

            if hasattr(self, "group_manager"):
                self.group_manager = None

            if self.debug:
                print("🧹 Cleanup completed. All threads stopped.")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")



def main():
    """Main entry point with multiple interface options"""
    parser = argparse.ArgumentParser(
        description="FileSync - Secure File Sharing Over Local Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  filesync --gui                    # Start with GUI (default)
  filesync --menu                   # Start with text menu
  filesync --cmd                    # Start with command line
  filesync --port 8890             # Use specific port

Interface priority: GUI > Menu > Command Line
        """
    )
    
    # Interface options
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--gui', '-g', action='store_true', 
                                help='Start with GUI interface (default if available)')
    interface_group.add_argument('--menu', '-m', action='store_true', 
                                help='Start with menu interface')
    interface_group.add_argument('--cmd', '-c', action='store_true', 
                                help='Start with command line interface')
    
    # Additional options
    parser.add_argument('--port', type=int, default=8889,
                       help='Port number for file transfer (default: 8889)')
    parser.add_argument('--download-dir',
                       help='Custom download directory')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose output')
    
    args = parser.parse_args()
    
    # Determine interface mode
    if args.gui:
        interface_mode = 'gui'
    elif args.menu:
        interface_mode = 'menu'
    elif args.cmd:
        interface_mode = 'cmd'
    else:
        # Default: try GUI first, fallback to menu
        interface_mode = 'auto'
    
    # Set up configuration
    config = {
        'port': args.port,
        'debug': args.debug
    }
    
    # Set custom download directory if provided
    if args.download_dir:
        config['download_dir'] = args.download_dir
    
    try:
        cli = LocalSyncCLI(interface_mode=interface_mode, config=config)
        
        # Run the appropriate interface
        if interface_mode == 'gui' or (interface_mode == 'auto' and cli.gui_mode):
            # GUI mode
            sys.exit(cli.cmdloop())
        else:
            # Menu or command mode
            cli.cmdloop()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install PyQt6 cryptography")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        if 'cli' in locals():
            cli._cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"💥 Error: {e}")

        import traceback
        traceback.print_exc()
        if 'cli' in locals():
            cli._cleanup()
        sys.exit(1)
    finally:
        if 'cli' in locals():
            cli._cleanup()


if __name__ == "__main__":
    main()