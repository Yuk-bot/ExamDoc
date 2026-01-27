import faiss, json, os
import numpy as np
from sentence_transformers import SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")

from backend.storage import (
    generate_doc_id,
    save_pdf,
    save_text,
    create_metadata,
    save_metadata
)

"""
from backend.pdf_extraction import extract_text_and_type
from backend.pdf_extraction import cleaned_text
from backend.chunking import adaptive_chunking
from backend.storage import save_chunks, validate_chunks
"""
doc_id=generate_doc_id
FAISS_DIR="storage/faiss/{doc_id}/"
os.makedirs(FAISS_DIR, exist_ok=True)



INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
META_PATH = os.path.join(FAISS_DIR, "metadata.json")

"""INDEX_PATH = f"storage/faiss/{doc_id}/index.faiss"
META_PATH  = f"storage/faiss/{doc_id}/metadata.json"""

def build_faiss_index(embeddings, metadatas):
    """
    embeddings contains obvio list of vectors
    metdata contains doc id, chunk id and text however will now store faiss_index like basically chubks will be mapped to indexes

    """
    vectors=np.array(embeddings).astype("float32")
    d=vectors.shape[1]
    index=faiss.IndexFlatL2(d) #building the index
    index.add(vectors)
    faiss.write_index(index, INDEX_PATH)

#storing faiss indexes along with the previous things
    with open(META_PATH, 'w', encoding="utf-8") as f:
        json.dump(metadatas, f, indent=2)

    print(index.is_trained, index.ntotal)




def load_faiss_index():
    if not os.path.exists(INDEX_PATH):
        raise RuntimeError(
            "FAISS index not found. Build the index before searching."
        )

    if not os.path.exists(META_PATH):
        raise RuntimeError(
            "FAISS metadata not found."
        )
    index=faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata

def search_faiss(query: str, k_top: int=5):
    index, metadata=load_faiss_index()
    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True #normalized query
    ).astype("float32")
 
    scores, indices=index.search(query_vector, k_top)
    results=[]
    threshold=1.5
    for score, i in zip(scores[0], indices[0]):
        #indices-i, socres-score
        #(score, indices) are the tuples zipped togther
        if i==-1:
            continue
        if score>threshold:
            continue
            
        chunk_meta=metadata[i].copy()
        chunk_meta["score"]=float(score)
        results.append(chunk_meta) #put the similar vector findings into metdata to be later used by llm
    return results




