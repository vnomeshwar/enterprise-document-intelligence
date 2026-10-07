from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import logging

from src.generator import generate_answer
from src.embedding import load_embedding_model
from src.document_loader import extract_pages_from_pdf
from src.chunker import create_chunks
from src.database import (
    search_similar_chunks,
    replace_document_chunks
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()


# Load embedding model once when API starts
embedding_model = load_embedding_model()


class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Processing document: {file.filename}")

    try:
        os.makedirs("documents", exist_ok=True)

        file_path = os.path.join(
            "documents",
            file.filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        pages = extract_pages_from_pdf(file_path)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        chunks = create_chunks(
            pages,
            file.filename
        )

        chunk_texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_model.encode(
            chunk_texts
        )

        replace_document_chunks(
            file.filename,
            chunks,
            embeddings
        )

        return {
            "message": "Document processed successfully",
            "filename": file.filename,
            "pages_extracted": len(pages),
            "chunks_created": len(chunks),
            "embedding_dimension": embeddings.shape[1]
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            f"Document processing failed: {file.filename}"
        )

        raise HTTPException(
            status_code=500,
            detail="Document processing failed."
        )

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    logger.info(
        f"Question received: {request.question}"
    )

    try:
        query_embedding = embedding_model.encode(
            [request.question]
        )[0]

        results = search_similar_chunks(
            query_embedding,
            request.question,
            top_k=3
        )

        MIN_SIMILARITY = 0.20

        relevant_results = [
            result
            for result in results
            if result[4] >= MIN_SIMILARITY
        ]

        if not relevant_results:
            return {
                "question": request.question,
                "answer": (
                    "I could not find the answer "
                    "in the provided documents."
                ),
                "sources": []
            }

        answer = generate_answer(
            question=request.question,
            retrieved_chunks=relevant_results
        )

        sources = []
        seen_sources = set()

        for result in relevant_results:
            document = result[1]
            page = result[2]
            similarity = result[4]

            source_key = (document, page)

            if source_key not in seen_sources:
                sources.append({
                    "document": document,
                    "page": page,
                    "similarity": round(
                        similarity,
                        4
                    )
                })

                seen_sources.add(source_key)

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except Exception:
        logger.exception(
            "Question processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process the question."
        )