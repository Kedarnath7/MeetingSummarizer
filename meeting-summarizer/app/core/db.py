import sqlite3
import json
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_database():
    """Initialize the database and create tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meeting_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def save_meeting_summary(filename: str, transcript: str, summary: dict) -> int:
    """Save meeting summary to database and return the ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO meeting_summaries (filename, transcript, summary)
        VALUES (?, ?, ?)
    ''', (filename, transcript, json.dumps(summary)))
    
    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
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