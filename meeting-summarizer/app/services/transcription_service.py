import assemblyai as aai
import os
import time
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_file_path: str) -> str:

    print(f"Starting AssemblyAI transcription for: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        error_msg = f"Audio file not found: {audio_file_path}"
        print(f"{error_msg}")
        raise Exception(error_msg)

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        error_msg = "AssemblyAI API key not configured"
        print(f"{error_msg}")
        raise Exception(error_msg)
    
    aai.settings.api_key = api_key
    
    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_detection=True,
            punctuate=True,
            format_text=True
        )

        transcriber = aai.Transcriber()
        
        print("Uploading to AssemblyAI...")
        start_time = time.time()
        
        transcript = transcriber.transcribe(audio_file_path, config=config)
        
        print(f"Transcription started. Status: {transcript.status}")
    
        poll_count = 0
        max_polls = 60 
        
        while transcript.status == 'processing' and poll_count < max_polls:
            poll_count += 1
            elapsed = time.time() - start_time
            print(f"Processing... {elapsed:.1f}s elapsed")
            
            transcript = transcriber.get_transcript(transcript.id)
            time.sleep(5)

        if transcript.status == aai.TranscriptStatus.error:
            error_msg = f"AssemblyAI Error: {transcript.error}"
            print(f"{error_msg}")
            raise Exception(error_msg)
        
        elif transcript.status == aai.TranscriptStatus.completed:
            actual_transcript = transcript.text
            elapsed = time.time() - start_time
            
            print(f"Transcription completed in {elapsed:.1f}s!")
            print(f"Transcript length: {len(actual_transcript)} characters")
            
            if transcript.utterances:
                print(f"Speakers detected: {len(transcript.utterances)}")
            
            return actual_transcript.strip()
        
        elif poll_count >= max_polls:
            error_msg = "AssemblyAI timeout - processing took too long"
            print(f"{error_msg}")
            raise Exception(error_msg)
        
        else:
            error_msg = f"Unexpected AssemblyAI status: {transcript.status}"
            print(f"{error_msg}")
            raise Exception(error_msg)
        
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        print("Falling back to sample transcript...")
        return get_sample_transcript()

def get_sample_transcript():
    """Fallback sample transcript when ASR fails"""
    return "[FALLBACK] This is a sample transcript. AssemblyAI transcription failed. Please check the logs for details."