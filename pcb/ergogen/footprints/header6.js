// 1列6ピンのピンヘッダ (2.54mm ピッチ)。トラックボールセンサー (PMW3610) 接続用
//
// Nets: P1〜P6 (VCC / GND / SCLK / SDIO / NCS / MOTION など)
module.exports = {
  params: {
    designator: 'J',
    P1: undefined,
    P2: undefined,
    P3: undefined,
    P4: undefined,
    P5: undefined,
    P6: undefined
  },
  body: p => {
    const nets = [p.P1, p.P2, p.P3, p.P4, p.P5, p.P6]
    const pads = nets.map((n, i) => {
      const x = (i - 2.5) * 2.54
      const shape = i == 0 ? 'rect' : 'circle'
      return `(pad ${i + 1} thru_hole ${shape} (at ${x} 0) (size 1.7 1.7) (drill 1.0) (layers *.Cu *.Mask) ${n || ''})`
    }).join('\n')
    return `
      (module header6 (layer F.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 -2) (layer F.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15))))
      (fp_text value "" (at 0 0) (layer F.SilkS) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_line (start -7.62 -1.27) (end 7.62 -1.27) (layer F.SilkS) (width 0.15))
      (fp_line (start 7.62 -1.27) (end 7.62 1.27) (layer F.SilkS) (width 0.15))
      (fp_line (start 7.62 1.27) (end -7.62 1.27) (layer F.SilkS) (width 0.15))
      (fp_line (start -7.62 1.27) (end -7.62 -1.27) (layer F.SilkS) (width 0.15))
      ${pads}
      )
    `
  }
}
