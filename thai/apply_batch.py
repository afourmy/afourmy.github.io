"""Apply batch 45 (rows 882-913) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    # rows 882, 884, 886, 887, 888, 891, 892, 893, 894: no instruction (skipped)
    {"row_id": "row-00895", "delete": [], "keep": None,
     "edits": {"t4k-c05-040": {"english": "you (rude)"}},
     "note": "keep both; t4k-c05-040 english -> 'you (rude)'"},
    {"row_id": "row-00897", "delete": [], "keep": None,
     "edits": {"tobo-330": {"english": "cleverness, smartness"}},
     "note": "keep both; tobo-330 english -> 'cleverness, smartness'"},
    {"row_id": "row-00898", "delete": ["t4k-c05-078", "t4k-c06-024"], "keep": None, "edits": {},
     "note": "remove both (เนื่อง / เนื่องมาจาก)"},
    {"row_id": "row-00900", "delete": ["t4k-c06-022"], "keep": "t4k-c10-041",
     "edits": {"t4k-c10-041": {"english": "stylish, chic, cool"}},
     "note": "keep t4k-c10-041 as stylish, chic, cool"},
    {"row_id": "row-00901", "delete": [], "keep": None,
     "edits": {"t4k-c06-042": {"english": "administrative office"}},
     "note": "keep both; t4k-c06-042 english -> 'administrative office'"},
    {"row_id": "row-00903", "delete": ["t4k-c10-099"], "keep": "t4k-c06-067",
     "edits": {"t4k-c06-067": {"english": "equal"}},
     "note": "keep t4k-c06-067 with english -> 'equal'"},
    {"row_id": "row-00904", "delete": ["wlt-c05-021"], "keep": "t4k-c06-068",
     "edits": {"t4k-c06-068": {"frequency": "rare"}},
     "note": "keep t4k-c06-068, set frequency -> rare"},
    {"row_id": "row-00905", "delete": ["t4k-c06-085"], "keep": "wlt-c21-016", "edits": {},
     "note": "keep wlt-c21-016"},
    {"row_id": "row-00906", "delete": ["t4k-c11-096"], "keep": "t4k-c07-011", "edits": {},
     "note": "keep t4k-c07-011"},
    {"row_id": "row-00907", "delete": [], "keep": None,
     "edits": {"t4k-c07-042": {"english": "world (Buddhist cosmology)"}},
     "note": "keep both; t4k-c07-042 english -> 'world (Buddhist cosmology)'"},
    {"row_id": "row-00908", "delete": ["t4k-c07-077", "t4k-c08-074"], "keep": None, "edits": {},
     "note": "remove both (สุทธิ / เน็ต)"},
    {"row_id": "row-00909", "delete": ["t4k-c07-088"], "keep": "yt-c18-019", "edits": {},
     "note": "keep yt-c18-019"},
    {"row_id": "row-00911", "delete": ["t4k-c08-007"], "keep": "wlt-c18-009",
     "edits": {"wlt-c18-009": {"thai": "ชาวต่างชาติ, คนต่างประเทศ"}},
     "note": "keep wlt-c18-009 as ชาวต่างชาติ, คนต่างประเทศ"},
    {"row_id": "row-00912", "delete": ["t4k-c08-024"], "keep": "tobo-280", "edits": {},
     "note": "keep tobo-280"},
    {"row_id": "row-00913", "delete": ["t4k-c08-033", "wlt-c08-008"], "keep": "wlt-c06-058",
     "edits": {"wlt-c06-058": {"thai": "ดวงอาทิตย์, พระอาทิตย์"}},
     "note": "keep wlt-c06-058 as ดวงอาทิตย์, พระอาทิตย์"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(882, 914)}

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

    log_lines = ["", "=" * 70, "Batch 45 — rows 882-913", ""]
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
