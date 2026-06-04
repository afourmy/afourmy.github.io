"""Apply batch 55 (rows 1045-1060) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01045", "delete": ["wlt-c11-064"], "keep": "wlt-c11-006",
     "edits": {"wlt-c11-006": {"thai": "น้องเขย, พี่เขย"}},
     "note": "keep wlt-c11-006 as น้องเขย, พี่เขย"},
    {"row_id": "row-01048", "delete": ["wlt-c14-042"], "keep": "wlt-c20-014",
     "edits": {"wlt-c20-014": {"thai": "ดีใจ, ยินดี"}},
     "note": "keep wlt-c20-014 as ดีใจ, ยินดี"},
    {"row_id": "row-01049", "delete": ["wlt-c14-074", "wlt-c14-075"], "keep": None, "edits": {},
     "note": "remove both (สวิตเซอร์แลนด์ / สวิส)"},
    {"row_id": "row-01050", "delete": ["wlt-c17-021", "wlt-c17-040"], "keep": None, "edits": {},
     "note": "remove both (เปล่า / ไม่)"},
    {"row_id": "row-01051", "delete": [], "keep": None,
     "edits": {
         "wlt-c21-010": {"english": "to watch, to look at"},
         "wlt-c17-033": {"english": "to look, to gaze"},
     },
     "note": "keep both; wlt-c21-010 and wlt-c17-033 english disambiguated"},
    {"row_id": "row-01052", "delete": ["wlt-c18-014", "wlt-c19-056"], "keep": None, "edits": {},
     "note": "remove both (คนหนึ่ง / หนึ่งคน)"},
    {"row_id": "row-01053", "delete": ["wlt-c18-095"], "keep": "wlt-c18-049", "edits": {},
     "note": "keep wlt-c18-049"},
    {"row_id": "row-01054", "delete": ["wlt-c19-036", "wlt-c19-037"], "keep": None, "edits": {},
     "note": "remove both (ลองดู / ลองใส่)"},
    {"row_id": "row-01055", "delete": ["yt-c07-025"], "keep": "yt-c04-034",
     "edits": {"yt-c04-034": {"thai": "นอบน้อมถ่อมตน, อ่อนน้อมถ่อมตน"}},
     "note": "keep yt-c04-034 as นอบน้อมถ่อมตน, อ่อนน้อมถ่อมตน"},
    {"row_id": "row-01056", "delete": [], "keep": None,
     "edits": {"yt-c06-022": {"frequency": "occasional", "english": "alone, isolated"}},
     "note": "keep both; yt-c06-022 -> occasional, english -> 'alone, isolated'"},
    {"row_id": "row-01057", "delete": ["yt-c10-065"], "keep": "yt-c08-047",
     "edits": {"yt-c08-047": {"thai": "ความชอบส่วนตัว, ความชอบส่วนบุคคล"}},
     "note": "keep yt-c08-047 as ความชอบส่วนตัว, ความชอบส่วนบุคคล"},
    {"row_id": "row-01058", "delete": ["yt-c22-003"], "keep": "yt-c09-032", "edits": {},
     "note": "keep yt-c09-032"},
    {"row_id": "row-01059", "delete": [], "keep": None,
     "edits": {
         "yt-c15-090": {"english": "unlucky, unfortunate", "frequency": "rare"},
         "yt-c09-039": {"english": "to have bad luck (astrology)"},
     },
     "note": "keep both; yt-c15-090 -> rare, english updated; yt-c09-039 english -> 'to have bad luck (astrology)'"},
    {"row_id": "row-01060", "delete": ["yt-c17-026"], "keep": "yt-c09-040",
     "edits": {"yt-c09-040": {"thai": "ทําโอที, ทํางานนอกเวลา, ทํางานล่วงเวลา"}},
     "note": "keep yt-c09-040 as ทําโอที, ทํางานนอกเวลา, ทํางานล่วงเวลา"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1045, 1061)}

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

    log_lines = ["", "=" * 70, "Batch 55 — rows 1045-1060", ""]
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
