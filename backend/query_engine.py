# src/query_engine.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import libraries
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.groq import Groq
from llama_index.core import Settings
import chromadb

# Import our new modules
from backend.youtube_search import YouTubeSearcher
from backend.quiz_generator import QuizGenerator
from backend.query_rewriter import QueryRewriter
from backend.database import get_quizzes

class EnhancedQueryEngine:
    def __init__(self):
        # --- Configuration ---
        self.persist_dir = project_root / "storage" / "chroma_db"
        
        # Check if vector store exists
        if not self.persist_dir.exists():
            raise FileNotFoundError("Vector store not found. Please run ingestion first.")
        
        # --- 1. Load the vector store ---
        chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        chroma_collection = chroma_client.get_or_create_collection("academic_lectures")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        
        # --- 2. Configure the LLM ---
        self.llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
        Settings.llm = self.llm
        
        # --- 3. Initialize advanced features ---
        self.youtube_searcher = YouTubeSearcher()
        self.quiz_generator = QuizGenerator(self.llm)
        self.query_rewriter = QueryRewriter(self.llm)
        
        # --- 4. Custom prompt template for academic tutoring ---
        qa_prompt_template = (
            "You are an academic tutor assistant. Your goal is to help students understand course materials.\n"
            "Use the following context information from the lecture to answer the query.\n"
            "If the answer isn't in the context, say so. Explain your reasoning step-by-step.\n"
            "Context:\n"
            "{context_str}\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        
        self.qa_prompt = PromptTemplate(qa_prompt_template)
        
        # --- 5. Create query engine with custom prompt ---
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            text_qa_template=self.qa_prompt
        )
    
    def query(self, question, get_videos=False):
        """
        Enhanced query method with optional YouTube video recommendations
        """
        # First, rewrite the query for better retrieval
        rewritten_query = self.query_rewriter.rewrite_query(question)
        print(f"Original query: {question}")
        print(f"Rewritten query: {rewritten_query}")
        
        # Get answer using the rewritten query
        response = self.query_engine.query(rewritten_query)
        
        result = {
            "answer": str(response),
            "source_nodes": response.source_nodes,
            "videos": []
        }
        
        # Get YouTube videos if requested or if confidence is low
        if get_videos or self._is_low_confidence(response):
            result["videos"] = self.youtube_searcher.search_educational_videos(question)
        
        return result
    
    def generate_quiz(self, topic, context=None, num_questions=5):
        """
        Generate a quiz on the given topic
        """
        if context is None:
            # If no context provided, retrieve some based on the topic
            retrieval_response = self.query_engine.query(topic)
            context = "\n".join([node.text for node in retrieval_response.source_nodes])
        
        return self.quiz_generator.generate_quiz(topic, context, num_questions)
    
    def get_saved_quizzes(self, limit=10):
        """
        Retrieve saved quizzes from the database
        """
        return get_quizzes(limit)
    
    def _is_low_confidence(self, response):
        """
        Simple confidence check based on similarity scores
        """
        if not response.source_nodes:
            return True
        
        # Check if any node has a decent similarity score
        for node in response.source_nodes:
            if node.score > 0.7:  # Adjust this threshold as needed
                return False
        
        return True

# Example usage
if __name__ == "__main__":
    try:
        engine = EnhancedQueryEngine()
        
        # Test query with YouTube recommendations
        result = engine.query("Explain object-oriented programming", get_videos=True)
        print("Answer:", result["answer"])
        
        if result["videos"]:
            print("\nRecommended YouTube videos:")
            for video in result["videos"]:
                print(f"- {video['title']} ({video['url']})")
        
        # Test quiz generation
        quiz = engine.generate_quiz("Object-Oriented Programming")
        if quiz:
            print(f"\nGenerated quiz: {quiz['quiz_title']}")
            for i, question in enumerate(quiz['questions']):
                print(f"{i+1}. {question['question']}")
                for j, option in enumerate(question['options']):
                    print(f"   {chr(65+j)}. {option}")
                print()
        
    except Exception as e:
        print(f"Error: {e}")