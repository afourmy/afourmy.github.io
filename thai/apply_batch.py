"""Apply batch 66 (rows pfx-0027 to pfx-0067) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-pfx-0027", "delete": ["tobo-313"], "keep": "tamago-l3-779", "edits": {},
     "note": "remove tobo-313; keep tamago-l3-779"},
    {"row_id": "row-pfx-0028", "delete": ["t4k-c04-041"], "keep": "tobo-111", "edits": {},
     "note": "remove t4k-c04-041; keep tobo-111"},
    # row-pfx-0029: keep both — no changes
    {"row_id": "row-pfx-0030", "delete": ["thaipod-0073"], "keep": "thaipod-0745", "edits": {},
     "note": "keep thaipod-0745; delete thaipod-0073"},
    {"row_id": "row-pfx-0031", "delete": [], "keep": None,
     "edits": {"thaipod-0074": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0074 frequency -> occasional"},
    {"row_id": "row-pfx-0032", "delete": ["tamago-l3-830"], "keep": "wlt-c20-049", "edits": {},
     "note": "keep only wlt-c20-049; delete tamago-l3-830"},
    {"row_id": "row-pfx-0033", "delete": [], "keep": None,
     "edits": {"tobo-385": {"frequency": "occasional"}},
     "note": "keep both; tobo-385 frequency -> occasional"},
    {"row_id": "row-pfx-0034", "delete": [], "keep": None,
     "edits": {"t4k-c03-039": {"frequency": "occasional"}},
     "note": "keep both; t4k-c03-039 frequency -> occasional"},
    # row-pfx-0035: keep both — no changes
    # row-pfx-0036: keep both — no changes
    {"row_id": "row-pfx-0037", "delete": ["thaipod-0079"], "keep": "t4k-c02-037", "edits": {},
     "note": "keep t4k-c02-037; delete thaipod-0079"},
    {"row_id": "row-pfx-0038", "delete": ["tobo-371"], "keep": "wlt-c09-080", "edits": {},
     "note": "keep wlt-c09-080; delete tobo-371"},
    {"row_id": "row-pfx-0039", "delete": [], "keep": None,
     "edits": {"tamago-l12-039": {"english": "issuance (document, certificate)"}},
     "note": "keep both; tamago-l12-039 english -> 'issuance (document, certificate)'"},
    {"row_id": "row-pfx-0040", "delete": ["tobo-203"], "keep": "wlt-c15-028", "edits": {},
     "note": "keep wlt-c15-028; delete tobo-203"},
    # row-pfx-0041: keep both — no changes
    {"row_id": "row-pfx-0042", "delete": [], "keep": None,
     "edits": {
         "t4k-c04-054": {"english": "sick, ill"},
         "thaipod-0083": {"frequency": "occasional", "english": "sickness, illness"},
     },
     "note": "keep both; t4k-c04-054 english -> 'sick, ill'; thaipod-0083 -> 'sickness, illness', occasional"},
    {"row_id": "row-pfx-0043", "delete": [], "keep": None,
     "edits": {"tobo-256": {"frequency": "occasional"}},
     "note": "keep both; tobo-256 frequency -> occasional"},
    # row-pfx-0044: keep both — no changes
    # row-pfx-0045: keep both — no changes
    {"row_id": "row-pfx-0046", "delete": [], "keep": None,
     "edits": {"tobo-518": {"frequency": "occasional"}},
     "note": "keep both; tobo-518 frequency -> occasional"},
    {"row_id": "row-pfx-0047", "delete": ["thaipod-0090"], "keep": "tamago-l12-586", "edits": {},
     "note": "remove thaipod-0090; keep tamago-l12-586"},
    {"row_id": "row-pfx-0048", "delete": ["thaipod-0092"], "keep": "thaipod-1318", "edits": {},
     "note": "remove thaipod-0092; keep thaipod-1318"},
    # row-pfx-0049: keep both — no changes
    {"row_id": "row-pfx-0050", "delete": [], "keep": None,
     "edits": {"yt-c05-058": {"frequency": "occasional"}},
     "note": "keep both; yt-c05-058 frequency -> occasional"},
    {"row_id": "row-pfx-0051", "delete": ["thaipod-0094"], "keep": "thaipod-1376", "edits": {},
     "note": "keep thaipod-1376; delete thaipod-0094"},
    {"row_id": "row-pfx-0052", "delete": [], "keep": None,
     "edits": {"tamago-l3-630": {"frequency": "occasional"}},
     "note": "keep both; tamago-l3-630 frequency -> occasional"},
    {"row_id": "row-pfx-0053", "delete": [], "keep": None,
     "edits": {"chula-l6-014": {"frequency": "occasional"}},
     "note": "keep both; chula-l6-014 frequency -> occasional"},
    {"row_id": "row-pfx-0054", "delete": [], "keep": None,
     "edits": {
         "tobo-003": {"frequency": "occasional"},
         "chula-l6-074": {"english": "harmonious, in harmony, to blend in well"},
     },
     "note": "keep both; tobo-003 -> occasional; chula-l6-074 english -> 'harmonious, in harmony, to blend in well'"},
    {"row_id": "row-pfx-0055", "delete": [], "keep": None,
     "edits": {"t4k-c04-016": {"frequency": "occasional"}},
     "note": "keep both; t4k-c04-016 frequency -> occasional"},
    {"row_id": "row-pfx-0056", "delete": [], "keep": None,
     "edits": {
         "tamago-l12-080": {"frequency": "occasional"},
         "wlt-c16-072": {"english": "wide, broad, vast"},
     },
     "note": "keep both; tamago-l12-080 -> occasional; wlt-c16-072 english -> 'wide, broad, vast'"},
    # row-pfx-0057: keep both — no changes
    # row-pfx-0058: keep both — no changes
    # row-pfx-0059: keep both — no changes
    {"row_id": "row-pfx-0060", "delete": [], "keep": None,
     "edits": {"t4k-c03-014": {"english": "to think, to be of the opinion"}},
     "note": "keep both; t4k-c03-014 english -> 'to think, to be of the opinion'"},
    {"row_id": "row-pfx-0061", "delete": [], "keep": None,
     "edits": {"thaipod-0176": {"frequency": "occasional"}},
     "note": "keep both; thaipod-0176 frequency -> occasional"},
    {"row_id": "row-pfx-0062", "delete": [], "keep": None,
     "edits": {"thaipod-0236": {"english": "beautiful, elegant, gorgeous (formal, literary)"}},
     "note": "keep both; thaipod-0236 english -> 'beautiful, elegant, gorgeous (formal, literary)'"},
    {"row_id": "row-pfx-0063", "delete": [], "keep": None,
     "edits": {"t4k-c10-003": {"english": "loyal, faithful, devoted"}},
     "note": "keep both; t4k-c10-003 english -> 'loyal, faithful, devoted'"},
    # row-pfx-0064: keep both — no changes
    # row-pfx-0065: keep both — no changes
    {"row_id": "row-pfx-0066", "delete": [], "keep": None,
     "edits": {"t4k-c05-094": {"english": "to contain, hold, have a capacity of"}},
     "note": "keep both; t4k-c05-094 english -> 'to contain, hold, have a capacity of'"},
    # row-pfx-0067: keep both — no changes
]

APPLIED_ROW_IDS = {f"row-pfx-{i:04d}" for i in range(27, 68)}

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

    log_lines = ["", "=" * 70, "Batch 66 — rows pfx-0027 to pfx-0067", ""]
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
