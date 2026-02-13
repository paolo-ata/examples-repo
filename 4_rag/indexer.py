"""Indexer: Dokumente laden, chunken und in ChromaDB speichern."""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    DATA_PATH,
    CHROMA_PATH,
    COLLECTION_NAME,
)

load_dotenv()


def load_case_bible(case_dir: Path) -> dict | None:
    """Lade case_bible.json aus einem Fall-Ordner."""
    bible_path = case_dir / "case_bible.json"
    if not bible_path.exists():
        return None
    with open(bible_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_documents(case_dir: Path) -> list[tuple[dict, str]]:
    """Lade alle Dokument-JSONs aus einem Fall-Ordner.

    Returns:
        Liste von (doc_data, filename) Tupeln.
    """
    documents = []
    for doc_path in sorted(case_dir.glob("*.json")):
        if doc_path.name == "case_bible.json":
            continue
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_data = json.load(f)
        documents.append((doc_data, doc_path.name))
    return documents


def get_all_case_dirs() -> list[Path]:
    """Alle Fall-Ordner aus dem Datenpfad holen."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Datenpfad nicht gefunden: {DATA_PATH}")
    case_dirs = [d for d in DATA_PATH.iterdir() if d.is_dir()]
    return sorted(case_dirs)


def index_all_cases() -> int:
    """Alle Fälle in ChromaDB indexieren. Gibt die Anzahl indexierter Chunks zurück."""
    print(f"Lade Dokumente aus: {DATA_PATH.resolve()}")
    print(f"Speichere Vektoren in: {CHROMA_PATH.resolve()}")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH),
    )

    # Alte Daten löschen für sauberen Neustart
    vectorstore.reset_collection()

    all_documents = []
    case_dirs = get_all_case_dirs()
    print(f"Gefundene Fälle: {len(case_dirs)}")

    for case_dir in case_dirs:
        case_bible = load_case_bible(case_dir)
        if not case_bible:
            print(f"  Überspringe {case_dir.name}: keine case_bible.json")
            continue

        documents = load_documents(case_dir)
        print(f"  Verarbeite {case_dir.name}: {len(documents)} Dokumente")

        for doc_data, filename in documents:
            content = doc_data.get("content", "")
            metadata = doc_data.get("metadata", {})

            if not content:
                continue

            # Nur reiner Text als page_content — keine Metadaten im Chunk!
            doc = Document(
                page_content=content,
                metadata={
                    "case_id": case_bible.get("case_id", ""),
                    "cluster": case_bible.get("cluster", ""),
                    "doc_typ": metadata.get("typ", ""),
                    "doc_datum": metadata.get("datum", ""),
                    "sprache": metadata.get("sprache", ""),
                    "schaden_chf": case_bible.get("betraege", {}).get("forderung_brutto", 0),
                    "status": case_bible.get("status", ""),
                    "source_file": filename,
                },
            )
            all_documents.append(doc)

    # RecursiveCharacterTextSplitter für intelligentes Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    splits = text_splitter.split_documents(all_documents)

    if splits:
        print(f"\nIndexiere {len(splits)} Chunks...")
        vectorstore.add_documents(splits)
        print("Fertig!")
    else:
        print("Keine Dokumente zum Indexieren gefunden.")

    return len(splits)


if __name__ == "__main__":
    count = index_all_cases()
    print(f"\n{count} Chunks indexiert.")
