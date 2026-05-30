"""Apply batch 8 (rows 211-231) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00211", "delete": ["t4k-c02-031", "wlt-c15-063"], "keep": None, "edits": {},
     "note": "remove both"},
    # row-00212: keep both — no action
    {"row_id": "row-00213", "delete": ["t4k-c02-053"], "keep": "wlt-c06-018", "edits": {},
     "note": "keep wlt-c06-018 (already edited in batch 4)"},
    # row-00214: keep both — no action
    {"row_id": "row-00215", "delete": ["t4k-c02-057"], "keep": "thaipod-0276", "edits": {},
     "note": "keep thaipod-0276"},
    {"row_id": "row-00216", "delete": ["t4k-c02-067"], "keep": "wlt-c17-037", "edits": {},
     "note": "keep wlt-c17-037"},
    {"row_id": "row-00217", "delete": ["t4k-c02-074"], "keep": "t4k-c05-063", "edits": {},
     "note": "keep t4k-c05-063 (t4k-c02-074 was already deleted in batch 7)"},
    {"row_id": "row-00218", "delete": ["t4k-c03-067"], "keep": "thaipod-0121", "edits": {},
     "note": "keep thaipod-0121"},
    {"row_id": "row-00219", "delete": ["t4k-c03-072"], "keep": "yt-c22-056",
     "edits": {"yt-c22-056": {"thai": "เลี่ยง, หลีกเลี่ยง"}},
     "note": "merge as เลี่ยง, หลีกเลี่ยง"},
    {"row_id": "row-00220", "delete": ["t4k-c03-078"], "keep": "tsl-187", "edits": {},
     "note": "keep tsl-187"},
    {"row_id": "row-00221", "delete": ["t4k-c03-082"], "keep": "wlt-c05-078",
     "edits": {"wlt-c05-078": {"thai": "แข่ง, แข่งขัน"}},
     "note": "merge as แข่ง, แข่งขัน"},
    {"row_id": "row-00222", "delete": ["t4k-c03-093"], "keep": "wlt-c21-046",
     "edits": {"wlt-c21-046": {"english": "next, following; season; face"}},
     "note": "keep wlt-c21-046; restructure english"},
    {"row_id": "row-00223", "delete": ["t4k-c06-059"], "keep": "t4k-c04-004", "edits": {},
     "note": "keep t4k-c04-004"},
    {"row_id": "row-00224", "delete": ["t4k-c04-013", "thaipod-1396"], "keep": None, "edits": {},
     "note": "remove both"},
    # row-00225: keep both — no action
    {"row_id": "row-00226", "delete": ["t4k-c04-042"], "keep": "tobo-346", "edits": {},
     "note": "keep tobo-346"},
    {"row_id": "row-00227", "delete": ["t4k-c04-046"], "keep": "tamago-l12-650", "edits": {},
     "note": "keep tamago-l12-650"},
    {"row_id": "row-00228", "delete": ["t4k-c04-056"], "keep": "wlt-c21-005", "edits": {},
     "note": "keep wlt-c21-005"},
    {"row_id": "row-00229", "delete": ["tsl-486"], "keep": "t4k-c04-059", "edits": {},
     "note": "keep t4k-c04-059"},
    {"row_id": "row-00230", "delete": ["t4k-c04-097"], "keep": "wlt-c15-027", "edits": {},
     "note": "keep wlt-c15-027"},
    {"row_id": "row-00231", "delete": [], "keep": "t4k-c05-025",
     "edits": {"t4k-c05-025": {"english": "to absorb (e.g liquid), to wipe"}},
     "note": "keep both; tweak t4k-c05-025 english"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(211, 232)}


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

    log_lines = ["", "=" * 70, "Batch 8 — rows 211-231", ""]
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
