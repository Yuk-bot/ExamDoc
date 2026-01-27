from fastapi import FastAPI, File, UploadFile
from typing import List
import os
from pydantic import BaseModel

from backend.pdf_extraction import extract_text_and_type
from backend.pdf_extraction import cleaned_text
from backend.storage import (
    generate_doc_id,
    save_pdf,
    save_text,
    create_metadata,
    save_metadata
)
from backend.chunking import adaptive_chunking
from backend.storage import save_chunks, validate_chunks
from backend.faiss import search_faiss
from backend.embeddings import embeded_chunks
from backend.faiss import build_faiss_index, INDEX_PATH
from backend.context import assemble_context



class QueryRequest(BaseModel):
    query: str
    k_top: int=5

app= FastAPI() #fast api object

@app.post("/query")
def query_documents(request: QueryRequest):
    results = search_faiss(
        query=request.query,
        k_top=request.k_top
    )

    assemble_context(results)

    if not results:
        return {
            "query": request.query,
            "answer": None,
            "matches": []
        }

    return {
        "query": request.query,
        "matches": results
    }

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def display():
    return{"done"}
@app.post("/upload-files")
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        pdf_bytes = await file.read()
        doc_id = generate_doc_id()
        pdf_path = save_pdf(pdf_bytes, doc_id)

        raw_text, is_scanned = extract_text_and_type(pdf_path)
        

        clean_text = cleaned_text(raw_text)
        text_path = save_text(clean_text, doc_id)

        chunks = adaptive_chunking(
        clean_text,
        doc_id,
        is_scanned
        )
    
        chunks = validate_chunks(chunks)
        chunk_path = save_chunks(chunks, doc_id)

        metadata = create_metadata(
            doc_id,
            file.filename,
            pdf_path,
            text_path,
            is_scanned,
            len(clean_text)
        )
        metadata["chunk_count"] = len(chunks)
        metadata["chunk_path"] = chunk_path

        texts = [c["text"] for c in chunks]

        if texts:  #safety check for embeddings
            embeddings = embeded_chunks(chunks)

        if not os.path.exists(INDEX_PATH):
            build_faiss_index(embeddings, chunks) #indexes built before handn so that can be searched later

        save_metadata(metadata, doc_id)
        results.append(metadata)
    return results 

#results - list of dictionaries of inidvidual metadata

#ye sab filhal ke reference keliye b4 github clean this it is actually senseless here like ahh this shud be ab ratta right the command
# uvicorn <filename>:<api_object> --reload
#eg - uvicorn main:app --reload
#the parameter inside the get function denotes the path of api endpoint- extension path