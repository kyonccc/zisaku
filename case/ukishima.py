"""浮島 (うきしま) の製作用 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    pip install manifold3d shapely ezdxf
    npx ergogen@4.1.0 pcb/ergogen -o pcb/ergogen/output   # 先に外形を作る
    python3 case/ukishima.py

できるもの (case/stl/ukishima/):
    tray_left.stl / tray_right.stl   … トレイ (床・低い枠・柱 8 本・MagSafe の溝・電池のくぼみ)。
                                       右はボールの受け (下ケース・センサー基板のくぼみとツメ・ケーブルの通り道) と一体
    ball_cup_25.stl / ball_cup_19.stl       … 上ケース: カップ (ベアリング 3 個)。ボールの大きさに合わせて交換
    ball_cover_25.stl / ball_cover_19.stl   … 上ケース: 爪留めカバー (爪 3 本・ひねってロック)
    ball_cup_34.stl                  … 34mm 用のカップ (固定の爪・フードのロックの出っぱりつき)
    ball_hood_34.stl                 … 34mm のフード (爪 2 本・外側でひねってロック)
    switch_cover_left.stl / _right   … 電源スイッチのカバー (トレイの縁に裏からネジ 2 本)
    switch_slider.stl                … つまみ＋フォーク (2 個印刷する・左右共通)
    view_cover_left.stl / _right     … nice!view のカバー (窓あき・nice!view にはめる)
STL は印刷する向き (置く面が下) で書き出す。

形と寸法は case/concept_ukishima.py (構想の 3D モデル) と同じものを使い、
ここでは「印刷する部品」にまとめて、USB の穴・ゴム足・ボールユニットの留め具を足す。
寸法はすべて mm。z はトレイの底面 (机) が 0。
"""
import math
import os
import sys

from shapely.geometry import Point, box
import manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_ukishima as cu  # noqa: E402

k, bu = cu.k, cu.bu
U = k.U
BATTERY, BAT_W, BAT_H = cu.BATTERY, cu.BAT_W, cu.BAT_H

# ===== ボールユニット =====
# ボールの受け (下ケース) はトレイと一体 (concept_ukishima.py の socket)。センサー基板はそこにツメで留めたまま。
# ボールの大きさを替える時は、上の部品 (カップ・カバー / 34mm はカップ・フード) だけを替える

# ===== トレイの穴・ゴム足 =====
USB_W = 14.0                      # USB-C のプラグが入る切り欠きの幅
# ゴム足は四隅の磁石の上に貼る (concept_ukishima.py の MAG_*)


def tray(side):
    parts = cu.half(side, 34 if side == "right" else 25)
    t = parts["tray"] + parts["posts"]
    h = k.HALVES[side]
    xx, xy = h["xiao"]
    ix, d = h["inner_x"], h["dir"]
    outer_x = ix + d * 5.0
    cut = [
        # USB-C の切り欠き (内側の壁。床の上から上まで)
        k.cube(min(ix - d, outer_x + d), xy - USB_W / 2, 1.0, max(ix - d, outer_x + d), xy + USB_W / 2, 20),
        # XIAO のリセットボタンを押す穴 (床)
        k.cube(ix + d * 2.5 - d * 5 - 2, xy - 6, -1, ix + d * 2.5 - d * 5 + 2, xy + 6, cu.FLOOR + 1),
    ]
    return t - k.union(cut)


def on_bed(m, rot=(0, 0, 0)):
    """印刷する向きに回して、机 (z=0) の上・真ん中に置く"""
    m = m.rotate(list(rot))
    b = m.bounding_box()
    return m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def check():
    """ぶつかり・置き場所の確認 (計算)。問題があれば止める"""
    problems = []
    for side in ("left", "right"):
        h = k.HALVES[side]
        o = k.load(f"board_{side}")
        mx, my = cu.MAG_CENTER[side]
        ring = Point(mx, my).buffer(cu.MAG_OD / 2 + 1).difference(Point(mx, my).buffer(cu.MAG_ID / 2 - 1))
        ex, ey = BATTERY[side]
        bat = box(ex - BAT_W / 2, ey - BAT_H / 2, ex + BAT_W / 2, ey + BAT_H / 2)
        avoid = [ring, bat.buffer(0.2)] + [Point(p).buffer(2.8 + 0.8) for p in cu.POSTS[side]]
        if h["ball"]:
            avoid.append(cu.lower_foot().buffer(1.0))                        # ボールの受け (トレイと一体)
        xx, xy = h["xiao"]
        avoid.append(box(xx - 9.4, xy - 11, xx + 9.4, xy + 11))      # XIAO (基板の裏で一番低い部品)
        sxp, syp, dp = cu.PWR[side]
        avoid.append(box(min(sxp - dp * 0.5, sxp + dp * 6), syp + cu.SWC_V0 - 0.1,
                         max(sxp - dp * 0.5, sxp + dp * 6), syp + cu.SWC_V1 + 0.1))   # 電源スイッチのカバー
        for x, y in cu.magnet_spots(side):
            boss = Point(x, y).buffer(cu.MAG_BOSS_R)
            rub = Point(x, y).buffer(cu.RUBBER_D / 2 + 0.15)
            if not o.buffer(-0.8).contains(rub) or any(boss.intersects(a) for a in avoid):
                problems.append(f"{side}: 磁石 ({x:.1f}, {y:.1f}) がほかの部品・穴・溝に近すぎる")
        if not o.buffer(-4.5).contains(Point(mx, my).buffer(cu.MAG_OD / 2 + cu.MAG_GAP)):
            problems.append(f"{side}: MagSafe の溝が壁に近すぎる")
    # 基板のナット (Ergogen の config.yaml) と、トレイの柱の位置が同じか
    sys.path.insert(0, os.path.join(HERE, "..", "tools"))
    import check_pcb
    for side in ("left", "right"):
        pcbf = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
        root = check_pcb.parse(open(pcbf, encoding="utf-8").read())
        nuts = sorted((round(float(check_pcb.find(m, "at")[1]), 2), round(-float(check_pcb.find(m, "at")[2]), 2))
                      for m in check_pcb.find_all(root, "module") if "SMT_Nut" in check_pcb.unq(m[1]))
        posts = sorted((round(x, 2), round(y, 2)) for x, y in cu.POSTS[side])
        if len(nuts) != len(posts) or any(math.dist(a, b) > 0.05 for a, b in zip(nuts, posts)):
            problems.append(f"{side}: 基板のナットとトレイの柱の位置が合わない")
    # 電源スイッチのカバー・つまみ、nice!view のカバー
    for side in ("left", "right"):
        p = cu.half(side, 34 if side == "right" else 25)
        low = p["pcb"].translate([0, 0, -cu.TRAVEL])        # キーを押して基板が一番沈んだ時
        if (p["tray"] ^ low).volume() > 0.01:
            problems.append(f"{side}: 基板が沈むとトレイ (電池の目隠しなど) に当たる")
        # 基板の裏のソケット: 止まっている時も、基板が一番沈んだ時も、トレイ・柱・ポロン・カバーなどに当たらないか
        so = p.get("sockets")
        if so is None:
            problems.append(f"{side}: ソケットの形が読めない (先に Ergogen を実行)")
        else:
            for dz, when in ((0, "止まっている時"), (-cu.TRAVEL, "基板が一番沈んだ時")):
                sz = so.translate([0, 0, dz])
                for name, label in (("tray", "トレイ"), ("posts", "柱"), ("gasket", "ポロン"), ("battery", "電池"),
                                    ("switch_cover", "電源スイッチのカバー"), ("slider", "つまみ"),
                                    ("ball_base", "ボールユニット"), ("ball_cup", "カップ"), ("screws", "ネジ・カラー")):
                    if name in p and (sz ^ p[name]).volume() > 0.01:
                        problems.append(f"{side}: ソケットが{label}に当たる ({when})")
        # 基板の裏のすべての部品 (XIAO・コネクタ・ナット・ダイオード・足): 一番沈んだ時もトレイなどに当たらないか
        bat_tol = p["battery"].translate([0, 0, 0]) + k.cube(*[v for v in p["battery"].bounding_box()][:2],
                                                              cu.BATTERY_SKIN, *[v for v in p["battery"].bounding_box()][3:5],
                                                              cu.BATTERY_SKIN + cu.BATTERY_T + cu.BATTERY_TOL)
        for ref, solid in cu.back_parts(side).items():
            low_s = solid.translate([0, 0, -cu.TRAVEL])
            for name in ("tray", "gasket", "switch_cover", "slider", "ball_base", "ball_cup", "screws", "magnets"):
                if ref.startswith("H") and name in ("gasket", "screws"):
                    continue                               # ナットはポロンの輪の中・ネジがねじ込まれる (設計どおり)
                if name in p and (low_s ^ p[name]).volume() > 0.01:
                    problems.append(f"{side}: 基板の裏の部品 {ref} が {name} に当たる (一番沈んだ時)")
            if (low_s ^ bat_tol).volume() > 0.01:
                problems.append(f"{side}: 基板の裏の部品 {ref} が電池 (厚めの電池) に当たる")
            if not ref.startswith("H") and (low_s ^ p["posts"]).volume() > 0.01:
                problems.append(f"{side}: 基板の裏の部品 {ref} が柱に当たる")
        # 電池の上のソケット: 基板が一番沈んでも電池に当たらないか
        sock_bottom = cu.PCB_B - 1.85 - cu.TRAVEL
        if sock_bottom < cu.BATTERY_SKIN + cu.BATTERY_T + cu.BATTERY_TOL + 0.05:
            problems.append(f"{side}: 基板が沈むとソケットが電池に当たる ({sock_bottom:.2f}mm)")
        for a, b, label in (("switch_cover", "pcb", "基板"), ("switch_cover", "plate", "プレート"),
                            ("switch_cover", "tray", "トレイ"), ("slider", "switch_cover", "カバー"),
                            ("slider", "pcb", "基板"), ("view_cover", "plate", "プレート"),
                            ("view_cover", "pcb", "基板"), ("view_cover", "ball_base", "ボールユニット")):
            if b in p and (p[a] ^ p[b]).volume() > 0.01:
                problems.append(f"{side}: {a} が {label} に当たる")
        if (p["switch_cover"] ^ low).volume() > 0.01 or (p["slider"] ^ low).volume() > 0.01:
            problems.append(f"{side}: 基板が沈むとスイッチのカバーに当たる")
        for pos in (-cu.SW_POS, cu.SW_POS):              # レバーの両方の位置で、つまみがレバーをつかめるか
            lever = cu._pwr_place(side, cu._uv_cube(1.6, cu.SW_LEVER_TIP, pos - 0.65, pos + 0.65,
                                                     cu.SW_LEVER_Z0, cu.SW_LEVER_Z1))
            sl = p["slider"].translate([0, pos, 0])
            if (sl ^ lever).volume() > 0.01 or (sl ^ p["switch_cover"]).volume() > 0.01:
                problems.append(f"{side}: つまみがレバーの位置 {pos:+.2f} で動けない")
            # 基板を留めたあと、カバー (つまみ付き) を横から差し込めるか
            sx, sy, d = cu.PWR[side]
            for du in (6.0, 4.0, 2.0, 1.0, 0.5):
                mv = [d * du, pos * 0, 0]
                unit = (p["switch_cover"] + sl).translate(mv)
                for name in ("pcb", "plate", "view_cover", "tray"):
                    if (unit ^ p[name]).volume() > 0.01:
                        problems.append(f"{side}: カバーを横から差し込む途中 ({du}mm) で {name} に当たる")
                if (sl.translate(mv) ^ lever).volume() > 0.01:
                    problems.append(f"{side}: 差し込む途中でフォークがレバーに当たる ({du}mm)")
    # ボールユニット: キー・基板・プレート・トレイに当たらないか (カバーを回してロックする途中も)
    tr = tray("right")
    for size in (19, 25, 34):
        p = cu.half("right", 34 if size == 34 else 25)
        T = cu.size_tilt(size)
        cover, _ = cu.claw_cover(size)
        for d in (0, 15, 30):
            cc = cu.unit_place(cover.rotate([0, 0, d]), T)
            for name in ("caps", "plate", "pcb", "view", "view_cover"):
                for dz in (0, -3) if name == "caps" else (0,):
                    if (cc ^ p[name].translate([0, 0, dz])).volume() > 0.01:
                        problems.append(f"{size}mm: カバーが {name} に当たる (回す角度 {d}°)")
            if (cc ^ tr).volume() > 0.01:
                problems.append(f"{size}mm: カバーがトレイ (受け) に当たる (回す角度 {d}°)")
        cup_l = cu.cup34() if size == 34 else cu.cup_unit(size)
        cup = cu.unit_place(cup_l, T)
        # ボールユニットのロック: 差し込む位置 (-20°) で上から入り、ひねる途中も当たらない (最後の山だけは乗り越える)
        for dz in (6.0, 3.0, 1.0, 0.0):
            v = (cu.unit_place(cup_l.rotate([0, 0, -cu.UNIT_TURN]).translate([0, 0, dz]), T) ^ tr).volume()
            if v > 0.01:
                problems.append(f"{size}mm: ユニットを差し込む途中 ({dz}mm 上) で受けに当たる ({v:.2f})")
        for d in (-15, -10, -5):
            v = (cu.unit_place(cup_l.rotate([0, 0, d]), T) ^ tr).volume()
            if v > 0.6:
                problems.append(f"{size}mm: ユニットをひねる途中 ({d}°) で受けに当たる ({v:.2f})")
        for name in ("caps", "plate", "pcb", "posts", "screws", "battery", "view_cover", "sockets"):
            if name in p and (cup ^ p[name]).volume() > 0.01:
                problems.append(f"{size}mm: カップが {name} に当たる")
        if (cup ^ tr).volume() > 0.01:
            problems.append(f"{size}mm: カップがトレイの受けに当たる ({(cup ^ tr).volume():.2f})")
        ball = cu.unit_place(mf.Manifold.sphere(bu.CUPS[size]["R"], 96).translate([0, 0, bu.BALL_BOTTOM + bu.CUPS[size]["R"]]), T)
        if (ball ^ tr).volume() > 0.01 or (ball ^ cup).volume() > 0.01:
            problems.append(f"{size}mm: ボールが受け・カップに当たる")
        # センサー基板: 受け (くぼみ・ツメ) とカップに食い込まないか、カップの足が届いているか、下の床が残るか
        sen = cu.unit_place(cu.sensor_model(), T)
        for name, o in (("トレイの受け", tr), ("カップ", cup)):
            if (sen ^ o).volume() > 0.01:
                problems.append(f"{size}mm: センサー基板が{name}に当たる ({(sen ^ o).volume():.2f})")
        if (sen.translate([0, 0, 0.3]) ^ cup).volume() < 0.01:
            problems.append(f"{size}mm: カップの足がセンサー基板を押さえていない")
        if sen.bounding_box()[2] < cu.LOWER_SKIN - 0.05:
            problems.append(f"{size}mm: センサー基板の下の床が薄すぎる")
    # センサー基板を留めるツメが基板の上にかかっているか (基板を 0.2mm 持ち上げると当たる)
    _, _, clips = cu.socket()
    if (cu.unit_place(cu.sensor_model()).translate([0, 0, 0.25]) ^ clips).volume() < 0.001:
        problems.append("センサー基板を留めるツメが基板にかかっていない")
    return problems


def main():
    out = os.path.join(HERE, "stl", "ukishima")
    os.makedirs(out, exist_ok=True)
    items = {
        "tray_left": tray("left"),
        "tray_right": tray("right"),
        "ball_cup_25": cu.cup_unit(25),
        "ball_cup_19": cu.cup_unit(19),
        "ball_cover_25": cu.claw_cover(25)[0],
        "ball_cover_19": cu.claw_cover(19)[0],
        "ball_cup_34": cu.cup34(),
        "ball_hood_34": cu.claw_cover(34)[0],
        "switch_cover_left": on_bed(cu.switch_cover("left"), (0, 90, 0)),      # 外の面を下
        "switch_cover_right": on_bed(cu.switch_cover("right"), (0, -90, 0)),
        "switch_slider": on_bed(cu.switch_slider("left"), (180, 0, 0)),        # つまみを下
        "view_cover_left": on_bed(cu.view_cover("left"), (180, 0, 0)),         # 上の面を下
        "view_cover_right": on_bed(cu.view_cover("right"), (180, 0, 0)),
    }
    for name, m in items.items():
        n = len(m.decompose())
        if n != 1:
            sys.exit(f"{name}: 1 つにつながっていない ({n} 個に分かれている)")
        k.save_stl(m, os.path.join(out, f"{name}.stl"))
        print(f"  {name}.stl  ({m.volume() / 1000:.1f} cm³)")
    problems = check()
    for p in problems:
        print("  ×", p)
    print("確認: 問題なし" if not problems else f"確認: 問題 {len(problems)} 件")
    print(f"高さ: 床 {cu.FLOOR} / トレイの縁 {cu.RIM:.2f} / 基板 {cu.PCB_B:.2f}〜{cu.PCB_T:.2f} / "
          f"プレート上 {cu.PLATE_T:.2f} / キーキャップ上 約 {cu.KEY_TOP:.1f}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
