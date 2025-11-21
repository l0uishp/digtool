import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class AdobeModule(BaseModule):
    """
    Module DigTool pour vérifier si un email est enregistré sur Adobe.
    """

    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Adobe] Checking {email}")

        url = "https://auth.services.adobe.com/signin/v2/users/accounts"
        headers = {
            "Host" : "auth.services.adobe.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "X-Ims-Clientid": "SunbreakWebUI1",
            "Content-Type": "application/json",
            "Origin": "https://auth.services.adobe.com"
        }

        payload = {
            "username": email,
            "usernameType": "EMAIL"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            self.rate_limit_sleep()

            # --- LOGIQUE BASÉE SUR LA RÉPONSE JSON ---
            try:
                data = response.json()
            except ValueError:
                self.logger.error(f"[Adobe] Invalid JSON response for {email}")
                return {"found": False, "error": "Invalid JSON"}

            if isinstance(data, list) and len(data) == 0:
                self.logger.info(f"[Adobe] Email {email} NOT registered")
                return {"found": False}

            elif isinstance(data, list) and len(data) > 0:
                self.logger.info(f"[Adobe] Email {email} EXISTS")
                profile_data = data[0]
                return {
                    "found": True,
                    "data": {
                        "type": profile_data.get("type"),
                        "status": profile_data.get("status"),
                        "images": profile_data.get("images"),
                        "hasT2ELinked": profile_data.get("hasT2ELinked", False)
                    }
                }

            else:
                self.logger.warning(f"[Adobe] Unexpected response format for {email}")
                return {"found": False, "error": "Unexpected response format"}

        except requests.exceptions.Timeout:
            self.logger.error(f"[Adobe] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Adobe] Request error: {str(e)}")
            return {"found": False, "error": str(e)}

        except Exception as e:
            self.logger.error(f"[Adobe] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
