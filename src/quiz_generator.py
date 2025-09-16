# src/quiz_generator.py

import json
from src.database import save_quiz

class QuizGenerator:
    def __init__(self, llm):
        self.llm = llm
    
    def generate_quiz(self, topic, context, num_questions=5):
        """
        Generate a quiz on the given topic using the provided context
        """
        prompt = f"""
        Based on the following context about {topic}, generate a {num_questions}-question multiple choice quiz.
        Format your response strictly as a JSON object with the following structure, no extra comments:
        {{
            "quiz_title": "Quiz about [topic]",
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": 0  // Index of the correct option (0-3)
                }}
            ]
        }}
        
        Context:
        {context}
        """
        
        try:
            # Get response from LLM
            response = self.llm.complete(prompt)
            
            # Parse the JSON response
            # print("llm text", response)
            quiz_data = json.loads(response.text)
            # print("quiz", quiz_data)
            # Save to database
            save_quiz(topic, quiz_data)
            
            return quiz_data
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None