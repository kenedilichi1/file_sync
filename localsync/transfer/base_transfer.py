import socket
import os
import json
import threading
import time
from typing import Optional, Callable

from .file_sender import FileSender
from .file_receiver import FileReceiver
from .streaming import StreamManager
from ..utils.crypto import CryptoManager
from ..utils.compression import CompressionMethod
from ..config import TransferConfig


class FileTransfer:
    def __init__(self, port=8889, cert_dir="~/.localsync/certs"):
        self.port = port
        self.cert_dir = os.path.expanduser(cert_dir)
        self.current_user = None
        self.transfer_config = TransferConfig()
        
        # Initialize components
        self.sender = FileSender(port, cert_dir)
        self.receiver = FileReceiver(port, cert_dir)
        self.stream_manager = StreamManager()
        
        # Ensure certificate directory exists
        os.makedirs(self.cert_dir, exist_ok=True)
        
        # Generate certificates if they don't exist
        cert_file = os.path.join(self.cert_dir, "server.crt")
        key_file = os.path.join(self.cert_dir, "server.key")
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            CryptoManager.generate_ssl_certificates("localsync", self.cert_dir)

    def get_current_port(self):
        """Get the current port being used by the receiver"""
        return self.receiver.port

    def send_file(self, file_path: str, recipient_ip: str, 
                 progress_callback: Optional[Callable] = None,
                 encryption_password: Optional[str] = None,
                 compression_method: CompressionMethod = CompressionMethod.ZLIB) -> tuple:
        """Send file using streaming to handle large files"""
        self.sender.current_user = self.current_user
        # Use the receiver's current port in case it changed
        self.sender.port = self.receiver.port
        return self.sender.send_file(
            file_path, recipient_ip, progress_callback,
            encryption_password, compression_method
        )

    def send_folder(self, folder_path: str, recipient_ip: str, 
                   progress_callback: Optional[Callable] = None,
                   encryption_password: Optional[str] = None,
                   compression_method: CompressionMethod = CompressionMethod.ZLIB) -> tuple:
        """Send folder with streaming support"""
        self.sender.current_user = self.current_user
        # Use the receiver's current port in case it changed
        self.sender.port = self.receiver.port
        return self.sender.send_folder(
            folder_path, recipient_ip, progress_callback,
            encryption_password, compression_method
        )

    def start_receiver(self, download_dir: str):
        """Start file receiver"""
        self.receiver.current_user = self.current_user
        self.receiver.download_dir = download_dir
        self.receiver.transfer_config = self.transfer_config
        self.receiver.start_receiver(download_dir)

    def stop_receiver(self):
        """Stop file receiver"""
        self.receiver.stop_receiver()

    def set_current_user(self, username: str):
        """Set current user for both sender and receiver"""
        self.current_user = username
        self.sender.current_user = username
        self.receiver.current_user = username