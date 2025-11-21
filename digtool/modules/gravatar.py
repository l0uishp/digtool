import hashlib
import httpx
from typing import Dict, Any
from digtool.modules.base import BaseModule


class GravatarModule(BaseModule):

    def check(self, email: str) -> Dict[str, Any]:
        self.logger.debug(f"[Gravatar] Checking {email}")

        try:
            # Nettoyage email
            email_clean = email.lower().strip()
            email_hash = hashlib.md5(email_clean.encode()).hexdigest()

            # URLs
            check_url = f"https://www.gravatar.com/{email_hash}?d=404"
            profile_url = f"https://gravatar.com/{email_hash}"
            profile_json_url = f"https://gravatar.com/{email_hash}.json"

            # Headers réalistes de Chrome + HTTP/2
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Upgrade-Insecure-Requests": "1",
            }

            # Client HTTP/2
            with httpx.Client(http2=True, headers=headers, timeout=self.timeout) as client:

                response = client.get(check_url, follow_redirects=False)

                self.logger.debug(
                    f"[Gravatar] Response status={response.status_code}, http={response.http_version}"
                )

                # 200 = avatar exists
                if response.status_code == 200:
                    self.logger.info(f"[Gravatar] Profile found for {email}")

                    # Try retrieving JSON profile
                    try:
                        profile_resp = client.get(profile_json_url, follow_redirects=True)

                        if profile_resp.status_code == 200:
                            data = profile_resp.json()
                            entry = data.get("entry", [{}])[0]

                            return {
                                "found": True,
                                "data": {
                                    "profile_url": profile_url,
                                    "avatar_url": f"https://www.gravatar.com/avatar/{email_hash}",
                                    "display_name": entry.get("displayName"),
                                    "username": entry.get("preferredUsername"),
                                    "location": entry.get("currentLocation"),
                                    "profile_background": (
                                        entry.get("profileBackground", {}).get("url")
                                    ),
                                    "accounts": [acc.get("url") for acc in entry.get("accounts", [])],
                                },
                            }

                    except Exception as e:
                        self.logger.warning(f"[Gravatar] Failed JSON parse: {str(e)}")

                    # Fallback: simple result without JSON
                    return {
                        "found": True,
                        "data": {
                            "profile_url": profile_url,
                            "avatar_url": f"https://www.gravatar.com/avatar/{email_hash}",
                            "email_hash": email_hash,
                        },
                    }

                # 404 = no avatar
                elif response.status_code == 404:
                    self.logger.debug(f"[Gravatar] No profile for {email}")
                    return {"found": False}

                else:
                    self.logger.warning(
                        f"[Gravatar] Unexpected status {response.status_code} for {email}"
                    )
                    return {"found": False, "error": f"Unexpected status: {response.status_code}"}

        except httpx.TimeoutException:
            self.logger.error(f"[Gravatar] Timeout for {email}")
            return {"found": False, "error": "Request timeout"}

        except httpx.RequestError as e:
            self.logger.error(f"[Gravatar] HTTP error: {str(e)}")
            return {"found": False, "error": str(e)}

        except Exception as e:
            self.logger.error(f"[Gravatar] Unexpected error: {str(e)}")
            return {"found": False, "error": str(e)}
