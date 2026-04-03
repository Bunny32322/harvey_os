"""
Harvey OS – Vector Memory (ChromaDB)
Upgraded from FAISS to ChromaDB for persistent, metadata-aware
semantic search. Supports temporal filtering, importance weighting,
and tagged retrieval.

NOTE: On low-memory environments (Render free tier), ChromaDB + 
sentence-transformers may fail to load. All functions gracefully 
degrade to return empty results instead of crashing.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from config.settings import DATA_DIR, EMBEDDING_MODEL

# ChromaDB persistence directory
CHROMA_DIR = DATA_DIR / "chromadb"

# ── Lazy-loaded globals ────────────────────────────────────────────────────
_client = None
_collection = None
_embed_fn = None
_available = None  # None = not checked yet, True/False after check


def _check_available() -> bool:
    """Check if ChromaDB + sentence-transformers can be loaded."""
    global _available
    if _available is not None:
        return _available
    try:
        import chromadb
        _available = True
    except ImportError:
        _available = False
    return _available


def _get_embed_fn():
    """Lazy-load the embedding function."""
    global _embed_fn
    if _embed_fn is None:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        _embed_fn = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return _embed_fn


def _get_collection():
    """Lazy-load the ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        import chromadb
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name="harvey_memories",
            embedding_function=_get_embed_fn(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ── Public API ──────────────────────────────────────────────────────────────

def add_memory(
    text: str,
    source: str = "general",
    importance: float = 5.0,
    tags: list[str] | None = None,
) -> str:
    """
    Encode and store a memory with metadata.
    Returns the memory ID (string), or empty string if unavailable.
    """
    if not _check_available():
        return ""
    try:
        collection = _get_collection()
        now = datetime.now().isoformat()
        mem_id = f"mem_{collection.count()}_{now.replace(':', '-')}"

        metadata = {
            "source": source,
            "importance": float(importance),
            "created_at": now,
            "tags": ",".join(tags) if tags else "",
        }

        collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[mem_id],
        )
        return mem_id
    except Exception:
        return ""


def search_memory(
    query: str,
    top_k: int = 3,
    source: str | None = None,
    min_importance: float = 0.0,
) -> list[dict]:
    """
    Semantic search for memories matching the query.
    Returns empty list if ChromaDB is unavailable.
    """
    if not _check_available():
        return []
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []

        # Build where filter
        where = None
        conditions = []
        if source:
            conditions.append({"source": {"$eq": source}})
        if min_importance > 0:
            conditions.append({"importance": {"$gte": min_importance}})

        if len(conditions) == 1:
            where = conditions[0]
        elif len(conditions) > 1:
            where = {"$and": conditions}

        k = min(top_k, collection.count())

        try:
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where,
            )
        except Exception:
            results = collection.query(
                query_texts=[query],
                n_results=k,
            )

        memories: list[dict] = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                entry = {
                    "text": doc,
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                }
                memories.append(entry)
        return memories
    except Exception:
        return []


def search_memory_text(query: str, top_k: int = 3) -> list[str]:
    """
    Backward-compatible: return just the text strings.
    """
    results = search_memory(query, top_k=top_k)
    return [r["text"] for r in results]


def memory_count() -> int:
    """Return the number of stored memories. 0 if unavailable."""
    if not _check_available():
        return 0
    try:
        collection = _get_collection()
        return collection.count()
    except Exception:
        return 0


def get_all_memories(limit: int = 100) -> list[dict]:
    """Retrieve all memories (for admin/debugging)."""
    if not _check_available():
        return []
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []
        results = collection.get(limit=limit, include=["documents", "metadatas"])
        memories = []
        for i, doc in enumerate(results["documents"]):
            memories.append({
                "id": results["ids"][i],
                "text": doc,
                "metadata": results["metadatas"][i] if results.get("metadatas") else {},
            })
        return memories
    except Exception:
        return []


def delete_memory(memory_id: str) -> bool:
    """Delete a specific memory by ID."""
    if not _check_available():
        return False
    try:
        collection = _get_collection()
        collection.delete(ids=[memory_id])
        return True
    except Exception:
        return False


# ── Migration helper ───────────────────────────────────────────────────────

def migrate_from_faiss() -> int:
    """
    One-time migration: read existing FAISS vector store
    and import texts into ChromaDB.
    Returns count of migrated memories.
    """
    if not _check_available():
        return 0

    import pickle
    from config.settings import VECTOR_STORE_FILE

    if not VECTOR_STORE_FILE.exists():
        return 0

    try:
        with open(VECTOR_STORE_FILE, "rb") as fh:
            texts = pickle.load(fh)
    except Exception:
        return 0

    if not texts:
        return 0

    count = 0
    for text in texts:
        if text and text.strip():
            add_memory(text, source="faiss_migration", importance=5.0)
            count += 1

    return count
