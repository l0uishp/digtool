from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class BaseModule(ABC):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.timeout = config.get("timeout", 10)
        self.rate_limit = config.get("rate_limit", 1.0)
        self.user_agent = config.get("user_agent", "DigTool/1.0")
    
    @abstractmethod
    def check(self, email: str) -> Dict[str, Any]:
        pass
    
    def rate_limit_sleep(self):
        time.sleep(self.rate_limit)
