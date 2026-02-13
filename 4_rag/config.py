"""Zentrale Konfiguration für das RAG-System."""

from pathlib import Path

# Pfade
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / ".." / "2_syntetic_data" / "output"
CHROMA_PATH = BASE_DIR / "chroma_db"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Modelle
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# Retrieval
TOP_K = 5

# ChromaDB
COLLECTION_NAME = "bauhaftpflicht_cases"
