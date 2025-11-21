# modules/gravatar.py
import hashlib
from urllib.parse import urlencode

def normalize_email(email: str) -> str:
    return email.strip().lower()

def check(email: str, requester):
    site = "gravatar"
    e = normalize_email(email)
    h = hashlib.md5(e.encode("utf-8")).hexdigest()
    params = {"d": "404", "s": "80"}
    url = f"https://www.gravatar.com/avatar/{h}?{urlencode(params)}"
    resp = requester.get(url)

    if resp is None:
        return {"site": site, "found": False, "evidence": "no-response", "raw": {}}

    ct = resp.headers.get("Content-Type", "")
    if resp.status_code == 200 and ct.startswith("image/"):
        return {"site": site, "found": True, "evidence": "avatar_found", "raw": {"url": resp.url, "content_type": ct}}
    if resp.status_code == 404:
        return {"site": site, "found": False, "evidence": "avatar_not_found", "raw": {"status_code": 404}}
    return {"site": site, "found": None, "evidence": f"unexpected_status_{resp.status_code}", "raw": {"status_code": resp.status_code, "content_type": ct}}
