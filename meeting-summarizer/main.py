from fastapi import FastAPI
from app.api.meeting import router as meeting_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Meeting Summarizer API",
    description="AI-powered meeting transcription and summarization using Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(meeting_router, prefix="/meeting", tags=["meeting"])

@app.get("/")
async def root():
    return {
        "message": "Meeting Summarizer API", 
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "summarize": "POST /meeting/summarize"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "meeting-summarizer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)