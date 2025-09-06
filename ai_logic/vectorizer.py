from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Convert the given text into a sentence embedding vector.
    If the text is empty or blank, return a zero vector.
    """
    if not text.strip():
        logging.warning("Empty text provided for embedding")
        return np.zeros((384,))
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        if not np.isfinite(embedding).all():
            logging.warning("Invalid embedding (non-finite values)")
            return np.zeros((384,))
        logging.debug(f"Embedding shape: {embedding.shape}, sample: {embedding[:5]}")
        return embedding
    except Exception as e:
        logging.error(f"Error generating embedding: {str(e)}")
        return np.zeros((384,))