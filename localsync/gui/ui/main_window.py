from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from .login_dialog import LoginDialog
from .widgets import DevicesTab, TransferTab, SettingsTab, HistoryTab
from ..workers import WorkerThread

class MainWindow(QMainWindow):
    """Main UI window - handles only UI presentation"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("LocalSync - Secure File Sharing")
        self.setGeometry(100, 100, 1000, 700)
        
        # Center the window
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        
    def show_login_dialog(self):
        """Show login dialog"""
        self.login_dialog = LoginDialog(self)
        self.login_dialog.login_signal.connect(self.on_login_requested)
        self.login_dialog.register_signal.connect(self.on_register_requested)
        self.login_dialog.exec()
        
    def show_main_dashboard(self, username: str):
        """Show main dashboard after login"""
        # Clear existing layout
        self.clear_layout(self.main_layout)
        
        # Create header
        header_layout = QHBoxLayout()
        welcome_label = QLabel(f"👋 Welcome, {username}!")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(welcome_label)
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.controller.logout)
        header_layout.addWidget(logout_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.setup_tabs()
        
        # Start device discovery updates
        self.start_device_updates()
        
    def setup_tabs(self):
        """Setup all the tabs"""
        self.devices_tab = DevicesTab(self.controller)
        self.transfer_tab = TransferTab(self.controller)
        self.settings_tab = SettingsTab(self.controller)
        self.history_tab = HistoryTab(self.controller)
        
        # Connect tab signals
        self.devices_tab.refresh_clicked.connect(self.controller.refresh_devices)
        self.devices_tab.device_double_clicked.connect(self.transfer_tab.set_recipient)
        
        self.transfer_tab.transfer_requested.connect(self.on_transfer_requested)
        
        self.settings_tab.auto_accept_changed.connect(self.controller.toggle_auto_accept)
        self.settings_tab.download_dir_changed.connect(self.on_download_dir_changed)
        
        self.history_tab.clear_requested.connect(self.history_tab.clear_history)
        
        self.tab_widget.addTab(self.devices_tab, "📱 Online Devices")
        self.tab_widget.addTab(self.transfer_tab, "📤 Send Files")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        self.tab_widget.addTab(self.history_tab, "📋 History")
        
    def connect_signals(self):
        """Connect controller signals to UI slots"""
        self.controller.login_completed.connect(self.on_login_completed)
        self.controller.registration_completed.connect(self.on_registration_completed)
        
    def on_login_requested(self, username: str, password: str):
        """Handle login request from UI"""
        worker = WorkerThread(self.controller.handle_login(username, password))
        worker.finished_signal.connect(self.controller.login_completed.emit)
        worker.start()
        
    def on_register_requested(self, username: str, password: str):
        """Handle register request from UI"""
        worker = WorkerThread(self.controller.handle_register(username, password))
        worker.finished_signal.connect(self.controller.registration_completed.emit)
        worker.start()
        
    def on_transfer_requested(self, file_path: str, recipient_ip: str, encrypt: bool, compress: bool):
        """Handle transfer request from UI"""
        worker = WorkerThread(self.controller.handle_file_transfer(file_path, recipient_ip, encrypt, compress))
        worker.finished_signal.connect(self.controller.transfer_completed.emit)
        worker.start()
        
    def on_download_dir_changed(self, directory: str):
        """Handle download directory change"""
        success, message = self.controller.change_download_directory(directory)
        if success:
            self.settings_tab.show_info("Success", message)
            self.settings_tab.load_settings()  # Refresh settings display
        else:
            self.settings_tab.show_error("Error", message)
        
    def on_login_completed(self, success: bool, message: str):
        """Handle login completion"""
        if success:
            self.login_dialog.accept()
            self.show_main_dashboard(self.controller.current_user)
            # Switch to devices tab
            self.tab_widget.setCurrentIndex(0)
        else:
            self.login_dialog.show_status(f"❌ {message}", "error")
            
    def on_registration_completed(self, success: bool, message: str):
        """Handle registration completion"""
        if success:
            self.login_dialog.show_status("✅ Registration successful! Please login.", "success")
            self.login_dialog.password_edit.clear()
        else:
            self.login_dialog.show_status(f"❌ {message}", "error")
            
    def start_device_updates(self):
        """Start periodic device updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.controller.refresh_devices)
        self.update_timer.start(5000)  # Update every 5 seconds
        
    def clear_layout(self, layout):
        """Clear all widgets from layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()