import pdfplumber

from docx import Document
import re


def extract_text_and_type(pdf_path: str, min_text_length: int = 100) -> tuple[str, bool]: #returns a list as [extracted test, scanned or not]
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    text = text.strip()
    if len(text) >= 100:
        return text, False
    
    else:
        return ("Still working on the deployement of scanned images via oce. Sorry will bw done soon", True)
    
def extract_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

#cleaning the text before storing

import os

def extract_raw_text(file_path: str) -> tuple[str, bool]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_and_type(file_path)  
    elif ext == ".docx":
        return extract_from_docx(file_path), False
    elif ext == ".txt":
        return extract_from_txt(file_path), False
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def split_into_lines(text: str):
    return text.splitlines() #you get a list of strings with lines as elements

def normalize_text(lines):
    normalize=[]
    for line in lines:
        line=line.strip() 
        line=re.sub(r"\s+ ", " ", line)
        normalize.append(line)
    return normalize # a list of lines with spaces thing solved

#removing lines with only numbers like pgno, or like just some numbers
def remove(lines):
    removed=[]
    for line in lines:
        if line.replace("/", "").isdigit()==False:  #checking if the whole one string=one line is a digit or wat
            removed.append(line)
    return removed

#removing repeated lines 
from collections import Counter 
def remove_repeated_lines(lines, repetition_threshold: float = 0.3):
    line_counts = Counter(lines)
    total_lines = len(lines)

    cleaned = []
    for line in lines:
        frequency = line_counts[line] / total_lines
        if frequency < repetition_threshold:
            cleaned.append(line)

    return cleaned

def rebuild_text(lines):
    return "\n".join(lines)#separating the lines inside the it by new line 

def cleaned_text(raw_text):
    lines=split_into_lines(raw_text)
    lines=normalize_text(lines)
    lines=remove(lines)
    lines=remove_repeated_lines(lines)
    return rebuild_text(lines)
