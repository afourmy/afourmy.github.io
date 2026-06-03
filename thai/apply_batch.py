"""Apply batch 42 (rows 839-851) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00839", "delete": [], "keep": None,
     "edits": {"t4k-c11-039": {"frequency": "rare", "english": "community, collective society"}},
     "note": "keep both; t4k-c11-039 -> rare, english -> 'community, collective society'"},
    {"row_id": "row-00840", "delete": ["t4k-c09-052"], "keep": "chula-l5-192", "edits": {},
     "note": "keep chula-l5-192"},
    # row-00841: keep both — no action
    {"row_id": "row-00842", "delete": [], "keep": None,
     "edits": {"yt-c03-010": {"frequency": "occasional"}},
     "note": "keep both; yt-c03-010 -> occasional"},
    {"row_id": "row-00843", "delete": ["chula-l5-255"], "keep": "wlt-c11-027",
     "edits": {"wlt-c11-027": {"thai": "บ่อย, มัก"}},
     "note": "keep wlt-c11-027 as บ่อย, มัก"},
    {"row_id": "row-00844", "delete": [], "keep": None,
     "edits": {"t4k-c02-038": {"english": "still, quiet"}},
     "note": "keep both; t4k-c02-038 english -> 'still, quiet'"},
    {"row_id": "row-00845", "delete": ["thaipod-0039"], "keep": "chula-l5-299",
     "edits": {"chula-l5-299": {"thai": "ชาวเรือ, กะลาสี"}},
     "note": "keep chula-l5-299 as ชาวเรือ, กะลาสี"},
    {"row_id": "row-00846", "delete": [], "keep": None,
     "edits": {"chula-l5-314": {"frequency": "occasional"}},
     "note": "keep both; chula-l5-314 -> occasional"},
    {"row_id": "row-00847", "delete": ["tamago-l12-291"], "keep": "chula-l5-317",
     "edits": {"chula-l5-317": {"thai": "ผ่อนจ่าย, แบ่งชำระ"}},
     "note": "keep chula-l5-317 as ผ่อนจ่าย, แบ่งชำระ"},
    {"row_id": "row-00848", "delete": ["tobo-437"], "keep": "chula-l5-353",
     "edits": {"chula-l5-353": {"thai": "เกษตรกรรม, การเกษตร"}},
     "note": "keep chula-l5-353 as เกษตรกรรม, การเกษตร"},
    {"row_id": "row-00849", "delete": [], "keep": None,
     "edits": {"t4k-c11-108": {"frequency": "rare", "english": "relationship (formal)"}},
     "note": "keep both; t4k-c11-108 -> rare, english -> 'relationship (formal)'"},
    {"row_id": "row-00850", "delete": [], "keep": None,
     "edits": {"chula-l5-375": {"english": "assets, wealth"}},
     "note": "keep both; chula-l5-375 english -> 'assets, wealth'"},
    {"row_id": "row-00851", "delete": [], "keep": None,
     "edits": {
         "chula-l5-376": {"frequency": "rare", "english": "such as (formal)"},
         "wlt-c02-005": {"english": "namely, consisting of (+ enumeration)"},
     },
     "note": "keep all 3; chula-l5-376 -> rare, english 'such as (formal)'; wlt-c02-005 english -> 'namely, consisting of (+ enumeration)'"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(839, 852)}

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

    log_lines = ["", "=" * 70, "Batch 42 — rows 839-851", ""]
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
