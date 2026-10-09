from fastapi import FastAPI

app = FastAPI(title='VideoMind AI')


@app.get("/Helth")
async def root():
    return {
        "status": "ok"
    }