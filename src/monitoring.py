# src/monitoring.py

import wandb
import pandas as pd
from datetime import datetime

class Monitor:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.run = None
        
        if enabled:
            try:
                wandb.login()
                self.run = wandb.init(
                    project="academic-tutor-assistant",
                    config={
                        "model": "llama-3.3-70b-versatile",
                        "vector_db": "ChromaDB",
                        "start_time": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                print(f"Failed to initialize W&B: {e}")
                self.enabled = False
    
    def log_query(self, query, response, videos=None, retrieval_score=0):
        if not self.enabled or not self.run:
            return
            
        log_data = {
            "query": query,
            "response": response[:500],  # Limit length
            "retrieval_score": retrieval_score,
            "timestamp": datetime.now().isoformat()
        }
        
        if videos:
            log_data["num_videos"] = len(videos)
            log_data["video_titles"] = [v["title"] for v in videos]
        
        self.run.log(log_data)
    
    def log_quiz(self, topic, num_questions, score=None):
        if not self.enabled or not self.run:
            return
            
        log_data = {
            "quiz_topic": topic,
            "quiz_questions": num_questions,
            "timestamp": datetime.now().isoformat()
        }
        
        if score is not None:
            log_data["quiz_score"] = score
        
        self.run.log(log_data)
    
    def log_feedback(self, query, helpful):
        if not self.enabled or not self.run:
            return
            
        self.run.log({
            "feedback_query": query,
            "feedback_helpful": helpful,
            "feedback_timestamp": datetime.now().isoformat()
        })
    
    def finish(self):
        if self.enabled and self.run:
            self.run.finish()