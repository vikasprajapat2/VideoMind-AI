import asyncio
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    IpBlocked,
    RequestBlocked,
    AgeRestricted,
    YouTubeTranscriptApiException,
)

from services.whisper_fallback import transcribe_with_whisper, WhisperError 

PREFERRED_LANGUAGES = ("en",'hi')

class TranscriptNotAvailable(Exception):
    pass

class TranscriptFetchError(Exception):
    pass

# now we convert second in time 
def format_timestemp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f"{m:02d}:{s:02d}"

def _pick_transcript(transcript_list):
    try: 
        return transcript_list.find_transcript(PREFERRED_LANGUAGES)
    except NoTranscriptFound:
        for t in transcript_list:
            return t
    raise TranscriptNotAvailable("this video transcript vidio not avalable ")

def _fetch_sync(video_id: str) -> dict:
    api = YouTubeTranscriptApi()
    try:
        chosen = _pick_transcript(api.list(video_id))
        fetched = chosen.fetch()
    except TranscriptsDisabled:
        raise TranscriptNotAvailable('transcript/captions disabled this video ')
    except VideoUnavailable:
        raise TranscriptNotAvailable("vidio not avalable (private or delete)")
    except AgeRestricted:
        raise TranscriptFetchError("Age- restricted video ")
    except (IpBlocked, RequestBlocked):
        raise TranscriptFetchError("youtube blocked ip request")
    except YouTubeTranscriptApiException as e:
        raise TranscriptFetchError(f"Transcript fetch fail hua: {type(e).__name__}")

    segments = [
        {'start': round(s.start, 2), 
         "duration": round(s.duration, 2), 
         "text": s.text} for s in fetched
    ]
    return {
        "video_id": video_id,
        "language": chosen.language_code,
        'is_generated': chosen.is_generated,
        'source': 'youtube',
        "segments": segments,
    }

async def fetch_transcript(video_id: str) -> dict:
    try:
        return await asyncio.to_thread(_fetch_sync, video_id)
    except TranscriptNotAvailable:
        pass

    try:
        return await transcribe_with_whisper(video_id)
    except WhisperError as e:
        raise TranscriptFetchError(str(e))
