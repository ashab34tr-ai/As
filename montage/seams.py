#!/usr/bin/env python3
"""Проверка стыков: сравнивает последний кадр клипа с первым кадром следующего.
Использование: seams.py clip1.mp4 clip2.mp4 ..."""
import sys, cv2, numpy as np
def frame(p, last):
    c = cv2.VideoCapture(p)
    if last: c.set(cv2.CAP_PROP_POS_FRAMES, max(c.get(cv2.CAP_PROP_FRAME_COUNT)-2, 0))
    ok, f = c.read(); c.release()
    if not ok: sys.exit(f"не прочитать {p}")
    return cv2.resize(f, (320, 180))
for a, b in zip(sys.argv[1:], sys.argv[2:]):
    x, y = frame(a, True), frame(b, False)
    lum = abs(float(x.mean()) - float(y.mean()))
    hx, hy = [cv2.calcHist([cv2.cvtColor(i, cv2.COLOR_BGR2HSV)], [0,1], None, [30,32], [0,180,0,256]) for i in (x, y)]
    sim = cv2.compareHist(cv2.normalize(hx, hx), cv2.normalize(hy, hy), cv2.HISTCMP_CORREL)
    flag = "ОК" if lum < 12 and sim > 0.5 else "ПРОВЕРИТЬ"
    print(f"{a} -> {b}: яркость Δ{lum:.1f}, цвет {sim:.2f} [{flag}]")
