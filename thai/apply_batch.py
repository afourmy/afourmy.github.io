"""Apply batch 57 (rows 1072-1083) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01072", "delete": ["wlt-c03-096"], "keep": "chula-l5-129", "edits": {},
     "note": "keep chula-l5-129"},
    {"row_id": "row-01073", "delete": ["thaipod-0845"], "keep": "chula-l5-130",
     "edits": {"chula-l5-130": {"thai": "รับรอง, รับประกัน"}},
     "note": "keep chula-l5-130 as รับรอง, รับประกัน"},
    {"row_id": "row-01074", "delete": ["chula-l5-338"], "keep": "chula-l5-156", "edits": {},
     "note": "keep chula-l5-156"},
    # row-01075: keep both — no changes
    {"row_id": "row-01078", "delete": [], "keep": None,
     "edits": {"chula-l5-253": {"english": "to vomit (formal)"}},
     "note": "keep both; chula-l5-253 english -> 'to vomit (formal)'"},
    {"row_id": "row-01079", "delete": ["t4k-c03-024"], "keep": "chula-l5-327",
     "edits": {"chula-l5-327": {"thai": "แลก, แลกเปลี่ยน"}},
     "note": "keep chula-l5-327 as แลก, แลกเปลี่ยน"},
    {"row_id": "row-01080", "delete": [], "keep": None,
     "edits": {"tsl-174": {"english": "present, token of appreciation (formal)"}},
     "note": "keep both; tsl-174 english -> 'present, token of appreciation (formal)'"},
    {"row_id": "row-01081", "delete": [], "keep": None,
     "edits": {"thaipod-0280": {"english": "rice farmer"}},
     "note": "keep all; thaipod-0280 english -> 'rice farmer'"},
    {"row_id": "row-01082", "delete": [], "keep": None,
     "edits": {"wlt-c11-063": {"english": "vehicle, means of transport"}},
     "note": "keep all; wlt-c11-063 english -> 'vehicle, means of transport'"},
    {"row_id": "row-01083", "delete": ["tamago-l3-243"], "keep": "chula-l5-389", "edits": {},
     "note": "keep chula-l5-389; delete tamago-l3-243"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1072, 1084)}

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

    log_lines = ["", "=" * 70, "Batch 57 — rows 1072-1083", ""]
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
