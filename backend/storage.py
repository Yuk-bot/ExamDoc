import uuid
import os
from datetime import datetime
import json
from backend.pdf_extraction import extract_text_and_type
def generate_doc_id() -> str:
    return str(uuid.uuid4())

BASE_STORAGE = "storage"
PDF_DIR = os.path.join(BASE_STORAGE, "original_pdfs")

os.makedirs(PDF_DIR, exist_ok=True)

def save_pdf(pdf_bytes, doc_id):#this function returns the path of the saved file- uploaded files
    path = os.path.join(PDF_DIR, f"{doc_id}.pdf")
    with open(path, "wb") as f:
        f.write(pdf_bytes)
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
    pdf_path: str,
    text_path: str,
    is_scanned: bool,
    text_length: int):

    return {
        "doc_id": doc_id,
        "original_filename": original_name,
        "pdf_path": pdf_path,
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

def validate_chunks(chunks: list[dict]):
    valid = []

    for c in chunks:
        if c.get("text") and len(c["text"].strip()) > 20:
            valid.append(c)

    return valid #the final chunks













