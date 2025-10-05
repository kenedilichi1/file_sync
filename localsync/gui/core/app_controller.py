import os
import time
from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal

class AppController(QObject):
    """Main application controller - handles core business logic"""
    
    # Signals
    login_completed = pyqtSignal(bool, str)
    registration_completed = pyqtSignal(bool, str)
    devices_updated = pyqtSignal(dict)
    transfer_progress = pyqtSignal(int, str)
    transfer_completed = pyqtSignal(bool, str)
    history_updated = pyqtSignal(str)
    
    def __init__(self, cli_instance):
        super().__init__()
        self.cli = cli_instance
        self.current_user: Optional[str] = None
        self.online_devices: Dict = {}
        
    def handle_login(self, username: str, password: str):
        """Handle login logic"""
        def login_task():
            return self.cli.auth_manager.login(username, password)
        return login_task
    
    def handle_register(self, username: str, password: str):
        """Handle registration logic"""
        def register_task():
            return self.cli.auth_manager.register(username, password)
        return register_task
    
    def handle_file_transfer(self, file_path: str, recipient_ip: str, 
                           encryption: bool = False, compression: bool = True):
        """Handle file transfer logic"""
        def transfer_task():
            # Set up progress callback
            def progress_callback(transferred, total, stage):
                self.transfer_progress.emit(transferred, stage)
            
            if os.path.isfile(file_path):
                success, message = self.cli.file_transfer.send_file(
                    file_path, recipient_ip,
                    progress_callback=progress_callback
                )
            else:
                success, message = self.cli.file_transfer.send_folder(
                    file_path, recipient_ip,
                    progress_callback=progress_callback
                )
            return success, message
        return transfer_task
    
    def refresh_devices(self):
        """Refresh online devices"""
        if self.cli.device_discovery:
            self.online_devices = self.cli.device_discovery.get_online_devices()
            self.devices_updated.emit(self.online_devices)
    
    def start_device_discovery(self, username: str):
        """Start device discovery service"""
        device_name = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'Unknown')
        self.cli.device_discovery = self.cli._create_discovery_manager()
        self.cli.device_discovery.start_discovery(username, device_name)
        self.current_user = username
    
    def stop_device_discovery(self):
        """Stop device discovery"""
        if self.cli.device_discovery:
            self.cli.device_discovery.stop_discovery()
    
    def change_download_directory(self, directory: str):
        """Change download directory"""
        old_directory = self.cli.download_dir
        
        try:
            # Stop current receiver
            self.cli.file_transfer.stop_receiver()
            
            # Update settings
            self.cli.file_transfer.transfer_config.update_setting('default_download_dir', directory)
            self.cli.download_dir = directory
            
            # Start new receiver
            self.cli.file_transfer.start_receiver(directory)
            return True, "Download directory updated successfully"
            
        except Exception as e:
            # Try to restore old directory
            try:
                self.cli.file_transfer.start_receiver(old_directory)
                self.cli.download_dir = old_directory
            except:
                pass
            return False, f"Failed to change download directory: {str(e)}"
    
    def toggle_auto_accept(self, enabled: bool):
        """Toggle auto-accept setting"""
        self.cli.file_transfer.transfer_config.update_setting('auto_accept', enabled)
    
    def get_settings(self):
        """Get current settings"""
        return {
            'auto_accept': self.cli.file_transfer.transfer_config.get_setting('auto_accept'),
            'download_dir': self.cli.file_transfer.transfer_config.get_setting('default_download_dir'),
            'trusted_senders': self.cli.file_transfer.transfer_config.get_setting('auto_accept_senders')
        }
    
    def add_to_history(self, message: str):
        """Add message to history"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history_updated.emit(f"[{timestamp}] {message}")