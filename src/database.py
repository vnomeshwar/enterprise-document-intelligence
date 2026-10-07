import os
import pg8000

from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = pg8000.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT"))
    )

    return connection

def insert_chunk(document_name, page_number, chunk_text, embedding):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO document_chunks
        (document_name, page_number, chunk_text, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        (
            document_name,
            page_number,
            chunk_text,
            str(embedding.tolist())
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


def search_similar_chunks(query_embedding, query_text, top_k=3):

    connection = get_connection()
    cursor = connection.cursor()

    query_vector = str(query_embedding.tolist())

    cursor.execute(
        """
        SELECT
            id,
            document_name,
            page_number,
            chunk_text,

            (
                0.7 * (1 - (embedding <=> %s::vector))
                +
                0.3 * ts_rank_cd(
                    to_tsvector('english', chunk_text),
                    plainto_tsquery('english', %s)
                )
            ) AS similarity

        FROM document_chunks

        ORDER BY similarity DESC

        LIMIT %s
        """,
        (
            query_vector,
            query_text,
            top_k
        )
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

def replace_document_chunks(document_name, chunks, embeddings):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Remove the previous version of this document
        cursor.execute(
            """
            DELETE FROM document_chunks
            WHERE document_name = %s
            """,
            (document_name,)
        )

        # Insert the current version
        for chunk, embedding in zip(chunks, embeddings):

            cursor.execute(
                """
                INSERT INTO document_chunks
                (document_name, page_number, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    chunk["document_name"],
                    chunk["page_number"],
                    chunk["text"],
                    str(embedding.tolist())
                )
            )

        # Save all changes together
        connection.commit()

    except Exception:
        # If anything fails, undo the whole operation
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()