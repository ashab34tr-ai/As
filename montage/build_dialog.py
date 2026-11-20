#!/usr/bin/env python3
"""Диалог двух героев: замена голоса по губам, ambience остаётся, субтитры, 1080x1920, -14 LUFS.
build_dialog.py out.mp4  (пути и фразы заданы ниже)"""
import subprocess, sys, pysubs2
U = "/root/.claude/uploads/99a9e230-f2a1-52ba-8a08-bdfdbd510d08/"
CLIPS = [U+"c5a3c79b-higgsfield-cb3920ab-261d-4e8a-8438-373ede43c386.mp4", U+"b60d488a-higgsfield-b8185ae9-8a65-4324-b3a2-ebd1943594b8.mp4"]
VOX = {"H": U+"9cb60017-fish-audio-20261121-010406.wav", "S": U+"259618d1-fish-audio-20261121-010441.wav"}
OFF = [0.0, 18.041667]  # старт клипов на общей шкале
# (клип, кто, где фраза начинается в клипе, голос от, голос до, окно губ в клипе от-до, текст)
P = [
 (0,"H", 0.0, 0.0, 3.1,(0.0,2.0),"Брат, руку дай!"),
 (0,"S", 3.4, 0.0, 0.5,(3.4,4.2),"Сам?"),
 (0,"H", 5.0, 4.9, 8.0,(5.0,7.9),"Ты нормальный? Я вишу!"),
 (0,"S", 8.6, 1.3, 3.1,(8.6,10.0),"Ты каждый месяц висишь."),
 (0,"S",10.6, 3.6, 5.0,(10.6,11.7),"Я каждый месяц тяну."),
 (0,"H",12.8, 9.3,11.2,(12.8,14.1),"Последний раз, брат."),
 (0,"S",15.8, 5.8, 7.3,(15.8,17.3),"Ты это в прошлый раз говорил."),
 (1,"H", 4.8,13.1,16.1,(4.8,6.6),"Ты бы смотрел, как я падаю."),
 (1,"S",11.6, 8.0, 8.9,(11.6,12.9),"Ты бы не упал."),
]
out = sys.argv[1]
inp = []; fc = []
for c in CLIPS: inp += ["-i", c]
for v in VOX.values(): inp += ["-i", v]
for i in range(2):
    fc.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,setsar=1[v{i}]")
    duck = "+".join(f"between(t,{a-0.1:.2f},{max(b,a+(e-s))+0.25:.2f})" for (c,_,t0,s,e,(a,b),_) in P if c==i)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume='if({duck},0.08,1)':eval=frame[a{i}]")
fc.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][amb]")
mix = ["[amb]"]
for k,(c,w,t0,s,e,_,_) in enumerate(P):
    src = 2 if w=="H" else 3; d = int((OFF[c]+t0)*1000)
    fc.append(f"[{src}:a]atrim={max(s-0.08,0):.2f}:{e+0.2:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={e-s+0.1:.2f}:d=0.1,aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d}[p{k}]")
    mix.append(f"[p{k}]")
fc.append("".join(mix)+f"amix=inputs={len(mix)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
ass = pysubs2.SSAFile(); ass.info["PlayResX"], ass.info["PlayResY"] = "1080","1920"
ass.styles["Default"] = pysubs2.SSAStyle(fontname="Inter", fontsize=64, bold=True, primarycolor=pysubs2.Color(255,255,255), outlinecolor=pysubs2.Color(0,0,0), outline=4, shadow=0, alignment=2, marginv=420, marginl=90, marginr=90)
for (c,w,t0,s,e,_,txt) in P:
    a = OFF[c]+t0; ass.append(pysubs2.SSAEvent(start=int(a*1000), end=int((a+(e-s)+0.2)*1000), text=txt))
ass.save("/tmp/dialog.ass")
fc[-3+0] = fc[-3]  # no-op
fc.insert(fc.index("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][amb]")+1, "[v]subtitles=/tmp/dialog.ass,format=yuv420p[vo]")
subprocess.run(["ffmpeg","-y","-loglevel","error",*inp,"-filter_complex",";".join(fc),"-map","[vo]","-map","[ao]","-c:v","libx264","-crf","16","-preset","slow","-c:a","aac","-b:a","192k","-movflags","+faststart",out],check=True)
print("ok", out)
