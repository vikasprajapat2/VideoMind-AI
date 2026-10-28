from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.youtube import extract_video_id, InvalidYouTubeURL
from services.metadata import fatch_vidio_metadata, MetadataError, VideoNotFound
from services.transcript import fetch_transcript, TranscriptFetchError, TranscriptNotAvailable
from services.cleaner import clean_transcript

app = FastAPI(title='VideoMind AI')

class VideoRequest(BaseModel):
    url: str


@app.get("/health")
async def root():
    return {
        "status": "ok"
    } 

@app.post("/extract-id")
async def extract_id(req: VideoRequest):
    try:
        video_id = extract_video_id(req.url)
    except InvalidYouTubeURL as e:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return {"video_id": video_id}

@app.post("/vidio-info")
async def video_info(req: VideoRequest):
    try: 
        video_id = extract_video_id(req.url)
        return await fatch_vidio_metadata(video_id)
    except InvalidYouTubeURL as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VideoNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MetadataError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/transcript")
async def transcript(req: VideoRequest):
    try:
        video_id = extract_video_id(req.url)
        return await fetch_transcript(video_id)
    except InvalidYouTubeURL as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TranscriptNotAvailable as e:
        raise HTTPException(status_code = 404, detail= str(e))
    except TranscriptFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/transcript/clean")
async def transcript_clean(req: VideoRequest):
    try:
        video_id = extract_video_id(req.url)
        raw = await fetch_transcript(video_id)
        return clean_transcript(raw)
    except InvalidYouTubeURL as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TranscriptNotAvailable as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TranscriptFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))