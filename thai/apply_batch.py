"""Apply vocab review batch 4 (chula-l5-145 to chula-l5-230 fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "chula-l5-173": {"english": "to doze off while driving"},
    "chula-l5-184": {"english": "to travel downstream, to drift (on a river)"},
    "chula-l5-193": {"english": "to lack, to be missing; torn, broken"},
    "chula-l5-201": {"english": "head (formal)", "frequency": "common"},
    "chula-l5-211": {"english": "restless, agitated"},
}

APPLIED_ROW_IDS = {
    "chula-l5-173", "chula-l5-184", "chula-l5-193", "chula-l5-201", "chula-l5-211",
}


def main():
    vocab_path = HERE / "vocab.json"
    decisions_path = HERE / "decisions.json"
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

    log_lines = [
        "", "=" * 70,
        "Vocab review batch 4 — chula-l5-145 to chula-l5-230 field fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total edits: {sum(len(f) for _, f in applied)}")
    log_lines.append("")

    existing_log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing_log + "\n".join(log_lines) + "\n", encoding="utf-8")

    backup = vocab_path.with_suffix(".json.bak")
    shutil.copy2(vocab_path, backup)
    vocab_path.write_text(
        json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    doc = json.loads(decisions_path.read_text(encoding="utf-8"))
    before = len(doc["rows"])
    doc["rows"] = [r for r in doc["rows"] if r["row_id"] not in APPLIED_ROW_IDS]
    doc["total_rows"] = len(doc["rows"])
    decisions_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Applied {sum(len(f) for _, f in applied)} field edits across {len(applied)} entries")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
