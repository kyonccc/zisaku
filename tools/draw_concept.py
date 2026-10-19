"""構想「浮島」の断面図 (親指の来る向き・ボールの中心を通る) を SVG で描く。

使い方 (リポジトリの一番上で): python3 tools/draw_concept.py docs/concept
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "case"))
import concept_ukishima as cu  # noqa: E402
import draw_case_section as ds  # noqa: E402

bu, k = cu.bu, cu.k
ds.C.update({"tray": "#d8d3c9", "posts": "#bdb7ab", "gasket": "#e98f9c", "pcb": "#202124", "plate": "#45474c",
             "switch": "#9aa0a6", "caps": "#ffffff", "view": "#11181f", "ball_base": "#c7c2b8",
             "ball_cup": "#e6dcc6", "ball_cover": "#c9c1ae", "ball": "#b8432f", "knob": "#2b2d31",
             "screws": "#a9adb3"})


def main(out):
    parts = cu.half("right")
    items = [(name, m) for name, m in parts.items()]
    bx, by = k.HALVES["right"]["ball"]
    th = bu.THUMB_FROM
    z0 = cu.BALL_Z0
    top = z0 + bu.BALL_BOTTOM + 25
    _, claw_top = cu.claw_cover(25)
    labels = [
        (-6, top - 2, f"ボール 25mm（てっぺん 約{top:.1f}mm）", (52, 40)),
        (-12.5, claw_top - 1.5, f"爪（3本）：先は約{claw_top:.0f}mm。0.7mm かぶって抜けない", (52, 36.5)),
        (15, cu.RING_TOP - 0.8, f"リング：上面 約{cu.RING_TOP:.1f}mm（キーキャップとほぼ同じ）", (52, 33)),
        (28, cu.KEY_TOP - 0.5, f"キーキャップの上 約{cu.KEY_TOP:.1f}mm", (52, 29.5)),
        (31, cu.PLATE_B + 0.6, "薄いプレート＋基板（いっしょに浮く）", (52, 26)),
        (40, cu.PCB_B - 2, f"基板の下 {cu.PCB_B - cu.FLOOR:.1f}mm（電池は床のくぼみへ）", (52, 22.5)),
        (40, 0.7, f"トレイの床 {cu.FLOOR}mm", (52, 19)),
        (-12, 2, "ボールユニット：床に落とし込んで低く", (52, 15.5)),
    ]
    W, H, body = ds.section(items, "az", (bx, by, th), ((-24, 50), (-1, 44)),
                            "浮島（低く・爪留め）：親指の来る向きの断面（右手・25mm ボール）", labels, px=12)
    open(os.path.join(out, "ukishima-section.svg"), "w").write(ds.svg(W, H, body))

    # 爪の断面 (奥の爪 160° を、ボールの中心を通って縦に切る。右が爪のある外側)
    unit = [(n, m) for n, m in parts.items() if n.startswith("ball")]
    a = cu.CLAWS[0]
    R_ = 12.5
    cz = z0 + bu.BALL_BOTTOM + R_
    rin = R_ + 0.3
    labels2 = [
        (rin + 1.2, claw_top - 0.6, f"爪の先：かぶり {cu.CLAW_OVER}mm（高さ 約{claw_top:.0f}mm）", (22, 31)),
        (rin + 2.2, cz + 2.2, "外側：リングの外周から曲線でつながる（最大約38°）", (22, 27.5)),
        (rin + 3.0, cu.RING_TOP + 0.4, f"根元の厚さ 約{bu.UNIT_R - rin:.1f}mm・先 {cu.CLAW_TIP_T}mm", (22, 24)),
        (15.5, cu.RING_TOP - 1.5, f"リング：上面 約{cu.RING_TOP:.1f}mm", (22, 20.5)),
        (14.0, bu.CUP_TOP - 1.5, "ひねってロックする差し込み部", (22, 17)),
        (5, cz, "ボール 25mm", (22, 13.5)),
    ]

    def arrow(X, Y):
        return (f'<line x1="{X(-15):.1f}" y1="{Y(14):.1f}" x2="{X(-15):.1f}" y2="{Y(27):.1f}" stroke="#2e86c1" stroke-width="3"/>'
                f'<path d="M{X(-15)-8:.1f},{Y(26):.1f} L{X(-15):.1f},{Y(28):.1f} L{X(-15)+8:.1f},{Y(26):.1f}" fill="none" stroke="#2e86c1" stroke-width="3"/>'
                f'<text x="{X(-14.6):.1f}" y="{Y(21):.1f}" font-size="16" fill="#2e86c1">印刷の向き</text>'
                f'<text x="{X(-14.6):.1f}" y="{Y(19.5):.1f}" font-size="14" fill="#2e86c1">（下から上へ積む）</text>')
    W2, H2, body2 = ds.section(unit, "az", (bx, by, a), ((-17, 20), (10, 34)),
                               "爪の断面（奥の爪・3D プリントで折れにくい形）", labels2, px=22, overlay=arrow)
    open(os.path.join(out, "ukishima-claw.svg"), "w").write(ds.svg(W2, H2, body2))

    mount_view(parts, out)
    top_view(parts, out)


def mount_view(parts, out):
    """基板の留め方 (バーガーマウント) の断面。内側の柱 1 本を左右に切る"""
    x, y = cu.POSTS["right"][6]
    items = [(n, m) for n, m in parts.items() if n in ("tray", "posts", "gasket", "pcb", "plate", "switch", "caps", "screws")]
    labels = [
        (6, cu.PLATE_T - 0.6, "プレート：穴もネジ山もなし（上から見てネジが見えない）", (16, 20)),
        (6, cu.PCB_B + 0.8, "基板：ポロンに乗って浮いている", (16, 17.5)),
        (-1.6, cu.NUT_B + 0.7, f"基板の裏の M2 はんだ付けナット（SMT ナット）", (16, 15)),
        (3.0, cu.POST_TOP + cu.PORON / 2, f"ポロン（3mm → 締めて約 {cu.PORON}mm）", (16, 12.5)),
        (1.8, cu.POST_TOP + 0.35, f"すき間 {cu.NUT_B - cu.POST_TOP:.1f}mm（押した時に沈める量）", (16, 10)),
        (1.2, cu.COLLAR_B + 1.5, "カラー 5mm（ねじの無い筒・締めすぎ防止）", (16, 7.5)),
        (3.3, 3, "トレイの柱（トレイと一体で印刷）", (16, 5)),
        (-2.2, 0.5, "下から M2 ネジ＋ワッシャー（床のくぼみに沈む）", (16, 2.5)),
    ]
    W, H, body = ds.section(items, "az", (x, y, 0), ((-14, 15), (-1, 22)),
                            "基板の留め方：下から留める（上からネジが見えない・ポロンで浮かせる）", labels, px=24)
    open(os.path.join(out, "ukishima-mount.svg"), "w").write(ds.svg(W, H, body))


def top_view(parts, out):
    """右手を上から見た図。爪の位置と、まわりのキー・親指の向き・ネジの位置"""
    x0, y0, x1, y1 = 183, -17, 331, 74
    px = 7
    W, H = int((x1 - x0) * px) + 60, int((y1 - y0) * px) + 150

    def X(x):
        return 30 + (x - x0) * px

    def Y(y):
        return 80 + (y1 - y) * px

    def poly(m, fill, stroke="#333", extra=""):
        d = " ".join("M" + " L".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pl) + " Z"
                     for pl in m.project().to_polygons())
        return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="1" fill-rule="nonzero" {extra}/>'

    bx, by = k.HALVES["right"]["ball"]
    o = ['<text x="30" y="34" font-size="22" font-weight="bold" fill="#333">'
         '上から見た右手：爪は打鍵の指が通らない所に（青い点線＝基板の下で留めるネジ。上からは見えない）</text>']
    o.append(poly(parts["tray"], "#e8e4dc"))
    o.append(poly(parts["pcb"], "#202124"))
    o.append(poly(parts["view"], "#11181f"))
    o.append(poly(parts["caps"], "#f3f0e9", extra='fill-opacity="0.82"'))
    for x, y in cu.POSTS["right"]:
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{cu.POST_R * px:.1f}" fill="none" stroke="#2e86c1" '
                 f'stroke-width="2" stroke-dasharray="5,4"/>')
    o.append(poly(parts["ball_cup"], "#ece7dd"))
    o.append(poly(parts["ball"], "#b8432f"))
    o.append(poly(parts["ball_cover"], "#2b2d31"))
    # 親指の来る向き
    th = math.radians(bu.THUMB_FROM)
    a0 = (bx + 40 * math.cos(th), by + 40 * math.sin(th))
    a1 = (bx + 21 * math.cos(th), by + 21 * math.sin(th))
    o.append(f'<line x1="{X(a0[0]):.1f}" y1="{Y(a0[1]):.1f}" x2="{X(a1[0]):.1f}" y2="{Y(a1[1]):.1f}" '
             f'stroke="#2e86c1" stroke-width="5" marker-end="url(#ah)"/>')
    o.append(f'<text x="{X(a0[0]) + 8:.1f}" y="{Y(a0[1]) + 22:.1f}" font-size="17" fill="#2e86c1">親指（-20°）：爪のない広いすき間 130°</text>')
    # 爪の注記
    notes = [(45, "爪 45°：右のキー 2 つの角のあいだ（キーまで約 6mm＝一番遠い所）", (250, 60)),
             (160, "爪 160°：内側。キーも指もない", (186, 46)),
             (275, "爪 275°：手前。キーも指もない", (186, -12))]
    for a, t, (lx, ly) in notes:
        r = math.radians(a)
        px_, py_ = bx + 15 * math.cos(r), by + 15 * math.sin(r)
        o.append(f'<line x1="{X(px_):.1f}" y1="{Y(py_):.1f}" x2="{X(lx):.1f}" y2="{Y(ly):.1f}" stroke="#666"/>'
                 f'<circle cx="{X(px_):.1f}" cy="{Y(py_):.1f}" r="3" fill="#e67e22"/>'
                 f'<rect x="{X(lx) - 4:.1f}" y="{Y(ly) - 18:.1f}" width="{len(t) * 16 + 8}" height="25" fill="#fff" fill-opacity="0.85"/>'
                 f'<text x="{X(lx):.1f}" y="{Y(ly):.1f}" font-size="16" fill="#333">{t}</text>')
    defs = ('<defs><marker id="ah" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto">'
            '<path d="M0,0 L6,3 L0,6 Z" fill="#2e86c1"/></marker></defs>')
    open(os.path.join(out, "ukishima-top.svg"), "w").write(ds.svg(W, H, defs + "".join(o)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/concept")
