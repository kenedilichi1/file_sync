import json
import os
import time
from unittest import case

class GroupManager:
    def __init__(self, config_dir="~/.filesync"):
        self.config_dir = os.path.expanduser(config_dir)
        self.groups_file = os.path.join(self.config_dir, "groups.json")
        self._ensure_config_dir()
        
    def _ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def create_group(self, group_name, members):
        if os.path.exists(self.groups_file):
            with open(self.groups_file, 'r') as f:
                groups = json.load(f)
        else:
            groups = {}

        match group_name in groups:
            case True:
                return False, "Group already exists"
            case False:
                groups[group_name] = {
                    'members': members,
                    'created_at': time.time()
                }
                with open(self.groups_file, 'w') as f:
                    json.dump(groups, f)
                return True, "Group created successfully"
    def get_user_groups(self, username):
        if not os.path.exists(self.groups_file):
            return {}
            
        with open(self.groups_file, 'r') as f:
            groups = json.load(f)
            
        user_groups = {}
        for group_name, group_info in groups.items():
            if username in group_info['members']:
                user_groups[group_name] = group_info
                
        return user_groups