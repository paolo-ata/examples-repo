from __future__ import annotations

import json
from pathlib import Path

import config
from generator import generate_document
from models import CaseBible, DocumentProgress
from prompts import SYSTEM_PROMPTS, build_user_prompt, get_template


def load_case_bibles() -> list[CaseBible]:
    """Load all case bibles from the JSON file."""
    with open(config.CASE_BIBLES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CaseBible(**cb) for cb in data]


def load_progress() -> dict[str, dict[int, str]]:
    """Load progress from file. Returns {case_id: {doc_index: status}}."""
    if config.PROGRESS_FILE.exists():
        with open(config.PROGRESS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # Convert string keys back to int
        return {
            case_id: {int(k): v for k, v in docs.items()}
            for case_id, docs in raw.items()
        }
    return {}


def save_progress(progress: dict[str, dict[int, str]]) -> None:
    """Save progress to file."""
    with open(config.PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def generate_case(case_bible: CaseBible, model: str, progress: dict[str, dict[int, str]]) -> dict:
    """Generate all documents for a single case. Returns stats."""
    case_id = case_bible.case_id
    case_dir = config.OUTPUT_DIR / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    # Save case bible to output
    case_bible_path = case_dir / "case_bible.json"
    with open(case_bible_path, "w", encoding="utf-8") as f:
        json.dump(case_bible.model_dump(), f, indent=2, ensure_ascii=False)

    if case_id not in progress:
        progress[case_id] = {}

    stats = {"generated": 0, "skipped": 0, "failed": 0}
    case_dict = case_bible.model_dump()

    for i, doc_entry in enumerate(case_bible.dokument_plan):
        doc_entry_dict = doc_entry.model_dump()

        # Check if already completed
        if progress[case_id].get(i) == "completed":
            stats["skipped"] += 1
            continue

        sprache = doc_entry.sprache
        system_prompt = SYSTEM_PROMPTS.get(sprache, SYSTEM_PROMPTS["DE"])
        template = get_template(doc_entry.typ)
        user_prompt = build_user_prompt(case_dict, doc_entry_dict, template)

        doc_id = f"{case_id}_{i+1:02d}_{doc_entry.typ}"
        print(f"  [{i+1}/{len(case_bible.dokument_plan)}] {doc_id}...", end=" ", flush=True)

        try:
            content = generate_document(system_prompt, user_prompt, model=model)

            # Build metadata
            metadata = {
                "case_id": case_id,
                "doc_id": doc_id,
                "typ": doc_entry.typ,
                "datum": doc_entry.datum,
                "sprache": sprache,
                "case_cluster": case_bible.cluster,
                "case_branche": case_bible.branche,
                "case_status": case_bible.status,
                "kanton": case_bible.kanton,
                "normen": case_bible.recht.normen,
                "forderung_brutto": case_bible.betraege.forderung_brutto,
                "model_used": model,
            }

            # Save document
            doc_filename = f"{i+1:02d}_{doc_entry.datum}_{doc_entry.typ}.json"
            doc_path = case_dir / doc_filename
            with open(doc_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"content": content, "metadata": metadata},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            progress[case_id][i] = "completed"
            save_progress(progress)
            stats["generated"] += 1
            print("OK")

        except Exception as e:
            progress[case_id][i] = "failed"
            save_progress(progress)
            stats["failed"] += 1
            print(f"FEHLER: {e}")

    return stats


def run_all(model: str) -> None:
    """Generate documents for all cases."""
    case_bibles = load_case_bibles()
    progress = load_progress()

    print(f"Starte Generierung fuer {len(case_bibles)} Faelle mit Modell '{model}'")
    print(f"Output-Verzeichnis: {config.OUTPUT_DIR}")
    print()

    total_stats = {"generated": 0, "skipped": 0, "failed": 0}

    for cb in case_bibles:
        total_docs = len(cb.dokument_plan)
        completed = sum(1 for v in progress.get(cb.case_id, {}).values() if v == "completed")
        if completed == total_docs:
            print(f"[{cb.case_id}] Alle {total_docs} Dokumente bereits vorhanden, uebersprungen.")
            total_stats["skipped"] += total_docs
            continue

        print(f"[{cb.case_id}] {cb.cluster} ({cb.sprache}, {cb.kanton}) – {total_docs} Dokumente")
        stats = generate_case(cb, model, progress)
        for k in total_stats:
            total_stats[k] += stats[k]
        print()

    print("=" * 60)
    print(f"Fertig! Generiert: {total_stats['generated']}, "
          f"Uebersprungen: {total_stats['skipped']}, "
          f"Fehlgeschlagen: {total_stats['failed']}")


def run_single(case_id: str, model: str) -> None:
    """Generate documents for a single case."""
    case_bibles = load_case_bibles()
    progress = load_progress()

    cb = next((c for c in case_bibles if c.case_id == case_id), None)
    if cb is None:
        available = ", ".join(c.case_id for c in case_bibles)
        print(f"Fall '{case_id}' nicht gefunden. Verfuegbar: {available}")
        return

    print(f"[{cb.case_id}] {cb.cluster} ({cb.sprache}, {cb.kanton})")
    print(f"Modell: {model}")
    print()

    stats = generate_case(cb, model, progress)
    print()
    print(f"Fertig! Generiert: {stats['generated']}, "
          f"Uebersprungen: {stats['skipped']}, "
          f"Fehlgeschlagen: {stats['failed']}")


def show_status() -> None:
    """Show generation progress."""
    case_bibles = load_case_bibles()
    progress = load_progress()

    print(f"{'Fall':<6} {'Cluster':<50} {'Status':<20}")
    print("-" * 76)

    total_docs = 0
    total_completed = 0
    total_failed = 0

    for cb in case_bibles:
        n_docs = len(cb.dokument_plan)
        case_progress = progress.get(cb.case_id, {})
        n_completed = sum(1 for v in case_progress.values() if v == "completed")
        n_failed = sum(1 for v in case_progress.values() if v == "failed")

        total_docs += n_docs
        total_completed += n_completed
        total_failed += n_failed

        if n_completed == n_docs:
            status = "fertig"
        elif n_completed == 0 and n_failed == 0:
            status = "ausstehend"
        else:
            status = f"{n_completed}/{n_docs} fertig"
            if n_failed > 0:
                status += f", {n_failed} fehlg."

        cluster_short = cb.cluster[:48]
        print(f"{cb.case_id:<6} {cluster_short:<50} {status:<20}")

    print("-" * 76)
    print(f"Total: {total_completed}/{total_docs} Dokumente generiert", end="")
    if total_failed > 0:
        print(f", {total_failed} fehlgeschlagen", end="")
    print()
