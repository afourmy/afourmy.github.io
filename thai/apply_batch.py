"""Apply vocab review batch 19 — tamago-l3 frequency and translation fixes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "tamago-l3-075": {"frequency": "everyday"},
    "tamago-l3-079": {"frequency": "occasional"},
    "tamago-l3-084": {"frequency": "occasional"},
    "tamago-l3-114": {"frequency": "occasional"},
    "tamago-l3-115": {"frequency": "occasional"},
    "tamago-l3-118": {"frequency": "everyday"},
    "tamago-l3-137": {"english": "timing, rhythm, beat; moment, opportunity", "frequency": "everyday"},
    "tamago-l3-152": {"frequency": "everyday"},
    "tamago-l3-158": {"frequency": "occasional"},
    "tamago-l3-165": {"frequency": "occasional"},
    "tamago-l3-167": {"frequency": "occasional"},
    "tamago-l3-169": {"frequency": "occasional"},
    "tamago-l3-183": {"frequency": "occasional"},
    "tamago-l3-185": {"frequency": "occasional"},
    "tamago-l3-194": {"frequency": "occasional"},
    "tamago-l3-206": {"frequency": "occasional"},
    "tamago-l3-210": {"frequency": "everyday"},
    "tamago-l3-225": {"frequency": "occasional"},
    "tamago-l3-244": {"frequency": "occasional"},
    "tamago-l3-266": {"frequency": "everyday"},
}

DELETES = {"tamago-l3-271"}
PARKS = set()

APPLIED_ROW_IDS = {
    "tamago-l3-075", "tamago-l3-079", "tamago-l3-084", "tamago-l3-114",
    "tamago-l3-115", "tamago-l3-118", "tamago-l3-137", "tamago-l3-152",
    "tamago-l3-158", "tamago-l3-165", "tamago-l3-167", "tamago-l3-169",
    "tamago-l3-170", "tamago-l3-175", "tamago-l3-177", "tamago-l3-183",
    "tamago-l3-185", "tamago-l3-187", "tamago-l3-188", "tamago-l3-192",
    "tamago-l3-194", "tamago-l3-206", "tamago-l3-210", "tamago-l3-225",
    "tamago-l3-241", "tamago-l3-244", "tamago-l3-255", "tamago-l3-265",
    "tamago-l3-266", "tamago-l3-271",
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
        "Vocab review batch 19 — tamago-l3 frequency and translation fixes", "",
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
