"""kataware ボールユニット (土台 + 交換カップ) の 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    python3 case/ball_unit.py

できるもの (case/stl/):
    ball_base.stl    … 土台。ケースの底に裏から皿ネジ M2 × 3本でとめる。PMW3610 センサーを中に置く
    ball_cup_25.stl  … 25mm ボール用カップ (ベアリング3個)
    ball_cup_19.stl  … 19mm ボール用カップ (ベアリング3個)

考え方:
  - 土台はケースに付けたまま。ボールの大きさを変える時は、カップを上から抜いて差し替えるだけ
  - どちらのカップも「ボールの一番下の高さ」が同じなので、センサーとのすき間 (2.4mm) は変わらない
  - カップは土台に差し込むだけ (重さとすき間の小ささで止まる)。回らないよう、奥に「キー」がある
  - センサー基板は土台の底のくぼみに置き、カップの足で上から押さえる (ネジなし)

座標: ユニットの中心が (0, 0)、土台の底面が z = 0。y が奥 (6ピン端子の方向)。
ケースの中では z = 0 がケースの底板の上面 (机から 2.5mm) になる。
"""
import math
import os

import manifold3d as mf

import kataware_case as k

HERE = os.path.dirname(os.path.abspath(__file__))

# ===== 土台 =====
UNIT_R = 17.0            # 外径 34mm (基板・プレートの穴は 36mm)
BASE_WALL = 1.5
BASE_IN_R = UNIT_R - BASE_WALL
BASE_FLOOR = 1.5         # 底の厚さ
BASE_H = 13.5            # 土台の高さ (ケースの中では机から 16.0mm。上ケースの上面 16.5mm より少し下)
BOSS_R = 2.4             # 底ネジのインサート (M2・外径3.2mm) を入れる柱
INSERT_R, INSERT_DEPTH = 1.6, 4.0

# ===== センサー (PMW3610 の基板。寸法は実物合わせ) =====
SENSOR_W, SENSOR_L = 16.0, 20.0   # 幅 (左右) × 長さ (前後)。コネクタは奥側
SENSOR_POCKET = 0.5               # 土台の底のくぼみの深さ
SENSOR_T = 1.6
LENS_H = 3.0                      # 基板の上面からレンズの上面まで
LENS_GAP = 2.4                    # レンズの上面からボールまで (センサーが読む距離)
SENSOR_TOP = BASE_FLOOR - SENSOR_POCKET + SENSOR_T
BALL_BOTTOM = SENSOR_TOP + LENS_H + LENS_GAP      # どちらのボールも、一番下はこの高さ

# ===== カップ =====
CUP_R = BASE_IN_R - 0.3           # 土台にすっと入る (すき間 0.3mm)
CUP_BOTTOM = 6.0                  # カップの底 (レンズの上面より上)
CLEAR = 0.8                       # ボールのまわりのすき間
TOP_ABOVE_CENTER = 3.0            # カップの上の縁 = ボールの中心より 3mm 上 (ボールを上から取り出せる)
LENS_HOLE_R = 5.0

# ===== ベアリング: MR63ZZ (内径3 × 外径6 × 幅2.5mm) + ダウエルピン 直径3 × 8mm =====
BRG_R, BRG_W = 3.0, 2.5
PIN_R, PIN_L = 1.5, 8.0
BRG_ANGLES = (90, 210, 330)       # 上から見た向き (センサーのケーブルとは関係なし)

CUPS = {
    25: {"R": 12.5, "contact": 45},   # 接点の角度 (水平から下向き)
    19: {"R": 9.5, "contact": 40},
}


def rot_z(m, deg):
    return m.rotate([0, 0, deg])


def along_x_cyl(r, length):
    """x 方向の円柱 (中心が原点)"""
    return mf.Manifold.cylinder(length, r, r, 48, True).rotate([0, 90, 0])


def base():
    m = k.cyl(0, 0, 0, BASE_H, UNIT_R)
    m = m - k.cyl(0, 0, BASE_FLOOR, BASE_H + 1, BASE_IN_R)
    bosses, cut = [], []
    for a in k.BALL_SCREW_ANGLES:
        x, y = k.BALL_SCREW_R*math.cos(math.radians(a)), k.BALL_SCREW_R*math.sin(math.radians(a))
        bosses.append(k.cyl(x, y, 0, INSERT_DEPTH + 0.6, BOSS_R))
        cut.append(k.cyl(x, y, -1, INSERT_DEPTH, INSERT_R))          # 下からインサートを入れる穴
    m = (m + k.union(bosses)) - k.union(cut)
    cut = [
        # センサー基板のくぼみ (+0.2mm の余裕)
        k.cube(-SENSOR_W/2 - 0.2, -SENSOR_L/2 - 0.2, BASE_FLOOR - SENSOR_POCKET,
               SENSOR_W/2 + 0.2, SENSOR_L/2 + 0.2, BASE_FLOOR + 1),
        # ケーブルの出口 (奥)
        k.cube(-4.5, BASE_IN_R - 1, BASE_FLOOR - SENSOR_POCKET, 4.5, UNIT_R + 1, 5.5),
        # カップの向きを決める切り欠き (奥)
        k.cube(-1.6, BASE_IN_R - 1, BASE_H - 1.5, 1.6, UNIT_R + 1, BASE_H + 1),
    ]
    return m - k.union(cut)


def cup(size):
    c = CUPS[size]
    R = c["R"]
    cz = BALL_BOTTOM + R                       # ボールの中心
    top = cz + TOP_ABOVE_CENTER
    body = k.cyl(0, 0, CUP_BOTTOM, BASE_H, CUP_R) + k.cyl(0, 0, BASE_H, top, UNIT_R)
    # 上の外側の角を 1mm 面取り
    body = body - (k.cyl(0, 0, top - 1, top + 0.01, UNIT_R + 1) - k.cyl(0, 0, top - 1, top + 0.01, UNIT_R, UNIT_R - 1))
    # 向きを決めるキー (土台の切り欠きに入る)
    body = body + k.cube(-1.3, CUP_R - 0.5, BASE_H - 1.4, 1.3, UNIT_R - 0.2, BASE_H)
    # センサーを押さえる足 (4本・基板の角の近く)
    legs = [k.cyl(x, y, SENSOR_TOP, CUP_BOTTOM + 0.5, 1.2) for x, y in
            ((-6, -8), (6, -8), (-6, 5), (6, 5))]
    body = body + k.union(legs)

    cut = [
        mf.Manifold.sphere(R + CLEAR, 96).translate([0, 0, cz]),       # ボールの受け
        k.cyl(0, 0, cz, top + 1, R + CLEAR),                           # 上から取り出せる
        k.cyl(0, 0, CUP_BOTTOM - 1, cz, LENS_HOLE_R),                  # センサーの窓
    ]
    t = math.radians(c["contact"])
    d = R + BRG_R                                                      # ボール中心〜ベアリング中心
    for a in BRG_ANGLES:
        # x = ベアリングの軸 (接線方向)、y = 外向き、z = 上 の向きで作ってから回す
        pocket = (along_x_cyl(BRG_R + 0.4, BRG_W + 0.6) +
                  k.cube(-(BRG_W + 0.6)/2, -(BRG_R + 0.4), 0, (BRG_W + 0.6)/2, BRG_R + 0.4, 20))
        cradle = (along_x_cyl(PIN_R + 0.05, PIN_L + 0.4) +
                  k.cube(-(PIN_L + 0.4)/2, -(PIN_R - 0.05), 0, (PIN_L + 0.4)/2, PIN_R - 0.05, 20))   # 上からパチンとはめる
        place = lambda m: rot_z(m, a - 90).translate(
            [d*math.cos(t)*math.cos(math.radians(a)), d*math.cos(t)*math.sin(math.radians(a)), cz - d*math.sin(t)])
        cut += [place(pocket), place(cradle)]
    m = body - k.union(cut)
    info = {"cz": cz, "top": top,
            "brg_z": cz - d*math.sin(t), "brg_r": d*math.cos(t)}
    return m, info


def bearings(size):
    """描画用: ベアリング3個とピン"""
    c = CUPS[size]
    R, t = c["R"], math.radians(c["contact"])
    d, cz = R + BRG_R, BALL_BOTTOM + R
    parts = []
    for a in BRG_ANGLES:
        m = along_x_cyl(BRG_R, BRG_W) + along_x_cyl(PIN_R, PIN_L)
        parts.append(rot_z(m, a - 90).translate(
            [d*math.cos(t)*math.cos(math.radians(a)), d*math.cos(t)*math.sin(math.radians(a)), cz - d*math.sin(t)]))
    return k.union(parts)


def main():
    out = os.path.join(HERE, "stl")
    os.makedirs(out, exist_ok=True)
    b = base()
    k.save_stl(b, os.path.join(out, "ball_base.stl"))
    print(f"土台: 外径 {2*UNIT_R:.0f}mm / 高さ {BASE_H}mm / センサー基板の上面 {SENSOR_TOP:.1f}mm / "
          f"ボールの一番下 {BALL_BOTTOM:.1f}mm  ({b.volume()/1000:.1f} cm³)")
    for size in CUPS:
        m, info = cup(size)
        k.save_stl(m, os.path.join(out, f"ball_cup_{size}.stl"))
        print(f"{size}mm カップ: ボール中心 {info['cz']:.1f}mm / 上の縁 {info['top']:.1f}mm / "
              f"ベアリング中心 高さ {info['brg_z']:.1f}mm・半径 {info['brg_r']:.1f}mm  ({m.volume()/1000:.1f} cm³)")
        assert info["brg_z"] - BRG_R - 0.4 > CUP_BOTTOM, "ベアリングがカップの底から出る"
        assert info["brg_r"] + BRG_R + 0.4 < CUP_R, "ベアリングがカップの外に出る"
    print(f"ケースの中では +{k.FLOOR}mm（机から）: 25mm ボールのてっぺん "
          f"{k.FLOOR + BALL_BOTTOM + 25:.1f}mm、19mm は {k.FLOOR + BALL_BOTTOM + 19:.1f}mm")


if __name__ == "__main__":
    main()
