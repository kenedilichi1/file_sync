from PyQt6.QtWidgets import QApplication

class LocalSyncGUI:
    def __init__(self, cli_instance):
        """Initialize the GUI application"""
        self.qt_app = QApplication.instance([]) 
        
        # Create controller and UI
        from gui.core.app_controller import AppController
        from gui.ui.main_window import MainWindow
        
        self.controller = AppController(cli_instance)
        self.main_window = MainWindow(self.controller)
        
    def run(self):
        """Start the application"""
        self.main_window.show_login_dialog()
        self.main_window.show()
        return self.qt_app.exec()