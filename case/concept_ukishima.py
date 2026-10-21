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

# --- 部品の寸法 (case/parts_dims.json)。環境変数 KATAWARE_DIMS で別のファイル (例: 一番大きい部品の値) に切り替えられる ---
DIMS_FILE = os.environ.get("KATAWARE_DIMS", os.path.join(HERE, "parts_dims.json"))
D = {kk: v for kk, v in json.load(open(DIMS_FILE, encoding="utf-8")).items() if not kk.startswith("_")}
# --- ボールユニットを低くする (構想の値): 土台の底を 1.0mm に (センサー基板の下は 0.5mm) ---
bu.BASE_FLOOR = 1.0
# --- センサー: PixArt PMW3610DM-SUDU ＋ レンズ LM18-LSI (データシートの値・図からの読み取り) ---
# ボールの下面から下へ: レンズの上面 (基準面) 2.4 / センサー基板の上面 約 5.75 / センサーがレンズに乗る面 8.35 /
#   センサー本体の裏 約 9.2。基板にはレンズが通る穴があり、センサー本体は基板の裏 (ボールと反対側) にぶら下がる。
# 収め方: 受けの床に、基板のくぼみ (位置決め) ＋ センサー本体が入る穴。カップの足で基板を上から押さえ、ツメで留める。
#   コネクタは横向き (JST SH SM06B など・高さ 2.9) を右 (+x) の辺に付け、ケーブルは床の穴から台の中を下りて窓から出す
bu.BALL_BOTTOM = 7.5                                   # ボールの下面 (ユニットの座標)。カップ・ベアリングはこれが基準
bu.SENSOR_T = D["sensor_t"]
PMW_LENS_TOP = bu.BALL_BOTTOM - D["pmw_gap"]           # レンズの上面
SPCB_TOP = bu.BALL_BOTTOM - D["pmw_pcb_top"]           # センサー基板の上面
SPCB_BOT = SPCB_TOP - bu.SENSOR_T                      # センサー基板の下面
PMW_REF = bu.BALL_BOTTOM - D["pmw_ref"]                # センサーがレンズに乗る面
PMW_BACK = bu.BALL_BOTTOM - D["pmw_back"]              # センサー本体の裏 (一番下)
PIT_EXTRA = 0.3                                        # センサー本体の裏の下のすき間 (レンズの固定ピンの頭など)
# --- 受け (トレイと一体) は 19 / 25mm 共通: 外径 34・穴 31。カップの外径は 30.4 (34mm ボールはやめた) ---
bu.UNIT_R = 17.0
bu.BASE_IN_R = bu.UNIT_R - bu.BASE_WALL
bu.CUP_R = bu.BASE_IN_R - 0.3
SENSOR_CONN_H = D["sensor_conn_h"]
SENSOR_CHAMFER = D["sensor_chamfer"]   # センサー基板の左手前の角の面取り (傾けた時に下へ来る角)
bu.SENSOR_TOP = SPCB_TOP                # カップの足はここ (基板の上面) を押さえる
bu.SENSOR_W = D["spcb_x1"] - D["spcb_x0"]
bu.SENSOR_L = D["spcb_y1"] - D["spcb_y0"]

# --- 34mm ボール: 専用ユニット (19 / 25mm と同じく親指で転がす) ---
# 34mm はボールが重く、指で押す力も大きいので、25 / 19mm と土台を共用しない。
#  - 土台とカップを一体に (受けの壁が 2 重にならない分、壁が厚い)。外径 35.4mm (基板の穴 36mm に収まる)
#  - ベアリングは 25 / 19mm と同じ向き (0°/120°/240°)・同じ 45° で支える → 傾けても約 45° までボールが浮かない
#  - ボールの一番太い所 (赤道) がキーキャップより上にあるので、ボールの下半分を囲むリングは作れない
#    (リングがボールに引っかかって、カバーが外せなくなる)。カバーは「赤道より下ではボールの外側だけ」を通る形にする
#  - 爪 3 本: 45° (キーの角のあいだ) は下ケースと一体の「固定の爪」。135° と 315° はフードの爪
#  - カバーは、キーも基板もない左手前の空き (140〜290°) を囲む「フード」。外側でひねってロックする
#  - 親指の来る左手前 (135°〜315°) は爪がなく 180° あく。フードはそこを赤道より下で囲む低い壁
bu.CUPS[34] = {"R": 17.0, "contact": 45}       # テンティングでも浮かないよう 45° (55° だと約 22° で浮く)
U34_R = 17.7                      # 34mm ユニットの外径 (半径)。基板・プレートの穴 (半径 18) とのすき間 0.3mm
U34_TOP = 16.0                    # 一体型の受けの上面
CLAWS_34 = (45, 135, 315)         # 爪の向き (19 / 25mm と同じ斜め 3 か所。親指の来る左手前に 180° の開き)
FIXED_CLAW_34 = 45                # 土台と一体の爪
FIXED34_ROOT_W, FIXED34_MAX_R = 11.0, 20.0     # 固定の爪: キーの角のあいだ (約 6mm) に収まる幅・ふくらみ
CLAW34_ROOT_W, CLAW34_TIP_W, CLAW34_TIP_T = 18.0, 5.0, 2.6
CLAW34_BULGE = 1.2                # 34mm の爪の中ほどを厚くする量
# フード (カバー): 左手前の空きを囲む C 形の壁。ひねってロック (さし込む時は +30° の位置)
HOOD34_A = (130, 320)             # フードの範囲 (ロックした時)。爪 135° / 315° の根元を含む
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
BATTERY_T, BATTERY_TOL = D["battery_t"], D["battery_tol"]   # 電池の厚さと、ばらつき・ふくらみの見込み
SOCKET_H = D["socket_h"]   # ホットスワップソケットの高さ (基板の裏から)
PORON = 1.9          # 基板の下のポロン (3mm のシートを締めて約 1.9mm)
NUT_R, NUT_H = D["nut_d"] / 2, D["nut_h"]   # SMT ナット
TRAVEL = PORON - NUT_H            # 基板が沈める量 0.4mm (ナットの下面と柱の上面のすき間)
PCB_B = BATTERY_SKIN + BATTERY_T + BATTERY_TOL + 0.1 + TRAVEL + SOCKET_H
PCB_T = PCB_B + 1.6
PLATE_B, PLATE_T = PCB_T + 1.0, PCB_T + 2.2
RIM = PCB_B - 1.5    # トレイの縁 (基板の下面より 1.5mm 低い → 浮いて見える)
RIM_TOP = None       # 縁の上 (下で PLATE_T に決める)。縁は全周、プレートの上面と同じ高さ (デッキ)
RIM_GAP = 0.6        # 縁の内側と基板・プレート・基板の裏の部品とのすき間
RIM_ROUND = 2.0      # 縁の上の外側の角の丸み
BALL_Z0 = 0.0        # ボールユニットの底 (トレイの床に落とし込む)
KEY_TOP = PLATE_T + D["plate_to_keytop"]   # キーキャップの上 (Choc v2 ＋ ロープロファイルのキーキャップ)
RIM_TOP = PLATE_T                         # 縁の上 = プレートの上面
HOOD34_Z0 = PLATE_T + HOOD34_Z0_ABOVE_PLATE
HOOD34_TOP = U34_TOP + 1.2        # フードの上面: カップの縁のすぐ上 (19 / 25mm のリングと同じく低く)。爪はそのぶん長い
HOOK34_Z0, HOOK34_Z1 = HOOD34_Z0, HOOD34_Z0 + 1.0
LEDGE34_Z0, LEDGE34_Z1 = HOOK34_Z1 + 0.1, HOOK34_Z1 + 1.3

# --- 爪留めカバー ---
RING_TOP = bu.CUP_TOP + 1.2        # リングの上面: カップの上面のすぐ上 (ボールの赤道より下・低く見せる)。爪はそのぶん長い
# 爪の向き (上から見て。0° = 右 = Enter の方)。斜め 3 か所:
#   45°  … 右の 2 つのキー ([ ] 側と N 側) の角と角のあいだ。リングのまわりでキーから一番遠い (約 6mm)
#   135° … 左奥。315° … 右手前
# 親指の来る左手前 (225°・ボールを傾ける向き) に 180° の開き → ボールを前後 (上下スクロール)・左右に転がしても
# 親指が爪に当たらない。爪はどれも赤道より上でボールにかぶるので、開きが広くてもボールは抜けない
CLAWS = (45, 135, 315)
CLAW_OVER = 0.7                   # 爪の先がボールにかぶる幅 (半径で)。これを基準にする
# 3D プリント (A1 mini などの 0.4mm ノズル・PLA) で折れにくい形
# 爪の外側の面は、リングの外周 (縦の面) からそのまま立ち上がり、なめらかにボール側へ曲がる
# (根元で外周に接する曲線 = 段差のない「馴染む」形)。上から見ても、根元は裾広がりの曲線でリングに溶け込む
CLAW_TIP_T = 2.2                  # 爪の先の厚さ (ボールの外側へ)。0.4mm ノズルで壁 5〜6 周
CLAW_ROOT_W = 14.0                # 爪の幅 (根元・リングの上面で・mm)
CLAW_TIP_W = 4.0                  # 爪の幅 (先・mm)
CLAW_STEPS = 28                   # 曲面を作る輪切りの数

# --- ボールユニットを傾ける (お試し中。角度はまだ決めていない) ---
# ユニット (土台・カップ・カバー) をそのまま左手前 (225°) へ傾ける。底の低い側の縁が机 (z=0) に来るまで持ち上げ、
# 下にくさび形の台を足す。傾けると基板の切り欠きの縁 (左と手前) に当たるので、少し奥 (キーの方) へずらす
TILT_AZ = 225.0                   # 傾ける向き (上から見て。225° = 左手前)
TILT_SHIFT = {0: (0.0, 0.0), 15: (1.0, 1.0), 30: (1.5, 1.5)}   # 角度ごとのずらす量 (計算で当たらないと確かめた値)
TRIAL_CLAWS = CLAWS


def ball_tilt(m, tilt):
    """ユニットの座標 (底の中心が原点) のまま、左手前へ tilt 度傾ける (ユニットの向きは回さない)"""
    return m.rotate([0, 0, -TILT_AZ]).rotate([0, tilt, 0]).rotate([0, 0, TILT_AZ])


def ball_place(m, tilt, r=None):
    """傾けたユニットをトレイの穴の位置へ置く。r = 土台の半径 (低い側の縁が机に来る高さを決める)"""
    bx, by = k.HALVES["right"]["ball"]
    sx, sy = TILT_SHIFT[tilt]
    lift = (r or bu.UNIT_R) * math.sin(math.radians(tilt))
    return ball_tilt(m, tilt).translate([bx + sx, by + sy, BALL_Z0 + lift])


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
BAT_W, BAT_H = D["battery_l"] + 1.0, D["battery_w"] + 1.0   # くぼみ (電池＋すき間)

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


XIAO_H, XIAO_HALF_W, XIAO_HALF_L = D["xiao_h"], 8.9, 10.5   # XIAO の厚さ (USB-C 込み)・半分の幅・半分の長さ
# エンコーダー (左手・EC11): 本体の高さ・軸の長さ (基板の上から)・つまみの直径
ENC = (5.5*U, U)
ENC_BODY_H, ENC_SHAFT_L, ENC_KNOB_D = D["enc_body_h"], D["enc_shaft_l"], D["enc_knob_d"]
# 基板の裏に出る部品の高さ (基板の裏から下へ・mm)。部品の名前の一部で決める
BACK_HEIGHTS = (("xiao", XIAO_H), ("jst", D["jst_h"]), ("molex", D["molex_h"]), ("smt_nut", NUT_H), ("socket", SOCKET_H))
DIODE_H = D["diode_h"]             # ダイオード (表面実装・基板の裏)
PIN_H = D["pin_h"]                 # 足の出る部品 (エンコーダー・nice!view のピン) を切った後の長さ


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
SW_LEVER_Z0, SW_LEVER_Z1 = PCB_T + D["pwr_lever_z0"], PCB_T + D["pwr_lever_z1"]      # レバーの高さ
SW_LEVER_TIP = 3.15               # レバーの先 (スイッチの中心から)
SW_POS = 0.75                     # レバーの位置 (中心から ±。動く量 1.5mm)
SWC_V0, SWC_V1 = -4.4, 6.9        # カバーの範囲 (奥行き。手前は XIAO の端と USB-C の切り欠きをよける)
SWC_POCKET_Z = 3.3                # トレイの壁を、ここまで掘ってカバーの台を入れる
SWC_BASE_TOP = PCB_B - TRAVEL - 0.45     # 台の上面 (基板の舌が沈んでも当たらない)
SWC_LEDGE_U, SWC_LEDGE_TOP = 2.35, PCB_T - 0.65   # つまみが乗る段 (舌の端 u 2.15 より外)
SWC_WALL_U0, SWC_WALL_U1 = 3.625, 5.125   # 外の壁 (トレイの外側の面より 1mm 出る)
SWC_ROOF_U0, SWC_ROOF_Z0, SWC_ROOF_Z1 = -1.0, PCB_T + D["pwr_sw_h"] + 0.45, PCB_T + D["pwr_sw_h"] + 2.45   # 屋根 (スイッチの上を隠す)
SWC_RECESS_Z = SWC_ROOF_Z0 + 1.0   # 屋根のくぼみの底 (つまみが入る)
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
    m = m + _uv_cube(SWC_ROOF_U0 - 0.5, 6.0, SWC_V0 - 0.1, SWC_V1 + 0.1, SWC_ROOF_Z0 - 0.3, 30)   # 屋根の内側の張り出し (全周の縁をよける)
    for u, v in SWC_SCREWS:
        m = m + k.cyl(u, v, -1, SWC_POCKET_Z + 0.1, 1.15) + k.cyl(u, v, -0.01, 1.2, 2.2, 1.0)
    return _pwr_place(side, m)


# --- nice!view のカバー: 画面のまわりにかぶせる枠 (窓あき)。nice!view の基板のふちに爪で引っかける ---
VIEW = {"left": (6*U, 2.5*U), "right": (k.RIGHT_X - U, 2.5*U)}
VIEW_W, VIEW_L = D["view_w"], D["view_l"]   # nice!view の大きさ (横 × 縦)
VIEW_PCB_B = PCB_T + D["view_mount_h"]   # nice!view の基板の下面 (ピンヘッダー・ソケットの高さ)
VIEW_TOP = VIEW_PCB_B + D["view_t"]   # nice!view の一番上 (基板＋画面)
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


def claw_cover(size, claw_angles=None):
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
    cl, tip_z = claws(size, cz, rin, RING_TOP, bu.UNIT_R, claw_angles or CLAWS, CLAW_ROOT_W, CLAW_TIP_W, CLAW_TIP_T)
    m = (ring + cl) - ball                                                  # 爪の内側をボールに沿わせる
    spigot = (k.cyl(0, 0, bu.RECESS_Z + 0.2, bu.CUP_TOP + 0.01, bu.SPIGOT_R) -
              k.cyl(0, 0, bu.RECESS_Z, bu.CUP_TOP + 1, R_ + 0.5))
    lugs = k.union([bu.sector(bu.SPIGOT_R - 0.3, bu.LUG_R, L - bu.LUG_W/2, L + bu.LUG_W/2,
                              bu.LUG_Z0, bu.LUG_Z0 + bu.LUG_H) for L in bu.LUG_ANGLES])
    return m + spigot + lugs, tip_z


def base34(cable_slot=True):
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
        mf.Manifold.sphere(R + 0.5, 160).translate([0, 0, cz]),                          # ボールの受け
        k.cyl(0, 0, bu.CUP_BOTTOM - 1, cz, bu.LENS_HOLE_R),                               # センサーの窓
    ]
    if cable_slot:
        cut.append(bu.rot_z(k.cube(-4.5, U34_R - 3, bu.BASE_FLOOR - bu.SENSOR_POCKET, 4.5, U34_R + 1, 5.5),
                            bu.CABLE_ANGLE - 90))
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


# ----- 34mm: カップ (受けはトレイと一体・共通) -----
CUP34_R = U34_R - 1.8             # カップの外径 (半径)。受けの穴とのすき間 0.3mm (19 / 25mm のカップと同じ)


# ----- ボールユニット (カップ＋球押さえ) と受けのロック: 差し込んで反時計回りに 20° ひねる -----
# (球押さえ・フードは時計回りで締まる。外す時に反時計回りに回すので、カップはそのたびに締まる向き)
UNIT_LUGS = (60, 180, 300)        # カップの外のツメ (ロックした時の向き)。ベアリングのネジ穴 (0/120/240° 付近) をよける
UNIT_LUG_W = 9.0                  # ツメの幅 (角度)
UNIT_TURN = 20.0                  # ひねる角度
UNIT_LUG_Z0, UNIT_LUG_Z1 = bu.BASE_H - 2.4, bu.BASE_H - 1.4    # ツメの高さ (ユニットの座標)
UNIT_LUG_R = bu.BASE_IN_R + 0.5   # ツメの先 (半径)。受けの溝は +0.2


def unit_lugs():
    """カップの外のツメ"""
    return k.union([bu.sector(bu.CUP_R - 0.5, UNIT_LUG_R, L - UNIT_LUG_W / 2, L + UNIT_LUG_W / 2, UNIT_LUG_Z0, UNIT_LUG_Z1)
                    for L in UNIT_LUGS])


def unit_lock_cut():
    """受けの内側の溝: 差し込む縦の溝 (ロックの -20° の位置) と、ひねる横の溝。ロックの手前に小さな山 (カチッ)"""
    r0, r1 = bu.BASE_IN_R - 0.1, UNIT_LUG_R + 0.2
    cut = []
    for L in UNIT_LUGS:
        e = L - UNIT_TURN                                                    # 差し込む時のツメの位置
        cut += [bu.sector(r0, r1, e - UNIT_LUG_W / 2 - 1.0, e + UNIT_LUG_W / 2 + 1.0, UNIT_LUG_Z0 - 0.2, bu.BASE_H + 1),
                bu.sector(r0, r1, e - UNIT_LUG_W / 2 - 1.0, L + UNIT_LUG_W / 2 + 0.8, UNIT_LUG_Z0 - 0.2, UNIT_LUG_Z1 + 0.2)]
    m = k.union(cut)
    bumps = k.union([bu.sector(r0, r1 + 0.1, L - UNIT_LUG_W / 2 - 2.6, L - UNIT_LUG_W / 2 - 1.0,
                               UNIT_LUG_Z1 + 0.2 - 0.3, UNIT_LUG_Z1 + 0.25) for L in UNIT_LUGS])
    return m - bumps


def _no_key(m, r):
    """カップの向きを決めるキー (奥の出っぱり) を取る (ロックのツメで向きが決まる)"""
    return m - (k.cube(-2, r - 0.01, bu.BASE_H - 2, 2, 20, bu.BASE_H) - k.cyl(0, 0, -1, 60, r))


def cup_unit(size):
    """ボールユニットのカップ (受けに差し込んでひねる)。19 / 25mm"""
    return _no_key(bu.cup(size)[0], bu.CUP_R) + unit_lugs()


def cup34():
    """34mm 用のカップ: 受け (トレイと一体・共通) の穴に入る下の部分＋受けの上に乗る縁 (固定の爪・フードのロックの出っぱり)。
    ベアリング 3 個・センサーを押さえる足 4 本"""
    b, _ = base34(cable_slot=False)
    m = (b ^ k.cyl(0, 0, bu.CUP_BOTTOM, bu.BASE_H, CUP34_R)) + (b ^ k.cyl(0, 0, bu.BASE_H, 80, 40))
    lx, ly0, ly1 = bu.SENSOR_W / 2 - 2.0, -(bu.SENSOR_L / 2 - 2.0), bu.SENSOR_L / 2 - 2.0
    legs = [k.cyl(x, y, bu.SENSOR_TOP, bu.CUP_BOTTOM + 0.5, 1.2) for x, y in
            ((-lx, ly0), (lx, ly0), (-lx, ly1), (lx, ly1))]
    return m + k.union(legs) + unit_lugs()


def _rect(x0, y0, x1, y1, margin=0.0):
    from shapely.geometry import box
    return box(x0 - margin, y0 - margin, x1 + margin, y1 + margin)


def pkg_poly(margin=0.0):
    """センサー本体 (足込み) を上から見た形。光学中心 (原点) から近い端まで pmw_pkg_oc、長い辺は y 方向"""
    w, L, oc = D["pmw_pkg_w"] / 2, D["pmw_pkg_l"], D["pmw_pkg_oc"]
    return _rect(-w, -oc, w, L - oc, margin)


def lens_poly(margin=0.0):
    w, L, oc = D["pmw_lens_w"] / 2, D["pmw_lens_l"], D["pmw_lens_oc"]
    return _rect(-w, -oc, w, L - oc, margin)


def conn_box():
    """横向きコネクタ (基板の上・右の辺)"""
    x1 = D["spcb_x1"]
    return (x1 - 4.5, 0.5, x1 + 1.5, 8.5)


def sensor_model():
    """センサー (ユニットの座標): 基板 (レンズの穴あき)・レンズ・センサー本体・横向きコネクタ"""
    board = k.prism(sensor_poly().difference(lens_poly(0.25)), SPCB_BOT, SPCB_TOP)
    lens = k.prism(lens_poly(), PMW_REF, PMW_LENS_TOP)
    pkg = k.prism(pkg_poly(), PMW_BACK, SPCB_BOT + 0.01)
    cx0, cy0, cx1, cy1 = conn_box()
    conn = k.cube(cx0, cy0, SPCB_TOP - 0.01, cx1, cy1, SPCB_TOP + SENSOR_CONN_H)
    return board + lens + pkg + conn


# ===== 斜めのボールユニット (下ケース・上ケース) =====
# ユニット (土台＝下ケース・カップと爪カバー＝上ケース) を左手前 (TILT_AZ) へ BALL_TILT 度傾けて、できるだけ沈める。
#  - 沈める深さは「センサー基板の一番低い角の下に LOWER_SKIN の床が残る」まで (センサーが一番下の部品)
#  - 机より下になる所は切り落とし、底は机と平行に平ら。傾いた底より下 (高い側) は台で埋める (下ケースと一体)
#  - 受け (下ケース) はトレイと一体。センサー基板はそこに収めたまま (ツメで留める)
#  - 上ケース (カップ・爪カバー / 34mm はカップ・フード) をボールの大きさごとに交換
#  - センサーのケーブルは、下ケースの底の穴から台の中を下りて、右 (コネクタ J の方) の窓から床の上へ出す
BALL_TILT = 30.0                  # 傾ける角度 (度)。お試しの模型で決める (19 / 25mm)
TILT_34 = None                    # None = 19 / 25mm と同じ角度
LOWER_SKIN = 0.4                  # センサー基板の下の床の一番薄い所 (印刷 2 層)
BALL_SHIFT = (0.0, 0.0)           # ユニットを置く位置 (トレイの穴の中心＝基板の ball からのずれ)


def _tilt_z(x, y, z, tilt=None):
    """ユニットの座標の点が、傾けたあと (沈める前) にどの高さに来るか"""
    t, a = math.radians(BALL_TILT if tilt is None else tilt), math.radians(TILT_AZ)
    return z * math.cos(t) - (x * math.cos(a) + y * math.sin(a)) * math.sin(t)


def sensor_poly(margin=0.0):
    """センサー基板を上から見た形 (ユニットの座標・光学中心が原点)。左手前 (-x, -y) の角を SENSOR_CHAMFER だけ面取り"""
    from shapely.geometry import Polygon
    x0, x1, y0, y1, c = D["spcb_x0"], D["spcb_x1"], D["spcb_y0"], D["spcb_y1"], SENSOR_CHAMFER
    p = Polygon([(x0 + c, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 + c)])
    return p.buffer(margin, join_style=2) if margin else p


def _rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def sensor_legs():
    """カップの足 (センサー基板を押さえる): 基板の角の近くで、レンズとコネクタをよけ、カップをひねる間も基板の上にある所"""
    from shapely.geometry import Point, box
    x0, x1, y0, y1 = D["spcb_x0"], D["spcb_x1"], D["spcb_y0"], D["spcb_y1"]
    keep = sensor_poly().buffer(-1.3).difference(lens_poly(1.5)).difference(box(*conn_box()).buffer(1.5))
    cands = [(x1 - 1.6, y0 + 1.6), (x1 - 1.6, y1 - 1.6), (x0 + 1.6, y1 - 1.6), (x0 + 1.6 + SENSOR_CHAMFER / 2, y0 + 1.6 + SENSOR_CHAMFER / 2)]
    out = []
    for x, y in cands:
        if all(keep.contains(Point(*_rot(x, y, d))) for d in range(0, -21, -4)):
            out.append((x, y))
    return out


def sensor_room_poly():
    """センサーの部屋 (基板の上〜カップの底): 基板＋足 (カップをひねる時に通る所も)＋コネクタ＋ケーブルの穴"""
    from shapely.geometry import Point, box
    from shapely.ops import unary_union
    cx0, cy0, cx1, cy1 = conn_box()
    g = [sensor_poly(0.8), box(cx0, cy0, cx1, cy1).buffer(0.5, join_style=2),
         box(D["spcb_x1"] + 0.4, cy0 - 0.5, bu.BASE_IN_R - 0.3, cy1 + 0.5)]
    for x, y in sensor_legs():
        for d in range(0, -21, -4):
            g.append(Point(*_rot(x, y, d)).buffer(1.8))
    return unary_union(g)


bu.LEGS = sensor_legs()


def ball_lift(tilt=None):
    """一番下に来る所が LOWER_SKIN の高さに来る持ち上げ量。調べる所: センサー本体の穴の底・基板の下 (くぼみと部屋の床)・
    カップが乗る段 (受けの穴の底のふち)"""
    pts = []
    pts += [(x, y, PMW_BACK - PIT_EXTRA) for x, y in pkg_poly(0.4).exterior.coords]
    pts += [(x, y, SPCB_BOT) for x, y in sensor_poly(0.2).exterior.coords]
    pts += [(x, y, SPCB_BOT) for x, y in sensor_room_poly().exterior.coords]
    pts += [(bu.BASE_IN_R * math.cos(math.radians(a)), bu.BASE_IN_R * math.sin(math.radians(a)), bu.CUP_BOTTOM)
            for a in range(0, 360, 5)]
    return LOWER_SKIN - min(_tilt_z(x, y, z, tilt) for x, y, z in pts)


def unit_place(m, tilt=None):
    """ユニットの座標 (底の中心が原点・z が軸) の形を、トレイの上の本当の位置へ"""
    tilt = BALL_TILT if tilt is None else tilt
    bx, by = k.HALVES["right"]["ball"]
    return ball_tilt(m, tilt).translate([bx + BALL_SHIFT[0], by + BALL_SHIFT[1], ball_lift(tilt)])


def _proj(m):
    """形を真上から見た外形 (shapely)"""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    return unary_union([Polygon(p).buffer(0) for p in m.project().to_polygons() if len(p) >= 3])


def size_tilt(size):
    return TILT_34 if (size == 34 and TILT_34 is not None) else BALL_TILT


def lower_foot(size=25):
    """受けの底の外形 (傾いた底を真上から見た形)"""
    return _proj(unit_place(k.cyl(0, 0, 0, 0.01, bu.UNIT_R)))


SENSOR_CLIP_W, SENSOR_CLIP_T, SENSOR_CLIP_HOOK = 3.0, 1.0, 0.35   # センサー基板を留めるツメ (幅・厚さ・かかり)
_SOCKET_CACHE = {}


SOCKET_FILLET = 10.0              # 受けの付け根のアールの半径 (床の上)。基板の下では基板の裏の部品より低く切る


def socket_fillet(solid, rf=None, steps=25):
    """受けの付け根の凹のアール: 床 (FLOOR) から高さ rf までの輪切りを、受けの断面を外へ広げて積む"""
    from shapely.geometry import Polygon
    rf = SOCKET_FILLET if rf is None else rf
    out = []
    for i in range(steps):
        h1 = rf * (i + 1) / steps
        z = FLOOR + h1
        sec = _proj(solid.trim_by_plane([0, 0, 1], z - 0.05).trim_by_plane([0, 0, -1], -z))
        if sec.is_empty:
            continue
        polys = getattr(sec, "geoms", [sec])
        sec = Polygon(max(polys, key=lambda g: g.area).exterior)
        hm = rf * (i + 0.5) / steps                                          # この輪切りの真ん中の高さ
        off = rf - math.sqrt(max(rf**2 - (rf - hm)**2, 0))                   # 円弧 (床で rf、高さ rf で 0)
        out.append(k.prism(sec.buffer(off, join_style=1), FLOOR - 0.01, FLOOR + h1))
    return k.union(out)


def socket():
    """ボールの受け (トレイと一体)。(足す形, くり抜く形, ツメ) を返す。19 / 25mm 共通
    傾けた受け＋その下の台。底は z=0 で平ら (トレイの裏と同じ面)。センサー基板のくぼみ・留めるツメ・ケーブルの通り道つき"""
    key = (BALL_TILT, BALL_SHIFT, bu.UNIT_R)
    if key in _SOCKET_CACHE:
        return _SOCKET_CACHE[key]
    r, inner = bu.UNIT_R, bu.BASE_IN_R
    # 受けの中: カップの入る穴 (カップの底から上) / センサーの部屋 (センサーの形に合わせて狭く) / 基板のくぼみ
    inside = (k.cyl(0, 0, bu.CUP_BOTTOM, 80, inner) +
              k.cyl(0, 0, bu.GROOVE_Z0 - 0.2, 80, bu.GROOVE_R + 0.2) +        # 上のふち: 球押さえのツメ・カチッの山が少しはみ出す分
              k.prism(sensor_room_poly(), SPCB_BOT + 1.0, bu.CUP_BOTTOM + 0.01) +      # 部屋 (基板の下面から 1mm 上〜)
              k.prism(sensor_poly(0.2), SPCB_BOT, SPCB_BOT + 1.01) +                  # 基板のくぼみ (位置決め)
              k.prism(pkg_poly(0.4), PMW_BACK - PIT_EXTRA, SPCB_BOT + 0.01))          # センサー本体の穴
    solid = unit_place(k.cyl(0, 0, 0, bu.BASE_H, r))
    foot = lower_foot()
    below = unit_place(k.cyl(0, 0, -80, 0.01, r + 30))                      # 傾いた底より下 (台)
    solid = solid + (k.prism(foot, -1, 60) ^ below)
    # 付け根のアール (トレイの床から受けの壁へ、なだらかにつなぐ裾。円柱が床から生えて見えないように)
    fil = socket_fillet(solid)
    keep_out = [k.prism(k.load("pcb_right").buffer(0.5), PCB_B - TRAVEL - SOCKET_H - 0.4, 60)]   # 基板の下は部品より低く
    for part in back_parts("right").values():                                # XIAO など背の高い部品はその下まで
        b = part.bounding_box()
        keep_out.append(k.prism(_proj(part).buffer(0.8), b[2] - TRAVEL - 0.4, 60))
    solid = solid + (fil - k.union(keep_out))
    solid = max(solid.decompose(), key=lambda m_: m_.volume())             # 切った残りの小さなかけらを除く
    # くり抜く形: 受けの中 (カップの入る穴・センサーの部屋・くぼみ・向きの溝)
    voids = unit_place(inside)
    voids = voids + unit_place(unit_lock_cut())                             # ボールユニットのロックの溝
    # センサーのケーブル: 底の穴 → 台の中をまっすぐ下へ → 右の窓から床の上へ (基板の裏のコネクタ J へ)
    cx0, cy0, cx1, cy1 = conn_box()
    slot = unit_place(k.cube(D["spcb_x1"] + 0.4, cy0 - 0.5, -3.0, inner - 0.3, cy1 + 0.5, SPCB_BOT + 1.2))
    shaft = k.prism(_proj(slot), FLOOR, 60) ^ unit_place(k.cyl(0, 0, -80, SPCB_BOT + 1.0, inner - 0.3))
    sb = slot.bounding_box()
    window = k.cube(sb[0], (sb[1] + sb[4]) / 2 - 4.5, FLOOR, sb[0] + 40, (sb[1] + sb[4]) / 2 + 4.5, FLOOR + 4.0)
    posts = k.union([k.cyl(x, y, -1, 60, POST_R + 1.0) for x, y in POSTS["right"]])
    voids = voids + slot + shaft + (window - posts)                         # 窓は受けの台・リップを抜ける (柱は残す)
    # センサー基板を留めるツメ 2 か所 (奥の辺・左の辺)。基板をパチッとはめる → カップを外しても基板は抜けない。
    # カップの足がひねる時に通る所はよける
    x0, x1, y0, y1 = D["spcb_x0"] - 0.2, D["spcb_x1"] + 0.2, D["spcb_y0"] - 0.2, D["spcb_y1"] + 0.2
    cw, T_, H_ = SENSOR_CLIP_W / 2, SENSOR_CLIP_T, SENSOR_CLIP_HOOK
    zt, z0 = SPCB_TOP, SPCB_BOT
    bx_ = (x0 + x1) / 2 - 3.0                                                # 奥の辺 (足・コネクタをよけて少し左)
    ly_ = (y0 + SENSOR_CHAMFER + y1) / 2                                     # 左の辺の、面取りから上の真ん中
    clips = [
        k.cube(bx_ - cw, y1, z0, bx_ + cw, y1 + T_, zt + 0.9) + mf.Manifold.batch_hull([
            k.cube(bx_ - cw, y1 - H_, zt + 0.05, bx_ + cw, y1, zt + 0.35),
            k.cube(bx_ - cw, y1, zt + 0.85, bx_ + cw, y1 + 0.01, zt + 0.9)]),
        k.cube(x0 - T_, ly_ - cw, z0, x0, ly_ + cw, zt + 0.9) + mf.Manifold.batch_hull([
            k.cube(x0, ly_ - cw, zt + 0.05, x0 + H_, ly_ + cw, zt + 0.35),
            k.cube(x0 - 0.01, ly_ - cw, zt + 0.85, x0, ly_ + cw, zt + 0.9)]),
    ]
    clips = unit_place(k.union(clips))
    _SOCKET_CACHE[key] = (solid, voids, clips)
    return _SOCKET_CACHE[key]


def lower_case(size=25):
    """受け (トレイと一体) を単体で見た形 (確認・絵用)"""
    solid, voids, clips = socket()
    m = (solid - voids + clips).trim_by_plane([0, 0, 1], 0.0)
    return k.union([p for p in m.decompose() if p.volume() > 1.0]), {}


def ball_set(size=25):
    """傾けて置いたユニット一式 (下ケース・カップ・カバー・ボール) と、ボールの中心"""
    R = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R
    T = size_tilt(size)
    info = {}
    out = {}
    if size == 34:
        out["ball_cup"] = unit_place(cup34(), T)
        cover, _ = claw_cover(34)
    else:
        out["ball_cup"] = unit_place(cup_unit(size), T)
        cover, _ = claw_cover(size)
    out["sensor"] = unit_place(sensor_model(), T)
    out["ball_cover"] = unit_place(cover, T)
    out["ball"] = unit_place(mf.Manifold.sphere(R, 128).translate([0, 0, cz]), T)
    info["ball_top"] = out["ball"].bounding_box()[5]
    return out, info


def rim_solid(side, outer, pcb, plate):
    """全周の縁 (床の上〜RIM_TOP)。外側の上の角は RIM_ROUND で丸める"""
    from shapely.ops import unary_union
    cav = unary_union([pcb, plate] + [_proj(s) for s in back_parts(side).values()]).buffer(RIM_GAP, join_style=1)
    top, r = RIM_TOP, RIM_ROUND
    m = k.prism(outer.difference(cav), FLOOR - 0.01, top - r)
    n = 8
    for i in range(n):
        z0, z1 = top - r + r * i / n, top - r + r * (i + 1) / n
        zm = (z0 + z1) / 2 - (top - r)
        d = r - math.sqrt(max(r**2 - zm**2, 0))
        m = m + k.prism(outer.buffer(-d, join_style=1).difference(cav), z0 - 0.01, z1)
    return m


def ball_clearance():
    """ボールユニット (カップの縁・球押さえ) のまわりのトレイを、少しあけてくり抜く形"""
    return unit_place(k.cyl(0, 0, bu.BASE_H - 0.01, 80, bu.UNIT_R + 0.4))


LIP_IN = 2.5                      # リップが基板の縁の下へ入る幅


def inner_lip(side, outer, pcb):
    """縁の内側のリップ: 基板の縁の下 LIP_IN まで、基板が沈んでも当たらない高さ。裏の部品・電池の所は低く/よける"""
    reg = outer.buffer(-0.5).difference(pcb.buffer(-LIP_IN))
    lip = k.prism(reg, FLOOR - 0.01, PCB_B - TRAVEL - 0.3)
    for part in back_parts(side).values():
        b = part.bounding_box()
        lip = lip - k.prism(_proj(part).buffer(0.6), b[2] - TRAVEL - 0.3, 60)
    ex, ey = BATTERY[side]
    lip = lip - k.cube(ex - BAT_W / 2 - 0.3, ey - BAT_H / 2 - 0.3, FLOOR - 1, ex + BAT_W / 2 + 0.3, ey + BAT_H / 2 + 0.3, 60)
    for x, y in POSTS[side]:                                                # 柱のまわり (ネジ・ナット)
        lip = lip - k.cyl(x, y, FLOOR, 60, PORON_OD / 2 + 0.5)
    return lip


# ===== ボールのまわりのデッキ (別部品・プレートと同じ色で印刷) =====
# 基板の四角い外形の中で、ボールのまわりの切り欠きを、プレートの上面の高さまで埋める板。
# 「プレート＋デッキ」が 1 枚の四角い島に見える。下の「キール」がトレイ (リップ・受けのアール) に乗り、トレイの裏から M2 ネジで留める。
# 外側の縁の下はトレイを低く削って、基板と同じ影のすき間を見せる。34mm の時はフードがこの角に来るので、デッキは付けない
DECK_UNDERCUT = 1.5               # デッキの外側の縁の下の影の奥行き (細い所でもキールが残るように)
DECK_SCREW_R = 0.8                # デッキの下穴 (M2 タッピング)


def deck_region():
    from shapely.geometry import Point, box
    pcb = k.load("pcb_right")
    bx, by = k.HALVES["right"]["ball"]
    rect = box(*pcb.bounds).buffer(-4.25).buffer(4.25)
    return rect.difference(pcb.buffer(RIM_GAP)).intersection(Point(bx, by).buffer(40)), rect


def deck_clearance(size):
    return unit_place(k.cyl(0, 0, -80, 80, bu.UNIT_R + 0.4))                # ユニット (受け・カップ・球押さえ)


_DECK_CACHE = {}


def deck_plan(size=25):
    """デッキを上から見た形: 四角の切り欠き − ユニットの通る所。細すぎる所 (幅 2mm 未満) は捨てる"""
    from shapely.geometry import Polygon, MultiPolygon
    reg, _ = deck_region()
    sec = _proj(deck_clearance(size).trim_by_plane([0, 0, 1], PCB_B).trim_by_plane([0, 0, -1], -PLATE_T))
    g = reg.difference(sec).buffer(-1.0, join_style=1).buffer(1.0, join_style=1)
    polys = [q for q in getattr(g, "geoms", [g]) if q.area > 15.0]
    return MultiPolygon(polys) if len(polys) > 1 else (polys[0] if polys else Polygon())


def deck_band():
    """デッキの外側の縁の下 (影のすき間): トレイを縁の高さまで低くする帯"""
    reg, rect = deck_region()
    return k.prism(reg.difference(rect.buffer(-DECK_UNDERCUT)), RIM, 60) - unit_place(k.cyl(0, 0, -80, 80, bu.UNIT_R + 0.01))


def deck_support():
    """デッキの下にあるトレイ (縁・リップ・受け) の形"""
    outer, pcb = k.load("board_right"), k.load("pcb_right")
    solid, voids, _c = socket()
    tr = k.prism(outer, 0, RIM) - k.prism(outer.buffer(-4.0), FLOOR, RIM + 1) + inner_lip("right", outer, pcb) + solid
    return tr - voids - deck_band()


def ball_deck(size=25):
    """デッキ (トレイの上の本当の位置・19 / 25mm 用)。上の板＋下の「キール」(外側の縁から影の奥行きだけ内側)。
    キールの下面はトレイ (リップ・受けのアール) にぴったり乗る"""
    key = (size, BALL_TILT)
    if key in _DECK_CACHE:
        return _DECK_CACHE[key]
    if not deck_screws():                                                    # ネジを入れる場所もないほど小さい → デッキは作らない
        _DECK_CACHE[key] = None
        return None
    _, rect = deck_region()
    plan = deck_plan(size)
    keel = plan.intersection(rect.buffer(-DECK_UNDERCUT))
    m = k.prism(plan, PCB_B, PLATE_T) + k.prism(keel, FLOOR, PCB_B + 0.01)
    m = m - deck_clearance(size) - deck_support()
    for x, y in deck_screws():
        m = m - k.cyl(x, y, 0, PCB_B + 2.5, DECK_SCREW_R)
    pin = deck_pin()
    if pin:
        m = m - k.cyl(pin[0], pin[1], 0, deck_pin_top() + 0.3, DECK_PIN_R + 0.15)
    pieces = [p for p in m.decompose() if p.volume() > 20.0]
    sc = deck_screws()
    if len(pieces) > 1 and sc:                                               # 分かれたら、ネジのあるかけらだけ残す (留められないので)
        x, y = sc[0]
        pieces = [p for p in pieces if (p ^ k.cyl(x, y, PCB_B, PLATE_T, 3.0)).volume() > 0.01] or pieces[:1]
    m = k.union(pieces)
    _DECK_CACHE[key] = m
    return m


def deck_tray_base():
    """デッキの下のトレイ (受けとアール) の形"""
    solid, voids, clips = socket()
    return solid - voids


def deck_screws():
    """デッキを留めるネジ (トレイの裏から M2 皿) の位置: キールの中 (縁から 1.6mm 以上内側)、ケーブルの通り道をよける"""
    from shapely.geometry import Point
    import numpy as np
    _, rect = deck_region()
    core = deck_plan(25).intersection(rect.buffer(-DECK_UNDERCUT)).buffer(-1.3)
    if core.is_empty:
        return []
    solid, voids, _c = socket()
    cup = deck_clearance(25)                                                 # 19 / 25mm のユニット (デッキは 19 / 25mm の時だけ)
    cands = []
    b = core.bounds
    for x in np.arange(b[0], b[2] + 0.01, 0.5):
        for y in np.arange(b[1], b[3] + 0.01, 0.5):
            rod = k.cyl(x, y, 0, PCB_B + 2.5, 1.2)
            if core.contains(Point(x, y)) and (rod ^ voids).volume() < 0.01 and (rod ^ cup).volume() < 0.01:
                cands.append((float(x), float(y)))
    if not cands:
        return []
    _, rect2 = deck_region()
    corner = (rect2.bounds[0], rect2.bounds[1])
    return [min(cands, key=lambda c: math.dist(c, corner) - 0.0)][:1]      # 角に近い 1 本


DECK_PIN_R, DECK_PIN_H = 1.0, 2.0  # デッキの向きを決めるピン (トレイと一体・デッキの穴に入る)


def deck_pin_top():
    """ピンの先: ピンの所のトレイ (リップなど) の上面から DECK_PIN_H"""
    p = deck_pin.__wrapped__() if hasattr(deck_pin, "__wrapped__") else None
    return PCB_B - TRAVEL - 0.3 + DECK_PIN_H


def deck_pin():
    """位置決めピン: キールの中で、ネジから一番遠い所"""
    from shapely.geometry import Point
    import numpy as np
    _, rect = deck_region()
    core = deck_plan(25).intersection(rect.buffer(-DECK_UNDERCUT)).buffer(-(DECK_PIN_R + 0.8))
    sc = deck_screws()
    if core.is_empty or not sc:
        return None
    b = core.bounds
    hood = ball_clearance()                                                  # 34mm のフード (ピンはトレイに残るのでよける)
    pts = [(float(x), float(y)) for x in np.arange(b[0], b[2] + 0.01, 0.5) for y in np.arange(b[1], b[3] + 0.01, 0.5)
           if core.contains(Point(x, y)) and
           (k.cyl(float(x), float(y), FLOOR, deck_pin_top(), DECK_PIN_R + 0.3) ^ hood).volume() < 0.01]
    return max(pts, key=lambda q: math.dist(q, sc[0])) if pts else None


def half(side, size=25):
    outer = k.load(f"board_{side}")
    cavity = k.load(f"cavity_{side}")
    pcb = k.load(f"pcb_{side}")
    plate = k.load(f"plate_{side}").intersection(cavity.buffer(-0.5, join_style=2))
    parts = {}
    # トレイ (低い枠と床)
    # トレイ: 床＋低い縁 (基板の下面より 1.5mm 低い → 一周同じ影のすき間で、基板とプレートが浮いて見える)
    # ＋縁の内側のリップ (基板の縁の下に入り、すき間から電池などが見えない)。ボールのまわりは別部品のデッキ
    tray = k.prism(outer, 0, RIM) - k.prism(outer.buffer(-4.0), FLOOR, RIM + 1) + inner_lip(side, outer, pcb)
    if side == "right":
        solid, voids, clips = socket()                                          # ボールの受け (トレイと一体)
        band = deck_band() if ball_deck(25) is not None else mf.Manifold()
        tray = ((tray + solid) - voids + clips - ball_clearance() - band).trim_by_plane([0, 0, 1], 0.0)
        tray = tray ^ k.prism(outer, -1, 80)                                    # トレイの外形からはみ出さない
        for x, y in deck_screws():                                              # デッキを留めるネジ (裏から M2 皿)
            tray = tray - k.cyl(x, y, -1, PCB_B + 1, 1.15) - k.cyl(x, y, -0.01, 1.2, 2.2, 1.0)
        pin = deck_pin()
        if pin:                                                                 # デッキの位置決めピン
            tray = tray + k.cyl(pin[0], pin[1], FLOOR, deck_pin_top(), DECK_PIN_R)
        tray = max(tray.decompose(), key=lambda m_: m_.volume())               # 計算でできる薄いかけらを除く
    # 電池のくぼみ (底 0.5mm) と、まわりのガイド
    ex, ey = BATTERY[side]
    tray = tray - k.cube(ex - BAT_W/2, ey - BAT_H/2, BATTERY_SKIN, ex + BAT_W/2, ey + BAT_H/2, FLOOR + 1)
    tray = tray + battery_guides(side)
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
    parts["battery"] = k.cube(ex - D["battery_l"]/2, ey - D["battery_w"]/2, BATTERY_SKIN, ex + D["battery_l"]/2, ey + D["battery_w"]/2, BATTERY_SKIN + BATTERY_T)
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
        ball, _ = ball_set(size)
        parts.update(ball)
        if ball_deck(25) is not None:
            parts["deck"] = ball_deck(25)
    return parts


COLORS = {  # 色・分解図での持ち上げ量
    "tray": ("#e8e4dc", 0), "posts": ("#d2cdc3", 0), "gasket": ("#e98f9c", 8),
    "pcb": ("#202124", 16), "plate": ("#3a3b3f", 26), "switch": ("#8e949b", 34), "caps": ("#f3f0e9", 46),
    "view": ("#11181f", 26), "knob": ("#2b2d31", 46), "screws": ("#a9adb3", 0), "magsafe": ("#8a8f98", -14), "battery": ("#5b7fa6", 4), "magnets": ("#8a8f98", -14), "sockets": ("#e8e8e8", 16),
    "view_cover": ("#2b2d31", 40), "switch_cover": ("#2b2d31", 20), "slider": ("#b8432f", 30),
    "ball_base": ("#d9d5cc", 0), "ball_cup": ("#ece7dd", 22), "sensor": ("#1f6f4a", 10), "deck": ("#3a3b3f", 26), "ball_cover": ("#2b2d31", 44), "ball": ("#b8432f", 62),
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
