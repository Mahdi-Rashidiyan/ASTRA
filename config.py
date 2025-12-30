"""
Configuration management for HPCShell
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """HPCShell configuration"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(Path.home() / '.hpcshellrc')
        self.config = self._load_default_config()
        self._load_user_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'shell': {
                'prompt_color': True,
                'history_size': 1000,
                'tab_completion': True,
            },
            'executor': {
                'default_cores': 1,
                'default_memory': '1GB',
                'default_priority': 'normal',
            },
            'scheduler': {
                'queues': ['default', 'long', 'gpu', 'short'],
                'max_jobs_per_user': 100,
                'scheduling_algorithm': 'fifo',
            },
            'monitor': {
                'update_interval': 1.0,
                'history_retention': 3600,
            },
            'benchmark': {
                'cpu_duration': 5,
                'memory_size': 100 * 1024 * 1024,  # 100MB
                'disk_file_size': 100 * 1024 * 1024,  # 100MB
            },
            'logging': {
                'level': 'INFO',
                'file': str(Path.home() / '.hpcshell.log'),
            },
            # In config.py, add to _load_default_config:
            'cern': {
                'root_path': '/usr/local/bin/root',  # Default ROOT installation path
                'data_portal_url': 'https://opendata.cern.ch',
                'default_dataset': 'CMS/2012/CSV',
                'grid_cert_path': '~/.globus/certificates',
                'batch_system': 'HTCondor',  # Default to HTCondor used at CERN
                'cernvm_image': 'cernvm.cern.ch',
                }
        }
    
    def _load_user_config(self):
        """Load user configuration file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def _merge_config(self, user_config: Dict):
        """Merge user config with defaults"""
        for section, values in user_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def get(self, section: str, key: str = None, default=None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")