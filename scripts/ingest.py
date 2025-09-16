# scripts/ingest.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the root of the project to the Python path so we can import from `src`
project_root = Path(__file__).parent.parent
print("project_root", project_root)
sys.path.append(str(project_root))
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_API_KEY")

# Now import the required libraries
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
# from llama_index import Ve
import chromadb

def get_embedding_model():
    """
    Instantiates and returns the embedding model.
    We are using OpenAI's 'text-embedding-3-small' for its reliability and performance.
    This is separate from the LLM (Groq) we use for generation.
    """
    return OpenAIEmbedding(model="text-embedding-3-small")

def main():
    # --- Configuration ---
    data_dir = project_root / "data"
    persist_dir = project_root / "storage" / "chroma_db"
    
    # Create directories if they don't exist
    data_dir.mkdir(exist_ok=True)
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    # --- 1. Load Documents ---
    print("Loading documents...")
    # This will automatically use PyPDF2 to read the PDF(s) in the data directory
    documents = SimpleDirectoryReader(str(data_dir)).load_data()


     # Enhance documents with custom metadata, e.g., lecture_id
    for doc in documents:
        # Example: Use the file name as lecture_id, or you can define a mapping
        file_name = "lecture_02"
        doc.metadata['lecture_id'] = file_name  # Or use a more structured ID
        # You can add other metadata fields here as needed

    print(f"Loaded {len(documents)} document(s).")
    
    # --- 2. Chunk Documents into Nodes ---
    print("Chunking documents...")
    # This is a key step. We experiment with size 512 and an overlap of 50.
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"Split sample into {nodes[:5]} node(s).")
    print(f"Created {len(nodes)} nodes.")
    
    # --- 3. Initialize ChromaDB ---
    # Create a ChromaDB client and collection
    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_or_create_collection("academic_lectures")
    # Wrap it in a LlamaIndex VectorStore
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # --- 4. Create and Persist the Index ---
    print("Creating index and generating embeddings...")
    # This step will use the embedding model to create vectors for all nodes and store them in ChromaDB.
    embed_model = get_embedding_model()
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model
    )
    
    # Persisting is handled by Chroma's PersistentClient.
    # The index is already saved in the `persist_dir`.
    print(f"Ingestion complete! Vector store persisted to: {persist_dir}")

if __name__ == "__main__":
    main()