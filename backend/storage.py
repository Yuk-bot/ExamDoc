import uuid
import os
from datetime import datetime
import json

def generate_doc_id() -> str:
    return str(uuid.uuid4())

BASE_STORAGE = "storage"
UPLOAD_DIR = os.path.join(BASE_STORAGE, "original_files")

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file_bytes, doc_id, ext):  #this function returns the path of the saved file- uploaded files
    path = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path

TEXT_DIR = os.path.join(BASE_STORAGE, "texts")
os.makedirs(TEXT_DIR, exist_ok=True)

def save_text(text: str, doc_id): #storing clean text files and returning its path
    path = os.path.join(TEXT_DIR, f"{doc_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def create_metadata(doc_id: str,
    original_name: str,
    file_path: str,
    text_path: str,
    is_scanned: bool,
    text_length: int):

    return {
        "doc_id": doc_id,
        "original_filename": original_name,
        "file_path": file_path,
        "text_path": text_path,
        "is_scanned": is_scanned,
        "text_length": text_length,
        "uploaded_at": datetime.utcnow().isoformat() #timezone aware times
    }


META_DIR = os.path.join(BASE_STORAGE, "metadata")
os.makedirs(META_DIR, exist_ok=True)

def save_metadata(metadata: dict, doc_id: str) -> str:
    path = os.path.join(META_DIR, f"{doc_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return path

CHUNK_DIR = "storage/chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def save_chunks(chunks: list[dict], doc_id: str) -> str:
    path = os.path.join(CHUNK_DIR, f"{doc_id}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return path

SUMMARY_DIR="storage/summary"
os.makedirs(SUMMARY_DIR, exist_ok=True)
def save_summary(summary:str, doc_id) :
    path=os.path.join(SUMMARY_DIR, f"{doc_id}.json")
    with open(path, "w", encoding="utf-8" ) as f:
        json.dump(summary, f, indent=2)

#stores the latest docid in this file so for summary it will pick the doc id from this file and pass tolaod summary so summary of latest files will be displayed
    latest_path = os.path.join(SUMMARY_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump({"doc_id": doc_id}, f, indent=2)

    return path



    

    
def validate_chunks(chunks: list[dict]):
    valid = []

    for c in chunks:
        text = c.get("text", "").strip()
        if len(text) >= 80:  # semantic chunks should be richer
            valid.append(c)

    return valid