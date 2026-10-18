// kataware: トラックボールセンサー (PMW3610) 用 6ピンコネクタの「仮」フットプリント (基板の裏に付ける)
// JST SH (1.0mm ピッチ・上から挿すタイプ) BM06B-SRSS-TB を想定。
// KiCad で標準ライブラリの Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical に
// 「フットプリントを変更」で置き換える。パッド番号 1〜6 のつながりはそのまま引き継がれる。
//
// ピン穴 (スルーホール) を使わないので、基板の表 (プレートの真下) に何も出ない。
// Nets: P1〜P6 (3V3 / GND / SCLK / SDIO / NCS / MOTION)
module.exports = {
  params: {
    designator: 'J',
    side: 'B',
    P1: { type: 'net', value: '' },
    P2: { type: 'net', value: '' },
    P3: { type: 'net', value: '' },
    P4: { type: 'net', value: '' },
    P5: { type: 'net', value: '' },
    P6: { type: 'net', value: '' },
  },
  body: p => {
    const nets = [p.P1, p.P2, p.P3, p.P4, p.P5, p.P6]
    const pads = nets.map((n, i) =>
      `(pad ${i + 1} smd rect (at ${(i - 2.5).toFixed(2)} -1.3 ${p.r}) (size 0.6 1.55) (layers B.Cu B.Paste B.Mask) ${n || ''})`).join('\n')
    return `
      (module kataware_jst_sh6_placeholder (layer B.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 3.2) (layer B.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
      (fp_text value "" (at 0 0) (layer B.SilkS) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "J (仮) JST SH 6P" (at 0 0 ${p.r}) (layer B.Fab) (effects (font (size 0.6 0.6) (thickness 0.1)) (justify mirror)))
      (fp_line (start -4 -2.2) (end 4 -2.2) (layer B.Fab) (width 0.1))
      (fp_line (start 4 -2.2) (end 4 2.2) (layer B.Fab) (width 0.1))
      (fp_line (start 4 2.2) (end -4 2.2) (layer B.Fab) (width 0.1))
      (fp_line (start -4 2.2) (end -4 -2.2) (layer B.Fab) (width 0.1))
      ${pads}
      (pad "" smd rect (at -3.3 1.2 ${p.r}) (size 1.2 1.8) (layers B.Cu B.Paste B.Mask))
      (pad "" smd rect (at 3.3 1.2 ${p.r}) (size 1.2 1.8) (layers B.Cu B.Paste B.Mask))
      )
    `
  }
}
