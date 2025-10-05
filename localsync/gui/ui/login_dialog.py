from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LoginDialog(QDialog):
    """Login dialog UI"""
    login_signal = pyqtSignal(str, str)
    register_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("LocalSync - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🚀 LocalSync")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        subheader_label = QLabel("Secure File Sharing Over Local Network")
        subheader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subheader_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subheader_label)
        
        layout.addSpacing(20)
        
        # Login form
        form_group = QGroupBox("Account")
        form_layout = QVBoxLayout(form_group)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        username_layout.addWidget(self.username_edit)
        form_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter your password")
        password_layout.addWidget(self.password_edit)
        form_layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        form_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e74c3c;")
        form_layout.addWidget(self.status_label)
        
        layout.addWidget(form_group)
        
        # Connect enter key to login
        self.password_edit.returnPressed.connect(self.handle_login)
        
    def handle_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.show_status("Please enter both username and password", "error")
            return
            
        self.show_status("Logging in...", "loading")
        self.login_signal.emit(username, password)
        
    def handle_register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.show_status("Please enter both username and password", "error")
            return
            
        if len(password) < 3:
            self.show_status("Password must be at least 3 characters", "error")
            return
            
        self.show_status("Registering...", "loading")
        self.register_signal.emit(username, password)
        
    def show_status(self, message, status_type="info"):
        colors = {
            "error": "#e74c3c",
            "loading": "#f39c12", 
            "success": "#27ae60",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#3498db")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")