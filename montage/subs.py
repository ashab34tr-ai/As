#!/usr/bin/env python3
"""Субтитры из речи: subs.py clip.mp4 out.ass [язык=ru]. Крупно, по центру-низу, безопасные поля 9:16."""
import sys, subprocess, numpy as np, pysubs2
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]; lang = sys.argv[3] if len(sys.argv) > 3 else "ru"
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",src,"-vn","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True).stdout, np.int16).astype(np.float32)/32768
segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
s = pysubs2.SSAFile(); s.info["PlayResX"], s.info["PlayResY"] = "1080", "1920"
s.styles["Default"] = pysubs2.SSAStyle(fontname="Inter", fontsize=64, bold=True, primarycolor=pysubs2.Color(255,255,255), outlinecolor=pysubs2.Color(0,0,0), outline=4, shadow=0, alignment=2, marginv=420, marginl=90, marginr=90)
for seg in segs:
    words = seg.words or []
    for i in range(0, len(words), 4):  # по 4 слова, коротко
        g = words[i:i+4]; s.append(pysubs2.SSAEvent(start=int(g[0].start*1000), end=int(g[-1].end*1000), text=" ".join(w.word.strip() for w in g)))
s.save(out); print(f"{len(s)} строк -> {out}")
