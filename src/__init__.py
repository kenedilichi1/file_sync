"""
FileSync - Secure File Sharing Over Local Network
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

import os
import sys
import platform

def get_platform_config():
    """Get platform-specific configuration"""
    system = platform.system().lower()
    
    config = {
        'system': system,
        'config_dir': None,
        'downloads_dir': None
    }
    
    # Set configuration directory
    if system == 'windows':
        config['config_dir'] = os.path.join(os.environ.get('APPDATA'), 'FileSync')
        config['downloads_dir'] = os.path.join(os.path.expanduser('~'), 'Downloads')
    elif system == 'darwin':  # macOS
        config['config_dir'] = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'FileSync')
        config['downloads_dir'] = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:  # Linux and other Unix-like systems
        config['config_dir'] = os.path.join(os.path.expanduser('~'), '.filesync')
        config['downloads_dir'] = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    return config