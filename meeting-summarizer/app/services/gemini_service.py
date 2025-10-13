import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_summary(transcript: str) -> dict:

    try:
        is_fallback = "[FALLBACK]" in transcript
        
        if is_fallback:
            print("Using fallback transcript (AssemblyAI service unavailable)")
            return {
                "summary": "AssemblyAI transcription service is currently unavailable. Please check your API key and internet connection.",
                "key_decisions": ["Service temporarily unavailable"],
                "action_items": [
                    {
                        "task": "Check AssemblyAI API configuration",
                        "assignee": "System Administrator",
                        "deadline": "ASAP"
                    }
                ]
            }
        else:
            print("Using REAL transcript for summary generation")
            
        model = genai.GenerativeModel("gemini-2.5-flash") 
            
        prompt = f"""
        Analyze this meeting transcript and return ONLY a valid JSON object with this exact structure:
        {{
            "summary": "concise overall summary of the meeting",
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
        - Return ONLY the JSON object, no other text
        - Do not use markdown formatting
        - Extract real action items and decisions from the conversation
        - If no clear assignee or deadline, use "TBD"
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        response_text = response_text.replace('```json', '').replace('```', '').strip()

        summary_data = json.loads(response_text)
        print("Summary generated successfully")
        return summary_data
        
    except Exception as e:
        print(f"Summary generation error: {str(e)}")
        return {
            "summary": f"Summary generation failed: {str(e)}",
            "key_decisions": ["Processing error"],
            "action_items": []
        }