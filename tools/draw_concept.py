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
             "ball_cup": "#e6dcc6", "ball_cover": "#c9c1ae", "ball": "#b8432f", "knob": "#2b2d31"})


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
        (rin + 1.5, cz + 1.5, f"爪の厚さ {cu.CLAW_T}mm（壁 6 周で中まで詰まる）", (22, 27.5)),
        (rin + cu.CLAW_T + 0.6, cu.RING_TOP + 0.6, f"控え壁（45°・サポート不要）根元 約{cu.CLAW_T + cu.BUTTRESS:.1f}mm", (22, 24)),
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


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/concept")
