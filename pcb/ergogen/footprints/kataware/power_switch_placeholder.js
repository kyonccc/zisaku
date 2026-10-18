// kataware: 電源スライドスイッチの「仮」フットプリント
// KiCad で標準ライブラリの Button_Switch_SMD:SW_SPDT_PCM12 (C&K PCM12、Alps SSSS811101 と同じ形)
// に「フットプリントを変更」で置き換える。パッド番号 1・2・3 のつながりはそのまま引き継がれる。
//
// Nets
//    from: パッド1 (電池＋)
//    to:   パッド2 (中央・XIAO の BAT+ へ)
//    パッド3 は未接続 (OFF 側)
module.exports = {
  params: {
    designator: 'PWR',
    from: undefined,
    to: undefined
  },
  // パッドの位置は KiCad 標準の SW_SPDT_PCM12 と同じ。パッド 1〜3 は y = -1.43 (上側)、
  // レバーは反対の +y 側 (下側) に出る → 置き換えても向きが変わらない
  body: p => `
    (module kataware_power_switch_placeholder (layer F.Cu) (tedit 0)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 -3.2 ${p.r}) (layer F.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15))))
    (fp_text value "" (at 0 0) (layer F.SilkS) hide (effects (font (size 1 1) (thickness 0.15))))
    (fp_text user "PWR (仮)" (at 0 0.3 ${p.r}) (layer F.Fab) (effects (font (size 0.6 0.6) (thickness 0.1))))
    (fp_line (start -3.35 -1) (end 3.35 -1) (layer F.Fab) (width 0.1))
    (fp_line (start 3.35 -1) (end 3.35 1.6) (layer F.Fab) (width 0.1))
    (fp_line (start 3.35 1.6) (end -3.35 1.6) (layer F.Fab) (width 0.1))
    (fp_line (start -3.35 1.6) (end -3.35 -1) (layer F.Fab) (width 0.1))
    (fp_line (start -1.4 1.6) (end -1.4 3.15) (layer F.Fab) (width 0.1))
    (fp_line (start -1.4 3.15) (end -0.1 3.15) (layer F.Fab) (width 0.1))
    (fp_line (start -0.1 3.15) (end -0.1 1.6) (layer F.Fab) (width 0.1))
    (fp_text user "レバー" (at -0.75 4.2 ${p.r}) (layer F.Fab) (effects (font (size 0.5 0.5) (thickness 0.08))))
    (pad 1 smd rect (at -2.25 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Paste F.Mask) ${p.from || ''})
    (pad 2 smd rect (at 0.75 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Paste F.Mask) ${p.to || ''})
    (pad 3 smd rect (at 2.25 -1.43 ${p.r}) (size 0.7 1.5) (layers F.Cu F.Paste F.Mask))
    (pad "" smd rect (at -3.65 -0.78 ${p.r}) (size 1 0.8) (layers F.Cu F.Paste F.Mask))
    (pad "" smd rect (at -3.65 1.43 ${p.r}) (size 1 0.8) (layers F.Cu F.Paste F.Mask))
    (pad "" smd rect (at 3.65 -0.78 ${p.r}) (size 1 0.8) (layers F.Cu F.Paste F.Mask))
    (pad "" smd rect (at 3.65 1.43 ${p.r}) (size 1 0.8) (layers F.Cu F.Paste F.Mask))
    (pad "" np_thru_hole circle (at -1.5 0.33) (size 0.9 0.9) (drill 0.9) (layers *.Cu *.Mask))
    (pad "" np_thru_hole circle (at 1.5 0.33) (size 0.9 0.9) (drill 0.9) (layers *.Cu *.Mask))
    )
  `
}
