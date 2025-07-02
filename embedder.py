from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import re

_model: Optional[SentenceTransformer] = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_embedding(text: str) -> np.ndarray:
    """
    Convert input text to a normalized (L2) embedding vector of shape (384,).
    Returns a zero vector if input is empty or on exception.
    """
    if not text or not text.strip():
        return np.zeros(384, dtype=np.float32)
    try:
        model = _get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return np.zeros(384, dtype=np.float32)
        return embedding / norm
    except Exception:
        return np.zeros(384, dtype=np.float32)

def summarize_video(title: str) -> str:
    """
    Generates a pseudo-summary from the title for now.
    Later can be replaced with transcript-based summarization.
    """
    # Clean the title
    title = re.sub(r'[^\u0000-\u00ff\w\s]', '', title)  # Remove non-ASCII for robustness
    words = title.split()

    if not words:
        return "No summary available"

    # Heuristic summary: first 8 words + keywords
    summary = " ".join(words[:8])
    
    # Add some keywords heuristically
    keywords = [w for w in words if len(w) > 5][:3]
    if keywords:
        summary += ". Keywords: " + ", ".join(keywords)

    return summary.strip() 