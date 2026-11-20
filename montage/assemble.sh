#!/usr/bin/env bash
# assemble.sh out.mp4 [--lut file.cube] [--subs file.ass] clip1.mp4 clip2.mp4 ...
# Склейка встык, один LUT на весь ролик, субтитры, 9:16 1080x1920, громкость -14 LUFS.
set -euo pipefail
out=$1; shift; lut=""; subs=""
while [[ ${1:-} == --* ]]; do case $1 in --lut) lut=$2;; --subs) subs=$2;; esac; shift 2; done
n=$#; inputs=(); fc=""; i=0
for c in "$@"; do inputs+=(-i "$c"); fc+="[$i:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"; i=$((i+1)); done
for ((k=0;k<n;k++)); do fc+="[v$k][a$k]"; done
fc+="concat=n=$n:v=1:a=1[v][a];[v]"
[[ -n $lut ]] && fc+="lut3d=$lut," ; [[ -n $subs ]] && fc+="subtitles=$subs," ; fc+="format=yuv420p[vo];[a]loudnorm=I=-14:TP=-1.5:LRA=11[ao]"
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$fc" -map "[vo]" -map "[ao]" -c:v libx264 -crf 16 -preset slow -c:a aac -b:a 192k -movflags +faststart "$out"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$out"
