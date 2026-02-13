"""Tools für den Bauhaftpflicht-Agenten.

Jedes Tool ist eine Funktion, die der Agent aufrufen kann.
Der Agent sieht den Docstring und entscheidet selbst, wann er welches Tool nutzt.

Architektur:
- vector_search      → ChromaDB  (für inhaltliche/semantische Fragen)
- get_case_overview   → JSON-Dateien (für Detail-Ansicht eines Falls)
- sql_query          → SQLite    (für strukturierte Analysen, Zählungen, Vergleiche)
"""

import json
import sqlite3

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from agents import function_tool

from config import (
    EMBEDDING_MODEL,
    CHROMA_PATH,
    COLLECTION_NAME,
    DATA_PATH,
    SQLITE_PATH,
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
# Tool 1: Semantische Suche (ChromaDB)
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
# Tool 2: Fall-Übersicht (JSON)
# ---------------------------------------------------------------------------
@function_tool
def get_case_overview(case_id: str) -> str:
    """Lädt die Übersicht (case_bible.json) eines bestimmten Falls.

    Nutze dieses Tool, wenn du Details zu einem spezifischen Fall brauchst:
    Beteiligte, Schadenssumme, Status, Cluster, Zeitraum, Zeitleiste usw.

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
# Tool 3: SQL-Abfrage (SQLite)
# ---------------------------------------------------------------------------
@function_tool
def sql_query(query: str) -> str:
    """Führt eine SQL-Abfrage auf den strukturierten Fall-Metadaten aus.

    Nutze dieses Tool für Zählungen, Summen, Durchschnitte, Gruppierungen
    und strukturierte Filter. NICHT für inhaltliche Fragen — dafür nutze
    vector_search.

    Verfügbare Tabellen und Spalten:

    Tabelle 'cases':
        case_id, sprache, kanton, gericht, branche, cluster,
        vn (Versicherungsnehmer), g01 (Gegner),
        sachverhalt (Kurzbeschreibung),
        forderung_brutto, erwartete_min, erwartete_max, selbstbehalt,
        status (z.B. 'vergleich', 'prozess', 'offen'),
        normen (kommasepariert, z.B. 'SIA 118, OR 371'),
        anzahl_dokumente

    Tabelle 'documents':
        id, case_id, doc_typ, datum, sprache

    Beispiel-Queries:
        SELECT COUNT(*) FROM cases
        SELECT cluster, COUNT(*) as anzahl, AVG(forderung_brutto) as avg_betrag FROM cases GROUP BY cluster
        SELECT case_id, forderung_brutto FROM cases WHERE status = 'prozess' ORDER BY forderung_brutto DESC
        SELECT case_id, COUNT(*) as docs FROM documents GROUP BY case_id
        SELECT DISTINCT doc_typ FROM documents

    WICHTIG: Nur SELECT-Abfragen sind erlaubt.

    Args:
        query: Die SQL-Abfrage (nur SELECT).
    """
    if not SQLITE_PATH.exists():
        return "Datenbank nicht gefunden. Bitte zuerst 'python indexer.py' ausführen."

    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return "Fehler: Nur SELECT-Abfragen sind erlaubt."

    db = sqlite3.connect(str(SQLITE_PATH))
    db.row_factory = sqlite3.Row
    try:
        cursor = db.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return "Keine Ergebnisse."

        # Spalten-Namen holen
        columns = [desc[0] for desc in cursor.description]
        # Formatierte Ausgabe
        lines = [" | ".join(columns)]
        lines.append("-" * len(lines[0]))
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))

        return "\n".join(lines)
    except Exception as e:
        return f"SQL-Fehler: {e}"
    finally:
        db.close()
