import streamlit as st
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="https://www.google.com/favicon.ico",
    layout="wide"
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
        color: white;
    }
    .stButton>button {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
    }
    .summary-box {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #2d2d2d;
        border-left: 4px solid #667eea;
    }
    .ai-message {
        background-color: #3d3d3d;
        border-left: 4px solid #764ba2;
    }
</style>
""", unsafe_allow_html=True)

st.title("Meeting Summarizer")
st.markdown("Upload meeting audio to get AI-powered summary, decisions, and action items")

API_BASE = "http://127.0.0.1:8000"

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'meeting_data' not in st.session_state:
    st.session_state.meeting_data = None
if 'chat_context' not in st.session_state:
    st.session_state.chat_context = "general" 

st.header("Upload Meeting Audio")
audio_file = st.file_uploader(
    "Choose an audio file",
    type=['mp3', 'wav'],
    help="Supported formats: MP3, WAV."
)

if audio_file is not None and st.session_state.meeting_data is None:
    st.write(f"**File:** {audio_file.name}")
    st.write(f"**Size:** {audio_file.size / 1024 / 1024:.2f} MB")

    if st.button("Process Meeting"):
        with st.spinner("Processing your meeting... This may take a few minutes."):
            try:
                files = {'audio': (audio_file.name, audio_file, audio_file.type)}
                
                response = requests.post(
                    f"{API_BASE}/meeting/summarize",
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.meeting_data = result
                    st.session_state.chat_context = "meeting_specific"

                    st.session_state.messages.append({
                        "role": "ai", 
                        "content": "I've analyzed your meeting! Here's the summary and you can ask me questions about it."
                    })
                    
                    st.success("Meeting processed successfully!")
                    st.rerun()
                    
                else:
                    st.error(f"Error processing meeting: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure your FastAPI server is running on http://127.0.0.1:8000")

if st.session_state.meeting_data:
    result = st.session_state.meeting_data
    
    st.header("Meeting Analysis")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Summary")
        st.markdown(f'<div class="summary-box">{result["summary"]["summary"]}</div>', unsafe_allow_html=True)

        st.subheader("Key Decisions")
        decisions = result["summary"]["key_decisions"]
        if decisions:
            for i, decision in enumerate(decisions, 1):
                st.write(f"{i}. {decision}")
        else:
            st.info("No key decisions identified")
    
    with col2:
        st.subheader("Action Items")
        action_items = result["summary"]["action_items"]
        if action_items:
            for i, item in enumerate(action_items, 1):
                with st.container():
                    st.write(f"**{i}. {item['task']}**")
                    if item.get('assignee'):
                        st.write(f"👤 **Assignee:** {item['assignee']}")
                    if item.get('deadline'):
                        st.write(f"**Deadline:** {item['deadline']}")
                    st.markdown("---")
        else:
            st.info("No action items identified")

st.header("Chat with Meeting AI")

if st.session_state.meeting_data:
    st.write("Ask questions about your meeting content, decisions, or action items")
else:
    st.write("Ask general questions about meeting summarization. To analyze a meeting, upload an audio file above.")

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message ai-message"><strong>AI:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Type your question...", 
            key="chat_input", 
            label_visibility="collapsed",
            placeholder="Type your message here and press Enter or click Send..."
        )
    with col2:
        send_button = st.form_submit_button("Send", use_container_width=True)

if send_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Thinking..."):
        try:
            if st.session_state.meeting_data and st.session_state.chat_context == "meeting_specific":
            
                result = st.session_state.meeting_data
                meeting_context = f"""
                Meeting Summary: {result['summary']['summary']}
                
                Key Decisions: {', '.join(result['summary']['key_decisions'])}
                
                Action Items: {', '.join([item['task'] for item in result['summary']['action_items']])}
                
                Transcript Preview: {result['transcript_preview']}
                
                User Question: {user_input}
                """
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(f"""
                Based on this meeting context, answer the user's question accurately and helpfully:
                
                {meeting_context}
                
                Answer the question based only on the meeting information provided. If you don't have enough information from the meeting context, say so.
                """)
            else:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(f"""
                You are a helpful AI assistant for a meeting summarization application. 
                The user is asking: {user_input}
                
                Provide a helpful response about meeting summarization, audio processing, 
                or general questions about the application. 
                
                If the user wants to analyze a meeting, guide them to use the file uploader at the top of the page.
                """)
            
            ai_response = response.text
            st.session_state.messages.append({"role": "ai", "content": ai_response})
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.messages.append({"role": "ai", "content": error_msg})
    
    st.rerun()

if st.session_state.meeting_data and st.button("Analyze New Meeting"):
    st.session_state.meeting_data = None
    st.session_state.chat_context = "general"
    st.rerun()

with st.sidebar:
    st.header("About")
    st.write("This app uses:")
    st.write("• **AssemblyAI** for speech-to-text")
    st.write("• **Google Gemini** for summarization & chat")
    st.write("• **FastAPI** backend for processing")
    
    st.header("API Status")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            st.success("Backend connected")
        else:
            st.error("Backend error")
    except:
        st.error("Backend unavailable")