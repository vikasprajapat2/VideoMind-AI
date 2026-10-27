import asyncio 
import  tempfile 
from pathlib import Path
import yt_dlp
from faster_whisper import WhisperModel

WHISPER_MODEL_SIZE = "base"
MAX_AUDIO_SECONDS = 3600  # moder than 1 hour video fallback off

__model = None

class WhisperError(Exception):
    pass

def _get_model() -> WhisperModel:
    global __model 
    if __model is None:
        __model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type = "int8")
    return __model

def _download_audio(video_id: str, out_dir: str) -> Path:
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(out_dir) / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
    }
    try : 
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if (info.get('duration') or 0) >  MAX_AUDIO_SECONDS:
                raise WhisperError(
                    f'very long vidio (limit {MAX_AUDIO_SECONDS // 60} minute)'
                )
            ydl.download([url])
    except yt_dlp.utils.downloadError as e:
        raise WhisperError(f'Audio Download failed : {str(e)[:150]}')

    files = list(Path(out_dir).glob(f'{video_id}.*'))
    if not files:
        raise WhisperError('Audio file not found')
    return files[0]

def _trancribe_sync(video_id: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:   # after work audio auto delete
        audio_path = _download_audio(video_id, tmp)
        try:
            segments, info = _get_model().transcribe(
                str(audio_path), vad_filter=True  # slience place skip
            )
            result = [
                {
                    'start': round(seg.start, 2),
                    'duration': round(seg.end - seg.start, 2),
                    'text': seg.text.strip(),
                }
                for seg in segments
                if seg.text.strip()
            ]

        except Exception as e :
            raise WhisperError(f"Whisper transcription full: {type(e).__name__}")

    if not result:
        raise WhisperError('dosent have audio text')
    return {
        "video_id": video_id,
        "language": info.language,
        "is_generated": True,
        "source": "whisper",
        "segments": result,
    }
async def transcribe_with_whisper(video_id: str) -> dict:
    return await asyncio.to_thread(_trancribe_sync, video_id)











