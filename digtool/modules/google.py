import requests
from digtool.modules.base import BaseModule
from typing import Dict, Any

class GoogleModule(BaseModule):
    """
    Module DigTool pour vérifier si un email est enregistré sur Google
    basé sur le code HTTP 200.
    """

    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Google] Checking {email}")

        url = "https://accounts.google.com/v3/signin/_/AccountsSignInUi/data/batchexecute"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://accounts.google.com",
            "Referer": "https://accounts.google.com/signin/v2/identifier",
        }

        try:
            response = requests.post(url, headers=headers, timeout=self.timeout)
            self.rate_limit_sleep()

            if response.status_code == 200:
                self.logger.info(f"[Google] Email {email} EXISTS")
                return {"found": True}
            else:
                self.logger.info(f"[Google] Email {email} NOT registered (status {response.status_code})")
                return {"found": False}

        except requests.exceptions.Timeout:
            self.logger.error(f"[Google] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"[Google] Request error: {str(e)}")
            return {"found": False, "error": str(e)}

        except Exception as e:
            self.logger.error(f"[Google] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
