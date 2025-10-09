import os
from PyQt6.QtCore import QObject, pyqtSignal

class TransferManager(QObject):
    """Handles file transfer operations"""
    
    progress_updated = pyqtSignal(int, str)  # progress, stage
    transfer_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, cli_file_transfer):
        super().__init__()
        self.cli_file_transfer = cli_file_transfer
    
    def send_file(self, file_path: str, recipient_ip: str, 
                 encryption: bool = False, compression: bool = True):
        """Send file to recipient"""
        def transfer_task():
            encryption_password = "default_password" if encryption else None
            compression_method = self.cli_file_transfer.compression_method.ZLIB if compression else self.cli_file_transfer.compression_method.NONE
            
            def progress_callback(transferred, total, stage):
                self.progress_updated.emit(transferred, stage)
            
            if os.path.isfile(file_path):
                success, message = self.cli_file_transfer.send_file(
                    file_path, recipient_ip,
                    progress_callback=progress_callback,
                    encryption_password=encryption_password,
                    compression_method=compression_method
                )
            else:
                success, message = self.cli_file_transfer.send_folder(
                    file_path, recipient_ip,
                    progress_callback=progress_callback,
                    encryption_password=encryption_password,
                    compression_method=compression_method
                )
            return success, message
        return transfer_task
    
    def start_receiver(self, download_dir: str):
        """Start file receiver"""
        self.cli_file_transfer.start_receiver(download_dir)
    
    def stop_receiver(self):
        """Stop file receiver"""
        self.cli_file_transfer.stop_receiver()