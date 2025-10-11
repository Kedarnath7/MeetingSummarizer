import google.generativeai as genai
import os
import json

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio using Gemini's file upload capability
    """
    try:
        # Upload the audio file to Gemini
        audio_file = genai.upload_file(audio_file_path)
        
        # Create a prompt for transcription
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Please transcribe the following audio file accurately. 
        Return only the raw transcript text without any additional commentary.
        Be precise and include every spoken word.
        """
        
        response = model.generate_content([prompt, audio_file])
        return response.text.strip()
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def generate_summary(transcript: str) -> dict:
    """
    Generate structured summary using Gemini Pro
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze this meeting transcript and create a structured summary.
        
        Return ONLY a valid JSON object with this exact structure:
        {{
            "summary": "concise overall summary of the meeting (2-3 paragraphs)",
            "key_decisions": ["decision1", "decision2", "decision3"],
            "action_items": [
                {{
                    "task": "specific task description",
                    "assignee": "person responsible",
                    "deadline": "timeline if mentioned"
                }}
            ]
        }}
        
        Transcript:
        {transcript}
        
        Important: 
        - Return ONLY the JSON object, no other text or markdown formatting
        - Extract real action items and decisions from the conversation
        - If no clear assignee or deadline, use "TBD"
        """
        
        response = model.generate_content(prompt)
        
        # Clean the response to extract pure JSON
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        # Parse JSON
        summary_data = json.loads(response_text.strip())
        return summary_data
        
    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            "summary": "Generated summary (formatting issue occurred)",
            "key_decisions": [],
            "action_items": []
        }
    except Exception as e:
        raise Exception(f"Summary generation failed: {str(e)}")