"""Apply batch 44 (rows 870-881) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    # rows 869, 872, 874: absent
    {"row_id": "row-00870", "delete": ["t4k-c01-093"], "keep": "tobo-402", "edits": {},
     "note": "keep tobo-402"},
    {"row_id": "row-00871", "delete": [], "keep": None,
     "edits": {"t4k-c02-000": {"frequency": "occasional", "english": "child (formal)"}},
     "note": "keep both; t4k-c02-000 -> occasional, english -> 'child (formal)'"},
    {"row_id": "row-00873", "delete": ["t4k-c02-036", "t4k-c04-032"], "keep": None, "edits": {},
     "note": "remove both (ดิ / เนี่ย)"},
    {"row_id": "row-00875", "delete": ["t4k-c02-059"], "keep": "wlt-c06-060",
     "edits": {"wlt-c06-060": {"thai": "ดังนั้น, เพราะฉะนั้น"}},
     "note": "keep wlt-c06-060 as ดังนั้น, เพราะฉะนั้น"},
    {"row_id": "row-00876", "delete": ["wlt-c05-039"], "keep": "t4k-c02-065", "edits": {},
     "note": "keep t4k-c02-065"},
    {"row_id": "row-00877", "delete": [], "keep": None,
     "edits": {
         "t4k-c07-005": {"english": "capital, funds"},
         "t4k-c02-069": {"english": "capital, asset"},
     },
     "note": "keep both; t4k-c07-005 english -> 'capital, funds'; t4k-c02-069 english -> 'capital, asset'"},
    {"row_id": "row-00878", "delete": ["t4k-c02-085"], "keep": "wlt-c11-096",
     "edits": {"wlt-c11-096": {"thai": "เปอร์เซ็นต์, ร้อยละ"}},
     "note": "keep wlt-c11-096 as เปอร์เซ็นต์, ร้อยละ"},
    {"row_id": "row-00879", "delete": [], "keep": None,
     "edits": {"t4k-c03-006": {"english": "space (in a text)"}},
     "note": "keep both; t4k-c03-006 english -> 'space (in a text)'"},
    {"row_id": "row-00880", "delete": [], "keep": None,
     "edits": {
         "t4k-c03-015": {"english": "to go back, to reverse"},
         "t4k-c05-069": {"frequency": "rare", "english": "to return, circle back, reminisce (literary)"},
     },
     "note": "keep both; t4k-c03-015 english updated; t4k-c05-069 -> rare, english updated"},
    {"row_id": "row-00881", "delete": ["t4k-c03-021"], "keep": "wlt-c05-083",
     "edits": {"wlt-c05-083": {"thai": "คนไข้, ผู้ป่วย"}},
     "note": "keep wlt-c05-083 as คนไข้, ผู้ป่วย"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(870, 882)}

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

    log_lines = ["", "=" * 70, "Batch 44 — rows 870-881", ""]
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
