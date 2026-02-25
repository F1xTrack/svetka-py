import pytest
import os
import json
from pathlib import Path
from core.config import ConfigManager
from core.memory.context import ContextManager

@pytest.fixture
def temp_memory():
    config_path = "test_memory_config.yaml"
    memory_path = "test_memory.json"
    if os.path.exists(config_path): os.remove(config_path)
    if os.path.exists(memory_path): os.remove(memory_path)
    
    cm = ConfigManager(config_path)
    # Correctly set fields through ConfigManager
    cm.set("memory.db_path", memory_path)
    cm.set("memory.short_term_limit", 5)
    cm.set("api.history_limit", 3)
    
    yield cm, memory_path
    
    if os.path.exists(config_path): os.remove(config_path)
    if os.path.exists(memory_path): os.remove(memory_path)

def test_add_message(temp_memory):
    cm, memory_path = temp_memory
    ctx = ContextManager(cm)
    ctx.add_message("user", "Hello")
    assert len(ctx.history) == 1
    assert ctx.history[0]["role"] == "user"
    assert ctx.history[0]["content"] == "Hello"
    assert os.path.exists(memory_path)

def test_limit_enforcement(temp_memory):
    cm, memory_path = temp_memory
    ctx = ContextManager(cm)
    for i in range(10):
        ctx.add_message("user", f"Message {i}")
    assert len(ctx.history) == 5
    assert ctx.history[0]["content"] == "Message 5"
    assert ctx.history[-1]["content"] == "Message 9"

def test_get_context(temp_memory):
    cm, memory_path = temp_memory
    ctx = ContextManager(cm)
    for i in range(5):
        ctx.add_message("user", f"Message {i}")
    
    # Check default limit from config (3)
    context = ctx.get_context()
    assert len(context) == 3
    assert context[0]["content"] == "Message 2"
    assert context[-1]["content"] == "Message 4"
    
    # Check explicit limit
    context2 = ctx.get_context(limit=2)
    assert len(context2) == 2
    assert context2[0]["content"] == "Message 3"

def test_load_save(temp_memory):
    cm, memory_path = temp_memory
    ctx = ContextManager(cm)
    ctx.add_message("user", "Persistent")
    
    # Create new ctx pointed at same memory file
    ctx2 = ContextManager(cm)
    assert len(ctx2.history) == 1
    assert ctx2.history[0]["content"] == "Persistent"

from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_summarization_logic(temp_memory):
    cm, memory_path = temp_memory
    cm.set("memory.summary_trigger", 4)
    cm.set("memory.compression_ratio", 0.5)
    
    mock_api = MagicMock()
    mock_api.summarize = AsyncMock(return_value="Summarized context")
    
    ctx = ContextManager(cm, api_bridge=mock_api)
    
    # Add messages
    ctx.add_message("user", "Message 1")
    ctx.add_message("assistant", "Message 2")
    ctx.add_message("user", "Message 3")
    ctx.add_message("assistant", "Message 4")
    
    # Manually trigger or wait for task
    await ctx.summarize_now()
    
    assert ctx.summary == "Summarized context"
    assert len(ctx.history) == 2 # 4 - (4*0.5) = 2
    assert ctx.history[0]["content"] == "Message 3"
    
    # Check context output
    context = ctx.get_context()
    assert context[0]["role"] == "system"
    assert "SUMMARY" in context[0]["content"]
    assert context[1]["content"] == "Message 3"

import numpy as np
from core.memory.rag import RAGProcessor

@pytest.mark.asyncio
async def test_rag_logic(temp_memory):
    cm, memory_path = temp_memory
    mock_api = MagicMock()
    
    # Simple mock for embeddings
    async def mock_get_embedding(text, model=None):
        if "apple" in text: return [1.0, 0.0]
        if "car" in text: return [0.0, 1.0]
        return [0.5, 0.5]
    
    mock_api.get_embedding = mock_get_embedding
    
    rag_path = "test_rag_store.json"
    if os.path.exists(rag_path): os.remove(rag_path)
    
    rag = RAGProcessor(mock_api, rag_path)
    await rag.add_text("I love apples")
    await rag.add_text("The car is blue")
    
    # Query for apple-related text
    results = await rag.query("red apple")
    assert len(results) >= 1
    assert "I love apples" in results
    assert "The car is blue" not in results
    
    if os.path.exists(rag_path): os.remove(rag_path)

@pytest.mark.asyncio
async def test_context_with_rag(temp_memory):
    cm, memory_path = temp_memory
    mock_api = MagicMock()
    mock_api.get_embedding = AsyncMock(return_value=[0.1]*1536)
    
    ctx = ContextManager(cm, api_bridge=mock_api)
    ctx.summary = "Global summary"
    
    # Mock RAG query to return specific facts
    ctx.rag.query = AsyncMock(return_value=["Historical fact about user"])
    
    context = await ctx.get_context_with_rag("Who am I?")
    
    assert context[0]["role"] == "system"
    assert "Global summary" in context[0]["content"]
    assert "Historical fact" in context[1]["content"]
    assert "RELEVANT INFO" in context[1]["content"]

def test_clear_history(temp_memory):
    cm, memory_path = temp_memory
    ctx = ContextManager(cm)
    ctx.add_message("user", "Clear me")
    ctx.summary = "Some summary"
    ctx.clear_history()
    assert len(ctx.history) == 0
    assert ctx.summary == ""
    with open(memory_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["summary"] == ""
        assert len(data["history"]) == 0
