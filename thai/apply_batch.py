"""Apply batch 6 (rows 162-186) to vocab.json.

Skips IDs that no longer exist (already deleted in a prior batch).
Appends to apply_log.txt.
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00162", "delete": ["yt-c03-034"], "keep": "chula-l6-042", "edits": {},
     "note": "keep chula-l6-042"},
    {"row_id": "row-00163", "delete": ["thaipod-1141"], "keep": "chula-l6-053", "edits": {},
     "note": "keep chula-l6-053"},
    {"row_id": "row-00164", "delete": ["t4k-c07-016"], "keep": "chula-l6-063", "edits": {},
     "note": "keep chula-l6-063"},
    # row-00165: keep both — no action
    {"row_id": "row-00166", "delete": [], "keep": "wlt-c21-025",
     "edits": {"wlt-c21-025": {"english": "about; to approximate, to estimate"}},
     "note": "keep both; tweak wlt-c21-025 english (comma -> semicolon)"},
    # row-00167: keep both — no action
    {"row_id": "row-00168", "delete": ["thaipod-0072"], "keep": "chula-l6-084", "edits": {},
     "note": "keep chula-l6-084"},
    {"row_id": "row-00169", "delete": ["chula-l6-111"], "keep": "yt-c03-040",
     "edits": {"yt-c03-040": {"thai": "ปรบ - ปรบมือ"}},
     "note": "merge as ปรบ - ปรบมือ"},
    # row-00170: keep both — no action
    {"row_id": "row-00171", "delete": ["yt-c14-058"], "keep": "chula-l6-147",
     "edits": {"chula-l6-147": {"thai": "วอน, อ้อนวอน"}},
     "note": "merge as วอน, อ้อนวอน (user comma)"},
    {"row_id": "row-00172", "delete": ["t4k-c11-047"], "keep": "chula-l6-163", "edits": {},
     "note": "keep chula-l6-163"},
    # row-00173: keep both — no action
    # row-00174: keep both — no action
    {"row_id": "row-00175", "delete": ["tamago-l12-363"], "keep": "chula-l6-173",
     "edits": {"chula-l6-173": {"thai": "รอยฟกช้ำ"}},
     "note": "rename chula-l6-173 thai to รอยฟกช้ำ (longer form per user)"},
    {"row_id": "row-00176", "delete": ["tobo-316"], "keep": "chula-l6-175", "edits": {},
     "note": "keep chula-l6-175"},
    {"row_id": "row-00177", "delete": ["tamago-l3-180"], "keep": "chula-l6-177", "edits": {},
     "note": "keep chula-l6-177"},
    {"row_id": "row-00178", "delete": ["yt-c04-041"], "keep": "chula-l6-180", "edits": {},
     "note": "keep chula-l6-180"},
    {"row_id": "row-00179", "delete": ["yt-c06-096"], "keep": "chula-l6-183",
     "edits": {"chula-l6-183": {"thai": "ก้าง"}},
     "note": "rename chula-l6-183 thai to ก้าง (shorter form per user)"},
    {"row_id": "row-00180", "delete": ["chula-l6-187"], "keep": "tamago-l3-739", "edits": {},
     "note": "keep tamago-l3-739"},
    {"row_id": "row-00181", "delete": [], "keep": "tamago-l3-645",
     "edits": {"tamago-l3-645": {"english": "to pressure emotionally, to oppress"}},
     "note": "keep both; rephrase tamago-l3-645 english"},
    {"row_id": "row-00182", "delete": ["wlt-c07-087"], "keep": "chula-l6-196",
     "edits": {"chula-l6-196": {"thai": "ผสม, ผสมผสาน"}},
     "note": "merge as ผสม, ผสมผสาน"},
    # row-00183: keep both — no action
    {"row_id": "row-00184", "delete": [], "keep": "thaipod-0394",
     "edits": {"thaipod-0394": {"english": "region, habitat, native place"}},
     "note": "keep both; rephrase thaipod-0394 english"},
    {"row_id": "row-00185", "delete": ["chula-l6-224"], "keep": "tsl-112",
     "edits": {"tsl-112": {"thai": "บ่ง, บ่งบอก"}},
     "note": "merge as บ่ง, บ่งบอก"},
    {"row_id": "row-00186", "delete": ["tobo-347"], "keep": "chula-l6-233",
     "edits": {"chula-l6-233": {"thai": "หมวด, หมวดหมู่"}},
     "note": "merge as หมวด, หมวดหมู่"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(162, 187)}


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

    log_lines = ["", "=" * 70, "Batch 6 — rows 162-186", ""]
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
