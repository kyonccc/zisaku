// kataware: XIAO nRF52840 Plus の「仮」フットプリント (基板の裏に付ける)
//
// 目的: KiCad で開いた時に、XIAO の各ピンへの「つながり (ネット)」が見えるようにすること。
// パッドの形・位置は仮。KiCad で Seeed 公式のフットプリントに置き換え、
// つながり (ネット) を公式のパッドに移すこと (パッド番号 1〜14 は Seeed 標準の番号)。
//
// 上から見た図 (USB-C が奥 = 上)。裏付けなので左右が反転して見える:
//          [USB-C]
//   5V  14 ●     ● 1  D0
//   GND 13 ●     ● 2  D1
//   3V3 12 ●     ● 3  D2
//   D10 11 ●     ● 4  D3
//   D9  10 ●     ● 5  D4
//   D8   9 ●     ● 6  D5
//   D7   8 ●     ● 7  D6
// Plus の裏面パッド (D11〜D13, D17〜D19, BAT+) は「仮の位置」に並べてある
module.exports = {
  params: {
    designator: 'MCU',
    D0: { type: 'net', value: '' },
    D1: { type: 'net', value: '' },
    D2: { type: 'net', value: '' },
    D3: { type: 'net', value: '' },
    D4: { type: 'net', value: '' },
    D5: { type: 'net', value: '' },
    D6: { type: 'net', value: '' },
    D7: { type: 'net', value: '' },
    D8: { type: 'net', value: '' },
    D9: { type: 'net', value: '' },
    D10: { type: 'net', value: '' },
    D11: { type: 'net', value: '' },
    D12: { type: 'net', value: '' },
    D13: { type: 'net', value: '' },
    D17: { type: 'net', value: '' },
    D18: { type: 'net', value: '' },
    D19: { type: 'net', value: '' },
    V3V3: { type: 'net', value: '' },
    GND: { type: 'net', value: '' },
    BATP: { type: 'net', value: '' },
  },
  body: p => {
    const pitch = 2.54
    const xr = 7.62   // 裏付けなので D0〜D6 は右側
    const pads = []
    const left = [p.D0, p.D1, p.D2, p.D3, p.D4, p.D5, p.D6]
    left.forEach((n, i) => pads.push(
      `(pad ${i + 1} thru_hole ${i == 0 ? 'rect' : 'circle'} (at ${xr} ${-7.62 + i * pitch} ${p.r}) (size 1.6 1.6) (drill 1.0) (layers *.Cu *.Mask) ${n})`))
    const right = [p.D7, p.D8, p.D9, p.D10, p.V3V3, p.GND, undefined]   // 8〜14 (下から上)
    right.forEach((n, i) => pads.push(
      `(pad ${i + 8} thru_hole circle (at ${-xr} ${7.62 - i * pitch} ${p.r}) (size 1.6 1.6) (drill 1.0) (layers *.Cu *.Mask) ${n})`))
    // Plus の裏面パッド (仮の位置): 中央に2列で並べる
    const extra = [['D11', p.D11], ['D12', p.D12], ['D13', p.D13], ['D17', p.D17],
                   ['D18', p.D18], ['D19', p.D19], ['BAT+', p.BATP]]
    extra.forEach(([name, n], i) => {
      const x = (i % 2 == 0 ? 1.6 : -1.6)
      const y = -5 + Math.floor(i / 2) * 2.6
      pads.push(`(pad "${name}" smd rect (at ${x} ${y} ${p.r}) (size 1.2 1.2) (layers B.Cu B.Mask) ${n || ''})`)
    })
    return `
      (module kataware_xiao_plus_placeholder (layer B.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 -12) (layer B.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
      (fp_text value "" (at 0 0) (layer B.SilkS) hide (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
      (fp_text user "XIAO nRF52840 Plus (裏・仮)" (at 0 9 ${p.r}) (layer B.Fab) (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))
      (fp_line (start -8.9 -10.5) (end 8.9 -10.5) (layer B.Fab) (width 0.12))
      (fp_line (start 8.9 -10.5) (end 8.9 10.5) (layer B.Fab) (width 0.12))
      (fp_line (start 8.9 10.5) (end -8.9 10.5) (layer B.Fab) (width 0.12))
      (fp_line (start -8.9 10.5) (end -8.9 -10.5) (layer B.Fab) (width 0.12))
      (fp_line (start -4.5 -12) (end 4.5 -12) (layer B.Fab) (width 0.12))
      (fp_line (start 4.5 -12) (end 4.5 -10.5) (layer B.Fab) (width 0.12))
      (fp_line (start -4.5 -12) (end -4.5 -10.5) (layer B.Fab) (width 0.12))
      ${pads.join('\n      ')}
      )
    `
  }
}
