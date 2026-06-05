"""Apply batch 69 (rows pfx-0107 to pfx-0131) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-pfx-0107", "delete": [], "keep": None,
     "edits": {"yt-c01-014": {"frequency": "occasional"}},
     "note": "keep both; yt-c01-014 frequency -> occasional"},
    {"row_id": "row-pfx-0108", "delete": ["t4k-c01-046"], "keep": "chula-l5-372",
     "edits": {},
     "note": "remove t4k-c01-046; keep chula-l5-372"},
    {"row_id": "row-pfx-0109", "delete": [], "keep": None,
     "edits": {"wlt-c14-082": {"frequency": "everyday"}},
     "note": "keep both; wlt-c14-082 frequency -> everyday"},
    # row-pfx-0110: keep both — no changes
    {"row_id": "row-pfx-0111", "delete": [], "keep": None,
     "edits": {"wlt-c21-044": {"english": "tall"}},
     "note": "keep both; wlt-c21-044 english -> 'tall'"},
    {"row_id": "row-pfx-0112", "delete": ["t4k-c01-061"], "keep": "wlt-c10-038",
     "edits": {},
     "note": "remove t4k-c01-061; keep wlt-c10-038"},
    {"row_id": "row-pfx-0113", "delete": [], "keep": None,
     "edits": {"tsl-099": {"frequency": "occasional"}},
     "note": "keep both; tsl-099 frequency -> occasional"},
    # row-pfx-0114: keep both — no changes
    {"row_id": "row-pfx-0115", "delete": [], "keep": None,
     "edits": {"t4k-c02-029": {"english": "various, many"}},
     "note": "keep both; t4k-c02-029 english -> 'various, many'"},
    # row-pfx-0116: keep both — no changes
    # row-pfx-0117: keep both — no changes
    # row-pfx-0118: keep both — no changes
    # row-pfx-0119: keep both — no changes
    {"row_id": "row-pfx-0120", "delete": [], "keep": None,
     "edits": {"yt-c06-025": {"english": "gentleness, tenderness"}},
     "note": "keep both; yt-c06-025 english -> 'gentleness, tenderness'"},
    # row-pfx-0121: keep both — no changes
    # row-pfx-0122: keep both — no changes
    {"row_id": "row-pfx-0123", "delete": [], "keep": None,
     "edits": {"t4k-c04-066": {"english": "hurt, painful, to be in pain"}},
     "note": "keep both; t4k-c04-066 english -> 'hurt, painful, to be in pain'"},
    {"row_id": "row-pfx-0124", "delete": [], "keep": None,
     "edits": {"wlt-c15-054": {"english": "to believe"}},
     "note": "keep both; wlt-c15-054 english -> 'to believe'"},
    {"row_id": "row-pfx-0125", "delete": [], "keep": None,
     "edits": {"yt-c08-069": {"english": "to be in trouble, to be in difficulty"}},
     "note": "keep both; yt-c08-069 english -> 'to be in trouble, to be in difficulty'"},
    {"row_id": "row-pfx-0126", "delete": [], "keep": None,
     "edits": {"wlt-c02-040": {"english": "willing, glad to do sth"}},
     "note": "keep both; wlt-c02-040 english -> 'willing, glad to do sth'"},
    {"row_id": "row-pfx-0127", "delete": ["thaipod-0198"], "keep": "wlt-c20-032",
     "edits": {"wlt-c20-032": {"english": "to be; to be able"}},
     "note": "remove thaipod-0198; wlt-c20-032 english -> 'to be; to be able'"},
    {"row_id": "row-pfx-0128", "delete": [], "keep": None,
     "edits": {"yt-c02-042": {"frequency": "occasional"}},
     "note": "keep both; yt-c02-042 frequency -> occasional"},
    {"row_id": "row-pfx-0129", "delete": [], "keep": None,
     "edits": {"yt-c03-011": {"english": "compassion, deep kindness"}},
     "note": "keep both; yt-c03-011 english -> 'compassion, deep kindness'"},
    {"row_id": "row-pfx-0130", "delete": [], "keep": None,
     "edits": {"thaipod-0201": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0201 frequency -> occasional"},
    # row-pfx-0131: keep both — no changes
]

APPLIED_ROW_IDS = {f"row-pfx-{i:04d}" for i in range(107, 132)}

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

    log_lines = ["", "=" * 70, "Batch 69 — rows pfx-0107 to pfx-0131", ""]
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
