import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()


API_URL = "https://www.googleapis.com/youtube/v3/videos"
DURATION_RE = re.compile( r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")  # its a provide a doution in iso 8601 froamte  -----eg -> PT5M30S → 5 minutes, 30 seconds ,PT1H27M10S → 1 hour, 27 minutes, 10 seconds, P1DT2H → 1 day, 2 hours
THUMB_ORDER = ('maxres', 'standard','high', 'medium', 'default')


class MetadataError(Exception):
    pass
class VideoNotFound(Exception):
    pass

#to convert duretion in second 
def parse_duration(iso: str) -> int:
    m = DURATION_RE.match(iso or "")
    if not m:
        return 0
    d, h, mi, s = (
        int(x)
        if x else 0 for x in m.groups()
    )

    return d * 86400 + h * 3600 + mi * 60 + s


#multiple thumbnail sizes
def best_thumbnail(thumbnails:dict) -> str:
    for key in THUMB_ORDER:
        if key in thumbnails:
            return thumbnails[key]['url']

    return ""

async def fatch_vidio_metadata(video_id: str) -> dict:
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise MetadataError("youtube api key not found in .env")
     
    params = {"part": "snippet,contentDetails", "id": video_id, "key": api_key}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(API_URL, params=params)

    if resp.status_code != 200:
        raise MetadataError(f"YouTube API error ({resp.status_code}): check a key tokens ")

    items = resp.json().get("items", [])
    if not items:
        raise VideoNotFound("vidio dosent found ")

    item = items[0]
    snippet = item["snippet"]
    return {
        "video_id": video_id,
        "title": snippet["title"],
        "channel": snippet["channelTitle"],
        "duration": parse_duration(item["contentDetails"]["duration"]),
        "thumbnail": best_thumbnail(snippet.get("thumbnails", {})),
        "description": snippet.get("description", ""),
    }