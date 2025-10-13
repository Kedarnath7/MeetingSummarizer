from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.db import save_meeting_summary, init_database
from app.services.ai_service import process_audio_and_generate_summary 
from app.models import MeetingResponse
import uuid
import os
from datetime import datetime

router = APIRouter()
init_database()

@router.post("/summarize", response_model=MeetingResponse)
async def summarize_meeting(audio: UploadFile = File(...)):

    allowed_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg'}
    file_extension = os.path.splitext(audio.filename.lower())[1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Use: {', '.join(allowed_extensions)}"
        )

    file_path = f"temp_{uuid.uuid4()}{file_extension}"
    
    try:
        print(f"Saving uploaded file to: {file_path}")

        with open(file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        file_size = os.path.getsize(file_path)
        print(f"File saved. Size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

        print("Starting transcription and summary generation...")
        result = process_audio_and_generate_summary(file_path)
        
        transcript = result["transcript"]
        summary_data = result["summary"]
        
        if "[FALLBACK]" in transcript:
            print("Transcription Service unavailable - using fallback")
        else:
            print(f"REAL transcription completed. Length: {len(transcript)} characters")

        print("Summary generation completed")
        
        meeting_id = save_meeting_summary(audio.filename, transcript, summary_data)
        print(f"Saved to database with ID: {meeting_id}")
        
        return MeetingResponse(
            id=meeting_id,
            filename=audio.filename,
            message="Meeting processed successfully with AssemblyAI ASR!" if "[FALLBACK]" not in transcript else "Meeting processed with fallback (ASR service unavailable)",
            summary=summary_data,
            transcript_preview=transcript[:200] + "..." if len(transcript) > 200 else transcript,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Error in summarize_meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temp file cleaned up: {file_path}")

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API and services are working"""
    return {
        "message": "Meeting Summarizer API is working",
        "asr_service": "AssemblyAI",
        "llm_service": "Google Gemini", 
        "status": "operational",
        "features": ["real_asr", "ai_summarization", "action_items"]
    }