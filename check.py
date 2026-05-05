from backend.pdf_extraction import extract_text_and_type

pdf_path = "test.pdf"  # path to your PDF

text, is_scanned = extract_text_and_type(pdf_path)

print("Is scanned PDF:", is_scanned)
print("Extracted text preview:")
print(text[:500])  # first 500 characters
