"""浮島の「大きさと高さ」を確かめるための模型 (モック) の STL を作る。部品を買う前に印刷して、手を置いてみる用。

使い方 (リポジトリの一番上で):
    npx ergogen@4.1.0 pcb/ergogen -o pcb/ergogen/output   # 先に外形を作る
    python3 case/mock.py            # case/parts_dims.json の寸法で → case/stl/mock/
    python3 case/mock.py --worst    # 候補で一番大きい部品の寸法 (case/parts_dims_worst.json) で → case/stl/mock_worst/

できるもの (case/stl/mock/):
    mock_tray_left.stl / mock_tray_right.stl … トレイ (本物と同じ形。柱だけポロンの分まで高くして、上の模型を乗せる)
    mock_top_left.stl  / mock_top_right.stl  … 基板＋プレート＋スイッチ＋キーキャップ＋nice!view (カバー込み)
                                               ＋エンコーダー (左) を 1 つにした模型。柱の上に乗せるだけ
    mock_ball_19.stl / mock_ball_25.stl / mock_ball_34.stl … ボールユニットとボールの外形 (トレイの穴に入れる)

高さはすべて case/concept_ukishima.py の数字 (部品の高さ) から作る。部品を実測して数字を直したら、
もう一度このプログラムを実行すれば模型も変わる。寸法はすべて mm。z はトレイの底面 (机) が 0。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# --worst: 候補の中で一番大きい部品の寸法 (case/parts_dims_worst.json) で作る。何も付けなければ case/parts_dims.json
PROFILE = "worst" if "--worst" in sys.argv else "normal"
if PROFILE == "worst":
    os.environ["KATAWARE_DIMS"] = os.path.join(HERE, "parts_dims_worst.json")

import manifold3d as mf  # noqa: E402

sys.path.insert(0, HERE)
import concept_ukishima as cu  # noqa: E402

k, bu = cu.k, cu.bu
U = k.U


def mock_tray(side):
    p = cu.half(side, 34 if side == "right" else 25)
    t = p["tray"] + p["posts"]
    # 柱の上にポロンの分 (締めた厚さ) を足す → 上の模型が本物の基板の高さに乗る
    t = t + k.union([k.cyl(x, y, cu.POST_TOP - 0.01, cu.PCB_B, cu.PORON_OD / 2) for x, y in cu.POSTS[side]])
    return t


def mock_top(side):
    pcb = k.load(f"pcb_{side}")
    m = k.prism(pcb, cu.PCB_B, cu.PLATE_T)                                   # 基板＋すき間＋プレート (ひとかたまり)
    for x, y in cu.KEYS[side]:
        m = m + k.cube(x - 6.9, y - 6.9, cu.PLATE_T - 0.01, x + 6.9, y + 6.9, cu.PLATE_T + 3.01)   # スイッチ
        lo = k.cube(x - 6.9, y - 6.9, cu.PLATE_T + 3.0, x + 6.9, y + 6.9, cu.PLATE_T + 3.01)
        mid = mf.Manifold.cube([17.8, 17.8, 0.01]).translate([x - 8.9, y - 8.9, cu.PLATE_T + 4.0])
        m = m + mf.Manifold.batch_hull([lo, mid]) + cu.keycap(x, y, cu.PLATE_T + 4.0, cu.KEY_TOP)   # キーキャップ
    # nice!view とカバー (外形のかたまり)
    vx, vy = cu.VIEW[side]
    iw, il = cu.VIEW_W / 2 + cu.VC_GAP + cu.VC_WALL, cu.VIEW_L / 2 + cu.VC_GAP + cu.VC_WALL
    view = k.cube(vx - iw, vy - il, cu.PLATE_T - 0.01, vx + iw, vy + il, cu.VIEW_TOP + cu.VC_SKIN)
    if k.HALVES[side]["ball"]:
        bx, by = k.HALVES[side]["ball"]
        view = view - k.cyl(bx, by, -1, 40, cu.U34_R + 0.6)
    m = m + view
    if side == "left":                                                      # エンコーダー (本体＋つまみ)
        ex, ey = cu.ENC
        m = m + k.cube(ex - 6.0, ey - 6.0, cu.PLATE_T - 0.01, ex + 6.0, ey + 6.0, cu.PCB_T + cu.ENC_BODY_H)
        m = m + k.cyl(ex, ey, cu.PCB_T + cu.ENC_BODY_H - 0.01, cu.PCB_T + cu.ENC_SHAFT_L, cu.ENC_KNOB_D / 2)
    return m


def mock_ball(size):
    R = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R
    if size == 34:
        body = k.cyl(0, 0, 0, cu.U34_TOP, cu.U34_R)
        start = cu.U34_TOP
    else:
        body = k.cyl(0, 0, 0, cu.RING_TOP, bu.UNIT_R)
        start = cu.RING_TOP
    ball = mf.Manifold.sphere(R, 128).translate([0, 0, cz]).trim_by_plane([0, 0, 1], start - 0.01)
    return body + ball


def main():
    out = os.path.join(HERE, "stl", "mock" if PROFILE == "normal" else "mock_worst")
    print(f"寸法: {cu.DIMS_FILE}")
    os.makedirs(out, exist_ok=True)
    bx, by = k.HALVES["right"]["ball"]
    items = {"mock_tray_left": mock_tray("left"), "mock_tray_right": mock_tray("right"),
             "mock_top_left": mock_top("left"), "mock_top_right": mock_top("right")}
    for size in (19, 25, 34):
        items[f"mock_ball_{size}"] = mock_ball(size)
    for name, m in items.items():
        n = len(m.decompose())
        if n != 1:
            sys.exit(f"{name}: 1 つにつながっていない ({n} 個)")
        if name.startswith("mock_ball"):
            m = m.translate([0, 0, 0])
        k.save_stl(m, os.path.join(out, f"{name}.stl"))
        print(f"  {name}.stl  ({m.volume() / 1000:.0f} cm³)")
    # 組み合わせた時にぶつからないか (ボールの模型はトレイの穴の位置で確かめる)
    for side in ("left", "right"):
        t, top = items[f"mock_tray_{side}"], items[f"mock_top_{side}"]
        if (t ^ top).volume() > 0.5:
            print(f"  × {side}: トレイと上の模型が重なる")
    for size in (19, 25, 34):
        b = items[f"mock_ball_{size}"].translate([bx, by, 0])
        for name in ("mock_tray_right", "mock_top_right"):
            if (b ^ items[name]).volume() > 0.5:
                print(f"  × {size}mm: ボールの模型が {name} に当たる")
    print(f"高さ: 基板の下 {cu.PCB_B:.2f} / プレート上 {cu.PLATE_T:.2f} / キーキャップ上 {cu.KEY_TOP:.2f} / "
          f"nice!view のカバー上 {cu.VIEW_TOP + cu.VC_SKIN:.2f} / つまみ上 {cu.PCB_T + cu.ENC_SHAFT_L:.2f}")


if __name__ == "__main__":
    main()
