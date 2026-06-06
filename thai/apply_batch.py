"""Apply vocab review batch 6 (chula-l5-319 to chula-l5-395 fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "chula-l5-340": {"english": "public relations (PR)"},
    "chula-l5-362": {"english": "tin"},
    "chula-l5-363": {"english": "lead"},
    "chula-l5-376": {"frequency": "occasional"},
    "chula-l5-384": {"english": "to spread (of a disease or pest)"},
    "chula-l5-395": {"english": "in this regard, with that said"},
}

PARKS = {"chula-l5-319"}

APPLIED_ROW_IDS = {
    "chula-l5-319", "chula-l5-340", "chula-l5-362", "chula-l5-363",
    "chula-l5-376", "chula-l5-384", "chula-l5-395",
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

    remove_ids = PARKS
    new_vocab = [e for e in vocab if e["id"] not in remove_ids]

    parked_doc = json.loads(parked_path.read_text(encoding="utf-8"))
    for entry in parked:
        parked_doc["entries"].append(entry)
    parked_path.write_text(
        json.dumps(parked_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log_lines = [
        "", "=" * 70,
        "Vocab review batch 6 — chula-l5-319 to chula-l5-395 field fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    for entry in parked:
        log_lines.append(f"    park {entry['id']}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total edits: {sum(len(f) for _, f in applied)}")
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
    print(f"Parked {len(parked)} entries: {', '.join(e['id'] for e in parked)}")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
