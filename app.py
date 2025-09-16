# app.py

import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


print("project file", project_root)
# Import our enhanced query engine
from src.query_engine import EnhancedQueryEngine

# Initialize the application
st.set_page_config(
    page_title="Academic Tutor Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'engine' not in st.session_state:
    try:
        st.session_state.engine = EnhancedQueryEngine()
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"Failed to initialize query engine: {e}")
        st.session_state.initialized = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'feedback' not in st.session_state:
    st.session_state.feedback = []

# Initialize W&B (optional - only if configured)
try:
    import wandb
    if 'wandb_run' not in st.session_state:
        wandb.login()
        st.session_state.wandb_run = wandb.init(
            project="academic-tutor-assistant",
            config={
                "model": "llama-3.3-70b-versatile",
                "vector_db": "ChromaDB"
            }
        )
except Exception as e:
    st.session_state.wandb_run = None
    print(f"W&B not configured: {e}")

# App title and description
st.title("📚 Academic Tutor Assistant")
st.markdown("""
Welcome to your AI-powered academic tutor! Ask questions about your course materials, 
get explanations, and even generate quizzes to test your understanding.
""")

# Sidebar for additional features
with st.sidebar:
    st.header("Features")
    
    # Quiz generation
    st.subheader("Generate Quiz")
    quiz_topic = st.text_input("Enter a topic for quiz generation")
    if st.button("Generate Quiz", disabled=not st.session_state.initialized):
        if quiz_topic:
            with st.spinner("Generating quiz..."):
                quiz = st.session_state.engine.generate_quiz(quiz_topic)
                if quiz:
                    st.session_state.current_quiz = quiz
                    st.success(f"Generated quiz: {quiz['quiz_title']}")
                    
                    # Log to W&B
                    if st.session_state.wandb_run:
                        st.session_state.wandb_run.log({
                            "quiz_generated": True,
                            "quiz_topic": quiz_topic,
                            "num_questions": len(quiz["questions"])
                        })
    
    # View saved quizzes
    st.subheader("Saved Quizzes")
    if st.button("View Saved Quizzes", disabled=not st.session_state.initialized):
        quizzes = st.session_state.engine.get_saved_quizzes()
        st.session_state.saved_quizzes = quizzes
    
    # Display saved quizzes if available
    if 'saved_quizzes' in st.session_state:
        for quiz in st.session_state.saved_quizzes:
            with st.expander(quiz['topic']):
                st.write(f"Created: {quiz['created_at']}")
                if st.button(f"Load Quiz", key=f"load_{quiz['id']}"):
                    st.session_state.current_quiz = {
                        "quiz_title": quiz['topic'],
                        "questions": quiz['questions']
                    }

# Main chat interface
st.header("Chat with Your Tutor")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display YouTube videos if available
        if message.get("videos"):
            st.subheader("Recommended Videos")
            for video in message["videos"]:
                st.markdown(f"[{video['title']} - {video['channel']}]({video['url']})")

# Chat input
if prompt := st.chat_input("Ask a question about your course materials..."):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Get answer with YouTube recommendations
                result = st.session_state.engine.query(prompt, get_videos=True)
                
                # Display answer
                st.markdown(result["answer"])
                
                # Display YouTube videos if available
                if result["videos"]:
                    st.subheader("Recommended Videos")
                    for video in result["videos"]:
                        st.markdown(f"[{video['title']} - {video['channel']}]({video['url']})")
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": result["answer"],
                    "videos": result["videos"]
                })
                
                # Log to W&B
                if st.session_state.wandb_run:
                    st.session_state.wandb_run.log({
                        "query": prompt,
                        "response": result["answer"],
                        "has_videos": len(result["videos"]) > 0,
                        "num_videos": len(result["videos"]),
                        "retrieval_score": max([node.score for node in result["source_nodes"]]) if result["source_nodes"] else 0
                    })
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
    
    # Feedback mechanism
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Helpful", key=f"helpful_{len(st.session_state.chat_history)}"):
            st.session_state.feedback.append({
                "query": prompt,
                "response": result["answer"],
                "helpful": True,
                "timestamp": pd.Timestamp.now()
            })
            st.success("Thanks for your feedback!")
            
            # Log feedback to W&B
            if st.session_state.wandb_run:
                st.session_state.wandb_run.log({
                    "feedback_helpful": True,
                    "feedback_query": prompt
                })
    
    with col2:
        if st.button("👎 Not Helpful", key=f"not_helpful_{len(st.session_state.chat_history)}"):
            st.session_state.feedback.append({
                "query": prompt,
                "response": result["answer"],
                "helpful": False,
                "timestamp": pd.Timestamp.now()
            })
            st.info("Thanks for your feedback. We'll improve!")
            
            # Log feedback to W&B
            if st.session_state.wandb_run:
                st.session_state.wandb_run.log({
                    "feedback_helpful": False,
                    "feedback_query": prompt
                })

# Quiz display and interaction
if 'current_quiz' in st.session_state:
    st.header("📝 Generated Quiz")
    quiz = st.session_state.current_quiz
    st.subheader(quiz["quiz_title"])
    
    user_answers = []
    for i, question in enumerate(quiz["questions"]):
        st.markdown(f"**{i+1}. {question['question']}**")
        answer = st.radio(
            "Select your answer:",
            question["options"],
            key=f"quiz_{i}",
            index=None
        )
        user_answers.append({
            "question": question["question"],
            "user_answer": answer,
            "correct_answer": question["options"][question["correct_answer"]],
            "is_correct": answer == question["options"][question["correct_answer"]] if answer else None
        })
    
    if st.button("Submit Quiz"):
        score = sum(1 for ans in user_answers if ans["is_correct"])
        total = len(user_answers)
        
        st.success(f"Your score: {score}/{total} ({score/total*100:.1f}%)")
        
        # Display correct answers
        for i, ans in enumerate(user_answers):
            with st.expander(f"Question {i+1}"):
                st.write(f"Your answer: {ans['user_answer'] or 'Not answered'}")
                st.write(f"Correct answer: {ans['correct_answer']}")
                if ans["is_correct"]:
                    st.success("✅ Correct!")
                elif ans["user_answer"]:
                    st.error("❌ Incorrect")
        
        # Log quiz results to W&B
        if st.session_state.wandb_run:
            st.session_state.wandb_run.log({
                "quiz_taken": True,
                "quiz_title": quiz["quiz_title"],
                "quiz_score": score,
                "quiz_total": total,
                "quiz_percentage": score/total*100
            })

# Monitoring dashboard (only show if W&B is configured)
if st.session_state.wandb_run:
    st.sidebar.header("Monitoring Dashboard")
    st.sidebar.markdown(f"""
    **W&B Run:** [{st.session_state.wandb_run.name}]({st.session_state.wandb_run.url})
    """)
    
    # Display basic stats
    if st.session_state.chat_history:
        st.sidebar.metric("Chat Messages", len(st.session_state.chat_history))
    
    if st.session_state.feedback:
        helpful_feedback = sum(1 for f in st.session_state.feedback if f["helpful"])
        total_feedback = len(st.session_state.feedback)
        st.sidebar.metric("Helpful Feedback", f"{helpful_feedback}/{total_feedback}")

# Add some debug info in an expander
with st.sidebar.expander("Debug Info"):
    st.write(f"Engine initialized: {st.session_state.initialized}")
    st.write(f"Chat history length: {len(st.session_state.chat_history)}")
    st.write(f"Feedback entries: {len(st.session_state.feedback)}")
    if st.session_state.wandb_run:
        st.write(f"W&B run: {st.session_state.wandb_run.name}")