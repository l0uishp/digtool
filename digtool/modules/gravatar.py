import hashlib
import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class GravatarModule(BaseModule):
    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Gravatar] Checking {email}")
        
        try:
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            url = f"https://www.gravatar.com/{email_hash}?d=404"
            
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            self.rate_limit_sleep()
            
            if response.status_code == 200:
                profile_url = f"https://www.gravatar.com/{email_hash}"
                self.logger.info(f"[Gravatar] Found profile for {email}")
                return {
                    "found": True,
                    "data": {
                        "profile_url": profile_url,
                        "avatar_url": url
                    }
                }
            else:
                self.logger.debug(f"[Gravatar] No profile found for {email}")
                return {"found": False}
                
        except Exception as e:
            self.logger.error(f"[Gravatar] Error: {str(e)}")
            return {"found": False, "error": str(e)}
