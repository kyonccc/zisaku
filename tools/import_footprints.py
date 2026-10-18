"""KiCad のフットプリント (.kicad_mod) を、Ergogen で使える形 (.js) に変換する。

使い方 (リポジトリの一番上で):
    python3 tools/import_footprints.py

pcb/ergogen/lib_src/ の .kicad_mod を読み、pcb/ergogen/footprints/lib/ に .js を書く。
- パッドの番号ごとに「つながり (ネット)」を Ergogen の設定から渡せるようにする
- side: 'B' にすると基板の裏に付ける形 (上から見て裏返し) にする
- KiCad 7 以降で読めるよう、古い書き方 (module / fp_text / width) で出力する

元のフットプリントのライセンス:
- KiCad 標準ライブラリ … CC-BY-SA 4.0 (作った基板には適用されない例外つき)
- Seeed Studio OPL (XIAO) … CC-BY-SA 4.0 (帰属表示が必要)
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb", "ergogen")
SRC = os.path.join(ROOT, "lib_src")
OUT = os.path.join(ROOT, "footprints", "lib")

# 変換するもの: (元ファイル, 出力名, 部品記号, ライブラリ名, {パッド番号: パラメーター名}, 出典)
PARTS = [
    ("XIAO-nRF52840-Plus-SMD.kicad_mod", "xiao_nrf52840_plus", "MCU", "Seeed_Studio_XIAO_Series:XIAO-nRF52840-Plus-SMD",
     {"1": "D0", "2": "D1", "3": "D2", "4": "D3", "5": "D4", "6": "D5", "7": "D6", "8": "D7", "9": "D8",
      "10": "D9", "11": "D10", "12": "V3V3", "13": "GND", "14": "VBUS", "15": "D11", "16": "D12", "17": "D13",
      "18": "D14", "19": "D15", "20": "D16", "21": "D17", "22": "D18", "23": "D19", "24": "SWDIO",
      "25": "SWDCLK", "26": "EN", "27": "GND", "28": "BATP", "29": "GND"},
     "Seeed Studio OPL_Kicad_Library (https://github.com/Seeed-Studio/OPL_Kicad_Library) CC-BY-SA 4.0"),
    ("SW_SPDT_PCM12.kicad_mod", "sw_spdt_pcm12", "PWR", "Button_Switch_SMD:SW_SPDT_PCM12",
     {"1": "from", "2": "to", "3": "off"},
     "KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)"),
    ("JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical.kicad_mod", "jst_sh_bm06b", "J",
     "Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical",
     {"1": "P1", "2": "P2", "3": "P3", "4": "P4", "5": "P5", "6": "P6"},
     "KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)"),
    ("Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal.kicad_mod", "molex_picoblade_2p", "BAT",
     "Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal",
     {"1": "neg", "2": "pos"},
     "KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)"),
]
LAYERS = ("F.SilkS", "F.Fab", "F.CrtYd")

# 追加するパッド (出力名ごと)。XIAO の電池パッド (28 = VBAT) は XIAO の真下に隠れるので、
# 基板に小さな穴 (スルーホール) をあけ、反対の面からはんだを流し込めるようにする
EXTRA = {
    "xiao_nrf52840_plus": [("28", "-5.517823", "-0.993988", "0.7", "1.1", "BATP")],
}


# ---------- S 式の読み込み ----------
def parse(text):
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0][0]


def find(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None


def find_all(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def unq(s):
    return s[1:-1] if s.startswith('"') else s


# ---------- 変換 ----------
def num(v):
    return float(v)


def js_layer(name):
    """F.xxx → ${S}.xxx (S は 'F' か 'B')"""
    if name.startswith("F."):
        return "${S}." + name[2:]
    if name.startswith("B."):
        return "${O}." + name[2:]
    return name


def pt(x, y):
    """座標。裏側なら y を反転 (KiCad の「裏返し」と同じ)"""
    return f"${{fx({x})}} ${{fy({y})}}"


def width_of(node):
    st = find(node, "stroke")
    w = find(st, "width") if st else find(node, "width")
    return w[1] if w else "0.12"


def graphic(node):
    kind = node[0]
    layer = unq(find(node, "layer")[1])
    if layer not in LAYERS:
        return None
    L, w = js_layer(layer), width_of(node)
    if kind == "fp_line":
        s, e = find(node, "start"), find(node, "end")
        return f"(fp_line (start {pt(s[1], s[2])}) (end {pt(e[1], e[2])}) (layer {L}) (width {w}))"
    if kind == "fp_rect":
        s, e = find(node, "start"), find(node, "end")
        x0, y0, x1, y1 = s[1], s[2], e[1], e[2]
        return "\n".join(f"(fp_line (start {pt(a, b)}) (end {pt(c, d)}) (layer {L}) (width {w}))"
                         for a, b, c, d in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)))
    if kind == "fp_circle":
        c, e = find(node, "center"), find(node, "end")
        return f"(fp_circle (center {pt(c[1], c[2])}) (end {pt(e[1], e[2])}) (layer {L}) (width {w}))"
    if kind == "fp_arc":
        s, m, e = find(node, "start"), find(node, "mid"), find(node, "end")
        if m is None:
            return None
        return f"(fp_arc (start {pt(s[1], s[2])}) (mid {pt(m[1], m[2])}) (end {pt(e[1], e[2])}) (layer {L}) (width {w}))"
    if kind == "fp_poly":
        xy = [p for p in find(node, "pts")[1:] if p[0] == "xy"]
        segs = [(xy[i], xy[(i + 1) % len(xy)]) for i in range(len(xy))]
        return "\n".join(f"(fp_line (start {pt(a[1], a[2])}) (end {pt(b[1], b[2])}) (layer {L}) (width {w}))"
                         for a, b in segs)
    return None


def pad(node, pinmap):
    number = unq(node[1])
    ptype, shape = node[2], node[3]
    at = find(node, "at")
    x, y = at[1], at[2]
    a = at[3] if len(at) > 3 else "0"
    size = find(node, "size")
    drill = find(node, "drill")
    layers = " ".join(js_layer(unq(l)) for l in find(node, "layers")[1:])
    extra = ""
    rr = find(node, "roundrect_rratio")
    if rr:
        extra += f" (roundrect_rratio {rr[1]})"
    if drill:
        extra += " (drill " + " ".join(drill[1:]) + ")"
    net = ""
    if number in pinmap:
        net = f" ${{p.{pinmap[number]} || ''}}"
    angle = f"${{p.r + fa({a})}}"
    name = f'"{number}"'
    return (f"(pad {name} {ptype} {shape} (at {pt(x, y)} {angle}) (size {size[1]} {size[2]}){extra} "
            f"(layers {layers}){net})")


def convert(src, name, designator, lib_id, pinmap, credit):
    root = parse(open(os.path.join(SRC, src), encoding="utf-8").read())
    descr = find(root, "descr")
    ref = None
    for prop in find_all(root, "property"):
        if unq(prop[1]) == "Reference":
            ref = find(prop, "at")
    rx, ry = (ref[1], ref[2]) if ref else ("0", "0")
    graphics = [g for g in (graphic(n) for n in root if isinstance(n, list) and n and n[0] in
                            ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly")) if g]
    pads = [pad(n, pinmap) for n in find_all(root, "pad")]
    for number, x, y, drill, size, param in EXTRA.get(name, []):
        pads.append(f'(pad "{number}" thru_hole circle (at {pt(x, y)} ${{p.r}}) (size {size} {size}) '
                    f'(drill {drill}) (layers *.Cu *.Mask) ${{p.{param} || \'\'}})')
    model = find(root, "model")
    model_txt = ""
    if model and "KICAD" in model[1]:
        model_txt = "(model " + model[1].replace("${", "\\${") + ")"     # JS の中なので $ を逃がす
    params = sorted(set(pinmap.values()))
    body = "\n      ".join(graphics + pads + ([model_txt] if model_txt else []))
    js = f"""// 自動生成: tools/import_footprints.py ({src} から)
// 元データ: {credit}
// KiCad のライブラリ名: {lib_id}
// {unq(descr[1]) if descr else ''}
//
// side: 'F' = 基板の表 / 'B' = 基板の裏 (上から見て裏返しの形になる)
// パッド番号とつながり: {', '.join(f'{k}={v}' for k, v in pinmap.items())}
module.exports = {{
  params: {{
    designator: '{designator}',
    side: 'F',
{chr(10).join(f"    {p}: {{ type: 'net', value: '' }}," for p in params)}
  }},
  body: p => {{
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    const fx = v => v
    const fy = v => back ? -v : v
    const fa = v => back ? -v : v
    return `
      (module "{lib_id}" (layer ${{S}}.Cu) (tedit 0)
      ${{p.at}}
      (fp_text reference "${{p.ref}}" (at {pt(rx, ry)} ${{p.r}}) (layer ${{S}}.SilkS) ${{p.ref_hide}} (effects (font (size 1 1) (thickness 0.15)) ${{back ? '(justify mirror)' : ''}}))
      (fp_text value "{lib_id.split(':')[1]}" (at 0 0 ${{p.r}}) (layer ${{S}}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12)) ${{back ? '(justify mirror)' : ''}}))
      {body}
      )
    `
  }}
}}
"""
    open(os.path.join(OUT, f"{name}.js"), "w", encoding="utf-8").write(js)
    print(f"{name}.js  ({len(pads)} パッド, {len(graphics)} 図形)")


def main():
    os.makedirs(OUT, exist_ok=True)
    for args in PARTS:
        convert(*args)


if __name__ == "__main__":
    sys.exit(main())
