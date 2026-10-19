"""浮島 (うきしま) の製作用 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    pip install manifold3d shapely ezdxf
    npx ergogen@4.1.0 pcb/ergogen -o pcb/ergogen/output   # 先に外形を作る
    python3 case/ukishima.py

できるもの (case/stl/ukishima/):
    tray_left.stl / tray_right.stl   … トレイ (床・低い枠・柱 8 本・MagSafe の溝・電池のくぼみ)
    ball_base.stl                    … 19 / 25mm 共用の土台 (センサー入り・トレイに 3 本のネジで留める)
    ball_cup_25.stl / ball_cup_19.stl       … カップ (ベアリング 3 個)
    ball_cover_25.stl / ball_cover_19.stl   … 爪留めカバー (ひねってロック)
    ball_base_34.stl                 … 34mm 専用の受け (土台とカップが一体・固定の爪つき)
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_ukishima as cu  # noqa: E402

k, bu = cu.k, cu.bu
U = k.U
BATTERY, BAT_W, BAT_H = cu.BATTERY, cu.BAT_W, cu.BAT_H

# ===== ボールユニットをトレイに留める耳 (3 か所) =====
# 土台は床の穴 (半径 18) に落とし込み、外の「耳」を床の上に乗せて、床の裏から皿ネジ M2 で留める (耳にインサート)
TAB_ANGLES = (150, 225, 300)      # 基板の裏の部品 (XIAO・コネクタ・ソケット) をよけた向き
TAB_R0, TAB_R1 = 16.5, 22.5       # 耳の内側・外側 (半径)
TAB_SCREW_R = 20.0                # ネジの位置 (ユニット中心から)
TAB_W = 7.0                       # 耳の幅
TAB_H = bu.INSERT_DEPTH + 0.6     # 耳の高さ (床の上から)
BALL_HOLE_R = max(bu.UNIT_R, cu.U34_R) + 0.3     # 床の穴 (34mm の受けも入る)

# ===== トレイの穴・ゴム足 =====
USB_W = 14.0                      # USB-C のプラグが入る切り欠きの幅
FOOT_R, FOOT_D = 5.25, 0.6        # ゴム足 (直径 10mm) のくぼみ
FEET = {"left": [(-4.0, -4.0), (118.5, -4.0), (-4.0, 61.0), (118.5, 61.0)],
        "right": [(196.0, 61.0), (318.5, 61.0), (318.5, 26.0), (250.0, -6.0), (285.0, -7.0)]}


def tab_ring(z0):
    """耳 (土台の外側)。z0 = 床の上面"""
    tabs = []
    for a in TAB_ANGLES:
        half = math.degrees(TAB_W / 2 / TAB_SCREW_R)
        t = bu.sector(TAB_R0, TAB_R1, a - half, a + half, z0, z0 + TAB_H)
        x, y = bu.polar(TAB_SCREW_R, a)
        t = t - k.cyl(x, y, z0 - 1, z0 + bu.INSERT_DEPTH, bu.INSERT_R)      # 下からインサート M2
        tabs.append(t)
    return k.union(tabs)


def ball_base():
    return bu.base() + tab_ring(cu.FLOOR)


def ball_base_34():
    b, _ = cu.base34()
    return b + tab_ring(cu.FLOOR)


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
    for fx, fy in FEET[side]:
        cut.append(k.cyl(fx, fy, -1, FOOT_D, FOOT_R))
    if h["ball"]:
        bx, by = h["ball"]
        cut.append(k.cyl(bx, by, -1, cu.FLOOR + 1, BALL_HOLE_R))
        for a in TAB_ANGLES:
            x, y = bu.polar(TAB_SCREW_R, a)
            cut += [k.cyl(bx + x, by + y, -1, cu.FLOOR + 1, 1.15), k.cyl(bx + x, by + y, -0.01, 1.2, 2.2, 1.0)]
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
        avoid = [ring, bat.buffer(1)] + [Point(p).buffer(2.8 + 1) for p in cu.POSTS[side]]
        if h["ball"]:
            bx, by = h["ball"]
            avoid.append(Point(bx, by).buffer(TAB_R1 + 1))
        for f in FEET[side]:
            c = Point(f).buffer(FOOT_R)
            if not o.buffer(-0.8).contains(c) or any(c.intersects(a) for a in avoid):
                problems.append(f"{side}: ゴム足 {f} がほかの穴や溝に近すぎる")
        if not o.buffer(-4.5).contains(Point(mx, my).buffer(cu.MAG_OD / 2 + cu.MAG_GAP)):
            problems.append(f"{side}: MagSafe の溝が壁に近すぎる")
        if h["ball"]:
            # 耳 (高さ 床+4.6mm) が基板の裏の部品 (ソケット・XIAO・コネクタ) の下に来ないか
            sys.path.insert(0, os.path.join(HERE, "..", "tools"))
            import check_pcb
            pcbf = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs", f"{side}.kicad_pcb")
            from shapely import affinity
            for ref, name, shp in check_pcb.back_bodies(pcbf):
                shp = affinity.scale(shp, 1, -1, origin=(0, 0))            # KiCad (y 下向き) → y 上向き
                for a in TAB_ANGLES:
                    half = math.degrees(TAB_W / 2 / TAB_SCREW_R)
                    pts = [bu.polar(r, a + s_) for r in (TAB_R0, TAB_R1) for s_ in (-half, half)]
                    tab = box(0, 0, 0, 0).union(
                        __import__("shapely.geometry", fromlist=["MultiPoint"]).MultiPoint(
                            [(bx + x, by + y) for x, y in pts]).convex_hull)
                    if tab.buffer(0.5).intersects(shp):
                        problems.append(f"耳 {a}° が基板の裏の部品 {ref} の下に来る")
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
        low = p["pcb"].translate([0, 0, -0.7])              # キーを押して基板が沈んだ時
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
    # ボールユニット: キー・基板・プレートに当たらないか (回してロックする途中も)
    for size in (25, 34):
        p = cu.half("right", size)
        bx, by = k.HALVES["right"]["ball"]
        cover, _ = cu.claw_cover(size)
        base = ball_base_34() if size == 34 else ball_base()
        for d in (0, 15, 30):
            cc = cover.rotate([0, 0, d]).translate([bx, by, 0])
            for name in ("caps", "plate", "pcb", "view"):
                for dz in (0, -3) if name == "caps" else (0,):
                    if (cc ^ p[name].translate([0, 0, dz])).volume() > 0.01:
                        problems.append(f"{size}mm: カバーが {name} に当たる (回す角度 {d}°)")
        bb = base.translate([bx, by, 0])
        for name in ("caps", "plate", "pcb", "posts", "screws", "battery"):
            if (bb ^ p[name]).volume() > 0.01:
                problems.append(f"{size}mm: 受けが {name} に当たる")
        if (bb ^ tray("right")).volume() > 0.01:
            problems.append(f"{size}mm: 受けがトレイに当たる")
    return problems


def main():
    out = os.path.join(HERE, "stl", "ukishima")
    os.makedirs(out, exist_ok=True)
    items = {
        "tray_left": tray("left"),
        "tray_right": tray("right"),
        "ball_base": ball_base(),
        "ball_cup_25": bu.cup(25)[0],
        "ball_cup_19": bu.cup(19)[0],
        "ball_cover_25": cu.claw_cover(25)[0],
        "ball_cover_19": cu.claw_cover(19)[0],
        "ball_base_34": ball_base_34(),
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
    print(f"高さ: 床 {cu.FLOOR} / トレイの縁 {cu.RIM:.1f} / 基板 {cu.PCB_B:.2f}〜{cu.PCB_T:.2f} / "
          f"プレート上 {cu.PLATE_T:.2f} / キーキャップ上 約 {cu.KEY_TOP:.1f}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
