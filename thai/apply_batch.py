"""Apply free-form `decisions` file batch 9 — per-line edits + 2 bulk-freq lists, 1 delete."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # english only
    "chula-l5-277": {"english": "to drain, to empty; to express strong emotions, to vent"},
    "chula-l5-417": {"english": "quantity, volume"},
    "chula-l6-024": {"english": "to focus on, to emphasize"},
    "chula-l6-075": {"english": "highlight, strong point, distinguishing feature"},
    "chula-l6-274": {"english": "dented, crushed, distorted"},
    "tamago-l12-325": {"english": "physically fit, in good shape (loanword)"},
    "tamago-l12-370": {"english": "edge, rim, side"},
    "chula-l5-154": {"english": "to head toward, to make one's way to"},
    "chula-l5-267": {"english": "accidentally, unintentionally"},
    "chula-l6-159": {"english": "group, cluster"},
    "chula-l6-222": {"english": "stick, bar, rod; classifier for long solid (stick-shaped) objects"},
    "chula-l6-338": {"english": "to support, accommodate, handle (e.g a need, a capacity)"},
    "tamago-l12-036": {"english": "to block, separate, divide"},
    "tamago-l12-203": {"english": "to spill on"},
    "tamago-l12-116": {"english": "to start a conversation, to engage someone in talking"},
    "tamago-l12-465": {"english": "to skip, to abstain from, to go without"},
    "tamago-l12-486": {"english": "to hold, to carry (mostly children and pets)"},
    "chula-l6-182": {"english": "wrinkles"},
    "tamago-l12-055": {"english": "to lock up, imprison, confine"},
    "tamago-l12-513": {"english": "to hike in the mountains"},
    "tamago-l12-564": {"english": "pole, pillar"},
    "tamago-l12-589": {"english": "to soak, to immerse"},
    "tamago-l12-503": {"english": "clear; to clarify, to sort out (loanword)"},
    "chula-l6-241": {"english": "to launch, introduce, unveil (event, product); to introduce a romantic partner to friends or family"},
    # frequency only
    "chula-l5-329": {"frequency": "everyday"},
    "chula-l5-424": {"frequency": "everyday"},
    "chula-l5-457": {"frequency": "everyday"},
    "chula-l6-003": {"frequency": "occasional"},
    "chula-l6-004": {"frequency": "occasional"},
    "chula-l6-006": {"frequency": "occasional"},
    "chula-l6-010": {"frequency": "occasional"},
    "chula-l6-023": {"frequency": "occasional"},
    "chula-l6-046": {"frequency": "occasional"},
    "chula-l6-050": {"frequency": "occasional"},
    "chula-l6-054": {"frequency": "occasional"},
    "chula-l6-038": {"frequency": "occasional"},
    "chula-l6-089": {"frequency": "occasional"},
    "chula-l6-117": {"frequency": "occasional"},
    "chula-l6-163": {"frequency": "occasional"},
    "chula-l6-259": {"frequency": "occasional"},
    "chula-l6-263": {"frequency": "occasional"},
    "chula-l6-258": {"frequency": "occasional"},
    "chula-l6-264": {"frequency": "occasional"},
    "chula-l6-302": {"frequency": "everyday"},
    # english + frequency
    "chula-l5-139": {"english": "to turn upside down, to capsize", "frequency": "occasional"},
    "chula-l6-120": {"english": "to end, conclude, finish (e.g a text, a sentence)", "frequency": "occasional"},
    "tamago-l12-500": {"english": "stationery (office supplies)", "frequency": "occasional"},
    "chula-l6-327": {"english": "aura, atmosphere; hint of sth", "frequency": "occasional"},
    "chula-l5-366": {"english": "to assemble, to put together", "frequency": "occasional"},
    "chula-l6-031": {"english": "to start (e.g a sentence, paragraph, letter, speech)", "frequency": "occasional"},
    "chula-l6-340": {"english": "to lighten, to relieve (someone's burden, workload, responsibility)", "frequency": "occasional"},
    "tamago-l12-606": {"english": "to exchange money into coins", "frequency": "occasional"},
    # change thai + english
    "chula-l6-256": {"thai": "ไกลลิบ", "english": "very far away"},
    "tamago-l12-536": {"thai": "เปลือง", "english": "to use more than necessary, to waste"},
}

# Bulk frequency lines (L49 / L51). tamago-l12-012 was listed twice -> set dedupes it.
# tamago-l12-202 was in the everyday list but is being removed instead (conflict resolved).
OCC_BULK = {
    "chula-l6-253", "chula-l6-255", "chula-l6-268", "chula-l6-292", "chula-l6-309",
    "chula-l6-310", "chula-l6-315", "chula-l6-317", "chula-l6-318", "tamago-l12-012",
    "tamago-l12-306", "tamago-l12-407", "chula-l6-307", "chula-l6-096", "chula-l6-226",
    "chula-l6-244", "chula-l6-333", "tamago-l12-221", "tamago-l12-230", "tamago-l12-397",
    "chula-l6-316", "chula-l6-331", "chula-l6-334", "chula-l6-335", "chula-l6-336",
    "tamago-l12-057", "tamago-l12-548", "tamago-l12-569", "tamago-l12-603", "thai9k-004",
    "tamago-l3-283",
}
EVERYDAY_BULK = {
    "tamago-l12-218", "tamago-l12-261", "tamago-l12-312", "tamago-l12-380",
    "tamago-l12-418", "tamago-l12-367",
}
for _id in OCC_BULK:
    EDITS.setdefault(_id, {})["frequency"] = "occasional"
for _id in EVERYDAY_BULK:
    EDITS.setdefault(_id, {})["frequency"] = "everyday"

DELETES = {
    "tamago-l12-202",  # ทำหก (conflict: everyday vs remove -> remove)
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
        "Free-form decisions file batch 9 — per-line edits + 2 bulk-freq lists, 1 delete", "",
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
    log_lines.append(f"Cards edited: {len(applied)}")
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
