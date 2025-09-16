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

def setup_query_engine():
    # --- Configuration ---
    persist_dir = project_root / "storage" / "chroma_db"
    
    # Check if vector store exists
    if not persist_dir.exists():
        raise FileNotFoundError("Vector store not found. Please run ingestion first.")
    
    # --- 1. Load the vector store ---
    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_or_create_collection("academic_lectures")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    
    # --- 2. Configure the LLM ---
    # Initialize Groq LLM
    llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    
    # Set the LLM in Settings
    Settings.llm = llm
    
    # --- 3. Custom prompt template for academic tutoring ---
    qa_prompt_template = (
        "You are an academic tutor assistant. Your goal is to help students understand course materials.\n"
        "Use the following context information from the lecture to answer the query.\n"
        "If the answer isn't in the context, say so. Explain your reasoning step-by-step.\n"
        "Context:\n"
        "{context_str}\n"
        "Query: {query_str}\n"
        "Answer: "
    )
    
    qa_prompt = PromptTemplate(qa_prompt_template)
    
    # --- 4. Create query engine with custom prompt ---
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        text_qa_template=qa_prompt
    )
    
    return query_engine

if __name__ == "__main__":
    try:
        query_engine = setup_query_engine()
        query = "What is the main topic of the lecture?"
        response = query_engine.query(query)
        print(f"Query: {query}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")