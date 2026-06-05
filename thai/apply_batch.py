"""Apply batch 64 (rows 1187-1200) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01187", "delete": [], "keep": None,
     "edits": {
         "tamago-l3-759": {"english": "club, association (e.g informal, like a school club)"},
         "wlt-c09-031": {"english": "club, organized association"},
     },
     "note": "keep both; tamago-l3-759 english -> 'club, association (e.g informal, like a school club)'; wlt-c09-031 english -> 'club, organized association'"},
    {"row_id": "row-01188", "delete": ["tsl-105"], "keep": "tamago-l3-795",
     "edits": {"tamago-l3-795": {"thai": "บีบคอ, รัดคอ"}},
     "note": "keep tamago-l3-795 as บีบคอ, รัดคอ; delete tsl-105"},
    {"row_id": "row-01189", "delete": [], "keep": None,
     "edits": {"yt-c01-061": {"english": "position, job title"}},
     "note": "keep both; yt-c01-061 english -> 'position, job title'"},
    # row-01190: keep both — no changes
    # row-01191: keep both — no changes
    {"row_id": "row-01192", "delete": [], "keep": None,
     "edits": {"thaipod-0041": {"english": "chapter, section (Buddhist text)"}},
     "note": "keep both; thaipod-0041 english -> 'chapter, section (Buddhist text)'"},
    {"row_id": "row-01193", "delete": ["thaipod-0078"], "keep": "thaipod-0763", "edits": {},
     "note": "remove thaipod-0078; keep thaipod-0763"},
    # row-01195: keep both — no changes
    {"row_id": "row-01197", "delete": [], "keep": None,
     "edits": {"thaipod-0252": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0252 frequency -> occasional"},
    {"row_id": "row-01198", "delete": ["thaipod-0300"], "keep": "yt-c12-084",
     "edits": {"yt-c12-084": {"thai": "แต่ประการใด, แต่อย่างใด", "english": "at all, whatsoever (formal)"}},
     "note": "keep yt-c12-084 as แต่ประการใด, แต่อย่างใด: at all, whatsoever (formal); delete thaipod-0300"},
    {"row_id": "row-01199", "delete": ["thaipod-0383"], "keep": "wlt-c10-096",
     "edits": {"wlt-c10-096": {"thai": "ทีหลัง, ต่อมา"}},
     "note": "keep wlt-c10-096 as ทีหลัง, ต่อมา; delete thaipod-0383"},
    # row-01200: keep both — no action (user unsure, entries not yet differentiated)
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1187, 1201)}

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

    log_lines = ["", "=" * 70, "Batch 64 — rows 1187-1200", ""]
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
