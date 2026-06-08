"""Apply free-form `decisions` file batch — 36 cards (28 edits, 8 deletes)."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # frequency only
    "tamago-l12-013": {"frequency": "occasional"},
    "tamago-l12-018": {"frequency": "occasional"},
    "tamago-l12-047": {"frequency": "common"},
    "tamago-l3-128": {"frequency": "common"},
    "tsl-088": {"frequency": "occasional"},
    "yt-c01-027": {"frequency": "common"},
    "yt-c01-030": {"frequency": "common"},
    # english only
    "tamago-l12-048": {"english": "size"},
    "tamago-l12-089": {"english": "to think; to charge (a price)"},
    "tamago-l12-147": {"english": "temporary market, flea market"},
    "tamago-l12-299": {"english": "to leave with, to entrust; to give (as a gift)"},
    "tamago-l12-308": {"english": "enough; when, as soon as, once"},
    "tamago-l12-336": {"english": "it (pronoun); fun, enjoyable; oily"},
    "tamago-l12-416": {"english": "to wash one's hair, to shampoo"},
    "tamago-l12-419": {"english": "to take an exam"},
    "tamago-l12-430": {"english": "to send; to drop someone off"},
    "tamago-l12-491": {"english": "island; to cling, to hold on to"},
    "tamago-l12-509": {"english": "merely, just, nothing special; indifferent"},
    "tamago-l12-535": {"english": "to change one's mind, to reconsider"},
    "tamago-l12-528": {"english": "meat; content; flesh"},
    "tamago-l12-595": {"english": "powder; flour, starch"},
    "tamago-l12-657": {"english": "(slang) rude pronoun marker for males"},
    "tamago-l3-051": {"english": "satisfied, relieved (esp. after revenge (schadenfreude) or achievement)"},
    "tamago-l3-097": {"english": "secretly, without others knowing; a little, slightly"},
    "tobo-004": {"english": "movie; leather"},
    "yt-c14-073": {"english": "head; classifier for plants heads (cabbage, bulb of garlic, etc)"},
    # frequency + english
    "tamago-l3-094": {"frequency": "common", "english": "to tease, to pick on; to pretend (in a deceptive or playful way)"},
    # thai + english rename
    "wlt-c01-010": {"thai": "กี่โมง", "english": "what time"},
}

DELETES = {
    "tamago-l12-029", "tamago-l12-069", "tamago-l12-242", "thaipod-1349",
    "wlt-c07-083", "yt-c04-078", "wlt-c01-026", "wlt-c01-003",
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
        "Free-form decisions file batch — 36 cards (28 edits, 8 deletes)", "",
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
