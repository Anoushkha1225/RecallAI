from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once
global_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> np.ndarray:
    embedding = global_model.encode(text, convert_to_numpy=True)
    return embedding 