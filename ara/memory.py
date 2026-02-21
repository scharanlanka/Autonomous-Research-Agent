import time
import chromadb
from chromadb.config import Settings

from ara.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION
from ara.azure_embeddings import AzureEmbeddings

class MemoryStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(name=CHROMA_COLLECTION)
        self.embedder = AzureEmbeddings()

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