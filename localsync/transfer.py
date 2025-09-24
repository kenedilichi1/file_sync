import socket
import os
import json
import hashlib
import threading
import time
import uuid
import tarfile
import tempfile
from typing import Callable, Optional
from pathlib import Path

from .utils.crypto import CryptoManager
from .utils.compression import CompressionManager, CompressionMethod
from .config import TransferConfig


class FileTransfer:
    def __init__(self, port=8889, cert_dir="~/.localsync/certs"):
        self.port = port
        self.transfer_socket = None
        self.cert_dir = cert_dir
        self.running = False
        self.pending_requests = {}
        self.request_timeout = 120
        self.current_user = None
        self.transfer_config = TransferConfig()
        
        # Ensure certificate directory exists
        os.makedirs(cert_dir, exist_ok=True)
        
        # Generate certificates if they don't exist
        cert_file = os.path.join(cert_dir, "server.crt")
        key_file = os.path.join(cert_dir, "server.key")
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            CryptoManager.generate_ssl_certificates("localsync", self.cert_dir)

    # ==================== PUBLIC METHODS ====================

    def send_folder(self, folder_path: str, recipient_ip: str, 
                   progress_callback: Optional[Callable] = None,
                   encryption_password: Optional[str] = None,
                   compression_method: CompressionMethod = CompressionMethod.ZLIB) -> tuple:
        """Send a folder (recursively) to recipient"""
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return False, "Folder does not exist or is not a directory"
            
        folder_name = os.path.basename(folder_path.rstrip(os.sep))
        temp_path = None
        
        try:
            # Count folder items first
            item_count = self._count_folder_items(folder_path)
            
            # Create a temporary tar archive of the folder
            with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as temp_tar:
                temp_path = temp_tar.name
            
            # Create tar archive
            with tarfile.open(temp_path, 'w') as tar:
                tar.add(folder_path, arcname=folder_name)
            
            # Send the tar file with special metadata
            success, message = self.send_file(
                temp_path, 
                recipient_ip, 
                progress_callback,
                encryption_password,
                compression_method,
                is_folder=True,
                original_folder_name=folder_name,
                item_count=item_count  # Pass the item count
            )
            
            return success, message
            
        except Exception as e:
            return False, f"Error preparing folder: {str(e)}"
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def send_file(
            self, 
            file_path: str, 
            recipient_ip: str, 
            progress_callback: Optional[Callable] = None,
            encryption_password: Optional[str] = None,
            compression_method: CompressionMethod = CompressionMethod.ZLIB,
            is_folder: bool = False,
            original_folder_name: str = None,
            item_count: dict = None) -> tuple:  # Add item_count parameter
        """Send a file to recipient with acceptance protocol"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
            
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Read and process file data
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
        except IOError as e:
            return False, f"Error reading file: {str(e)}"
        
        # Compress data
        if progress_callback:
            progress_callback(0, file_size, "Compressing")
        compressed_data = CompressionManager.compress_data(file_data, compression_method)
        
        # Encrypt data if password provided
        if encryption_password:
            if progress_callback:
                progress_callback(0, file_size, "Encrypting")
            encrypted_data = CryptoManager.encrypt_data(compressed_data, encryption_password)
            transfer_data = encrypted_data
        else:
            transfer_data = compressed_data
        
        # Create connection and transfer
        try:
            context = CryptoManager.create_ssl_client_context()
            with socket.create_connection((recipient_ip, self.port), timeout=30) as sock:
                with context.wrap_socket(sock, server_hostname=recipient_ip) as ssock:
                    
                    # Send transfer request with item count for folders
                    if not self._send_transfer_request(ssock, file_name, file_size, is_folder, item_count):
                        return False, "Transfer request failed"
                    
                    # Send file metadata and data
                    return self._send_file_data(
                        ssock, file_data, transfer_data, file_name, 
                        file_size, encryption_password, compression_method,
                        is_folder, original_folder_name, progress_callback
                    )

        except socket.timeout:
            return False, "Connection timeout"
        except ConnectionRefusedError:
            return False, "Connection refused"
        except Exception as e:
            return False, f"Error sending file: {str(e)}"

    def start_receiver(self, download_dir="."):
        """Start file receiver server with acceptance capability"""
        self.download_dir = download_dir
        self.running = True
        
        context = CryptoManager.create_ssl_context(
            os.path.join(self.cert_dir, "server.crt"),
            os.path.join(self.cert_dir, "server.key")
        )
        
        self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transfer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.transfer_socket.bind(('', self.port))
        self.transfer_socket.listen(5)
        
        # Start listening for incoming transfers
        self.receiver_thread = threading.Thread(target=self._accept_connections, args=(context,))
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def stop_receiver(self):
        """Stop the file receiver"""
        self.running = False
        if self.transfer_socket:
            self.transfer_socket.close()

    # ==================== PRIVATE TRANSFER METHODS ====================

    def _send_transfer_request(self, ssock, file_name, file_size, is_folder, item_count=None):
        """Send transfer request and wait for acceptance"""
        request_metadata = {
            'type': 'transfer_request',
            'file_name': file_name,
            'file_size': file_size,
            'sender': self.current_user,
            'timestamp': time.time(),
            'request_id': str(uuid.uuid4()),
            'is_folder': is_folder,
        }
        
        # Add item count for folders
        if is_folder and item_count:
            request_metadata['item_count'] = item_count
        
        ssock.send(json.dumps(request_metadata).encode() + b'<REQUEST_END>')
        
        # Wait for recipient response
        response = ssock.recv(1024).decode()
        if response == "DECLINED":
            return False
        elif response != "ACCEPTED":
            return False
        return True

    def _send_file_data(
            self, 
            ssock, 
            original_data, 
            transfer_data, 
            file_name, 
            file_size, encryption_password, compression_method,
            is_folder, original_folder_name, progress_callback):
        """Send file metadata and data after acceptance"""
        metadata = {
            'file_name': file_name,
            'file_size': file_size,
            'compressed_size': len(transfer_data),
            'compression_method': compression_method.value,
            'encrypted': encryption_password is not None,
            'checksum': self._calculate_checksum(original_data),
            'timestamp': time.time(),
            'is_folder': is_folder,
            'original_folder_name': original_folder_name or file_name
        }

        ssock.send(json.dumps(metadata).encode() + b'<METADATA_END>')
        
        # Send file data with progress
        total_sent = 0
        chunk_size = 16384
        
        for i in range(0, len(transfer_data), chunk_size):
            chunk = transfer_data[i:i+chunk_size]
            ssock.send(chunk)
            total_sent += len(chunk)
            
            if progress_callback:
                progress_callback(total_sent, len(transfer_data), "Sending")
        
        # Wait for acknowledgment
        ack = ssock.recv(1024).decode()
        if ack != "SUCCESS":
            return False, f"Transfer failed: {ack}"
        
        return True, "File sent successfully"

    # ==================== RECEIVER METHODS ====================

    def _accept_connections(self, context):
        """Accept incoming connections and handle them"""
        while self.running:
            try:
                client_socket, addr = self.transfer_socket.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, context))
                client_thread.daemon = True
                client_thread.start()
            except OSError:
                break

    def _handle_client(self, client_socket, context):
        """Handle a client connection"""
        try:
            with context.wrap_socket(client_socket, server_side=True) as ssock:
                # Receive and process request
                request_info = self._receive_request_metadata(ssock)
                if not request_info:
                    return
                
                # Handle transfer request
                if request_info.get('type') == 'transfer_request':
                    self._handle_transfer_request(ssock, request_info)
                    
        except Exception as e:
            try:
                ssock.send(f"ERROR: {str(e)}".encode())
            except:
                pass
        finally:
            client_socket.close()

    def _receive_request_metadata(self, ssock):
        """Receive and parse request metadata"""
        request_data = b''
        while True:
            chunk = ssock.recv(1024)
            request_data += chunk
            if b'<REQUEST_END>' in request_data:
                break
            if len(request_data) > 65536:
                ssock.send("ERROR: Request too large".encode())
                return None
        
        request_str = request_data.split(b'<REQUEST_END>')[0].decode()
        return json.loads(request_str)

    def _handle_transfer_request(self, ssock, request_info):
        """Handle a file transfer request"""
        accepted = self._prompt_for_acceptance(request_info)
        
        if accepted:
            ssock.send("ACCEPTED".encode())
            self._receive_file_data(ssock, request_info)
        else:
            ssock.send("DECLINED".encode())

    def _receive_file_data(self, ssock, request_info):
        """Receive and process file data after acceptance"""
        # Receive file metadata
        file_info = self._receive_file_metadata(ssock)
        if not file_info:
            return
        
        is_folder = file_info.get('is_folder', False)
        original_name = file_info.get('original_folder_name', file_info['file_name'])
        
        if is_folder:
            success = self._receive_and_extract_folder(ssock, file_info, original_name)
        else:
            success = self._receive_single_file(ssock, file_info)
        
        if success:
            ssock.send("SUCCESS".encode())
            item_type = "Folder" if is_folder else "File"
            print(f"✅ {item_type} received: {original_name}")
        else:
            ssock.send("ERROR: Transfer failed".encode())

    def _receive_file_metadata(self, ssock):
        """Receive and parse file metadata"""
        metadata = b''
        while True:
            chunk = ssock.recv(1024)
            metadata += chunk
            if b'<METADATA_END>' in metadata:
                break
            if len(metadata) > 65536:
                ssock.send("ERROR: Metadata too large".encode())
                return None
        
        metadata_str = metadata.split(b'<METADATA_END>')[0].decode()
        return json.loads(metadata_str)

    def _receive_single_file(self, ssock, file_info):
        """Receive a single file"""
        received_path = os.path.join(self.download_dir, file_info['file_name'])
        temp_path = received_path + '.part'
        
        try:
            # Receive file data
            with open(temp_path, 'wb') as f:
                remaining = file_info['compressed_size']
                while remaining > 0:
                    chunk_size = min(16384, remaining)
                    data = ssock.recv(chunk_size)
                    if not data:
                        break
                    f.write(data)
                    remaining -= len(data)
            
            # Process and verify file
            return self._process_received_file(temp_path, received_path, file_info)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    def _receive_and_extract_folder(self, ssock, file_info, folder_name):
        """Receive and extract a folder from tar archive"""
        temp_path = os.path.join(self.download_dir, f"{folder_name}.tar.part")
        final_path = os.path.join(self.download_dir, folder_name)
        
        try:
            # Receive the tar file
            with open(temp_path, 'wb') as f:
                remaining = file_info['compressed_size']
                while remaining > 0:
                    chunk_size = min(16384, remaining)
                    data = ssock.recv(chunk_size)
                    if not data:
                        break
                    f.write(data)
                    remaining -= len(data)
            
            # Process and extract folder
            return self._process_received_folder(temp_path, final_path, file_info)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    # ==================== FILE PROCESSING METHODS ====================

    def _process_received_file(self, temp_path, final_path, file_info):
        """Process and verify a received file"""
        try:
            with open(temp_path, 'rb') as f:
                received_data = f.read()
            
            # Decompress
            compression_method = CompressionMethod(file_info['compression_method'])
            decompressed_data = CompressionManager.decompress_data(received_data, compression_method)
            
            # Verify checksum
            if self._calculate_checksum(decompressed_data) != file_info['checksum']:
                return False
            
            # Save final file
            with open(final_path, 'wb') as f:
                f.write(decompressed_data)
            
            os.remove(temp_path)
            return True
            
        except Exception:
            return False

    def _process_received_folder(self, temp_path, final_path, file_info):
        """Process and extract a received folder"""
        try:
            with open(temp_path, 'rb') as f:
                received_data = f.read()
            
            # Decompress if needed
            compression_method = CompressionMethod(file_info['compression_method'])
            if compression_method != CompressionMethod.NONE:
                received_data = CompressionManager.decompress_data(received_data, compression_method)
            
            # Save decompressed tar file
            tar_path = temp_path + ".decompressed"
            with open(tar_path, 'wb') as f:
                f.write(received_data)
            
            # Extract tar archive
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(path=self.download_dir)
            
            # Clean up temporary files
            try:
                os.unlink(temp_path)
                os.unlink(tar_path)
            except:
                pass
            
            return os.path.exists(final_path)
            
        except Exception:
            # Clean up on error
            try:
                os.unlink(temp_path)
                os.unlink(temp_path + ".decompressed")
            except:
                pass
            return False

    # ==================== UI & UTILITY METHODS ====================

    def _prompt_for_acceptance(self, request_info):
        """Prompt user to accept or decline transfer"""
        # Auto-accept check
        if self.transfer_config.should_auto_accept(request_info):
            print(f"\n✅ Auto-accepted transfer from {request_info['sender']}")
            item_type = "folder" if request_info.get('is_folder') else "file"
            print(f"   {item_type.capitalize()}: {request_info['file_name']}")
            return True
        
        # Show detailed transfer request
        is_folder = request_info.get('is_folder', False)
        item_type = "folder" if is_folder else "file"
        
        print(f"\n📨 Incoming {item_type} transfer request:")
        print(f"   From: {request_info['sender']}")
        print(f"   Name: {request_info['file_name']}")
        print(f"   Size: {self._format_file_size(request_info['file_size'])}")
        
        if is_folder:
            item_count = request_info.get('item_count', {})
            print(f"   Contents: {item_count.get('files', 0)} files, {item_count.get('folders', 0)} folders")
        
        # Get user response with timeout
        response = None
        response_event = threading.Event()
        
        def timeout_handler():
            time.sleep(self.request_timeout)
            if not response_event.is_set():
                print("\n⏰ Request timed out - automatically declined")
                return False
        
        timeout_thread = threading.Thread(target=timeout_handler)
        timeout_thread.daemon = True
        timeout_thread.start()
        
        try:
            user_input = input("Accept transfer? (y/n): ").lower().strip()
            if user_input in ['y', 'yes']:
                response = True
            elif user_input in ['n', 'no']:
                response = False
        except (EOFError, KeyboardInterrupt):
            response = False
            print("\nTransfer declined")
        
        response_event.set()
        return response if response is not None else False

    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _calculate_checksum(self, data):
        """Calculate MD5 checksum of data"""
        return hashlib.md5(data).hexdigest()

    def _count_folder_items(self, folder_path):
        """Count files and folders in a directory"""
        file_count = 0
        folder_count = 0
        for root, dirs, files in os.walk(folder_path):
            folder_count += len(dirs)
            file_count += len(files)
        return {'files': file_count, 'folders': folder_count}