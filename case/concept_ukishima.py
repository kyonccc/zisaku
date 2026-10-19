"""構想「浮島（うきしま）」のイメージ用 3D モデルを作る (製作用ではなく、見た目の確認用)。

使い方 (リポジトリの一番上で):
    python3 case/concept_ukishima.py <出力フォルダ> [ボールの大きさ 19 / 25 / 34 (省略時 25)]
    → 部品ごとの STL と manifest.json (色・分解図の高さ) を書き出す

構想:
  - ケースは低いトレイ。壁は基板より低く、横から見ると基板が浮いて見える
  - 基板＋薄いプレートを、トレイから立てた柱のポロン (ガスケット) で上下から挟んで支える
    (外周 6 か所＋内側 2 か所。キーの角どうしのすき間に置く)
  - ボールユニットは机から立つ柱。トレイの床に落とし込んで低くする (25mm ボール)
  - カバーは「爪留め」: キーキャップとほぼ同じ高さの低いリング＋細い爪 3 本でボールを押さえる
    (宝石の爪留めの形。爪のあいだからボールの横まで見え、親指で上からも横からも触れる)
  - 全体を低くする: 床 1.5mm、電池は床のくぼみ (底 0.5mm) に入れ、基板の下のすき間を 7 → 5.85mm に
"""
import json
import math
import os
import sys

import manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ball_unit as bu  # noqa: E402
import kataware_case as k  # noqa: E402

U = k.U
# --- ボールユニットを低くする (構想の値): 土台の底を 1.0mm に (センサー基板の下は 0.5mm) ---
bu.BASE_FLOOR = 1.0
bu.SENSOR_TOP = bu.BASE_FLOOR - bu.SENSOR_POCKET + bu.SENSOR_T
bu.BALL_BOTTOM = bu.SENSOR_TOP + bu.LENS_H + bu.LENS_GAP

# --- 34mm ボール: 専用ユニット (人差し指と中指で転がす向き) ---
# 34mm はボールが重く、指で押す力も大きいので、25 / 19mm と土台を共用しない。
#  - 土台とカップを一体に (受けの壁が 2 重にならない分、壁が厚い)。外径 35.4mm (基板の穴 36mm に収まる)
#  - ベアリングは 25 / 19mm と同じ向き (0°/120°/240°)・同じ 45° で支える → 傾けても約 45° までボールが浮かない
#  - ボールの一番太い所 (赤道) がキーキャップより上にあるので、ボールの下半分を囲むリングは作れない
#    (リングがボールに引っかかって、カバーが外せなくなる)。カバーは「赤道より下ではボールの外側だけ」を通る形にする
#  - 爪 3 本: 45° (キーの角のあいだ) は土台と一体の「固定の爪」。170° と 250° はカバーの爪
#  - カバーは、キーも基板もない左手前の空き (140〜290°) を囲む「フード」。外側でひねってロックする
#  - 指は右手前から来る (ボールの手前に手のひら) ので、そこ (爪のすき間 155° の真ん中) を広くあける
bu.CUPS[34] = {"R": 17.0, "contact": 45}       # テンティングでも浮かないよう 45° (55° だと約 22° で浮く)
U34_R = 17.7                      # 34mm ユニットの外径 (半径)。基板・プレートの穴 (半径 18) とのすき間 0.3mm
U34_TOP = 16.0                    # 一体型の受けの上面
CLAWS_34 = (45, 170, 250)         # 爪の向き (すき間 125° / 80° / 155°)
FIXED_CLAW_34 = 45                # 土台と一体の爪
FIXED34_ROOT_W, FIXED34_MAX_R = 11.0, 20.0     # 固定の爪: キーの角のあいだ (約 6mm) に収まる幅・ふくらみ
CLAW34_ROOT_W, CLAW34_TIP_W, CLAW34_TIP_T = 18.0, 5.0, 2.6
CLAW34_BULGE = 1.2                # 34mm の爪の中ほどを厚くする量
# フード (カバー): 左手前の空きを囲む C 形の壁。ひねってロック (さし込む時は +30° の位置)
HOOD34_A = (140, 290)             # フードの範囲 (ロックした時)
HOOD34_IN, HOOD34_OUT = 19.4, 21.4
HOOD34_Z0_ABOVE_PLATE, HOOD34_TOP_ABOVE_KEYS = 0.25, 0.4   # フードの下はプレートの上面より上・上はキーキャップより上
LOCK34_A = (180, 260)             # ツメの位置 (ロックした時)。基板の切り欠きの中
LOCK34_W = 20.0                   # ツメの幅 (角度)
LEDGE34_R, HOOK34_R = 19.2, 18.0   # 土台の外の出っぱり (ツメがこの下に入る)・フードの内側のツメ

# --- 高さ (机から) ---
# 基板の下の高さは、一番きびしい「電池の上にソケットが来る所」で決める (docs/ukishima-build.md の高さの表):
#   床のくぼみの底 0.5 + 電池 5.0 (ばらつき・ふくらみ +0.3) + すき間 0.1 + 沈む量 0.4 + ソケット 1.85 = 8.15
FLOOR = 1.5          # トレイの床
BATTERY_SKIN = 0.5   # 電池のくぼみの底
BATTERY_T, BATTERY_TOL = 5.0, 0.3   # 電池の厚さ (GA-011 約 5mm) と、ばらつき・ふくらみの見込み
SOCKET_H = 1.85      # ホットスワップソケットの高さ (基板の裏から)
PORON = 1.9          # 基板の下のポロン (3mm のシートを締めて約 1.9mm)
NUT_R, NUT_H = 1.9, 1.5           # SMT ナット (外径 3.8mm・高さ 1.5mm)
TRAVEL = PORON - NUT_H            # 基板が沈める量 0.4mm (ナットの下面と柱の上面のすき間)
PCB_B = BATTERY_SKIN + BATTERY_T + BATTERY_TOL + 0.1 + TRAVEL + SOCKET_H
PCB_T = PCB_B + 1.6
PLATE_B, PLATE_T = PCB_T + 1.0, PCB_T + 2.2
RIM = PCB_B - 1.5    # トレイの縁 (基板の下面より 1.5mm 低い → 浮いて見える)
BALL_Z0 = 0.0        # ボールユニットの底 (トレイの床に落とし込む)
KEY_TOP = PLATE_T + 7.5          # キーキャップの上 (Choc v2 ＋ ロープロファイルのキーキャップの目安)
HOOD34_Z0, HOOD34_TOP = PLATE_T + HOOD34_Z0_ABOVE_PLATE, KEY_TOP + HOOD34_TOP_ABOVE_KEYS
HOOK34_Z0, HOOK34_Z1 = HOOD34_Z0, HOOD34_Z0 + 1.0
LEDGE34_Z0, LEDGE34_Z1 = HOOK34_Z1 + 0.1, HOOK34_Z1 + 1.3

# --- 爪留めカバー ---
RING_TOP = KEY_TOP + 0.3          # リングの上面 (キーキャップとほぼ同じ高さ)
# 爪の向き (上から見て。0° = 右 = Enter の方)。打鍵の指に当たらない所に置く:
#   45°  … 右の 2 つのキー ([ ] 側と N 側) の角と角のあいだ。リングのまわりでキーから一番遠い (約 6mm)
#   160° … 内側 (左手側の外)。キーも指もない
#   275° … 手前。キーも指もない
# 爪どうしのすき間は 115° / 115° / 130°。一番広い 130° の真ん中 (-20°) が親指の来る向き
CLAWS = (160, 45, 275)
CLAW_OVER = 0.7                   # 爪の先がボールにかぶる幅 (半径で)。これを基準にする
# 3D プリント (A1 mini などの 0.4mm ノズル・PLA) で折れにくい形
# 爪の外側の面は、リングの外周 (縦の面) からそのまま立ち上がり、なめらかにボール側へ曲がる
# (根元で外周に接する曲線 = 段差のない「馴染む」形)。上から見ても、根元は裾広がりの曲線でリングに溶け込む
CLAW_TIP_T = 2.2                  # 爪の先の厚さ (ボールの外側へ)。0.4mm ノズルで壁 5〜6 周
CLAW_ROOT_W = 14.0                # 爪の幅 (根元・リングの上面で・mm)
CLAW_TIP_W = 4.0                  # 爪の幅 (先・mm)
CLAW_STEPS = 28                   # 曲面を作る輪切りの数

# --- 基板の留め方 (下から留める・上から見てネジが見えない) ---
# 基板の裏に M2 の「はんだ付けナット (SMT ナット)」を付け、トレイの裏から M2 ネジで留める。
# プレートには穴もネジ山も無い → 上から見えるのはキーとプレートだけ。プレートの素材を替えても加工はいらない
# (1.2mm の FR4 / POM にネジ山を切ると山が少なく、すぐ潰れるので、ナットは基板の側に付ける)
# 下から: ネジの頭＋ワッシャー (床のくぼみ) → カラー (ねじの無い筒・長さで締めすぎを防ぐ) が柱の穴を「触れずに」通る
# → 基板の裏のナット。基板は柱の上のポロンだけに乗っていて、浮いたまま (キーを押すとポロンが縮む)
COLLAR_R = 1.5                    # カラー 外径 3mm (内径 2.1mm)
POST_R = 3.6                      # 柱 (ポロンを受ける面を広く)
PORON_OD, PORON_ID = 7.0, 4.5     # ポロンの輪 (3mm のシートを φ7 と φ4.5 のポンチで抜く)
POST_HOLE_R = 1.7                 # 柱の穴 (カラーとのすき間 0.2mm)
WASHER_R, WASHER_T = 2.5, 0.4     # M2 ワッシャー (外径 5mm)
SCREW_HEAD_R, SCREW_HEAD_H = 2.0, 0.8
POST_TOP = PCB_B - PORON
NUT_B = PCB_B - NUT_H             # ナットの下面 (柱の上面とのすき間 = 押した時に動ける量)
COLLAR_B = NUT_B - 5.0            # カラー 長さ 5mm (市販の長さ)
RECESS_D = COLLAR_B               # 床の裏のくぼみの深さ (ワッシャーの上面 = カラーの下面)

KEYS = {
    "left": [(c*U, r*U) for c in range(5) for r in range(4)] + [(5*U, 0), (5*U, 2*U), (5*U, 3*U), (6*U, 0)],
    "right": [(k.RIGHT_X + i*U, r*U) for i in range(1, 6) for r in range(4)] + [(k.RIGHT_X, 2*U), (k.RIGHT_X, 3*U)],
}
# 柱 (キーの角どうしのすき間)。トレイ裏の MagSafe リングの溝・電池をよけて、
# どのキーからも柱が近くなるように計算で選んだ (キーと一番近い柱の距離は前の並びと同じくらい)
POSTS = {
    "left": [(a*U, b*U) for a, b in ((0.5, 0.5), (1.5, 0.5), (4.5, 0.5), (0.5, 2.5), (1.5, 2.5),
                                     (4.5, 2.5), (3.5, 1.5))] + [(5.5*U, 17.0)],   # 最後: エンコーダーの真下 (足のあいだ)
    "right": [(k.RIGHT_X + a*U, b*U) for a, b in ((1.5, 0.5), (3.5, 0.5), (0.5, 1.5), (0.5, 2.5), (2.5, 2.5),
                                                 (4.5, 2.5), (2.5, 1.5), (4.5, 1.5))],
}

# --- テンティング: トレイの裏に MagSafe のメタルリングを埋める溝 ---
# 市販の「MagSafe 用メタルリング (鉄の薄いリング・シール付き)」を貼る。磁石はスタンド側にあるので、
# キーボード側は鉄のリングだけでよい (重さ・厚さが少ない)。買ったリングの寸法に合わせて数字を変える
MAG_OD, MAG_ID = 56.0, 46.0       # リングの外径・内径
MAG_T = 0.6                       # リングの厚さ (標準 0.4〜0.6mm。一番厚い 0.6mm に合わせる)
MAG_TAPE = 0.1                    # リングの裏のシール (両面テープ) の厚さ
MAG_GAP = 0.3                     # 溝のすき間 (半径で)
MAG_DEPTH = MAG_T + MAG_TAPE      # 溝の深さ 0.7mm: 0.6mm のリングで裏面とぴったり (0.4mm なら 0.2mm 引っ込む)
MAG_BOSS = 0.6                    # 溝の真上の床を内側から厚くする量 (溝の上に残る床 0.8 → 1.4mm)
MAG_CENTER = {"left": (3.0*U, 1.5*U), "right": (k.RIGHT_X + 2.5*U, 2.0*U)}
# 電池 (31 × 21 × 5mm・PSE 品) の位置。リングの溝・柱・XIAO をよけた所 (中心・床のくぼみ)
BATTERY = {"left": (8.5, 26.0), "right": (306.0, 8.0)}   # 目隠しの壁が入るよう、基板の縁から少し離す
BAT_W, BAT_H = 31.0, 21.0

# --- 四隅の磁石＋ゴム足 ---
# 持ち運ぶ時は、左手を左右にひっくり返して右手の裏に重ねると、四隅の磁石でくっつく。
# 机では磁石の上に貼ったゴム足が滑り止めになる (テンティングなしでも使える)。
# 位置は左右のトレイの中心から見て左右対称 → 左右どちらを裏返しても四隅が重なる。
# 極: 上から見て左側の 2 個は N 極を下、右側の 2 個は S 極を下 (左右とも同じ)。裏返すと N と S が向き合う
MAG_DX, MAG_YS = 63.35, (-6.8, 64.0)  # トレイの中心からの横の距離・高さ (y)
MAGNET_D, MAGNET_T = 6.0, 2.0     # ネオジム磁石 φ6 × 2mm
RUBBER_D, RUBBER_T = 8.0, 1.0     # ゴム足 φ8 × 1mm (くぼみ 0.6mm に貼る → 0.4mm 出る)
RUBBER_RECESS = 0.6
MAG_BOSS_R, MAG_BOSS_TOP = 4.0, 3.2   # 磁石の上の床を厚くする台 (磁石の上に 0.5mm 残る)


def magnet_spots(side):
    cx = (k.load(f"board_{side}").bounds[0] + k.load(f"board_{side}").bounds[2]) / 2
    return [(cx + sx * MAG_DX, y) for sx in (-1, 1) for y in MAG_YS]


def magnet_feet(side):
    """(床の内側に足す台, 裏から掘る所, 磁石 (絵用))"""
    boss, cut, mags = [], [], []
    for x, y in magnet_spots(side):
        boss.append(k.cyl(x, y, FLOOR - 0.01, MAG_BOSS_TOP, MAG_BOSS_R))
        cut += [k.cyl(x, y, -1, RUBBER_RECESS, RUBBER_D / 2 + 0.15),
                k.cyl(x, y, RUBBER_RECESS - 0.01, RUBBER_RECESS + MAGNET_T + 0.1, MAGNET_D / 2 + 0.1)]
        mags.append(k.cyl(x, y, RUBBER_RECESS, RUBBER_RECESS + MAGNET_T, MAGNET_D / 2))
    return k.union(boss), k.union(cut), k.union(mags)


# --- 電池のガイド: くぼみ (深さ 1mm) の 4 つの角に L 形の低い壁。電池がずれない ---
BAT_GUIDE_H, BAT_GUIDE_T, BAT_GUIDE_L = 3.0, 1.2, 6.0


# --- 電池の目隠し: 基板の縁とトレイの縁のすき間から電池が見えないよう、電池の近くの基板の縁の内側に低い壁 ---
# 基板の下 (縁から 0.3〜1.1mm 内側) に立てる。高さは基板が沈んでも当たらない所まで。裏の部品 (ソケット等) はよける
SCREEN_IN, SCREEN_OUT = 0.3, 1.1
SCREEN_TOP = PCB_B - TRAVEL - 0.25
SCREEN_REACH = 9.0                # 電池からこの距離までの縁に立てる


SCREEN_LIP = 2.0                  # 上の「ひさし」(内側へ。上から斜めにのぞいても電池が見えない)
SCREEN_LOW_TOP = PCB_B - 1.85 - TRAVEL - 0.25   # ソケットの下は、ソケットに当たらない高さまで


def battery_screen(side):
    from shapely.geometry import box as sbox
    from shapely.ops import unary_union
    pcb = k.load(f"pcb_{side}")
    pcb = pcb.buffer(-1.0, join_style=2).buffer(1.0, join_style=2)     # 細い帯 (ソケット用) をならして、縁をなめらかに
    ex, ey = BATTERY[side]
    bat = sbox(ex - BAT_W/2, ey - BAT_H/2, ex + BAT_W/2, ey + BAT_H/2)
    near = bat.buffer(SCREEN_REACH, join_style=2)
    band = pcb.buffer(-SCREEN_IN, join_style=2).difference(pcb.buffer(-SCREEN_OUT, join_style=2)).intersection(near)
    lip = pcb.buffer(-SCREEN_OUT + 0.01, join_style=2).difference(
        pcb.buffer(-SCREEN_OUT - SCREEN_LIP, join_style=2)).intersection(near)
    sockets, tall = [], []
    try:                                   # 基板の裏の部品 (ソケットは低い壁、XIAO・コネクタ・ナットはよける)
        sys.path.insert(0, os.path.join(HERE, "..", "tools"))
        import check_pcb
        from shapely import affinity
        f = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
        for ref, name, shp in check_pcb.back_bodies(f):
            shp = affinity.scale(shp, 1, -1, origin=(0, 0)).buffer(0.5)
            (sockets if name == "socket" else tall).append(shp)
    except (ImportError, FileNotFoundError):
        pass
    sockets, tall = unary_union(sockets), unary_union(tall)
    band = band.difference(tall).difference(bat.buffer(0.3))
    lip = lip.difference(tall).difference(sockets)                     # 電池の上に張り出してよい (高さが違う)
    hi = band.difference(sockets)
    lo = band.intersection(sockets)
    parts = []
    if not hi.is_empty:
        parts.append(k.prism(hi, FLOOR - 0.01, SCREEN_TOP))
    if not lo.is_empty:
        parts.append(k.prism(lo, FLOOR - 0.01, SCREEN_LOW_TOP))
    if not lip.is_empty:
        parts.append(k.prism(lip, SCREEN_TOP - 0.6, SCREEN_TOP))
    return k.union(parts) if parts else None


def sockets(side):
    """基板の裏のホットスワップソケット (本体＋パッド) の 3D の形。確かめる用・絵用"""
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "tools"))
        import check_pcb
        from shapely import affinity
        f = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
        shapes = [affinity.scale(b[2], 1, -1, origin=(0, 0)) for b in check_pcb.back_bodies(f) if b[1] == "socket"]
    except (ImportError, FileNotFoundError):
        return None
    if not shapes:
        return None
    return k.union([k.prism(sh, PCB_B - SOCKET_H, PCB_B + 0.01) for sh in shapes])


XIAO_H, XIAO_HALF_W, XIAO_HALF_L = 5.0, 8.9, 10.5   # XIAO の厚さ (USB-C 込み)・半分の幅・半分の長さ
# エンコーダー (左手・EC11): 本体の高さ・軸の長さ (基板の上から)・つまみの直径
ENC = (5.5*U, U)
ENC_BODY_H, ENC_SHAFT_L, ENC_KNOB_D = 6.5, 15.0, 15.0
# 基板の裏に出る部品の高さ (基板の裏から下へ・mm)。部品の名前の一部で決める
BACK_HEIGHTS = (("xiao", 5.0), ("jst", 4.25), ("molex", 3.4), ("smt_nut", NUT_H), ("socket", SOCKET_H))
DIODE_H = 1.35                     # ダイオード (SOD-123・表面実装・基板の裏)
PIN_H = 2.0                        # 足の出る部品 (エンコーダー・nice!view のピン) を切った後の長さ


def back_parts(side):
    """基板の裏に出る部品を、高さのある形にする (確かめる用)。{名前: 形}"""
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "tools"))
        import check_pcb
        from shapely import affinity
        from shapely.geometry import MultiPoint
    except ImportError:
        return {}
    f = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
    if not os.path.exists(f):
        return {}
    out = {}
    for ref, name, shp in check_pcb.back_bodies(f):
        h = next((v for key, v in BACK_HEIGHTS if key in name.lower()), None)
        if h is None:
            continue
        shp = affinity.scale(shp, 1, -1, origin=(0, 0))
        out[ref] = k.prism(shp, PCB_B - h, PCB_B + 0.01)
    pads = check_pcb.pad_shapes(f)
    diodes = {}
    for ref, num, cu_, shp, net, kind in pads:
        if ref.startswith("D") and kind == "smd" and "B" in cu_:
            diodes.setdefault(ref, []).append(affinity.scale(shp, 1, -1, origin=(0, 0)))
        elif kind == "thru_hole" and not ref.startswith(("D", "H", "MCU")):     # 足の出る部品 (ダイオードは表面実装を使う)
            out[f"{ref}-{num}"] = k.prism(affinity.scale(shp, 1, -1, origin=(0, 0)), PCB_B - PIN_H, PCB_B + 0.01)
    for ref, shs in diodes.items():
        hull = MultiPoint([pt for sh in shs for pt in sh.exterior.coords]).convex_hull
        out[ref] = k.prism(hull, PCB_B - DIODE_H, PCB_B + 0.01)
    return out


def battery_guides(side):
    ex, ey = BATTERY[side]
    x0, x1, y0, y1 = ex - BAT_W/2, ex + BAT_W/2, ey - BAT_H/2, ey + BAT_H/2
    t, L, z0, z1 = BAT_GUIDE_T, BAT_GUIDE_L, FLOOR - 0.01, FLOOR + BAT_GUIDE_H
    g = []
    for cx, sx_ in ((x0, -1), (x1, 1)):
        for cy, sy_ in ((y0, -1), (y1, 1)):
            xa, xb = sorted((cx, cx + sx_*t))
            ya, yb = sorted((cy - sy_*(L - t), cy + sy_*t))
            g.append(k.cube(xa, ya, z0, xb, yb, z1))
            xa, xb = sorted((cx - sx_*(L - t), cx + sx_*t))
            ya, yb = sorted((cy, cy + sy_*t))
            g.append(k.cube(xa, ya, z0, xb, yb, z1))
    return k.union(g)


# --- 電源スイッチ (横のスライドスイッチ PCM12) のカバーとつまみ ---
# スイッチのレバーは基板の「舌」の端から 1mm 出るだけで、トレイの外側の面より 1mm 奥にある。
# トレイの縁に「カバー」を留め、屋根の上の「つまみ」を前後に滑らせると、つまみの下の「フォーク」がレバーを動かす。
# フォークは上下に余裕があるので、基板が沈んで (ポロン) も引っかからない。
# 持ち運びで勝手に ON にならないよう、つまみは屋根のくぼみに沈めてある (上面が屋根より 0.1mm 低い)。
# 組み立て: 基板をトレイに留めたあと、カバーを横から差し込み (フォークがレバーをはさむ)、裏からネジで留める。
# 座標: スイッチの中心から外へ u、奥へ v (左右で v の向きは同じ)
PWR = {"left": (6*U + 0.5*U + 0.85, 52.5, +1), "right": (k.RIGHT_X - 1.5*U - 0.85, 52.5, -1)}   # config.yaml の pwr_y
SW_LEVER_Z0, SW_LEVER_Z1 = PCB_T + 0.3, PCB_T + 1.2      # レバーの高さ (PCM12 の想定・実物合わせ)
SW_LEVER_TIP = 3.15               # レバーの先 (スイッチの中心から)
SW_POS = 0.75                     # レバーの位置 (中心から ±。動く量 1.5mm)
SWC_V0, SWC_V1 = -4.4, 6.9        # カバーの範囲 (奥行き。手前は XIAO の端と USB-C の切り欠きをよける)
SWC_POCKET_Z = 3.3                # トレイの壁を、ここまで掘ってカバーの台を入れる
SWC_BASE_TOP = PCB_B - TRAVEL - 0.45     # 台の上面 (基板の舌が沈んでも当たらない)
SWC_LEDGE_U, SWC_LEDGE_TOP = 2.35, PCB_T - 0.65   # つまみが乗る段 (舌の端 u 2.15 より外)
SWC_WALL_U0, SWC_WALL_U1 = 3.625, 5.125   # 外の壁 (トレイの外側の面より 1mm 出る)
SWC_ROOF_U0, SWC_ROOF_Z0, SWC_ROOF_Z1 = -1.0, PCB_T + 1.85, PCB_T + 3.85   # 屋根 (スイッチ 1.4mm の上を隠す)
SWC_RECESS_Z = PCB_T + 2.85       # 屋根のくぼみの底 (つまみが入る)
SWC_RECESS_V = 3.65               # くぼみの半分の幅 (つまみ 2.6 + 動く量 0.75 + すき間)
SWC_SLOT = 1.7                    # 屋根のみぞ (つまみの軸が通る・半分の幅)
SWC_SCREWS = ((1.2, -2.6), (1.2, 4.9))    # カバーをトレイの裏から留めるタッピングネジ M2 (u, v)


def _pwr_place(side, m):
    sx, sy, d = PWR[side]
    if d < 0:
        m = m.mirror([1, 0, 0])
    return m.translate([sx, sy, 0])


def _uv_cube(u0, u1, v0, v1, z0, z1):
    return k.cube(u0, v0, z0, u1, v1, z1)


def switch_cover(side):
    m = _uv_cube(0.225, 4.125, SWC_V0, SWC_V1, SWC_POCKET_Z + 0.05, SWC_BASE_TOP)               # 台
    m = m + _uv_cube(SWC_LEDGE_U, SWC_WALL_U0 + 0.01, SWC_V0, SWC_V1, SWC_BASE_TOP - 0.01, SWC_LEDGE_TOP)   # 段
    m = m + _uv_cube(SWC_WALL_U0, SWC_WALL_U1, SWC_V0, SWC_V1, SWC_POCKET_Z + 0.05, SWC_ROOF_Z1)  # 外の壁
    m = m + _uv_cube(SWC_ROOF_U0, SWC_WALL_U1, SWC_V0, SWC_V1, SWC_ROOF_Z0, SWC_ROOF_Z1)          # 屋根
    m = m - _uv_cube(SWC_ROOF_U0 - 1, 3.9, -SWC_RECESS_V, SWC_RECESS_V, SWC_RECESS_Z, SWC_ROOF_Z1 + 1)   # くぼみ
    m = m - _uv_cube(SWC_ROOF_U0 - 1, 3.45, -SWC_SLOT, SWC_SLOT, SWC_ROOF_Z0 - 0.1, SWC_ROOF_Z1 + 1)    # みぞ
    for u, v in SWC_SCREWS:
        m = m - k.cyl(u, v, SWC_POCKET_Z - 1, SWC_BASE_TOP - 0.8, 0.8)          # タッピングの下穴
    return _pwr_place(side, m)


def switch_slider(side):
    """フォーク＋つまみ (1 つの部品)。屋根のみぞに内側から差し込む"""
    z0, z1 = SW_LEVER_Z0 - 0.7 - 0.15, SWC_ROOF_Z0 - 0.1     # フォーク (基板が 0.7mm 沈んでもレバーをつかむ)
    gap = 0.8                                                # レバー 1.3mm + すき間
    m = (_uv_cube(2.4, 3.25, gap, 1.8, z0, z1) + _uv_cube(2.4, 3.25, -1.8, -gap, z0, z1) +
         _uv_cube(3.25, 3.525, -1.8, 1.8, z0, z1))                                       # フォーク
    m = m + _uv_cube(2.7, 3.3, -0.8, 0.8, z1 - 0.01, SWC_RECESS_Z + 0.11)                # 軸
    top = SWC_ROOF_Z1 - 0.1                                  # つまみの上面 (屋根より少し低い)
    cap = _uv_cube(1.6, 3.6, -2.6, 2.6, SWC_RECESS_Z + 0.1, top)                       # つまみ
    for v in (-1.6, 0, 1.6):                                 # すべり止めのみぞ
        cap = cap - _uv_cube(1.0, 4.2, v - 0.25, v + 0.25, top - 0.3, top + 1)
    return _pwr_place(side, m + cap)


def switch_pocket(side):
    """トレイの壁を掘る所 (カバーの台が入る) と、裏からのネジ穴"""
    m = _uv_cube(-0.5, 6.0, SWC_V0 - 0.1, SWC_V1 + 0.1, SWC_POCKET_Z, 30)
    for u, v in SWC_SCREWS:
        m = m + k.cyl(u, v, -1, SWC_POCKET_Z + 0.1, 1.15) + k.cyl(u, v, -0.01, 1.2, 2.2, 1.0)
    return _pwr_place(side, m)


# --- nice!view のカバー: 画面のまわりにかぶせる枠 (窓あき)。nice!view の基板のふちに爪で引っかける ---
VIEW = {"left": (6*U, 2.5*U), "right": (k.RIGHT_X - U, 2.5*U)}
VIEW_W, VIEW_L = 14.0, 36.0       # nice!view の大きさ (横 × 縦)
VIEW_PCB_B = PCB_T + 2.5          # nice!view の基板の下面 (ピンヘッダーの樹脂 2.5mm の上に直接はんだ付け)
VIEW_TOP = VIEW_PCB_B + 2.9       # nice!view の一番上 (基板＋画面 約 2.9mm)
VC_WALL, VC_SKIN, VC_GAP = 1.0, 1.0, 0.2
VC_WIN_W, VC_WIN_L = 11.2, 31.0   # 窓 (画面の見える所・実物合わせ)
VC_LIP = 0.4                      # 爪 (基板のふちの下に入る量)


def view_cover(side):
    vx, vy = VIEW[side]
    iw, il = VIEW_W/2 + VC_GAP, VIEW_L/2 + VC_GAP
    ow, ol = iw + VC_WALL, il + VC_WALL
    z0 = VIEW_PCB_B - 0.65
    top = VIEW_TOP + VC_SKIN
    m = k.cube(-ow, -ol, z0, ow, ol, top) - k.cube(-iw, -il, z0 - 1, iw, il, VIEW_TOP + 0.05)
    # 窓 (上に向かって広がる)
    win = mf.Manifold.batch_hull([k.cube(-VC_WIN_W/2, -VC_WIN_L/2, VIEW_TOP - 0.1, VC_WIN_W/2, VC_WIN_L/2, VIEW_TOP),
                                  k.cube(-VC_WIN_W/2 - 1.2, -VC_WIN_L/2 - 1.2, top, VC_WIN_W/2 + 1.2, VC_WIN_L/2 + 1.2, top + 0.01)])
    m = m - win
    # 爪 (長い辺だけ。端にはピンがあるのでつけない)
    for sgn in (-1, 1):
        x0, x1 = sorted((sgn*iw, sgn*(iw - VC_LIP)))
        m = m + k.cube(x0, -il + 5, z0, x1, il - 5, VIEW_PCB_B - 0.05)
    m = m.translate([vx, vy, 0])
    if k.HALVES[side]["ball"]:                  # ボールユニット (34mm の受け 外径 35.4) のまわりを曲線でよける
        bx, by = k.HALVES[side]["ball"]
        m = m - k.cyl(bx, by, -1, 40, U34_R + 0.6)
    return m


def keycap(x, y, z0, z1):
    lo = mf.Manifold.cube([17.8, 17.8, 0.01]).translate([x - 8.9, y - 8.9, z0])
    hi = mf.Manifold.cube([15.8, 15.2, 0.01]).translate([x - 7.9, y - 7.3, z1 - 0.01])
    return mf.Manifold.batch_hull([lo, hi])


def claws(size, cz, rin, ring_top, r_base, angles, root_w, tip_w, tip_t, low_max=None, bulge=0.0):
    """爪 (リングの外周から曲線で立ち上がり、ボールにそって先が 0.7mm かぶる)"""
    R_ = bu.CUPS[size]["R"]
    tip_r = R_ - CLAW_OVER                                   # 爪の先の半径
    tip_z = cz + (rin**2 - tip_r**2) ** 0.5                  # 爪の先の高さ (ボールの赤道より上)
    r_tip = tip_r + tip_t                                    # 先の外側
    z_root = ring_top - 0.8
    h = tip_z - z_root

    def ball_r(z):
        return math.sqrt(max(rin**2 - (z - cz)**2, 0))
    t_root = r_base - ball_r(z_root)                         # 根元の厚さ (ボールの外側へ)
    out = []
    for a in angles:
        slices = []
        for i in range(CLAW_STEPS + 1):
            t = i / CLAW_STEPS
            z = z_root + h * t
            # 外側の面: 根元では縦 (リングの外周に接する)、先に向かって内側へ曲がる
            r_out = r_tip + (r_base - r_tip) * math.cos(math.pi / 2 * t)
            # 大きいボール (34mm) は赤道がリングより上なので、ボールの丸みに沿って外へふくらませる
            r_out = max(r_out, ball_r(z) + t_root + (tip_t - t_root) * t + bulge * math.sin(math.pi * t))
            if low_max and z < KEY_TOP + 0.5:
                r_out = min(r_out, low_max)                  # キーキャップの高さまではふくらませない
            # 幅: 根元は広く、先へ向かって曲線で細くなる
            w = tip_w + (root_w - tip_w) * (1 - t) ** 2.2
            half = math.degrees(w / 2 / r_out)
            slices.append(bu.sector(0, r_out, a - half, a + half, z - 0.01, z))
        out.append(k.union([mf.Manifold.batch_hull([slices[n], slices[n + 1]]) for n in range(CLAW_STEPS)]))
    return k.union(out), tip_z


def chamfer_top(m, z, r):
    """上の外側の角を丸く見せる面取り"""
    return m - (k.cyl(0, 0, z - 0.8, z + 0.01, r + 1) - k.cyl(0, 0, z - 0.8, z + 0.01, r, r - 0.8))


def claw_cover(size):
    """低いリング＋爪 3 本の「爪留め」カバー。ひねってロックする"""
    R_ = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R_
    rin = R_ + 0.3                                           # 爪の内側 (ボールとのすき間 0.3mm)
    ball = mf.Manifold.sphere(rin, 160).translate([0, 0, cz])
    if size == 34:
        a0, a1 = HOOD34_A
        hood = chamfer_top(bu.sector(HOOD34_IN, HOOD34_OUT, a0, a1, HOOD34_Z0, HOOD34_TOP), HOOD34_TOP, HOOD34_OUT)
        hooks = k.union([bu.sector(HOOK34_R, HOOD34_IN + 0.1, L - LOCK34_W/2, L + LOCK34_W/2, HOOK34_Z0, HOOK34_Z1)
                         for L in LOCK34_A])
        cl, tip_z = claws(34, cz, rin, HOOD34_TOP, HOOD34_OUT, [a for a in CLAWS_34 if a != FIXED_CLAW_34],
                          CLAW34_ROOT_W, CLAW34_TIP_W, CLAW34_TIP_T, bulge=CLAW34_BULGE)
        m = hood + hooks + (cl - k.cyl(0, 0, 0, HOOD34_Z0 + 0.5, 40))
        # 赤道より下ではボールの外側だけ (上へ抜ける)・土台にも触れない
        m = m - k.cyl(0, 0, 0, cz, R_ + 0.3) - k.cyl(0, 0, 0, U34_TOP + 0.5, U34_R + 0.2)
        return m - ball, tip_z
    ring = k.cyl(0, 0, bu.CUP_TOP, RING_TOP, bu.UNIT_R) - k.cyl(0, 0, bu.CUP_TOP - 1, RING_TOP + 1, R_ + 0.8)
    ring = chamfer_top(ring, RING_TOP, bu.UNIT_R)
    cl, tip_z = claws(size, cz, rin, RING_TOP, bu.UNIT_R, CLAWS, CLAW_ROOT_W, CLAW_TIP_W, CLAW_TIP_T)
    m = (ring + cl) - ball                                                  # 爪の内側をボールに沿わせる
    spigot = (k.cyl(0, 0, bu.RECESS_Z + 0.2, bu.CUP_TOP + 0.01, bu.SPIGOT_R) -
              k.cyl(0, 0, bu.RECESS_Z, bu.CUP_TOP + 1, R_ + 0.5))
    lugs = k.union([bu.sector(bu.SPIGOT_R - 0.3, bu.LUG_R, L - bu.LUG_W/2, L + bu.LUG_W/2,
                              bu.LUG_Z0, bu.LUG_Z0 + bu.LUG_H) for L in bu.LUG_ANGLES])
    return m + spigot + lugs, tip_z


def base34():
    """34mm 専用: 土台とカップが一体の受け。底は 25 / 19mm の土台と同じ (センサー・ネジ 3 本・ケーブルの出口)"""
    R = 17.0
    cz = bu.BALL_BOTTOM + R
    m = k.cyl(0, 0, 0, U34_TOP, U34_R)
    m = m - k.cyl(0, 0, bu.BASE_FLOOR, bu.CUP_BOTTOM, U34_R - 1.5)                       # センサーの部屋
    bosses, cut = [], []
    for a in k.BALL_SCREW_ANGLES:
        x, y = bu.polar(k.BALL_SCREW_R, a)
        bosses.append(k.cyl(x, y, 0, bu.CUP_BOTTOM, bu.BOSS_R))
        cut.append(k.cyl(x, y, -1, bu.INSERT_DEPTH, bu.INSERT_R))
    m = (m + k.union(bosses)) - k.union(cut)
    cut = [
        k.cube(-bu.SENSOR_W/2 - 0.2, -bu.SENSOR_L/2 - 0.2, bu.BASE_FLOOR - bu.SENSOR_POCKET,
               bu.SENSOR_W/2 + 0.2, bu.SENSOR_L/2 + 0.2, bu.BASE_FLOOR + 1),
        bu.rot_z(k.cube(-4.5, U34_R - 3, bu.BASE_FLOOR - bu.SENSOR_POCKET, 4.5, U34_R + 1, 5.5), bu.CABLE_ANGLE - 90),
        mf.Manifold.sphere(R + 0.5, 160).translate([0, 0, cz]),                          # ボールの受け
        k.cyl(0, 0, bu.CUP_BOTTOM - 1, cz, bu.LENS_HOLE_R),                               # センサーの窓
    ]
    # ベアリング (ボールの下寄り 55° で支える)。軸のネジはユニットの外から締める
    t = math.radians(bu.CUPS[34]["contact"])
    d = R + bu.BRG_R
    for a in bu.BRG_ANGLES:
        w = bu.BRG_W/2 + bu.BRG_SIDE
        pocket = (bu.along_x_cyl(bu.BRG_R + 0.4, 2*w) + k.cube(-w, -(bu.BRG_R + 0.4), 0, w, bu.BRG_R + 0.4, 20))
        reach = math.sqrt(U34_R**2 - (d*math.cos(t))**2) + 1
        head0 = w + bu.NEAR_WALL
        screw = (bu.x_cyl(bu.SCREW_PASS_R, 0, head0 + 0.1) + bu.x_cyl(bu.SCREW_HEAD_R, head0, reach) +
                 bu.x_cyl(bu.SCREW_PILOT_R, -(head0 - bu.NEAR_WALL + bu.SCREW_L - bu.NEAR_WALL + 0.8), 0))
        place = lambda m_, a=a: bu.rot_z(m_, a - 90).translate(
            [d*math.cos(t)*math.cos(math.radians(a)), d*math.cos(t)*math.sin(math.radians(a)), cz - d*math.sin(t)])
        cut += [place(pocket), place(screw)]
    m = m - k.union(cut)
    # 固定の爪 (土台と一体・回らないのでキーの角のあいだいっぱいまで太くできる)
    rin = R + 0.3
    fixed, _ = claws(34, cz, rin, U34_TOP + 0.8, U34_R, (FIXED_CLAW_34,), FIXED34_ROOT_W, CLAW34_TIP_W,
                     CLAW34_TIP_T, low_max=FIXED34_MAX_R, bulge=CLAW34_BULGE)
    m = m + (fixed - mf.Manifold.sphere(rin, 160).translate([0, 0, cz]))
    # ロックの出っぱり (左手前・基板の切り欠きの中)。フードのツメがこの下に入る。手前に小さな山 (カチッ)
    m = m + k.union([bu.sector(U34_R - 0.5, LEDGE34_R, L - LOCK34_W/2 - 1, L + LOCK34_W/2 + 1, LEDGE34_Z0, LEDGE34_Z1)
                     for L in LOCK34_A])
    m = m + k.union([bu.sector(U34_R - 0.5, HOOK34_R + 0.3, L + LOCK34_W/2 + 1.5, L + LOCK34_W/2 + 4,
                               HOOK34_Z0 + 0.1, HOOK34_Z1 - 0.1) for L in LOCK34_A])
    return m, {"cz": cz}


def half(side, size=25):
    outer = k.load(f"board_{side}")
    cavity = k.load(f"cavity_{side}")
    pcb = k.load(f"pcb_{side}")
    plate = k.load(f"plate_{side}").intersection(cavity.buffer(-0.5, join_style=2))
    parts = {}
    # トレイ (低い枠と床)
    tray = k.prism(outer, 0, RIM) - k.prism(outer.buffer(-4.0), FLOOR, RIM + 1)
    if side == "right":
        bx, by = k.HALVES["right"]["ball"]
        tray = tray - k.cyl(bx, by, -1, FLOOR + 1, (U34_R if size == 34 else bu.UNIT_R) + 0.3)
    # 電池のくぼみ (底 0.5mm) と、まわりのガイド
    ex, ey = BATTERY[side]
    tray = tray - k.cube(ex - BAT_W/2, ey - BAT_H/2, BATTERY_SKIN, ex + BAT_W/2, ey + BAT_H/2, FLOOR + 1)
    tray = tray + battery_guides(side)
    scr = battery_screen(side)
    if scr is not None:
        tray = tray + scr
    # ソケットの真下は、トレイの縁を少し削る (外側の列のソケットが縁の角の丸みにかかる所)
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "tools"))
        import check_pcb
        from shapely import affinity
        from shapely.ops import unary_union
        f = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
        sock = unary_union([affinity.scale(b[2], 1, -1, origin=(0, 0)).buffer(0.5)
                            for b in check_pcb.back_bodies(f) if b[1] == "socket"])
        if not sock.is_empty:
            tray = tray - k.prism(sock, PCB_B - SOCKET_H - TRAVEL - 0.25, 30)
    except (ImportError, FileNotFoundError):
        pass
    # 四隅の磁石とゴム足
    mboss, mcut, mags = magnet_feet(side)
    tray = (tray + mboss) - mcut
    # 電池のくぼみ (磁石の台がはみ出していても、電池の所は空ける)
    tray = tray - k.cube(ex - BAT_W/2, ey - BAT_H/2, BATTERY_SKIN, ex + BAT_W/2, ey + BAT_H/2, FLOOR + 5)
    # 電源スイッチのカバーが入る所
    tray = tray - switch_pocket(side)
    # XIAO の USB-C 側の端は壁の上に 1.5mm はみ出すので、その下だけ壁を低く掘る (外側の縁は残す)
    xb = k.HALVES[side]["xiao"]
    xd = k.HALVES[side]["dir"]
    x0, x1 = sorted((xb[0] + xd * 7.0, xb[0] + xd * (XIAO_HALF_L + 0.6)))
    tray = tray - k.cube(x0, xb[1] - XIAO_HALF_W - 0.5, PCB_B - XIAO_H - TRAVEL - 0.3, x1, xb[1] + XIAO_HALF_W + 0.5, 30)
    # MagSafe リングの溝 (裏) と、その真上の床の内側の厚み
    mx, my = MAG_CENTER[side]
    r0, r1 = MAG_ID/2 - MAG_GAP, MAG_OD/2 + MAG_GAP
    tray = tray + (k.cyl(mx, my, FLOOR - 0.01, FLOOR + MAG_BOSS, r1 + 1.0) - k.cyl(mx, my, FLOOR - 1, FLOOR + 2, r0 - 1.0))
    tray = tray - (k.cyl(mx, my, -1, MAG_DEPTH, r1) - k.cyl(mx, my, -2, MAG_DEPTH + 1, r0))
    parts["tray"] = tray
    parts["magsafe"] = k.cyl(mx, my, MAG_DEPTH - MAG_T, MAG_DEPTH, MAG_OD/2) - k.cyl(mx, my, -1, 5, MAG_ID/2)
    parts["magnets"] = mags
    parts["battery"] = k.cube(ex - 15, ey - 10, BATTERY_SKIN, ex + 15, ey + 10, BATTERY_SKIN + BATTERY_T)
    # 柱とガスケット・ネジ (下から留める)
    posts, pads, metal = [], [], []
    for x, y in POSTS[side]:
        posts.append(k.cyl(x, y, FLOOR - 0.01, POST_TOP, POST_R))
        pads.append(k.cyl(x, y, POST_TOP, PCB_B, PORON_OD / 2) - k.cyl(x, y, POST_TOP - 1, PCB_B + 1, PORON_ID / 2))
        metal += [k.cyl(x, y, NUT_B, PCB_B, NUT_R),                                  # ナット
                  k.cyl(x, y, COLLAR_B, NUT_B, COLLAR_R),                            # カラー
                  k.cyl(x, y, COLLAR_B - WASHER_T, COLLAR_B, WASHER_R),              # ワッシャー
                  k.cyl(x, y, COLLAR_B - WASHER_T - SCREW_HEAD_H, COLLAR_B - WASHER_T, SCREW_HEAD_R),
                  k.cyl(x, y, COLLAR_B, PCB_B - 0.3, 1.0)]                           # ネジ
    holes = k.union([k.cyl(x, y, -1, POST_TOP + 1, POST_HOLE_R) + k.cyl(x, y, -1, RECESS_D, WASHER_R + 0.3)
                     for x, y in POSTS[side]])
    parts["tray"] = parts["tray"] - holes
    parts["posts"] = k.union(posts) - holes
    parts["gasket"] = k.union(pads)
    parts["screws"] = k.union(metal)
    # 基板・プレート (プレートには穴なし)
    parts["pcb"] = k.prism(pcb, PCB_B, PCB_T)
    so = sockets(side)
    if so is not None:
        parts["sockets"] = so
    parts["plate"] = k.prism(plate, PLATE_B, PLATE_T)
    # スイッチとキーキャップ
    parts["switch"] = k.union([k.cube(x - 6.9, y - 6.9, PLATE_T, x + 6.9, y + 6.9, PLATE_T + 3) for x, y in KEYS[side]])
    parts["caps"] = k.union([keycap(x, y, PLATE_T + 4, KEY_TOP) for x, y in KEYS[side]])
    # nice!view
    vx = 6*U if side == "left" else k.RIGHT_X - U
    parts["view"] = k.cube(vx - 7, 2.5*U - 18, VIEW_PCB_B, vx + 7, 2.5*U + 18, VIEW_TOP)
    parts["view_cover"] = view_cover(side)
    parts["switch_cover"] = switch_cover(side)
    parts["slider"] = switch_slider(side)
    if side == "left":
        ex, ey = 5.5*U, U
        parts["knob"] = (k.cyl(ex, ey, PCB_T + ENC_BODY_H, PCB_T + ENC_SHAFT_L, ENC_KNOB_D / 2) -
                         k.cyl(ex, ey, PCB_T + ENC_SHAFT_L - 0.6, PCB_T + ENC_SHAFT_L + 1, ENC_KNOB_D / 2 - 1.3)) + \
                        k.cube(ex - 6.0, ey - 6.0, PCB_T, ex + 6.0, ey + 6.0, PCB_T + ENC_BODY_H)
    else:
        bx, by = k.HALVES["right"]["ball"]

        def at(m):
            return m.translate([bx, by, BALL_Z0])
        cover, _ = claw_cover(size)
        if size == 34:
            base, info = base34()
            parts["ball_base"] = at(base)
        else:
            cup, info = bu.cup(size)
            parts["ball_base"] = at(bu.base())
            parts["ball_cup"] = at(cup)
        parts["ball_cover"] = at(cover)
        parts["ball"] = at(mf.Manifold.sphere(bu.CUPS[size]["R"], 128).translate([0, 0, info["cz"]]))
    return parts


COLORS = {  # 色・分解図での持ち上げ量
    "tray": ("#e8e4dc", 0), "posts": ("#d2cdc3", 0), "gasket": ("#e98f9c", 8),
    "pcb": ("#202124", 16), "plate": ("#3a3b3f", 26), "switch": ("#8e949b", 34), "caps": ("#f3f0e9", 46),
    "view": ("#11181f", 26), "knob": ("#2b2d31", 46), "screws": ("#a9adb3", 0), "magsafe": ("#8a8f98", -14), "battery": ("#5b7fa6", 4), "magnets": ("#8a8f98", -14), "sockets": ("#e8e8e8", 16),
    "view_cover": ("#2b2d31", 40), "switch_cover": ("#2b2d31", 20), "slider": ("#b8432f", 30),
    "ball_base": ("#d9d5cc", 0), "ball_cup": ("#ece7dd", 22), "ball_cover": ("#2b2d31", 44), "ball": ("#b8432f", 62),
}


def main(out, size=25):
    os.makedirs(out, exist_ok=True)
    manifest = []
    for side in ("left", "right"):
        for name, m in half(side, size).items():
            fn = f"{name}_{side}"
            k.save_stl(m, os.path.join(out, f"{fn}.stl"))
            color, ex = COLORS[name]
            manifest.append(dict(name=fn, color=color, explode=ex, opacity=1))
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"))
    cz = bu.BALL_BOTTOM + 12.5
    _, claw_top = claw_cover(25)
    print(f"キーキャップ上 {KEY_TOP:.1f} / リング上面 {RING_TOP:.1f} / 爪の先 {claw_top:.1f} / "
          f"ボールのてっぺん {cz + 12.5:.1f} (19mm: {bu.BALL_BOTTOM + 19:.1f}) / トレイの縁 {RIM:.1f}")
    print(f"柱の上 {POST_TOP:.2f} / ナットの下 {NUT_B:.2f} (動ける量 {NUT_B - POST_TOP:.2f}) / "
          f"カラー {COLLAR_B:.2f}〜{NUT_B:.2f} / 床のくぼみ {RECESS_D:.2f} (床 {FLOOR})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "concept_out", int(sys.argv[2]) if len(sys.argv) > 2 else 25)
