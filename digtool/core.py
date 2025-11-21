import concurrent.futures
from typing import Dict, Any
from digtool.modules import get_all_modules

class DigToolCore:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.modules = get_all_modules()
        
    def scan(self, email: str) -> Dict[str, Any]:
        results = {}
        active_modules = self.config.data.get("modules", [])
        max_workers = self.config.data.get("max_workers", 5)
        
        modules_to_run = [
            (name, mod) for name, mod in self.modules.items()
            if not active_modules or name in active_modules
        ]
        
        self.logger.info(f"Starting scan for: {email}")
        self.logger.info(f"Running {len(modules_to_run)} modules with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_module = {
                executor.submit(self._run_module, mod, email): name
                for name, mod in modules_to_run
            }
            
            for future in concurrent.futures.as_completed(future_to_module):
                module_name = future_to_module[future]
                try:
                    results[module_name] = future.result()
                except Exception as e:
                    self.logger.error(f"Module {module_name} failed: {str(e)}")
                    results[module_name] = {
                        "found": False,
                        "error": str(e)
                    }
        
        return results
    
    def _run_module(self, module_class, email: str) -> Dict[str, Any]:
        module = module_class(self.config, self.logger)
        return module.check(email)
