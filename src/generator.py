import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def generate_answer(question, retrieved_chunks):

    context_parts = []

    for chunk in retrieved_chunks:

        chunk_id, document_name, page_number, chunk_text, similarity = chunk

        context_parts.append(
            f"Document: {document_name}\n"
            f"Page: {page_number}\n"
            f"Content:\n{chunk_text}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are an enterprise document assistant.

Answer the user's question using ONLY the information provided
in the document context below.

If the answer cannot be found in the context, say:
"I could not find the answer in the provided documents."

Do not make up information.

Document context:
{context}

User question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]