"""Apply batch 61 (rows 1132-1143) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01132", "delete": ["t4k-c08-000"], "keep": "wlt-c19-078", "edits": {},
     "note": "keep wlt-c19-078; delete t4k-c08-000"},
    {"row_id": "row-01135", "delete": ["wlt-c11-068"], "keep": None, "edits": {},
     "note": "remove wlt-c11-068; keep t4k-c08-049 and thaipod-0663"},
    {"row_id": "row-01137", "delete": ["yt-c02-022"], "keep": "t4k-c09-002",
     "edits": {"t4k-c09-002": {"thai": "พลเอก, นายพล", "english": "general (military)"}},
     "note": "keep t4k-c09-002 as พลเอก, นายพล: general (military); delete yt-c02-022"},
    {"row_id": "row-01138", "delete": ["t4k-c09-003"], "keep": "yt-c08-060", "edits": {},
     "note": "keep yt-c08-060; delete t4k-c09-003"},
    {"row_id": "row-01139", "delete": [], "keep": None,
     "edits": {"t4k-c09-042": {"english": "steam (water)"}},
     "note": "keep both; t4k-c09-042 english -> 'steam (water)'"},
    {"row_id": "row-01140", "delete": [], "keep": None,
     "edits": {
         "t4k-c10-015": {"english": "push (e.g cart, wheelchair)"},
         "tobo-139": {"english": "to push (e.g a door)"},
     },
     "note": "keep both; t4k-c10-015 english -> 'push (e.g cart, wheelchair)'; tobo-139 english -> 'to push (e.g a door)'"},
    {"row_id": "row-01141", "delete": ["t4k-c10-093"], "keep": "wlt-c16-003",
     "edits": {"wlt-c16-003": {"english": "satisfied"}},
     "note": "keep only wlt-c16-003 with eng: 'satisfied'; delete t4k-c10-093"},
    {"row_id": "row-01142", "delete": ["t4k-c10-095"], "keep": "yt-c10-084",
     "edits": {"yt-c10-084": {"thai": "โทน, โทนเสียง"}},
     "note": "keep yt-c10-084 as โทน, โทนเสียง; delete t4k-c10-095"},
    {"row_id": "row-01143", "delete": [], "keep": None,
     "edits": {
         "t4k-c11-014": {"frequency": "rare", "english": "temple hall (Buddhism)"},
         "yt-c02-047": {"english": "temple (forehead)"},
     },
     "note": "keep both; t4k-c11-014 frequency -> rare, english -> 'temple hall (Buddhism)'; yt-c02-047 english -> 'temple (forehead)'"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1132, 1144)}

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

    log_lines = ["", "=" * 70, "Batch 61 — rows 1132-1143", ""]
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
