import logging
import os
import time
from pathlib import Path

# Disable Chroma telemetry before importing chromadb to avoid noisy telemetry errors
# when local dependency versions (e.g., posthog/opentelemetry) are incompatible.
# Also remove previously-set invalid overrides from earlier app versions.
os.environ.pop("CHROMA_PRODUCT_TELEMETRY_IMPL", None)
os.environ.pop("CHROMA_TELEMETRY_IMPL", None)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "FALSE")

import chromadb
from chromadb.config import Settings

from ara.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION
from ara.azure_embeddings import AzureEmbeddings

# Suppress telemetry logger noise if Chroma still tries to initialize telemetry.
for _logger_name in (
    "chromadb.telemetry.product.posthog",
    "chromadb.telemetry",
    "posthog",
):
    logging.getLogger(_logger_name).setLevel(logging.CRITICAL)

_SHARED_CLIENT = None
_SHARED_COLLECTION = None
_SHARED_EMBEDDER = None


def _chroma_path() -> str:
    # Use a stable absolute path so Chroma's shared client cache keys don't drift.
    return str(Path(CHROMA_PERSIST_DIR).expanduser().resolve())


def _build_settings() -> Settings:
    return Settings(anonymized_telemetry=False)


def _create_persistent_client():
    path = _chroma_path()
    settings = _build_settings()
    try:
        return chromadb.PersistentClient(path=path, settings=settings)
    except ValueError as e:
        msg = str(e)
        if "already exists" not in msg or "different settings" not in msg:
            raise

        # Streamlit reruns can reuse the in-process Chroma shared system cache.
        # Clear it and recreate with the current settings.
        try:
            from chromadb.api.client import SharedSystemClient  # type: ignore

            clear_fn = getattr(SharedSystemClient, "clear_system_cache", None)
            if callable(clear_fn):
                clear_fn()
                return chromadb.PersistentClient(path=path, settings=settings)
        except Exception:
            pass

        # Last resort: attach with default settings for the existing shared instance.
        return chromadb.PersistentClient(path=path)


class MemoryStore:
    def __init__(self):
        global _SHARED_CLIENT, _SHARED_COLLECTION, _SHARED_EMBEDDER

        if _SHARED_CLIENT is None:
            _SHARED_CLIENT = _create_persistent_client()
        if _SHARED_COLLECTION is None:
            _SHARED_COLLECTION = _SHARED_CLIENT.get_or_create_collection(name=CHROMA_COLLECTION)
        if _SHARED_EMBEDDER is None:
            _SHARED_EMBEDDER = AzureEmbeddings()

        self.client = _SHARED_CLIENT
        self.collection = _SHARED_COLLECTION
        self.embedder = _SHARED_EMBEDDER

    def add(self, texts: list[str], metadatas: list[dict], ids: list[str]) -> None:
        embeddings = self.embedder.embed(texts)
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(self, query: str, k: int = 5) -> list[str]:
        q_emb = self.embedder.embed([query])[0]
        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=k,
            include=["documents", "metadatas"],
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        out = []
        for d, m in zip(docs, metas):
            src = m.get("source", "memory")
            ts = m.get("timestamp", "")
            out.append(f"[{src} | {ts}] {d}")
        return out

def make_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time()*1000)}"
