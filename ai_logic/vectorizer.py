from sentence_transformers import SentenceTransformer
import numpy as np

# Load the sentence transformer model once (MiniLM is small & fast, good for similarity)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Convert the given text into a sentence embedding vector.
    
    If the text is empty or blank, return a zero vector instead of crashing.
    This vector will be used later for comparing with other documents.
    """
    if not text.strip():
        return np.zeros((384,))  # Return zero vector if empty text
    return model.encode(text, convert_to_numpy=True)  # Return sentence embedding
