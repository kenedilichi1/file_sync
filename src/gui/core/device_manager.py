import time
from PyQt6.QtCore import QObject, pyqtSignal

class DeviceManager(QObject):
    """Handles device discovery and management"""
    
    devices_updated = pyqtSignal(dict)
    
    def __init__(self, cli_instance):
        super().__init__()
        self.cli = cli_instance
        self.online_devices = {}
    
    def refresh_devices(self):
        """Refresh online devices list"""
        if self.cli.device_discovery:
            self.online_devices = self.cli.device_discovery.get_online_devices()
            self.devices_updated.emit(self.online_devices)
    
    def get_recipients(self, exclude_current_user: bool = True):
        """Get list of available recipients"""
        recipients = []
        current_user = getattr(self.cli, 'current_user', None)
        
        for username, info in self.online_devices.items():
            if not exclude_current_user or username != current_user:
                recipients.append(username)
        return recipients
    
    def get_device_info(self, username: str):
        """Get device information for a user"""
        return self.online_devices.get(username)
    
    def get_device_status(self, username: str):
        """Get device status"""
        info = self.online_devices.get(username)
        if info:
            last_seen = time.time() - info['last_seen']
            return "🟢 Online" if last_seen < 30 else "🟡 Away"
        return "🔴 Offline"