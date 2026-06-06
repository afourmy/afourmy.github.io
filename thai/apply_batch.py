"""Apply vocab review batch 5 (chula-l5-231 to chula-l5-315 fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "chula-l5-244": {"english": "to screen, screening (e.g. health check, security)"},
    "chula-l5-249": {"thai": "เชื้อ, เชื้อโรค", "english": "germ, pathogen"},
    "chula-l5-276": {"english": "bored, fed up, feeling blue"},
    "chula-l5-280": {"english": "monsoon"},
    "chula-l5-281": {"english": "monsoon trough"},
    "chula-l5-282": {"english": "(storm) to pass through, to sweep across"},
    "chula-l5-285": {"english": "stuffy, hot and humid", "frequency": "common"},
    "chula-l5-307": {"english": "to stagger, to be unsteady"},
}

DELETES = {"chula-l5-297"}

APPLIED_ROW_IDS = {
    "chula-l5-244", "chula-l5-249", "chula-l5-276", "chula-l5-280",
    "chula-l5-281", "chula-l5-282", "chula-l5-285", "chula-l5-297", "chula-l5-307",
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

    deleted = [eid for eid in DELETES if eid in by_id]
    skipped += [eid for eid in DELETES if eid not in by_id]

    new_vocab = [e for e in vocab if e["id"] not in DELETES]

    log_lines = [
        "", "=" * 70,
        "Vocab review batch 5 — chula-l5-231 to chula-l5-315 field fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    for eid in deleted:
        log_lines.append(f"    delete {eid}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total edits: {sum(len(f) for _, f in applied)}")
    log_lines.append(f"Total deletions: {len(deleted)}")
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
    print(f"Deleted {len(deleted)} entries: {', '.join(deleted)}")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
