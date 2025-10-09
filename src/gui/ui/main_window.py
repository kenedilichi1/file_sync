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
        self.active_threads = []
        
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
        self.clear_layout(self.main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        welcome_label = QLabel(f"👋 Welcome, {username}!")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(welcome_label)
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.controller.logout)  # logout logic handled by controller
        header_layout.addWidget(logout_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Tabs
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.setup_tabs()
        self.start_device_updates()
        
    def setup_tabs(self):
        """Setup all tabs"""
        self.devices_tab = DevicesTab(self.controller)
        self.transfer_tab = TransferTab(self.controller)
        self.settings_tab = SettingsTab(self.controller)
        self.history_tab = HistoryTab(self.controller)
        
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
        self.controller.login_completed.connect(self.on_login_completed)
        self.controller.registration_completed.connect(self.on_registration_completed)
        self.controller.logout_completed.connect(self.on_logout_completed)
        
    def on_login_requested(self, username: str, password: str):
        worker = WorkerThread(self.controller.handle_login(username, password))
        worker.finished_signal.connect(self.controller.login_completed.emit)
        self.active_threads.append(worker)
        worker.finished_signal.connect(lambda *_: self._cleanup_thread(worker))
        worker.start()
        
    def on_register_requested(self, username: str, password: str):
        worker = WorkerThread(self.controller.handle_register(username, password))
        worker.finished_signal.connect(self.controller.registration_completed.emit)
        self.active_threads.append(worker)
        worker.finished_signal.connect(lambda *_: self._cleanup_thread(worker))
        worker.start()
        
    def on_transfer_requested(self, file_path, recipient_ip, encrypt, compress):
        worker = WorkerThread(self.controller.handle_file_transfer(file_path, recipient_ip, encrypt, compress))
        worker.finished_signal.connect(self.controller.transfer_completed.emit)
        self.active_threads.append(worker)
        worker.finished_signal.connect(lambda *_: self._cleanup_thread(worker))
        worker.start()
        
    def on_download_dir_changed(self, directory):
        success, message = self.controller.change_download_directory(directory)
        if success:
            self.settings_tab.show_info("Success", message)
            self.settings_tab.load_settings()
        else:
            self.settings_tab.show_error("Error", message)
            
    def on_registration_completed(self, success, message):
        if success:
            self.login_dialog.show_status("✅ Registration successful! Please login.", "success")
            self.login_dialog.password_edit.clear()
        else:
            self.login_dialog.show_status(f"❌ {message}", "error")
            
    def start_device_updates(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.controller.refresh_devices)
        self.update_timer.start(5000)
        
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _cleanup_thread(self, worker):
        if worker in self.active_threads:
            self.active_threads.remove(worker)
        worker.deleteLater()

    def closeEvent(self, event):
        for worker in getattr(self, "active_threads", []):
            try:
                worker.quit()
                worker.wait(1000)
            except Exception:
                pass
        self.active_threads.clear()
        event.accept()
    
    def on_login_completed(self, success: bool, message: str):
        if success:
            if hasattr(self, "login_dialog") and self.login_dialog:
                self.login_dialog.accept()
                self.login_dialog = None
            self.show_main_dashboard(self.controller.current_user)
            self.tab_widget.setCurrentIndex(0)
        else:
            if hasattr(self, "login_dialog") and self.login_dialog:
                self.login_dialog.show_status(f"❌ {message}", "error")

    def on_logout_completed(self):
        """Handle logout and return to login screen"""
        if hasattr(self, "update_timer") and self.update_timer.isActive():
            self.update_timer.stop()
        self.clear_layout(self.main_layout)
        self.tab_widget = None
        QMessageBox.information(self, "Logged Out", "You have been logged out successfully.")
        self.show_login_dialog()
