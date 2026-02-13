"""Zentrale Konfiguration für das Agentic RAG-System."""

from pathlib import Path

# Pfade
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / ".." / "2_syntetic_data" / "output"
CHROMA_PATH = BASE_DIR / ".." / "4_rag" / "chroma_db"
SQLITE_PATH = BASE_DIR / "cases.db"

# Modelle
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# Retrieval
TOP_K = 5

# ChromaDB
COLLECTION_NAME = "bauhaftpflicht_cases"
