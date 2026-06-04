"""Apply batch 51 (rows 981-996) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00981", "delete": ["thaipod-1044"], "keep": "thaipod-0818",
     "edits": {"thaipod-0818": {"thai": "รบ, สู้รบ"}},
     "note": "keep thaipod-0818 as รบ, สู้รบ"},
    {"row_id": "row-00983", "delete": ["yt-c05-041"], "keep": "thaipod-0861", "edits": {},
     "note": "keep thaipod-0861"},
    {"row_id": "row-00985", "delete": ["tobo-024"], "keep": "thaipod-0913",
     "edits": {"thaipod-0913": {"thai": "วรรณคดี, วรรณกรรม"}},
     "note": "keep thaipod-0913 as วรรณคดี, วรรณกรรม"},
    {"row_id": "row-00986", "delete": ["thaipod-0960"], "keep": "tsl-261",
     "edits": {"tsl-261": {"frequency": "occasional", "english": "living conditions, way of life"}},
     "note": "keep tsl-261 in occasional; english -> 'living conditions, way of life'"},
    {"row_id": "row-00987", "delete": ["wlt-c19-070"], "keep": "thaipod-1119", "edits": {},
     "note": "keep thaipod-1119"},
    {"row_id": "row-00988", "delete": ["yt-c22-032"], "keep": "thaipod-1379",
     "edits": {"thaipod-1379": {"thai": "โรงฆ่า, โรงฆ่าสัตว์"}},
     "note": "keep thaipod-1379 as โรงฆ่า, โรงฆ่าสัตว์"},
    {"row_id": "row-00989", "delete": [], "keep": None,
     "edits": {"yt-c23-013": {"frequency": "occasional", "english": "many people, various people"}},
     "note": "keep both; yt-c23-013 -> occasional, english -> 'many people, various people'"},
    {"row_id": "row-00990", "delete": ["wlt-c03-069"], "keep": "tobo-017", "edits": {},
     "note": "keep tobo-017"},
    {"row_id": "row-00991", "delete": ["wlt-c05-084"], "keep": "tobo-144", "edits": {},
     "note": "keep tobo-144"},
    {"row_id": "row-00992", "delete": [], "keep": None,
     "edits": {"yt-c04-010": {"frequency": "occasional", "english": "basket (gifts or decorative)"}},
     "note": "keep both; yt-c04-010 -> occasional, english -> 'basket (gifts or decorative)'"},
    {"row_id": "row-00993", "delete": [], "keep": None,
     "edits": {"yt-c01-097": {"english": "inmate, detainee"}},
     "note": "keep both; yt-c01-097 english -> 'inmate, detainee'"},
    {"row_id": "row-00994", "delete": ["tobo-329", "wlt-c03-008"], "keep": "wlt-c16-035",
     "edits": {"wlt-c16-035": {"frequency": "common"}},
     "note": "keep only wlt-c16-035 in common"},
    {"row_id": "row-00995", "delete": ["tobo-389"], "keep": "yt-c05-019",
     "edits": {"yt-c05-019": {"thai": "ถุย, ถุยน้ำลาย"}},
     "note": "keep yt-c05-019 as ถุย, ถุยน้ำลาย"},
    {"row_id": "row-00996", "delete": ["wlt-c05-000"], "keep": "tobo-414",
     "edits": {"tobo-414": {"thai": "ห้องนั่งเล่น, ห้องรับแขก"}},
     "note": "keep tobo-414 as ห้องนั่งเล่น, ห้องรับแขก"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(981, 997)}

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

    log_lines = ["", "=" * 70, "Batch 51 — rows 981-996", ""]
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
