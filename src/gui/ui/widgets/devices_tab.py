import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import QTimer, pyqtSignal

class DevicesTab(QWidget):
    refresh_clicked = pyqtSignal()
    device_double_clicked = pyqtSignal(str)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_clicked.emit)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        # Devices tree
        self.devices_tree = QTreeWidget()
        self.devices_tree.setHeaderLabels(["Username", "Device Name", "IP Address", "Status"])
        self.devices_tree.setColumnWidth(0, 120)
        self.devices_tree.setColumnWidth(1, 150)
        self.devices_tree.setColumnWidth(2, 120)
        self.devices_tree.setColumnWidth(3, 100)
        
        # Connect double click
        self.devices_tree.itemDoubleClicked.connect(self.on_device_double_click)
        
        layout.addWidget(self.devices_tree)
        
    def connect_signals(self):
        """Connect controller signals to UI slots"""
        self.controller.devices_updated.connect(self.update_devices_list)
        
    def update_devices_list(self, devices):
        """Update devices treeview"""
        self.devices_tree.clear()

        for device in devices:
            if device['username'] != self.controller.current_user:
                last_seen = device.get('last_seen')
                status = "🟢 Online" if last_seen else "🟡 Away"

                item = QTreeWidgetItem([
                    device['username'],
                    device['device_name'],
                    device['ip_address'],
                    status
                ])
                self.devices_tree.addTopLevelItem(item)

                
    def on_device_double_click(self, item, column):
        """Handle double click on device"""
        username = item.text(0)
        self.device_double_clicked.emit(username)