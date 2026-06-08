"""Apply free-form `decisions` file batch 3 — 31 cards (27 edits, 4 deletes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # english only
    "wlt-c05-010": {"english": "to want to get (sth)"},
    "wlt-c05-032": {"english": "okay (loanword)"},
    "wlt-c06-037": {"english": "kiss, to kiss"},
    "wlt-c06-051": {"english": "good luck"},
    "wlt-c06-086": {"english": "excited, thrilled"},
    "wlt-c08-055": {"english": "there is no need to"},
    "wlt-c08-066": {"english": "this evening, this late afternoon"},
    "wlt-c08-067": {"english": "bad, terrible"},
    "wlt-c09-076": {"english": "alcohol, liquor"},
    "wlt-c10-031": {"english": "to ride (when sitting astride on top of animal or vehicle)"},
    "wlt-c10-032": {"english": "flu, cold"},
    "wlt-c10-045": {"english": "sleepy"},
    "wlt-c10-068": {"english": "better"},
    "wlt-c11-000": {"english": "the same, equal"},
    "wlt-c11-003": {"english": "to call (by phone)"},
    "wlt-c11-016": {"english": "scary, frightening"},
    "wlt-c11-025": {"english": "sure, certain"},
    "wlt-c11-034": {"english": "bored"},
    "wlt-c11-044": {"english": "sick, ill"},
    "wlt-c11-045": {"english": "problem, issue"},
    "wlt-c11-048": {"english": "to have a cold"},
    "wlt-c11-076": {"english": "drunk"},
    "wlt-c08-058": {"english": "to not have, there isn't"},
    "wlt-c10-046": {"english": "in that case, therefore (informal short form)"},
    # CHECK glosses — inner quotes kept per user
    "wlt-c05-012": {"english": "'don't do that yet!', 'hold on!'"},
    "wlt-c09-075": {"english": "'really?' (particle asking for confirmation)"},
    # drop the เร็ว form (เร็ว stays as wlt-c08-082); รวดเร็ว -> formal, common
    "t4k-c01-035": {"thai": "รวดเร็ว", "frequency": "common", "english": "fast, quick (formal)"},
}

DELETES = {
    "wlt-c05-080", "wlt-c06-012", "wlt-c09-085", "wlt-c11-008",
}
PARKS = set()

APPLIED_ROW_IDS = set()


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
        "Free-form decisions file batch 3 — 31 cards (27 edits, 4 deletes)", "",
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
