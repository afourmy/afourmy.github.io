"""Apply batch 58 (rows 1085-1100) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01085", "delete": ["tsl-292"], "keep": "chula-l5-429", "edits": {},
     "note": "keep chula-l5-429; delete tsl-292"},
    {"row_id": "row-01086", "delete": [], "keep": None,
     "edits": {"chula-l5-436": {"frequency": "rare"}},
     "note": "keep both; chula-l5-436 frequency -> rare"},
    {"row_id": "row-01089", "delete": ["thaipod-0826"], "keep": "chula-l6-089", "edits": {},
     "note": "keep chula-l6-089; delete thaipod-0826"},
    {"row_id": "row-01090", "delete": ["yt-c02-037"], "keep": "chula-l6-132", "edits": {},
     "note": "keep chula-l6-132; delete yt-c02-037"},
    {"row_id": "row-01091", "delete": [], "keep": None,
     "edits": {"chula-l6-155": {"frequency": "occasional"}},
     "note": "keep both; chula-l6-155 frequency -> occasional"},
    {"row_id": "row-01092", "delete": ["chula-l6-219"], "keep": "yt-c02-035",
     "edits": {"yt-c02-035": {"thai": "ตำ, โขลก"}},
     "note": "keep yt-c02-035 as ตำ, โขลก; delete chula-l6-219"},
    {"row_id": "row-01093", "delete": ["thaipod-0096"], "keep": "chula-l6-262", "edits": {},
     "note": "keep chula-l6-262; delete thaipod-0096"},
    {"row_id": "row-01095", "delete": ["tsl-085"], "keep": "chula-l6-267",
     "edits": {"chula-l6-267": {"thai": "เนื้อเรื่อง, โครงเรื่อง"}},
     "note": "keep chula-l6-267 as เนื้อเรื่อง, โครงเรื่อง; delete tsl-085"},
    {"row_id": "row-01098", "delete": [], "keep": None,
     "edits": {"tamago-l12-050": {"frequency": "rare"}},
     "note": "keep both; tamago-l12-050 frequency -> rare"},
    {"row_id": "row-01099", "delete": ["wlt-c10-075"], "keep": "t4k-c01-002", "edits": {},
     "note": "keep t4k-c01-002; delete wlt-c10-075"},
    {"row_id": "row-01100", "delete": ["t4k-c09-023"], "keep": "t4k-c05-040", "edits": {},
     "note": "keep t4k-c05-040 (already 'you (rude)'); delete t4k-c09-023"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1085, 1101)}

STALE_ROW_IDS: set = set()


def main():
    vocab_path = HERE / "vocab.json"
    decisions_path = HERE / "decisions.json"
    log_path = HERE / "apply_log.txt"

    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in vocab}

    to_delete = set()
    sources_into = defaultdict(set)
    field_edits = defaultdict(dict)
    skipped_missing = []

    for m in MUTATIONS:
        keep = m["keep"]
        if keep is not None and keep not in by_id:
            skipped_missing.append((m["row_id"], "keep", keep))
            keep = None
        for eid in m["delete"]:
            if eid not in by_id:
                skipped_missing.append((m["row_id"], "delete", eid))
                continue
            if eid in to_delete:
                continue
            to_delete.add(eid)
            if keep is not None and keep != eid:
                sources_into[keep].update(by_id[eid].get("sources", []))
        for eid, fields in m["edits"].items():
            if eid not in by_id:
                skipped_missing.append((m["row_id"], "edit", eid))
                continue
            if eid in to_delete:
                continue
            field_edits[eid].update(fields)

    for keep_id, extra_sources in sources_into.items():
        keep_entry = by_id[keep_id]
        original = list(keep_entry.get("sources", []))
        seen = set(original)
        additions = [s for s in sorted(extra_sources) if s not in seen]
        if additions:
            keep_entry["sources"] = original + additions

    for eid, fields in field_edits.items():
        for k, v in fields.items():
            by_id[eid][k] = v

    new_vocab = [e for e in vocab if e["id"] not in to_delete]

    log_lines = ["", "=" * 70, "Batch 58 — rows 1085-1100", ""]
    for m in MUTATIONS:
        log_lines.append(f"[{m['row_id']}] {m['note']}")
        if m["delete"]:
            log_lines.append(f"    delete: {', '.join(m['delete'])}")
        if m["keep"]:
            log_lines.append(f"    keep:   {m['keep']}")
        for eid, fields in m["edits"].items():
            for fk, fv in fields.items():
                log_lines.append(f"    edit {eid}.{fk} = {fv!r}")
    log_lines.append("")
    if skipped_missing:
        log_lines.append("Skipped (entry already deleted in a prior batch):")
        for r, k, eid in skipped_missing:
            log_lines.append(f"    {r}: {k} {eid}")
        log_lines.append("")
    log_lines.append(f"Total deletions this batch: {len(to_delete)}")
    log_lines.append(f"Total source-unions:        {len(sources_into)}")
    log_lines.append(f"Total field-edits:          {sum(len(v) for v in field_edits.values())}")
    log_lines.append(f"Vocab: {len(vocab)} -> {len(new_vocab)}")

    existing_log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing_log + "\n".join(log_lines) + "\n", encoding="utf-8")

    backup = vocab_path.with_suffix(".json.bak")
    shutil.copy2(vocab_path, backup)
    vocab_path.write_text(
        json.dumps(new_vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    remove_ids = APPLIED_ROW_IDS | STALE_ROW_IDS
    doc = json.loads(decisions_path.read_text(encoding="utf-8"))
    before = len(doc["rows"])
    doc["rows"] = [r for r in doc["rows"] if r["row_id"] not in remove_ids]
    doc["total_rows"] = len(doc["rows"])
    decisions_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"vocab.json: {len(vocab)} -> {len(new_vocab)} entries (backup: {backup.name})")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows ({before - doc['total_rows']} removed)")
    if skipped_missing:
        print(f"Skipped {len(skipped_missing)} already-deleted refs (see apply_log.txt)")
    print(f"log appended to: {log_path.name}")


if __name__ == "__main__":
    main()
