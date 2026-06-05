"""Apply batch 73 (rows row-01246 to row-01274) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01246", "delete": [], "keep": None,
     "edits": {"tsl-350": {"frequency": "rare"}},
     "note": "keep both; tsl-350 frequency -> rare"},
    {"row_id": "row-01248", "delete": [], "keep": None,
     "edits": {"tsl-352": {"english": "I, me (royal, or used jokingly)"}},
     "note": "keep both; tsl-352 english -> 'I, me (royal, or used jokingly)'"},
    {"row_id": "row-01249", "delete": ["wlt-c03-050"], "keep": "wlt-c01-037",
     "edits": {"wlt-c01-037": {"thai": "ไปนอน, เข้านอน"}},
     "note": "merge into wlt-c01-037; thai -> 'ไปนอน, เข้านอน'; delete wlt-c03-050"},
    {"row_id": "row-01250", "delete": [], "keep": None,
     "edits": {"wlt-c07-061": {"frequency": "occasional"}},
     "note": "keep all; wlt-c07-061 frequency -> occasional"},
    {"row_id": "row-01251", "delete": ["wlt-c01-098"], "keep": "wlt-c11-058",
     "edits": {},
     "note": "remove wlt-c01-098; keep wlt-c11-058"},
    {"row_id": "row-01252", "delete": ["wlt-c02-004"], "keep": "wlt-c08-082",
     "edits": {},
     "note": "remove wlt-c02-004; keep wlt-c08-082"},
    {"row_id": "row-01254", "delete": ["wlt-c02-027", "wlt-c02-029"], "keep": None,
     "edits": {},
     "note": "remove both wlt-c02-027, wlt-c02-029"},
    # row-01255: keep both — no changes
    {"row_id": "row-01256", "delete": ["wlt-c02-062", "wlt-c18-021", "wlt-c18-076"], "keep": None,
     "edits": {},
     "note": "remove all wlt-c02-062, wlt-c18-021, wlt-c18-076"},
    # row-01258: keep both — no changes
    # row-01259: keep both — no changes
    {"row_id": "row-01260", "delete": ["wlt-c04-014"], "keep": "wlt-c14-080",
     "edits": {},
     "note": "remove wlt-c04-014; keep wlt-c14-080"},
    {"row_id": "row-01262", "delete": ["wlt-c04-050"], "keep": "yt-c13-001",
     "edits": {},
     "note": "remove wlt-c04-050; keep yt-c13-001"},
    {"row_id": "row-01264", "delete": ["wlt-c04-096", "wlt-c14-090"], "keep": None,
     "edits": {},
     "note": "remove both wlt-c04-096, wlt-c14-090"},
    {"row_id": "row-01265", "delete": ["wlt-c05-033"], "keep": "wlt-c17-089",
     "edits": {},
     "note": "remove wlt-c05-033; keep wlt-c17-089"},
    {"row_id": "row-01266", "delete": ["wlt-c13-050"], "keep": "wlt-c05-062",
     "edits": {},
     "note": "remove wlt-c13-050; keep wlt-c05-062"},
    {"row_id": "row-01267", "delete": ["yt-c10-006"], "keep": None,
     "edits": {"wlt-c05-064": {"english": "to scratch (in a way that leaves injury or marks)"}},
     "note": "remove yt-c10-006; wlt-c05-064 english -> 'to scratch (in a way that leaves injury or marks)'"},
    {"row_id": "row-01268", "delete": ["wlt-c05-067", "wlt-c10-025"], "keep": None,
     "edits": {},
     "note": "remove both wlt-c05-067, wlt-c10-025"},
    # row-01269: keep both — no changes
    {"row_id": "row-01271", "delete": ["wlt-c09-018"], "keep": "wlt-c05-097",
     "edits": {},
     "note": "remove wlt-c09-018; keep wlt-c05-097"},
    {"row_id": "row-01272", "delete": ["wlt-c06-004"], "keep": "wlt-c10-039",
     "edits": {"wlt-c10-039": {"thai": "คอม, คอมพิวเตอร์"}},
     "note": "merge into wlt-c10-039; thai -> 'คอม, คอมพิวเตอร์'; delete wlt-c06-004"},
    # row-01273: keep both — no changes
    # row-01274: keep all — no changes
]

APPLIED_ROW_IDS = {
    "row-01246", "row-01248", "row-01249", "row-01250", "row-01251",
    "row-01252", "row-01254", "row-01255", "row-01256", "row-01258",
    "row-01259", "row-01260", "row-01262", "row-01264", "row-01265",
    "row-01266", "row-01267", "row-01268", "row-01269", "row-01271",
    "row-01272", "row-01273", "row-01274",
}

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

    log_lines = ["", "=" * 70, "Batch 73 — rows row-01246 to row-01274", ""]
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
