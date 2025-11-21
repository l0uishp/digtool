import hashlib
import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class GravatarModule(BaseModule):
    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Gravatar] Checking {email}")
        
        try:
            # Normaliser l'email : minuscules et supprimer espaces
            email_clean = email.lower().strip()
            email_hash = hashlib.md5(email_clean.encode()).hexdigest()
            
            # Utiliser d=404 pour obtenir un 404 si pas de Gravatar
            check_url = f"https://www.gravatar.com/{email_hash}.json"
            
            headers = {
                "Host": "gravatar.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            response = requests.get(check_url, headers=headers, timeout=self.timeout)
            
            self.rate_limit_sleep()
            
            # Code 200 = Gravatar existe
            # Code 404 = Pas de Gravatar
            if response.status_code in (200, 301, 302):
                profile_url = f"https://gravatar.com/{email_hash}"
                avatar_url = f"https://www.gravatar.com/avatar/{email_hash}"
                
                self.logger.info(f"[Gravatar] Found profile for {email}")
                
                # Essayer de récupérer plus d'infos depuis le profil JSON
                try:
                    profile_json_url = f"https://gravatar.com/{email_hash}.json"
                    profile_response = requests.get(profile_json_url, headers=headers, timeout=self.timeout)
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        entry = profile_data.get('entry', [{}])[0]
                        
                        return {
                            "found": True,
                            "data": {
                                "profile_url": profile_url,
                                "avatar_url": avatar_url,
                                "display_name": entry.get('displayName'),
                                "username": entry.get('preferredUsername'),
                                "location": entry.get('currentLocation'),
                                "profile_background": entry.get('profileBackground', {}).get('url'),
                                "accounts": [acc.get('url') for acc in entry.get('accounts', [])]
                            }
                        }
                except:
                    pass
                
                # Si pas de JSON, retourner infos basiques
                return {
                    "found": True,
                    "data": {
                        "profile_url": profile_url,
                        "avatar_url": avatar_url,
                        "email_hash": email_hash
                    }
                }
                
            elif response.status_code == 404:
                self.logger.debug(f"[Gravatar] No profile found for {email}")
                return {"found": False}
            
            else:
                self.logger.warning(f"[Gravatar] Unexpected status code {response.status_code} for {email}")
                return {"found": False, "error": f"Unexpected status: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            self.logger.error(f"[Gravatar] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Gravatar] Request error: {str(e)}")
            return {"found": False, "error": str(e)}
            
        except Exception as e:
            self.logger.error(f"[Gravatar] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
