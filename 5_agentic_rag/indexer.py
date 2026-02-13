"""Indexer: Case-Bible-Daten in SQLite laden.

Liest alle case_bible.json-Dateien und erstellt zwei Tabellen:
- cases: Eine Zeile pro Fall (Metadaten, Beträge, Status)
- documents: Eine Zeile pro Dokument (Typ, Datum, Sprache)

Die ChromaDB (Vektor-Suche) wird weiterhin aus 4_rag genutzt.
Dieser Indexer erstellt nur die SQL-Datenbank für strukturierte Abfragen.
"""

import json
import sqlite3
from pathlib import Path

from config import DATA_PATH, SQLITE_PATH


def create_tables(db: sqlite3.Connection) -> None:
    """Tabellen erstellen (falls sie nicht existieren)."""
    db.executescript("""
        DROP TABLE IF EXISTS documents;
        DROP TABLE IF EXISTS cases;

        CREATE TABLE cases (
            case_id         TEXT PRIMARY KEY,
            sprache         TEXT,
            kanton          TEXT,
            gericht         TEXT,
            branche         TEXT,
            cluster         TEXT,
            vn              TEXT,
            g01             TEXT,
            sachverhalt     TEXT,
            forderung_brutto REAL,
            erwartete_min   REAL,
            erwartete_max   REAL,
            selbstbehalt    REAL,
            status          TEXT,
            normen          TEXT,
            anzahl_dokumente INTEGER
        );

        CREATE TABLE documents (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id  TEXT,
            doc_typ  TEXT,
            datum    TEXT,
            sprache  TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(case_id)
        );
    """)


def index_case(db: sqlite3.Connection, case_dir: Path) -> bool:
    """Einen Fall in die Datenbank schreiben. Gibt True zurück bei Erfolg."""
    bible_path = case_dir / "case_bible.json"
    if not bible_path.exists():
        return False

    with open(bible_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parteien = data.get("parteien", {})
    betraege = data.get("betraege", {})
    spanne = betraege.get("erwartete_spanne", {})
    recht = data.get("recht", {})
    normen = ", ".join(recht.get("normen", []))
    dok_plan = data.get("dokument_plan", [])

    db.execute(
        """INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("case_id"),
            data.get("sprache"),
            data.get("kanton"),
            data.get("gericht"),
            data.get("branche"),
            data.get("cluster"),
            parteien.get("vn"),
            parteien.get("g01"),
            data.get("sachverhalt", {}).get("kurz"),
            betraege.get("forderung_brutto"),
            spanne.get("min"),
            spanne.get("max"),
            betraege.get("sb"),
            data.get("status"),
            normen,
            len(dok_plan),
        ),
    )

    for dok in dok_plan:
        db.execute(
            "INSERT INTO documents (case_id, doc_typ, datum, sprache) VALUES (?, ?, ?, ?)",
            (data.get("case_id"), dok.get("typ"), dok.get("datum"), dok.get("sprache")),
        )

    return True


def index_all() -> int:
    """Alle Fälle indexieren. Gibt die Anzahl indexierter Fälle zurück."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Datenpfad nicht gefunden: {DATA_PATH}")

    db = sqlite3.connect(str(SQLITE_PATH))
    create_tables(db)

    count = 0
    for case_dir in sorted(DATA_PATH.iterdir()):
        if not case_dir.is_dir():
            continue
        if index_case(db, case_dir):
            print(f"  Indexiert: {case_dir.name}")
            count += 1

    db.commit()
    db.close()

    print(f"\n{count} Fälle in {SQLITE_PATH} gespeichert.")
    return count


if __name__ == "__main__":
    index_all()
