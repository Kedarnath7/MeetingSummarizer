from app.services.transcription_service import transcribe_audio
from app.services.gemini_service import generate_summary

def process_audio_and_generate_summary(audio_file_path: str) -> dict:

    try:
        transcript = transcribe_audio(audio_file_path)
        
        summary_data = generate_summary(transcript)
        
        return {
            "transcript": transcript,
            "summary": summary_data,
            "success": True
        }
        
    except Exception as e:
        print(f"Error in audio processing pipeline: {str(e)}")
        return {
            "transcript": "",
            "summary": {
                "summary": f"Processing failed: {str(e)}",
                "key_decisions": ["Processing error"],
                "action_items": []
            },
            "success": False
        }