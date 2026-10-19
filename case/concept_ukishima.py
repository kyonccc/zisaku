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

# --- 34mm ボール (画像用): 土台は同じ (外径 34mm)。ボールが外径いっぱいなので専用のカップと低いリングを使う ---
# ベアリングはボールの下寄り (55°) で支え、爪はキーのない 3 か所でキーキャップより上を外へふくらむ
bu.CUPS[34] = {"R": 17.0, "contact": 55}
RING_TOP_34 = 17.5                # 34mm のリングの上面 (ボールが太いので低くして、壁の厚さを確保)

# --- 高さ (机から) ---
FLOOR = 1.5          # トレイの床
BATTERY_SKIN = 0.5   # 電池のくぼみの底 (電池の上面 = 0.5 + 5.0 = 5.5mm)
PCB_B = BATTERY_SKIN + 5.0 + 0.5 + 1.85   # 電池 → 0.5mm → ソケット (1.85mm) → 基板の下面
PCB_T = PCB_B + 1.6
PLATE_B, PLATE_T = PCB_T + 1.0, PCB_T + 2.2
RIM = PCB_B - 1.5    # トレイの縁 (基板の下面より 1.5mm 低い → 浮いて見える)
PORON = 2.2          # 基板の下のポロン (3mm のシートを締めて約 2.2mm)
BALL_Z0 = 0.0        # ボールユニットの底 (トレイの床に落とし込む)
KEY_TOP = PLATE_T + 7.5

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

# --- 基板の留め方 (バーガーマウント: ビス留めでも、基板はポロンにはさまれて浮いたまま) ---
# 下から: トレイの床の皿ネジ (M2) → 柱の中 → M2 スペーサー (長さ 5mm) → 基板の穴 (φ4.2) を「触れずに」通る
# → 基板の上のポロン → ワッシャー → 上から M2 ネジ。ネジの頭はプレートの穴 (φ5.6) の中に沈む (キーキャップに当たらない)
# プレートはスイッチで基板にくっついているので、基板といっしょに浮く。
# スペーサーの長さで締めすぎを防ぐ (誰が組んでもポロンのつぶれ具合が同じ)
TOP_PORON = 0.8                   # 基板の上のポロン (1mm のシートを締めて約 0.8mm)
WASHER_R, WASHER_T = 2.5, 0.4     # M2 ワッシャー (外径 5mm)
SPACER_R = 1.75                   # 丸スペーサー 外径 3.5mm
SPACER_L = PORON + 1.6 + TOP_PORON + WASHER_T     # = 5.0mm (市販の長さ)
PCB_HOLE_R = 2.1                  # 基板の穴 φ4.2 (スペーサーに触れない)
PLATE_HOLE_R = 2.8                # プレートの穴 φ5.6 (キーの角どうしのすき間に収まる大きさ)
SCREW_HEAD_R, SCREW_HEAD_H = 2.0, 0.8     # 上のネジの頭 (φ4・高さ 0.8mm の極低頭)
POST_TOP = PCB_B - PORON
SCREW_TOP = POST_TOP + SPACER_L + SCREW_HEAD_H    # ネジの頭の上 (プレートの上面より低い)

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


def claw_cover(size):
    """低いリング＋爪 3 本の「爪留め」カバー。ひねってロックする部分は ball_unit と同じ (34mm は未設計)"""
    R_ = bu.CUPS[size]["R"]
    cz = bu.BALL_BOTTOM + R_
    ring_top = RING_TOP_34 if size == 34 else RING_TOP
    ring = k.cyl(0, 0, bu.CUP_TOP, ring_top, bu.UNIT_R)
    if size != 34:
        ring = ring - k.cyl(0, 0, bu.CUP_TOP - 1, ring_top + 1, R_ + 0.8)
    # 上の外側の角を丸く見せる面取り
    ring = ring - (k.cyl(0, 0, ring_top - 0.8, ring_top + 0.01, bu.UNIT_R + 1) -
                   k.cyl(0, 0, ring_top - 0.8, ring_top + 0.01, bu.UNIT_R, bu.UNIT_R - 0.8))
    rin = R_ + 0.3                                           # 爪の内側 (ボールとのすき間 0.3mm)
    tip_r = R_ - CLAW_OVER                                   # 爪の先の半径
    tip_z = cz + (rin**2 - tip_r**2) ** 0.5                  # 爪の先の高さ (ボールの赤道より上)
    claws = []
    r_base = bu.UNIT_R                                       # 根元の外側 = リングの外周
    r_tip = tip_r + CLAW_TIP_T                               # 先の外側
    z_root = ring_top - 0.8
    h = tip_z - z_root

    def ball_r(z):
        return math.sqrt(max(rin**2 - (z - cz)**2, 0))
    t_root = r_base - ball_r(z_root)                         # 根元の厚さ (ボールの外側へ)
    for a in CLAWS:
        slices = []
        for i in range(CLAW_STEPS + 1):
            t = i / CLAW_STEPS
            z = z_root + h * t
            # 外側の面: 根元では縦 (リングの外周に接する)、先に向かって内側へ曲がる
            r_out = r_tip + (r_base - r_tip) * math.cos(math.pi / 2 * t)
            # 大きいボール (34mm) は赤道がリングより上なので、ボールの丸みに沿って外へふくらませる
            r_out = max(r_out, ball_r(z) + t_root + (CLAW_TIP_T - t_root) * t)
            # 幅: 根元は広く、先へ向かって曲線で細くなる
            w = CLAW_TIP_W + (CLAW_ROOT_W - CLAW_TIP_W) * (1 - t) ** 2.2
            half = math.degrees(w / 2 / r_out)
            slices.append(bu.sector(0, r_out, a - half, a + half, z - 0.01, z))
        claws.append(k.union([mf.Manifold.batch_hull([slices[n], slices[n + 1]]) for n in range(CLAW_STEPS)]))
    m = ring + k.union(claws)
    m = m - mf.Manifold.sphere(rin, 128).translate([0, 0, cz])              # 爪の内側をボールに沿わせる
    if size == 34:
        return m, tip_z
    spigot = (k.cyl(0, 0, bu.RECESS_Z + 0.2, bu.CUP_TOP + 0.01, bu.SPIGOT_R) -
              k.cyl(0, 0, bu.RECESS_Z, bu.CUP_TOP + 1, R_ + 0.5))
    lugs = k.union([bu.sector(bu.SPIGOT_R - 0.3, bu.LUG_R, L - bu.LUG_W/2, L + bu.LUG_W/2,
                              bu.LUG_Z0, bu.LUG_Z0 + bu.LUG_H) for L in bu.LUG_ANGLES])
    return m + spigot + lugs, tip_z


def ball_cup(size):
    if size != 34:
        return bu.cup(size)
    keep = bu.LUG_ANGLES, bu.CLEAR
    bu.LUG_ANGLES, bu.CLEAR = (), 0.5          # 34mm: ひねるロックの溝はまだ無し (専用のロックは今後)
    try:
        return bu.cup(34)
    finally:
        bu.LUG_ANGLES, bu.CLEAR = keep


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
        tray = tray - k.cyl(bx, by, -1, FLOOR + 1, bu.UNIT_R + 0.3)
    parts["tray"] = tray
    # 柱とガスケット・ネジ (バーガーマウント)
    posts, pads, tops, metal = [], [], [], []
    for x, y in POSTS[side]:
        posts.append(k.cyl(x, y, FLOOR - 0.01, POST_TOP, 2.6))
        pads.append(k.cyl(x, y, POST_TOP, PCB_B, 3.0))
        tops.append(k.cyl(x, y, PCB_T, PCB_T + TOP_PORON, 2.7))
        st = POST_TOP + SPACER_L
        metal += [k.cyl(x, y, POST_TOP, st, SPACER_R),
                  k.cyl(x, y, st - WASHER_T, st, WASHER_R),
                  k.cyl(x, y, st, st + SCREW_HEAD_H, SCREW_HEAD_R),
                  k.cyl(x, y, 0, 1.2, 1.9, 1.1), k.cyl(x, y, 1.2, POST_TOP, 1.0)]
    screw_holes = k.union([k.cyl(x, y, -1, POST_TOP + 1, 1.1) + k.cyl(x, y, -0.01, 1.2, 2.0, 1.1)
                           for x, y in POSTS[side]])
    parts["tray"] = parts["tray"] - screw_holes
    parts["posts"] = k.union(posts) - screw_holes
    gap = k.union([k.cyl(x, y, POST_TOP - 1, PCB_T + TOP_PORON + 1, SPACER_R + 0.2) for x, y in POSTS[side]])
    parts["gasket"] = (k.union(pads) + k.union(tops)) - gap
    parts["screws"] = k.union(metal)
    # 基板・プレート
    parts["pcb"] = k.prism(pcb, PCB_B, PCB_T) - k.union([k.cyl(x, y, 0, 30, PCB_HOLE_R) for x, y in POSTS[side]])
    parts["plate"] = k.prism(plate, PLATE_B, PLATE_T) - k.union([k.cyl(x, y, 0, 30, PLATE_HOLE_R) for x, y in POSTS[side]])
    # スイッチとキーキャップ
    parts["switch"] = k.union([k.cube(x - 6.9, y - 6.9, PLATE_T, x + 6.9, y + 6.9, PLATE_T + 3) for x, y in KEYS[side]])
    parts["caps"] = k.union([keycap(x, y, PLATE_T + 4, KEY_TOP) for x, y in KEYS[side]])
    # nice!view
    vx = 6*U if side == "left" else k.RIGHT_X - U
    parts["view"] = k.cube(vx - 7, 2.5*U - 18, PCB_T, vx + 7, 2.5*U + 18, PCB_T + 4.2)
    if side == "left":
        ex, ey = 5.5*U, U
        parts["knob"] = (k.cyl(ex, ey, PCB_T + 1, KEY_TOP + 1.0, 7.5) -
                         k.cyl(ex, ey, KEY_TOP + 0.4, KEY_TOP + 2, 6.2))
    else:
        bx, by = k.HALVES["right"]["ball"]

        def at(m):
            return m.translate([bx, by, BALL_Z0])
        cup, info = ball_cup(size)
        cover, _ = claw_cover(size)
        parts["ball_base"] = at(bu.base())
        parts["ball_cup"] = at(cup)
        parts["ball_cover"] = at(cover)
        parts["ball"] = at(mf.Manifold.sphere(bu.CUPS[size]["R"], 128).translate([0, 0, info["cz"]]))
    return parts


COLORS = {  # 色・分解図での持ち上げ量
    "tray": ("#e8e4dc", 0), "posts": ("#d2cdc3", 0), "gasket": ("#e98f9c", 8),
    "pcb": ("#202124", 16), "plate": ("#3a3b3f", 26), "switch": ("#8e949b", 34), "caps": ("#f3f0e9", 46),
    "view": ("#11181f", 26), "knob": ("#2b2d31", 46), "screws": ("#a9adb3", 0),
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
    print(f"柱の上 {POST_TOP:.2f} / スペーサー {SPACER_L:.2f} / ネジの頭の上 {SCREW_TOP:.2f} "
          f"(プレートの上面より {PLATE_T - SCREW_TOP:.2f}mm 低い)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "concept_out", int(sys.argv[2]) if len(sys.argv) > 2 else 25)
