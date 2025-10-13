from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.meeting import router as meeting_router
#from app.core.db import get_all_meetings, get_service_stats
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="Meeting Summarizer API",
    description="AI-powered meeting transcription using AssemblyAI ASR and summarization using Google Gemini",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default port
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meeting_router, prefix="/meeting", tags=["meeting"])

@app.get("/")
async def root():
    return {
        "message": "Meeting Summarizer API with REAL AssemblyAI ASR Integration", 
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "summarize": "POST /meeting/summarize",
            "test": "GET /meeting/test", 
            "health": "GET /health",
            "meetings": "GET /meetings",
            "stats": "GET /stats"
        },
        "features": {
            "asr": "AssemblyAI API (Real Transcription)",
            "llm": "Google Gemini",
            "database": "SQLite",
            "supported_formats": ["MP3", "WAV", "M4A", "OGG", "FLAC"]
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    asr_configured = bool(os.getenv("ASSEMBLYAI_API_KEY")) and os.getenv("ASSEMBLYAI_API_KEY") != "your_assemblyai_api_key_here"
    llm_configured = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    
    return {
        "status": "healthy", 
        "service": "meeting-summarizer",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "asr": {
                "provider": "AssemblyAI",
                "configured": asr_configured,
                "status": "ready" if asr_configured else "missing_api_key"
            },
            "llm": {
                "provider": "Google Gemini", 
                "configured": llm_configured,
                "status": "ready" if llm_configured else "missing_api_key"
            }
        }
    }

# @app.get("/meetings")
# async def list_meetings(limit: int = 10):
#     """Get list of recent meeting summaries with service info"""
#     meetings = get_all_meetings(limit)
#     return {
#         "meetings": meetings,
#         "total": len(meetings)
#     }

# @app.get("/stats")
# async def service_stats():
#     """Get service usage statistics"""
#     stats = get_service_stats()
#     return {
#         "statistics": stats,
#         "timestamp": datetime.now().isoformat()
#     }

@app.get("/info")
async def api_info():
    """Get detailed API information"""
    return {
        "name": "Meeting Summarizer",
        "version": "2.0.0", 
        "asr_service": {
            "provider": "AssemblyAI",
            "status": "active",
            "features": ["real-time transcription", "speaker diarization", "multiple languages"],
            "tested": "Working (verified with local MP3)"
        },
        "llm_service": {
            "provider": "Google Gemini",
            "model": "gemini-2.5-flash", 
            "features": ["structured output", "action item extraction", "decision tracking"]
        },
        "database": "SQLite with service tracking",
        "author": "Your Name"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Meeting Summarizer with ASR...")
    uvicorn.run(app, host="127.0.0.1", port=8000)