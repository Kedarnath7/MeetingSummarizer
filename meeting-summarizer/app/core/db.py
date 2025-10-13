import sqlite3
import json
from datetime import datetime

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database and create/update tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meeting_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            asr_service TEXT DEFAULT 'AssemblyAI',
            llm_service TEXT DEFAULT 'Gemini',
            transcript_length INTEGER DEFAULT 0,
            is_fallback BOOLEAN DEFAULT FALSE
        )
    ''')

    cursor.execute("PRAGMA table_info(meeting_summaries)")
    columns = [column[1] for column in cursor.fetchall()]
 
    if 'transcript_length' not in columns:
        cursor.execute('ALTER TABLE meeting_summaries ADD COLUMN transcript_length INTEGER DEFAULT 0')
    
    if 'is_fallback' not in columns:
        cursor.execute('ALTER TABLE meeting_summaries ADD COLUMN is_fallback BOOLEAN DEFAULT FALSE')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def save_meeting_summary(filename: str, transcript: str, summary: dict) -> int:
    """Save meeting summary to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_fallback = "[FALLBACK]" in transcript
    transcript_length = len(transcript)
    
    cursor.execute('''
        INSERT INTO meeting_summaries (filename, transcript, summary, asr_service, llm_service, transcript_length, is_fallback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, transcript, json.dumps(summary), 'AssemblyAI', 'Gemini', transcript_length, is_fallback))
    
    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    status = "fallback" if is_fallback else "real"
    print(f"Meeting summary saved with ID: {meeting_id} ({status} transcription)")
    return meeting_id

def get_meeting_summary(meeting_id: int):
    """Retrieve a meeting summary by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM meeting_summaries WHERE id = ?
    ''', (meeting_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return dict(result)
    return None

# def get_all_meetings(limit: int = 10):
#     """Get all meeting summaries with service status"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute('''
#         SELECT id, filename, created_at, asr_service, llm_service, transcript_length, is_fallback
#         FROM meeting_summaries 
#         ORDER BY created_at DESC 
#         LIMIT ?
#     ''', (limit,))
    
#     results = cursor.fetchall()
#     conn.close()
    
#     return [dict(result) for result in results]

# def get_service_stats():
#     """Get statistics about ASR service usage"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute('''
#         SELECT 
#             COUNT(*) as total_meetings,
#             SUM(CASE WHEN is_fallback = 1 THEN 1 ELSE 0 END) as fallback_count,
#             SUM(CASE WHEN is_fallback = 0 THEN 1 ELSE 0 END) as real_transcription_count,
#             AVG(transcript_length) as avg_transcript_length
#         FROM meeting_summaries
#     ''')
    
#     result = cursor.fetchone()
#     conn.close()
    
#     return dict(result) if result else None