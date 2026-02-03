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
from backend.chunking import  adaptive_chunking
from backend.storage import save_chunks, validate_chunks, save_summary
from backend.faiss import search_faiss
from backend.embeddings import embeded_chunks
from backend.faiss import build_or_update_faiss, INDEX_PATH
from backend.context import assemble_context
from backend.llm import generate_answer, merge_chunks

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

    context=assemble_context(results)
    answer=generate_answer(query=request.query, context=context)

    if not results:
        return {
            "query": request.query,
            "answer": None, #this will  be returned 
            "matches": []
        }

   
    

    

    return {
        "query": request.query,
        "answer": answer,
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


        #propositions = get_propositions("The impact of pop music on people’s perception of gender in daily life is enormous. Just think of it, teenagers sharing their voices with the new single oftheir favorite influencer on Spotify and kids imitating the viral hit’s choreography in their rooms.")
        
        #if not propositions:
            #results.append({"doc_id": doc_id, "filename": file.filename, "error": "No propositions extracted"})
            #continue
        
        
      
        #checks the required chunking technique- clustering or sliding window chunking and executes it as per the document 
        #chunks = semantic_chunk_pipeline( doc_id, clean_text, similarity_threshold=0.7, large_block_size=15, use_clustering=True)
        chunks=adaptive_chunking(clean_text, doc_id, is_scanned)

    
        chunks = validate_chunks(chunks)
        chunk_path = save_chunks(chunks, doc_id)

        """chunk structure:
            doc id:" "
            chunk id:" "
            text: " "

        """

        metadata = create_metadata(
            doc_id,
            file.filename,
            pdf_path,
            text_path,
            is_scanned,
            len(clean_text),
            
        )
        metadata["chunk_count"] = len(chunks)
        metadata["chunk_path"] = chunk_path

        texts = [c["text"] for c in chunks]

        

        if texts:
            embeddings = embeded_chunks(chunks)
            build_or_update_faiss(embeddings, chunks)
            #indexes built before handn so that can be searched later

        summary=merge_chunks(chunks) #returns summary as a string
        summary_path=save_summary(summary, doc_id)
        metadata["summary_path"]=summary_path

        save_metadata(metadata, doc_id)
        results.append({"metadata":metadata, "summary": summary})
    return results 

#imp::: in results if the answer given to the query is :
#none-empty chunks or basically empty index files
#if it returns i dont know- when no reelvant conetnt acc to  threshold is found fom the chunks

#results - list of dictionaries of inidvidual metadata

#ye sab filhal ke reference keliye b4 github clean this it is actually senseless here like ahh this shud be ab ratta right the command
# uvicorn <filename>:<api_object> --reload
#eg - uvicorn main:app --reload
#the parameter inside the get function denotes the path of api endpoint- extension path