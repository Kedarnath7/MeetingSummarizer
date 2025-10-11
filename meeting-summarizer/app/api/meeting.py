from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ai_service import transcribe_audio, generate_summary
from app.core.database import save_meeting_summary, init_database
from app.models import MeetingResponse
import uuid
import os
import json

router = APIRouter()

# Initialize database when module loads
init_database()

@router.post("/summarize", response_model=MeetingResponse)
async def summarize_meeting(audio: UploadFile = File(...)):
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    file_extension = os.path.splitext(audio.filename.lower())[1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Use: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    file_path = f"/tmp/{uuid.uuid4()}_{audio.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Step 1: Transcribe audio using Gemini
        print("Starting transcription...")
        transcript = transcribe_audio(file_path)
        
        # Step 2: Generate summary using Gemini
        print("Generating summary...")
        summary_data = generate_summary(transcript)
        
        # Step 3: Save to database
        print("Saving to database...")
        meeting_id = save_meeting_summary(audio.filename, transcript, summary_data)
        
        # Step 4: Return response
        return MeetingResponse(
            id=meeting_id,
            filename=audio.filename,
            message="Meeting summarized successfully!",
            summary=summary_data,
            transcript_preview=transcript[:200] + "..." if len(transcript) > 200 else transcript
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)