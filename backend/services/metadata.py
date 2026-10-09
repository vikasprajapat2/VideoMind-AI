import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()
API_URL = "https://www.googleapis.com/youtube/v3/videos"

DURATION_RE = re.compile( r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")  # its a provide a doution in iso 8601 froamte  -----eg -> PT5M30S → 5 minutes, 30 seconds ,PT1H27M10S → 1 hour, 27 minutes, 10 seconds, P1DT2H → 1 day, 2 hours

#to convert duretion in second 
def parse_duration(iso: str) -> int:
    m = DURATION_RE.match(iso or "")
    if not m:
        return 0
    d, h, mi, s = (
        int(x) if x else 0 for x in m.groups()
    )

    return d * 86400 + h * 3600 + mi * 60 + s


#multiple thumbnail sizes
