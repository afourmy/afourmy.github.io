"""Apply batch 24 (rows 503-521) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    # row-00503: keep both — no action
    {"row_id": "row-00504", "delete": ["wlt-c18-005"], "keep": "thaipod-1134", "edits": {},
     "note": "keep thaipod-1134"},
    {"row_id": "row-00505", "delete": ["thaipod-1137"], "keep": "thaipod-1136",
     "edits": {"thaipod-1136": {"frequency": "rare", "english": "based on, according to; to lean against"}},
     "note": "keep thaipod-1136, move to rare, new english"},
    {"row_id": "row-00506", "delete": [], "keep": None,
     "edits": {"thaipod-1161": {"frequency": "occasional"}},
     "note": "keep both; thaipod-1161 to occasional"},
    {"row_id": "row-00507", "delete": ["wlt-c17-044"], "keep": "thaipod-1167",
     "edits": {"thaipod-1167": {"thai": "ร่วม, เข้าร่วม"}},
     "note": "keep thaipod-1167 as ร่วม, เข้าร่วม"},
    {"row_id": "row-00508", "delete": ["thaipod-1180"], "keep": "tsl-085",
     "edits": {"tsl-085": {"frequency": "occasional"}},
     "note": "keep tsl-085, move to occasional"},
    {"row_id": "row-00509", "delete": ["thaipod-1181"], "keep": "wlt-c21-058", "edits": {},
     "note": "keep wlt-c21-058"},
    {"row_id": "row-00510", "delete": [], "keep": None,
     "edits": {"thaipod-1198": {"english": "to connect, to link up"}},
     "note": "keep both; thaipod-1198 'to link' -> 'to link up'"},
    {"row_id": "row-00511", "delete": [], "keep": None,
     "edits": {"yt-c07-063": {"frequency": "occasional", "english": "to associate, connect, link (e.g. sth abstract, idea, relations)"}},
     "note": "keep both; yt-c07-063 to occasional, add parenthetical to english"},
    {"row_id": "row-00512", "delete": ["thaipod-1201"], "keep": "wlt-c10-062", "edits": {},
     "note": "keep wlt-c10-062"},
    {"row_id": "row-00513", "delete": [], "keep": None,
     "edits": {"thaipod-1203": {"english": "to walk, to go on foot"}},
     "note": "keep both; thaipod-1203 english -> 'to walk, to go on foot'"},
    {"row_id": "row-00514", "delete": [], "keep": None,
     "edits": {"thaipod-1204": {"english": "original, former, same as before"}},
     "note": "keep both; thaipod-1204 english -> 'original, former, same as before'"},
    {"row_id": "row-00515", "delete": ["tsl-172"], "keep": "thaipod-1217", "edits": {},
     "note": "keep thaipod-1217"},
    {"row_id": "row-00516", "delete": ["wlt-c14-055"], "keep": "thaipod-1249",
     "edits": {"thaipod-1249": {"thai": "เริ่ม, เริ่มต้น"}},
     "note": "keep thaipod-1249 as เริ่ม, เริ่มต้น"},
    {"row_id": "row-00517", "delete": ["thaipod-1260"], "keep": "wlt-c21-038", "edits": {},
     "note": "keep wlt-c21-038"},
    {"row_id": "row-00518", "delete": [], "keep": None,
     "edits": {"tsl-222": {"frequency": "rare", "english": "just right, moderate, appropriate"}},
     "note": "keep both; tsl-222 to rare, english -> 'just right, moderate, appropriate'"},
    {"row_id": "row-00519", "delete": ["thaipod-1298"], "keep": "thaipod-1297", "edits": {},
     "note": "keep thaipod-1297"},
    {"row_id": "row-00520", "delete": ["thaipod-1314"], "keep": "tsl-511", "edits": {},
     "note": "keep tsl-511"},
    {"row_id": "row-00521", "delete": [], "keep": None,
     "edits": {
         "yt-c01-008": {"english": "to share with others (e.g. food, experience)"},
         "thaipod-1329": {"english": "to divide, to separate; to share"},
     },
     "note": "keep both; differentiate english for yt-c01-008 and thaipod-1329"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(503, 522)}


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

    log_lines = ["", "=" * 70, "Batch 24 — rows 503-521", ""]
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
