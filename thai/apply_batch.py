"""Apply free-form `decisions` file batch 7 — 45 field edits (44 cards), 17 deletes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # english only
    "wlt-c17-022": {"english": "to open, to turn on"},
    "wlt-c17-029": {"english": "(someone older) I, he, she, you, brother, sister"},
    "wlt-c17-032": {"english": "language"},
    "wlt-c17-051": {"english": "to go down, to get off"},
    "wlt-c17-052": {"english": "wind, air, breeze"},
    "wlt-c17-055": {"english": "day"},
    "wlt-c17-059": {"english": "to put (down), to place, to lay"},
    "wlt-c17-064": {"english": "girl, young woman"},
    "wlt-c17-065": {"english": "ten (10)"},
    "wlt-c17-071": {"english": "one (1)"},
    "wlt-c17-078": {"english": "ear"},
    "wlt-c17-080": {"english": "to want"},
    "wlt-c17-076": {"english": "to kiss (Thai style, on the cheek); to smell good"},
    "wlt-c17-074": {"english": "many, several, a lot"},
    "wlt-c17-092": {"english": "to snack"},
    "wlt-c17-097": {"english": "nearby, close"},
    "wlt-c18-069": {"english": "looks delicious"},
    "wlt-c20-038": {"english": "to rest, to take a break; to stay at (temporarily)"},
    "wlt-c20-046": {"english": "city, town; country"},
    "wlt-c20-059": {"english": "small (in size)"},
    "wlt-c20-079": {"english": "upper body garment (e.g. shirt, T-shirt)"},  # e.g. fixed
    "wlt-c20-084": {"english": "to look for, to search; (informal) to visit, to go see (someone)"},
    "t4k-c06-003": {"english": "excellent, awesome, the best"},
    "t4k-c11-036": {"english": "a little bit, just a little"},
    "wlt-c10-073": {"english": "in the afternoon (1 pm - 4 pm)"},  # spacing fixed
    "t4k-c04-024": {"english": "afternoon (1 pm - 4 pm)"},  # spacing fixed
    "t4k-c02-043": {"english": "to talk, to chat"},
    "t4k-c01-017": {"english": "to talk about, to refer to"},
    "wlt-c21-078": {"english": "I (male speaker); hair"},
    "wlt-c21-076": {"english": "phone"},
    "wlt-c21-072": {"english": "new; again"},
    "wlt-c21-073": {"english": "with"},
    "wlt-c21-074": {"english": "body; classifier for animals, clothes, furniture, etc"},
    "wlt-c21-077": {"english": "in"},
    "wlt-c21-071": {"english": "cold"},
    "wlt-c20-006": {"english": "will (future tense)"},
    "wlt-c17-082": {"english": "to go out, leave, exit"},
    "wlt-c18-022": {"english": "just, only"},
    "wlt-c18-071": {"english": "plain water"},
    "wlt-c18-082": {"english": "phone number"},
    "wlt-c19-001": {"english": "free (of charge)"},
    "wlt-c19-020": {"english": "uneasy, troubled, uncomfortable"},
    "wlt-c18-054": {"english": "'in that case', 'if so, then...'"},
    # english + frequency
    "t4k-c08-049": {"english": "foot (informal, rude)", "frequency": "occasional"},
}

DELETES = {
    "wlt-c18-010",  # คนนี้
    "wlt-c18-028",  # เจอกัน
    "wlt-c18-074",  # นึง
    "t4k-c10-072",  # แค่นั้น (was listed twice in decisions)
    "t4k-c05-085",  # น้ำเงิน
    "t4k-c04-055",  # คุณหมอ
    "t4k-c07-089",  # บาย
    "t4k-c07-015",  # แค่นี้
    "t4k-c05-058",  # เทา
    "t4k-c02-094",  # มั้ย
    "t4k-c01-020",  # ดังนั้น
    "t4k-c01-000",  # ทำให้
    "wlt-c21-075",  # ที่
    "wlt-c20-017",  # ตอน
    "wlt-c19-009",  # มาจาก
    "wlt-c19-019",  # ไม่ว่าง
    "wlt-c18-073",  # นิดนึง
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
        "Free-form decisions file batch 7 — 45 field edits (44 cards), 17 deletes", "",
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
