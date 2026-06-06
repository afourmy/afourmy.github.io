"""Apply vocab review batch 11 — retroactive Thai/English field scan fixes."""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent

EDITS = {
    "chula-l5-035": {"thai": "บุก, บุกรุก", "english": "to storm, to charge in; to trespass, to intrude"},
    "tamago-l12-008": {"thai": "ไหว"},
    "tamago-l12-059": {"thai": "ขี้, อึ", "english": "feces, stool (informal and child-speak variants)"},
    "tamago-l12-076": {"thai": "คนละ", "english": "each one gets their own; different from each other"},
    "tamago-l12-460": {"english": "to suck at, to be terrible at"},
    "tamago-l12-475": {"english": "things like that"},
    "tamago-l12-623": {"english": "kilo (colloquial short form of kilogram)"},
    "tamago-l12-641": {"thai": "ไม่กี่", "english": "only a few"},
    "tamago-l3-202": {"thai": "ทีละ"},
    "tamago-l3-250": {"english": "excellent, fabulous (slang)"},
    "tamago-l3-358": {"thai": "มั่วๆ"},
    "tamago-l3-491": {"thai": "ไม่เอาไหน"},
    "tamago-l3-745": {"thai": "ว่าที่"},
    "tsl-394": {"english": "Thai Food and Drug Administration (FDA equivalent)"},
    "thaipod-1178": {"english": "(informal) he, she, I"},
    "yt-c02-086": {"english": "classifier for monks and novice monks", "frequency": "rare"},
    "yt-c03-023": {"english": "homework (emphatic redundant variant)"},
    "yt-c03-024": {"english": "nose (emphatic redundant variant)"},
    "yt-c03-025": {"english": "have you eaten yet? (emphatic redundant variant)", "frequency": "occasional"},
    "yt-c03-074": {"thai": "ถ่านไฟ, ถ่าน"},
    "yt-c03-086": {"english": "prefix (in general); honorific title before someone's name"},
    "yt-c04-051": {"english": "enthusiast, fan of sth (lit. 'neck of...') - fan of coffee"},
    "yt-c09-071": {
        "thai": "ศีลห้าข้อ - ไม่ฆ่าสัตว์ ไม่ขโมยของ ไม่พูดไม่ดี ไม่เป็นชู้กับสามีภรรยาชาวบ้าน ไม่ดื่ม",
        "english": "the five Buddhist precepts: no killing, no stealing, no sexual misconduct, no lying, no alcohol",
        "frequency": "common",
    },
    "yt-c18-027": {"thai": "ว่าที่"},
    "wlt-c08-003": {"thai": "พุทธศักราช (พ.ศ.)", "english": "Buddhist Era (B.E.)"},
    "wlt-c10-046": {"english": "in that case, so, then, therefore (informal short form)"},
    "wlt-c18-099": {"thai": "พอ + ได้"},
    "wlt-c21-055": {"english": "you"},
}

DELETES = {
    "chula-l5-294", "chula-l5-295", "chula-l5-296",
    "tamago-l12-100", "tamago-l12-653",
    "thaipod-0299", "thaipod-0303",
    "yt-c04-040", "yt-c10-073", "yt-c20-066",
    "wlt-c06-025", "wlt-c07-056", "wlt-c16-073",
}

PARKS = {"yt-c04-051", "yt-c23-015"}

APPLIED_ROW_IDS = {
    "chula-l5-035", "chula-l5-294", "chula-l5-295", "chula-l5-296",
    "tamago-l12-008", "tamago-l12-059", "tamago-l12-076", "tamago-l12-100",
    "tamago-l12-460", "tamago-l12-475", "tamago-l12-623", "tamago-l12-641",
    "tamago-l12-653", "tamago-l3-202", "tamago-l3-250", "tamago-l3-358",
    "tamago-l3-491", "tamago-l3-745",
    "tsl-394", "thaipod-0299", "thaipod-0303", "thaipod-1178",
    "yt-c02-086", "yt-c03-023", "yt-c03-024", "yt-c03-025", "yt-c03-074",
    "yt-c03-086", "yt-c04-040", "yt-c04-051", "yt-c09-071", "yt-c10-073",
    "yt-c18-027", "yt-c20-066", "yt-c23-015",
    "wlt-c06-025", "wlt-c07-056", "wlt-c08-003", "wlt-c10-046",
    "wlt-c16-073", "wlt-c18-099", "wlt-c21-055",
}


def main():
    vocab_path = HERE / "vocab.json"
    decisions_path = HERE / "decisions.json"
    parked_path = HERE / "parked.json"
    log_path = HERE / "apply_log.txt"

    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in vocab}

    # Apply field edits
    applied = []
    skipped = []
    for eid, fields in EDITS.items():
        if eid not in by_id:
            skipped.append(eid)
            continue
        for k, v in fields.items():
            by_id[eid][k] = v
        applied.append((eid, fields))

    # Park entries (edit already applied to by_id above)
    parked = [by_id[eid] for eid in PARKS if eid in by_id]
    skipped += [eid for eid in PARKS if eid not in by_id]

    parked_doc = json.loads(parked_path.read_text(encoding="utf-8"))
    for entry in parked:
        parked_doc["entries"].append(entry)
    parked_path.write_text(
        json.dumps(parked_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Remove deleted and parked entries from vocab
    remove_ids = DELETES | PARKS
    deleted = [eid for eid in DELETES if eid in by_id]
    skipped += [eid for eid in DELETES if eid not in by_id]
    new_vocab = [e for e in vocab if e["id"] not in remove_ids]

    log_lines = [
        "", "=" * 70,
        "Vocab review batch 11 — retroactive Thai/English field scan fixes", "",
    ]
    for eid, fields in applied:
        for k, v in fields.items():
            log_lines.append(f"    edit {eid}.{k} = {v!r}")
    for eid in deleted:
        log_lines.append(f"    delete {eid}")
    for entry in parked:
        log_lines.append(f"    park {entry['id']}")
    if skipped:
        log_lines.append(f"Skipped (not found): {', '.join(skipped)}")
    log_lines.append(f"Total field edits: {sum(len(f) for _, f in applied)}")
    log_lines.append(f"Total deletions: {len(deleted)}")
    log_lines.append(f"Total parked: {len(parked)}")
    log_lines.append(f"Vocab: {len(vocab)} -> {len(new_vocab)}")
    log_lines.append("")

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

    print(f"Applied {sum(len(f) for _, f in applied)} field edits across {len(applied)} entries")
    print(f"Deleted {len(deleted)} entries: {', '.join(deleted)}")
    print(f"Parked {len(parked)} entries: {', '.join(e['id'] for e in parked)}")
    if skipped:
        print(f"Skipped: {skipped}")
    print(f"decisions.json: {before} -> {doc['total_rows']} rows")
    print(f"vocab.json backup: {backup.name}")


if __name__ == "__main__":
    main()
