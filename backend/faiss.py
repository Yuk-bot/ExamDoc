import faiss
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.storage import generate_doc_id

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_id=generate_doc_id()
FAISS_DIR = f"storage/faiss"
os.makedirs(FAISS_DIR, exist_ok=True)
INDEX_PATH=f"{FAISS_DIR}/index.faiss"
META_PATH=f"{FAISS_DIR}/metadata.json"

def build_or_update_faiss(embeddings, metadatas):
    if len(embeddings) != len(metadatas):
        raise ValueError(
            "Embeddings and metadata length mismatch"
        )

    vectors = np.array(embeddings).astype("float32")
    #faiss.normalize_L2(vectors) #normalized vector for query

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            existing_meta = json.load(f)
    else:
        index = faiss.IndexFlatL2(vectors.shape[1])
        existing_meta = []

    index.add(vectors)
    existing_meta.extend(metadatas)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_meta, f, indent=2)


def load_faiss_index():
    if not os.path.exists(INDEX_PATH):
        raise RuntimeError("FAISS index not found. Build the index before searching.")

    if not os.path.exists(META_PATH):
        raise RuntimeError("FAISS metadata not found.")

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search_faiss(query: str, k_top: int = 20):
    index, metadata = load_faiss_index()

    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    distances, indices = index.search(query_vector, k_top*5)

    results = []
    #DISTANCE_THRESHOLD=1.1
    for distance, i in zip(distances[0], indices[0]):
        if i == -1 or i >= len(metadata):
            continue

        #if distance>DISTANCE_THRESHOLD:
            #continue
        
        #if metadata[i]["doc_id"] != doc_id: #to ensure that the ans comes from the uploaded pdf only like the one whose doc id u mention
            #continue   
        
        chunk_meta = metadata[i].copy()
        chunk_meta["distance"] = float(distance)
        results.append(chunk_meta)
    return results 