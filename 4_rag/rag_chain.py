"""RAG Chain: Retrieval + LLM für Frage-Antwort kombinieren."""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from config import LLM_MODEL, TOP_K
from retriever import search

load_dotenv()

SYSTEM_PROMPT = """Du bist ein Experte für Bauhaftpflicht-Fälle in der Schweiz.
Beantworte Fragen basierend auf den bereitgestellten Dokumenten.

Wichtige Regeln:
1. Antworte nur basierend auf den gegebenen Quellen
2. Wenn die Information nicht in den Quellen ist, sage das klar
3. Gib immer die Fall-ID(s) an, aus denen die Information stammt
4. Antworte auf Deutsch, auch wenn die Quellen auf Französisch sind
5. Sei präzise und strukturiert in deinen Antworten
6. Wenn du Beträge nennst, nutze das Format 'CHF 50'000'

Format deiner Antwort:
- Beginne mit einer direkten Antwort auf die Frage
- Führe relevante Details auf
- Ende mit den Quellen (Fall-IDs und Dokumenttypen)
"""


def build_prompt(query: str, chunks: list[tuple[Document, float]]) -> str:
    """Prompt mit abgerufenem Kontext bauen.

    Metadaten-Header werden hier zur Laufzeit hinzugefügt,
    damit das LLM weiss, woher die Info kommt, der Vektor aber sauber bleibt.
    """
    context_parts = []

    for doc, score in chunks:
        meta = doc.metadata
        header = (
            f"[QUELLE: Fall {meta.get('case_id', '?')} | "
            f"Cluster: {meta.get('cluster', '?')} | "
            f"CHF {meta.get('schaden_chf', '?')}]"
        )
        doc_info = (
            f"[DOKUMENT: {meta.get('doc_typ', '?')} vom {meta.get('doc_datum', '?')}]"
        )
        context_parts.append(
            f"{header}\n{doc_info}\nInhalt: {doc.page_content}"
        )

    context = "\n--------------------------------------------------\n".join(context_parts)

    return f"""Kontext aus der Falldatenbank:

{context}

---
Frage: {query}

Antwort:"""


def ask(
    query: str,
    k: int = TOP_K,
    filter_dict: dict | None = None,
    verbose: bool = False,
) -> dict:
    """Frage stellen und Antwort mit Quellen erhalten.

    Args:
        query: Die Frage
        k: Anzahl abzurufender Chunks
        filter_dict: Optionaler Metadaten-Filter
        verbose: Wenn True, Zwischenschritte ausgeben

    Returns:
        Dict mit 'answer', 'sources' und 'chunks'
    """
    if verbose:
        print(f"Rufe {k} relevante Chunks ab...")
        if filter_dict:
            print(f"Filter aktiv: {filter_dict}")

    chunks = search(query, k=k, filter_dict=filter_dict)

    if not chunks:
        return {
            "answer": "Keine relevanten Dokumente gefunden.",
            "sources": [],
            "chunks": [],
        }

    if verbose:
        print(f"{len(chunks)} Chunks gefunden")
        for doc, score in chunks:
            print(
                f"  - {doc.metadata.get('case_id')}/{doc.metadata.get('doc_typ')} "
                f"(Score: {score:.3f})"
            )

    prompt = build_prompt(query, chunks)

    if verbose:
        print(f"\nPrompt-Länge: {len(prompt)} Zeichen")

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    answer = response.content

    # Quellen-Deduplizierung
    sources = []
    seen = set()
    for doc, score in chunks:
        source_key = (doc.metadata.get("case_id"), doc.metadata.get("doc_typ"))
        if source_key not in seen:
            seen.add(source_key)
            sources.append({
                "case_id": doc.metadata.get("case_id"),
                "doc_typ": doc.metadata.get("doc_typ"),
                "doc_datum": doc.metadata.get("doc_datum"),
                "cluster": doc.metadata.get("cluster"),
            })

    return {
        "answer": answer,
        "sources": sources,
        "chunks": [(doc.page_content[:200], score) for doc, score in chunks],
    }


if __name__ == "__main__":
    test_queries = [
        "Gibt es Fälle mit Wasserabdichtungsproblemen?",
        "Welche SIA-Normen sind relevant?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Frage: {query}")
        print("=" * 60)

        result = ask(query, verbose=True)

        print(f"\nAntwort:\n{result['answer']}")
        print("\nQuellen:")
        for s in result["sources"]:
            print(f"  - Fall {s['case_id']}: {s['doc_typ']} ({s['doc_datum']})")
