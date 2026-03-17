"""
Harvey OS – Vector Memory (FAISS + sentence-transformers)
Stores and retrieves strategic memories via semantic search.
"""

import pickle
from pathlib import Path

import numpy as np

from config.settings import EMBEDDING_MODEL, VECTOR_INDEX_FILE, VECTOR_STORE_FILE

# Lazy-loaded globals to avoid slow import at startup
_model = None
_index = None
_texts: list[str] = []


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _load_index():
    """Load FAISS index and text list from disk (if they exist)."""
    global _index, _texts
    import faiss

    if VECTOR_INDEX_FILE.exists() and VECTOR_STORE_FILE.exists():
        _index = faiss.read_index(str(VECTOR_INDEX_FILE))
        with open(VECTOR_STORE_FILE, "rb") as fh:
            _texts = pickle.load(fh)
    else:
        dim = _get_model().get_sentence_embedding_dimension()
        _index = faiss.IndexFlatL2(dim)
        _texts = []


def _save_index():
    """Persist FAISS index and text list to disk."""
    import faiss

    VECTOR_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(_index, str(VECTOR_INDEX_FILE))
    with open(VECTOR_STORE_FILE, "wb") as fh:
        pickle.dump(_texts, fh)


def _ensure_loaded():
    """Make sure the index is in memory."""
    if _index is None:
        _load_index()


# ── Public API ──────────────────────────────────────────────────────────────

def add_memory(text: str) -> None:
    """Encode *text* and add it to the vector store."""
    _ensure_loaded()
    embedding = _get_model().encode([text])
    _index.add(np.array(embedding, dtype=np.float32))
    _texts.append(text)
    _save_index()


def search_memory(query: str, top_k: int = 3) -> list[str]:
    """Return the *top_k* most relevant memories for *query*."""
    _ensure_loaded()
    if _index.ntotal == 0:
        return []
    embedding = _get_model().encode([query])
    k = min(top_k, _index.ntotal)
    _, indices = _index.search(np.array(embedding, dtype=np.float32), k)
    return [_texts[i] for i in indices[0] if 0 <= i < len(_texts)]


def memory_count() -> int:
    """Return the number of stored memories."""
    _ensure_loaded()
    return _index.ntotal
