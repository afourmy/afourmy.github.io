"""Apply batch 54 (rows 1029-1044) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01029", "delete": [], "keep": None,
     "edits": {
         "wlt-c04-087": {"english": "underwear (upper body)"},
         "wlt-c05-049": {"english": "underwear (lower body)"},
     },
     "note": "keep both; wlt-c04-087 english -> 'underwear (upper body)'; wlt-c05-049 -> 'underwear (lower body)'"},
    {"row_id": "row-01031", "delete": ["wlt-c05-007", "wlt-c20-081"], "keep": None, "edits": {},
     "note": "remove both (เหลอ / หรือ)"},
    {"row_id": "row-01032", "delete": ["wlt-c05-019"], "keep": "wlt-c09-092",
     "edits": {"wlt-c09-092": {"thai": "อาทิตย์ที่แล้ว, อาทิตย์ก่อน"}},
     "note": "keep wlt-c09-092 as อาทิตย์ที่แล้ว, อาทิตย์ก่อน"},
    {"row_id": "row-01033", "delete": ["wlt-c05-022"], "keep": "wlt-c12-084", "edits": {},
     "note": "keep wlt-c12-084"},
    {"row_id": "row-01034", "delete": ["wlt-c06-001"], "keep": "wlt-c05-094", "edits": {},
     "note": "keep wlt-c05-094"},
    {"row_id": "row-01036", "delete": [], "keep": None,
     "edits": {
         "wlt-c07-002": {"english": "to flood"},
         "yt-c10-085": {"english": "to overflow, to spill over"},
     },
     "note": "keep both; wlt-c07-002 english -> 'to flood'; yt-c10-085 -> 'to overflow, to spill over'"},
    {"row_id": "row-01037", "delete": [], "keep": None,
     "edits": {
         "wlt-c07-007": {"english": "to memorize by repetition"},
         "yt-c03-005": {"english": "to remember, to retain in memory"},
     },
     "note": "keep both; wlt-c07-007 and yt-c03-005 english disambiguated"},
    {"row_id": "row-01038", "delete": ["wlt-c07-025"], "keep": "wlt-c17-049",
     "edits": {"wlt-c17-049": {"thai": "แรก, ที่หนึ่ง"}},
     "note": "keep wlt-c17-049 as แรก, ที่หนึ่ง"},
    {"row_id": "row-01039", "delete": ["wlt-c07-037"], "keep": "wlt-c08-018",
     "edits": {"wlt-c08-018": {"frequency": "occasional", "thai": "น้องสะใภ้, พี่สะใภ้"}},
     "note": "keep wlt-c08-018 as น้องสะใภ้, พี่สะใภ้, occasional"},
    {"row_id": "row-01040", "delete": ["wlt-c08-015"], "keep": "yt-c11-008",
     "edits": {"yt-c11-008": {"thai": "พิพิธภัณฑ์, พิพิธภัณฑสถาน"}},
     "note": "keep yt-c11-008 as พิพิธภัณฑ์, พิพิธภัณฑสถาน"},
    {"row_id": "row-01041", "delete": ["wlt-c08-054"], "keep": "wlt-c14-063",
     "edits": {"wlt-c14-063": {"frequency": "occasional", "english": "morally bad, evil"}},
     "note": "keep wlt-c14-063 occasional; english -> 'morally bad, evil'"},
    {"row_id": "row-01042", "delete": ["wlt-c12-054"], "keep": "wlt-c08-091",
     "edits": {"wlt-c08-091": {"thai": "ฤดูฝน, หน้าฝน"}},
     "note": "keep wlt-c08-091 as ฤดูฝน, หน้าฝน"},
    {"row_id": "row-01043", "delete": ["wlt-c09-006"], "keep": "wlt-c12-018",
     "edits": {"wlt-c12-018": {"thai": "เลขา, เลขานุการ"}},
     "note": "keep wlt-c12-018 as เลขา, เลขานุการ"},
    # row-01044: wlt-c09-069 already occasional with thai 'หาก, ถ้าหาก'; just add (literary) to english
    {"row_id": "row-01044", "delete": [], "keep": None,
     "edits": {"wlt-c09-069": {"english": "if (literary)"}},
     "note": "keep both; wlt-c09-069 english -> 'if (literary)' (freq/thai already set)"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(1029, 1045)}

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

    log_lines = ["", "=" * 70, "Batch 54 — rows 1029-1044", ""]
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
