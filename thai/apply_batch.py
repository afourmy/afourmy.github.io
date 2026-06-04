"""Apply batch 52 (rows 997-1014) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00997", "delete": [], "keep": None,
     "edits": {"tobo-450": {"english": "to tease light-heartedly, to gently provoke"}},
     "note": "keep both; tobo-450 english updated"},
    {"row_id": "row-00998", "delete": ["tobo-466"], "keep": "yt-c09-058",
     "edits": {"yt-c09-058": {"thai": "พลุ, ดอกไม้ไฟ"}},
     "note": "keep yt-c09-058 as พลุ, ดอกไม้ไฟ"},
    {"row_id": "row-00999", "delete": [], "keep": None,
     "edits": {
         "tsl-157": {"english": "hole, small opening, cavity"},
         "yt-c01-082": {"english": "cavity, hollow space (e.g. in nature)"},
     },
     "note": "keep both; tsl-157 and yt-c01-082 english disambiguated"},
    {"row_id": "row-01000", "delete": ["tsl-420"], "keep": "yt-c03-042",
     "edits": {"yt-c03-042": {"thai": "สบตา, สบสายตา"}},
     "note": "keep yt-c03-042 as สบตา, สบสายตา"},
    {"row_id": "row-01002", "delete": ["wlt-c01-012"], "keep": "yt-c22-069",
     "edits": {"yt-c22-069": {"thai": "เก็บเงิน, เก็บออมเงิน"}},
     "note": "keep yt-c22-069 as เก็บเงิน, เก็บออมเงิน"},
    {"row_id": "row-01003", "delete": ["wlt-c01-031"], "keep": "wlt-c15-007", "edits": {},
     "note": "keep wlt-c15-007"},
    {"row_id": "row-01004", "delete": ["wlt-c01-048"], "keep": "wlt-c01-049", "edits": {},
     "note": "keep only wlt-c01-049"},
    {"row_id": "row-01005", "delete": [], "keep": None,
     "edits": {"wlt-c06-021": {"english": "whoever"}},
     "note": "keep both; wlt-c06-021 english -> 'whoever'"},
    {"row_id": "row-01006", "delete": ["wlt-c19-012"], "keep": "wlt-c01-066",
     "edits": {"wlt-c01-066": {"english": "someone, a certain person"}},
     "note": "keep wlt-c01-066; english -> 'someone, a certain person'"},
    {"row_id": "row-01007", "delete": ["wlt-c18-046"], "keep": "wlt-c01-099",
     "edits": {"wlt-c01-099": {"thai": "เด็กชาย, เด็กผู้ชาย"}},
     "note": "keep wlt-c01-099 as เด็กชาย, เด็กผู้ชาย"},
    {"row_id": "row-01008", "delete": ["wlt-c18-047"], "keep": "wlt-c02-000",
     "edits": {"wlt-c02-000": {"thai": "เด็กหญิง, เด็กผู้หญิง"}},
     "note": "keep wlt-c02-000 as เด็กหญิง, เด็กผู้หญิง"},
    {"row_id": "row-01010", "delete": ["wlt-c02-014"], "keep": "wlt-c07-011",
     "edits": {"wlt-c07-011": {"thai": "ตลอดวัน, ทั้งวัน"}},
     "note": "keep wlt-c07-011 as ตลอดวัน, ทั้งวัน"},
    {"row_id": "row-01012", "delete": ["wlt-c02-065"], "keep": "wlt-c10-089", "edits": {},
     "note": "keep wlt-c10-089"},
    {"row_id": "row-01013", "delete": ["wlt-c11-002"], "keep": None,
     "edits": {
         "wlt-c09-019": {"english": "second (unit of time)"},
         "wlt-c02-071": {"english": "second (2nd)"},
     },
     "note": "remove wlt-c11-002; wlt-c09-019 and wlt-c02-071 english disambiguated"},
    {"row_id": "row-01014", "delete": [], "keep": None,
     "edits": {
         "wlt-c03-004": {"thai": "นึกถึง", "english": "to think of, to recall"},
         "wlt-c06-011": {"thai": "คำนึง, คำนึงถึง", "english": "to think deeply, to take into consideration"},
     },
     "note": "keep both; wlt-c03-004 thai -> นึกถึง, english updated; wlt-c06-011 thai/english updated; ดำริ split into new card wlt-c03-004b"},
]

# New entries to insert (splits from existing cards)
CREATES = [
    {
        "id": "wlt-c03-004b",
        "thai": "ดำริ",
        "english": "to have an idea, to conceive (royal)",
        "topic": "monarchy",
        "frequency": "rare",
        "sources": ["Anki Basics"],
        "insert_after": "wlt-c03-004",
    },
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(997, 1015)}

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

    # Insert new entries after their anchor
    for c in CREATES:
        anchor = c.pop("insert_after")
        entry = {k: v for k, v in c.items()}
        idx = next((i for i, e in enumerate(new_vocab) if e["id"] == anchor), None)
        if idx is not None:
            new_vocab.insert(idx + 1, entry)
        else:
            new_vocab.append(entry)

    log_lines = ["", "=" * 70, "Batch 52 — rows 997-1014", ""]
    for m in MUTATIONS:
        log_lines.append(f"[{m['row_id']}] {m['note']}")
        if m["delete"]:
            log_lines.append(f"    delete: {', '.join(m['delete'])}")
        if m["keep"]:
            log_lines.append(f"    keep:   {m['keep']}")
        for eid, fields in m["edits"].items():
            for fk, fv in fields.items():
                log_lines.append(f"    edit {eid}.{fk} = {fv!r}")
    log_lines.append(f"    create: wlt-c03-004b (ดำริ)")
    log_lines.append("")
    if skipped_missing:
        log_lines.append("Skipped (entry already deleted in a prior batch):")
        for r, k, eid in skipped_missing:
            log_lines.append(f"    {r}: {k} {eid}")
        log_lines.append("")
    log_lines.append(f"Total deletions this batch: {len(to_delete)}")
    log_lines.append(f"Total source-unions:        {len(sources_into)}")
    log_lines.append(f"Total field-edits:          {sum(len(v) for v in field_edits.values())}")
    log_lines.append(f"Total creates:              {len(CREATES)}")
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
