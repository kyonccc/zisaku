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
    lo = z0 + bu.cover_z(25, bu.UNIT_R, th)
    hi = z0 + bu.cover_z(25, bu.UNIT_R, th + 180)
    g = bu.cover_geometry(25)
    top = z0 + g["cz"] + 12.5
    key_top = cu.PLATE_T + 7.5
    labels = [
        (-6, top - 2, f"ボール 25mm（てっぺん 約{top:.0f}mm）", (52, 40)),
        (-16.5, hi - 0.8, f"カバー奥側 約{hi:.0f}mm（縁のかぶり 0.5mm・傾き {bu.COVER_TILT:.0f}°）", (52, 36.5)),
        (16, lo - 0.6, f"カバー親指側 約{lo:.0f}mm", (52, 33)),
        (28, key_top - 0.5, f"キーキャップの上 約{key_top:.0f}mm", (52, 29.5)),
        (31, cu.PLATE_B + 0.6, "薄いプレート＋基板（いっしょに浮く）", (52, 26)),
        (40, cu.PCB_B - 3, "基板の下は空き（電池・XIAO が入る）。柱とポロンは別の断面", (52, 22.5)),
        (40, 1, "トレイの床", (52, 19)),
        (-12, 3, "ボールユニット：床に落とし込んで低く", (52, 15.5)),
    ]
    W, H, body = ds.section(items, "az", (bx, by, th), ((-24, 50), (-1, 44)),
                            "浮島：親指の来る向きの断面（右手・25mm ボール）", labels, px=12)
    open(os.path.join(out, "ukishima-section.svg"), "w").write(ds.svg(W, H, body))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/concept")
