import re
""""
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
import numpy as np

model=SentenceTransformer("all-MiniLM-L6-v2")

#to detect structure of the documents and perform semnatic chunking on the basis of structure
def detect_boundaries(text):
    lines = text.split('\n')
    boundaries = []
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if not line_strip:
            continue
        
        if (
            line_strip.isupper()
            or line_strip.endswith(':')
            or re.match(r'^\d+️⃣', line_strip) #line starting with numbered emoji(for  gpt docs lol)
            or re.match(r'^\d+[\.\)]\s+', line_strip) #starting with numbers
            or re.match(r'^[•●▪■◦–—\-*]\s+', line_strip) #sentence starting with bullets and symbols
        ):
            boundaries.append(idx)

    return boundaries, lines


#splitting the lines to sentences for similarity score check
nlp=spacy.load("en_core_web_sm")
def spilt_sentences(lines):
    sentences=[]
    for line in lines:
        doc=nlp(line) #the model applied on lines to processs the lines
        sentences.extend([sent.text.strip() for sent in doc.sents if sent.text.strip()])
    return sentences

def sliding_window_merge(sentences, threshold=0.7):
    if not sentences:
        return []

    embeddings = model.encode(sentences)
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        #checking the cosine similarity
        sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
        if sim >= threshold:
            current_chunk.append(sentences[i]) #if similarity socres nearby, append the sentence to the same chunk
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]] #new chunk for sentence with diff similarity score

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def cluster_sentences(sentences, n_clusters=None):
    if len(sentences) < 2:
        return sentences

    embeddings = model.encode(sentences)
    
    if not n_clusters: #chsoosing number of chunks
        n_clusters = max(1, len(sentences) // 5)  #5 sentences per cluster

    clustering = AgglomerativeClustering(n_clusters=n_clusters, metric='cosine', linkage='average')
    labels = clustering.fit_predict(embeddings)

    chunks = []
    for label in sorted(set(labels)):
        cluster_sents = [sentences[i] for i, l in enumerate(labels) if l == label]
        chunks.append(" ".join(cluster_sents))
    return chunks

def semantic_chunk_pipeline(doc_id, text, similarity_threshold=0.7, large_block_size=15, use_clustering=True):
    boundaries, lines = detect_boundaries(text)
    boundaries = sorted(set([0] + boundaries + [len(lines)]))
    all_chunks=[]
    chunk_id=0

    for i in range(len(boundaries)-1):
        segment_lines = lines[boundaries[i]:boundaries[i+1]]
        sentences =spilt_sentences(segment_lines)

        if not sentences:
            continue

        # If block is large, optionally use clustering for concept-level chunks
        if use_clustering and len(sentences) > large_block_size:
            segment_chunks = cluster_sentences(sentences) #returns list of chunks
            chunk_type="cluster chunking"
        else:
            segment_chunks = sliding_window_merge(sentences, threshold=similarity_threshold)#returns list of chunks
            chunk_type="cluster chunking"

        for chunk_text in segment_chunks: #for every chunk in the list return chunks in this  manner
            all_chunks.append({
                "id": chunk_id,
                "doc_id": doc_id,
                "text": chunk_text,
                "chunk_type": chunk_type
            })


            
            chunk_id=chunk_id+1 #next id for next chunk

    return all_chunks



"""
def analyze_document_structure(text:str):
    lines = []

    for l in text.splitlines():
        stripped = l.strip()
        if stripped:
            lines.append(stripped)
    
    word_count=len(text.split())
    headcount=0
    for line in lines:
        if len(lines)<80 and (line.isupper() or re.match(r"^\d+(\.\d+)*\s+[A-Z]", line)): 
            #the etxt inside the match function is like the grammar used to check and mtach if the text id like a title that is usually seen. i.e. matching the format of the txtt to the ususal platform of a ttile
            headcount=headcount+1
    
    paragraph_count = text.count("\n\n")
    avg_line_length = sum(len(l) for l in lines) / max(len(lines), 1)

    return {
        "word_count": word_count,
        "heading_count": headcount,
        "paragraph_count": paragraph_count,
        "avg_line_length": avg_line_length
    }

def choose_chunking_strategy(stats: dict, is_scanned):
    if stats["word_count"] < 400:
        return "single"

    if is_scanned:
        return "fixed amount of words every chunk"

    if stats["heading_count"] >= 3:
        return "hierarchical"

    if stats["paragraph_count"] >= 5:
        return "paragraph wise"

    return "fixed"

#chunking implementations
def single_chunk(text: str, doc_id: str):
    return [{
        "doc_id": doc_id,
        "chunk_index": 0,
        "text": text
    }]


def fixed(text, doc_id, max_chars=700, overlap=150):
    chunks=[]
    start = 0
    index = 0

    while start < len(text):
        end = start + max_chars
        chunk_text = text[start:end]

        chunks.append({
            "doc_id": doc_id,
            "chunk_index": index,
            "text": chunk_text
        })

        start = end - overlap
        index += 1

    return chunks

def paragraph(text, doc_id, max_chars=1500):
    paragraphs=[]
    for p in text.split("\n\n"):
        para=p.strip()
        if para:
            paragraphs.append(para)

    chunks=[]
    buffer=""
    index=0

    for p in paragraphs:
        if len(buffer)+len(p) <= max_chars:
            buffer += " "+p
        else:
            chunks.append({
                "doc_id": doc_id,
                "chunk_index": index,
                "text": buffer.strip()
            })
            buffer = p
            index=index+1

    if buffer:
        chunks.append({
            "doc_id": doc_id,
            "chunk_index": index,
            "text": buffer.strip()
        })
    return chunks

def split_into_sections(text: str):
    sections = []
    current_title = "Introduction"
    current_content = []

    for line in text.splitlines():
        line = line.strip()

        if (
            len(line) < 80
            and line.isupper()
            or re.match(r"^\d+(\.\d+)*\s+[A-Z]", line)
        ):
            if current_content:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_content)
                })
            current_title = line
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_content)
        })

    return sections

def split_into_paragraphs(section_text: str):
    paragraphs = [
        p.strip()
        for p in section_text.split("\n\n")
        if p.strip()
    ]
    return paragraphs

def split_into_sentences(paragraph: str):
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s.strip() for s in sentences if s.strip()]

def build_chunks(sentences, section_title, doc_id):
    chunks = []
    current_chunk = []
    chunk_index = 0

    for sentence in sentences:
        current_chunk.append(sentence)

        chunk_text = " ".join(current_chunk)

        if len(chunk_text) >= 1500:
            chunks.append({
                "doc_id": doc_id,
                "section": section_title,
                "chunk_index": chunk_index,
                "text": chunk_text
            })

            # overlap
            current_chunk = current_chunk[2:]
            chunk_index += 1

    if current_chunk:
        chunks.append({
            "doc_id": doc_id,
            "section": section_title,
            "chunk_index": chunk_index,
            "text": " ".join(current_chunk)
        })

    return chunks


def hierarchical_chunking(text: str, doc_id: str):
    all_chunks = []

    sections = split_into_sections(text)

    for section in sections:
        paragraphs = split_into_paragraphs(section["content"])

        for paragraph in paragraphs:
            sentences = split_into_sentences(paragraph)

            if not sentences:
                continue

            chunks = build_chunks(
                sentences,
                section["title"],
                doc_id
            )

            all_chunks.extend(chunks)

    return all_chunks

"""def recursive_chunk(text, max_size:int , level=0):
    
    Recursively chunk the text into smaller parts using a set of separators.
    
    Parameters:
    text (str): The input text to be chunked.
    max_size (int): The maximum desired chunk size.
    level (int): The current recursion level (used for debugging purposes).
    
    Returns:
    list: A list of text chunks.
    
    # Define separators for different levels of chunking
    separators = [r'(?<=[.!?]) +', r'\s+']  # Sentence level, word level

    # If the text is already within the max size, return it as a single chunk
    if len(text) <= max_size:
        return [text]

    # Select the appropriate separator based on the recursion level
    separator = separators[min(level, len(separators) - 1)]
    
    # Split the text using the selected separator
    chunks = re.split(separator, text)
    
    # If the number of chunks is too large, recursively split each chunk
    if any(len(chunk) > max_size for chunk in chunks):
        new_chunks = []
        for chunk in chunks:
            if len(chunk) > max_size:
                new_chunks.extend(recursive_chunk(chunk, max_size, level + 1))
            else:
                new_chunks.append(chunk)
        return new_chunks
    else:
        return chunks
"""

    
def adaptive_chunking(text: str, doc_id: str, is_scanned: bool):
    stats = analyze_document_structure(text)
    strategy =hierarchical_chunking(text, doc_id)

    print("Chunking strategy:", strategy)

    if strategy == "single":
        return single_chunk(text, doc_id)

    if strategy == "hierarchical":
        return hierarchical_chunking(text, doc_id)

    if strategy == "paragraph":
        return paragraph(text, doc_id)

    return fixed(text, doc_id)
