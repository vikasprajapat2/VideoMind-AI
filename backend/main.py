from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.youtube import extract_video_id

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