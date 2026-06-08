"""Apply free-form `decisions` file batch 4 — 39 cards (37 edits, 2 deletes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "wlt-c11-077": {"english": "wife, long-term girlfriend (informal)"},
    "wlt-c11-086": {"english": "unwell"},
    "wlt-c11-094": {"english": "to wait"},
    "wlt-c12-011": {"english": "lower, bottom"},
    "wlt-c12-019": {"english": "to stop, end, quit, break up"},
    "wlt-c12-032": {"english": "to feel well, to be okay"},
    "wlt-c12-066": {"english": "to break, to fracture; to deduct, to subtract"},
    "wlt-c12-068": {"english": "hungry"},
    "wlt-c12-075": {"english": "dry"},
    "wlt-c13-005": {"english": "to drive a car"},
    "wlt-c13-007": {"english": "news"},
    "wlt-c13-016": {"english": "dusk (6 pm - 7 pm)"},
    "wlt-c13-019": {"english": "to talk, to chat"},
    "wlt-c13-021": {"english": "quiet"},
    "wlt-c13-024": {"english": "to catch, to grab"},
    "wlt-c13-038": {"english": "soon, in a short while"},
    "wlt-c13-040": {"english": "right, OK, to agree (to something)"},
    "wlt-c13-041": {"english": "straight ahead, go straight"},
    "wlt-c13-055": {"english": "bag"},
    "wlt-c13-068": {"english": "all of it, the whole"},
    "wlt-c13-072": {"english": "address, place of residence"},
    "wlt-c13-077": {"english": "you, she (informal, usually feminine)"},
    "wlt-c14-013": {"english": "wrong, incorrect, mistaken"},
    "wlt-c14-020": {"english": "song"},
    "wlt-c14-021": {"english": "to lose (e.g. in a game); allergic to"},
    "wlt-c14-025": {"english": "boyfriend, girlfriend, partner"},
    "wlt-c14-041": {"english": "grandmother (mother's mother)"},
    "wlt-c14-049": {"english": "to cry"},
    "wlt-c14-054": {"english": "to hurry"},
    "wlt-c14-057": {"english": "to reduce, to lower; to discount"},
    "wlt-c14-068": {"english": "glasses"},
    "wlt-c14-088": {"english": "clothes"},
    "wlt-c14-036": {"english": "it's okay, no problem, never mind"},
    # inner quotes kept per user
    "wlt-c14-035": {"english": "no, 'that's not it'"},
    "wlt-c13-031": {"english": "to invite someone to do sth (polite request: 'please...')"},
    "wlt-c13-017": {"english": "to miss someone (lit. 'think about')"},
    "wlt-c13-008": {"english": "poop; (of a person) habitually prone to (usually negative trait)"},
}

DELETES = {
    "wlt-c12-040", "wlt-c14-009",
}
PARKS = set()

APPLIED_ROW_IDS = set()


def main():
    vocab_path = HERE / "vocab.json"
    decisions_path = HERE / "decisions.json"
    parked_path = HERE / "parked.json"
    log_path = HERE / "apply_log.txt"

    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in vocab}

    applied = []
    skipped = []
    for eid, fields in EDITS.items():
        if eid not in by_id:
            skipped.append(eid)
            continue
        for k, v in fields.items():
            by_id[eid][k] = v
        applied.append((eid, fields))

    parked = [by_id[eid] for eid in PARKS if eid in by_id]
    parked_doc = json.loads(parked_path.read_text(encoding="utf-8"))
    for entry in parked:
        parked_doc["entries"].append(entry)
    parked_path.write_text(
        json.dumps(parked_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    remove_ids = DELETES | PARKS
    deleted = [eid for eid in DELETES if eid in by_id]
    new_vocab = [e for e in vocab if e["id"] not in remove_ids]

    log_lines = [
        "", "=" * 70,
        "Free-form decisions file batch 4 — 39 cards (37 edits, 2 deletes)", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    if deleted:
        for eid in deleted:
            log_lines.append(f"    delete {eid}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total field edits: {sum(len(f) for _, f in applied)}")
    log_lines.append(f"Deletions: {len(deleted)}")
    log_lines.append(f"Vocab: {len(vocab)} -> {len(new_vocab)}")
    log_lines.append("")

    existing_log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing_log + "\n".join(log_lines) + "\n", encoding="utf-8")

    backup = vocab_path.with_suffix(".json.bak")
    shutil.copy2(vocab_path, backup)
    vocab_path.write_text(
        json.dumps(new_vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    doc = json.loads(decisions_path.read_text(encoding="utf-8"))
    before = len(doc["rows"])
    doc["rows"] = [r for r in doc["rows"] if r["row_id"] not in APPLIED_ROW_IDS]
    doc["total_rows"] = len(doc["rows"])
    decisions_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Applied {sum(len(f) for _, f in applied)} field edits")
    print(f"Deleted: {deleted}")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
