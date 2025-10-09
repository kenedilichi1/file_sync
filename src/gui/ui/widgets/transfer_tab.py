import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QProgressBar, QGroupBox, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class TransferTab(QWidget):
    transfer_requested = pyqtSignal(str, str, bool, bool)  # file_path, recipient_ip, encrypt, compress
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.selected_path = None
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # File selection
        file_group = QGroupBox("Select File or Folder")
        file_layout = QVBoxLayout(file_group)
        
        file_buttons_layout = QHBoxLayout()
        select_file_btn = QPushButton("📁 Select File")
        select_file_btn.clicked.connect(self.select_file)
        select_folder_btn = QPushButton("📂 Select Folder")
        select_folder_btn.clicked.connect(self.select_folder)
        
        file_buttons_layout.addWidget(select_file_btn)
        file_buttons_layout.addWidget(select_folder_btn)
        file_buttons_layout.addStretch()
        
        file_layout.addLayout(file_buttons_layout)
        
        self.selected_path_label = QLabel("No file selected")
        self.selected_path_label.setStyleSheet("color: #7f8c8d;")
        file_layout.addWidget(self.selected_path_label)
        
        layout.addWidget(file_group)
        
        # Recipient selection
        recipient_group = QGroupBox("Select Recipient")
        recipient_layout = QVBoxLayout(recipient_group)
        
        self.recipient_combo = QComboBox()
        recipient_layout.addWidget(self.recipient_combo)
        
        layout.addWidget(recipient_group)
        
        # Options
        options_group = QGroupBox("Transfer Options")
        options_layout = QVBoxLayout(options_group)
        
        self.encrypt_check = QCheckBox("🔒 Encrypt file")
        self.compress_check = QCheckBox("🗜️ Compress file")
        self.compress_check.setChecked(True)
        
        options_layout.addWidget(self.encrypt_check)
        options_layout.addWidget(self.compress_check)
        
        layout.addWidget(options_group)
        
        # Send button
        send_btn = QPushButton("🚀 Send File")
        send_btn.clicked.connect(self.start_file_transfer)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(send_btn)
        
        # Progress
        progress_group = QGroupBox("Transfer Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready to transfer")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
    def connect_signals(self):
        """Connect controller signals to UI slots"""
        self.controller.devices_updated.connect(self.update_recipients)
        self.controller.transfer_progress.connect(self.update_progress)
        self.controller.transfer_completed.connect(self.on_transfer_completed)
        
    def select_file(self):
        """Select file to send"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select file to send",
            "",
            "All files (*.*)"
        )
        if filename:
            self.selected_path = filename
            self.selected_path_label.setText(f"Selected: {os.path.basename(filename)}")
            
    def select_folder(self):
        """Select folder to send"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select folder to send"
        )
        if folder:
            self.selected_path = folder
            self.selected_path_label.setText(f"Selected: {os.path.basename(folder)} (Folder)")
            
    def start_file_transfer(self):
        """Start file transfer"""
        if not self.selected_path:
            self.show_error("Please select a file or folder first")
            return
            
        recipient = self.recipient_combo.currentText()
        if not recipient:
            self.show_error("Please select a recipient")
            return
            
        # Get recipient IP from controller
        recipient_ip = None
        for username, info in self.controller.online_devices.items():
            if username == recipient:
                recipient_ip = info['ip_address']
                break
                
        if not recipient_ip:
            self.show_error("Selected recipient is no longer online")
            return
            
        # Emit transfer request
        self.transfer_requested.emit(
            self.selected_path,
            recipient_ip,
            self.encrypt_check.isChecked(),
            self.compress_check.isChecked()
        )
        
    def update_progress(self, progress, stage):
        """Update progress bar and label"""
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(f"{stage}: {progress:.1f}%")
        
    def on_transfer_completed(self, success, message):
        """Handle transfer completion"""
        if success:
            self.show_info("Transfer Complete", f"✅ {message}")
        else:
            self.show_error(f"Transfer Failed: {message}")
            
        self.update_progress(0, "Ready to transfer")
        
    def update_recipients(self, devices):
        """Update recipient combo box"""
        self.recipient_combo.clear()
        recipients = []
        
        for username, info in devices.items():
            if username != self.controller.current_user:
                recipients.append(username)
                
        self.recipient_combo.addItems(recipients)
        
    def set_recipient(self, username):
        """Set recipient in combo box"""
        self.recipient_combo.setCurrentText(username)
        
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        
    def show_info(self, title, message):
        """Show info message"""
        QMessageBox.information(self, title, message)