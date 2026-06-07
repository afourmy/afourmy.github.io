"""Apply vocab review batch 24 — tsl-014 to tsl-226 (frequency + translation fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "tsl-019": {"frequency": "common"},
    "tsl-029": {"frequency": "common"},
    "tsl-037": {"frequency": "rare"},
    "tsl-060": {"frequency": "occasional"},
    "tsl-063": {"frequency": "occasional"},
    "tsl-065": {"frequency": "occasional"},
    "tsl-067": {"frequency": "occasional"},
    "tsl-070": {"frequency": "occasional"},
    "tsl-074": {"frequency": "occasional"},
    "tsl-087": {"frequency": "occasional"},
    "tsl-095": {"frequency": "occasional"},
    "tsl-098": {"english": "needle; (informal) shot, injection"},
    "tsl-109": {"frequency": "occasional"},
    "tsl-110": {"frequency": "occasional"},
    "tsl-127": {"frequency": "common"},
    "tsl-140": {"frequency": "rare"},
    "tsl-147": {"frequency": "common"},
    "tsl-148": {"frequency": "occasional"},
    "tsl-161": {"frequency": "occasional"},
    "tsl-166": {"frequency": "occasional"},
    "tsl-169": {"frequency": "occasional"},
    "tsl-194": {"frequency": "occasional"},
    "tsl-200": {"frequency": "occasional"},
    "tsl-220": {"frequency": "occasional"},
    "tsl-222": {"frequency": "occasional"},
}

DELETES = set()
PARKS = set()

APPLIED_ROW_IDS = {
    "tsl-019", "tsl-029", "tsl-037", "tsl-060", "tsl-063", "tsl-064", "tsl-065",
    "tsl-067", "tsl-069", "tsl-070", "tsl-074", "tsl-087", "tsl-095", "tsl-098",
    "tsl-109", "tsl-110", "tsl-127", "tsl-140", "tsl-147", "tsl-148", "tsl-161",
    "tsl-166", "tsl-169", "tsl-194", "tsl-200", "tsl-220", "tsl-222",
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
        "Vocab review batch 24 — tsl-014 to tsl-226 (frequency + translation fixes)", "",
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
