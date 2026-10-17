"""kataware ケース (ガスケットマウント) の 3D データ (STL) を作る。

使い方 (リポジトリの一番上で):
    pip install manifold3d shapely ezdxf
    npx ergogen@4.1.0 pcb/ergogen -o pcb/ergogen/output   # 先に外形を作る
    python3 case/kataware_case.py

できるもの (case/stl/):
    bottom_left.stl / bottom_right.stl … 下ケース (底と壁)
    top_left.stl    / top_right.stl    … 上ケース (フレーム)

平面の形 (外形・内側・基板・プレートの耳) は Ergogen の DXF を読み込んで使う。
ここで決めているのは「高さ」と、ネジ・USB・電源スイッチなどの穴の位置だけ。
寸法はすべて mm。z は机側 (底面) が 0。
"""
import math
import os
import struct
import sys

import ezdxf
import manifold3d as mf
from ezdxf import path as ezpath
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUTLINES = os.path.join(HERE, "..", "pcb", "ergogen", "output", "outlines")

U = 19.05
RIGHT_X = 200 + U          # 右手の原点 (Ergogen の rx + kx)

# ===== 高さ (z) =====
FLOOR = 2.5                # 底板の厚さ
PCB_B = FLOOR + 7.0        # 基板の下面 (下に XIAO・電池・ソケットが入る 7mm)
PCB_T = PCB_B + 1.6        # 基板の上面
PLATE_B = PCB_T + 1.0      # プレートの下面 (Choc: 基板上面〜プレート上面 2.2mm)
PLATE_T = PLATE_B + 1.2    # プレートの上面 (FR4 1.2mm)
GASKET = 1.5               # ガスケット (ポロン) の厚さ
SPLIT = PLATE_B - GASKET   # 下ケースと上ケースの分かれ目 = 下のガスケットが乗る面
CEIL = PLATE_T + GASKET - 0.2   # 上のガスケットを押さえる面 (0.2mm だけ押しつぶす)
TOP = CEIL + 1.9           # 上ケースの一番上
BAT_POCKET = 1.0           # 電池のくぼみの深さ

# ===== 平面の位置 (Ergogen と同じ座標。y は上がプラス) =====
HALVES = {
    "left": {
        "inner_x": 6.5*U,          # 内側 (相手側) の壁の内面
        "dir": +1,                 # 内側の壁がどちら向きか
        "xiao": (6.5*U - 8, 38.5),
        "pwr_y": 51.5,
        "battery": (29.0, 0.5*U),
        "screws": [(2.15, "top"), (53.15, "top"), (102.15, "top"),
                   (2.15, "bottom"), (47.15, "bottom"), (102.15, "bottom")],
        "feet": [(2.15, 1.575), (112.15, 1.575), (2.15, 55.575), (112.15, 55.575)],
        "ball": None,
    },
    "right": {
        "inner_x": RIGHT_X - 1.5*U,
        "dir": -1,
        "xiao": (RIGHT_X - 1.5*U + 8, 38.5),
        "pwr_y": 51.5,
        "battery": (RIGHT_X + 67.7, 0.5*U),
        "screws": [(RIGHT_X + 93.1, "top"), (RIGHT_X + 42.1, "top"), (RIGHT_X - 6.9, "top"),
                   (RIGHT_X + 93.1, "bottom"), (RIGHT_X + 48.1, "bottom"), (RIGHT_X + 13.0, "bottom")],
        "feet": [(RIGHT_X + 93.1, 1.575), (RIGHT_X + 18.1, 1.575),
                 (RIGHT_X + 93.1, 55.575), (RIGHT_X - 16.9, 55.575)],
        "ball": (RIGHT_X - 8.0, 11.0),          # config.yaml の ball_x / ball_y と同じ
    },
}
WALL_TOP_Y = 3.5*U + 2.5       # 上の壁の真ん中
WALL_BOTTOM_Y = -0.5*U - 2.5   # 下の壁の真ん中
BALL_SCREW_R = 13.5            # ボールユニットの底ネジ (ユニット中心から)
BALL_SCREW_ANGLES = (30, 150, 270)   # 奥 (90°) はセンサーのケーブルの出口なのであける


# ---------- DXF → shapely ----------
def load(name):
    doc = ezdxf.readfile(os.path.join(OUTLINES, f"{name}.dxf"))
    lines = []
    for e in doc.modelspace():
        pts = [(round(v.x, 3), round(v.y, 3)) for v in ezpath.make_path(e).flattening(0.02)]
        lines += [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    shape = Polygon()
    for face in polygonize(lines):           # 穴は「偶奇」で処理する
        shape = shape.symmetric_difference(Polygon(face.exterior))
    return shape


def polys(g):
    if g.is_empty:
        return []
    return list(g.geoms) if isinstance(g, MultiPolygon) else [g]


# ---------- shapely → manifold ----------
def prism(shape, z0, z1):
    contours = []
    for p in polys(shape):
        contours.append([list(c) for c in list(p.exterior.coords)[:-1]])
        contours += [[list(c) for c in list(r.coords)[:-1]] for r in p.interiors]
    cs = mf.CrossSection(contours, mf.FillRule.EvenOdd)
    return cs.extrude(z1 - z0).translate([0, 0, z0])


def cyl(x, y, z0, z1, r, r_top=None):
    return mf.Manifold.cylinder(z1 - z0, r, r if r_top is None else r_top, 48).translate([x, y, z0])


def cube(x0, y0, z0, x1, y1, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def union(items):
    return mf.Manifold.batch_boolean(items, mf.OpType.Add)


# ---------- 部品 ----------
def build(side):
    h = HALVES[side]
    outer = load(f"board_{side}")
    cavity = load(f"cavity_{side}")
    opening = load(f"top_opening_{side}")
    pcb = load(f"pcb_{side}")
    plate = Polygon(load(f"plate_{side}").exterior)      # 穴は不要。外まわりだけ
    pcb_pocket = pcb.buffer(0.75, join_style=2)          # 基板のまわり 0.75mm
    plate_pocket = plate.buffer(0.5, join_style=2)       # プレートの耳のまわり 0.5mm
    ix, d = h["inner_x"], h["dir"]
    xx, xy = h["xiao"]
    outer_x = ix + d*5.0
    wall = outer.difference(cavity)

    # ===== 下ケース =====
    bottom = prism(outer, 0, SPLIT)
    cut = [
        prism(cavity, FLOOR, SPLIT + 1),
        prism(pcb_pocket, PCB_B - 1.0, SPLIT + 1),
        # 電池のくぼみ (30 x 20mm + 余裕)
        cube(h["battery"][0] - 15.5, h["battery"][1] - 10.5, FLOOR - BAT_POCKET,
             h["battery"][0] + 15.5, h["battery"][1] + 10.5, FLOOR + 1),
        # USB-C の穴 (内側の側面)
        cube(min(ix, outer_x + d), xy - 6.5, 2.7, max(ix, outer_x + d), xy + 6.5, SPLIT + 1),
        # リセットボタンを押す穴 (XIAO の USB 側から約5mm。実物合わせ)
        cube(ix + d*2.5 - d*5 - 2, xy - 6, -1, ix + d*2.5 - d*5 + 2, xy + 6, FLOOR + 1),
    ]
    for sx, edge in h["screws"]:                 # 上下ケースをとめるネジ (底から)
        sy = WALL_TOP_Y if edge == "top" else WALL_BOTTOM_Y
        cut += [cyl(sx, sy, -1, SPLIT + 1, 1.15), cyl(sx, sy, -1, 1.8, 2.1)]
    for fx, fy in h["feet"]:                     # ゴム足のくぼみ (直径10mm 用)
        cut.append(cyl(fx, fy, -1, 0.6, 5.25))
    if h["ball"]:                                # ボールユニットの底ネジ (皿ネジ M2)
        bx, by = h["ball"]
        for a in BALL_SCREW_ANGLES:
            sx = bx + BALL_SCREW_R*math.cos(math.radians(a))
            sy = by + BALL_SCREW_R*math.sin(math.radians(a))
            cut += [cyl(sx, sy, -1, FLOOR + 1, 1.15), cyl(sx, sy, -0.01, 1.2, 2.2, 1.0)]
    bottom = bottom - union(cut)

    # ===== 上ケース =====
    top = prism(outer, SPLIT, TOP)
    pwr_y = h["pwr_y"]
    cut = [
        prism(cavity, SPLIT - 1, CEIL),
        prism(opening, CEIL - 0.01, TOP + 1),
        prism(plate_pocket, SPLIT - 1, CEIL),
        prism(pcb_pocket, SPLIT - 1, PCB_T + 0.5),
        # 電源スイッチ: 本体の逃げ + レバーの穴
        cube(min(ix, ix + d*3.75), pwr_y - 4.25, SPLIT - 1, max(ix, ix + d*3.75), pwr_y + 4.25, PCB_T + 2.0),
        cube(min(ix, outer_x + d), pwr_y - 2.5, PCB_T - 0.1, max(ix, outer_x + d), pwr_y + 2.5, PCB_T + 1.7),
    ]
    for sx, edge in h["screws"]:                 # タッピングネジ M2 の下穴
        sy = WALL_TOP_Y if edge == "top" else WALL_BOTTOM_Y
        cut.append(cyl(sx, sy, SPLIT - 1, SPLIT + 4.5, 0.85))
    top = top - union(cut)

    check(side, wall, cavity, pcb_pocket, plate_pocket, h)
    return bottom, top


def check(side, wall, cavity, pcb_pocket, plate_pocket, h):
    """ネジ穴が壁の中に収まり、溝とぶつからないかを確かめる"""
    voids = unary_union([cavity, pcb_pocket, plate_pocket])
    for sx, edge in h["screws"]:
        sy = WALL_TOP_Y if edge == "top" else WALL_BOTTOM_Y
        hole = Point(sx, sy).buffer(1.15)                # ネジの通る穴 (座ぐりは底板の中なので見ない)
        if not wall.buffer(-1.0).contains(hole) or hole.distance(voids) < 1.0:
            sys.exit(f"{side}: ネジ ({sx:.1f}, {sy:.1f}) が壁からはみ出すか溝に近すぎる")
    print(f"  {side}: 壁の一番薄い所 (溝の外側) ≈ {min_skin(wall, voids):.2f}mm")


def min_skin(wall, voids):
    outer_edge = wall.exterior
    return min(outer_edge.distance(Point(c)) for g in polys(voids) for c in g.exterior.coords)


# ---------- STL ----------
def save_stl(m, path):
    mesh = m.to_mesh()
    v, t = mesh.vert_properties, mesh.tri_verts
    with open(path, "wb") as f:
        f.write(b"kataware".ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        for a, b, c in t:
            p = [v[a][:3], v[b][:3], v[c][:3]]
            ux, uy, uz = (p[1][i] - p[0][i] for i in range(3))
            wx, wy, wz = (p[2][i] - p[0][i] for i in range(3))
            n = (uy*wz - uz*wy, uz*wx - ux*wz, ux*wy - uy*wx)
            ln = math.sqrt(sum(k*k for k in n)) or 1.0
            f.write(struct.pack("<12fH", *(k/ln for k in n), *p[0], *p[1], *p[2], 0))


def main():
    out = os.path.join(HERE, "stl")
    os.makedirs(out, exist_ok=True)
    print(f"高さ: 底板 {FLOOR} / 基板 {PCB_B}〜{PCB_T:.1f} / プレート {PLATE_B:.1f}〜{PLATE_T:.1f} / "
          f"分かれ目 {SPLIT:.1f} / 上ケース上面 {TOP:.1f}")
    for side in ("left", "right"):
        bottom, top = build(side)
        for name, m in (("bottom", bottom), ("top", top)):
            p = os.path.join(out, f"{name}_{side}.stl")
            save_stl(m, p)
            print(f"  {p}  ({m.num_tri()} 三角形, {m.volume()/1000:.1f} cm³)")


if __name__ == "__main__":
    main()
