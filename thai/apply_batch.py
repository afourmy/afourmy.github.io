"""Apply free-form `decisions` file batch 2 — 23 cards (14 edits, 9 deletes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # english only
    "wlt-c01-060": {"english": "to chat together"},
    "wlt-c01-078": {"english": "these days, lately"},
    "wlt-c02-016": {"english": "at night, during the night"},
    "wlt-c02-017": {"english": "in the evening (around dusk)"},
    "wlt-c02-051": {"english": "to go travelling, to travel for pleasure"},
    "wlt-c03-013": {"english": "often, frequently"},
    "wlt-c03-023": {"english": "what type?"},
    "wlt-c03-042": {"english": "to be worried, to be concerned about"},
    "wlt-c03-085": {"english": "to have an appointment"},
    "wlt-c03-094": {"english": "the day before yesterday"},
    "wlt-c04-020": {"english": "sandals, flip-flops"},
    "wlt-c04-093": {"english": "doctor"},
    # frequency only
    "t4k-c01-085": {"frequency": "everyday"},
    # merge survivor (wlt-c03-090 เมื่อกี้ merged in here, then deleted below)
    "tamago-l12-551": {
        "thai": "เมื่อกี้, เมื่อกี้นี้, เมื่อตะกี้นี้",
        "english": "just now, a moment ago",
        "frequency": "everyday",
    },
}

DELETES = {
    "wlt-c01-070", "wlt-c02-067", "wlt-c03-068", "wlt-c04-027", "wlt-c04-031",
    "wlt-c04-032", "wlt-c04-095",
    "wlt-c03-057",  # พบกัน dup of wlt-c18-096 (delete dup only)
    "wlt-c03-090",  # merged into tamago-l12-551
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
        "Free-form decisions file batch 2 — 23 cards (14 edits, 9 deletes)", "",
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
