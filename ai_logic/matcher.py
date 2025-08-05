from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def match_documents(query_text, documents, document_names, embed_func):
    """
    Compare query_text (like job description or CV) with a list of documents.

    Steps:
    1. Convert query_text to embedding vector using embed_func.
    2. Convert each document in 'documents' list to its embedding.
    3. Use cosine similarity to measure how similar each document is to the query.
    4. Pair each document's name with its similarity score.
    5. Sort all results from most similar to least similar.

    Parameters:
        - query_text (str): The main text to match against (job or CV).
        - documents (List[str]): List of all text files (CVs or jobs).
        - document_names (List[str]): Corresponding filenames for above documents.
        - embed_func (Callable): Function to convert text to vector (like get_embedding).

    Returns:
        - List of tuples: (filename, similarity_score), sorted from best to worst match.
    """
    query_embedding = embed_func(query_text)  # Convert input text to embedding
    doc_embeddings = np.array([embed_func(doc) for doc in documents])  # Embed all documents

    # Reshape the query vector to compare with document matrix
    query_embedding = query_embedding.reshape(1, -1)

    # Get similarity score between query and each document
    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

    # Pair filenames with scores, sort by highest score
    results = list(zip(document_names, similarities))
    results.sort(key=lambda x: x[1], reverse=True)
    return results
