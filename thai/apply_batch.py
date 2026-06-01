"""Apply batch 26 (rows 545-562) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00545", "delete": ["tobo-353"], "keep": "wlt-c09-028", "edits": {},
     "note": "keep wlt-c09-028"},
    {"row_id": "row-00546", "delete": [], "keep": None,
     "edits": {"tsl-542": {"frequency": "rare", "english": "to crunch, to chew on snacks"}},
     "note": "keep both; tsl-542 to rare, english -> 'to crunch, to chew on snacks'"},
    # row-00547: keep both — no action
    {"row_id": "row-00548", "delete": ["wlt-c03-041"], "keep": "tobo-412", "edits": {},
     "note": "keep tobo-412"},
    {"row_id": "row-00549", "delete": [], "keep": None,
     "edits": {"tobo-419": {"english": "to sweat"}},
     "note": "keep both; remove 'sweaty' from tobo-419 english"},
    {"row_id": "row-00550", "delete": [], "keep": None,
     "edits": {"wlt-c09-080": {"frequency": "everyday", "english": "to permit"}},
     "note": "keep both; wlt-c09-080 to everyday, english -> 'to permit'"},
    # row-00551: keep both — no action
    {"row_id": "row-00552", "delete": ["tobo-500"], "keep": "wlt-c02-022",
     "edits": {"wlt-c02-022": {"english": "to receive, to welcome"}},
     "note": "keep wlt-c02-022, english -> 'to receive, to welcome'"},
    {"row_id": "row-00553", "delete": [], "keep": None,
     "edits": {
         "tobo-515": {"frequency": "everyday"},
         "yt-c19-074": {"frequency": "occasional"},
     },
     "note": "keep both; tobo-515 to everyday, yt-c19-074 to occasional"},
    {"row_id": "row-00554", "delete": ["yt-c19-084"], "keep": "tsl-075",
     "edits": {"tsl-075": {"thai": "บ้านนอก, ชนบท", "english": "countryside, village", "frequency": "everyday"}},
     "note": "keep tsl-075 as บ้านนอก, ชนบท: countryside, village, move to everyday"},
    {"row_id": "row-00555", "delete": ["yt-c12-089"], "keep": "tsl-093",
     "edits": {"tsl-093": {"thai": "มุก, ไข่มุก"}},
     "note": "keep tsl-093 as มุก, ไข่มุก"},
    # row-00556: keep both — no action
    {"row_id": "row-00557", "delete": [], "keep": None,
     "edits": {"yt-c05-077": {"frequency": "rare"}},
     "note": "keep both; yt-c05-077 to rare"},
    {"row_id": "row-00558", "delete": [], "keep": None,
     "edits": {
         "tsl-127": {"thai": "โม้", "english": "to brag, to boast, to exaggerate", "frequency": "occasional"},
         "yt-c14-032": {"frequency": "occasional"},
     },
     "note": "keep both at occasional; tsl-127 -> โม้: to brag, to boast, to exaggerate"},
    {"row_id": "row-00559", "delete": ["wlt-c18-081"], "keep": "tsl-135",
     "edits": {"tsl-135": {"thai": "บูด, เน่า, บูดเน่า"}},
     "note": "keep tsl-135 as บูด, เน่า, บูดเน่า"},
    {"row_id": "row-00560", "delete": ["yt-c08-035"], "keep": "tsl-135", "edits": {},
     "note": "delete yt-c08-035 (เน่า merged into tsl-135 per row-00559)"},
    {"row_id": "row-00561", "delete": ["tsl-158"], "keep": "yt-c03-047", "edits": {},
     "note": "keep yt-c03-047"},
    # row-00562: keep both — no action
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(545, 563)}


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

    log_lines = ["", "=" * 70, "Batch 26 — rows 545-562", ""]
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
