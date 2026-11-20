#!/usr/bin/env python3
"""Диалог двух героев: голос по губам, оригинальная речь убрана полностью, ветер-подложка,
субтитры по словам, 1080x1920, громкость -14 LUFS (два прохода). build_dialog.py out.mp4"""
import subprocess, sys, json, re, tempfile, os, pysubs2
U = "/root/.claude/uploads/99a9e230-f2a1-52ba-8a08-bdfdbd510d08/"
CLIPS = [U+"c5a3c79b-higgsfield-cb3920ab-261d-4e8a-8438-373ede43c386.mp4", U+"b60d488a-higgsfield-b8185ae9-8a65-4324-b3a2-ebd1943594b8.mp4"]
VOX = {"H": U+"9cb60017-fish-audio-20261121-010406.wav", "S": U+"259618d1-fish-audio-20261121-010441.wav"}
OFF = [0.0, 18.041667]; DUR = 34.083334
# (клип, кто, старт в клипе, голос от, голос до, слова [(текст, от, до)], карточки по числу слов)
P = [
 (0,"H", 0.0, 0.0, 3.1,[("Брат,",0.0,1.5),("руку",2.2,2.8),("дай!",2.8,3.1)],[3]),
 (0,"S", 3.4, 0.0, 0.5,[("Сам?",0.0,0.5)],[1]),
 (0,"H", 5.0, 4.9, 8.0,[("Ты",4.9,5.4),("нормальный?",5.4,6.1),("Я",6.8,7.0),("вишу!",7.0,8.0)],[2,2]),
 (0,"S", 8.6, 1.3, 3.1,[("Ты",1.3,1.6),("каждый",1.6,2.0),("месяц",2.0,2.6),("висишь.",2.6,3.1)],[4]),
 (0,"S",10.6, 3.55, 5.0,[("Я",3.55,3.8),("каждый",3.8,4.0),("месяц",4.0,4.5),("тяну.",4.5,5.0)],[4]),
 (0,"H",12.8, 9.3,11.2,[("Последний",9.3,10.3),("раз,",10.3,10.7),("брат.",10.9,11.2)],[3]),
 (0,"S",15.8, 5.8, 7.3,[("Ты",5.8,5.9),("это",5.9,6.1),("в",6.1,6.2),("прошлый",6.2,6.7),("раз",6.7,6.8),("говорил.",6.8,7.3)],[3,3]),
 (1,"H", 4.8,13.1,16.1,[("Ты",13.1,13.8),("бы",13.8,13.9),("смотрел,",13.9,14.8),("как",14.8,15.0),("я",15.0,15.3),("падаю.",15.3,16.1)],[3,3]),
 (1,"S",11.6, 8.0, 8.9,[("Ты",8.0,8.2),("бы",8.2,8.3),("не",8.3,8.5),("упал.",8.5,8.9)],[4]),
]
out = sys.argv[1]; tmp = tempfile.mkdtemp()
def tl(c,t0,s,v): return OFF[c] + t0 + (v - max(s-0.08,0))   # время голоса на общей шкале

# --- звук: ветер + голоса ---
inp = []
for v in VOX.values(): inp += ["-i", v]
fc = [f"anoisesrc=d={DUR}:c=brown:a=0.5,highpass=f=60,lowpass=f=700,tremolo=f=0.15:d=0.5,volume=0.35,aformat=channel_layouts=stereo,aresample=48000[wind]"]
mix = ["[wind]"]
for k,(c,w,t0,s,e,_,_) in enumerate(P):
    src = 0 if w=="H" else 1; d = int((OFF[c]+t0)*1000)
    fc.append(f"[{src}:a]atrim={max(s-0.08,0):.2f}:{e+0.2:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={e-s+0.1:.2f}:d=0.1,aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d}[p{k}]")
    mix.append(f"[p{k}]")
raw = f"{tmp}/mix.wav"
subprocess.run(["ffmpeg","-y","-loglevel","error",*inp,"-filter_complex",";".join(fc)+";"+"".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{DUR}[a]","-map","[a]",raw],check=True)
m = subprocess.run(["ffmpeg","-hide_banner","-i",raw,"-af","loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
j = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", m, re.S).group(0))
final_a = f"{tmp}/final.wav"
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true","-ar","48000",final_a],check=True)

# --- субтитры по словам ---
ass = pysubs2.SSAFile(); ass.info["PlayResX"], ass.info["PlayResY"] = "1080","1920"
ass.styles["Default"] = pysubs2.SSAStyle(fontname="Inter Black", fontsize=92, primarycolor=pysubs2.Color(255,255,255), outlinecolor=pysubs2.Color(0,0,0), backcolor=pysubs2.Color(0,0,0,110), outline=6, shadow=3, alignment=2, marginv=560, marginl=70, marginr=70)
YEL = r"{\c&H00D4FF&\fscx108\fscy108}"; WHT = r"{\c&HFFFFFF&\fscx100\fscy100}"
for (c,w,t0,s,e,words,cards) in P:
    i = 0
    for n in cards:
        grp = words[i:i+n]; i += n
        for a,(wt,vs,ve) in enumerate(grp):
            start = tl(c,t0,s,vs)
            end = tl(c,t0,s,grp[a+1][1]) if a+1 < len(grp) else tl(c,t0,s,grp[-1][2]) + 0.3
            text = " ".join((YEL if b==a else WHT)+x[0] for b,x in enumerate(grp))
            ass.append(pysubs2.SSAEvent(start=int(start*1000), end=int(end*1000), text=text))
ass_path = f"{tmp}/d.ass"; ass.save(ass_path)

# --- видео ---
vin = []
for c in CLIPS: vin += ["-i", c]
vf = ";".join(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,setsar=1[v{i}]" for i in range(2))
vf += f";[v0][v1]concat=n=2:v=1:a=0[v];[v]subtitles={ass_path},format=yuv420p[vo]"
subprocess.run(["ffmpeg","-y","-loglevel","error",*vin,"-i",final_a,"-filter_complex",vf,"-map","[vo]","-map","2:a","-c:v","libx264","-crf","16","-preset","slow","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],check=True)
print("ok", out)
