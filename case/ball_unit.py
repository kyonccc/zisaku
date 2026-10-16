"""kataware ボールユニット (土台 + 交換カップ) の 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    python3 case/ball_unit.py

できるもの (case/stl/):
    ball_base.stl    … 土台。ケースの底に裏から皿ネジ M2 × 3本でとめる。PMW3610 センサーを中に置く
    ball_cup_25.stl  … 25mm ボール用カップ (ベアリング3個)
    ball_cup_19.stl  … 19mm ボール用カップ (ベアリング3個)
    ball_cover_25.stl / ball_cover_19.stl … ボールを押さえるカバー (親指用に斜め。磁石でカップに付く)

考え方:
  - 土台はケースに付けたまま。ボールの大きさを変える時は、カップを上から抜いて差し替えるだけ
  - どちらのカップも「ボールの一番下の高さ」が同じなので、センサーとのすき間 (2.4mm) は変わらない
  - カップは土台に差し込むだけ (重さとすき間の小ささで止まる)。回らないよう、奥に「キー」がある
  - センサー基板は土台の底のくぼみに置き、カップの足で上から押さえる (ネジなし)
  - カバーはボールの赤道より上をぐるりと押さえるので、ふだんはボールが抜けない。
    磁石 (直径3 × 2mm × 3個) で付いているだけなので、掃除の時はカバーをつまんで外せばボールだけ取り出せる
  - カバーの上面は、親指が来る方 (Enter の方・少し手前) に向かって 25° 下がる。
    親指側の縁はキーキャップの上とほぼ同じ高さ、奥側はボールのてっぺん近くまで上がる (背もたれ・飛び出し防止)

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
CUP_TOP = 16.0                    # カップの上面 (机から 18.5mm。上ケースの上面より 2mm 上)。ボールの中心より下
LENS_HOLE_R = 5.0

# ===== ベアリング: MR63ZZ (内径3 × 外径6 × 幅2.5mm) + ダウエルピン 直径3 × 8mm =====
BRG_R, BRG_W = 3.0, 2.5
PIN_R, PIN_L = 1.5, 8.0
BRG_ANGLES = (90, 210, 330)       # 上から見た向き (センサーのケーブルとは関係なし)

# ===== カバー (親指用) =====
COVER_TILT = 25.0                 # 上面の傾き (度)
THUMB_FROM = -20.0                # 親指が来る向き (上から見て。0° = 右 (Enter の方)、-90° = 手前)
LIP_OVERLAP = 0.8                 # カバーの縁がボールにかぶる幅 (半径で)。これでボールが抜けない
LIP_GAP = 0.3                     # カバーの内側とボールのすき間
LIP_LAND = 0.8                    # 縁の、まっすぐな部分の厚さ
COVER_MIN = 2.5                   # カバーの一番薄い所 (カップの上面から)
MAGNET_R, MAGNET_H = 1.55, 2.1    # 磁石 直径3 × 2mm 用の穴
MAGNET_AT = 14.8                  # 磁石の位置 (中心から)
MAGNET_ANGLES = (30, 150, 270)    # ベアリング (90, 210, 330°) の間
PIN_AT, PIN_ANGLE = 14.5, 0       # 向きを決めるピン (カバー側) と穴 (カップ側)

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
    top = CUP_TOP
    body = k.cyl(0, 0, CUP_BOTTOM, BASE_H, CUP_R) + k.cyl(0, 0, BASE_H, top, UNIT_R)
    # 向きを決めるキー (土台の切り欠きに入る)
    body = body + k.cube(-1.3, CUP_R - 0.5, BASE_H - 1.4, 1.3, UNIT_R - 0.2, BASE_H)
    # センサーを押さえる足 (4本・基板の角の近く)
    legs = [k.cyl(x, y, SENSOR_TOP, CUP_BOTTOM + 0.5, 1.2) for x, y in
            ((-6, -8), (6, -8), (-6, 5), (6, 5))]
    body = body + k.union(legs)

    cut = [
        mf.Manifold.sphere(R + CLEAR, 96).translate([0, 0, cz]),       # ボールの受け
        k.cyl(0, 0, CUP_BOTTOM - 1, cz, LENS_HOLE_R),                  # センサーの窓
        k.cyl(*polar(PIN_AT, PIN_ANGLE), top - 2.4, top + 1, 1.3),     # カバーの向きを決めるピンの穴
    ]
    cut += [k.cyl(*polar(MAGNET_AT, a), top - MAGNET_H, top + 1, MAGNET_R) for a in MAGNET_ANGLES]
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


def polar(r, deg):
    return r*math.cos(math.radians(deg)), r*math.sin(math.radians(deg))


def thumb_normal():
    """カバー上面の向き (上向きの単位ベクトル。親指の来る方へ COVER_TILT だけ倒す)"""
    t, f = math.radians(COVER_TILT), math.radians(THUMB_FROM)
    return [math.sin(t)*math.cos(f), math.sin(t)*math.sin(f), math.cos(t)]


def along_n(m):
    """z 方向に作った形を、カバー上面の向き (thumb_normal) に倒す"""
    return m.rotate([0, COVER_TILT, 0]).rotate([0, 0, THUMB_FROM])


def cover_geometry(size):
    R = CUPS[size]["R"]
    cz = BALL_BOTTOM + R
    r_open = R - LIP_OVERLAP                                   # 縁の穴の半径 (ボールより小さい)
    hs = math.sqrt((R + LIP_GAP)**2 - r_open**2)               # 縁の高さ (ボール中心から、上面の向きに)
    h_top = hs + LIP_LAND + 0.6                                # 上面 (縁のまわりは 0.6mm の面取り)
    t = math.radians(COVER_TILT)
    floor = CUP_TOP + COVER_MIN
    far_lip = cz + (hs + LIP_LAND)*math.cos(t) + r_open*math.sin(t)
    cap = max(cz + R - 1.5, far_lip + 1.2)                     # 奥側の一番高い所 (ボールのてっぺんより少し下)
    return dict(R=R, cz=cz, r_open=r_open, hs=hs, h_top=h_top, floor=floor, cap=cap)


def cover_z(size, r, deg):
    """カバー上面の高さ (中心から r、向き deg の所)"""
    g = cover_geometry(size)
    n = thumb_normal()
    x, y = polar(r, deg)
    z_plane = g["cz"] + (g["h_top"] - n[0]*x - n[1]*y)/n[2]
    return min(max(z_plane, g["floor"]), g["cap"])


def cover(size):
    g = cover_geometry(size)
    n = thumb_normal()
    C = [0, 0, g["cz"]]
    nc = n[2]*g["cz"]
    solid = k.cyl(0, 0, CUP_TOP, g["cap"] + 1, UNIT_R)
    # 上面 = 斜めの面。ただし親指側は COVER_MIN より薄くしない・奥側は cap で頭打ち
    solid = (solid.trim_by_plane([-v for v in n], -(nc + g["h_top"])) +
             solid.trim_by_plane([0, 0, -1], -g["floor"])).trim_by_plane([0, 0, -1], -g["cap"])
    # 上面の外の角を 1mm 面取り (斜めの面に沿って)
    big = 40
    chamfer = along_n(mf.Manifold.cylinder(big, UNIT_R - 1 + big, UNIT_R - 1, 96).translate([0, 0, g["h_top"] - big]) +
                      mf.Manifold.cylinder(big, UNIT_R - 1, UNIT_R - 1, 96).translate([0, 0, g["h_top"]])).translate(C)
    solid = solid ^ chamfer
    cut = [
        mf.Manifold.sphere(g["R"] + LIP_GAP, 96).translate(C),                       # ボールの受け
        along_n(mf.Manifold.cylinder(LIP_LAND + 1, g["r_open"], g["r_open"], 96)
                .translate([0, 0, g["hs"] - 1])).translate(C),                      # 縁 (ボールより小さい穴)
        along_n(mf.Manifold.cylinder(20, g["r_open"], g["r_open"] + 20, 96)
                .translate([0, 0, g["hs"] + LIP_LAND])).translate(C),               # 縁の上の面取り (45°)
    ]
    cut += [k.cyl(*polar(MAGNET_AT, a), CUP_TOP - 1, CUP_TOP + MAGNET_H, MAGNET_R) for a in MAGNET_ANGLES]
    m = solid - k.union(cut)
    m = m + k.cyl(*polar(PIN_AT, PIN_ANGLE), CUP_TOP - 2.0, CUP_TOP + 0.01, 1.1)  # 向きを決めるピン
    return m, g


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
        assert CUP_TOP < info["cz"], "カップの上面がボールの中心より上 (カバーを外してもボールが取れない)"
        cv, g = cover(size)
        k.save_stl(cv, os.path.join(out, f"ball_cover_{size}.stl"))
        lo = cover_z(size, UNIT_R, THUMB_FROM)
        hi = cover_z(size, UNIT_R, THUMB_FROM + 180)
        thin = min(cover_z(size, MAGNET_AT, a) for a in MAGNET_ANGLES) - CUP_TOP - MAGNET_H
        print(f"   カバー: 親指側の縁 {lo:.1f}mm (机から {k.FLOOR + lo:.1f}) / 奥側 {hi:.1f}mm (机から {k.FLOOR + hi:.1f}) / "
              f"縁の穴 直径 {2*g['r_open']:.1f}mm / 磁石の上の厚さ {thin:.1f}mm  ({cv.volume()/1000:.1f} cm³)")
        assert thin >= 0.8, "磁石の穴の上が薄すぎる"
    print(f"ケースの中では +{k.FLOOR}mm（机から）: 25mm ボールのてっぺん "
          f"{k.FLOOR + BALL_BOTTOM + 25:.1f}mm、19mm は {k.FLOOR + BALL_BOTTOM + 19:.1f}mm")


if __name__ == "__main__":
    main()
