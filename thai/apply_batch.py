"""Apply batch 53 (rows 1015-1028) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01015", "delete": ["wlt-c03-012", "wlt-c03-064"], "keep": None, "edits": {},
     "note": "remove both (บอกว่า / พูดว่า)"},
    {"row_id": "row-01017", "delete": ["wlt-c03-033"], "keep": "wlt-c09-046",
     "edits": {"wlt-c09-046": {"thai": "ปลายเดือน, สิ้นเดือน"}},
     "note": "keep wlt-c09-046 as ปลายเดือน, สิ้นเดือน"},
    {"row_id": "row-01018", "delete": ["wlt-c04-065"], "keep": "wlt-c03-034",
     "edits": {"wlt-c03-034": {"thai": "ปลายปี, สิ้นปี"}},
     "note": "keep wlt-c03-034 as ปลายปี, สิ้นปี"},
    {"row_id": "row-01019", "delete": ["wlt-c03-046"], "keep": "wlt-c18-093", "edits": {},
     "note": "keep wlt-c18-093"},
    {"row_id": "row-01020", "delete": ["wlt-c03-067"], "keep": "yt-c20-095",
     "edits": {"yt-c20-095": {"thai": "แฟ้บ, ผงซักฟอก"}},
     "note": "keep yt-c20-095 as แฟ้บ, ผงซักฟอก"},
    {"row_id": "row-01021", "delete": ["wlt-c18-039"], "keep": "wlt-c03-092", "edits": {},
     "note": "keep wlt-c03-092"},
    {"row_id": "row-01023", "delete": ["wlt-c03-097", "wlt-c04-003"], "keep": None, "edits": {},
     "note": "remove both (ไม่ชอบ / ไม่มีความสุข)"},
    {"row_id": "row-01024", "delete": ["wlt-c04-024"], "keep": "wlt-c17-047", "edits": {},
     "note": "keep wlt-c17-047"},
    {"row_id": "row-01025", "delete": ["wlt-c13-078", "wlt-c14-038"], "keep": "wlt-c04-045",
     "edits": {"wlt-c04-045": {"thai": "เว้นแต่, ยกเว้น"}},
     "note": "keep wlt-c04-045 as เว้นแต่, ยกเว้น"},
    {"row_id": "row-01026", "delete": ["wlt-c07-081"], "keep": "wlt-c04-077",
     "edits": {"wlt-c04-077": {"thai": "สีฟัน, แปรงฟัน"}},
     "note": "keep wlt-c04-077 as สีฟัน, แปรงฟัน"},
    {"row_id": "row-01027", "delete": ["wlt-c04-081"], "keep": "wlt-c08-036",
     "edits": {"wlt-c08-036": {"thai": "มีความสุข, สุขใจ"}},
     "note": "keep wlt-c08-036 as มีความสุข, สุขใจ"},
    {"row_id": "row-01028", "delete": ["wlt-c04-084"], "keep": "wlt-c20-012",
     "edits": {"wlt-c20-012": {"thai": "ดัง, เสียงดัง"}},
     "note": "keep wlt-c20-012 as ดัง, เสียงดัง"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1015, 1029)}

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

    log_lines = ["", "=" * 70, "Batch 53 — rows 1015-1028", ""]
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
