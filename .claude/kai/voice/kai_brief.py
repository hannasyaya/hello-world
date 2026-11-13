#!/usr/bin/env python3
"""Turn a speaker-tagged briefing script into one MP3, with a different voice per agent.

Usage:
    python3 .claude/kai/voice/kai_brief.py <briefing.txt> [-o briefing.mp3]

Script format: each paragraph starts with a speaker tag from voices.json, e.g.

    [kai] Good morning. This is your AI agent risk briefing.
    [auditor-critic] My opinion is satisfactory with exceptions.

Everything runs locally with Piper (offline neural text-to-speech): the report text is never
sent to an outside service. Piper and the voice files are installed on first use; voices are
cached outside the repo in ~/.cache/kai-voices.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "kai-voices")
RATE = 22050
PAUSE_SPEAKER = 0.6   # seconds of silence when the speaker changes
PAUSE_PARAGRAPH = 0.35


def ensure_piper():
    try:
        import piper  # noqa: F401
    except ImportError:
        print("Installing Piper (first use)...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "piper-tts"], check=True)


def ensure_voice(name):
    model = os.path.join(VOICE_DIR, name + ".onnx")
    if not (os.path.exists(model) and os.path.exists(model + ".json")):
        os.makedirs(VOICE_DIR, exist_ok=True)
        print(f"Downloading voice {name} (first use)...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "piper.download_voices", name,
                        "--download-dir", VOICE_DIR], check=True)
    return model


def parse_script(text, voices):
    """Return [(speaker, paragraph), ...]. Untagged text continues the previous speaker."""
    segments, speaker = [], "kai"
    for block in re.split(r"\n\s*\n", text.strip()):
        block = " ".join(l.strip() for l in block.splitlines() if not l.strip().startswith("#"))
        if not block:
            continue
        m = re.match(r"\[([\w-]+)\]\s*(.*)", block)
        if m:
            speaker, block = m.group(1).lower(), m.group(2)
            if speaker not in voices:
                sys.exit(f"Unknown speaker [{speaker}]. Known: {', '.join(k for k in voices if k[0] != '_')}")
        segments.append((speaker, block))
    return segments


def for_the_ear(text):
    """Light clean-up so markdown and symbols are not read out literally."""
    text = re.sub(r"[*_`#>|]", "", text)
    text = text.replace("×", " by ").replace("&", " and ").replace("→", " to ")
    text = re.sub(r"\bR-0?(\d+)([ab]?)\b", lambda m: f"R {m.group(1)}{(' ' + m.group(2).upper()) if m.group(2) else ''}", text)
    return re.sub(r"\s+", " ", text).strip()


def to_raw(wav_path, raw_path):
    """Normalize any Piper output to 22.05 kHz mono 16-bit raw PCM."""
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav_path, "-ar", str(RATE),
                    "-ac", "1", "-f", "s16le", raw_path], check=True)
    with open(raw_path, "rb") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("-o", "--output")
    ap.add_argument("--title", default="Kai briefing")
    args = ap.parse_args()
    out = args.output or os.path.splitext(args.script)[0] + ".mp3"

    with open(os.path.join(HERE, "voices.json"), encoding="utf-8") as f:
        voices = json.load(f)
    with open(args.script, encoding="utf-8") as f:
        segments = parse_script(f.read(), voices)
    if not segments:
        sys.exit("Briefing script is empty.")

    ensure_piper()
    from piper import PiperVoice, SynthesisConfig

    loaded, pcm, prev = {}, bytearray(), None
    with tempfile.TemporaryDirectory() as tmp:
        for i, (speaker, text) in enumerate(segments):
            cfg = voices[speaker]
            if cfg["voice"] not in loaded:
                loaded[cfg["voice"]] = PiperVoice.load(ensure_voice(cfg["voice"]))
            wav_path, raw_path = os.path.join(tmp, f"{i}.wav"), os.path.join(tmp, f"{i}.raw")
            with wave.open(wav_path, "wb") as wf:
                loaded[cfg["voice"]].synthesize_wav(
                    for_the_ear(text), wf, syn_config=SynthesisConfig(length_scale=cfg.get("length_scale")))
            if prev is not None:
                pause = PAUSE_SPEAKER if speaker != prev else PAUSE_PARAGRAPH
                pcm += b"\x00\x00" * int(RATE * pause)
            pcm += to_raw(wav_path, raw_path)
            prev = speaker

        raw_all = os.path.join(tmp, "all.raw")
        with open(raw_all, "wb") as f:
            f.write(pcm)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(RATE), "-ac", "1",
                        "-i", raw_all, "-filter:a", "volume=-1.5dB", "-codec:a", "libmp3lame", "-q:a", "4",
                        "-metadata", f"title={args.title}", "-metadata", "artist=Kai (mini)", out], check=True)

    seconds = len(pcm) / 2 / RATE
    speakers = sorted({voices[s]["label"] for s, _ in segments})
    print(f"Wrote {out} ({seconds:.0f} s; voices: {', '.join(speakers)})")


if __name__ == "__main__":
    main()
