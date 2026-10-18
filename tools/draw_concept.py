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


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/concept")
