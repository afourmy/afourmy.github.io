"""Apply vocab review batch 14 — tamago-l12 frequency fixes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "tamago-l12-255": {"frequency": "occasional"},
    "tamago-l12-262": {"frequency": "occasional"},
    "tamago-l12-263": {"frequency": "occasional"},
    "tamago-l12-265": {"frequency": "occasional"},
    "tamago-l12-269": {"frequency": "rare"},
    "tamago-l12-279": {"frequency": "occasional"},
    "tamago-l12-285": {"frequency": "occasional"},
    "tamago-l12-288": {"frequency": "occasional"},
    "tamago-l12-293": {"frequency": "occasional"},
    "tamago-l12-294": {"frequency": "occasional"},
    "tamago-l12-295": {"frequency": "occasional"},
    "tamago-l12-304": {"frequency": "occasional"},
    "tamago-l12-315": {"frequency": "occasional"},
    "tamago-l12-316": {"frequency": "occasional"},
    "tamago-l12-322": {"frequency": "occasional"},
    "tamago-l12-324": {"frequency": "occasional"},
    "tamago-l12-349": {"frequency": "occasional"},
    "tamago-l12-356": {"frequency": "occasional"},
}

DELETES = set()
PARKS = set()

APPLIED_ROW_IDS = {
    "tamago-l12-255", "tamago-l12-262", "tamago-l12-263",
    "tamago-l12-264", "tamago-l12-265", "tamago-l12-269",
    "tamago-l12-279", "tamago-l12-282", "tamago-l12-285",
    "tamago-l12-288", "tamago-l12-293", "tamago-l12-294",
    "tamago-l12-295", "tamago-l12-301", "tamago-l12-304",
    "tamago-l12-307", "tamago-l12-313", "tamago-l12-315",
    "tamago-l12-316", "tamago-l12-320", "tamago-l12-322",
    "tamago-l12-324", "tamago-l12-326", "tamago-l12-330",
    "tamago-l12-332", "tamago-l12-340", "tamago-l12-344",
    "tamago-l12-349", "tamago-l12-350", "tamago-l12-356",
}


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
    skipped += [eid for eid in PARKS if eid not in by_id]

    parked_doc = json.loads(parked_path.read_text(encoding="utf-8"))
    for entry in parked:
        parked_doc["entries"].append(entry)
    parked_path.write_text(
        json.dumps(parked_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    remove_ids = DELETES | PARKS
    deleted = [eid for eid in DELETES if eid in by_id]
    skipped += [eid for eid in DELETES if eid not in by_id]
    new_vocab = [e for e in vocab if e["id"] not in remove_ids]

    log_lines = [
        "", "=" * 70,
        "Vocab review batch 14 — tamago-l12 frequency fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    for eid in deleted:
        log_lines.append(f"    delete {eid}")
    for entry in parked:
        log_lines.append(f"    park {entry['id']}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total field edits: {sum(len(f) for _, f in applied)}")
    log_lines.append(f"Total deletions: {len(deleted)}")
    log_lines.append(f"Total parked: {len(parked)}")
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

    print(f"Applied {sum(len(f) for _, f in applied)} field edits across {len(applied)} entries")
    print(f"Deleted {len(deleted)} entries")
    print(f"Parked {len(parked)} entries")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
