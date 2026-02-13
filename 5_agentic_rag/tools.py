"""Tools für den Bauhaftpflicht-Agenten.

Jedes Tool ist eine Funktion, die der Agent aufrufen kann.
Der Agent sieht den Docstring und entscheidet selbst, wann er welches Tool nutzt.
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from agents import function_tool

from config import (
    EMBEDDING_MODEL,
    CHROMA_PATH,
    COLLECTION_NAME,
    DATA_PATH,
    TOP_K,
)

load_dotenv()


def _get_vectorstore() -> Chroma:
    """ChromaDB-Verbindung herstellen (interne Hilfsfunktion)."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH),
    )


# ---------------------------------------------------------------------------
# Tool 1: Semantische Suche
# ---------------------------------------------------------------------------
@function_tool
def vector_search(query: str, k: int = TOP_K, case_id: str = "") -> str:
    """Durchsucht die Falldatenbank nach semantisch ähnlichen Dokumenten.

    Nutze dieses Tool, wenn du nach inhaltlich ähnlichen Fällen,
    Argumentationen oder Sachverhalten suchst.
    Beispiel-Fragen: "Gab es Fälle mit undichten Duschen?",
    "Welche SIA-Normen wurden bei Wasserschäden angewendet?"

    Args:
        query: Die Suchanfrage in natürlicher Sprache.
        k: Anzahl Ergebnisse (Standard: 5).
        case_id: Optional — nur in diesem Fall suchen, z.B. "W1".
    """
    vectorstore = _get_vectorstore()
    filter_dict = {"case_id": case_id} if case_id else None

    results = vectorstore.similarity_search_with_score(
        query, k=k, filter=filter_dict
    )

    if not results:
        return "Keine relevanten Dokumente gefunden."

    parts = []
    for doc, score in results:
        meta = doc.metadata
        parts.append(
            f"[Fall {meta.get('case_id', '?')} | "
            f"{meta.get('doc_typ', '?')} | "
            f"{meta.get('doc_datum', '?')} | "
            f"Cluster: {meta.get('cluster', '?')} | "
            f"Score: {score:.3f}]\n"
            f"{doc.page_content[:500]}"
        )

    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Tool 2: Fall-Übersicht
# ---------------------------------------------------------------------------
@function_tool
def get_case_overview(case_id: str) -> str:
    """Lädt die Übersicht (case_bible.json) eines bestimmten Falls.

    Nutze dieses Tool, wenn du Details zu einem spezifischen Fall brauchst:
    Beteiligte, Schadenssumme, Status, Cluster, Zeitraum usw.

    Args:
        case_id: Die Fall-ID, z.B. "W1", "F2", "H3".
    """
    bible_path = DATA_PATH / case_id / "case_bible.json"
    if not bible_path.exists():
        return f"Fall '{case_id}' nicht gefunden."

    with open(bible_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 3: Alle Fälle auflisten
# ---------------------------------------------------------------------------
@function_tool
def list_cases(cluster: str = "") -> str:
    """Listet alle verfügbaren Fälle auf, optional gefiltert nach Cluster.

    Nutze dieses Tool für Übersichtsfragen wie:
    "Wie viele Fälle gibt es?", "Welche Fälle gehören zum Cluster Wasser?"

    Args:
        cluster: Optional — nur Fälle dieses Clusters anzeigen, z.B. "Wasser".
                 Sucht als Teilstring (Gross-/Kleinschreibung egal).
    """
    if not DATA_PATH.exists():
        return f"Datenpfad nicht gefunden: {DATA_PATH}"

    cases = []
    for case_dir in sorted(DATA_PATH.iterdir()):
        if not case_dir.is_dir():
            continue
        bible_path = case_dir / "case_bible.json"
        if not bible_path.exists():
            continue

        with open(bible_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        case_cluster = data.get("cluster", "")

        if cluster and cluster.lower() not in case_cluster.lower():
            continue

        status = data.get("status", "?")
        betraege = data.get("betraege", {})
        forderung = betraege.get("forderung_brutto", "?")

        cases.append(
            f"- {data.get('case_id', case_dir.name)}: "
            f"{case_cluster} | Status: {status} | CHF {forderung}"
        )

    if not cases:
        return "Keine Fälle gefunden."

    return f"{len(cases)} Fälle gefunden:\n\n" + "\n".join(cases)
