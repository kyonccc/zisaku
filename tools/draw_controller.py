"""内側の帯 (マイコンまわり) の配置図を SVG で生成する。寸法は mm、目安。

使い方: python3 tools/draw_controller.py docs/images
"""
import sys

U = 19.05
WALL = 5.0
R = 14.0
S = 7.0  # px per mm

C = {"bg": "#f7f7f5", "ink": "#333", "sub": "#666", "case": "#ffffff", "edge": "#9aa3ad",
     "key": "#ffffff", "view": "#1f2a33", "viewact": "#7f8c8d", "xiao": "#2e7d32", "usb": "#90a4ae",
     "sw": "#f0a500", "rst": "#c0392b", "ball": "#c0392b", "housing": "#f3d6d2", "enc": "#5d6d7e"}

XIAO_W, XIAO_H = 17.8, 21.0       # XIAO nRF52840 Plus (厚さ 約5mm)
VIEW_W, VIEW_H = 14.0, 32.0       # nice!view のガラス (Sharp LS011B7DH03 外形 32 x 14mm)
VIEW_PCB_W, VIEW_PCB_H = 14.0, 36.0  # nice!view 本体 36 x 14 x 2.9mm
ACT_W, ACT_H = 10.74, 25.28       # 表示部
SW_W, SW_H = 3.5, 8.5             # スライドスイッチ (横向きに側面へ)


def px(v):
    return v * S


class Svg:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, fill, stroke=None, dash=None, rx=0.6, sw=2, op=1.0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{px(x):.1f}" y="{px(y):.1f}" width="{px(w):.1f}" height="{px(h):.1f}" rx="{px(rx):.1f}" '
                 f'fill="{fill}" fill-opacity="{op}"{st}{d}/>')

    def text(self, x, y, t, size=17, anchor="start", color=None, weight="normal"):
        self.add(f'<text x="{px(x):.1f}" y="{px(y):.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{color or C["ink"]}" font-weight="{weight}">{t}</text>')

    def line(self, x1, y1, x2, y2, color=None, w=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{px(x1):.1f}" y1="{px(y1):.1f}" x2="{px(x2):.1f}" y2="{px(y2):.1f}" '
                 f'stroke="{color or C["sub"]}" stroke-width="{w}"{d}/>')


def strip(svg, ox, oy, side):
    """片手の内側の帯まわりを描く。side='L' なら帯が右側、'R' なら左側"""
    # 表示範囲: キー2列 + 帯 2列 (=4U) x 4段
    if side == "L":
        x0 = ox - 2*U          # 左に T・G 列の手前2列だけ見せる
        cols_keys = [(ox - 2*U, "R"), (ox - U, "T"), (ox, "-")]
        ctrl_x = ox + U        # マイコン列
        inner_edge = ox + 2*U  # 内側 (相手側) のケース端
        case_x, case_w = x0, 4*U
    else:
        x0 = ox
        ctrl_x = ox            # マイコン列 (一番内側)
        cols_keys = [(ox + U, "["), (ox + 2*U, "Y"), (ox + 3*U, "U")]
        inner_edge = ox
        case_x, case_w = ox, 4*U
    # ケース (切り取り表示)
    svg.add(f'<rect x="{px(case_x-WALL):.1f}" y="{px(oy-WALL):.1f}" width="{px(case_w+2*WALL):.1f}" '
            f'height="{px(4*U+2*WALL):.1f}" rx="{px(R):.1f}" fill="{C["case"]}" stroke="{C["edge"]}" stroke-width="2"/>')
    # 切り取り線 (外側方向)
    cut_x = case_x - WALL if side == "L" else case_x + case_w + WALL
    svg.line(cut_x, oy - WALL - 2, cut_x, oy + 4*U + WALL + 2, C["bg"], 14)
    # キー (上2段)
    labels2 = {"R": "F", "T": "G", "-": "'", "[": "]", "Y": "H", "U": "J"}
    for x, lab in cols_keys:
        for r, l in enumerate([lab, labels2[lab]]):
            svg.rect(x + 0.6, oy + r*U + 0.6, U - 1.2, U - 1.2, C["key"], C["ink"], rx=1.5)
            svg.text(x + U/2, oy + r*U + U/2 + 1.6, l, 22, "middle")
    # XIAO (基板の裏側・点線)。USB-C は奥側 (上) のケース端へ
    xx = ctrl_x + (U - XIAO_W)/2
    xy = oy - 2.5
    svg.rect(xx, xy, XIAO_W, XIAO_H, C["xiao"], C["xiao"], dash="5 4", op=0.18)
    svg.rect(ctrl_x + U/2 - 4.5, oy - WALL - 1.0, 9.0, 7.5, C["usb"], C["ink"], rx=1.2)
    svg.text(ctrl_x + U/2, oy - WALL - 2.2, "USB-C", 15, "middle", C["sub"])
    # リセットボタン (裏向き) → 底面の穴から押す
    rx_ = xx + XIAO_W - 4.0 if side == "L" else xx + 4.0
    svg.add(f'<circle cx="{px(rx_):.1f}" cy="{px(xy+3.0):.1f}" r="{px(1.6):.1f}" fill="{C["rst"]}"/>')
    # nice!view (基板の表側)
    vx = ctrl_x + (U - VIEW_PCB_W)/2
    vy = oy + (2*U - VIEW_PCB_H)/2
    svg.rect(vx, vy, VIEW_PCB_W, VIEW_PCB_H, "#3d4b57", C["ink"], rx=1.0)
    svg.rect(ctrl_x + (U - ACT_W)/2, vy + (VIEW_PCB_H - ACT_H)/2, ACT_W, ACT_H, "#b8c4c9", None, rx=0.4)
    svg.text(ctrl_x + U/2, vy + VIEW_PCB_H/2 - 2, "nice!", 14, "middle", "#2b3640", "bold")
    svg.text(ctrl_x + U/2, vy + VIEW_PCB_H/2 + 2.5, "view", 14, "middle", "#2b3640", "bold")
    # スライドスイッチ (内側の側面)
    sx = inner_edge + WALL - SW_W + 1.2 if side == "L" else inner_edge - WALL - 1.2
    svg.rect(sx, oy + 8, SW_W, SW_H, C["sw"], C["ink"], rx=0.8)
    knob_y = oy + 8 + 1.0
    kx = sx + SW_W if side == "L" else sx - 2.0
    svg.rect(kx, knob_y, 2.0, 3.0, C["sw"], C["ink"], rx=0.4)
    # 下の段: 左はエンコーダーの塊、右はボール
    if side == "L":
        ex, ey = ox + U, oy + 2.5*U
        svg.add(f'<circle cx="{px(ex):.1f}" cy="{px(ey):.1f}" r="{px(7.5):.1f}" fill="{C["enc"]}" stroke="{C["ink"]}" stroke-width="2"/>')
        for i, l in enumerate(["英数", "Raise"]):
            svg.rect(ox + i*U + 0.6, oy + 3*U + 0.6, U - 1.2, U - 1.2, "#e6eef7", C["ink"], rx=1.5)
            svg.text(ox + i*U + U/2, oy + 3*U + U/2 + 1.4, l, 17, "middle")
        for (x, _), labs in zip(cols_keys[:2], (("V", "Lower"), ("B", "Space"))):
            for r, l in zip((2, 3), labs):
                svg.rect(x + 0.6, oy + r*U + 0.6, U - 1.2, U - 1.2, C["key"] if r == 2 else "#e6eef7", C["ink"], rx=1.5)
                svg.text(x + U/2, oy + r*U + U/2 + 1.6, l, 22 if len(l) == 1 else 17, "middle")
    else:
        svg.add(f'<circle cx="{px(ox+U):.1f}" cy="{px(oy+3.25*U):.1f}" r="{px(17):.1f}" fill="{C["housing"]}" stroke="{C["ball"]}" stroke-width="2" stroke-dasharray="8 5"/>')
        svg.add(f'<circle cx="{px(ox+U):.1f}" cy="{px(oy+3.25*U):.1f}" r="{px(12.5):.1f}" fill="{C["ball"]}" opacity="0.85"/>')
        for (x, _), labs in zip(cols_keys[1:], (("N", "Enter"), ("M", "Raise"))):
            for r, l in zip((2, 3), labs):
                svg.rect(x + 0.6, oy + r*U + 0.6, U - 1.2, U - 1.2, C["key"] if r == 2 else "#e6eef7", C["ink"], rx=1.5)
                svg.text(x + U/2, oy + r*U + U/2 + 1.6, l, 22 if len(l) == 1 else 17, "middle")


def top_view():
    svg = Svg()
    W, H = 1500, 980
    svg.text(3, 6, "マイコンまわりの配置（上から見た図・内側の帯を拡大）", 30, weight="bold")
    svg.text(3, 11, "XIAO（21×17.8×厚さ約5mm）は基板の裏側（点線）、nice!view（36×14×2.9mm）は表側に重ねる", 19, color=C["sub"])
    oy = 26
    strip(svg, 50, oy, "L")
    strip(svg, 128, oy, "R")
    svg.text(50 - 2*U + 2*U, oy + 4*U + WALL + 9, "左手（内側＝右端）", 22, "middle", weight="bold")
    svg.text(128 + 2*U, oy + 4*U + WALL + 9, "右手（内側＝左端）", 22, "middle", weight="bold")
    # 凡例
    ly = 124
    items = [("#3d4b57", "nice!view（表側・ケースの窓から見える）"), (C["xiao"], "XIAO nRF52840 Plus（裏側）"),
             (C["sw"], "電源スライドスイッチ（内側の側面）"), (C["rst"], "リセットボタン（裏向き → 底面の穴から押す）"),
             (C["usb"], "USB-C（奥側のケース端）")]
    for i, (col, lab) in enumerate(items):
        x = 3 + (i % 3) * 70
        y = ly + (i // 3) * 7
        svg.rect(x, y - 3.6, 4.5, 4.5, col, C["ink"], rx=0.6, op=0.85)
        svg.text(x + 6.5, y, lab, 19)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(svg.o) + "</svg>")


def section():
    """横から見た断面 (マイコンの列)。厚みは目安"""
    svg = Svg()
    W, H = 1500, 330
    svg.text(3, 6, "マイコンまわりの断面（横から見た図・厚みは目安）", 30, weight="bold")
    base = 38  # 机の高さ (mm 座標)
    x0, x1 = 20, 160
    # 層 (下から): 底板 1.5 / 空間(XIAO 3.5, 電池) / 基板 1.6 / nice!view / トップケース
    layers = []
    y = base
    def layer(h, label, fill, xa=x0, xb=x1, dash=None):
        nonlocal y
        y -= h
        svg.rect(xa, y, xb - xa, h, fill, C["ink"], dash=dash, rx=0.3, op=0.9)
        layers.append((y + h/2, label))
    layer(1.5, "底板（リセット穴）", "#d9dde3")
    y_air_bottom = y
    y -= 5.5
    svg.rect(70, y + 0.5, 21, 5.0, C["xiao"], C["ink"], rx=0.3, op=0.8)      # XIAO (21mm, 厚さ5mm)
    svg.rect(110, y + 0.5, 40, 5.0, "#cfd8dc", C["ink"], rx=0.6, op=0.9)      # 電池
    svg.text(80.5, y + 3.6, "XIAO 厚さ約5mm", 16, "middle", "#fff")
    svg.text(130, y + 3.6, "電池（厚さ5mm前後）", 17, "middle")
    svg.rect(66, y + 1.2, 4.0, 3.2, C["usb"], C["ink"], rx=0.3)
    svg.text(62, y + 3.0, "USB-C →", 16, "end", C["sub"])
    # リセットの穴と押し棒
    svg.rect(86, y_air_bottom - 0.2, 3, 1.9, C["bg"], None)
    svg.line(87.5, y + 5.5, 87.5, base + 4, C["rst"], 4)
    svg.text(90, base + 4.5, "← 細い棒・ピンで裏から押す", 17, color=C["rst"])
    layer(1.6, "メイン基板（PCB）", "#2e7d32")
    # nice!view とキー
    pcb_top = y
    svg.rect(70, pcb_top - 2.9, 36, 2.9, "#3d4b57", C["ink"], rx=0.2)      # nice!view 36mm, 2.9mm
    svg.rect(72, pcb_top - 3.4, 32, 0.6, "#b8c4c9", C["ink"], rx=0.1)
    svg.text(68, pcb_top - 1.0, "nice!view 厚さ2.9mm →", 16, "end")
    for kx in (112, 132):
        svg.rect(kx, pcb_top - 5.0, 14, 5.0, "#bbbbbb", C["ink"], rx=0.4)
        svg.rect(kx - 2, pcb_top - 9.5, 18, 4.5, "#ffffff", C["ink"], rx=1.0)
    svg.text(127, pcb_top - 11, "キースイッチ＋キーキャップ", 18, "middle")
    # トップケースと窓
    tc = pcb_top - 8.5
    svg.rect(x0, tc, 50, 1.6, "#e6e6e6", C["ink"], rx=0.3)
    svg.rect(106, tc, 2, 1.6, "#e6e6e6", C["ink"], rx=0.3)
    svg.text(88, tc - 1.8, "↓ 画面の窓（透明板）", 17, "middle", C["sub"])
    svg.rect(70, tc, 36, 1.0, "#d6eaf8", C["ink"], rx=0.2, op=0.8)
    svg.text(x0 + 2, tc - 1.5, "トップケース", 17)
    # 机
    svg.line(x0 - 5, base, x1 + 5, base, C["ink"], 2)
    svg.text(x1 + 5, base + 4.5, "机", 16, "end", C["sub"])
    svg.text(x1 + 3, base - 3.2, "↕ 基板の下は 5.5mm 以上", 17, color=C["sub"])
    # ラベル
    for yy, lab in layers:
        svg.text(x1 + 3, yy + 1.0, lab, 17, color=C["sub"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(svg.o) + "</svg>")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/images"
    open(f"{out}/controller-top.svg", "w").write(top_view())
    open(f"{out}/controller-section.svg", "w").write(section())
