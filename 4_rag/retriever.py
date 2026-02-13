"""Retriever: Ähnliche Chunks in ChromaDB suchen."""

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from config import EMBEDDING_MODEL, CHROMA_PATH, COLLECTION_NAME, TOP_K

load_dotenv()


def get_vectorstore() -> Chroma:
    """ChromaDB-Verbindung herstellen."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH),
    )


def search(
    query: str,
    k: int = TOP_K,
    filter_dict: dict | None = None,
) -> list[tuple[Document, float]]:
    """Generische Suche mit optionalem Metadaten-Filter.

    Args:
        query: Die Suchanfrage
        k: Anzahl Ergebnisse
        filter_dict: Optionaler Filter, z.B. {"case_id": "W1"} oder {"cluster": "..."}

    Returns:
        Liste von (Document, score) Tupeln
    """
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search_with_score(
        query,
        k=k,
        filter=filter_dict,
    )


def get_collection_stats() -> dict:
    """Statistiken über die indexierte Collection."""
    vectorstore = get_vectorstore()
    try:
        count = vectorstore._collection.count()
        return {
            "total_chunks": count,
            "collection_name": COLLECTION_NAME,
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    stats = get_collection_stats()
    print(f"Collection-Statistiken: {stats}")

    if stats.get("total_chunks", 0) > 0:
        print("\nTestsuche: 'Wasseraustritt'")
        results = search("Wasseraustritt", k=3)
        for i, (doc, score) in enumerate(results):
            print(f"\n--- Ergebnis {i + 1} (Score: {score:.3f}) ---")
            print(f"Fall: {doc.metadata.get('case_id')}")
            print(f"Cluster: {doc.metadata.get('cluster')}")
            print(f"Inhalt: {doc.page_content[:200]}...")
