"""kataware 配置イメージ図を SVG で生成する (1mm = S px, 寸法は実寸比)"""
import sys

S = 5.0          # px per mm
U = 19.05        # キーピッチ mm
CAP = 17.5       # キーキャップの見た目サイズ mm
BALL = 25.0      # ボール直径 mm
HOUSING = 32.0   # ボール受け皿の目安 mm
GAP = 45.0       # 左右の間隔 mm (図の見やすさ用)
MARGIN = 14.0

C = {
    "bg": "#f7f7f5", "alpha": "#ffffff", "mod": "#e6eef7", "extra": "#ffe7c2",
    "stroke": "#4a4a4a", "text": "#222", "sub": "#666", "ball": "#c0392b",
    "housing": "#f3d6d2", "empty": "#bbbbbb", "thumb": "#2e86de", "grid": "#e2e2de",
}

LEFT_ALPHA = [list("QWERT"), list("ASDFG"), list("ZXCVB")]
RIGHT_ALPHA = [list("YUIOP"), ["H", "J", "K", "L", ";"], ["N", "M", ",", ".", "/"]]
LEFT_ROW4 = ["Ctrl", "Alt", "GUI", "Lower", "Space"]      # 外側→内側
RIGHT_ROW4 = ["Enter", "Raise", "かな", "Alt", "Shift"]    # 内側→外側


def mm(v):
    return v * S


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, s):
        self.items.append(s)

    def key(self, x, y, label, fill, dashed=False, w=1, h=1):
        pad = (U - CAP) / 2
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        self.add(f'<rect x="{mm(x+pad):.1f}" y="{mm(y+pad):.1f}" width="{mm(U*w-2*pad):.1f}" '
                 f'height="{mm(U*h-2*pad):.1f}" rx="{mm(1.8):.1f}" fill="{fill}" '
                 f'stroke="{C["empty"] if dashed else C["stroke"]}" stroke-width="2"{dash}/>')
        if label:
            fs = 30 if len(label) == 1 else (19 if len(label) <= 3 else 16)
            col = C["sub"] if dashed else C["text"]
            self.add(f'<text x="{mm(x+U*w/2):.1f}" y="{mm(y+U*h/2)+fs*0.36:.1f}" font-size="{fs}" '
                     f'text-anchor="middle" fill="{col}">{label}</text>')

    def ball(self, cx, cy):
        self.add(f'<circle cx="{mm(cx):.1f}" cy="{mm(cy):.1f}" r="{mm(HOUSING/2):.1f}" fill="{C["housing"]}" '
                 f'stroke="{C["ball"]}" stroke-width="2" stroke-dasharray="8 5"/>')
        self.add(f'<circle cx="{mm(cx):.1f}" cy="{mm(cy):.1f}" r="{mm(BALL/2):.1f}" fill="{C["ball"]}" opacity="0.85"/>')
        self.add(f'<text x="{mm(cx):.1f}" y="{mm(cy)+8:.1f}" font-size="22" text-anchor="middle" fill="#fff" '
                 f'font-weight="bold">25mm</text>')

    def thumb(self, x, y):
        # 親指の定位置マーク
        self.add(f'<circle cx="{mm(x+U-3.2):.1f}" cy="{mm(y+3.2):.1f}" r="{mm(2.6):.1f}" fill="{C["thumb"]}"/>')

    def text(self, x, y, s, size=22, anchor="start", color=None, weight="normal"):
        self.add(f'<text x="{mm(x):.1f}" y="{mm(y):.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{color or C["text"]}" font-weight="{weight}">{s}</text>')

    def dim_h(self, x1, x2, y, label):
        self.add(f'<line x1="{mm(x1):.1f}" y1="{mm(y):.1f}" x2="{mm(x2):.1f}" y2="{mm(y):.1f}" '
                 f'stroke="{C["sub"]}" stroke-width="1.5" marker-start="url(#a)" marker-end="url(#a)"/>')
        self.text((x1+x2)/2, y-1.2, label, 18, "middle", C["sub"])

    def dim_v(self, x, y1, y2, label):
        self.add(f'<line x1="{mm(x):.1f}" y1="{mm(y1):.1f}" x2="{mm(x):.1f}" y2="{mm(y2):.1f}" '
                 f'stroke="{C["sub"]}" stroke-width="1.5" marker-start="url(#a)" marker-end="url(#a)"/>')
        self.add(f'<text x="{mm(x)-8:.1f}" y="{mm((y1+y2)/2):.1f}" font-size="18" fill="{C["sub"]}" '
                 f'text-anchor="middle" transform="rotate(-90 {mm(x)-8:.1f} {mm((y1+y2)/2):.1f})">{label}</text>')

    def render(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" height="{self.h:.0f}" '
                f'viewBox="0 0 {self.w:.0f} {self.h:.0f}" font-family="IPAPGothic, IPAGothic, sans-serif">'
                f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0,2 L5,5 L0,8" fill="none" stroke="{C["sub"]}" '
                f'stroke-width="1.5"/></marker></defs>'
                f'<rect width="100%" height="100%" fill="{C["bg"]}"/>')
        return head + "".join(self.items) + "</svg>"


def half_left(svg, ox, oy, extra, extra_rows):
    """左手(ボールなし)。外側から5列。extra: 内側に足すマスの描き方"""
    for r in range(3):
        for c in range(5):
            svg.key(ox + c*U, oy + r*U, LEFT_ALPHA[r][c], C["alpha"])
    for c in range(5):
        svg.key(ox + c*U, oy + 3*U, LEFT_ROW4[c], C["mod"])
    svg.thumb(ox + 4*U, oy + 3*U)
    extra(svg, ox, oy)


def half_right(svg, ox, oy, ball_fn, alpha_ox):
    for r in range(3):
        for c in range(5):
            svg.key(alpha_ox + c*U, oy + r*U, RIGHT_ALPHA[r][c], C["alpha"])
    for c in range(5):
        svg.key(alpha_ox + c*U, oy + 3*U, RIGHT_ROW4[c], C["mod"])
    svg.thumb(alpha_ox, oy + 3*U)
    # 親指マークは内側(左上)に置き直す
    svg.items[-1] = (f'<circle cx="{mm(alpha_ox+3.2):.1f}" cy="{mm(oy+3*U+3.2):.1f}" r="{mm(2.6):.1f}" '
                     f'fill="{C["thumb"]}"/>')
    ball_fn(svg)


def legend(svg, x, y):
    items = [(C["alpha"], "英字キー"), (C["mod"], "4段目（親指・修飾キー）"),
             (C["extra"], "内側に追加したキー"), (C["housing"], "左右で対になる「塊」")]
    cx = x
    for fill, label in items:
        svg.add(f'<rect x="{mm(cx):.1f}" y="{mm(y):.1f}" width="{mm(6):.1f}" height="{mm(6):.1f}" rx="4" '
                f'fill="{fill}" stroke="{C["stroke"]}" stroke-width="1.5"/>')
        svg.text(cx + 8, y + 5, label, 20)
        cx += 8 + len(label) * 4.6 + 8
    svg.add(f'<circle cx="{mm(cx+3):.1f}" cy="{mm(y+3):.1f}" r="{mm(2.6):.1f}" fill="{C["thumb"]}"/>')
    svg.text(cx + 8, y + 5, "親指を自然に置く場所", 20)


def plan1():
    # 左手: 5列 + 内側2マス(4段目に追加キー, 5段目は空き)
    lw = 7 * U
    rw = 7 * U
    title_h = 30
    w = MARGIN*2 + lw + GAP + rw
    h = title_h + 5*U + 44
    svg = Svg(mm(w), mm(h))
    svg.text(MARGIN, 10, "修正案：ボールは4段目のすぐ内側（2×2マス）", 30, weight="bold")
    svg.text(MARGIN, 17, "全キーが 19.05mm の格子に一直線。ボールなし側は同じ場所の上段に親指キー2つ（合計42キー）", 20, color=C["sub"])
    oy = title_h
    lx = MARGIN

    def left_extra(s, ox, oy_):
        s.key(ox + 5*U, oy_ + 3*U, "BS", C["extra"])
        s.key(ox + 6*U, oy_ + 3*U, "Tab", C["extra"])
        s.key(ox + 5*U, oy_ + 4*U, "空き", C["bg"], dashed=True)
        s.key(ox + 6*U, oy_ + 4*U, "空き", C["bg"], dashed=True)

    half_left(svg, lx, oy, left_extra, None)
    rx = lx + lw + GAP
    ball_cx, ball_cy = rx + U, oy + 4*U

    def rball(s):
        s.add(f'<rect x="{mm(rx):.1f}" y="{mm(oy+3*U):.1f}" width="{mm(2*U):.1f}" height="{mm(2*U):.1f}" '
              f'fill="none" stroke="{C["grid"]}" stroke-width="2" stroke-dasharray="4 4"/>')
        s.ball(ball_cx, ball_cy)

    half_right(svg, rx, oy, rball, rx + 2*U)
    svg.text(lx + 3.5*U, oy + 5*U + 7, "左手（ボールなし）", 24, "middle", weight="bold")
    svg.text(rx + 3.5*U, oy + 5*U + 7, "右手（ボールあり）", 24, "middle", weight="bold")
    svg.dim_h(lx, lx + 5*U, oy - 2.5, "英字部分 約95mm")
    svg.dim_h(rx, rx + 7*U, oy + 5*U + 17, "最大幅 約133mm")
    svg.dim_v(rx + 7*U + 6, oy, oy + 5*U, "約95mm")
    legend(svg, MARGIN, h - 11)
    return svg.render()


def plan2():
    lw = 5 * U
    rw = 5 * U
    title_h = 30
    w = MARGIN*2 + lw + GAP + rw + 20
    h = title_h + 6*U + 34
    svg = Svg(mm(w), mm(h))
    svg.text(MARGIN, 10, "別案：ボールは4段目の内側2列の真下", 30, weight="bold")
    svg.text(MARGIN, 17, "横幅は約95mmのまま。縦が6マス分に伸び、ボールなし側の空きは押しにくい位置", 20, color=C["sub"])
    oy = title_h
    lx = MARGIN

    def left_extra(s, ox, oy_):
        for r in (4, 5):
            for c in (3, 4):
                s.key(ox + c*U, oy_ + r*U, "空き", C["bg"], dashed=True)

    half_left(svg, lx, oy, left_extra, None)
    rx = lx + lw + GAP

    def rball(s):
        s.add(f'<rect x="{mm(rx):.1f}" y="{mm(oy+4*U):.1f}" width="{mm(2*U):.1f}" height="{mm(2*U):.1f}" '
              f'fill="none" stroke="{C["grid"]}" stroke-width="2" stroke-dasharray="4 4"/>')
        s.ball(rx + U, oy + 5*U)

    half_right(svg, rx, oy, rball, rx)
    svg.text(lx + 2.5*U, oy + 6*U + 6, "左手（ボールなし）", 24, "middle", weight="bold")
    svg.text(rx + 2.5*U, oy + 6*U + 6, "右手（ボールあり）", 24, "middle", weight="bold")
    svg.dim_h(rx, rx + 5*U, oy - 2.5, "約95mm")
    svg.dim_v(rx + 5*U + 6, oy, oy + 6*U, "約114mm")
    legend(svg, MARGIN, h - 11)
    return svg.render()


def plan_final():
    """確定案: FrostOrtho 型。右手=5x4+内側にボール帯、左手=5x4+4段目内側に1キー"""
    STRIP = 2 * U         # 内側の帯 = キー2つ分 (38.1mm)。ボールの受け皿(約34mm)も収まる
    WALL = 5.0            # ケースの縁 (目安)
    RADIUS = 14.0         # 外周の角の丸み (これ以上大きいと角のキーキャップにかかる)
    def island(kx, ky, ex, ey):
        """2キー(kx..kx+2U, ky..ky+U) とエンコーダー(ex,ey) を包む丸みのある三角形"""
        import math
        pad = 1.0
        # 下側の角は外周の丸みに当たらないよう、半径4mm で丸める
        rr = 4.0
        pts = [(kx - pad, ky + 2.0), (kx + 2*U + pad, ky + 2.0)]
        for cx_, cy_, a0 in ((kx + 2*U + pad - rr, ky + U + pad - rr, 0), (kx - pad + rr, ky + U + pad - rr, 90)):
            for k in range(0, 91, 15):
                t = math.radians(a0 + k)
                pts.append((cx_ + rr*math.cos(t), cy_ + rr*math.sin(t)))
        for k in range(0, 181, 15):
            t = math.radians(180 + k)
            pts.append((ex + 9.0*math.cos(t), ey + 9.0*math.sin(t)))
        # 凸包
        pts = sorted(set(pts))
        def cross(o, a, b):
            return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
        lower, upper = [], []
        for p_ in pts:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p_) <= 0: lower.pop()
            lower.append(p_)
        for p_ in reversed(pts):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p_) <= 0: upper.pop()
            upper.append(p_)
        hull = lower[:-1] + upper[:-1]
        d = "M" + " L".join(f"{mm(x):.1f},{mm(y):.1f}" for x, y in hull) + " Z"
        svg.add(f'<path d="{d}" fill="{C["housing"]}" stroke="{C["housing"]}" stroke-width="6" stroke-linejoin="round"/>')
        svg.add(f'<path d="{d}" fill="none" stroke="{C["ball"]}" stroke-width="2" stroke-dasharray="8 5" stroke-linejoin="round"/>')

    title_h = 30
    rw = STRIP + 5 * U
    lw = rw               # 左右のケースを同じ大きさにする
    w = MARGIN*2 + lw + GAP + rw + 2*WALL + 14
    h = title_h + 4*U + 2*WALL + 46
    svg = Svg(mm(w), mm(h))
    svg.text(MARGIN, 10, "kataware：左の「塊」（エンコーダー＋英数＋Raise）と右のボールが対になる", 30, weight="bold")
    svg.text(MARGIN, 17, "全キーが 19.05mm の格子に一直線。合計46キー。左右のケースは同じ大きさ・角の丸み R14mm", 20, color=C["sub"])
    oy = title_h + WALL
    lx = MARGIN + WALL
    def case(x, y, cw, ch):
        svg.add(f'<rect x="{mm(x-WALL):.1f}" y="{mm(y-WALL):.1f}" width="{mm(cw+2*WALL):.1f}" '
                f'height="{mm(ch+2*WALL):.1f}" rx="{mm(RADIUS):.1f}" fill="#ffffff" stroke="#9aa3ad" stroke-width="2"/>')
    case(lx, oy, lw, 4*U)
    rx = lx + lw + WALL + GAP + WALL
    case(rx, oy, rw, 4*U)

    # 左手: 5x4 + 内側の帯 (4段目に英数キー、その上にエンコーダー、上部にマイコン)
    LROW4 = ["Shift", "Tab", "Ctrl", "Lower", "Space"]
    for r in range(3):
        for c in range(5):
            svg.key(lx + c*U, oy + r*U, LEFT_ALPHA[r][c], C["alpha"])
    for c in range(5):
        svg.key(lx + c*U, oy + 3*U, LROW4[c], C["mod"])
    # 左の「塊」: エンコーダーを英数・Raise の真上の中央に置き、3つを三角形の島でまとめる
    ex, ey = lx + 6*U, oy + 2.5*U
    island(lx + 5*U, oy + 3*U, ex, ey)
    svg.key(lx + 5*U, oy + 3*U, "英数", C["mod"])
    svg.key(lx + 6*U, oy + 3*U, "Raise", C["mod"])
    svg.add(f'<circle cx="{mm(ex):.1f}" cy="{mm(ey):.1f}" r="{mm(7.5):.1f}" fill="#5d6d7e" stroke="{C["stroke"]}" stroke-width="2"/>')
    svg.add(f'<circle cx="{mm(ex):.1f}" cy="{mm(ey):.1f}" r="{mm(5.5):.1f}" fill="#85929e"/>')
    svg.add(f'<line x1="{mm(ex):.1f}" y1="{mm(ey-5):.1f}" x2="{mm(ex):.1f}" y2="{mm(ey-1.5):.1f}" stroke="#fff" stroke-width="3"/>')
    svg.thumb(lx + 4*U, oy + 3*U)
    svg.key(lx + 5*U, oy, "-", C["extra"])
    svg.key(lx + 5*U, oy + U, "'", C["extra"])
    svg.add(f'<rect x="{mm(lx+6*U+1):.1f}" y="{mm(oy+1):.1f}" width="{mm(U-2):.1f}" height="{mm(2*U-2):.1f}" rx="8" '
            f'fill="none" stroke="{C["empty"]}" stroke-width="2" stroke-dasharray="6 5"/>')
    svg.text(lx + 6.5*U, oy + U - 1, "マイコン", 15, "middle", C["sub"])
    svg.text(lx + 6.5*U, oy + U + 4, "電源SW", 15, "middle", C["sub"])

    # 右手: 内側にボール帯
    gx = rx + STRIP
    RROW4 = ["Enter", "Raise", "BS", "かな", "Shift"]
    for r in range(3):
        for c in range(5):
            svg.key(gx + c*U, oy + r*U, RIGHT_ALPHA[r][c], C["alpha"])
    for c in range(5):
        svg.key(gx + c*U, oy + 3*U, RROW4[c], C["mod"])
    svg.add(f'<circle cx="{mm(gx+3.2):.1f}" cy="{mm(oy+3*U+3.2):.1f}" r="{mm(2.6):.1f}" fill="{C["thumb"]}"/>')
    svg.key(gx - U, oy, "[", C["extra"])
    svg.key(gx - U, oy + U, "]", C["extra"])
    svg.add(f'<rect x="{mm(rx+1):.1f}" y="{mm(oy+1):.1f}" width="{mm(U-2):.1f}" height="{mm(2*U-2):.1f}" rx="8" '
            f'fill="none" stroke="{C["empty"]}" stroke-width="2" stroke-dasharray="6 5"/>')
    svg.text(rx + U/2, oy + U - 1, "マイコン", 15, "middle", C["sub"])
    svg.text(rx + U/2, oy + U + 4, "電源SW", 15, "middle", C["sub"])
    svg.ball(rx + STRIP/2, oy + 3.25*U)

    svg.text(lx + lw/2, oy + 4*U + WALL + 8, "左手（24キー＋エンコーダー）", 24, "middle", weight="bold")
    svg.text(rx + rw/2, oy + 4*U + WALL + 8, "右手（22キー＋25mmボール）", 24, "middle", weight="bold")
    svg.dim_h(lx - WALL, lx + lw + WALL, oy - WALL - 2.5, "外形 約143mm（右と同じ）")
    svg.dim_h(rx - WALL, rx + rw + WALL, oy - WALL - 2.5, "外形 約143mm")
    svg.dim_v(rx + rw + WALL + 6, oy - WALL, oy + 4*U + WALL, "外形 約86mm")
    legend(svg, MARGIN, h - 9)
    return svg.render()


def left_options():
    """左手にもう1キー追加する2案の比較 (内側の帯 = 2キー幅 38.1mm)"""
    STRIP = 2 * U
    WALL = 4.0
    lw = 5*U + STRIP
    title_h = 30
    gap = 30.0
    w = MARGIN*2 + 2*(lw + 2*WALL) + gap
    h = title_h + 4*U + 2*WALL + 40
    svg = Svg(mm(w), mm(h))
    svg.text(MARGIN, 10, "左手にもう1キー：2つの候補（内側の帯を2キー幅＝38.1mmに）", 30, weight="bold")
    svg.text(MARGIN, 17, "どちらも格子に一直線。右手のボール帯も同じ幅にして、左右のケースは同じ大きさ（約133 × 76mm）", 20, color=C["sub"])
    LROW4 = ["Shift", "Tab", "Ctrl", "Lower", "Space"]

    def base(lx, oy, label):
        svg.add(f'<rect x="{mm(lx-WALL):.1f}" y="{mm(oy-WALL):.1f}" width="{mm(lw+2*WALL):.1f}" '
                f'height="{mm(4*U+2*WALL):.1f}" rx="{mm(6):.1f}" fill="#ffffff" stroke="#9aa3ad" stroke-width="2"/>')
        for r in range(3):
            for c in range(5):
                svg.key(lx + c*U, oy + r*U, LEFT_ALPHA[r][c], C["alpha"])
        for c in range(5):
            svg.key(lx + c*U, oy + 3*U, LROW4[c], C["mod"])
        svg.key(lx + 5*U, oy + 3*U, "英数", C["mod"])
        svg.thumb(lx + 4*U, oy + 3*U)
        ex, ey = lx + 5.5*U, oy + 2.5*U
        svg.add(f'<circle cx="{mm(ex):.1f}" cy="{mm(ey):.1f}" r="{mm(7.5):.1f}" fill="#5d6d7e" stroke="{C["stroke"]}" stroke-width="2"/>')
        svg.add(f'<circle cx="{mm(ex):.1f}" cy="{mm(ey):.1f}" r="{mm(5.5):.1f}" fill="#85929e"/>')
        svg.text(lx + lw/2, oy + 4*U + WALL + 8, label, 24, "middle", weight="bold")

    # 案1: 4段目をさらに内側へ (親指キー)
    lx1 = MARGIN + WALL
    oy = title_h + WALL
    base(lx1, oy, "案1：親指の段をもう1つ内側へ")
    svg.key(lx1 + 6*U, oy + 3*U, "追加", C["extra"])
    svg.add(f'<rect x="{mm(lx1+5*U+1):.1f}" y="{mm(oy+1):.1f}" width="{mm(STRIP-2):.1f}" height="{mm(2*U-2):.1f}" rx="8" '
            f'fill="none" stroke="{C["empty"]}" stroke-width="2" stroke-dasharray="6 5"/>')
    svg.text(lx1 + 5*U + STRIP/2, oy + U - 1, "マイコン", 17, "middle", C["sub"])
    svg.text(lx1 + 5*U + STRIP/2, oy + U + 4, "電源SW", 17, "middle", C["sub"])

    # 案2: 人差し指の内側 (G の右) に追加。マイコンは帯の外寄りへ
    lx2 = lx1 + lw + 2*WALL + gap
    base(lx2, oy, "案2：人差し指の内側（G の右）")
    svg.key(lx2 + 5*U, oy + 1*U, "追加", C["extra"])
    svg.add(f'<rect x="{mm(lx2+6*U+1):.1f}" y="{mm(oy+1):.1f}" width="{mm(U-2):.1f}" height="{mm(2*U-2):.1f}" rx="8" '
            f'fill="none" stroke="{C["empty"]}" stroke-width="2" stroke-dasharray="6 5"/>')
    svg.text(lx2 + 6.5*U, oy + U - 1, "マイコン", 15, "middle", C["sub"])
    svg.text(lx2 + 6.5*U, oy + U + 4, "電源SW", 15, "middle", C["sub"])
    return svg.render()


if __name__ == "__main__":
    out = sys.argv[1]
    open(f"{out}/plan1.svg", "w").write(plan1())
    open(f"{out}/plan2.svg", "w").write(plan2())
    open(f"{out}/final.svg", "w").write(plan_final())
    open(f"{out}/left-options.svg", "w").write(left_options())
