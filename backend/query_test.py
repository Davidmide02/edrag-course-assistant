# scripts/query_test.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the root of the project to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import required libraries
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

def main():
    # --- Configuration ---
    persist_dir = project_root / "storage" / "chroma_db"
    
    # --- 1. Load the persisted ChromaDB index ---
    print("Loading persisted vector store...")
    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_or_create_collection("academic_lectures")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Load the index from storage
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    
    # --- 2. Create a query engine ---
    # For testing, we'll use a simple retriever to get top chunks
    retriever = index.as_retriever(similarity_top_k=5)  # Get top 3 similar chunks
    
    # --- 3. Perform a sample query ---


    # Try these more specific queries
    test_queries = [
    "Explain the main concepts covered in this lecture",
    "What are the key learning objectives",
    "existential quantification"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        retrieved_nodes = retriever.retrieve(query)
        for i, node in enumerate(retrieved_nodes[:3]):  # Show top 3 only
            print(f"--- Chunk {i+1} (Score: {node.score:.3f}) ---")
            print(f"Text: {node.text[:200]}...")  # Show first 200 chars
            print()
    # query = "What is the main topic of the lecture?"
    # print(f"Query: {query}")
    
    # retrieved_nodes = retriever.retrieve(query)
    # for i, node in enumerate(retrieved_nodes):
    #     print(f"\n--- Chunk {i+1} ---")
    #     print(f"Text: {node.text}")
    #     print(f"Metadata: {node.metadata}")
    #     print(f"Score: {node.score}")

if __name__ == "__main__":
    main()