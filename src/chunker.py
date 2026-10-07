def create_chunks(pages, document_name, chunk_size=500, overlap=100):

    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "document_name": document_name,
                "text": chunk_text,
                "page_number": page_number
            })

            start += chunk_size - overlap

    return chunks