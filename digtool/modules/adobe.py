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
            'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-IMS-CLIENTID': 'adobedotcom2',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://auth.services.adobe.com',
        'DNT': '1',
        'Connection': 'keep-alive',
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
