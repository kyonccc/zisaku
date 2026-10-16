"""kataware の基板イメージ (上から見た図) と、ボールユニットの底ネジ止めの断面図を SVG で生成する。
位置は pcb/ergogen/config.yaml と同じ。寸法は mm、部品の大きさは目安。

使い方: python3 tools/draw_pcb.py docs/images
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case"))
import kataware_case  # noqa: E402  (Ergogen の DXF から基板の外形を読む)

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
        # 裏: ダイオード (キーの手前 5mm)
        self.rect(x, y - 5, 3.7, 1.6, C["back"], None, rx=0.2, op=0.55)

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
        self.rect(conn_x, conn_y, 6, 3.5, C["back"], C["ink"], rx=0.3, sw=1)

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
    b.rect(ex, ey - 9.2, 3.7, 1.6, C["back"], None, rx=0.2, op=0.55)
    b.text(ex, ey + 9, "エンコーダー", 11, color=C["enc"])
    b.xiao(6.5*U - 8, 37, +1)
    b.view(6*U, 2.5*U)
    b.power(6.5*U + 1.5, 51.5, +1)
    b.battery(29.0, 0.5*U, 0.5*U, 0.5*U)
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
    bx, by = -0.5*U, 0.25*U
    b.circle(bx, by, UNIT_R, C["unit"], C["ink"], sw=1.5)            # ユニット (34mm)
    b.circle(bx, by, 12.5, C["ball"], None, op=0.85)                  # ボール 25mm
    b.text(bx, by + 2.5, "25mm", 15, color="#fff", weight="bold")
    for a in (90, 210, 330):                                          # 底ネジ (裏から)
        sx, sy = bx + SCREW_R*math.cos(math.radians(a)), by + SCREW_R*math.sin(math.radians(a))
        b.circle(sx, sy, 1.9, "#fff", C["screw"], sw=2)
        b.o.append(f'<path d="M{b.X(sx)-6:.1f},{b.Y(sy):.1f} h12 M{b.X(sx):.1f},{b.Y(sy)-6:.1f} v12" '
                   f'stroke="{C["screw"]}" stroke-width="1.5"/>')
    # センサーへのケーブルの端子 (裏・ボールの穴のすぐ上)
    hx, hy = bx, by + 20.5
    b.rect(hx, hy, 15.6, 2.8, "none", C["back"], dash="4 3", rx=0.3, sw=1.2)
    for k in range(6):
        b.circle(hx + (k - 2.5)*2.54, hy, 0.6, C["back"])
    b.xiao(-1.5*U + 8, 37, -1)
    b.view(-U, 2.5*U)
    b.power(-1.5*U - 1.5, 51.5, -1)
    b.battery(67.7, 0.5*U, 4.5*U, 0.5*U)
    return b.svg()


def top_view():
    gap = 40
    W = int(2*BOARD_W*S + 3*gap)
    H = int(BOARD_H*S + 230)
    oy = 95
    lx, rx = gap, 2*gap + BOARD_W*S
    o = [f'<text x="{gap}" y="38" font-size="28" font-weight="bold" fill="{C["ink"]}">kataware 基板のイメージ（上から見た図・ガスケットマウント用）</text>',
         f'<text x="{gap}" y="70" font-size="17" fill="{C["sub"]}">実線 = 基板の表（上）にある物　／　オレンジや点線 = 基板の裏（下）にある物。部品の大きさは目安</text>',
         left_board(lx, oy), right_board(rx, oy),
         f'<text x="{lx + BOARD_W*S/2:.0f}" y="{oy + BOARD_H*S + 30:.0f}" font-size="20" text-anchor="middle" font-weight="bold" fill="{C["ink"]}">左手（24キー＋エンコーダー）</text>',
         f'<text x="{rx + BOARD_W*S/2:.0f}" y="{oy + BOARD_H*S + 30:.0f}" font-size="20" text-anchor="middle" font-weight="bold" fill="{C["ink"]}">右手（22キー＋トラックボール）</text>']
    legend = [
        (C["back"], "点線の横長の枠 = ホットスワップソケット（裏）、小さい四角 = ダイオード（裏）"),
        (C["pcb"], "緑の太線 = 基板の外形（ケースの内側より 0.75mm 小さい。内側の「舌」に USB-C と電源）、グレーの点線 = ケースの外形"),
        (C["screw"], "青い ＋ = ボールユニットを裏からとめるネジ3本（基板には穴なし。ケースの底からユニットへ）"),
    ]
    for i, (col, t) in enumerate(legend):
        y = oy + BOARD_H*S + 70 + i*28
        o.append(f'<rect x="{gap}" y="{y-14:.0f}" width="18" height="18" rx="3" fill="{col}"/>'
                 f'<text x="{gap+28}" y="{y:.0f}" font-size="17" fill="{C["ink"]}">{t}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(o) + "</svg>")


def mount_section():
    """ボールユニットの中心を通る断面 (手前から見た図)。z は机からの高さ"""
    P = 10.0                       # px / mm
    W, H = 1480, 800
    cx, base = 360, 640            # ユニット中心 x / 机の y (px)

    def X(x):
        return cx + x*P

    def Z(z):
        return base - z*P

    o = []
    add = o.append

    def box(x0, z0, x1, z1, fill, stroke=C["ink"], sw=1.5, op=1.0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<rect x="{X(min(x0, x1)):.1f}" y="{Z(max(z0, z1)):.1f}" width="{abs(x1-x0)*P:.1f}" '
            f'height="{abs(z1-z0)*P:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(x, z, t, size=17, anchor="start", color=C["ink"], weight="normal"):
        add(f'<text x="{X(x):.1f}" y="{Z(z):.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
            f'font-weight="{weight}">{t}</text>')

    def line(x0, z0, x1, z1, color=C["sub"], w=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<line x1="{X(x0):.1f}" y1="{Z(z0):.1f}" x2="{X(x1):.1f}" y2="{Z(z1):.1f}" stroke="{color}" '
            f'stroke-width="{w}"{d}/>')

    FLOOR = kataware_case.FLOOR    # ケース底の厚さ
    PCB0 = kataware_case.PCB_B     # 基板の下面
    PCB1 = PCB0 + 1.6
    PL0, PL1 = PCB1 + 1.0, PCB1 + 2.2   # Choc のプレート (FR4 1.2mm)
    UB = 1.5                       # ユニットの底の厚さ
    SEN0 = FLOOR + UB
    LENS1 = SEN0 + 1.6 + 3.0
    BALL_C = LENS1 + 2.4 + 12.5
    xl, xr = -28, 60               # 描く範囲 (ユニットの左の壁 … 右のキー)

    add(f'<text x="30" y="40" font-size="28" font-weight="bold" fill="{C["ink"]}">ボールユニットを「底からネジ止め」する断面イメージ</text>')
    add(f'<text x="30" y="72" font-size="17" fill="{C["sub"]}">ボールの中心を通る断面を手前から見た図。寸法は目安（部品の実測で決める）</text>')
    # ケース (底と左の壁)
    box(xl - 5, 0, xr, FLOOR, "#d9dde3")
    box(xl - 5, FLOOR, xl, PL1 + 3, "#d9dde3")
    # ガスケット (プレートの縁を上下から挟む)
    box(xl, PL1, xl + 6, PL1 + 1.5, "#f5b7b1", op=0.9)
    box(xl, PL0 - 1.5, xl + 6, PL0, "#f5b7b1", op=0.9)
    box(xl, PL1 + 1.5, xl + 6, PL1 + 3, "#d9dde3")           # 上側の押さえ (トップケース)
    box(xl, FLOOR, xl + 2, PL0 - 1.5, "#d9dde3")              # 下側の受け
    # プレートと基板 (ユニットの穴のところで切れている)
    hole = BALL_HOLE_R
    for x0, x1 in ((xl, -hole), (hole, xr)):
        box(x0, PL0, x1, PL1, "#c8b88a")
        box(x0 + (2 if x0 == xl else 0), PCB0, x1, PCB1, C["xiao"])
    # 右側のキー (Choc v2 + キーキャップ)
    kx = 31
    box(kx - 7.5, PCB1, kx + 7.5, PL1 + 5, "#ecf0f1")
    box(kx - 9, PL1 + 5, kx + 9, PL1 + 8.5, "#ffffff")
    box(kx - 5, PCB0 - 1.8, kx + 4, PCB0, C["back"], op=0.8)  # ソケット
    text(kx, PL1 + 10, "キー", 15, "middle", C["sub"])
    # ユニット本体 (カップ)
    box(-UNIT_R, FLOOR, UNIT_R, FLOOR + UB, C["unit"])
    box(-UNIT_R, FLOOR, -UNIT_R + 2.5, BALL_C + 2, C["unit"])
    box(UNIT_R - 2.5, FLOOR, UNIT_R, BALL_C + 2, C["unit"])
    # 上カバー
    for sg in (-1, 1):
        add(f'<path d="M{X(sg*UNIT_R):.1f},{Z(BALL_C+2):.1f} L{X(sg*UNIT_R):.1f},{Z(BALL_C+5):.1f} '
            f'L{X(sg*10.3):.1f},{Z(BALL_C+8):.1f} L{X(sg*10.3):.1f},{Z(BALL_C+5.5):.1f} Z" fill="#b0bec5" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # センサー・レンズ・ボール
    box(-10, SEN0, 10, SEN0 + 1.6, C["xiao"])
    box(-4.5, SEN0 + 1.6, 4.5, LENS1, "#90a4ae")
    add(f'<circle cx="{X(0):.1f}" cy="{Z(BALL_C):.1f}" r="{12.5*P:.1f}" fill="{C["ball"]}" fill-opacity="0.88"/>')
    text(0, BALL_C - 0.8, "25mm", 26, "middle", "#fff", "bold")
    for a in (-50, 50):
        t = math.radians(-90 + a)
        add(f'<circle cx="{X(14.1*math.cos(t)):.1f}" cy="{Z(BALL_C + 14.1*math.sin(t)):.1f}" r="{1.6*P:.1f}" '
            f'fill="{C["sw"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
    # 底ネジ (皿ネジ M2、ケースの底からユニットのインサートへ)
    for sx in (-SCREW_R, SCREW_R):
        add(f'<path d="M{X(sx-2):.1f},{Z(0):.1f} L{X(sx+2):.1f},{Z(0):.1f} L{X(sx+1):.1f},{Z(1):.1f} '
            f'L{X(sx+1):.1f},{Z(FLOOR+UB+2.5):.1f} L{X(sx-1):.1f},{Z(FLOOR+UB+2.5):.1f} L{X(sx-1):.1f},{Z(1):.1f} Z" '
            f'fill="{C["screw"]}"/>')
        box(sx - 1.8, FLOOR, sx + 1.8, FLOOR + UB + 3, "#b7950b", op=0.5, sw=1)
    # ケーブル (たるませる)
    add(f'<path d="M{X(8):.1f},{Z(SEN0+0.8):.1f} C{X(22):.1f},{Z(SEN0-0.5):.1f} {X(20):.1f},{Z(PCB0-4):.1f} '
        f'{X(23.5):.1f},{Z(PCB0-2.6):.1f}" fill="none" stroke="{C["back"]}" stroke-width="3"/>')
    box(21.5, PCB0 - 2.6, 26.5, PCB0, C["back"])
    # すき間の矢印
    line(-UNIT_R, PL1 + 5.5, -hole, PL1 + 5.5, C["ball"], 3)
    text(-UNIT_R - 0.5, PL1 + 6.5, "1mm", 14, "middle", C["ball"])
    # 説明
    notes = [
        (PL1 + 13, "① 基板とプレートは ガスケットで浮いている → 押すと上下に少し動く", C["ink"]),
        (PL1 + 10.3, "② ボールユニットは ケースの底にネジ止め → 動かない", C["ink"]),
        (PL1 + 7.6, "③ ユニットと穴のあいだに すき間 約1mm → 基板が動いてもユニットに当たらない", C["ball"]),
    ]
    for i, (_, t, col) in enumerate(notes):
        add(f'<text x="30" y="{125 + i*30}" font-size="19" fill="{col}">{t}</text>')
    labels = [
        (BALL_C + 7, "上カバー（ボールが外れないように押さえる）"),
        (PL1 + 1.5, "ガスケット（ピンク）とプレート"),
        (PCB0 + 0.6, "基板（緑・厚さ1.6mm）"),
        (PCB0 - 2.4, "ケーブルは たるませて つなぐ（基板が動いても引っぱらない）"),
        (SEN0 + 1.2, "PMW3610 センサー（ユニットの底・上向き）"),
        (0.6, "裏から 皿ネジ M2 × 3本（ゴム足の間）→ ユニット底のインサートへ"),
    ]
    zs = [z for z, _ in labels]
    for i in range(1, len(zs)):          # 上から順に、重ならないよう 2.6mm 以上あける
        zs[i] = min(zs[i], zs[i - 1] - 2.6)
    for z, (zt, t) in zip(zs, labels):
        line(xr + 0.5, zt, xr + 3.5, z + 0.5, C["sub"], 1)
        text(xr + 4, z, t, 16, color=C["sub"])
    # 机
    line(xl - 10, 0, xr + 2, 0, C["ink"], 2)
    text(xl - 8, -2.2, "机", 15, color=C["sub"])
    # 付け替えの手順
    steps = ["25mm ⇔ 19mm の付け替え（ユニットごと交換・外径34mmとネジ位置は共通）",
             "1. ボールを上から取り出す　2. 裏のネジ3本を外す",
             "3. ユニットを上に少し持ち上げ、センサー側のケーブルを抜く　4. もう一方のユニットを入れて逆の順番でとめる"]
    for i, t in enumerate(steps):
        add(f'<text x="30" y="{H - 100 + i*26}" font-size="{18 if i == 0 else 16}" '
            f'font-weight="{"bold" if i == 0 else "normal"}" fill="{C["ink"]}">{t}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>'
            + "".join(o) + "</svg>")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/images"
    open(f"{out}/pcb-top.svg", "w").write(top_view())
    open(f"{out}/ballmount-section.svg", "w").write(mount_section())
