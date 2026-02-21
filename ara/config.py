from pathlib import Path
from dotenv import load_dotenv

# Always load .env from project root (../.env relative to this file)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
import os

def env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val

AZURE_LLM_ENDPOINT = env("AZURE_LLM_ENDPOINT")
AZURE_LLM_API_KEY = env("AZURE_LLM_API_KEY", "")
AZURE_LLM_DEPLOYMENT_NAME = env("AZURE_LLM_DEPLOYMENT_NAME", "grok-3-mini")

AZURE_EMBEDDING_ENDPOINT = env("AZURE_EMBEDDING_ENDPOINT")
AZURE_EMBEDDING_API_KEY = env("AZURE_EMBEDDING_API_KEY", "")
AZURE_EMBEDDING_DEPLOYMENT_NAME = env("AZURE_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large")

CHROMA_PERSIST_DIR = env("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION = env("CHROMA_COLLECTION", "ara_memory")

DDG_MAX_RESULTS = int(env("DDG_MAX_RESULTS", "8"))
ARXIV_MAX_RESULTS = int(env("ARXIV_MAX_RESULTS", "5"))
FETCH_MAX_CHARS = int(env("FETCH_MAX_CHARS", "12000"))

TAVILY_API_KEY = env("TAVILY_API_KEY")
TAVILY_MAX_RESULTS = int(env("TAVILY_MAX_RESULTS", "8"))