import os
import json

class TransferConfig:
    def __init__(self, config_dir="~/.filesync"):
        self.config_dir = os.path.expanduser(config_dir)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "auto_accept": False,
            "auto_accept_senders": [],  # List of trusted senders
            "max_auto_accept_size": 104857600,  # 100MB max for auto-accept
            "default_download_dir": "~/Downloads",
            "notifications": True,
            "request_timeout": 120,
            "always_ask_for_large_files": True,
            "large_file_threshold": 104857600  # 100MB
        }
        self.config = self._load_config()
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _load_config(self):
        """Load config from file or use defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Save current config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def should_auto_accept(self, request_info):
        """Determine if transfer should be auto-accepted"""
        if not self.config['auto_accept']:
            return False
        
        # Check if sender is trusted
        if request_info['sender'] in self.config['auto_accept_senders']:
            # Check file size limit
            if request_info['file_size'] <= self.config['max_auto_accept_size']:
                return True
        
        return False
    
    def update_setting(self, key, value):
        """Update a configuration setting"""
        if key in self.config:
            self.config[key] = value
            return self.save_config()
        return False
    
    def get_setting(self, key):
        """Get a configuration setting"""
        return self.config.get(key)