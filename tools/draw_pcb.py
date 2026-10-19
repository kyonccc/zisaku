"""kataware の基板イメージ (上から見た図) を SVG で生成する。
位置は pcb/ergogen/config.yaml と同じ。寸法は mm、部品の大きさは目安。

使い方: python3 tools/draw_pcb.py docs/images
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case"))
import kataware_case  # noqa: E402  (Ergogen の DXF から基板の外形を読む)
import ukishima  # noqa: E402  (浮島: 電池・柱・ユニットの留めネジの位置)

U = 19.05
WALL = 5.0
CORNER = 14.0
BOARD_W, BOARD_H = 7*U + 2*WALL, 4*U + 2*WALL
BALL_HOLE_R = 18.0       # 基板・プレートの穴 (直径36mm = ユニット34mm + すき間1mm)
UNIT_R = 17.0            # ボールユニットの外径 34mm (25mm 用・19mm 用で共通)
SCREW_R = 13.5           # 底ネジの位置 (ユニット中心から)
S = 5.0                  # px / mm

C = {"bg": "#f7f7f5", "ink": "#333", "sub": "#666", "pcb": "#2f6f3e", "pcbfill": "#e3efe6",
     "key": "#ffffff", "back": "#d35400", "xiao": "#2e7d32", "view": "#1f2a33", "ball": "#c0392b",
     "unit": "#f3d6d2", "enc": "#5d6d7e", "sw": "#f0a500", "bat": "#7f8c8d", "screw": "#1a5276"}

LEFT = [
    ["Q", "W", "E", "R", "T", "-"],
    ["A", "S", "D", "F", "G", "'"],
    ["Z", "X", "C", "V", "B"],
    ["Shift", "Tab", "Ctrl", "Lower", "Space", "英数", "Raise"],
]
RIGHT = [
    ["Y", "U", "I", "O", "P"],
    ["H", "J", "K", "L", ";"],
    ["N", "M", ",", ".", "/"],
    ["Enter", "Raise", "BS", "かな", "Shift"],
]


class Board:
    """Ergogen 座標 (y 上がプラス) で描く。xmin / ymax が図の左上"""

    def __init__(self, ox, oy, xmin, ymax):
        self.ox, self.oy, self.xmin, self.ymax = ox, oy, xmin, ymax
        self.o = []

    def X(self, x):
        return self.ox + (x - self.xmin)*S

    def Y(self, y):
        return self.oy + (self.ymax - y)*S

    def rect(self, cx, cy, w, h, fill="none", stroke=None, dash=None, rx=0.5, sw=1.5, op=1.0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<rect x="{self.X(cx - w/2):.1f}" y="{self.Y(cy + h/2):.1f}" width="{w*S:.1f}" '
                      f'height="{h*S:.1f}" rx="{rx*S:.1f}" fill="{fill}" fill-opacity="{op}"{st}{d}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, dash=None, sw=1.5, op=1.0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<circle cx="{self.X(cx):.1f}" cy="{self.Y(cy):.1f}" r="{r*S:.1f}" fill="{fill}" '
                      f'fill-opacity="{op}"{st}{d}/>')

    def text(self, x, y, t, size=14, anchor="middle", color=None, weight="normal"):
        self.o.append(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-size="{size}" text-anchor="{anchor}" '
                      f'fill="{color or C["ink"]}" font-weight="{weight}">{t}</text>')

    def outline(self, cx, cy, side, dx=0.0):
        # ケースの外形 (グレーの点線) と、基板の外形 (緑。Ergogen の DXF そのもの)
        self.rect(cx, cy, BOARD_W, BOARD_H, "#ffffff", "#9aa3ad", dash="8 5", rx=CORNER, sw=2)
        for poly in kataware_case.polys(kataware_case.load(f"pcb_{side}")):
            for ring in [poly.exterior] + list(poly.interiors):
                d = "M" + " L".join(f"{self.X(x - dx):.1f},{self.Y(y):.1f}" for x, y in ring.coords) + " Z"
                self.o.append(f'<path d="{d}" fill="{C["pcbfill"]}" stroke="{C["pcb"]}" stroke-width="3"/>')

    def key(self, x, y, label):
        # 表: スイッチ (Choc v2) とキーの名前
        self.rect(x, y, 15, 15, C["key"], C["ink"], rx=1.2, sw=1.2)
        self.circle(x, y, 2.5, "none", "#bbb", sw=1)
        size = 15 if len(label) == 1 else (12 if len(label) <= 3 else 10)
        self.text(x, y + 3.6, label, size)
        # 裏: ホットスワップソケット (KiCad の座標は y 下向き → ここでは y を反転)
        self.rect(x + 2.5, y + 4.85, 11.6, 4.6, "none", C["back"], dash="4 3", rx=0.6, sw=1.2)
        # 裏: ダイオード (キーの手前 5mm・右へ 2mm)
        self.rect(x + 2, y - 5, 3.7, 1.6, C["back"], None, rx=0.2, op=0.55)

    def xiao(self, x, y, toward):
        # 横向き。USB-C は内側の側面 (toward の向き) に出る
        self.rect(x, y, 21, 17.8, C["xiao"], C["xiao"], dash="5 4", op=0.15, rx=1)
        self.rect(x + toward*(10.5 - 1.6), y, 3.2, 9, "#90a4ae", C["ink"], rx=0.8, sw=1)
        self.text(x - toward*1.5, y - 6.5, "XIAO（裏）", 11, color=C["xiao"])

    def view(self, x, y):
        self.rect(x, y, 14, 36, C["view"], None, rx=0.8, op=0.88)
        self.rect(x, y, 10.7, 25.3, "#7f8c8d", None, rx=0.3, op=0.9)
        self.o.append(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-size="12" fill="#fff" '
                      f'text-anchor="middle" transform="rotate(-90 {self.X(x):.1f} {self.Y(y):.1f})">nice!view（表）</text>')

    def power(self, x, y, toward):
        self.rect(x, y, 3.5, 8.5, C["sw"], C["ink"], rx=0.4, sw=1)
        self.rect(x + toward*2.6, y, 1.8, 2.6, C["ink"], None, rx=0.2)
        self.text(x - toward*1, y - 7.5, "電源", 11, color=C["sub"])

    def battery(self, x, y, conn_x, conn_y):
        self.rect(x, y, 30, 20, C["bat"], C["bat"], dash="6 4", op=0.12, rx=1.5)
        self.text(x, y - 1.5, "電池（裏）", 12, color=C["sub"])
        self.rect(conn_x, conn_y, 9, 4.5, C["back"], C["ink"], rx=0.3, sw=1)   # 電池コネクタ (横向き)
        self.text(conn_x, conn_y + 6.5, "電池コネクタ", 9, color=C["back"])

    def nuts(self, side, dx=0.0):
        """浮島: 基板の裏の M2 ナット (トレイの柱に下から留める所)"""
        for x, y in ukishima.cu.POSTS[side]:
            self.circle(x - dx, y, 2.5, "#fff", C["back"], sw=1.5)
            self.circle(x - dx, y, 1.2, C["back"], None)

    def svg(self):
        return "".join(self.o)


def left_board(ox, oy):
    b = Board(ox, oy, -0.5*U - WALL, 3.5*U + WALL)
    b.outline(3*U, 1.5*U, "left")
    for c in range(7):
        for r in range(4):         # r: 0=親指の段 … 3=一番上
            row = LEFT[3 - r]
            if c >= len(row) or (c == 5 and r == 1) or (c == 6 and r != 0):
                continue
            b.key(c*U, r*U, row[c])
    # エンコーダー (英数・Raise の上の真ん中)
    ex, ey = 5.5*U, U
    b.rect(ex, ey, 12, 12, "#d5d8dc", C["enc"], rx=0.8)
    b.circle(ex, ey, 7.5, "none", C["enc"], sw=2)
    b.circle(ex, ey, 3, C["enc"])
    b.rect(ex - 9, ey - 9.2, 3.7, 1.6, C["back"], None, rx=0.2, op=0.55)
    b.text(ex, ey + 9, "エンコーダー", 11, color=C["enc"])
    b.xiao(6.5*U - 8, kataware_case.HALVES["left"]["xiao"][1], +1)
    b.view(6*U, 2.5*U)
    b.power(6.5*U + 0.85, 52.5, +1)
    b.battery(*ukishima.BATTERY["left"], 48, 29)
    b.nuts("left")
    return b.svg()


def right_board(ox, oy):
    b = Board(ox, oy, -1.5*U - WALL, 3.5*U + WALL)
    b.outline(2*U, 1.5*U, "right", dx=kataware_case.RIGHT_X)
    for r in range(4):
        for i in range(5):
            b.key((i + 1)*U, r*U, RIGHT[3 - r][i])
    b.key(0, 3*U, "[")
    b.key(0, 2*U, "]")
    # ボールユニット
    bx, by = kataware_case.HALVES["right"]["ball"]
    bx -= kataware_case.RIGHT_X
    b.circle(bx, by, UNIT_R, C["unit"], C["ink"], sw=1.5)            # ユニット (34mm)
    b.circle(bx, by, 12.5, C["ball"], None, op=0.85)                  # ボール 25mm
    b.text(bx, by + 2.5, "25mm", 15, color="#fff", weight="bold")
    for a in ukishima.TAB_ANGLES:                                     # ユニットをトレイに留めるネジ (トレイの裏から)
        sx, sy = bx + ukishima.TAB_SCREW_R*math.cos(math.radians(a)), by + ukishima.TAB_SCREW_R*math.sin(math.radians(a))
        b.circle(sx, sy, 1.9, "#fff", C["screw"], sw=2)
        b.o.append(f'<path d="M{b.X(sx)-6:.1f},{b.Y(sy):.1f} h12 M{b.X(sx):.1f},{b.Y(sy)-6:.1f} v12" '
                   f'stroke="{C["screw"]}" stroke-width="1.5"/>')
    # センサーへのケーブルの端子 (裏・ボールの穴のすぐ上)
    # センサーのケーブルをつなぐコネクタ J (裏・Enter と N のあいだ。JST SH 6ピン)
    hx, hy = 247 - kataware_case.RIGHT_X, 29
    b.rect(hx, hy, 8, 4.4, "none", C["back"], dash="4 3", rx=0.3, sw=1.2)
    for k in range(6):
        b.rect(hx + (k - 2.5)*1.0, hy + 1.3, 0.6, 1.5, C["back"], None, rx=0.1)
    b.text(hx, hy - 4.2, "J", 11, color=C["back"])
    b.xiao(-1.5*U + 8, kataware_case.HALVES["right"]["xiao"][1], -1)
    b.view(-U, 2.5*U)
    b.power(-1.5*U - 0.85, 52.5, -1)
    ex, ey = ukishima.BATTERY["right"]
    b.battery(ex - kataware_case.RIGHT_X, ey, 267 - kataware_case.RIGHT_X, 10)
    b.nuts("right", kataware_case.RIGHT_X)
    return b.svg()


def plates_view():
    """プレート (Choc v2・FR4 など) の図面。Ergogen の plate_*.dxf をそのまま描く"""
    sc, gap = 4.0, 30
    shapes = [kataware_case.load("plate_left"), kataware_case.load("plate_right")]
    xs = [sh.bounds for sh in shapes]
    W = int(sum((b[2] - b[0]) * sc for b in xs) + 3 * gap)
    H = int(max(b[3] - b[1] for b in xs) * sc + 140)
    o = [f'<text x="{gap}" y="38" font-size="26" font-weight="bold" fill="{C["ink"]}">プレート（Choc v2・穴 13.8mm 角・耳やネジ穴なし）</text>']
    x0 = gap
    for sh, b in zip(shapes, xs):
        d = ""
        for poly in ([sh] if sh.geom_type == "Polygon" else list(sh.geoms)):
            for ring in [poly.exterior] + list(poly.interiors):
                d += "M" + " L".join(f"{x0 + (x - b[0]) * sc:.1f},{70 + (b[3] - y) * sc:.1f}" for x, y in ring.coords) + " Z "
        o.append(f'<path d="{d}" fill="#3a3b3f" fill-rule="evenodd" stroke="{C["ink"]}" stroke-width="1"/>')
        x0 += (b[2] - b[0]) * sc + gap
    o.append(f'<text x="{gap}" y="{H - 30}" font-size="16" fill="{C["sub"]}">pcb/ergogen/output/outlines/plate_left.dxf ・ plate_right.dxf'
             f'（FR4 1.2mm で注文できる）</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="Noto Sans CJK JP, sans-serif"><rect width="{W}" height="{H}" fill="{C["bg"]}"/>' + "".join(o) + "</svg>")


def top_view():
    gap = 40
    W = int(2*BOARD_W*S + 3*gap)
    H = int(BOARD_H*S + 230)
    oy = 95
    lx, rx = gap, 2*gap + BOARD_W*S
    o = [f'<text x="{gap}" y="38" font-size="28" font-weight="bold" fill="{C["ink"]}">kataware 基板のイメージ（上から見た図・浮島）</text>',
         f'<text x="{gap}" y="70" font-size="17" fill="{C["sub"]}">実線 = 基板の表（上）にある物　／　オレンジや点線 = 基板の裏（下）にある物。部品の大きさは目安</text>',
         left_board(lx, oy), right_board(rx, oy),
         f'<text x="{lx + BOARD_W*S/2:.0f}" y="{oy + BOARD_H*S + 30:.0f}" font-size="20" text-anchor="middle" font-weight="bold" fill="{C["ink"]}">左手（24キー＋エンコーダー）</text>',
         f'<text x="{rx + BOARD_W*S/2:.0f}" y="{oy + BOARD_H*S + 30:.0f}" font-size="20" text-anchor="middle" font-weight="bold" fill="{C["ink"]}">右手（22キー＋トラックボール）</text>']
    legend = [
        (C["back"], "点線の横長の枠 = ホットスワップソケット（裏）、小さい四角 = ダイオード（裏）、白い丸 = トレイの柱に留める M2 ナット（裏・8か所）"),
        (C["pcb"], "緑の太線 = 基板の外形（内側の「舌」に USB-C と電源）、グレーの点線 = トレイの外形"),
        (C["screw"], "青い ＋ = ボールユニットの耳をトレイの裏からとめるネジ3本（基板には穴なし）"),
    ]
    for i, (col, t) in enumerate(legend):
        y = oy + BOARD_H*S + 70 + i*28
        o.append(f'<rect x="{gap}" y="{y-14:.0f}" width="18" height="18" rx="3" fill="{col}"/>'
                 f'<text x="{gap+28}" y="{y:.0f}" font-size="17" fill="{C["ink"]}">{t}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(o) + "</svg>")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/images"
    open(f"{out}/pcb-top.svg", "w").write(top_view())
    open(f"{out}/plates-choc.svg", "w").write(plates_view())
