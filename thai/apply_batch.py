"""Apply free-form `decisions` file batch 8 — 47 field edits (46 cards, incl. 1 thai+eng), 1 delete."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # english only
    "wlt-c19-044": {"english": "'no problem', 'no worries', relaxed"},
    "wlt-c19-087": {"english": "about, regarding"},
    "wlt-c19-088": {"english": "almost, nearly"},
    "wlt-c19-089": {"english": "old"},
    "wlt-c19-090": {"english": "glass; crystal"},
    "wlt-c19-091": {"english": "chicken"},
    "wlt-c19-092": {"english": "to request, to ask"},
    "wlt-c20-001": {"english": "tight; crowded, packed"},
    "wlt-c20-005": {"english": "to park"},
    "wlt-c20-010": {"english": "to use, to be used for"},
    "wlt-c20-011": {"english": "to wash (clothes)"},
    "wlt-c20-020": {"english": "short (in height)"},
    "wlt-c20-047": {"english": "wood"},
    "wlt-c20-048": {"english": "medicine, drug"},
    "wlt-c20-076": {"english": "for, meant for, intended for (formal)"},
    "wlt-c20-082": {"english": "sweet"},
    "wlt-c20-087": {"english": "to be located at; to live, to stay"},
    "wlt-c20-089": {"english": "again, once more"},
    "wlt-c20-090": {"english": "to get, to take, to want"},
    "wlt-c20-094": {"english": "to eat"},
    "wlt-c20-095": {"english": "(of things) old; former, previous"},
    "wlt-c20-098": {"english": "beside, next to, nearby"},
    "wlt-c21-005": {"english": "to pay, to spend"},
    "wlt-c21-006": {"english": "to like"},
    "wlt-c21-007": {"english": "morning (6am - 11am)"},
    "wlt-c21-018": {"english": "way, path; direction; means, method"},
    "wlt-c21-019": {"english": "to eat (formal)"},
    "wlt-c21-000": {"english": "to go up, to rise; to get on (vehicle)"},
    "wlt-c21-020": {"english": "to do, to make"},
    "wlt-c21-023": {"english": "milk; breast"},
    "wlt-c21-025": {"english": "approximately, roughly"},
    "wlt-c21-027": {"english": "to go"},
    "wlt-c21-035": {"english": "evening (4pm - 6pm); (of things) cold"},
    "wlt-c21-036": {"english": "hot"},
    "wlt-c21-045": {"english": "heavy"},
    "wlt-c21-050": {"english": "weather"},
    "wlt-c21-056": {"english": "who"},
    "wlt-c21-040": {"english": "child; classifier for round objects (balls, fruits, etc)"},
    "wlt-c21-041": {"english": "to choose"},
    "wlt-c21-058": {"english": "money; silver"},
    "wlt-c21-059": {"english": "name"},
    "wlt-c21-067": {"english": "car, vehicle"},
    "wlt-c21-061": {"english": "south; under"},
    "wlt-c21-064": {"english": "paternal grandfather"},
    "wlt-c21-047": {"english": "to give; to allow"},
    # make it: clean up thai + english
    "wlt-c21-063": {"thai": "เที่ยง, เที่ยงวัน", "english": "noon, midday"},
}

DELETES = {
    "wlt-c18-096",  # พบกัน
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
    missing_deletes = [eid for eid in DELETES if eid not in by_id]
    new_vocab = [e for e in vocab if e["id"] not in remove_ids]

    log_lines = [
        "", "=" * 70,
        "Free-form decisions file batch 8 — 47 field edits (46 cards, incl. 1 thai+eng), 1 delete", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    if deleted:
        for eid in deleted:
            log_lines.append(f"    delete {eid}")
    if skipped:
        log_lines.append(f"Skipped edits (not found): {', '.join(skipped)}")
    if missing_deletes:
        log_lines.append(f"Skipped deletes (not found): {', '.join(missing_deletes)}")
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

    print(f"Applied {sum(len(f) for _, f in applied)} field edits across {len(applied)} cards")
    print(f"Deleted ({len(deleted)}): {deleted}")
    if skipped:
        print(f"Skipped edits: {skipped}")
    if missing_deletes:
        print(f"Skipped deletes: {missing_deletes}")
    print(f"vocab.json: {len(vocab)} -> {len(new_vocab)}")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
