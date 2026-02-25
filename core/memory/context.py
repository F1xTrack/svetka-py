import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import ConfigManager

from core.memory.rag import RAGProcessor

class ContextManager:
    """
    Manages short-term conversation history and context for the AI.
    Handles limits, saving/loading history, and providing context for API calls.
    Includes summarization logic for long conversations and RAG for long-term memory.
    """
    def __init__(self, config_manager: ConfigManager, api_bridge=None):
        self.config = config_manager
        self.api_bridge = api_bridge
        self.history: List[Dict[str, Any]] = []
        self.summary: str = "" # Holds the summary of old context
        
        # Initialize RAG
        vector_path = self.config.get("memory.vector_store_path", "vector_store.json")
        if not vector_path.endswith(".json"):
             vector_path += ".json"
        self.rag = RAGProcessor(api_bridge, vector_path)
        
        # Determine memory file path
        db_path = self.config.get("memory.db_path", "memory.json")
        if not db_path.endswith(".json"):
            if self.config.get("memory.storage_type") == "json":
                db_path = str(Path(db_path).with_suffix(".json"))
        
        self.memory_file = Path(db_path)
        self.short_term_limit = self.config.get("memory.short_term_limit", 100)
        self.summary_trigger = self.config.get("memory.summary_trigger", 50)
        self.compression_ratio = self.config.get("memory.compression_ratio", 0.5)
        
        self.load_history()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Adds a message to the history and saves it.
        Triggers summarization if needed and stores in RAG if enabled.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(message)
        
        # Store in Long-Term Memory (RAG) if enabled and relevant (e.g. user messages)
        if self.config.get("memory.long_term_enabled") and role == "user" and self.api_bridge:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.rag.add_text(content, metadata))
            except Exception as e:
                print(f"Error starting RAG storage: {e}")
        
        # Check if we should summarize
        self._check_summary_needed()
        self._enforce_limit()
        self.save_history()

    async def get_context_with_rag(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Returns the context including relevant bits from Long-Term Memory (RAG).
        """
        if limit is None:
            limit = self.config.get("api.history_limit", 20)
            
        context = []
        
        # 1. Add Summary
        if self.summary:
            context.append({
                "role": "system", 
                "content": f"SUMMARY OF PREVIOUS CONVERSATION: {self.summary}"
            })
            
        # 2. Add RAG Context
        if self.config.get("memory.rag_enabled") and self.api_bridge:
            relevant_items = await self.rag.query(query)
            if relevant_items:
                rag_content = "\n".join(relevant_items)
                context.append({
                    "role": "system",
                    "content": f"RELEVANT INFO FROM LONG-TERM MEMORY:\n{rag_content}"
                })
                
        # 3. Add Recent History
        api_format = [
            {"role": m["role"], "content": m["content"]}
            for m in self.history
        ]
        context.extend(api_format[-limit:])
        return context

    def get_context(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Returns the context (Summary + last N messages).
        """
        if limit is None:
            limit = self.config.get("api.history_limit", 20)
        
        context = []
        # If we have a summary, add it as a system message
        if self.summary:
            context.append({
                "role": "system", 
                "content": f"SUMMARY OF PREVIOUS CONVERSATION: {self.summary}"
            })
            
        # Add actual history
        api_format = [
            {"role": m["role"], "content": m["content"]}
            for m in self.history
        ]
        context.extend(api_format[-limit:])
        return context

    def _check_summary_needed(self):
        """Checks if history length exceeds trigger and initiates summarization."""
        if len(self.history) >= self.summary_trigger and self.api_bridge:
            # We use a non-blocking way to call the async summarize
            # In a real app, this would be handled by a task manager
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.summarize_now())
                else:
                    asyncio.run(self.summarize_now())
            except Exception as e:
                print(f"Error starting summarization: {e}")

    async def summarize_now(self):
        """Performs summarization and shrinks history."""
        if not self.api_bridge: return
        
        # Take messages to summarize (compression_ratio fraction)
        num_to_summarize = int(len(self.history) * self.compression_ratio)
        if num_to_summarize <= 0: return
        
        to_summarize = self.history[:num_to_summarize]
        
        # Include old summary if exists
        context_for_summary = []
        if self.summary:
            context_for_summary.append({"role": "system", "content": f"Current summary: {self.summary}"})
        context_for_summary.extend(to_summarize)
        
        try:
            new_summary = await self.api_bridge.summarize(context_for_summary)
            if new_summary:
                self.summary = new_summary
                self.history = self.history[num_to_summarize:]
                self.save_history()
        except Exception as e:
            print(f"Summarization failed: {e}")

    def _enforce_limit(self):
        """Ensures history doesn't exceed strict limit."""
        if len(self.history) > self.short_term_limit:
            self.history = self.history[-self.short_term_limit:]

    def save_history(self):
        """Saves both history and summary to memory file."""
        data = {
            "summary": self.summary,
            "history": self.history
        }
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        """Loads both history and summary."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.summary = data.get("summary", "")
                        self.history = data.get("history", [])
                    else:
                        # Fallback for old list-only format
                        self.history = data
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = []

    def clear_history(self):
        self.history = []
        self.summary = ""
        self.save_history()

    def full_wipe(self):
        """Полная очистка всех данных памяти (история + RAG)"""
        self.clear_history()
        if hasattr(self, "rag"):
            self.rag.clear()
