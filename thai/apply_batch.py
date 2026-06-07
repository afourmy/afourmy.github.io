"""Apply vocab review batch 39 — yt-c09-010 to yt-c11-021 (typo + translation fixes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "yt-c09-012": {"thai": "จารีต"},
    "yt-c09-028": {"thai": "เวทมนตร์, คาถา"},
    "yt-c09-029": {"thai": "เซ่น, เซ่นไหว้"},
    "yt-c09-044": {"english": "something that happens suddenly, out of nowhere (lit. 'wind blowing here and there')"},
    "yt-c09-095": {"thai": "ล้ำเส้น"},
    "yt-c09-098": {"english": "to give power, to strengthen"},
    "yt-c10-010": {"thai": "คิดตังค์, คิดเงิน, เช็คบิล"},
    "yt-c10-011": {"thai": "ฉัน + เลี้ยงเอง, จัดการเอง, จ่ายเอง"},
    "yt-c10-066": {"thai": "ฟู", "english": "fluffy, puffed-up (of hair)"},
    "yt-c10-068": {"english": "gratuitous gift, giving with affection"},
    "yt-c10-095": {"thai": "ข้อพิพาท, กรณีพิพาท"},
    "yt-c11-020": {"thai": "สบู่อาบน้ำสูตรเย็น, ยาสระผมสูตรเย็น"},
}

DELETES = set()
PARKS = set()

APPLIED_ROW_IDS = {
    "yt-c09-012", "yt-c09-028", "yt-c09-029", "yt-c09-044", "yt-c09-095",
    "yt-c09-098", "yt-c10-010", "yt-c10-011", "yt-c10-066", "yt-c10-068",
    "yt-c10-095", "yt-c11-020",
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
        "Vocab review batch 39 — yt-c09-010 to yt-c11-021 (typo + translation fixes)", "",
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
