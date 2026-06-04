"""Apply batch 49 (rows 960-967) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00960", "delete": [], "keep": None,
     "edits": {
         "tamago-l3-751": {"frequency": "occasional"},
         "yt-c17-091": {"frequency": "occasional", "english": "to calm down, regain composure, get your mind under control"},
     },
     "note": "keep both -> occasional; yt-c17-091 english updated"},
    {"row_id": "row-00961", "delete": ["thai9k-011"], "keep": "yt-c02-049",
     "edits": {"yt-c02-049": {"thai": "ตาดำ, รูม่านตา", "english": "pupil"}},
     "note": "keep yt-c02-049 as ตาดำ, รูม่านตา; english -> 'pupil'"},
    {"row_id": "row-00962", "delete": ["wlt-c07-003"], "keep": "thaipod-0037",
     "edits": {"thaipod-0037": {"frequency": "occasional", "thai": "กองทัพเรือ, ทหารเรือ"}},
     "note": "keep thaipod-0037 as กองทัพเรือ, ทหารเรือ, occasional"},
    {"row_id": "row-00963", "delete": ["wlt-c09-040"], "keep": "thaipod-0234",
     "edits": {"thaipod-0234": {"thai": "งง, สับสน"}},
     "note": "keep thaipod-0234 as งง, สับสน"},
    {"row_id": "row-00964", "delete": ["thaipod-0251", "thaipod-0539"], "keep": "yt-c02-089", "edits": {},
     "note": "keep yt-c02-089"},
    {"row_id": "row-00965", "delete": ["tsl-170"], "keep": "thaipod-0335",
     "edits": {"thaipod-0335": {"frequency": "occasional", "thai": "ด้วยความที่, ด้วยเหตุที่"}},
     "note": "keep thaipod-0335 as ด้วยความที่, ด้วยเหตุที่, occasional"},
    {"row_id": "row-00966", "delete": ["thaipod-0358"], "keep": "yt-c13-058",
     "edits": {"yt-c13-058": {"thai": "ตัดคอ, ตัดเศียร"}},
     "note": "keep yt-c13-058 as ตัดคอ, ตัดเศียร"},
    {"row_id": "row-00967", "delete": ["thaipod-0440"], "keep": "tobo-179",
     "edits": {"tobo-179": {"thai": "ทางเท้า, ทางเดินเท้า"}},
     "note": "keep tobo-179 as ทางเท้า, ทางเดินเท้า"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(957, 968)}

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

    log_lines = ["", "=" * 70, "Batch 49 — rows 960-967", ""]
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
