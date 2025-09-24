"""
LocalSync - Secure local network file transfer tool
"""

__version__ = "2.0.0"
__author__ = "LocalSync Team"
__email__ = "support@localsync.org"

from .auth import AuthManager
from .discovery import DeviceDiscovery
from .transfer import FileTransfer
from .groups import GroupManager
from .config import TransferConfig

__all__ = [
    "AuthManager",
    "DeviceDiscovery", 
    "FileTransfer",
    "GroupManager",
    "TransferConfig",
]