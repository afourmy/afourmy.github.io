"""Apply batch 47 (rows 935-950) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00935", "delete": ["tamago-l12-235", "yt-c02-084"], "keep": "yt-c02-094",
     "edits": {"yt-c02-094": {"thai": "นิ้วโป้ง, นิ้วหัวแม่มือ"}},
     "note": "keep yt-c02-094 as นิ้วโป้ง, นิ้วหัวแม่มือ"},
    # row-00936: keep both; wlt-c13-013 already updated by user (thai='ควร, ควรจะ')
    {"row_id": "row-00937", "delete": [], "keep": None,
     "edits": {"tobo-194": {"english": "to throw"}},
     "note": "keep both; tobo-194 english -> 'to throw'"},
    {"row_id": "row-00938", "delete": ["wlt-c14-016"], "keep": "tamago-l12-317", "edits": {},
     "note": "keep tamago-l12-317"},
    {"row_id": "row-00939", "delete": ["yt-c06-063"], "keep": "tamago-l12-344",
     "edits": {"tamago-l12-344": {"thai": "ยางแบน, ยางรั่ว"}},
     "note": "keep tamago-l12-344 as ยางแบน, ยางรั่ว"},
    {"row_id": "row-00940", "delete": ["yt-c08-046"], "keep": "tamago-l12-395",
     "edits": {"tamago-l12-395": {"thai": "วันหยุดราชการ, วันหยุดนักขัตฤกษ์"}},
     "note": "keep tamago-l12-395 as วันหยุดราชการ, วันหยุดนักขัตฤกษ์"},
    {"row_id": "row-00941", "delete": ["wlt-c05-029"], "keep": "tamago-l12-403", "edits": {},
     "note": "keep tamago-l12-403"},
    {"row_id": "row-00942", "delete": ["tamago-l12-438"], "keep": "thaipod-0609",
     "edits": {"thaipod-0609": {"thai": "ผา, หน้าผา"}},
     "note": "keep thaipod-0609 as ผา, หน้าผา"},
    {"row_id": "row-00944", "delete": ["yt-c01-032"], "keep": "tamago-l12-496",
     "edits": {"tamago-l12-496": {"thai": "เครื่องทำน้ำร้อน, เครื่องทำน้ำอุ่น"}},
     "note": "keep tamago-l12-496 as เครื่องทำน้ำร้อน, เครื่องทำน้ำอุ่น"},
    {"row_id": "row-00945", "delete": ["yt-c08-045"], "keep": "tamago-l12-506",
     "edits": {"tamago-l12-506": {"thai": "เจ้าของธุรกิจ, เจ้าของกิจการ"}},
     "note": "keep tamago-l12-506 as เจ้าของธุรกิจ, เจ้าของกิจการ"},
    {"row_id": "row-00946", "delete": ["tamago-l12-537"], "keep": "tamago-l3-800",
     "edits": {"tamago-l3-800": {"thai": "เปล่าๆ, โดยเปล่าประโยชน์"}},
     "note": "keep tamago-l3-800 as เปล่าๆ, โดยเปล่าประโยชน์"},
    {"row_id": "row-00947", "delete": [], "keep": None,
     "edits": {"thaipod-1328": {"frequency": "occasional", "english": "completely flat, flat and smooth"}},
     "note": "keep both; thaipod-1328 -> occasional, english -> 'completely flat, flat and smooth'"},
    {"row_id": "row-00948", "delete": ["wlt-c01-038"], "keep": "tamago-l12-632",
     "edits": {"tamago-l12-632": {"thai": "ไข่คน, ไข่กวน"}},
     "note": "keep tamago-l12-632 as ไข่คน, ไข่กวน"},
    {"row_id": "row-00949", "delete": ["wlt-c15-049"], "keep": "tamago-l3-056",
     "edits": {"tamago-l3-056": {"thai": "ใจ, จิตใจ"}},
     "note": "keep tamago-l3-056 as ใจ, จิตใจ"},
    {"row_id": "row-00950", "delete": ["wlt-c02-063"], "keep": "tamago-l3-059",
     "edits": {"tamago-l3-059": {"thai": "ลงโทษ, ทำโทษ"}},
     "note": "keep tamago-l3-059 as ลงโทษ, ทำโทษ"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(935, 951)}

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

    log_lines = ["", "=" * 70, "Batch 47 — rows 935-950", ""]
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
