import os
import json
from typing import List, Dict
import numpy as np
import faiss
from embedder import get_embedding
import random


def add_to_index(user_id: str, video_id: str, title: str, summary: str, embedding: np.ndarray):
    index_path = f"index_{user_id}.faiss"
    memory_path = f"memory_{user_id}.json"

    # Load or create FAISS index
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        index = faiss.IndexFlatL2(embedding.shape[0])

    # Add embedding to index
    index.add(np.expand_dims(embedding, axis=0).astype(np.float32))  # type: ignore
    faiss.write_index(index, index_path)

    # Append metadata to JSON
    metadata = {
        "video_id": video_id,
        "title": title,
        "summary": summary
    }
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(metadata)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def search_memory(user_id: str, query: str) -> List[Dict]:
    index_path = f"index_{user_id}.faiss"
    memory_path = f"memory_{user_id}.json"
    if not os.path.exists(index_path) or not os.path.exists(memory_path):
        return []

    # Load index and metadata
    index = faiss.read_index(index_path)
    with open(memory_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Embed query
    query_vec = get_embedding(query).astype(np.float32)
    D, I = index.search(np.expand_dims(query_vec, axis=0), k=min(3, len(data)))

    results = []
    for idx in I[0]:
        if idx < 0 or idx >= len(data):
            continue
        item = data[idx]
        video_id = item["video_id"]
        # YouTube thumbnail URL format
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        results.append({
            "video_id": video_id,
            "title": item["title"],
            "summary": item["summary"],
            "thumbnail_url": thumbnail_url
        })
    return results


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
        add_to_index(user_id, video["video_id"], video["title"], video["summary"], embedding)

def clear_memory(user_id: str):
    index_path = f"index_{user_id}.faiss"
    memory_path = f"memory_{user_id}.json"
    if os.path.exists(index_path):
        os.remove(index_path)
    if os.path.exists(memory_path):
        os.remove(memory_path) 