import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model only once
global_model = None

def get_embedding(text: str) -> np.ndarray:
    global global_model
    if global_model is None:
        global_model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = global_model.encode(text)
    return np.array(embedding) 