"""Apply batch 75 (rows row-01302 to row-01312) to vocab.json. Final batch."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01302", "delete": [], "park": ["yt-c19-096", "yt-c21-016", "yt-c21-018", "yt-c22-063"],
     "keep": None,
     "edits": {"yt-c02-003": {"english": "to have sex (idiom)"}},
     "note": "keep yt-c02-003 (idiom); park yt-c19-096, yt-c21-016, yt-c21-018, yt-c22-063"},
    {"row_id": "row-01303", "delete": ["yt-c20-032"], "park": [], "keep": "yt-c02-031",
     "edits": {"yt-c02-031": {"thai": "หี, จิ๋ม"}},
     "note": "merge into yt-c02-031; thai -> 'หี, จิ๋ม'; delete yt-c20-032"},
    {"row_id": "row-01304", "delete": ["yt-c03-031"], "park": [], "keep": "yt-c08-083",
     "edits": {"yt-c08-083": {"thai": "ทัพพี, กระบวย", "frequency": "occasional"}},
     "note": "merge into yt-c08-083; thai -> 'ทัพพี, กระบวย'; frequency -> occasional; delete yt-c03-031"},
    # row-01305: keep both — no changes
    # row-01306: keep both — no changes
    {"row_id": "row-01307", "delete": ["yt-c10-046"], "park": [], "keep": "yt-c05-052",
     "edits": {},
     "note": "remove yt-c10-046; keep yt-c05-052"},
    {"row_id": "row-01308", "delete": ["yt-c07-096"], "park": [], "keep": "yt-c17-046",
     "edits": {"yt-c17-046": {"thai": "ไม้เท้า, ไม้นําทาง"}},
     "note": "merge into yt-c17-046; thai -> 'ไม้เท้า, ไม้นําทาง'; delete yt-c07-096"},
    # row-01310: keep all — no changes
    {"row_id": "row-01311", "delete": [], "park": ["yt-c20-003"], "keep": None,
     "edits": {},
     "note": "park yt-c20-003; keep yt-c20-002, yt-c20-005"},
    {"row_id": "row-01312", "delete": [], "park": ["yt-c20-026"], "keep": "yt-c20-025",
     "edits": {},
     "note": "park yt-c20-026; keep yt-c20-025"},
]

APPLIED_ROW_IDS = {
    "row-01302", "row-01303", "row-01304", "row-01305", "row-01306",
    "row-01307", "row-01308", "row-01310", "row-01311", "row-01312",
}

STALE_ROW_IDS: set = set()


def main():
    vocab_path = HERE / "vocab.json"
    decisions_path = HERE / "decisions.json"
    parked_path = HERE / "parked.json"
    log_path = HERE / "apply_log.txt"

    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in vocab}

    to_delete = set()
    to_park = set()
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
        for eid in m["park"]:
            if eid not in by_id:
                skipped_missing.append((m["row_id"], "park", eid))
                continue
            to_park.add(eid)
            to_delete.add(eid)
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

    parked_doc = json.loads(parked_path.read_text(encoding="utf-8"))
    existing_parked_ids = {e["id"] for e in parked_doc["entries"]}
    for eid in sorted(to_park):
        if eid not in existing_parked_ids:
            parked_doc["entries"].append(by_id[eid])
    parked_path.write_text(
        json.dumps(parked_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log_lines = ["", "=" * 70, "Batch 75 — rows row-01302 to row-01312 (final batch)", ""]
    for m in MUTATIONS:
        log_lines.append(f"[{m['row_id']}] {m['note']}")
        if m["delete"]:
            log_lines.append(f"    delete: {', '.join(m['delete'])}")
        if m["park"]:
            log_lines.append(f"    park:   {', '.join(m['park'])}")
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
    log_lines.append(f"  of which parked:          {len(to_park)}")
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
    print(f"parked.json: {len(parked_doc['entries'])} entries added ({len(to_park)} new)")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows ({before - doc['total_rows']} removed)")
    if skipped_missing:
        print(f"Skipped {len(skipped_missing)} already-deleted refs (see apply_log.txt)")
    print(f"log appended to: {log_path.name}")


if __name__ == "__main__":
    main()
