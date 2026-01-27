import re

def load_text(text_path: str) -> str:
    with open(text_path, "r", encoding="utf-8") as f:
        return f.read()


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

        # Heuristic: heading detection
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
    
def adaptive_chunking(text: str, doc_id: str, is_scanned: bool):
    stats = analyze_document_structure(text)
    strategy = choose_chunking_strategy(stats, is_scanned)

    print("Chunking strategy:", strategy)

    if strategy == "single":
        return single_chunk(text, doc_id)

    if strategy == "hierarchical":
        return hierarchical_chunking(text, doc_id)

    if strategy == "paragraph":
        return paragraph(text, doc_id)

    return fixed(text, doc_id)

