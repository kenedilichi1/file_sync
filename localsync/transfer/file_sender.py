import socket
import os
import json
import uuid
import time
from typing import Optional, Callable
from ..utils.crypto import CryptoManager
from ..utils.compression import CompressionManager, CompressionMethod
from .streaming import StreamManager


class FileSender:
    def __init__(self, port=8889, cert_dir="~/.localsync/certs"):
        self.port = port
        self.cert_dir = cert_dir
        self.current_user = None
        self.stream_manager = StreamManager()

    def send_file(self, file_path: str, recipient_ip: str, 
                 progress_callback: Optional[Callable] = None,
                 encryption_password: Optional[str] = None,
                 compression_method: CompressionMethod = CompressionMethod.ZLIB) -> tuple:
        """Send file using streaming to handle large files"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
            
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Warn about large files
        if file_size > 1024 * 1024 * 1024:  # 1GB
            print(f"⚠️  Large file detected: {self.stream_manager.format_size(file_size)}")
            print("⏳ This may take several minutes...")
        
        try:
            context = CryptoManager.create_ssl_client_context()
            with socket.create_connection((recipient_ip, self.port), timeout=120) as sock:
                with context.wrap_socket(sock, server_hostname=recipient_ip) as ssock:
                    
                    # Send transfer request
                    if not self._send_transfer_request(ssock, file_name, file_size, False):
                        return False, "Transfer request failed"
                    
                    # Calculate checksum
                    print("🔍 Calculating file checksum...")
                    file_checksum = self.stream_manager.calculate_file_checksum(file_path)
                    
                    # Send file metadata
                    if not self._send_file_metadata(ssock, file_name, file_size, file_checksum, 
                                                   encryption_password, compression_method, False):
                        return False, "Failed to send metadata"
                    
                    # Stream file data
                    success = self.stream_manager.stream_file_data(
                        ssock, file_path, file_size, 
                        encryption_password, compression_method, 
                        progress_callback
                    )
                    
                    if success:
                        ack = ssock.recv(1024).decode()
                        if ack == "SUCCESS":
                            return True, "File sent successfully"
                        else:
                            return False, f"Transfer failed: {ack}"
                    else:
                        return False, "File streaming failed"
                        
        except socket.timeout:
            return False, "Connection timeout - file may be too large"
        except ConnectionRefusedError:
            return False, "Connection refused"
        except Exception as e:
            return False, f"Error sending file: {str(e)}"

    def _send_transfer_request(self, ssock, file_name: str, file_size: int, is_folder: bool) -> bool:
        """Send transfer request to recipient"""
        request_metadata = {
            'type': 'transfer_request',
            'file_name': file_name,
            'file_size': file_size,
            'sender': self.current_user,
            'timestamp': time.time(),
            'request_id': str(uuid.uuid4()),
            'is_folder': is_folder
        }
        
        try:
            ssock.send(json.dumps(request_metadata).encode() + b'<REQUEST_END>')
            response = ssock.recv(1024).decode()
            return response == "ACCEPTED"
        except:
            return False

    def _send_file_metadata(self, ssock, file_name: str, file_size: int, checksum: str,
                           encryption_password: Optional[str], compression_method: CompressionMethod,
                           is_folder: bool) -> bool:
        """Send file metadata to recipient"""
        metadata = {
            'file_name': file_name,
            'file_size': file_size,
            'compression_method': compression_method.value,
            'encrypted': encryption_password is not None,
            'checksum': checksum,
            'timestamp': time.time(),
            'is_folder': is_folder
        }
        
        try:
            ssock.send(json.dumps(metadata).encode() + b'<METADATA_END>')
            return True
        except:
            return False

    def send_folder(self, folder_path: str, recipient_ip: str, 
                   progress_callback: Optional[Callable] = None,
                   encryption_password: Optional[str] = None,
                   compression_method: CompressionMethod = CompressionMethod.ZLIB) -> tuple:
        """Send folder with streaming support"""
        return self.stream_manager.send_folder_as_archive(
            self, folder_path, recipient_ip, progress_callback,
            encryption_password, compression_method
        )