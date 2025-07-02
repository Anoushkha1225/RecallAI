import os
import json
from typing import List, Dict
import numpy as np
import faiss
from embedder import get_embedding
import random

# In-memory storage for each user
memory_index: Dict[str, List[Dict]] = {}

def add_to_index(user_id: str, title: str, summary: str, url: str, embedding: np.ndarray):
    """
    Add a memory item (video) to a user's memory index.
    """
    if user_id not in memory_index:
        memory_index[user_id] = []
    
    memory_index[user_id].append({
        "title": title,
        "summary": summary,
        "url": url,
        "embedding": embedding
    })

def search_memory(user_id: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
    """
    Search the user's memory index for the closest matching items using cosine similarity.
    """
    if user_id not in memory_index or not memory_index[user_id]:
        return []
    
    memories = memory_index[user_id]
    scored = []

    for item in memories:
        sim = cosine_similarity(query_embedding, item["embedding"])
        scored.append((sim, item))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    top_matches = [item for _, item in scored[:top_k]]
    return top_matches

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

def clear_memory(user_id: str):
    """
    Clear all stored memory for a user.
    """
    memory_index[user_id] = []

def generate_dummy_data(user_id: str):
    """
    Creates 3 fake videos with summaries and random embeddings, and adds them to the index and metadata file for demo purposes.
    """
    fake_videos = [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Never Gonna Give You Up",
            "summary": "A classic music video that became an internet meme. The song is catchy and the video is iconic."
        },
        {
            "video_id": "3JZ_D3ELwOQ",
            "title": "Charlie bit my finger!",
            "summary": "A viral video featuring two brothers. Charlie bites his brother's finger, leading to a funny reaction."
        },
        {
            "video_id": "9bZkp7q19f0",
            "title": "PSY - GANGNAM STYLE(강남스타일) M/V",
            "summary": "The most-watched YouTube video for years. PSY's dance moves and catchy tune took the world by storm."
        }
    ]
    for video in fake_videos:
        # Generate a random embedding of the correct dimension (384)
        embedding = np.random.rand(384).astype(np.float32)
        add_to_index(user_id, video["title"], video["summary"], "", embedding) 