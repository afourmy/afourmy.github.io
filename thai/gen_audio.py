#!/usr/bin/env python3
"""Generate Thai pronunciation MP3s with Azure AI Speech, one per word.

Reads thai/vocab.json, synthesizes the Thai text of the first N words (or
--all), writes thai/audio/<id>.mp3, and flags those words with "audio": true so
the page shows a speaker button only where audio actually exists. Idempotent:
skips words whose mp3 already exists unless --force.

Credentials come from the environment (see thai/.tts-credentials):
  AZURE_SPEECH_KEY     your Speech resource key
  AZURE_SPEECH_REGION  e.g. southeastasia, eastus

Usage:
  source thai/.tts-credentials && python3 thai/gen_audio.py        # first 10
  source thai/.tts-credentials && python3 thai/gen_audio.py -n 25
  source thai/.tts-credentials && python3 thai/gen_audio.py --all
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent  # .../thai
VOCAB = HERE / "vocab.json"
AUDIO_DIR = HERE / "audio"

VOICE = "th-TH-PremwadeeNeural"  # dedicated Thai neural voice (female)
# 24 kHz / 96 kbps mono mp3: high quality for speech, small files.
OUTPUT_FORMAT = "audio-24khz-96kbitrate-mono-mp3"


def ssml(text):
    return (
        "<speak version='1.0' xml:lang='th-TH'>"
        "<voice name='" + VOICE + "'>" + text + "</voice>"
        "</speak>"
    )


def synth(text, key, region):
    url = "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1"
    req = urllib.request.Request(
        url,
        data=ssml(text).encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
            "User-Agent": "thai-vocab-tts",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", "--count", type=int, default=10,
                    help="number of words from the top of the deck (default 10)")
    ap.add_argument("--all", action="store_true", help="process every word")
    ap.add_argument("--force", action="store_true",
                    help="re-synthesize even if the mp3 already exists")
    args = ap.parse_args()

    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        sys.exit("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION "
                 "(e.g. `source thai/.tts-credentials`).")

    words = json.loads(VOCAB.read_text(encoding="utf-8"))
    targets = words if args.all else words[: args.count]
    AUDIO_DIR.mkdir(exist_ok=True)

    changed = False
    failures = []
    for word in targets:
        out = AUDIO_DIR / (word["id"] + ".mp3")
        ok = out.exists()
        if ok and not args.force:
            print("skip (exists):", word["id"], word["thai"])
        else:
            try:
                audio = synth(word["thai"], key, region)
                out.write_bytes(audio)
                ok = True
                print("wrote:", out.name, "(%d bytes)" % len(audio), word["thai"])
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")[:300]
                ok = False
                failures.append((word["id"], e.code, body))
                print("FAIL:", word["id"], e.code, body)
            except Exception as e:  # noqa: BLE001 - report and continue
                ok = False
                failures.append((word["id"], "?", str(e)))
                print("FAIL:", word["id"], e)
        if ok and not word.get("audio"):
            word["audio"] = True
            changed = True

    if changed:
        VOCAB.write_text(
            json.dumps(words, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("updated vocab.json (audio flags)")

    if failures:
        print("\n%d failed:" % len(failures))
        for fid, code, body in failures:
            print(" ", fid, code, body)
        sys.exit(1)


if __name__ == "__main__":
    main()
