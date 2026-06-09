"""Apply free-form `decisions` file batch 5 — 57 edits (incl. 1 merge), 1 delete."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    # frequency only
    "chula-l4-033": {"frequency": "common"},
    "chula-l4-039": {"frequency": "common"},
    "chula-l4-120": {"frequency": "everyday"},
    "chula-l4-121": {"frequency": "everyday"},
    "chula-l4-122": {"frequency": "occasional"},
    "chula-l4-126": {"frequency": "occasional"},
    "chula-l5-038": {"frequency": "occasional"},
    "chula-l5-064": {"frequency": "occasional"},
    "chula-l5-076": {"frequency": "occasional"},
    "chula-l5-077": {"frequency": "occasional"},
    "chula-l5-078": {"frequency": "occasional"},
    "chula-l5-108": {"frequency": "occasional"},
    "chula-l5-191": {"frequency": "occasional"},
    "chula-l5-371": {"frequency": "everyday"},
    "chula-l5-374": {"frequency": "everyday"},
    "chula-l5-403": {"frequency": "everyday"},
    "chula-l6-279": {"frequency": "occasional"},
    "tamago-l12-042": {"frequency": "occasional"},
    "tamago-l12-040": {"frequency": "occasional"},
    "tamago-l12-081": {"frequency": "occasional"},
    "tamago-l12-114": {"frequency": "occasional"},
    # english only
    "wlt-c14-050": {"english": "careful"},
    "wlt-c14-093": {"english": "mall"},
    "wlt-c15-033": {"english": "above, on top, upstairs"},
    "wlt-c15-034": {"english": "below, under"},
    "chula-l4-008": {"english": "private, non-governmental"},
    "chula-l4-062": {"english": "to pin, to stick"},
    "chula-l5-087": {"english": "to interview"},
    "chula-l5-203": {"english": "to take (photo, video); to defecate; to transfer (data)"},
    "chula-l5-216": {"english": "to get rid of, to eliminate"},
    "chula-l5-067": {"english": "to extinguish, to put out (a fire); to cease, to stop functioning"},
    "wlt-c15-043": {"english": "to be, is"},
    "wlt-c15-048": {"english": "to meet; to encounter (unexpectedly)"},
    "wlt-c15-050": {"english": "kind-hearted"},
    "wlt-c15-062": {"english": "only, single, alone"},
    "wlt-c15-066": {"english": "next, later"},
    "wlt-c15-068": {"english": "from, since"},
    "wlt-c15-070": {"english": "low, inferior"},
    "wlt-c15-078": {"english": "there"},
    "wlt-c15-079": {"english": "here"},
    "wlt-c15-082": {"english": "student"},
    "wlt-c15-089": {"english": "some, a little"},
    "wlt-c15-090": {"english": "sometimes; maybe, perhaps"},
    "wlt-c15-091": {"english": "Baht"},
    "wlt-c16-051": {"english": "to fall asleep"},
    "wlt-c16-064": {"english": "to take a shower, to bathe"},
    "wlt-c16-070": {"english": "so, then"},
    "chula-l6-272": {"english": "to guess, predict, speculate, infer from clues"},
    "tamago-l12-093": {"english": "to pay back, to refund"},
    "tamago-l12-115": {"english": "to box (muay thai)"},
    "tamago-l12-627": {"english": "indoors, under cover (e.g. from rain, sun)"},
    "tamago-l3-034": {"english": "to accuse (e.g. without proof), to claim (sth negative)"},
    "tamago-l3-044": {"english": "motivation"},
    "wlt-c15-055": {"english": "'isn't it so?', 'right?'"},
    # frequency + english
    "chula-l4-042": {"frequency": "occasional", "english": "around, surrounding"},
    "wlt-c16-046": {"frequency": "occasional", "english": "female"},
    # merge: wlt-c12-068 หิวข้าว folded into wlt-c14-095 (eng/freq already match), then deleted
    "wlt-c14-095": {"thai": "หิว, หิวข้าว"},
}

DELETES = {
    "wlt-c12-068",
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
        "Free-form decisions file batch 5 — 57 edits (incl. 1 merge), 1 delete", "",
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
