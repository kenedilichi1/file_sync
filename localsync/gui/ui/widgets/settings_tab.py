from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, 
    QGroupBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class SettingsTab(QWidget):
    auto_accept_changed = pyqtSignal(bool)
    download_dir_changed = pyqtSignal(str)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Auto-accept
        auto_accept_group = QGroupBox("Auto-Accept Settings")
        auto_accept_layout = QVBoxLayout(auto_accept_group)
        
        self.auto_accept_check = QCheckBox("Auto-accept files from trusted senders")
        self.auto_accept_check.toggled.connect(self.auto_accept_changed.emit)
        
        auto_accept_layout.addWidget(self.auto_accept_check)
        layout.addWidget(auto_accept_group)
        
        # Download directory
        download_group = QGroupBox("Download Directory")
        download_layout = QVBoxLayout(download_group)
        
        self.download_dir_label = QLabel()
        download_layout.addWidget(self.download_dir_label)
        
        change_dir_btn = QPushButton("Change Download Directory")
        change_dir_btn.clicked.connect(self.change_download_dir)
        download_layout.addWidget(change_dir_btn)
        
        layout.addWidget(download_group)
        
        # Trusted senders
        trusted_group = QGroupBox("Trusted Senders")
        trusted_layout = QVBoxLayout(trusted_group)
        
        self.trusted_senders_label = QLabel()
        trusted_layout.addWidget(self.trusted_senders_label)
        
        layout.addWidget(trusted_group)
        
        layout.addStretch()
        
    def load_settings(self):
        """Load current settings"""
        settings = self.controller.get_settings()
        
        self.auto_accept_check.setChecked(settings['auto_accept'])
        self.download_dir_label.setText(f"Current: {settings['download_dir']}")
        
        trusted_text = ", ".join(settings['trusted_senders']) if settings['trusted_senders'] else "None"
        self.trusted_senders_label.setText(f"Trusted: {trusted_text}")
        
    def change_download_dir(self):
        """Change download directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory"
        )

        if directory:
            self.download_dir_changed.emit(directory)
            
    def show_error(self, title, message):
        """Show error message"""
        QMessageBox.critical(self, title, message)
        
    def show_info(self, title, message):
        """Show info message"""
        QMessageBox.information(self, title, message)