import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class AdobeModule(BaseModule):
    """
    Module DigTool pour vérifier si un email est enregistré sur Adobe.
    Méthode : analyse le message de la page d'authentification
    """
    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Adobe] Checking {email}")
        
        try:
            # URL de la page d'authentification
            url = "https://auth.services.adobe.com/en_US/index.html#/"
            
            # Headers pour simuler un navigateur
            headers = {
                "User-Agent": self.user_agent,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            # Envoi de l'email (Adobe peut utiliser POST via JS, ici on tente POST simple)
            data = {"username": email}
            response = requests.post(url, headers=headers, data=data, timeout=self.timeout)
            
            # Respect du rate limit
            self.rate_limit_sleep()
            
            # Vérification du texte retourné
            if "No account associated with this email address" in response.text:
                self.logger.info(f"[Adobe] Email {email} not registered")
                return {"found": False, "data": {"url": url}}
            else:
                self.logger.info(f"[Adobe] Email {email} already registered")
                return {"found": True, "data": {"url": url}}
        
        except requests.exceptions.Timeout:
            self.logger.error(f"[Adobe] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Adobe] Request error: {str(e)}")
            return {"found": False, "error": str(e)}
        
        except Exception as e:
            self.logger.error(f"[Adobe] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
