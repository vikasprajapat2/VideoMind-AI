import re
from urllib.parse import urlparse, parse_qs  # urlparse() its diveded url in different parts   and  paes_qs() its convert query parameters in dictionary

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
SHORT_HOST = "youtu.be"

class InvalidYouTubeURL(ValueError):
    pass
def extract_video_id(url: str) -> str:
    url =(url or "").strip()
    if not url:
        raise InvalidYouTubeURL("URL is Empty")
    if not re.match(r"https?://", url,re.IGNORECASE):
        url = "https://" + url

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    candidate = ""

    if host == SHORT_HOST:
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif host in YOUTUBE_HOSTS:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/shorts/"):
            candidate = parsed.path[len("/shorts/"):].split("/")[0]
        else:
            raise InvalidYouTubeURL("your Youtube link formate not suported ")

    else:
        raise InvalidYouTubeURL("its not a you tube url")

    if not VIDEO_ID_RE.match(candidate):
        raise InvalidYouTubeURL("Vedio id is worng ")
    return candidate