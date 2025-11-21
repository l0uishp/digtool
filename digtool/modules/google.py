import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class GoogleModule(BaseModule):
    """
    Module DigTool pour vérifier si un email est enregistré sur Google.
    Méthode : envoi POST sur le endpoint batchexecute.
    """
    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Google] Checking {email}")
        
        url = "https://accounts.google.com/v3/signin/_/AccountsSignInUi/data/batchexecute"
        
        # Headers réalistes pour simuler un navigateur
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://accounts.google.com",
            "Referer": "https://accounts.google.com/signin/v2/identifier",
            "Connection": "keep-alive"
        }
        
        # Préparer le payload : f.req avec l’email
        payload = {
            "f.req": f'[[["MI613e","[null,\\"{email}\\",1,null,null,1,1,null,null,null,null,null,null,null,null,null,null,null,null,null,null,\\"\\",\\"FR\\",null,[\\"youtube:353\\",\\"youtube\\",1],null,null,null,null,7,null,null,null,null,null,null,null,null,[\\"S-1559915780:1763758189184134\\",[null,null,null,null,null,null,null,0,0,1,\\"\\",null,null,1,1,2]]",null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,[]],null,null,null,[null,null,null,null,null,[null,[["continue",[["https://www.google.com/"]]]],[["dsh",["S-1559915780:1763758189184134"]]],["gae",["cb-none"]],["hl",["fr"]],["ifkv",["ARESoU3NPw4MVjj14YezNG0Ocz2jRNImImhxur5-FD3KXGsHVSrbyLgbId03phgod9Khw9j6JHHF"]],["flowName",["GlifWebSignIn"]],["flowEntry",["ServiceLogin"]]]]', 
            "at": ""  # Ici tu peux mettre un token si nécessaire
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=self.timeout)
            self.rate_limit_sleep()
            
            # Vérification simplifiée : chercher "Couldn’t find your Google Account"
            if "Couldn’t find your Google Account" in response.text:
                self.logger.info(f"[Google] Email {email} not registered")
                return {"found": False, "data": {"url": url}}
            else:
                self.logger.info(f"[Google] Email {email} already registered")
                return {"found": True, "data": {"url": url}}
        
        except requests.exceptions.Timeout:
            self.logger.error(f"[Google] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Google] Request error: {str(e)}")
            return {"found": False, "error": str(e)}
        
        except Exception as e:
            self.logger.error(f"[Google] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
