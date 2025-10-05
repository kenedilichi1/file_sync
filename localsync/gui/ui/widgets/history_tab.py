from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit
)
from PyQt6.QtCore import pyqtSignal

class HistoryTab(QWidget):
    clear_requested = pyqtSignal()
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # History text area
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        # Clear button
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(clear_btn)
        
    def connect_signals(self):
        """Connect controller signals to UI slots"""
        self.controller.history_updated.connect(self.add_to_history)
        
    def add_to_history(self, message):
        """Add message to history"""
        self.history_text.append(message)
        
    def clear_history(self):
        """Clear history"""
        self.history_text.clear()