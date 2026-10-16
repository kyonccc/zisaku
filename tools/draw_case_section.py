"""ケース (ガスケットマウント) の断面図を、実際の 3D データを切って SVG で描く。

使い方 (リポジトリの一番上で): python3 tools/draw_case_section.py docs/images
case/kataware_case.py と同じ寸法を使う。
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case"))
import kataware_case as k  # noqa: E402
import ball_unit as bu  # noqa: E402
import manifold3d as mf  # noqa: E402

U = k.U
C = {"bg": "#f7f7f5", "ink": "#333", "sub": "#666", "bottom": "#c9ccd1", "top": "#e8e2d4", "pcb": "#2f7d45",
     "plate": "#3a3a3a", "gasket": "#f19ca6", "switch": "#9aa0a6", "cap": "#ffffff", "xiao": "#1b5e20",
     "usb": "#90a4ae", "bat": "#b0b6bb", "pwr": "#f0a500", "base": "#aeb4bc", "cup": "#f3ede2",
     "brg": "#d4a017", "ball": "#c0392b", "lens": "#5d6d7e", "screw": "#1a5276", "cover": "#d9d4c7"}


def parts(side):
    bottom, top = k.build(side)
    out = [("bottom", bottom), ("top", top),
           ("pcb", k.prism(k.load(f"pcb_{side}"), k.PCB_B, k.PCB_T)),
           ("plate", k.prism(k.load(f"plate_{side}"), k.PLATE_B, k.PLATE_T))]
    tabs, cav = k.load(f"tabs_{side}"), k.load(f"cavity_{side}")
    g = tabs.intersection(cav.buffer(3.0, join_style=2)).difference(cav.buffer(0.75, join_style=2))
    out += [("gasket", k.prism(g, k.SPLIT, k.PLATE_B)), ("gasket", k.prism(g, k.PLATE_T, k.CEIL))]
    return out


def keys(side):
    if side == "left":
        pts = [(c*U, r*U) for c in range(5) for r in range(4)] + [(5*U, 0), (5*U, 2*U), (5*U, 3*U), (6*U, 0)]
    else:
        pts = [(k.RIGHT_X + i*U, r*U) for i in range(1, 6) for r in range(4)] + [(k.RIGHT_X, 2*U), (k.RIGHT_X, 3*U)]
    sw = k.union([k.cube(x - 6.9, y - 6.9, k.PLATE_T, x + 6.9, y + 6.9, k.PLATE_T + 3) for x, y in pts])
    sw = sw + k.union([k.cube(x - 6.9, y - 6.9, k.PLATE_B - 0.8, x + 6.9, y + 6.9, k.PLATE_B) for x, y in pts])
    cap = k.union([k.cube(x - 9, y - 9, k.PLATE_T + 4, x + 9, y + 9, k.PLATE_T + 7.5) for x, y in pts])
    return [("switch", sw), ("cap", cap)]


def section(items, plane, at, window, title, labels, px=12.0, extra=(), overlay=None):
    """plane='x' なら x=at の面 (横軸 y)、'y' なら y=at の面 (横軸 x) で切る。
    plane='az' なら at=(x, y, 向き) を通る縦の面 (横軸 = その向き、点 (x, y) が 0)"""
    if plane == "az":
        cx, cy, deg = at
        c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        mat = [[c, s_, 0, -(c*cx + s_*cy)], [0, 0, 1, 0], [s_, -c, 0, -(s_*cx - c*cy)]]
        z = 0
        at = deg
    elif plane == "x":
        mat = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]
        z = at
    else:
        mat = [[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0]]
        z = -at
    (u0, u1), (v0, v1) = window
    W, H = int((u1 - u0)*px) + 460, int((v1 - v0)*px) + 110

    def X(u):
        return 30 + (u - u0)*px

    def Y(v):
        return 80 + (v1 - v)*px

    o = [f'<text x="30" y="34" font-size="22" font-weight="bold" fill="{C["ink"]}">{title}</text>',
         f'<clipPath id="w{plane}{int(at)}"><rect x="30" y="80" width="{(u1-u0)*px:.0f}" height="{(v1-v0)*px:.0f}"/></clipPath>',
         f'<g clip-path="url(#w{plane}{int(at)})">']
    for name, m in list(items) + list(extra):
        cs = m.transform(mat).slice(z)
        for poly in cs.to_polygons():
            d = "M" + " L".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in poly) + " Z"
            o.append(f'<path d="{d}" fill="{C[name]}" stroke="{C["ink"]}" stroke-width="1" fill-rule="evenodd"/>')
    if overlay:
        o.append(overlay(X, Y))
    o.append("</g>")
    o.append(f'<line x1="30" y1="{Y(0):.1f}" x2="{X(u1):.1f}" y2="{Y(0):.1f}" stroke="{C["ink"]}" stroke-width="2"/>')
    for u, v, t, (lu, lv) in labels:
        o.append(f'<line x1="{X(u):.1f}" y1="{Y(v):.1f}" x2="{X(lu):.1f}" y2="{Y(lv):.1f}" stroke="{C["sub"]}" stroke-width="1"/>'
                 f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="2.5" fill="{C["sub"]}"/>'
                 f'<text x="{X(lu)+6:.1f}" y="{Y(lv)+5:.1f}" font-size="16" fill="{C["ink"]}">{t}</text>')
    return W, H, "".join(o)


def svg(W, H, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="IPAPGothic, IPAGothic, sans-serif"><rect width="100%" height="100%" fill="{C["bg"]}"/>{body}</svg>')


def main(out):
    left = parts("left") + keys("left")
    # ① 上の壁の耳 (x = 24.15 で切る。右が奥)
    L = k.U*3.5
    labels = [
        (L + 3.2, k.TOP - 0.5, "上ケース", (L + 9.5, 17.5)),
        (L + 1.8, k.CEIL - 0.5, "上のガスケット（ポロン 1.5mm）", (L + 9.5, 15.0)),
        (L + 1.5, k.PLATE_B + 0.6, "プレートの耳（ここだけ壁に入る）", (L + 9.5, 12.5)),
        (L + 1.8, k.SPLIT + 0.5, "下のガスケット", (L + 9.5, 10.0)),
        (L - 2, k.PCB_B + 0.8, "基板（壁から 0.75mm 離す）", (L + 9.5, 7.5)),
        (L + 2.5, 5, "下ケース", (L + 9.5, 5.0)),
        (L - 6, k.PLATE_T + 5.5, "キーキャップ", (L + 9.5, 20.0)),
    ]
    W1, H1, b1 = section(left, "x", 24.15, ((L - 16, L + 6), (-1, 22)),
                         "① 耳のところの断面（プレートの耳をガスケットで上下から挟む）", labels, px=22)
    # ② 内側の側面 (y = 37 で切る): XIAO と USB-C
    ix = 6.5*U
    xiao = k.cube(ix - 18.5, 37 - 8.9, k.PCB_B - 4.5, ix + 2.5, 37 + 8.9, k.PCB_B - 1.2)
    usb = k.cube(ix - 5, 37 - 4.5, k.PCB_B - 4.5, ix + 2.5, 37 + 4.5, k.PCB_B - 1.2)
    labels2 = [
        (ix + 1.5, k.PCB_B + 0.8, "基板の舌（壁の溝に入る）", (ix + 9.5, 12.5)),
        (ix - 6, k.PCB_B - 2.5, "XIAO（基板の裏）", (ix + 9.5, 9.5)),
        (ix + 2.0, k.PCB_B - 3.2, "USB-C → 側面の穴から挿す", (ix + 9.5, 6.5)),
        (ix - 10, 1.2, "底板 2.5mm", (ix + 9.5, 3.0)),
    ]
    W2, H2, b2 = section(left, "y", 37, ((ix - 22, ix + 6), (-1, 22)),
                         "② 内側の側面の断面（XIAO の USB-C）", labels2, px=22,
                         extra=[("xiao", xiao), ("usb", usb)])
    # ③ ボールユニット (右手。ボールの中心を通る前後の断面。右が奥)
    right = parts("right") + keys("right")
    bx, by = k.HALVES["right"]["ball"]
    z0 = k.FLOOR

    def at(m):
        return m.translate([bx, by, z0])
    size = 25
    cup, info = bu.cup(size)
    sensor = k.cube(-bu.SENSOR_W/2, -bu.SENSOR_L/2, bu.BASE_FLOOR - bu.SENSOR_POCKET, bu.SENSOR_W/2, bu.SENSOR_L/2, bu.SENSOR_TOP)
    lens = k.cube(-3.5, -4.5, bu.SENSOR_TOP, 3.5, 4.5, bu.SENSOR_TOP + bu.LENS_H)
    ball = mf.Manifold.sphere(bu.CUPS[size]["R"], 96).translate([0, 0, info["cz"]])
    screws = k.union([k.cyl(0, -k.BALL_SCREW_R, -z0, bu.INSERT_DEPTH - 0.5, 1.0),
                      k.cyl(0, -k.BALL_SCREW_R, -z0, -z0 + 1.2, 2.0, 1.0)])
    unit = [("base", at(bu.base())), ("cup", at(cup)), ("pcb", at(sensor)), ("lens", at(lens)),
            ("brg", at(bu.bearings(size))), ("ball", at(ball)), ("screw", at(screws)),
            ("cover", at(bu.cover(size)[0]))]
    zc = z0 + info["cz"]
    labels3 = [
        (by + 12.5*0.6, zc + 7, "ボール 25mm", (by + 26, 36)),
        (by + 15.5, z0 + 25, "カバー（磁石で付く。縁がボールを押さえる）", (by + 26, 32)),
        (by + 16, z0 + 14.5, "カップ（25mm 用・19mm 用を差し替え）", (by + 26, 30)),
        (by + 11, z0 + info["brg_z"], "ベアリング 681X ＋ ピン（3か所）", (by + 26, 28)),
        (by - 16.2, z0 + 11, "土台（ケースに固定したまま）", (by + 26, 24)),
        (by + 3, z0 + bu.SENSOR_TOP + 1.5, "PMW3610 センサー（すき間 2.4mm）", (by + 26, 20)),
        (by + 21, k.PCB_B + 0.8, "基板（穴 36mm・ユニットに触れない）", (by + 26, 16)),
        (by + 16.2, z0 + 3, "センサーのケーブルの出口（奥）", (by + 26, 12)),
        (by - k.BALL_SCREW_R, 0.6, "底から皿ネジ M2 → 土台のインサート", (by + 26, 8)),
    ]
    W3, H3, b3 = section(right, "x", bx, ((by - 22, by + 25), (-1, 40)),
                         "③ ボールユニットの断面（25mm。右が奥）", labels3, px=13, extra=unit)
    open(f"{out}/ballunit-section.svg", "w").write(svg(W3, H3, b3))

    # ④ 親指の来る向きの断面 (右が親指側 = Enter の方)
    th = bu.THUMB_FROM
    lo = k.FLOOR + bu.cover_z(size, bu.UNIT_R, th)
    hi = k.FLOOR + bu.cover_z(size, bu.UNIT_R, th + 180)
    key_top = k.PLATE_T + 7.5

    g = bu.cover_geometry(size)
    ta = math.radians(bu.COVER_TILT)

    def plane_z(u):                                         # カバー上面 (斜めの部分) の高さ
        return z0 + g["cz"] + (g["h_top"] - math.sin(ta)*u)/math.cos(ta)
    hl = g["hs"] + bu.LIP_LAND
    lip_u, lip_z = hl*math.sin(ta) + g["r_open"]*math.cos(ta), zc + hl*math.cos(ta) - g["r_open"]*math.sin(ta)

    def thumb(X, Y):
        R_ = bu.CUPS[size]["R"]
        a, b = math.radians(55), math.radians(12)           # 親指の腹が当たる所 (ボールの右上 55°)・親指の向き
        cx_ = R_*math.cos(a) - 7.5*math.sin(b) + 14*math.cos(b)    # 親指の楕円の下側がボールに触れる位置
        cy_ = zc + R_*math.sin(a) + 7.5*math.cos(b) + 14*math.sin(b)
        t = (f'<ellipse cx="{X(cx_):.1f}" cy="{Y(cy_):.1f}" rx="{30*12:.0f}" ry="{8.5*12:.0f}" '
             f'transform="rotate({-math.degrees(b):.1f} {X(cx_):.1f} {Y(cy_):.1f})" fill="#e8b89a" fill-opacity="0.4" '
             f'stroke="#b5785a" stroke-width="2" stroke-dasharray="8 5"/>')
        u0_, u1_ = -14, 16
        t += (f'<line x1="{X(u0_):.1f}" y1="{Y(plane_z(u0_) + 1.2):.1f}" x2="{X(u1_):.1f}" y2="{Y(plane_z(u1_) + 1.2):.1f}" '
              f'stroke="#b03a2e" stroke-width="2" stroke-dasharray="6 4"/>'
              f'<line x1="{X(u1_):.1f}" y1="{Y(plane_z(u1_) + 1.2):.1f}" x2="{X(u1_ - 12):.1f}" y2="{Y(plane_z(u1_) + 1.2):.1f}" '
              f'stroke="#b03a2e" stroke-width="1.2"/>'
              f'<text x="{X(u1_ - 10):.1f}" y="{Y(plane_z(u1_) + 2.0):.1f}" font-size="18" fill="#b03a2e">{bu.COVER_TILT:.0f}°</text>')
        t += (f'<line x1="{X(-22):.1f}" y1="{Y(key_top):.1f}" x2="{X(48):.1f}" y2="{Y(key_top):.1f}" '
              f'stroke="#888" stroke-width="1" stroke-dasharray="3 4"/>')
        return t
    labels4 = [
        (28, zc + 17, "親指（Enter から左へ滑らせ、ボールの右上を転がす）", (50, 42)),
        (16.5, lo - 0.5, f"親指側の縁：机から約{lo:.0f}mm（キーキャップとほぼ同じ）", (50, 34)),
        (-16.5, hi - 0.5, f"奥側：約{hi:.0f}mm（背もたれ・飛び出し防止）", (50, 30)),
        (lip_u, lip_z, "縁はボールより 0.8mm 内側 → 抜けない", (50, 26)),
        (29, key_top - 0.5, f"キーキャップの上（約{key_top:.0f}mm）", (50, 20)),
    ]
    W4, H4, b4 = section(right, "az", (bx, by, th), ((-22, 48), (-1, 46)),
                         f"④ 親指の来る向きの断面（右が親指側・Enter の方。カバーの傾き {bu.COVER_TILT:.0f}°）",
                         labels4, px=12, extra=unit, overlay=thumb)
    open(f"{out}/ballunit-thumb.svg", "w").write(svg(W4, H4, b4))
    open(f"{out}/case-section-tab.svg", "w").write(svg(W1, H1, b1))
    open(f"{out}/case-section-usb.svg", "w").write(svg(W2, H2, b2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/images")
