"""Apply batch 9 (rows 232-252) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    # row-00232: keep both — no action
    {"row_id": "row-00233", "delete": ["wlt-c01-088"], "keep": "t4k-c05-046", "edits": {},
     "note": "keep t4k-c05-046"},
    {"row_id": "row-00234", "delete": ["t4k-c09-088"], "keep": "t4k-c05-051", "edits": {},
     "note": "keep t4k-c05-051"},
    {"row_id": "row-00235", "delete": ["t4k-c05-055"], "keep": "wlt-c20-065", "edits": {},
     "note": "keep wlt-c20-065"},
    {"row_id": "row-00236", "delete": ["tobo-508"], "keep": "t4k-c05-096", "edits": {},
     "note": "keep t4k-c05-096"},
    {"row_id": "row-00237", "delete": ["t4k-c06-000"], "keep": "wlt-c06-044", "edits": {},
     "note": "keep wlt-c06-044"},
    {"row_id": "row-00238", "delete": ["t4k-c06-007"], "keep": "tamago-l3-276",
     "edits": {"tamago-l3-276": {"thai": "ทัก, ทักทาย", "english": "to greet, to say hi"}},
     "note": "merge as ทัก, ทักทาย: to greet, to say hi"},
    {"row_id": "row-00239", "delete": ["t4k-c06-020"], "keep": "tobo-206", "edits": {},
     "note": "keep tobo-206"},
    {"row_id": "row-00240", "delete": ["t4k-c06-044"], "keep": "wlt-c08-064", "edits": {},
     "note": "keep wlt-c08-064"},
    # row-00241: keep both — no action
    {"row_id": "row-00242", "delete": ["t4k-c06-082"], "keep": "wlt-c15-022", "edits": {},
     "note": "keep wlt-c15-022"},
    {"row_id": "row-00243", "delete": ["thai9k-006"], "keep": "t4k-c07-012",
     "edits": {"t4k-c07-012": {"thai": "อรุณ, รุ่งอรุณ"}},
     "note": "merge as อรุณ, รุ่งอรุณ"},
    {"row_id": "row-00244", "delete": ["t4k-c07-034"], "keep": "wlt-c17-001",
     "edits": {"wlt-c17-001": {"thai": "ทอง, ทองคำ"}},
     "note": "merge as ทอง, ทองคำ"},
    {"row_id": "row-00245", "delete": [], "keep": "t4k-c07-053",
     "edits": {"t4k-c07-053": {"english": "peace (opposite of war)"}},
     "note": "keep both; clarify t4k-c07-053 english"},
    {"row_id": "row-00246", "delete": [], "keep": "t4k-c07-054",
     "edits": {"t4k-c07-054": {"frequency": "occasional",
                                 "english": "to adhere to, to be committed to"}},
     "note": "keep both; move ยึดมั่น to occasional + update english"},
    {"row_id": "row-00247", "delete": ["t4k-c07-066"], "keep": "wlt-c20-066", "edits": {},
     "note": "keep wlt-c20-066"},
    {"row_id": "row-00248", "delete": ["t4k-c07-094"], "keep": "wlt-c20-080",
     "edits": {"wlt-c20-080": {"thai": "หน่อย, สักหน่อย"}},
     "note": "merge as หน่อย, สักหน่อย"},
    {"row_id": "row-00249", "delete": ["t4k-c08-015"], "keep": "wlt-c20-000", "edits": {},
     "note": "keep wlt-c20-000"},
    {"row_id": "row-00250", "delete": ["t4k-c08-038"], "keep": "wlt-c20-064", "edits": {},
     "note": "keep wlt-c20-064"},
    {"row_id": "row-00251", "delete": ["t4k-c08-041"], "keep": "tamago-l12-593", "edits": {},
     "note": "keep tamago-l12-593"},
    {"row_id": "row-00252", "delete": ["t4k-c08-045"], "keep": "wlt-c20-069", "edits": {},
     "note": "keep wlt-c20-069"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(232, 253)}


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

    log_lines = ["", "=" * 70, "Batch 9 — rows 232-252", ""]
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
