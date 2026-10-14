"""25mm トラックボール専用ケース(ベアリング式・センサー底面)の概念図を SVG で生成する。
寸法はおおよその目安。実際の値は部品の実測で決める。"""
import math
import sys

S = 9.0  # px per mm
BALL_R = 12.5
GAP = 2.4          # PMW3610 + レンズ: レンズ基準面〜追跡面の距離の目安
LENS_H = 3.0       # レンズ部の高さ目安
SENSOR_PCB = 1.6
BOTTOM = 1.5       # ケース底板
C = {"bg": "#f7f7f5", "ink": "#333", "sub": "#666", "ball": "#c0392b", "case": "#d9dde3",
     "pcb": "#2e7d32", "lens": "#90a4ae", "bear": "#f0a500", "cover": "#b0bec5", "key": "#ffffff"}


def px(v):
    return v * S


def cross_section():
    W, H = 820, 540
    o = []
    add = o.append
    ox, base = 260, 470  # ボール中心 x / 机の高さ (px)
    y_bottom_top = base - px(BOTTOM)
    y_pcb_top = y_bottom_top - px(SENSOR_PCB)
    y_lens_top = y_pcb_top - px(LENS_H)
    y_ball_bottom = y_lens_top - px(GAP)
    cy = y_ball_bottom - px(BALL_R)

    add(f'<text x="20" y="34" font-size="26" font-weight="bold" fill="{C["ink"]}">ボールケースの断面イメージ（横から見た図）</text>')
    add(f'<text x="20" y="62" font-size="17" fill="{C["sub"]}">寸法はおおよその目安。実際の部品を測って最終決定します</text>')
    # ケース外形 (カップ)
    cup_w = px(34)
    add(f'<path d="M{ox-cup_w/2},{base} L{ox-cup_w/2},{cy-px(3)} L{ox-cup_w/2+px(3)},{cy-px(3)} '
        f'L{ox-cup_w/2+px(3)},{y_bottom_top} L{ox+cup_w/2-px(3)},{y_bottom_top} L{ox+cup_w/2-px(3)},{cy-px(3)} '
        f'L{ox+cup_w/2},{cy-px(3)} L{ox+cup_w/2},{base} Z" fill="{C["case"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    # 上カバー(ボール押さえ)
    for sgn in (-1, 1):
        x0 = ox + sgn*(cup_w/2)
        x1 = ox + sgn*px(BALL_R*0.82)
        add(f'<path d="M{x0},{cy-px(3)} L{x0},{cy-px(6)} L{x1},{cy-px(9.5)} L{x1},{cy-px(7)} Z" fill="{C["cover"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    # センサー基板とレンズ
    add(f'<rect x="{ox-px(10)}" y="{y_pcb_top}" width="{px(20)}" height="{px(SENSOR_PCB)}" fill="{C["pcb"]}"/>')
    add(f'<rect x="{ox-px(4.5)}" y="{y_lens_top}" width="{px(9)}" height="{px(LENS_H)}" rx="3" fill="{C["lens"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # ボール
    add(f'<circle cx="{ox}" cy="{cy}" r="{px(BALL_R)}" fill="{C["ball"]}" opacity="0.88"/>')
    add(f'<text x="{ox}" y="{cy+8}" font-size="24" text-anchor="middle" fill="#fff" font-weight="bold">25mm</text>')
    # ベアリング(下半球 120°配置のうち断面に見える2個)
    for ang in (-50, 50):
        a = math.radians(90 + ang)
        bx = ox + px((BALL_R+1.6)*math.cos(a))
        by = cy + px((BALL_R+1.6)*math.sin(a))
        add(f'<circle cx="{bx}" cy="{by}" r="{px(1.6)}" fill="{C["bear"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # 寸法: ボール下〜レンズ
    add(f'<line x1="{ox+px(6)}" y1="{y_ball_bottom}" x2="{ox+px(6)}" y2="{y_lens_top}" stroke="{C["sub"]}" stroke-width="2"/>')
    # 説明ラベル
    labels = [
        (cy - px(9), "上カバー：ボールが外れないように押さえる"),
        (cy + px(BALL_R*0.6), "ベアリング×3（120°間隔）でボールを支える"),
        (y_lens_top - px(GAP/2), "すき間 約2.4mm（センサーが読める距離）"),
        (y_lens_top + px(LENS_H/2), "レンズ"),
        (y_pcb_top + px(SENSOR_PCB/2), "PMW3610 基板（底面に上向きで固定）"),
        (base - px(BOTTOM/2), "ケース底板"),
    ]
    # ラベルが重ならないよう、下から順に最低 28px 間隔をあける
    ys = [y for y, _ in labels]
    for i in range(len(ys) - 2, -1, -1):
        ys[i] = min(ys[i], ys[i + 1] - 28)
    labels = [(y, t) for y, (_, t) in zip(ys, labels)]
    for y, t in labels:
        add(f'<line x1="{ox+px(17.5)}" y1="{y}" x2="{ox+px(21)}" y2="{y}" stroke="{C["sub"]}" stroke-width="1.5"/>')
        add(f'<text x="{ox+px(22)}" y="{y+6}" font-size="18" fill="{C["ink"]}">{t}</text>')
    # 高さ
    top = cy - px(BALL_R)
    add(f'<line x1="{ox-px(21)}" y1="{top}" x2="{ox-px(21)}" y2="{base}" stroke="{C["sub"]}" stroke-width="2"/>')
    h_mm = (base - top) / S
    add(f'<text x="{ox-px(22.5)}" y="{(top+base)/2}" font-size="18" fill="{C["sub"]}" text-anchor="middle" '
        f'transform="rotate(-90 {ox-px(22.5)} {(top+base)/2})">ボール頂点まで 約{h_mm:.0f}mm</text>')
    add(f'<line x1="20" y1="{base}" x2="{W-20}" y2="{base}" stroke="{C["ink"]}" stroke-width="2"/>')
    add(f'<text x="{W-20}" y="{base+24}" font-size="16" fill="{C["sub"]}" text-anchor="end">机</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+20}" viewBox="0 0 {W} {H+20}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(o) + "</svg>")


def top_view():
    W, H = 420, 540
    o = []
    add = o.append
    cx, cy = W/2, 290
    add(f'<text x="20" y="34" font-size="26" font-weight="bold" fill="{C["ink"]}">上から見た図</text>')
    add(f'<circle cx="{cx}" cy="{cy}" r="{px(17)}" fill="{C["case"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    add(f'<rect x="{cx-px(10)}" y="{cy-px(10)}" width="{px(20)}" height="{px(20)}" fill="{C["pcb"]}" opacity="0.35" stroke="{C["pcb"]}" stroke-dasharray="6 4"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="{px(BALL_R)}" fill="{C["ball"]}" opacity="0.55"/>')
    for k in range(3):
        a = math.radians(90 + k*120)
        r = BALL_R*0.72
        add(f'<circle cx="{cx+px(r*math.cos(a))}" cy="{cy+px(r*math.sin(a))}" r="{px(1.8)}" fill="{C["bear"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="{px(2)}" fill="{C["lens"]}" stroke="{C["ink"]}"/>')
    notes = ["オレンジ：ベアリング（3個・120°間隔）", "緑の点線：底面の PMW3610 基板", "中央：センサーが読む位置",
             "ケース外径の目安：約34mm"]
    for i, t in enumerate(notes):
        add(f'<text x="20" y="{455+i*24}" font-size="17" fill="{C["ink"]}">{t}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+20}" viewBox="0 0 {W} {H+20}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(o) + "</svg>")


if __name__ == "__main__":
    out = sys.argv[1]
    open(f"{out}/ballcase-section.svg", "w").write(cross_section())
    open(f"{out}/ballcase-top.svg", "w").write(top_view())
