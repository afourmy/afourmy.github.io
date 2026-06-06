"""Apply vocab review batch 2 (chula-l4-101 to chula-l5-051 fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "chula-l4-105": {"english": "womanizer, someone who likes to flirt"},
    "chula-l4-125": {"english": "regular job, steady job"},
    "chula-l4-132": {"english": "memory loss, memory deterioration (e.g. from aging)", "frequency": "occasional"},
    "chula-l4-136": {"english": "rotten, spoiled"},
    "chula-l5-008": {"english": "channel, pathway"},
    "chula-l5-014": {"english": "carrier (of a disease), vector"},
    "chula-l5-017": {"english": "nighttime, late at night"},
    "chula-l5-024": {"thai": "สื่อ, สื่อสาร", "english": "to convey, to communicate"},
    "chula-l5-046": {"english": "punch, blow delivered with fist", "frequency": "occasional"},
    "chula-l5-048": {"english": "to crawl, to squeeze through a narrow space"},
}

APPLIED_ROW_IDS = {
    "chula-l4-105", "chula-l4-125", "chula-l4-132", "chula-l4-134",
    "chula-l4-136", "chula-l5-008", "chula-l5-014", "chula-l5-017",
    "chula-l5-024", "chula-l5-046", "chula-l5-048",
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
        "Vocab review batch 2 — chula-l4-101 to chula-l5-051 field fixes", "",
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
