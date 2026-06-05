"""Apply batch 65 (rows pfx-0001 to pfx-0026) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-pfx-0001", "delete": [], "keep": None,
     "edits": {
         "t4k-c01-030": {"english": "to act, to perform an action", "frequency": "rare"},
         "yt-c01-016": {"frequency": "occasional"},
     },
     "note": "keep both; t4k-c01-030 -> 'to act, to perform an action', rare; yt-c01-016 -> occasional"},
    # row-pfx-0002: keep both — no changes
    {"row_id": "row-pfx-0003", "delete": [], "keep": None,
     "edits": {"tobo-372": {"frequency": "occasional"}},
     "note": "keep both; tobo-372 frequency -> occasional"},
    # row-pfx-0004: keep both — no changes
    {"row_id": "row-pfx-0005", "delete": [], "keep": None,
     "edits": {"yt-c07-064": {"frequency": "occasional"}},
     "note": "keep both in occasional; yt-c07-064 frequency -> occasional"},
    {"row_id": "row-pfx-0006", "delete": [], "keep": None,
     "edits": {"tobo-361": {"frequency": "occasional"}},
     "note": "keep both; tobo-361 frequency -> occasional"},
    {"row_id": "row-pfx-0007", "delete": ["thaipod-0049"], "keep": "thaipod-0135", "edits": {},
     "note": "keep thaipod-0135; delete thaipod-0049"},
    {"row_id": "row-pfx-0008", "delete": ["t4k-c07-003"], "keep": "chula-l5-360", "edits": {},
     "note": "keep chula-l5-360; delete t4k-c07-003"},
    {"row_id": "row-pfx-0009", "delete": [], "keep": None,
     "edits": {
         "t4k-c10-033": {"english": "storehouse, warehouse", "frequency": "occasional"},
         "t4k-c05-042": {"english": "public finance, treasury", "frequency": "occasional"},
     },
     "note": "keep both; t4k-c10-033 -> 'storehouse, warehouse', occasional; t4k-c05-042 -> 'public finance, treasury', occasional"},
    {"row_id": "row-pfx-0010", "delete": [], "keep": None,
     "edits": {"thaipod-0052": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0052 frequency -> occasional"},
    {"row_id": "row-pfx-0011", "delete": [], "keep": None,
     "edits": {"tobo-296": {"frequency": "occasional"}},
     "note": "keep both; tobo-296 frequency -> occasional"},
    {"row_id": "row-pfx-0012", "delete": [], "keep": None,
     "edits": {"t4k-c07-026": {"english": "to commit suicide"}},
     "note": "keep both; t4k-c07-026 english -> 'to commit suicide'"},
    # row-pfx-0013: keep both — no changes
    {"row_id": "row-pfx-0014", "delete": ["thaipod-0056"], "keep": "tamago-l3-737",
     "edits": {"tamago-l3-737": {"english": "to organize an event, to hold a ceremony"}},
     "note": "keep tamago-l3-737 as 'to organize an event, to hold a ceremony'; delete thaipod-0056"},
    {"row_id": "row-pfx-0015", "delete": ["thaipod-0057"], "keep": "t4k-c02-070", "edits": {},
     "note": "keep t4k-c02-070; delete thaipod-0057"},
    # row-pfx-0016: keep both — no changes
    # row-pfx-0017: keep both — no changes
    {"row_id": "row-pfx-0018", "delete": ["thaipod-0059"], "keep": "t4k-c09-064",
     "edits": {"t4k-c09-064": {"english": "to produce a movie, to shoot a movie"}},
     "note": "keep t4k-c09-064 as 'to produce a movie, to shoot a movie'; delete thaipod-0059"},
    # row-pfx-0019: keep both — no changes
    # row-pfx-0020: keep both — no changes
    {"row_id": "row-pfx-0021", "delete": ["yt-c04-042"], "keep": "wlt-c15-084", "edits": {},
     "note": "keep wlt-c15-084; delete yt-c04-042"},
    {"row_id": "row-pfx-0022", "delete": ["t4k-c09-087"], "keep": "tobo-441", "edits": {},
     "note": "keep tobo-441; delete t4k-c09-087"},
    # row-pfx-0023: keep both — no changes
    {"row_id": "row-pfx-0024", "delete": ["thaipod-0065"], "keep": "thaipod-0541",
     "edits": {"thaipod-0541": {"frequency": "occasional"}},
     "note": "keep thaipod-0541, move to occasional; delete thaipod-0065"},
    {"row_id": "row-pfx-0025", "delete": ["t4k-c03-098"], "keep": "tobo-002",
     "edits": {"tobo-002": {"frequency": "common"}},
     "note": "keep tobo-002 (revolution), move to common; delete t4k-c03-098"},
    # row-pfx-0026: keep both — no changes
]

APPLIED_ROW_IDS = {f"row-pfx-{i:04d}" for i in range(1, 27)}

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

    log_lines = ["", "=" * 70, "Batch 65 — rows pfx-0001 to pfx-0026", ""]
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
