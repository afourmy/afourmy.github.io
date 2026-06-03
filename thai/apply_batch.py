"""Apply batch 41 (rows 827-838) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    # row-00826: absent
    {"row_id": "row-00827", "delete": ["wlt-c04-010"], "keep": "chula-l4-102", "edits": {},
     "note": "keep chula-l4-102"},
    {"row_id": "row-00828", "delete": [], "keep": None,
     "edits": {"tobo-210": {"english": "competitive advantage", "frequency": "occasional"}},
     "note": "keep both; tobo-210 english -> 'competitive advantage', occasional"},
    # row-00829: absent (stale)
    {"row_id": "row-00830", "delete": [], "keep": None,
     "edits": {
         "yt-c22-050": {"frequency": "occasional"},
         "chula-l5-006": {"english": "cost, expenses"},
     },
     "note": "keep both; yt-c22-050 -> occasional; chula-l5-006 english -> 'cost, expenses'"},
    {"row_id": "row-00831", "delete": [], "keep": None,
     "edits": {"chula-l5-011": {"english": "savings (account)"}},
     "note": "keep both; chula-l5-011 english -> 'savings (account)'"},
    {"row_id": "row-00832", "delete": ["tamago-l3-734"], "keep": "chula-l5-073",
     "edits": {"chula-l5-073": {"thai": "หลักฐาน, เครื่องพิสูจน์"}},
     "note": "keep chula-l5-073 as หลักฐาน, เครื่องพิสูจน์"},
    {"row_id": "row-00833", "delete": ["t4k-c05-000", "thaipod-0053"], "keep": "chula-l5-090",
     "edits": {},
     "note": "keep chula-l5-090; delete t4k-c05-000, thaipod-0053"},
    {"row_id": "row-00834", "delete": [], "keep": None,
     "edits": {
         "chula-l5-109": {"english": "painting (art)"},
         "tobo-135": {"english": "painting, drawing"},
     },
     "note": "keep both; chula-l5-109 english -> 'painting (art)'; tobo-135 english -> 'painting, drawing'"},
    {"row_id": "row-00835", "delete": ["wlt-c11-015"], "keep": "chula-l5-114",
     "edits": {"chula-l5-114": {"thai": "นา, ทุ่งนา"}},
     "note": "keep chula-l5-114 as นา, ทุ่งนา"},
    {"row_id": "row-00836", "delete": [], "keep": None,
     "edits": {
         "yt-c10-079": {"english": "to be hooked on sth, swept in (slang)"},
         "chula-l5-116": {"english": "to be infatuated, to be deeply in love"},
     },
     "note": "keep all 3; yt-c10-079 and chula-l5-116 english updated"},
    {"row_id": "row-00837", "delete": ["t4k-c10-043", "wlt-c03-083"], "keep": "chula-l5-120",
     "edits": {"chula-l5-120": {"thai": "โด่งดัง, ชื่อดัง, มีชื่อเสียง"}},
     "note": "keep chula-l5-120 as โด่งดัง, ชื่อดัง, มีชื่อเสียง"},
    {"row_id": "row-00838", "delete": [], "keep": None,
     "edits": {"chula-l5-139": {"english": "upside down, to overturn, to capsize"}},
     "note": "keep both; chula-l5-139 english -> 'upside down, to overturn, to capsize'"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(827, 839)}

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

    log_lines = ["", "=" * 70, "Batch 41 — rows 827-838", ""]
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
