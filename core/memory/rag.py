import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.api_bridge import APIBridge

class RAGProcessor:
    """
    Handles Long-Term Memory (RAG) using OpenAI Embeddings.
    Maintains a simple vector store for retrieving relevant past information.
    Uses numpy for cosine similarity calculation.
    """
    def __init__(self, api_bridge: APIBridge, storage_path: str = "vector_store.json"):
        self.api_bridge = api_bridge
        self.storage_path = Path(storage_path)
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.load()

    async def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Creates embedding and adds text to long-term memory.
        
        Args:
            text: The content to store
            metadata: Optional dictionary with extra info
        """
        embedding = await self.api_bridge.get_embedding(text)
        if embedding:
            self.vectors.append(np.array(embedding))
            self.metadata.append({
                "text": text,
                "metadata": metadata or {}
            })
            self.save()

    async def query(self, query_text: str, k: int = 3) -> List[str]:
        """
        Queries the vector store for most relevant context.
        
        Args:
            query_text: The user query or current context
            k: Number of relevant items to retrieve
        """
        if not self.vectors:
            return []
            
        query_embedding = await self.api_bridge.get_embedding(query_text)
        if not query_embedding:
            return []
            
        q_vec = np.array(query_embedding)
        
        # Calculate cosine similarities
        similarities = []
        for v in self.vectors:
            norm_q = np.linalg.norm(q_vec)
            norm_v = np.linalg.norm(v)
            if norm_q > 0 and norm_v > 0:
                sim = np.dot(q_vec, v) / (norm_q * norm_v)
            else:
                sim = 0.0
            similarities.append(float(sim))
            
        # Get top K indices above threshold
        threshold = 0.7 # Minimum similarity
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = [
            self.metadata[i]["text"] 
            for i in top_indices 
            if similarities[i] >= threshold
        ]
        
        return results

    def save(self):
        """Saves vectors and metadata to a JSON file."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "vectors": [v.tolist() for v in self.vectors],
                "metadata": self.metadata
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"RAG Save Error: {e}")

    def load(self):
        """Loads vectors and metadata from a JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vectors = [np.array(v) for v in data.get("vectors", [])]
                    self.metadata = data.get("metadata", [])
            except Exception as e:
                print(f"RAG Load Error: {e}")
                self.vectors = []
                self.metadata = []

    def clear(self):
        """Clears all stored vectors and metadata."""
        self.vectors = []
        self.metadata = []
        if self.storage_path.exists():
            try:
                self.storage_path.unlink()
            except Exception as e:
                print(f"Error deleting vector store: {e}")
