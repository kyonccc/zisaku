"""Ergogen で作った基板 (.kicad_pcb) の簡単な検査。

使い方 (リポジトリの一番上で): python3 tools/check_pcb.py

調べること:
  1. ちがう部品のパッド (銅) どうしが 0.2mm より近くないか (同じつながりは除く)
  2. パッドが基板の外形から 0.3mm 以上内側にあるか
  3. 基板の裏の部品どうしが重ならないか (部品の外形 = コートヤード。ソケットはパッドのまわり)
  4. 浮島: 電池の上に背の高い部品 (XIAO・コネクタ・ナット) が来ていないか
KiCad の DRC (デザインルールチェック) の代わりではない。KiCad でも必ず DRC をすること。
"""
import math
import os
import sys

from shapely import affinity
from shapely.geometry import MultiPoint, Point, Polygon, box

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "case"))
from import_footprints import find, find_all, parse, unq  # noqa: E402
import kataware_case  # noqa: E402
import ukishima  # noqa: E402

PCBS = os.path.join(HERE, "..", "pcb", "ergogen", "output", "pcbs")
GAP, EDGE = 0.2, 0.3


def pad_shapes(path):
    root = parse(open(path, encoding="utf-8").read())
    res = []
    for m in find_all(root, "module"):
        at = find(m, "at")
        X, Y = float(at[1]), float(at[2])
        r = float(at[3]) if len(at) > 3 else 0.0
        refs = [unq(t[2]) for t in find_all(m, "fp_text") if t[1] == "reference"]
        ref = refs[0] if refs else unq(m[1])
        rr = math.radians(r)
        for p in find_all(m, "pad"):
            a = find(p, "at")
            x, y = float(a[1]), float(a[2])
            pr = float(a[3]) if len(a) > 3 else r
            w, h = (float(v) for v in find(p, "size")[1:3])
            gx = X + x*math.cos(rr) + y*math.sin(rr)
            gy = Y - x*math.sin(rr) + y*math.cos(rr)
            if p[3] == "circle":
                shp = Point(gx, gy).buffer(w/2)
            else:
                shp = affinity.rotate(box(gx - w/2, gy - h/2, gx + w/2, gy + h/2), -pr, origin=(gx, gy))
            cu = set()
            for layer in (unq(v) for v in find(p, "layers")[1:]):
                if layer == "*.Cu" or p[2] == "np_thru_hole":
                    cu |= {"F", "B"}
                elif layer in ("F.Cu", "B.Cu"):
                    cu.add(layer[0])
            net = find(p, "net")
            res.append((ref, unq(p[1]), cu, shp, unq(net[2]) if net else "", p[2]))
    return res


def back_bodies(path):
    """基板の裏の部品の外形 (KiCad の座標)。コートヤードがあればそれ、無ければ裏のパッドのまわり"""
    root = parse(open(path, encoding="utf-8").read())
    res = []
    for m in find_all(root, "module"):
        is_socket = "choc" in unq(m[1]).lower() or "hotswap" in unq(m[1]).lower()
        if unq(find(m, "layer")[1]) != "B.Cu" and not is_socket:   # スイッチの部品は表扱いだが、ソケットは裏
            continue
        at = find(m, "at")
        X, Y = float(at[1]), float(at[2])
        rr = math.radians(float(at[3]) if len(at) > 3 else 0.0)
        refs = [unq(t[2]) for t in find_all(m, "fp_text") if t[1] == "reference"]
        ref = refs[0] if refs else unq(m[1])

        def g(x, y):
            return (X + x*math.cos(rr) + y*math.sin(rr), Y - x*math.sin(rr) + y*math.cos(rr))
        pts = []
        for ln in find_all(m, "fp_line"):
            if unq(find(ln, "layer")[1]) == "B.CrtYd":
                for key in ("start", "end"):
                    q = find(ln, key)
                    pts.append(g(float(q[1]), float(q[2])))
        for c in find_all(m, "fp_circle"):
            if unq(find(c, "layer")[1]) == "B.CrtYd":
                cc, e = find(c, "center"), find(c, "end")
                r = math.dist((float(cc[1]), float(cc[2])), (float(e[1]), float(e[2])))
                res.append((ref, unq(m[1]), Point(g(float(cc[1]), float(cc[2]))).buffer(r)))
        if pts:
            res.append((ref, unq(m[1]), MultiPoint(pts).convex_hull))
        elif is_socket:
            # Kailh Choc ホットスワップソケット (CPG135001S30) の樹脂の本体のおおよその形 (部品の座標)
            sm = [g(x, y) for x, y in SOCKET_BODY]
            for pd in find_all(m, "pad"):
                if pd[2] == "smd":
                    a = find(pd, "at")
                    w, h = (float(v) for v in find(pd, "size")[1:3])
                    x, y = float(a[1]), float(a[2])
                    sm += [g(x + dx, y + dy) for dx in (-w/2, w/2) for dy in (-h/2, h/2)]
            if sm:
                res.append((ref, "socket", MultiPoint(sm).convex_hull.buffer(0.3)))
    return res


SOCKET_BODY = [(-2.0, -4.25), (-2.0, -7.7), (-1.5, -8.2), (1.5, -8.2), (2.0, -7.7), (2.0, -6.2),
               (7.0, -6.2), (7.0, -1.5), (2.5, -1.5), (2.0, -4.25)]
SOCKET_H = 1.85                    # ソケットの高さ (基板の裏から)
TALL = ("xiao", "jst", "molex", "smt_nut")     # 電池の上に置けない (背が 2.35mm より高い・ネジが通る)


def outline(side):
    g = kataware_case.load(f"pcb_{side}")          # Ergogen の座標 (y 上向き) → KiCad (y 下向き)
    return Polygon([(x, -y) for x, y in g.exterior.coords],
                   [[(x, -y) for x, y in r.coords] for r in g.interiors])


def main():
    bad = 0
    for side in ("left", "right"):
        pads = pad_shapes(os.path.join(PCBS, f"{side}.kicad_pcb"))
        board = outline(side).buffer(-EDGE)
        print(f"== {side}  (パッド {len(pads)} 個)")
        for i, a in enumerate(pads):
            for b in pads[i + 1:]:
                if a[0] == b[0] or not (a[2] & b[2]) or (a[4] and a[4] == b[4]):
                    continue
                d = a[3].distance(b[3])
                if d < GAP:
                    bad += 1
                    print(f"  近すぎ: {a[0]} パッド{a[1]} と {b[0]} パッド{b[1]} ({d:.2f}mm)")
            if a[5] != "np_thru_hole" and not board.contains(a[3]):
                bad += 1
                print(f"  基板の端に近すぎ/はみ出し: {a[0]} パッド{a[1]}")
        bodies = back_bodies(os.path.join(PCBS, f"{side}.kicad_pcb"))
        for i, a in enumerate(bodies):
            for b in bodies[i + 1:]:
                if a[0] != b[0] and a[2].intersects(b[2]) and a[2].intersection(b[2]).area > 0.01:
                    bad += 1
                    print(f"  裏の部品が重なる: {a[0]} と {b[0]}")
        ex, ey = ukishima.BATTERY[side]
        bat = box(ex - ukishima.BAT_W/2, -(ey + ukishima.BAT_H/2), ex + ukishima.BAT_W/2, -(ey - ukishima.BAT_H/2))
        for ref, name, shp in bodies:
            if any(t in name.lower() for t in TALL) and shp.intersects(bat):
                bad += 1
                print(f"  電池の上に背の高い部品: {ref} ({name})")
    print("問題なし" if bad == 0 else f"問題 {bad} 件")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
