"""Ergogen で作った基板 (.kicad_pcb) の簡単な検査。

使い方 (リポジトリの一番上で): python3 tools/check_pcb.py

調べること:
  1. ちがう部品のパッド (銅) どうしが 0.2mm より近くないか (同じつながりは除く)
  2. パッドが基板の外形から 0.3mm 以上内側にあるか
KiCad の DRC (デザインルールチェック) の代わりではない。KiCad でも必ず DRC をすること。
"""
import math
import os
import sys

from shapely import affinity
from shapely.geometry import Point, Polygon, box

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "case"))
from import_footprints import find, find_all, parse, unq  # noqa: E402
import kataware_case  # noqa: E402

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
    print("問題なし" if bad == 0 else f"問題 {bad} 件")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
