"""Apply batch 72 (rows row-01216 to row-01245) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-01216", "delete": [], "keep": None,
     "edits": {
         "wlt-c12-005": {"english": "to study, to learn"},
         "thaipod-0942": {"english": "to study, to learn (formal)"},
     },
     "note": "keep both; wlt-c12-005 english -> 'to study, to learn'; thaipod-0942 english -> 'to study, to learn (formal)'"},
    {"row_id": "row-01218", "delete": [], "keep": None,
     "edits": {
         "yt-c22-015": {"english": "to die, to pass away (idioms)"},
         "yt-c19-026": {"english": "to die, to pass away (formal)"},
     },
     "note": "keep all; yt-c22-015 english -> 'to die, to pass away (idioms)'; yt-c19-026 english -> 'to die, to pass away (formal)'"},
    # row-01220: keep both — no changes
    # row-01221: keep both — no changes
    {"row_id": "row-01223", "delete": ["tobo-298"], "keep": "thaipod-1140",
     "edits": {"thaipod-1140": {"english": "rank, status (royal)"}},
     "note": "remove tobo-298; thaipod-1140 english -> 'rank, status (royal)'"},
    {"row_id": "row-01224", "delete": [], "keep": None,
     "edits": {"thaipod-1149": {"frequency": "occasional", "english": "chubby, plump and round (cute baby-talk style)"}},
     "note": "keep both; thaipod-1149 frequency -> occasional; english -> 'chubby, plump and round (cute baby-talk style)'"},
    # row-01225: keep both — no changes
    # row-01226: keep both — no changes
    {"row_id": "row-01227", "delete": [], "keep": None,
     "edits": {
         "thaipod-1320": {"frequency": "occasional", "english": "candle"},
         "yt-c07-003": {"english": "candlestick"},
     },
     "note": "keep both; thaipod-1320 -> occasional, english -> 'candle'; yt-c07-003 english -> 'candlestick'"},
    {"row_id": "row-01228", "delete": ["thaipod-1327", "wlt-c03-022"], "keep": "yt-c03-074",
     "edits": {},
     "note": "keep only yt-c03-074; delete thaipod-1327, wlt-c03-022"},
    {"row_id": "row-01229", "delete": ["thaipod-1378"], "keep": "tsl-647",
     "edits": {"tsl-647": {"thai": "โรคภัย, โรคภัยไข้เจ็บ"}},
     "note": "merge into tsl-647; thai -> 'โรคภัย, โรคภัยไข้เจ็บ'; delete thaipod-1378"},
    # row-01232: keep both — no changes
    {"row_id": "row-01233", "delete": ["yt-c16-029"], "keep": "tobo-090",
     "edits": {},
     "note": "remove yt-c16-029; keep tobo-090"},
    # row-01234: keep both — no changes
    {"row_id": "row-01235", "delete": ["tobo-138"], "keep": "wlt-c20-077",
     "edits": {},
     "note": "remove tobo-138; keep wlt-c20-077"},
    # row-01236: keep both — no changes
    {"row_id": "row-01237", "delete": ["tobo-226"], "keep": "wlt-c19-081",
     "edits": {},
     "note": "remove tobo-226; keep wlt-c19-081"},
    {"row_id": "row-01238", "delete": ["tobo-232"], "keep": "wlt-c20-036",
     "edits": {},
     "note": "remove tobo-232; keep wlt-c20-036"},
    {"row_id": "row-01239", "delete": ["tobo-241"], "keep": "wlt-c20-040",
     "edits": {},
     "note": "remove tobo-241; keep wlt-c20-040"},
    {"row_id": "row-01240", "delete": [], "keep": None,
     "edits": {"wlt-c09-079": {"english": "degree (temperature)"}},
     "note": "keep both; wlt-c09-079 english -> 'degree (temperature)'"},
    {"row_id": "row-01241", "delete": [], "keep": None,
     "edits": {"wlt-c06-020": {"english": "to desire, to wish (literary)", "frequency": "rare"}},
     "note": "keep all; wlt-c06-020 english -> 'to desire, to wish (literary)'; frequency -> rare"},
    # row-01242: keep both — no changes
    # row-01243: keep both — no changes
    {"row_id": "row-01245", "delete": [], "keep": None,
     "edits": {"tsl-075": {"thai": "บ้านนอก", "english": "countryside, rural area (spoken)"}},
     "note": "keep both; tsl-075 thai -> 'บ้านนอก'; english -> 'countryside, rural area (spoken)'"},
]

APPLIED_ROW_IDS = {
    "row-01216", "row-01218", "row-01220", "row-01221", "row-01223",
    "row-01224", "row-01225", "row-01226", "row-01227", "row-01228",
    "row-01229", "row-01232", "row-01233", "row-01234", "row-01235",
    "row-01236", "row-01237", "row-01238", "row-01239", "row-01240",
    "row-01241", "row-01242", "row-01243", "row-01245",
}

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

    log_lines = ["", "=" * 70, "Batch 72 — rows row-01216 to row-01245", ""]
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
