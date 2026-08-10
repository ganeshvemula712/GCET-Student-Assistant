import threading

_model = None
_model_lock = threading.Lock()


def get_embedding_model():
    """
    Lazily initialize the SentenceTransformer model on first inference call.
    This keeps FastAPI startup RAM usage minimal (~120MB) so cloud deployments
    stay well within memory limits (e.g. Render 512MB Free tier).
    """
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                import torch
                # Restrict PyTorch CPU threads to reduce memory and thread overhead
                torch.set_num_threads(1)

                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text chunks into numerical vectors.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)

    return embeddings.tolist()