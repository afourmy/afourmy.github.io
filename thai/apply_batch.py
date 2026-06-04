"""Apply batch 50 (rows 968-980) to vocab.json."""

import json
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

MUTATIONS = [
    {"row_id": "row-00968", "delete": [], "keep": None,
     "edits": {"thaipod-0535": {"english": "to perform meritorious religious rites, to accumulate merit"}},
     "note": "keep both; thaipod-0535 english updated"},
    {"row_id": "row-00969", "delete": ["thaipod-0449"], "keep": "thaipod-0500", "edits": {},
     "note": "keep thaipod-0500"},
    {"row_id": "row-00970", "delete": ["thaipod-0479"], "keep": "thaipod-0478", "edits": {},
     "note": "keep thaipod-0478"},
    {"row_id": "row-00971", "delete": ["thaipod-1354"], "keep": "thaipod-0549",
     "edits": {"thaipod-0549": {"frequency": "rare"}},
     "note": "keep thaipod-0549 in rare"},
    {"row_id": "row-00972", "delete": ["thaipod-0617"], "keep": "thaipod-0616",
     "edits": {"thaipod-0616": {"thai": "ผู้กำกับ, ผู้กำกับภาพยนตร์"}},
     "note": "keep thaipod-0616 as ผู้กำกับ, ผู้กำกับภาพยนตร์"},
    {"row_id": "row-00973", "delete": ["thaipod-0653"], "keep": "thaipod-0650",
     "edits": {"thaipod-0650": {"thai": "พระชนมายุ, พระชันษา"}},
     "note": "keep thaipod-0650 as พระชนมายุ, พระชันษา"},
    {"row_id": "row-00974", "delete": ["tobo-129"], "keep": "thaipod-0657",
     "edits": {"thaipod-0657": {"thai": "พระนาง, ราชินี"}},
     "note": "keep thaipod-0657 as พระนาง, ราชินี"},
    {"row_id": "row-00976", "delete": ["thaipod-1387"], "keep": "thaipod-0712",
     "edits": {"thaipod-0712": {"thai": "โอรส, พระโอรส, พระราชโอรส"}},
     "note": "keep thaipod-0712 as โอรส, พระโอรส, พระราชโอรส"},
    {"row_id": "row-00977", "delete": [], "keep": None,
     "edits": {"thaipod-0719": {"english": "to sacrifice (literary)"}},
     "note": "keep both; thaipod-0719 english -> 'to sacrifice (literary)'"},
    {"row_id": "row-00978", "delete": ["wlt-c14-070"], "keep": "thaipod-0738",
     "edits": {"thaipod-0738": {"thai": "พุทธศาสนา, ศาสนาพุทธ"}},
     "note": "keep thaipod-0738 as พุทธศาสนา, ศาสนาพุทธ"},
    {"row_id": "row-00979", "delete": ["thaipod-0751"], "keep": "yt-c07-028",
     "edits": {"yt-c07-028": {"thai": "หนังสยองขวัญ, ภาพยนตร์สยองขวัญ"}},
     "note": "keep yt-c07-028 as หนังสยองขวัญ, ภาพยนตร์สยองขวัญ"},
    {"row_id": "row-00980", "delete": ["thaipod-0815"], "keep": "wlt-c19-029",
     "edits": {"wlt-c19-029": {"thai": "รถแอร์, รถปรับอากาศ"}},
     "note": "keep wlt-c19-029 as รถแอร์, รถปรับอากาศ"},
]

APPLIED_ROW_IDS = {f"row-{i:05d}" for i in range(968, 981)}

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

    log_lines = ["", "=" * 70, "Batch 50 — rows 968-980", ""]
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
