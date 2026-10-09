import re
from urllib.parse import urlparse, parse_qs  # urlparse() its diveded url in different parts   and  paes_qs() its convert query parameters in dictionary

ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}

def get_youtube_id(url: str) -> str | None:
    parsed = urlparse(url.strip())
    if parsed.netloc.lower() not in HOSTS:
        return None

    if parsed.netloc.lower() == "youtu.be":
        candidate = parsed.path.lstrip("/")
    elif parsed.path =="/watch":
        candidate=parse_qs(parsed.query).get('v',[""])[0]
    else: 
        parts = parsed.path.strip("/").split("/")
        candidate = parts[1] if len(parts) == 2 and parts[0] in ("embed", "shorts", "live") else ""

    return candidate if ID_RE.match(candidate) else None
