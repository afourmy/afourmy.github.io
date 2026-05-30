"""Apply batch 13 (rows 307-315) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00307", "delete": ["tamago-l12-373"], "keep": "thai9k-005",
     "edits": {"thai9k-005": {"thai": "สายรุ้ง, รุ้ง, รุ้งกินน้ำ"}},
     "note": "merge as สายรุ้ง, รุ้ง, รุ้งกินน้ำ"},
    {"row_id": "row-00308", "delete": ["wlt-c11-071"], "keep": "tamago-l12-374",
     "edits": {"tamago-l12-374": {"thai": "ภาพ, รูปภาพ"}},
     "note": "merge as ภาพ, รูปภาพ"},
    {"row_id": "row-00309", "delete": ["tamago-l12-376"], "keep": "wlt-c14-065", "edits": {},
     "note": "keep wlt-c14-065"},
    {"row_id": "row-00310", "delete": ["tamago-l12-382"], "keep": "thaipod-0887",
     "edits": {"thaipod-0887": {"thai": "ลาย, ลวดลาย"}},
     "note": "merge as ลาย, ลวดลาย"},
    {"row_id": "row-00311", "delete": ["thaipod-1066"], "keep": "tamago-l12-395", "edits": {},
     "note": "keep tamago-l12-395"},
    # row-00312: keep both — no action
    {"row_id": "row-00313", "delete": ["yt-c12-040"], "keep": "tamago-l12-399", "edits": {},
     "note": "keep tamago-l12-399"},
    {"row_id": "row-00314", "delete": [], "keep": "yt-c22-026",
     "edits": {"yt-c22-026": {"english": "crowded, bustling"}},
     "note": "keep both; rephrase yt-c22-026 english"},
    # row-00315: keep both — no action (wlt-c21-046 already edited in batch 8)
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(307, 316)}


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

    log_lines = ["", "=" * 70, "Batch 13 — rows 307-315", ""]
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
