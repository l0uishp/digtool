import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class AdobeModule(BaseModule):
    """
    Module DigTool pour vérifier si un email est enregistré sur Adobe.
    Méthode : envoi POST JSON au endpoint officiel.
    Si la réponse est 404, l'email n'existe pas.
    """
    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Adobe] Checking {email}")
        
        url = "https://auth.services.adobe.com/signin/v2/users/accounts"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://auth.services.adobe.com",
            "Referer": "https://auth.services.adobe.com/en_US/index.html#/",
            "Connection": "keep-alive",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-CH-UA": '"Chromium";v="120", "Not A(Brand";v="24", "Microsoft Edge";v="120"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"'
        }
        payload = {
            "username": email,
            "accountType" : "individual"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            self.rate_limit_sleep()
            
            if response.status_code == 404:
                # Email non utilisé
                self.logger.info(f"[Adobe] Email {email} not registered")
                return {"found": False, "data": {"url": url}}
            elif response.status_code == 200:
                # Email déjà utilisé
                self.logger.info(f"[Adobe] Email {email} already registered")
                return {"found": True, "data": {"url": url}}
            else:
                self.logger.warning(f"[Adobe] Unexpected status {response.status_code} for {email}")
                return {"found": False, "error": f"Unexpected status: {response.status_code}"}
        
        except requests.exceptions.Timeout:
            self.logger.error(f"[Adobe] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Adobe] Request error: {str(e)}")
            return {"found": False, "error": str(e)}
        
        except Exception as e:
            self.logger.error(f"[Adobe] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
