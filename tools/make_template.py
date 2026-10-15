"""kataware の実寸テンプレート (A4 横・1ページに片手ずつ) を HTML で生成する。

使い方:
    python3 tools/make_template.py docs/template
    → docs/template/kataware-template.html ができる。ブラウザで PDF に印刷する。

すべての寸法は mm。印刷時は「実際のサイズ (100%)」にすること。
"""
import math
import os
import sys

U = 19.05        # キーピッチ
CAP = 18.0       # キーキャップの大きさ (目安)
WALL = 5.0       # ケースの縁
RADIUS = 14.0    # 外周の角の丸み
BALL = 25.0
HOUSING = 34.0
KNOB = 15.0      # エンコーダーのつまみ (目安)
MCU_W, MCU_H = 18.0, 33.0   # ProMicro nRF52840 互換の大きさ
PAGE_W, PAGE_H = 297.0, 210.0

INK = "#222"
SUB = "#666"
FAINT = "#9aa3ad"

LEFT = [
    ["Q", "W", "E", "R", "T", "-"],
    ["A", "S", "D", "F", "G", "'"],
    ["Z", "X", "C", "V", "B"],
    ["Shift", "Tab", "Ctrl", "Lower", "Space", "英数", "Raise"],
]
RIGHT_ALPHA = [
    ["Y", "U", "I", "O", "P"],
    ["H", "J", "K", "L", ";"],
    ["N", "M", ",", ".", "/"],
    ["Enter", "Raise", "BS", "かな", "Shift"],
]


def key(x, y, label):
    pad = (U - CAP) / 2
    fs = 6.0 if len(label) == 1 else (3.4 if len(label) <= 3 else 2.9)
    return (f'<rect x="{x+pad:.2f}" y="{y+pad:.2f}" width="{CAP}" height="{CAP}" rx="1.6" '
            f'fill="none" stroke="{INK}" stroke-width="0.3"/>'
            f'<text x="{x+U/2:.2f}" y="{y+U/2+fs*0.35:.2f}" font-size="{fs}" text-anchor="middle" fill="{INK}">{label}</text>')


def case_outline(w, h):
    return (f'<rect x="{-WALL}" y="{-WALL}" width="{w+2*WALL:.2f}" height="{h+2*WALL:.2f}" rx="{RADIUS}" '
            f'fill="none" stroke="{INK}" stroke-width="0.5"/>')


def mcu(x, y):
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{MCU_W}" height="{MCU_H}" rx="1" fill="none" '
            f'stroke="{FAINT}" stroke-width="0.3" stroke-dasharray="1.5 1"/>'
            f'<text x="{x+MCU_W/2:.2f}" y="{y+MCU_H/2-1:.2f}" font-size="2.6" text-anchor="middle" fill="{SUB}">マイコン</text>'
            f'<text x="{x+MCU_W/2:.2f}" y="{y+MCU_H/2+2.5:.2f}" font-size="2.2" text-anchor="middle" fill="{SUB}">18×33</text>')


def hull_path(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in hull) + " Z"


def left_half():
    o = [case_outline(7*U, 4*U)]
    for r, row in enumerate(LEFT):
        for c, label in enumerate(row):
            if r == 3 and c in (5, 6):
                continue
            o.append(key(c*U, r*U, label))
    # 塊: エンコーダー + 英数 + Raise
    ex, ey = 6*U, 2.5*U
    rr = 4.0  # 下側の角の丸み (外周の丸みに当たらないように)
    pts = [(7*U + 1, 3*U + 2), (5*U - 1, 3*U + 2)]
    for cx_, cy_, a0 in ((7*U + 1 - rr, 4*U + 1 - rr, 0), (5*U - 1 + rr, 4*U + 1 - rr, 90)):
        for k in range(0, 91, 15):
            t = math.radians(a0 + k)
            pts.append((cx_ + rr*math.cos(t), cy_ + rr*math.sin(t)))
    for k in range(0, 181, 10):
        t = math.radians(180 + k)
        pts.append((ex + 9*math.cos(t), ey + 9*math.sin(t)))
    o.append(f'<path d="{hull_path(pts)}" fill="none" stroke="{SUB}" stroke-width="0.3" '
             f'stroke-dasharray="2 1" stroke-linejoin="round"/>')
    o.append(key(5*U, 3*U, "英数"))
    o.append(key(6*U, 3*U, "Raise"))
    o.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{KNOB/2}" fill="none" stroke="{INK}" stroke-width="0.4"/>'
             f'<line x1="{ex:.2f}" y1="{ey-KNOB/2+1.5:.2f}" x2="{ex:.2f}" y2="{ey-2:.2f}" stroke="{INK}" stroke-width="0.4"/>'
             f'<text x="{ex:.2f}" y="{ey+3.5:.2f}" font-size="2.2" text-anchor="middle" fill="{SUB}">エンコーダー</text>')
    o.append(mcu(6*U + (U - MCU_W)/2, (2*U - MCU_H)/2))
    return "".join(o), 7*U, 4*U


def right_half():
    o = [case_outline(7*U, 4*U)]
    gx = 2*U
    for r, row in enumerate(RIGHT_ALPHA):
        for c, label in enumerate(row):
            o.append(key(gx + c*U, r*U, label))
    o.append(key(U, 0, "["))
    o.append(key(U, U, "]"))
    cx, cy = U, 3.25*U
    o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{HOUSING/2}" fill="none" stroke="{SUB}" stroke-width="0.3" stroke-dasharray="2 1"/>'
             f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{BALL/2}" fill="none" stroke="{INK}" stroke-width="0.5"/>'
             f'<text x="{cx:.2f}" y="{cy+1.5:.2f}" font-size="4" text-anchor="middle" fill="{INK}">25mm</text>'
             f'<text x="{cx:.2f}" y="{cy+6:.2f}" font-size="2.2" text-anchor="middle" fill="{SUB}">ボール</text>')
    o.append(mcu((U - MCU_W)/2, (2*U - MCU_H)/2))
    return "".join(o), 7*U, 4*U


def page(title, body, w, h):
    ox = (PAGE_W - (w + 2*WALL)) / 2 + WALL
    oy = (PAGE_H - (h + 2*WALL)) / 2 + WALL + 6
    ow, oh = w + 2*WALL, h + 2*WALL
    return f'''<section class="page"><svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm"
 viewBox="0 0 {PAGE_W} {PAGE_H}" font-family="IPAPGothic, IPAGothic, sans-serif">
<text x="12" y="16" font-size="6" font-weight="bold" fill="{INK}">kataware 実寸テンプレート — {title}</text>
<text x="12" y="23" font-size="3.4" fill="{SUB}">印刷は「実際のサイズ（100%）」で。下の線が 50mm ちょうどか定規で確認してから使ってください。</text>
<text x="12" y="28" font-size="3.4" fill="{SUB}">外形 約{ow:.0f} × {oh:.0f}mm／角の丸み R{RADIUS:.0f}mm／キー間隔 19.05mm／キーキャップは 18mm 角の目安</text>
<g transform="translate({ox:.2f},{oy:.2f})">{body}</g>
<line x1="12" y1="196" x2="62" y2="196" stroke="{INK}" stroke-width="0.6"/>
<line x1="12" y1="193.5" x2="12" y2="198.5" stroke="{INK}" stroke-width="0.6"/>
<line x1="62" y1="193.5" x2="62" y2="198.5" stroke="{INK}" stroke-width="0.6"/>
<text x="37" y="192" font-size="3.4" text-anchor="middle" fill="{INK}">50mm</text>
</svg></section>'''


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    lb, lw, lh = left_half()
    rb, rw, rh = right_half()
    html = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>kataware 実寸テンプレート</title>
<style>@page {{ size: A4 landscape; margin: 0; }} html, body {{ margin: 0; padding: 0; background: #fff; }}
.page {{ width: 297mm; height: 210mm; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }} svg {{ display: block; }}</style></head><body>
{page("左手", lb, lw, lh)}
{page("右手", rb, rw, rh)}
</body></html>'''
    path = os.path.join(out_dir, "kataware-template.html")
    with open(path, "w") as f:
        f.write(html)
    print(path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/template")
