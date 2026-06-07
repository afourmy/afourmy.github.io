"""Apply vocab review batch 18 — tamago-l12/thai9k/tamago-l3 frequency and translation fixes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "tamago-l12-571": {"frequency": "rare"},
    "tamago-l12-573": {"frequency": "occasional"},
    "tamago-l12-574": {"frequency": "occasional"},
    "tamago-l12-601": {"frequency": "rare"},
    "tamago-l12-618": {"frequency": "occasional"},
    "tamago-l12-621": {"frequency": "occasional"},
    "tamago-l12-629": {"frequency": "occasional"},
    "tamago-l12-654": {"english": "where; which", "frequency": "everyday"},
    "thai9k-008": {"frequency": "occasional"},
    "thai9k-009": {"frequency": "rare"},
    "thai9k-010": {"frequency": "occasional"},
    "thai9k-017": {"frequency": "common"},
    "thai9k-020": {"frequency": "occasional"},
    "thai9k-021": {"frequency": "occasional"},
    "thai9k-025": {"frequency": "occasional"},
    "thai9k-038": {"frequency": "occasional"},
    "thai9k-041": {"frequency": "occasional"},
    "thai9k-042": {"frequency": "occasional"},
    "tamago-l3-027": {"frequency": "occasional"},
    "tamago-l3-037": {"frequency": "occasional"},
    "tamago-l3-050": {"frequency": "occasional"},
    "tamago-l3-056": {"frequency": "everyday"},
}

DELETES = {"tamago-l12-641", "tamago-l3-015"}
PARKS = set()

APPLIED_ROW_IDS = {
    "tamago-l12-571", "tamago-l12-573", "tamago-l12-574", "tamago-l12-575",
    "tamago-l12-577", "tamago-l12-600", "tamago-l12-601", "tamago-l12-618",
    "tamago-l12-621", "tamago-l12-629", "tamago-l12-641", "tamago-l12-654",
    "tamago-l12-656", "thai9k-001", "thai9k-008", "thai9k-009", "thai9k-010",
    "thai9k-015", "thai9k-017", "thai9k-020", "thai9k-021", "thai9k-023",
    "thai9k-025", "thai9k-030", "thai9k-031", "thai9k-038", "thai9k-041",
    "thai9k-042", "tamago-l3-015", "tamago-l3-027", "tamago-l3-037",
    "tamago-l3-050", "tamago-l3-056",
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
        "Vocab review batch 18 — tamago-l12/thai9k/tamago-l3 frequency and translation fixes", "",
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
