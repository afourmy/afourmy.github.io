"""Apply batch 46 (rows 914-934) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00914", "delete": ["t4k-c08-037"], "keep": "tobo-074", "edits": {},
     "note": "keep tobo-074"},
    {"row_id": "row-00915", "delete": ["t4k-c08-087"], "keep": "wlt-c09-003",
     "edits": {"wlt-c09-003": {"thai": "กระสุน, ลูกปืน"}},
     "note": "keep wlt-c09-003 as กระสุน, ลูกปืน"},
    {"row_id": "row-00916", "delete": ["t4k-c09-012", "wlt-c02-021"], "keep": None, "edits": {},
     "note": "remove both (ละก็ / ตอนนั้น)"},
    {"row_id": "row-00917", "delete": ["t4k-c09-028"], "keep": "wlt-c12-021", "edits": {},
     "note": "keep wlt-c12-021"},
    {"row_id": "row-00918", "delete": ["t4k-c10-016"], "keep": "wlt-c11-037",
     "edits": {"wlt-c11-037": {"thai": "ประจำวัน, รายวัน"}},
     "note": "keep wlt-c11-037 as ประจำวัน, รายวัน"},
    {"row_id": "row-00919", "delete": ["t4k-c10-030"], "keep": "wlt-c13-046", "edits": {},
     "note": "keep wlt-c13-046"},
    {"row_id": "row-00920", "delete": ["t4k-c10-082"], "keep": "wlt-c08-039",
     "edits": {"wlt-c08-039": {"thai": "มือถือ, โทรศัพท์มือถือ"}},
     "note": "keep wlt-c08-039 as มือถือ, โทรศัพท์มือถือ"},
    {"row_id": "row-00922", "delete": ["t4k-c11-019"], "keep": "wlt-c20-037",
     "edits": {"wlt-c11-032": {"frequency": "occasional", "english": "father (formal)"}},
     "note": "keep wlt-c20-037 + wlt-c11-032; delete t4k-c11-019; wlt-c11-032 -> occasional, 'father (formal)'"},
    {"row_id": "row-00924", "delete": ["t4k-c11-106"], "keep": "wlt-c02-016", "edits": {},
     "note": "keep wlt-c02-016"},
    {"row_id": "row-00926", "delete": ["yt-c09-017"], "keep": "tamago-l12-112",
     "edits": {"tamago-l12-112": {"thai": "ฉลอง, เฉลิมฉลอง"}},
     "note": "keep tamago-l12-112 as ฉลอง, เฉลิมฉลอง"},
    {"row_id": "row-00927", "delete": ["wlt-c01-001"], "keep": "tamago-l12-136", "edits": {},
     "note": "keep tamago-l12-136"},
    {"row_id": "row-00928", "delete": ["tamago-l12-162"], "keep": "tobo-501",
     "edits": {"tobo-501": {"thai": "ต่างหู, ตุ้มหู"}},
     "note": "keep tobo-501 as ต่างหู, ตุ้มหู"},
    {"row_id": "row-00930", "delete": ["wlt-c02-078"], "keep": "wlt-c18-062",
     "edits": {
         "wlt-c18-062": {"thai": "ทุกครั้ง, ทุกที"},
         "tamago-l12-208": {"english": "whenever, every time that"},
     },
     "note": "keep wlt-c18-062 as ทุกครั้ง, ทุกที; delete wlt-c02-078; tamago-l12-208 english -> 'whenever, every time that'"},
    {"row_id": "row-00931", "delete": ["tamago-l12-209"], "keep": "tobo-028",
     "edits": {"tobo-028": {"thai": "ที่เป่าผม, ไดร์เป่าผม"}},
     "note": "keep tobo-028 as ที่เป่าผม, ไดร์เป่าผม"},
    {"row_id": "row-00932", "delete": ["tamago-l12-210"], "keep": "tobo-511",
     "edits": {"tobo-511": {"thai": "ที่โกนหนวด, มีดโกน"}},
     "note": "keep tobo-511 as ที่โกนหนวด, มีดโกน"},
    {"row_id": "row-00933", "delete": [], "keep": None,
     "edits": {"yt-c09-012": {"english": "custom, deep-rooted traditional norm"}},
     "note": "keep both; yt-c09-012 english -> 'custom, deep-rooted traditional norm'"},
    {"row_id": "row-00934", "delete": ["tamago-l12-225"], "keep": "tamago-l3-207",
     "edits": {"tamago-l3-207": {"thai": "นานๆที, นานๆครั้ง"}},
     "note": "keep tamago-l3-207 as นานๆที, นานๆครั้ง"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(914, 935)}

STALE_ROW_IDS = {"row-01130", "row-01133", "row-01134"}


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

    log_lines = ["", "=" * 70, "Batch 46 — rows 914-934 + stale cleanup", ""]
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
    if STALE_ROW_IDS:
        log_lines.append(f"Stale rows removed: {', '.join(sorted(STALE_ROW_IDS))}")
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
