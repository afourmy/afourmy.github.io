"""Apply batch 68 (rows pfx-0091 to pfx-0106) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-pfx-0091", "delete": [], "keep": None,
     "edits": {"yt-c02-013": {"frequency": "occasional"}},
     "note": "keep both; yt-c02-013 frequency -> occasional"},
    {"row_id": "row-pfx-0092", "delete": [], "keep": None,
     "edits": {"yt-c09-020": {"frequency": "occasional"}},
     "note": "keep both; yt-c09-020 frequency -> occasional"},
    {"row_id": "row-pfx-0093", "delete": [], "keep": None,
     "edits": {"thaipod-0186": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0186 frequency -> occasional"},
    {"row_id": "row-pfx-0094", "delete": [], "keep": None,
     "edits": {"t4k-c08-025": {"frequency": "occasional", "english": "justice, fairness"}},
     "note": "keep both; t4k-c08-025 -> 'justice, fairness', occasional"},
    # row-pfx-0095: keep both — no changes
    {"row_id": "row-pfx-0096", "delete": [], "keep": None,
     "edits": {"thaipod-0187": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0187 frequency -> occasional"},
    # row-pfx-0097: keep both — no changes
    {"row_id": "row-pfx-0098", "delete": [], "keep": None,
     "edits": {"tamago-l12-367": {"english": "to take responsibility, to be responsible"}},
     "note": "keep both; tamago-l12-367 english -> 'to take responsibility, to be responsible'"},
    {"row_id": "row-pfx-0099", "delete": [], "keep": None,
     "edits": {"wlt-c04-026": {"english": "violent, harsh"}},
     "note": "keep both; wlt-c04-026 english -> 'violent, harsh'"},
    # row-pfx-0100: keep both — no changes
    # row-pfx-0101: keep both — no changes
    # row-pfx-0102: keep both — no changes
    {"row_id": "row-pfx-0103", "delete": [], "keep": None,
     "edits": {"yt-c17-024": {"frequency": "occasional", "english": "precision, resolution, fineness"}},
     "note": "keep both; yt-c17-024 -> 'precision, resolution, fineness', occasional"},
    # row-pfx-0104: keep both — no changes
    {"row_id": "row-pfx-0105", "delete": [], "keep": None,
     "edits": {
         "yt-c06-031": {"english": "faith, belief, to have faith in (e.g Buddhism)"},
         "thaipod-0190": {"frequency": "occasional"},
     },
     "note": "keep both; yt-c06-031 -> 'faith, belief, to have faith in (e.g Buddhism)'; thaipod-0190 -> occasional"},
    {"row_id": "row-pfx-0106", "delete": [], "keep": None,
     "edits": {"thaipod-0193": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0193 frequency -> occasional"},
]

APPLIED_ROW_IDS = {f"row-pfx-{i:04d}" for i in range(91, 107)}

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

    log_lines = ["", "=" * 70, "Batch 68 — rows pfx-0091 to pfx-0106", ""]
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
