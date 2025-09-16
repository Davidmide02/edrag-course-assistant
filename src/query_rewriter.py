# src/query_rewriter.py

class QueryRewriter:
    def __init__(self, llm):
        self.llm = llm
    
    def rewrite_query(self, original_query):
        """
        Rewrite the user query to be more effective for retrieval
        """
        prompt = f"""
        Rewrite the following student question to be more effective for retrieving relevant information from educational materials.
        Make it more specific, clear, and focused on key concepts.
        
        Original query: "{original_query}"
        
        Rewritten query:
        """
        
        try:
            response = self.llm.complete(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return original_query  # Fallback to original query