import socket
import os
import threading
import time
from utils.crypto import CryptoManager
from .streaming import StreamManager
from .protocols import TransferProtocol


class FileReceiver:
    def __init__(self, port=8889, cert_dir="~/.filesync/certs"):
        self.port = port
        self.cert_dir = os.path.expanduser(cert_dir)
        self.client_threads = []

        os.makedirs(self.cert_dir, exist_ok=True)

        self.transfer_socket = None
        self.receiver_running = False
        self.receiver_thread = threading.Thread(
            target=self._receiver_loop,
            daemon=False
        )
        self.current_user = None
        self.download_dir = None
        self.transfer_config = None
        self.stream_manager = StreamManager()
        self.protocol = TransferProtocol()

    def start_receiver(self, download_dir: str):
        """Start file receiver in a separate thread"""
        self.stop_receiver()  # Ensure previous receiver is stopped
        time.sleep(0.5)  # Increased delay to ensure socket release
        
        try:
            # Create new socket with SO_REUSEADDR
            self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.transfer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.transfer_socket.bind(('', self.port))
            self.transfer_socket.listen(5)
            self.receiver_running = True
            self.download_dir = download_dir
            
            self.receiver_thread = threading.Thread(
                target=self._receiver_loop, 
                daemon=True
            )
            self.receiver_thread.start()
            print(f"✅ File receiver started on port {self.port}")
            
        except OSError as e:
            print(f"❌ Failed to start receiver: {e}")
            # Try different port if default is busy
            if "Address already in use" in str(e):
                print("🔄 Trying alternative port...")
                self._start_with_alternative_port(download_dir)
            else:
                self.transfer_socket = None
                raise

    def _start_with_alternative_port(self, download_dir: str):
        """Try starting receiver with alternative ports"""
        alternative_ports = [8888, 8890, 8891, 8892, 8893]
        
        for alt_port in alternative_ports:
            try:
                self.port = alt_port
                self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.transfer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                self.transfer_socket.bind(('', self.port))
                self.transfer_socket.listen(5)
                self.receiver_running = True
                self.download_dir = download_dir
                
                self.receiver_thread = threading.Thread(
                    target=self._receiver_loop, 
                    daemon=True
                )
                self.receiver_thread.start()
                print(f"✅ File receiver started on alternative port {self.port}")
                return
                
            except OSError as e:
                print(f"❌ Port {alt_port} also in use: {e}")
                if self.transfer_socket:
                    self.transfer_socket.close()
                    self.transfer_socket = None
                continue
        
        # If all ports fail
        raise OSError("All attempted ports are busy")

    def _receiver_loop(self):
        """Main receiver loop that accepts incoming connections"""

        cert_path = os.path.expanduser(self.cert_dir)
        certfile = os.path.join(cert_path, "server.crt")
        keyfile = os.path.join(cert_path, "server.key")

        # Auto-generate missing certificates
        if not os.path.exists(certfile) or not os.path.exists(keyfile):
            print("🔐 SSL certificates not found, generating new ones...")
            os.makedirs(cert_path, exist_ok=True)
            CryptoManager.generate_ssl_certificates("FileSyncServer", cert_path)

        context = CryptoManager.create_ssl_server_context(self.cert_dir)
        
        while self.receiver_running:
            try:
                self.transfer_socket.settimeout(1.0)
                client_socket, client_address = self.transfer_socket.accept()
                print(f"🔗 Connection from {client_address}")
                
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, context, client_address),
                    daemon=False
            )
                client_thread.start()
                self.client_threads.append(client_thread)
                
            except socket.timeout:
                # Expected timeout, continue loop
                continue
            except OSError as e:
                if self.receiver_running:
                    print(f"⚠️ Receiver loop error: {e}")
                break
            except Exception as e:
                print(f"❌ Unexpected error in receiver loop: {e}")
                break

    def _handle_client(self, client_socket: socket.socket, context, client_address: tuple):
        """Handle a client connection"""
        try:
            with context.wrap_socket(client_socket, server_side=True) as ssock:
                # Receive request metadata
                request_info = self.protocol.receive_request_metadata(ssock)
                if not request_info:
                    return
                
                # Handle transfer request
                if request_info.get('type') == 'transfer_request':
                    self._handle_transfer_request(ssock, request_info)
                    
        except Exception as e:
            print(f"❌ Client handling error: {e}")
            try:
                ssock.send(f"ERROR: {str(e)}".encode())
            except:
                pass
        finally:
            try:
                client_socket.close()
            except:
                pass

    def _handle_transfer_request(self, ssock, request_info):
        """Handle file transfer request"""
        accepted = self._prompt_for_acceptance(request_info)
        
        if accepted:
            ssock.send("ACCEPTED".encode())
            self._receive_file_data(ssock, request_info)
        else:
            ssock.send("DECLINED".encode())

    def _receive_file_data(self, ssock, request_info):
        """Receive file data using streaming"""
        file_info = self.protocol.receive_file_metadata(ssock)
        if not file_info:
            return
        
        # Determine save path
        if file_info.get('is_folder', False):
            save_path = os.path.join(self.download_dir, file_info.get('original_folder_name', file_info['file_name']))
        else:
            save_path = os.path.join(self.download_dir, file_info['file_name'])
        
        # Ensure download directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Receive file with streaming
        success = self.stream_manager.receive_streamed_file(ssock, save_path, file_info, request_info)
        
        if success:
            ssock.send("SUCCESS".encode())
            item_type = "Folder" if file_info.get('is_folder') else "File"
            print(f"✅ {item_type} received: {os.path.basename(save_path)}")
        else:
            ssock.send("ERROR: Transfer failed".encode())

    def _prompt_for_acceptance(self, request_info):
        """Prompt user to accept transfer"""
        if self.transfer_config and self.transfer_config.get_setting('auto_accept'):
            return True
            
        # For GUI implementation, this would show a dialog
        print(f"📨 Incoming transfer from {request_info.get('sender', 'Unknown')}")
        print(f"📄 File: {request_info.get('file_name')}")
        print(f"📦 Size: {self.stream_manager.format_size(request_info.get('file_size', 0))}")
        
        # Auto-accept for now in GUI context
        return True

    def stop_receiver(self):
        """Stop the file receiver with proper cleanup"""
        self.receiver_running = False

        # shutdown and close listening socket to unblock accept()
        if self.transfer_socket:
            try:
                try:
                    # Try to shutdown gracefully first
                    self.transfer_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.transfer_socket.close()
            except Exception as e:
                print(f"⚠️ Error closing socket: {e}")
            finally:
                self.transfer_socket = None

        # Wait for receiver loop to stop
        if self.receiver_thread and self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=5.0)
            if self.receiver_thread.is_alive():
                print("⚠️ Receiver thread didn't terminate cleanly")

        # Wait for client handler threads to finish
        for t in list(self.client_threads):
            if t.is_alive():
                t.join(timeout=3.0)

        # Remove finished threads from list
        self.client_threads = [t for t in self.client_threads if t.is_alive()]

        print("🛑 File receiver stopped")