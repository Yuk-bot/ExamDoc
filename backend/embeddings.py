from sentence_transformers import SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")

def embeded_chunks(chunks: list[dict]):
    texts=[c["text"] for c in chunks]
    embeddings=model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True) #projecting chunks as vectors
#converting embeddings vector to numpy array-easier for vector db use- normalized embeddings
#normalizing embeddings- since magntidue of vector embeddings equals 1, it becomes easy for cosine similarity calculation
    
    return embeddings
#to do while calling- print shape 