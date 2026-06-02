"""Apply batch 30 (rows 628-649) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00628", "delete": ["wlt-c20-003"], "keep": "wlt-c06-014", "edits": {},
     "note": "keep wlt-c06-014"},
    # row-00629: keep both; wlt-c06-027 frequency="occasional"
    {"row_id": "row-00629", "delete": [], "keep": None,
     "edits": {"wlt-c06-027": {"frequency": "occasional"}},
     "note": "keep both; wlt-c06-027 frequency -> occasional"},
    {"row_id": "row-00630", "delete": ["wlt-c06-033"], "keep": "wlt-c21-005", "edits": {},
     "note": "keep wlt-c21-005"},
    {"row_id": "row-00631", "delete": ["wlt-c06-054"], "keep": "wlt-c06-053",
     "edits": {"wlt-c06-053": {"thai": "ซื่อ, ซื่อตรง"}},
     "note": "keep wlt-c06-053 as ซื่อ, ซื่อตรง"},
    # row-00632: keep both — no action
    # row-00633: keep both; edits only
    {"row_id": "row-00633", "delete": [], "keep": None,
     "edits": {"wlt-c06-071": {"frequency": "everyday", "english": "forever"}},
     "note": "keep both; wlt-c06-071 frequency -> everyday, english -> forever"},
    {"row_id": "row-00634", "delete": [], "keep": None,
     "edits": {"wlt-c06-072": {"frequency": "everyday"}},
     "note": "keep both; wlt-c06-072 frequency -> everyday"},
    {"row_id": "row-00635", "delete": ["wlt-c06-088"], "keep": "wlt-c06-089",
     "edits": {"wlt-c06-089": {"thai": "เต้น, เต้นรำ"}},
     "note": "keep wlt-c06-089 as เต้น, เต้นรำ"},
    {"row_id": "row-00636", "delete": [], "keep": None,
     "edits": {
         "wlt-c06-090": {"frequency": "occasional"},
         "wlt-c12-002": {"frequency": "occasional"},
     },
     "note": "keep both at occasional"},
    {"row_id": "row-00637", "delete": ["yt-c04-049"], "keep": "wlt-c07-009", "edits": {},
     "note": "keep wlt-c07-009"},
    # row-00638: absent
    # row-00639: absent
    {"row_id": "row-00640", "delete": ["wlt-c07-038"], "keep": "wlt-c20-026", "edits": {},
     "note": "keep wlt-c20-026"},
    {"row_id": "row-00641", "delete": ["wlt-c07-071"], "keep": "wlt-c07-070", "edits": {},
     "note": "keep wlt-c07-070"},
    {"row_id": "row-00642", "delete": ["wlt-c07-078"], "keep": "wlt-c15-040", "edits": {},
     "note": "keep wlt-c15-040"},
    # row-00643: absent
    {"row_id": "row-00644", "delete": ["wlt-c08-002"], "keep": "wlt-c11-056",
     "edits": {"wlt-c11-056": {"thai": "ฝึก, หัด, ฝึกหัด", "frequency": "everyday"}},
     "note": "keep wlt-c11-056 as ฝึก, หัด, ฝึกหัด; frequency -> everyday"},
    {"row_id": "row-00645", "delete": ["yt-c15-064"], "keep": None, "edits": {},
     "note": "delete yt-c15-064; wlt-c08-002 already deleted in row-00644"},
    {"row_id": "row-00646", "delete": ["wlt-c08-009", "wlt-c18-012"], "keep": None, "edits": {},
     "note": "remove both"},
    {"row_id": "row-00647", "delete": ["wlt-c08-010"], "keep": "wlt-c16-020", "edits": {},
     "note": "keep wlt-c16-020"},
    {"row_id": "row-00648", "delete": [], "keep": None,
     "edits": {
         "wlt-c08-021": {"frequency": "everyday"},
         "yt-c13-021": {"frequency": "rare", "english": "gender identity"},
     },
     "note": "keep both; wlt-c08-021 frequency -> everyday; yt-c13-021 frequency -> rare, english -> gender identity"},
    {"row_id": "row-00649", "delete": ["wlt-c08-022"], "keep": "wlt-c11-065",
     "edits": {"wlt-c11-065": {"thai": "เพิ่ม, เพิ่มขึ้น"}},
     "note": "keep wlt-c11-065 as เพิ่ม, เพิ่มขึ้น"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(628, 650)}

STALE_ROW_IDS = {
    "row-00808", "row-01022", "row-01030", "row-01263", "row-01270",
}


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

    log_lines = ["", "=" * 70, "Batch 30 — rows 628-649", ""]
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
    print(f"decisions.json: {before} -> {doc['total_rows']} rows ({before - doc['total_rows']} removed, incl. {len(STALE_ROW_IDS)} stale)")
    if skipped_missing:
        print(f"Skipped {len(skipped_missing)} already-deleted refs (see apply_log.txt)")
    print(f"log appended to: {log_path.name}")


if __name__ == "__main__":
    main()
