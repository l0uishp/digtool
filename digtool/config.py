import json
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            "timeout": 10,
            "rate_limit": 1.0,
            "user_agent": "DigTool/1.0 (OSINT Scanner)",
            "modules": ["gravatar", "adobe", "site_template"],
            "max_workers": 5,
            "verbose": False
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
