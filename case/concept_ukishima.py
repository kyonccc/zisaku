"""構想「浮島（うきしま）」のイメージ用 3D モデルを作る (製作用ではなく、見た目の確認用)。

使い方 (リポジトリの一番上で):
    python3 case/concept_ukishima.py <出力フォルダ>
    → 部品ごとの STL と manifest.json (色・分解図の高さ) を書き出す

構想:
  - ケースは低いトレイ。壁は基板より低く、横から見ると基板が浮いて見える
  - 基板＋薄いプレートを、トレイから立てた柱のポロン (ガスケット) で上下から挟んで支える
    (外周 6 か所＋内側 2 か所。キーの角どうしのすき間に置く)
  - ボールユニットは机から立つ柱。トレイの床に落とし込んで低くする (25mm ボール)
  - カバーは縁のかぶり 0.5mm・傾き 20° にして低くする
"""
import json
import os
import sys

import manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ball_unit as bu  # noqa: E402
import kataware_case as k  # noqa: E402

U = k.U
# --- カバーを低くする (構想の値) ---
bu.LIP_OVERLAP = 0.5
bu.COVER_TILT = 20.0

# --- 高さ (机から) ---
FLOOR = 2.0          # トレイの床
RIM = 7.5            # トレイの縁の高さ (基板の下面より 1.5mm 低い → 浮いて見える)
PCB_B, PCB_T = 9.0, 10.6
PLATE_B, PLATE_T = 11.6, 12.8
PORON = 1.5
BALL_Z0 = 0.0        # ボールユニットの底 (トレイの床に落とし込む)

KEYS = {
    "left": [(c*U, r*U) for c in range(5) for r in range(4)] + [(5*U, 0), (5*U, 2*U), (5*U, 3*U), (6*U, 0)],
    "right": [(k.RIGHT_X + i*U, r*U) for i in range(1, 6) for r in range(4)] + [(k.RIGHT_X, 2*U), (k.RIGHT_X, 3*U)],
}
# 柱 (キーの角どうしのすき間)。外周 6 か所 + 内側 2 か所
POSTS = {
    "left": [(a*U, b*U) for a, b in ((0.5, 0.5), (2.5, 0.5), (4.5, 0.5), (0.5, 2.5), (2.5, 2.5), (4.5, 2.5),
                                     (1.5, 1.5), (3.5, 1.5))],
    "right": [(k.RIGHT_X + a*U, b*U) for a, b in ((1.5, 0.5), (3.5, 0.5), (4.5, 1.5), (0.5, 2.5), (2.5, 2.5),
                                                 (4.5, 2.5), (2.5, 1.5), (3.5, 1.5))],
}


def keycap(x, y, z0, z1):
    lo = mf.Manifold.cube([17.8, 17.8, 0.01]).translate([x - 8.9, y - 8.9, z0])
    hi = mf.Manifold.cube([15.8, 15.2, 0.01]).translate([x - 7.9, y - 7.3, z1 - 0.01])
    return mf.Manifold.batch_hull([lo, hi])


def half(side):
    outer = k.load(f"board_{side}")
    cavity = k.load(f"cavity_{side}")
    pcb = k.load(f"pcb_{side}")
    plate = k.load(f"plate_{side}").intersection(cavity.buffer(-0.5, join_style=2))
    parts = {}
    # トレイ (低い枠と床)
    tray = k.prism(outer, 0, RIM) - k.prism(outer.buffer(-4.0), FLOOR, RIM + 1)
    if side == "right":
        bx, by = k.HALVES["right"]["ball"]
        tray = tray - k.cyl(bx, by, -1, FLOOR + 1, bu.UNIT_R + 0.3)
    parts["tray"] = tray
    # 柱とガスケット
    posts, pads, tops = [], [], []
    for x, y in POSTS[side]:
        posts.append(k.cyl(x, y, FLOOR - 0.01, PCB_B - PORON, 2.6))
        pads.append(k.cyl(x, y, PCB_B - PORON, PCB_B, 2.6))
        tops.append(k.cyl(x, y, PLATE_T, PLATE_T + 1.0, 2.2))
    parts["posts"] = k.union(posts)
    parts["gasket"] = k.union(pads) + k.union(tops)
    # 基板・プレート
    parts["pcb"] = k.prism(pcb, PCB_B, PCB_T)
    parts["plate"] = k.prism(plate, PLATE_B, PLATE_T)
    # スイッチとキーキャップ
    parts["switch"] = k.union([k.cube(x - 6.9, y - 6.9, PLATE_T, x + 6.9, y + 6.9, PLATE_T + 3) for x, y in KEYS[side]])
    parts["caps"] = k.union([keycap(x, y, PLATE_T + 4, PLATE_T + 7.5) for x, y in KEYS[side]])
    # nice!view
    vx = 6*U if side == "left" else k.RIGHT_X - U
    parts["view"] = k.cube(vx - 7, 2.5*U - 18, PCB_T, vx + 7, 2.5*U + 18, PCB_T + 4.2)
    if side == "left":
        ex, ey = 5.5*U, U
        parts["knob"] = (k.cyl(ex, ey, PCB_T + 1, PLATE_T + 9.0, 7.5) -
                         k.cyl(ex, ey, PLATE_T + 8.2, PLATE_T + 10, 6.2))
    else:
        bx, by = k.HALVES["right"]["ball"]

        def at(m):
            return m.translate([bx, by, BALL_Z0])
        cup, info = bu.cup(25)
        cover, _ = bu.cover(25)
        parts["ball_base"] = at(bu.base())
        parts["ball_cup"] = at(cup)
        parts["ball_cover"] = at(cover)
        parts["ball"] = at(mf.Manifold.sphere(12.5, 128).translate([0, 0, info["cz"]]))
    return parts


COLORS = {  # 色・分解図での持ち上げ量
    "tray": ("#e8e4dc", 0), "posts": ("#d2cdc3", 0), "gasket": ("#e98f9c", 8),
    "pcb": ("#202124", 16), "plate": ("#3a3b3f", 26), "switch": ("#8e949b", 34), "caps": ("#f3f0e9", 46),
    "view": ("#11181f", 26), "knob": ("#2b2d31", 46),
    "ball_base": ("#d9d5cc", 0), "ball_cup": ("#ece7dd", 22), "ball_cover": ("#e8e4dc", 44), "ball": ("#b8432f", 62),
}


def main(out):
    os.makedirs(out, exist_ok=True)
    manifest = []
    for side in ("left", "right"):
        for name, m in half(side).items():
            fn = f"{name}_{side}"
            k.save_stl(m, os.path.join(out, f"{fn}.stl"))
            color, ex = COLORS[name]
            manifest.append(dict(name=fn, color=color, explode=ex, opacity=1))
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"))
    g = bu.cover_geometry(25)
    print("カバー 親指側", round(BALL_Z0 + bu.cover_z(25, bu.UNIT_R, bu.THUMB_FROM), 1),
          "奥側", round(BALL_Z0 + bu.cover_z(25, bu.UNIT_R, bu.THUMB_FROM + 180), 1),
          "ボールのてっぺん", round(BALL_Z0 + g["cz"] + 12.5, 1), "キーキャップ上", PLATE_T + 7.5)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "concept_out")
