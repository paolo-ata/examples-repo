# RAG System für Bauhaftpflicht-Fälle

## Overview

RAG (Retrieval-Augmented Generation) system for finding comparable construction liability cases. Combines the best approaches from `3_rag` (clean architecture) and `3a_rag` (better chunking, clean embeddings, Streamlit UI).

## Tech Stack

- Python 3.13+
- ChromaDB (local vector database)
- OpenAI embeddings (text-embedding-3-small)
- OpenAI LLM (gpt-4o-mini)
- LangChain for orchestration
- Streamlit for web UI

## Project Structure

```
4_rag/
├── pyproject.toml      # Dependencies
├── .env                # OpenAI API Key
├── config.py           # Central configuration
├── indexer.py          # Load documents → chunk → ChromaDB
├── retriever.py        # Search similar chunks (generic filter)
├── rag_chain.py        # Combine retrieval + LLM
├── app.py              # Streamlit web UI
├── tutorial.ipynb      # Beginner tutorial (German)
├── chroma_db/          # Persistent vector DB (generated)
└── CLAUDE.md           # This file
```

## Usage

```bash
# Install dependencies
uv sync

# Index all documents (run once)
uv run python indexer.py

# Ask questions via Streamlit
uv run streamlit run app.py
```

## Key Design Decisions

- **No metadata in chunk text**: page_content contains only the original document text. Metadata (case_id, cluster, etc.) is stored in the metadata dict. This keeps embedding vectors clean.
- **Metadata header at prompt time**: When building the LLM prompt, we prepend `[QUELLE: Fall W1 | Cluster: ... | CHF ...]` so the LLM knows the source.
- **RecursiveCharacterTextSplitter**: Splits at paragraph/sentence boundaries instead of fixed character positions.
- **Generic filter**: One `filter_dict` parameter instead of separate filter functions per field.
- **reset_collection()**: Clean re-index instead of manual delete.

## Data Source

Documents from `../2_syntetic_data/output/` with:
- case_bible.json per case (metadata)
- Document JSON files with content and metadata
