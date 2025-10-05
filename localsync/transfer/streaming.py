import os
import hashlib
import tempfile
import tarfile
import time
from typing import Optional, Callable
from ..utils.crypto import CryptoManager
from ..utils.compression import CompressionManager, CompressionMethod


class StreamManager:
    def __init__(self):
        pass

    def stream_file_data(self, ssock, file_path: str, file_size: int,
                        encryption_password: Optional[str], 
                        compression_method: CompressionMethod,
                        progress_callback: Optional[Callable]) -> bool:
        """Stream file data in chunks without loading entire file into memory"""
        chunk_size = 64 * 1024  # 64KB chunks
        total_sent = 0
        
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    processed_chunk = self._process_chunk(
                        chunk, encryption_password, compression_method
                    )
                    
                    chunk_size_data = len(processed_chunk).to_bytes(4, byteorder='big')
                    ssock.send(chunk_size_data + processed_chunk)
                    
                    total_sent += len(chunk)
                    
                    if progress_callback:
                        progress_callback(total_sent, file_size, "Sending")
                    
                    time.sleep(0.001)
                
                ssock.send(b'\x00\x00\x00\x00')  # EOF marker
                return True
                
        except Exception as e:
            print(f"Streaming error: {e}")
            return False

    def _process_chunk(self, chunk, encryption_password, compression_method):
        """Process a single chunk of data"""
        if compression_method != CompressionMethod.NONE:
            try:
                chunk = CompressionManager.compress_data(chunk, compression_method)
            except:
                pass
        
        if encryption_password:
            try:
                chunk = CryptoManager.encrypt_data(chunk, encryption_password)
            except:
                pass
        
        return chunk

    def receive_streamed_file(self, ssock, save_path: str, file_info: dict, request_info: dict) -> bool:
        """Receive file using streaming"""
        temp_path = save_path + '.part'
        hash_md5 = hashlib.md5()
        total_received = 0
        
        try:
            with open(temp_path, 'wb') as file:
                while True:
                    chunk_size_data = ssock.recv(4)
                    if not chunk_size_data:
                        break
                    
                    chunk_size = int.from_bytes(chunk_size_data, byteorder='big')
                    if chunk_size == 0:
                        break
                    
                    chunk_data = b''
                    while len(chunk_data) < chunk_size:
                        remaining = chunk_size - len(chunk_data)
                        chunk_data += ssock.recv(min(4096, remaining))
                    
                    processed_chunk = self._process_received_chunk(chunk_data, file_info)
                    file.write(processed_chunk)
                    hash_md5.update(processed_chunk)
                    
                    total_received += len(processed_chunk)
                    
                    if request_info['file_size'] > 100 * 1024 * 1024:
                        progress = (total_received / request_info['file_size']) * 100
                        print(f"📥 Receiving: {progress:.1f}%", end='\r')
                
                print()
                
            if hash_md5.hexdigest() != file_info['checksum']:
                print("❌ Checksum mismatch - file may be corrupted")
                os.unlink(temp_path)
                return False
            
            os.rename(temp_path, save_path)
            return True
            
        except Exception as e:
            print(f"❌ Receive error: {e}")
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            return False

    def _process_received_chunk(self, chunk_data, file_info):
        """Process a received chunk"""
        # Add decompression/decryption logic here
        return chunk_data

    def calculate_file_checksum(self, file_path):
        """Calculate MD5 checksum incrementally for large files"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def send_folder_as_archive(self, sender, folder_path: str, recipient_ip: str, 
                              progress_callback: Optional[Callable],
                              encryption_password: Optional[str],
                              compression_method: CompressionMethod) -> tuple:
        """Send folder as tar archive"""
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return False, "Folder does not exist or is not a directory"
            
        temp_path = None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as temp_tar:
                temp_path = temp_tar.name
            
            print("📦 Creating archive...")
            folder_name = os.path.basename(folder_path.rstrip(os.sep))
            with tarfile.open(temp_path, 'w') as tar:
                tar.add(folder_path, arcname=folder_name)
            
            success, message = sender.send_file(
                temp_path, recipient_ip, progress_callback,
                encryption_password, compression_method
            )
            
            return success, message
            
        except Exception as e:
            return False, f"Error preparing folder: {str(e)}"
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def format_size(self, size_bytes):
        """Format file size human-readably"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"