from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model():
    model = SentenceTransformer(MODEL_NAME)
    return model


def create_embeddings(model, chunks):
    embeddings = model.encode(chunks)
    return embeddings