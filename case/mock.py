"""浮島の「大きさと高さ」を確かめるための模型 (モック) の STL を作る。部品を買う前に印刷して、手を置いてみる用。

使い方 (リポジトリの一番上で):
    npx ergogen@4.1.0 pcb/ergogen -o pcb/ergogen/output   # 先に外形を作る
    python3 case/mock.py            # case/parts_dims.json の寸法で → case/stl/mock/
    python3 case/mock.py --worst    # 候補で一番大きい部品の寸法 (case/parts_dims_worst.json) で → case/stl/mock_worst/
    python3 case/mock.py --tilt     # ボールの角度のお試し (25mm・0° / 15° / 30°・左手前へ傾ける) → case/stl/mock_tilt/

できるもの (case/stl/mock/):
    mock_tray_left.stl / mock_tray_right.stl … トレイ (本物と同じ形。柱だけポロンの分まで高くして、上の模型を乗せる)
    mock_top_left.stl  / mock_top_right.stl  … 基板＋プレート＋スイッチ＋キーキャップ＋nice!view (カバー込み)
                                               ＋エンコーダー (左) を 1 つにした模型。柱の上に乗せるだけ
    mock_ball_19.stl / mock_ball_25.stl / mock_ball_34.stl … ボールユニット (下ケース＋上ケース＋ボール) の外形。
                                               19 / 25mm は左手前へ傾いた形 (底は平ら)。トレイの穴に入れる

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

BED = 180.0                       # A1 mini の造形台 (180 × 180 × 180mm)
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
    """ボールユニットの外形 (下ケース＋上ケース＋ボール)。トレイの上の本当の位置 (傾いた形) のまま"""
    R = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R
    T = cu.size_tilt(size)
    lower, _ = cu.lower_case(34 if size == 34 else 25)
    cover, _ = cu.claw_cover(size)
    if size == 34:
        top = cu.U34_TOP
        a0, a1 = cu.HOOD34_A
        body = k.cyl(0, 0, 0, top + 0.01, cu.U34_R) + bu.sector(cu.U34_R - 1, cu.HOOD34_IN + 0.5, a0, a1, cu.HOOD34_Z0, cu.HOOD34_Z0 + 0.6)
    else:
        top = cu.RING_TOP
        body = k.cyl(0, 0, 0, top - 0.8, bu.UNIT_R) + k.cyl(0, 0, 0, top, bu.UNIT_R - 1.0)
    ball = mf.Manifold.sphere(R, 128).translate([0, 0, cz]).trim_by_plane([0, 0, 1], top - 0.3)
    m = lower + cu.unit_place(body + cover + ball, T)
    return m.trim_by_plane([0, 0, 1], 0.0)


TILTS = (0, 15, 30)


def mock_ball_tilt(size, tilt):
    """角度のお試し: ユニットの外形 (土台＋カップ＋爪留めカバー＋ボール) を左手前へ傾け、下にくさびの台を足す。
    爪は斜め 3 か所 (cu.TRIAL_CLAWS)。トレイの穴 (半径 18) にそのまま差し替えられる"""
    R = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R
    cover, _ = cu.claw_cover(size, cu.TRIAL_CLAWS)
    ball = mf.Manifold.sphere(R, 128).translate([0, 0, cz]).trim_by_plane([0, 0, 1], cu.RING_TOP - 0.01)
    unit = k.cyl(0, 0, 0, cu.RING_TOP - 0.8, bu.UNIT_R) + cover + ball
    m = cu.ball_place(unit, tilt)
    if tilt:
        bx, by = k.HALVES["right"]["ball"]
        below = cu.ball_place(k.cyl(0, 0, -60, 0.01, 40), tilt)       # 傾けた底より下
        m = m + (k.cyl(bx, by, 0, 40, cu.U34_R - 0.1) ^ below)       # くさびの台 (トレイの穴に入る太さ)
    return m


def main_tilt():
    out = os.path.join(HERE, "stl", "mock_tilt")
    os.makedirs(out, exist_ok=True)
    top, tray = mock_top("right"), mock_tray("right")
    for t in TILTS:
        m = mock_ball_tilt(25, t)
        b = m.bounding_box()
        hit = [n for n, o in (("上の模型", top), ("トレイ", tray)) if (m ^ o).volume() > 0.05]
        k.save_stl(m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]]),
                   os.path.join(out, f"mock_ball_25_tilt{t:02d}.stl"))
        R = bu.CUPS[25]["R"]
        top_z = cu.ball_place(k.cyl(0, 0, bu.BALL_BOTTOM + R, bu.BALL_BOTTOM + R + 0.01, 0.01), t).bounding_box()[5] + R
        print(f"  mock_ball_25_tilt{t:02d}.stl  ({b[3]-b[0]:.0f} × {b[4]-b[1]:.0f} × {b[5]-b[2]:.0f}mm)  "
              f"ボールの上 {top_z:.1f}mm  {'× ' + '・'.join(hit) + ' に当たる' if hit else '当たりなし'}")


def main():
    if "--tilt" in sys.argv:
        return main_tilt()
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
        b = m.bounding_box()
        size = (b[3] - b[0], b[4] - b[1], b[5] - b[2])
        if max(size) > BED:
            sys.exit(f"{name}: {BED}mm の造形台に入らない ({size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f})")
        bed = m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])     # 造形台の上・真ん中に置く (置く面が下)
        k.save_stl(bed, os.path.join(out, f"{name}.stl"))
        print(f"  {name}.stl  ({size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f}mm・{m.volume() / 1000:.0f} cm³)")
    # 組み合わせた時にぶつからないか (ボールの模型はトレイの穴の位置で確かめる)
    for side in ("left", "right"):
        t, top = items[f"mock_tray_{side}"], items[f"mock_top_{side}"]
        if (t ^ top).volume() > 0.5:
            print(f"  × {side}: トレイと上の模型が重なる")
    for size in (19, 25, 34):
        b = items[f"mock_ball_{size}"]
        for name in ("mock_tray_right", "mock_top_right"):
            if (b ^ items[name]).volume() > 0.5:
                print(f"  × {size}mm: ボールの模型が {name} に当たる")
    print(f"高さ: 基板の下 {cu.PCB_B:.2f} / プレート上 {cu.PLATE_T:.2f} / キーキャップ上 {cu.KEY_TOP:.2f} / "
          f"nice!view のカバー上 {cu.VIEW_TOP + cu.VC_SKIN:.2f} / つまみ上 {cu.PCB_T + cu.ENC_SHAFT_L:.2f}")


if __name__ == "__main__":
    main()
