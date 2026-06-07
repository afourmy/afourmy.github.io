"""Apply vocab review batch 16 — tamago-l12 frequency and translation fixes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "tamago-l12-358": {"frequency": "occasional"},
    "tamago-l12-369": {"english": "about, approximately; handrail, railing"},
    "tamago-l12-378": {"frequency": "occasional"},
    "tamago-l12-383": {"frequency": "occasional"},
    "tamago-l12-385": {"english": "lace (fabric); trick, maneuver"},
    "tamago-l12-386": {"frequency": "occasional"},
    "tamago-l12-389": {"frequency": "occasional"},
    "tamago-l12-411": {"frequency": "occasional"},
    "tamago-l12-426": {"frequency": "occasional"},
    "tamago-l12-428": {"frequency": "occasional"},
    "tamago-l12-433": {"frequency": "occasional"},
    "tamago-l12-436": {"frequency": "occasional"},
    "tamago-l12-441": {"frequency": "occasional"},
    "tamago-l12-445": {"english": "to pinch; curly, wavy (of hair)"},
    "tamago-l12-453": {"english": "dormitory, dorm (short for หอพัก); tower"},
    "tamago-l12-455": {"frequency": "occasional"},
    "tamago-l12-462": {"frequency": "occasional"},
}

DELETES = set()
PARKS = set()

APPLIED_ROW_IDS = {
    "tamago-l12-358", "tamago-l12-362", "tamago-l12-364", "tamago-l12-369",
    "tamago-l12-378", "tamago-l12-383", "tamago-l12-385", "tamago-l12-386",
    "tamago-l12-389", "tamago-l12-394", "tamago-l12-411", "tamago-l12-423",
    "tamago-l12-424", "tamago-l12-426", "tamago-l12-428", "tamago-l12-429",
    "tamago-l12-433", "tamago-l12-436", "tamago-l12-441", "tamago-l12-445",
    "tamago-l12-453", "tamago-l12-455", "tamago-l12-459", "tamago-l12-462",
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
        "Vocab review batch 16 — tamago-l12 frequency and translation fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total field edits: {sum(len(f) for _, f in applied)}")
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
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
