"""Apply batch 23 (rows 479-502) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00479", "delete": ["thaipod-1080"], "keep": "thaipod-0835", "edits": {},
     "note": "keep thaipod-0835"},
    {"row_id": "row-00480", "delete": ["thaipod-1401"], "keep": "thaipod-0835", "edits": {},
     "note": "keep thaipod-0835"},
    # row-00481: keep both — no action
    {"row_id": "row-00482", "delete": ["thaipod-0857"], "keep": "thaipod-1130",
     "edits": {"thaipod-1130": {"thai": "อาณาจักร, ราชอาณาจักร"}},
     "note": "keep thaipod-1130 as อาณาจักร, ราชอาณาจักร"},
    {"row_id": "row-00483", "delete": [], "keep": None,
     "edits": {"thaipod-0869": {"frequency": "rare"}},
     "note": "keep both; thaipod-0869 to rare"},
    {"row_id": "row-00484", "delete": [], "keep": None,
     "edits": {"thaipod-1384": {"english": "to cheer, acclaim, shout in unison"}},
     "note": "keep both; thaipod-1384 english -> 'to cheer, acclaim, shout in unison'"},
    {"row_id": "row-00485", "delete": ["thaipod-0878"], "keep": "wlt-c11-095", "edits": {},
     "note": "remove thaipod-0878; keep wlt-c11-095"},
    {"row_id": "row-00486", "delete": ["yt-c11-074"], "keep": "thaipod-0879",
     "edits": {"thaipod-0879": {"thai": "ร้าง, ทิ้งร้าง"}},
     "note": "keep thaipod-0879 as ร้าง, ทิ้งร้าง"},
    {"row_id": "row-00487", "delete": ["wlt-c16-018"], "keep": "thaipod-0880",
     "edits": {"thaipod-0880": {"thai": "ร้าน, ร้านค้า"}},
     "note": "keep thaipod-0880 as ร้าน, ร้านค้า"},
    # row-00488: keep both — no action
    # row-00489: keep both — no action
    {"row_id": "row-00490", "delete": [], "keep": None,
     "edits": {"tsl-430": {"frequency": "rare"}},
     "note": "keep both; move tsl-430 to rare"},
    {"row_id": "row-00491", "delete": [], "keep": None,
     "edits": {"wlt-c05-046": {"english": "to build, to construct"}},
     "note": "keep both; wlt-c05-046 english -> 'to build, to construct'"},
    {"row_id": "row-00492", "delete": ["thaipod-0978"], "keep": "tsl-423",
     "edits": {"tsl-423": {"thai": "สลัก, แกะสลัก", "frequency": "rare"}},
     "note": "keep tsl-423 in rare as สลัก, แกะสลัก"},
    {"row_id": "row-00493", "delete": ["thaipod-0983"], "keep": "thaipod-0982", "edits": {},
     "note": "keep thaipod-0982"},
    {"row_id": "row-00494", "delete": [], "keep": None,
     "edits": {
         "wlt-c16-036": {"english": "light, bright"},
         "thaipod-0986": {"frequency": "rare"},
     },
     "note": "keep both; wlt-c16-036 remove 'to be'; thaipod-0986 to rare"},
    {"row_id": "row-00495", "delete": ["wlt-c14-081"], "keep": "thaipod-0996",
     "edits": {"thaipod-0996": {"thai": "สังเกต, สังเกตเห็น"}},
     "note": "keep thaipod-0996 as สังเกต, สังเกตเห็น"},
    {"row_id": "row-00496", "delete": ["thaipod-0999"], "keep": "thaipod-0998", "edits": {},
     "note": "keep thaipod-0998"},
    {"row_id": "row-00497", "delete": ["yt-c04-007"], "keep": "thaipod-1003", "edits": {},
     "note": "keep thaipod-1003"},
    {"row_id": "row-00498", "delete": ["thaipod-1026"], "keep": "wlt-c12-042",
     "edits": {"wlt-c12-042": {"thai": "สิ้น, สิ้นสุด"}},
     "note": "keep wlt-c12-042 as สิ้น, สิ้นสุด"},
    {"row_id": "row-00499", "delete": ["thaipod-1205"], "keep": "thaipod-1052", "edits": {},
     "note": "keep thaipod-1052"},
    {"row_id": "row-00500", "delete": ["thaipod-1064"], "keep": "thaipod-1063",
     "edits": {"thaipod-1063": {"thai": "หยอก, หยอกล้อ", "english": "to tease, make fun of, joke around"}},
     "note": "keep thaipod-1063 as หยอก, หยอกล้อ"},
    {"row_id": "row-00501", "delete": [], "keep": None,
     "edits": {"tobo-507": {"frequency": "occasional"}},
     "note": "keep both; tobo-507 to occasional"},
    {"row_id": "row-00502", "delete": [], "keep": None,
     "edits": {
         "thaipod-1076": {"english": "handsome"},
         "tsl-407": {"thai": "หล่อ, หล่อหลอม", "english": "to mold, to shape, to cast"},
     },
     "note": "keep both; thaipod-1076 -> handsome only; tsl-407 -> หล่อ, หล่อหลอม: to mold, to shape, to cast"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(479, 503)}


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

    log_lines = ["", "=" * 70, "Batch 23 — rows 479-502", ""]
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
