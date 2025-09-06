import numpy as np
from .vectorizer import get_embedding
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def match_documents(query_text, documents, document_names, embed_func):
    """
    Compare query_text with a list of documents using embeddings.
    Returns sorted list of (filename, similarity_score) with scores in [0, 1].
    """
    # Embed the query
    query_embedding = embed_func(query_text)
    if query_embedding is None or not query_text.strip() or not np.isfinite(query_embedding).all():
        logging.warning("Invalid query embedding or empty query text")
        return []

    # Normalize query embedding
    query_norm = np.linalg.norm(query_embedding)
    if query_norm == 0:
        logging.warning("Query embedding has zero norm")
        return []
    query_embedding = query_embedding / query_norm
    logging.debug(f"Query embedding norm: {np.linalg.norm(query_embedding):.4f}")
    logging.debug(f"Query embedding sample: {query_embedding[:5]}")

    # Embed all documents
    doc_embeddings = []
    valid_docs = []
    valid_names = []
    for doc, name in zip(documents, document_names):
        if doc.strip():
            embedding = embed_func(doc)
            if embedding is not None and np.isfinite(embedding).all() and np.linalg.norm(embedding) > 0:
                norm = np.linalg.norm(embedding)
                embedding = embedding / norm
                logging.debug(f"Document {name} embedding norm: {np.linalg.norm(embedding):.4f}")
                logging.debug(f"Document {name} embedding sample: {embedding[:5]}")
                doc_embeddings.append(embedding)
                valid_docs.append(doc)
                valid_names.append(name)
            else:
                logging.warning(f"Invalid embedding for document {name}")
        else:
            logging.warning(f"Empty document {name}")

    if not doc_embeddings:
        logging.warning("No valid document embeddings")
        return []

    # Manual cosine similarity calculation
    similarities = []
    for i, doc_embedding in enumerate(doc_embeddings):
        similarity = np.dot(query_embedding, doc_embedding)
        similarity = max(0.0, min(1.0, similarity))  # Ensure [0, 1]
        similarities.append(similarity)
        logging.debug(f"Similarity for {valid_names[i]}: {similarity:.4f}")

    similarities = np.array(similarities)
    logging.debug(f"All similarities: {similarities.tolist()}")

    results = list(zip(valid_names, similarities))
    results.sort(key=lambda x: x[1], reverse=True)
    return results