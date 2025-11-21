# modules/site_template.py
import re

SITE = "site_template"

def _extract_text(resp, requester):
    soup = requester.soup_from_response(resp)
    return soup.get_text(" ", strip=True) if soup else ""

def check(email: str, requester):
    """
    Template module — does NOT target a real service.
    Replace base URLs, endpoints and regex patterns when implementing a real module.
    """
    try:
        base = "https://example.com"
        reset_page = f"{base}/account/password/reset"
        resp_get = requester.get(reset_page)
        text_get = _extract_text(resp_get, requester) if resp_get else ""

        reset_endpoint = f"{base}/api/password_reset"
        resp_post = requester.post(reset_endpoint, json={"email": email})
        text_post = _extract_text(resp_post, requester) if resp_post else ""

        # Example heuristics (tailor per-site)
        if re.search(r"(we have sent|check your inbox|email sent)", text_post, re.IGNORECASE):
            return {"site": SITE, "found": True, "evidence": "password_reset_email_sent_message", "raw": {"status_code": getattr(resp_post, 'status_code', None), "snippet": text_post[:300]}}
        if re.search(r"(If an account exists|we will not reveal|email not found)", text_post, re.IGNORECASE):
            return {"site": SITE, "found": None, "evidence": "ambiguous_password_reset_message", "raw": {"status_code": getattr(resp_post, 'status_code', None), "snippet": text_post[:300]}}

        # Fallback: check a profile-like URL
        profile_url = f"{base}/users/{email}"
        resp_profile = requester.get(profile_url, allow_redirects=False)
        if resp_profile:
            if resp_profile.status_code == 200:
                return {"site": SITE, "found": True, "evidence": "profile_page_200", "raw": {"profile_url": resp_profile.url}}
            if resp_profile.status_code == 404:
                return {"site": SITE, "found": False, "evidence": "profile_404", "raw": {"status_code": 404}}
            if resp_profile.status_code in (301, 302):
                return {"site": SITE, "found": None, "evidence": f"redirect_{resp_profile.status_code}", "raw": {"location": resp_profile.headers.get("Location")}}

        return {"site": SITE, "found": None, "evidence": "no_conclusion", "raw": {}}
    except Exception as e:
        return {"site": SITE, "found": None, "evidence": "exception", "raw": {"error": str(e)}}
