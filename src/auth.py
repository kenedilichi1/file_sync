import json
import hashlib
import os
from getpass import getpass

class AuthManager:
    def __init__(self, config_dir="~/.filesync"):
        self.config_dir: str = os.path.expanduser(config_dir)
        self.users_file: str = os.path.join(self.config_dir, "users.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> tuple[bool, str]:
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        else:
            users = {}
            
        if username in users:
            return False, "Username already exists"
            
        users[username] = {
            'password_hash': self._hash_password(password),
            'device_name': os.uname().nodename if hasattr(os, 'uname') else os.environ['COMPUTERNAME']
        }
        
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
            
        return True, "Registration successful"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        if not os.path.exists(self.users_file):
            return False, "No users registered"
            
        with open(self.users_file, 'r') as f:
            users = json.load(f)
            
        if username not in users:
            return False, "User not found"
            
        if users[username]['password_hash'] != self._hash_password(password):
            return False, "Invalid password"
            
        return True, "Login successful"