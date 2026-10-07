import pymupdf


def extract_pages_from_pdf(file_path):
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page_number": page_number + 1,
                "text": text
            })

    document.close()

    return pages