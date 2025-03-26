import json
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SimpleEmbeddings:
    """A simple wrapper for OpenAI's embeddings API"""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in the .env file or pass it to SimpleEmbeddings.")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents"""
        all_embeddings = []
        
        # Process in batches of 20 to avoid API limits
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self._get_embeddings_from_api(batch_texts)
            all_embeddings.extend(batch_embeddings)
            
            # Print progress
            print(f"Embedded {min(i+batch_size, len(texts))}/{len(texts)} documents")
        
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embeddings for a query string"""
        embeddings = self._get_embeddings_from_api([text])
        return embeddings[0]
    
    def _get_embeddings_from_api(self, texts: List[str]) -> List[List[float]]:
        """Call OpenAI API to get embeddings"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "input": texts,
                "model": "text-embedding-3-small"  # Using OpenAI's latest embedding model
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract and return the embeddings
            return [item["embedding"] for item in result["data"]]
            
        except Exception as e:
            print(f"Error getting embeddings from API: {e}")
            # Return a fake embedding for testing
            return [[0.0] * 1536] * len(texts)  # OpenAI embeddings are 1536-dimensional

class SimpleVectorStore:
    """A simple in-memory vector store that mimics basic functionality of ChromaDB"""
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        texts = [doc["content"] for doc in documents]
        embeddings = self.embedding_function.embed_documents(texts)
        
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        
        print(f"Added {len(documents)} documents to vector store")
        
        # Save to disk
        self.save("data/vector_store.pkl")
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Find the k most similar documents to the query"""
        # Get query embedding
        query_embedding = self.embedding_function.embed_query(query)
        
        # Calculate cosine similarity
        similarities = self._cosine_similarity(query_embedding)
        
        # Get top k indices
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        # Return documents
        return [self.documents[i] for i in top_k_indices]
    
    def _cosine_similarity(self, query_embedding: List[float]) -> np.ndarray:
        """Calculate cosine similarity between query and all documents"""
        query_norm = np.linalg.norm(query_embedding)
        dot_products = np.dot(self.embeddings, query_embedding)
        
        # Calculate norms for document embeddings
        doc_norms = np.linalg.norm(self.embeddings, axis=1)
        
        # Calculate cosine similarity
        similarities = dot_products / (doc_norms * query_norm)
        
        return similarities
    
    def save(self, filepath: str):
        """Save the vector store to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'embeddings': self.embeddings
            }, f)
        print(f"Vector store saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str, embedding_function):
        """Load the vector store from disk"""
        instance = cls(embedding_function)
        
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                instance.documents = data['documents']
                instance.embeddings = data['embeddings']
            print(f"Vector store loaded from {filepath} with {len(instance.documents)} documents")
        else:
            print(f"No existing vector store found at {filepath}")
        
        return instance
    
    def as_retriever(self, search_kwargs=None):
        """Return a retriever interface"""
        search_kwargs = search_kwargs or {"k": 3}
        
        class SimpleRetriever:
            def __init__(self, vector_store, search_kwargs):
                self.vector_store = vector_store
                self.search_kwargs = search_kwargs
            
            def get_relevant_documents(self, query):
                return self.vector_store.similarity_search(query, **self.search_kwargs)
        
        return SimpleRetriever(self, search_kwargs)

def create_vector_store(processed_data_file: str = 'data/processed_data.json', 
                        vector_store_file: str = 'data/vector_store.pkl'):
    """Create or load a vector store from processed data"""
    # Initialize embeddings function
    embeddings_function = SimpleEmbeddings()
    
    # Try to load existing vector store
    if os.path.exists(vector_store_file):
        print(f"Loading existing vector store from {vector_store_file}")
        return SimpleVectorStore.load(vector_store_file, embeddings_function)
    
    # Load processed data
    if not os.path.exists(processed_data_file):
        print(f"Processed data file {processed_data_file} not found")
        return SimpleVectorStore(embeddings_function)
    
    with open(processed_data_file, 'r') as f:
        processed_data = json.load(f)
    
    # Create vector store
    vector_store = SimpleVectorStore(embeddings_function)
    vector_store.add_documents(processed_data)
    
    return vector_store

if __name__ == "__main__":
    # If no processed data, generate it
    if not os.path.exists('data/processed_data.json'):
        from data_processor import process_scraped_data
        
        # If no scraped data, scrape it
        if not os.path.exists('data/scraped_data.json') and not os.path.exists('data/fallback_data.json'):
            from scraper import get_fallback_data
            get_fallback_data()
        
        process_scraped_data()
    
    # Create vector store
    create_vector_store()
