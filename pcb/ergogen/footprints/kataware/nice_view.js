// kataware: nice!view (36 x 14mm) 用フットプリント (基板の表に付ける)
// 5本のピン (2.54mm ピッチ) と外形の目安。ピンの並び: 1=MOSI 2=SCK 3=VCC 4=GND 5=CS
// (nice!view の公式ピン配置: https://nicekeyboards.com/docs/nice-view/pinout-schematic)
//
// 基準点は画面の中心。ピンは +16.7mm (回転 0° のとき下側) に並ぶ
module.exports = {
  params: {
    designator: 'DISP',
    MOSI: undefined,
    SCK: undefined,
    VCC: undefined,
    GND: undefined,
    CS: undefined
  },
  body: p => {
    const nets = [p.MOSI, p.SCK, p.VCC, p.GND, p.CS]
    const names = ['MOSI', 'SCK', 'VCC', 'GND', 'CS']
    const pads = nets.map((n, i) => {
      const x = (i - 2) * 2.54
      const shape = i == 0 ? 'rect' : 'circle'
      return `(pad ${i + 1} thru_hole ${shape} (at ${x} 16.7 ${p.r}) (size 1.7 1.7) (drill 1.0) (layers *.Cu *.Mask) ${n || ''})
      (fp_text user "${names[i]}" (at ${x} 13.9 ${p.r + 90}) (layer F.SilkS) (effects (font (size 0.7 0.7) (thickness 0.12))))`
    }).join('\n')
    return `
      (module kataware_nice_view (layer F.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 -19.2) (layer F.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "" (at 0 0) (layer F.SilkS) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "nice!view" (at 0 0 ${p.r + 90}) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -7 -18) (end 7 -18) (layer F.Fab) (width 0.12))
      (fp_line (start 7 -18) (end 7 18) (layer F.Fab) (width 0.12))
      (fp_line (start 7 18) (end -7 18) (layer F.Fab) (width 0.12))
      (fp_line (start -7 18) (end -7 -18) (layer F.Fab) (width 0.12))
      (fp_line (start -6.6 15.3) (end 6.6 15.3) (layer F.SilkS) (width 0.12))
      (fp_line (start 6.6 15.3) (end 6.6 18.1) (layer F.SilkS) (width 0.12))
      (fp_line (start 6.6 18.1) (end -6.6 18.1) (layer F.SilkS) (width 0.12))
      (fp_line (start -6.6 18.1) (end -6.6 15.3) (layer F.SilkS) (width 0.12))
      ${pads}
      )
    `
  }
}
