"""Apply batch 4 (rows 119-133) to vocab.json.

Skips IDs that no longer exist (already deleted in a prior batch).
Appends to apply_log.txt.
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00119", "delete": [], "keep": "thaipod-0132",
     "edits": {"thaipod-0132": {"english": "steps, procedure"}},
     "note": "keep both; rephrase thaipod-0132 english"},
    {"row_id": "row-00120", "delete": ["thaipod-0787"], "keep": "chula-l5-117", "edits": {},
     "note": "keep chula-l5-117"},
    {"row_id": "row-00121", "delete": ["thaipod-0331"], "keep": "chula-l5-121", "edits": {},
     "note": "keep chula-l5-121"},
    {"row_id": "row-00122", "delete": ["tsl-184"], "keep": "chula-l5-121", "edits": {},
     "note": "keep chula-l5-121"},
    {"row_id": "row-00123", "delete": ["yt-c05-026"], "keep": "chula-l5-121", "edits": {},
     "note": "keep chula-l5-121"},
    # row-00124: keep both — no action
    # row-00125: keep both — no action
    {"row_id": "row-00126", "delete": ["tobo-146"], "keep": "chula-l5-142", "edits": {},
     "note": "keep chula-l5-142"},
    {"row_id": "row-00127", "delete": ["chula-l5-147"], "keep": "thaipod-1360", "edits": {},
     "note": "keep thaipod-1360"},
    {"row_id": "row-00128", "delete": ["chula-l5-155"], "keep": "wlt-c06-018",
     "edits": {"wlt-c06-018": {"english": "to move, shift, displace"}},
     "note": "keep wlt-c06-018; english='to move, shift, displace'"},
    # row-00129: keep both — no action
    # row-00130: keep both — no action
    {"row_id": "row-00131", "delete": ["chula-l5-161"], "keep": "thaipod-0467",
     "edits": {"thaipod-0467": {"english": "end, at the back, rear side"}},
     "note": "keep thaipod-0467; append 'rear side'"},
    {"row_id": "row-00132", "delete": ["chula-l5-170"], "keep": "thaipod-0848",
     "edits": {"thaipod-0848": {"thai": "รั้ว - รั้วกั้น"}},
     "note": "merge as รั้ว - รั้วกั้น"},
    {"row_id": "row-00133", "delete": [], "keep": "chula-l5-181",
     "edits": {"chula-l5-181": {"english": "intricate, complicated, convoluted"}},
     "note": "keep both; append 'convoluted' to chula-l5-181"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(119, 134)}


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

    log_lines = ["", "=" * 70, "Batch 4 — rows 119-133", ""]
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

    doc = json.loads(decisions_path.read_text(encoding="utf-8"))
    before = len(doc["rows"])
    doc["rows"] = [r for r in doc["rows"] if r["row_id"] not in APPLIED_ROW_IDS]
    doc["total_rows"] = len(doc["rows"])
    decisions_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"vocab.json: {len(vocab)} -> {len(new_vocab)} entries (backup: {backup.name})")
    print(f"decisions.json: {before} rows -> {doc['total_rows']} rows ({before - doc['total_rows']} removed)")
    if skipped_missing:
        print(f"Skipped {len(skipped_missing)} references to already-deleted entries (see apply_log.txt)")
    print(f"log appended to: {log_path.name}")


if __name__ == "__main__":
    main()
