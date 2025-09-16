# src/database.py

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def init_db():
    """Initialize the SQLite database for storing quizzes"""
    db_path = Path("./storage/quizzes.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create quizzes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        questions TEXT NOT NULL,  -- JSON string of questions
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def save_quiz(topic, questions):
    """Save a quiz to the database"""
    db_path = init_db()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO quizzes (topic, questions) VALUES (?, ?)",
        (topic, json.dumps(questions))
    )
    
    conn.commit()
    conn.close()

def get_quizzes(limit=10):
    """Retrieve quizzes from the database"""
    db_path = init_db()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM quizzes ORDER BY created_at DESC LIMIT ?", (limit,))
    quizzes = cursor.fetchall()
    
    conn.close()
    
    # Convert JSON strings back to objects
    result = []
    for quiz in quizzes:
        quiz_id, topic, questions_json, created_at = quiz
        result.append({
            'id': quiz_id,
            'topic': topic,
            'questions': json.loads(questions_json),
            'created_at': created_at
        })
    
    return result

# Initialize the database when this module is imported
init_db()