from PyQt6.QtCore import QObject, pyqtSignal

class AuthManager(QObject):
    """Handles authentication logic"""
    
    auth_status_changed = pyqtSignal(str, bool)  # username, is_logged_in
    
    def __init__(self, cli_auth_manager):
        super().__init__()
        self.cli_auth_manager = cli_auth_manager
        self.current_user = None
    
    def login(self, username: str, password: str):
        """Perform login"""
        success, message = self.cli_auth_manager.login(username, password)
        if success:
            self.current_user = username
            self.auth_status_changed.emit(username, True)
        return success, message
    
    def register(self, username: str, password: str):
        """Perform registration"""
        success, message = self.cli_auth_manager.register(username, password)
        return success, message
    
    def logout(self):
        """Perform logout"""
        self.current_user = None
        self.auth_status_changed.emit("", False)