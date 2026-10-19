"""kataware ボールユニット (土台 + 交換カップ) の 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    python3 case/ball_unit.py

できるもの (case/stl/):
    ball_base.stl    … 土台。ケースの底に裏から皿ネジ M2 × 3本でとめる。PMW3610 センサーを中に置く
    ball_cup_25.stl  … 25mm ボール用カップ (ベアリング3個)
    ball_cup_19.stl  … 19mm ボール用カップ (ベアリング3個)
    ball_cover_25.stl / ball_cover_19.stl … ボールを押さえるカバー (親指用に斜め。ひねってカップにロック)

考え方:
  - 土台はケースに付けたまま。ボールの大きさを変える時は、カップを上から抜いて差し替えるだけ
  - どちらのカップも「ボールの一番下の高さ」が同じなので、センサーとのすき間 (2.4mm) は変わらない
  - カップは土台に差し込むだけ (重さとすき間の小ささで止まる)。回らないよう、奥に「キー」がある
  - センサー基板は土台の底のくぼみに置き、カップの足で上から押さえる (ネジなし)
  - ベアリングの軸は M1.4 ネジ。締め具合でボールの回り方 (軽さ・ガタ) を調整できる
  - カバーはボールの赤道より上をぐるりと押さえるので、ふだんはボールが抜けない。
    カバーはバヨネット式 (ひねってロック)。カバーの3つのツメをカップの溝に入れ、時計回りに 30° 回すと
    カチッと止まる。指が当たっても外れない。掃除の時は反時計回りに 30° 回して持ち上げれば、ボールだけ取り出せる
  - カバーの上面は、親指が来る方 (Enter の方・少し手前) に向かって 25° 下がる。
    親指側の縁はキーキャップの上とほぼ同じ高さ、奥側はボールのてっぺん近くまで上がる (背もたれ・飛び出し防止)

座標: ユニットの中心が (0, 0)、土台の底面が z = 0。x が右 (Enter の方)、y が奥。
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
CABLE_ANGLE = 0.0        # センサーのケーブルの出口の向き (0° = 右 = 基板のコネクタ J のある Enter の方)

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

# ===== ベアリング: 681X (内径1.5 × 外径4 × 幅2mm) + 軸は M1.4 × 6mm のタッピングネジ =====
# FrostOrtho と同じ大きさのベアリング。小さいのでボールを深く包めて、溝も小さくて済む
# ネジはカップの外側の穴から入れ、ベアリングを通して反対側の下穴にねじ込む。
# ベアリングの横のすき間は小さめ (BRG_SIDE) なので、ネジを締めると壁がベアリングを軽く挟み、
#   ゆるめる → 軽く回るがガタが出る / 締める → ガタが減り、回り方が重くなる
# の間で調整できる
BRG_R, BRG_W = 2.0, 2.0
BRG_SIDE = 0.15                   # ベアリングの左右のすき間 (片側)
SCREW_L = 6.0                     # M1.4 × 6mm
SCREW_PASS_R = 0.8                # ネジが通る穴 (直径1.6)
SCREW_PILOT_R = 0.55              # 反対側の下穴 (直径1.1。ここにねじ込む)
SCREW_HEAD_R = 1.45               # ネジ頭の通る穴 (直径2.9。なべ頭 直径2.5 用)
NEAR_WALL = 1.2                   # ネジ頭が当たる壁の厚さ
BRG_ANGLES = (0, 120, 240)        # 上から見た向き。0° (右・外側) に 1 個 → テンティング (内側を持ち上げる) で
#                                   ボールが外側へ寄っても、そのベアリングが受ける (計算上 約 45° まで傾けても浮かない)

# ===== カバー (親指用) =====
COVER_TILT = 25.0                 # 上面の傾き (度)
THUMB_FROM = -20.0                # 親指が来る向き (上から見て。0° = 右 (Enter の方)、-90° = 手前)
LIP_OVERLAP = 0.8                 # カバーの縁がボールにかぶる幅 (半径で)。これでボールが抜けない
LIP_GAP = 0.3                     # カバーの内側とボールのすき間
LIP_LAND = 0.8                    # 縁の、まっすぐな部分の厚さ
COVER_MIN = 2.5                   # カバーの一番薄い所 (カップの上面から)
# ===== カバーのロック (バヨネット式: 差し込んで時計回りにひねる) =====
LOCK_TURN = 30.0                  # ロックするまでに回す角度 (時計回り)
LUG_ANGLES = (0, 110, 235)        # ツメの位置 (ロックした時)。わざと不等間隔 → 差し込める向きが1つだけ
LUG_W = 12.0                      # ツメの幅 (角度)
RECESS_R = 15.0                   # カップ上面の段 (カバーの差し込み部が入る)
RECESS_Z = 13.0                   # 段の底の高さ
SPIGOT_R = 14.8                   # カバーの差し込み部の外径 (半径)
LUG_R = 15.9                      # ツメの先 (半径)
GROOVE_R = 16.1                   # カップの溝の奥 (半径)。外側に 0.9mm の壁が残る
GROOVE_Z0, GROOVE_Z1 = 13.3, 14.7 # 溝の下面・上面
LUG_Z0, LUG_H = 13.4, 1.1         # ツメの下面・厚さ (上下のすき間 0.1 / 0.2mm)
DETENT_H = 0.3                    # ロック位置の手前の小さな山 (ここを越える時にカチッとする)
GRIP_N, GRIP_R = 36, 0.5          # カバー外側のすべり止めの溝 (本数・半径)

CUPS = {
    25: {"R": 12.5, "contact": 45},   # 接点の角度 (水平から下向き)
    19: {"R": 9.5, "contact": 45},
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
        # ケーブルの出口 (基板のコネクタのある Enter の方)
        rot_z(k.cube(-4.5, BASE_IN_R - 1, BASE_FLOOR - SENSOR_POCKET, 4.5, UNIT_R + 1, 5.5), CABLE_ANGLE - 90),
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
        k.cyl(0, 0, RECESS_Z, top + 1, RECESS_R),                      # カバーの差し込み部が入る段
    ]
    for L in LUG_ANGLES:
        e = L + LOCK_TURN                                              # 差し込む時のツメの位置
        cut += [sector(RECESS_R - 0.1, GROOVE_R, e - LUG_W/2 - 1.5, e + LUG_W/2 + 1.5, GROOVE_Z0, top + 1),   # 入口
                sector(RECESS_R - 0.1, GROOVE_R, L - LUG_W/2 - 1.0, e + LUG_W/2 + 1.5, GROOVE_Z0, GROOVE_Z1)]  # 回す溝
    t = math.radians(c["contact"])
    d = R + BRG_R                                                      # ボール中心〜ベアリング中心
    for a in BRG_ANGLES:
        # x = ベアリングの軸 (接線方向)、y = 外向き、z = 上 の向きで作ってから回す
        w = BRG_W/2 + BRG_SIDE                                          # ポケットの半分の幅
        pocket = (along_x_cyl(BRG_R + 0.4, 2*w) +
                  k.cube(-w, -(BRG_R + 0.4), 0, w, BRG_R + 0.4, 20))   # ベアリングは上から入れる
        reach = math.sqrt(CUP_R**2 - (d*math.cos(t))**2) + 1           # ベアリング中心からカップの外まで
        head0 = w + NEAR_WALL                                           # ネジ頭が当たる面
        screw = (x_cyl(SCREW_PASS_R, 0, head0 + 0.1) +                 # ネジが通る穴
                 x_cyl(SCREW_HEAD_R, head0, reach) +                     # ネジ頭とドライバーの通り道
                 x_cyl(SCREW_PILOT_R, -(head0 - NEAR_WALL + SCREW_L - NEAR_WALL + 0.8), 0))   # 反対側の下穴
        place = lambda m: rot_z(m, a - 90).translate(
            [d*math.cos(t)*math.cos(math.radians(a)), d*math.cos(t)*math.sin(math.radians(a)), cz - d*math.sin(t)])
        cut += [place(pocket), place(screw)]
    m = body - k.union(cut)
    # ロック位置の手前の小さな山 (溝の下面に残す)
    m = m + k.union([sector(RECESS_R + 0.1, GROOVE_R - 0.05, L + LUG_W/2 + 1.5, L + LUG_W/2 + 4.0,
                            GROOVE_Z0 - 0.01, GROOVE_Z0 + DETENT_H) for L in LUG_ANGLES])
    info = {"cz": cz, "top": top,
            "brg_z": cz - d*math.sin(t), "brg_r": d*math.cos(t)}
    return m, info


def x_cyl(r, x0, x1):
    """x 方向の円柱 (x0 〜 x1)"""
    return mf.Manifold.cylinder(x1 - x0, r, r, 32).rotate([0, 90, 0]).translate([x0, 0, 0])


def sector(r0, r1, a0, a1, z0, z1):
    """扇形のリング (半径 r0〜r1・角度 a0〜a1 度・高さ z0〜z1)"""
    n = max(4, int(abs(a1 - a0)/2))
    angs = [math.radians(a0 + (a1 - a0)*i/n) for i in range(n + 1)]
    pts = [[r1*math.cos(t), r1*math.sin(t)] for t in angs] + [[r0*math.cos(t), r0*math.sin(t)] for t in reversed(angs)]
    return mf.CrossSection([pts]).extrude(z1 - z0).translate([0, 0, z0])


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
    # すべり止めの溝 (ひねる時に指がかかる)
    cut += [k.cyl(*polar(UNIT_R + 0.15, 360*i/GRIP_N), CUP_TOP + 0.6, g["cap"] + 1, GRIP_R) for i in range(GRIP_N)]
    m = solid - k.union(cut)
    # 差し込み部 (カップの段に入るリング) と3つのツメ
    spigot = k.cyl(0, 0, RECESS_Z + 0.2, CUP_TOP + 0.01, SPIGOT_R) - k.cyl(0, 0, RECESS_Z, CUP_TOP + 1, g["R"] + 0.5)
    lugs = k.union([sector(SPIGOT_R - 0.3, LUG_R, L - LUG_W/2, L + LUG_W/2, LUG_Z0, LUG_Z0 + LUG_H) for L in LUG_ANGLES])
    m = m + spigot + lugs
    return m, g


def bearings(size):
    """描画用: ベアリング3個と軸のネジ"""
    c = CUPS[size]
    R, t = c["R"], math.radians(c["contact"])
    d, cz = R + BRG_R, BALL_BOTTOM + R
    parts = []
    for a in BRG_ANGLES:
        head0 = BRG_W/2 + BRG_SIDE + NEAR_WALL
        m = (along_x_cyl(BRG_R, BRG_W) + x_cyl(0.7, head0 - SCREW_L, head0) +
             x_cyl(1.25, head0, head0 + 1.0))
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
        print(f"   カバー: 親指側の縁 {lo:.1f}mm (机から {k.FLOOR + lo:.1f}) / 奥側 {hi:.1f}mm (机から {k.FLOOR + hi:.1f}) / "
              f"縁の穴 直径 {2*g['r_open']:.1f}mm  ({cv.volume()/1000:.1f} cm³)")
        # ロックした状態で、カバーとカップがぶつからないか (ツメが溝に収まっているか)
        overlap = (cv ^ m).volume()
        assert overlap < 0.05, f"カバーとカップが重なっている ({overlap:.2f} mm³)"
        # 差し込む向き (反時計回りに LOCK_TURN 回した位置) では、ツメが入口を通れるか
        ins = cv.rotate([0, 0, LOCK_TURN]).translate([0, 0, 0])
        assert (ins ^ m).volume() < 0.05, "差し込む向きでツメが入口を通れない"
    print(f"ケースの中では +{k.FLOOR}mm（机から）: 25mm ボールのてっぺん "
          f"{k.FLOOR + BALL_BOTTOM + 25:.1f}mm、19mm は {k.FLOOR + BALL_BOTTOM + 19:.1f}mm")


if __name__ == "__main__":
    main()
