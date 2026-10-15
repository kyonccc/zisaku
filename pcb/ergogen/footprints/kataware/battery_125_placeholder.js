// kataware: 電池コネクタ (1.25mm ピッチ 2ピン) の「仮」フットプリント
// 電池: ジイエクサ Gexa GA-011 (PSE 認証済み)。コネクタは Molex PicoBlade 互換と思われる (要実物確認)
// 電池側の向き: 端子面から見て 左 = 黒 (−) / 右 = 赤 (＋)
//
// KiCad で標準ライブラリの Molex PicoBlade 2ピン (例: Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal)
// に「フットプリントを変更」で置き換える。置き換えた後、どちらのピンが＋になるかを
// 実物の電池とテスターで必ず確認し、パッドのつながり (BAT_P / GND) を合わせること。
//
// Nets
//    pos: パッド2 (＋、電池の赤)
//    neg: パッド1 (−、電池の黒)
module.exports = {
  params: {
    designator: 'BAT',
    side: 'B',
    pos: undefined,
    neg: undefined
  },
  body: p => {
    const layer = p.side == 'B' ? 'B' : 'F'
    const mirror = p.side == 'B' ? '(justify mirror)' : ''
    return `
    (module kataware_battery_125_placeholder (layer ${layer}.Cu) (tedit 0)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 -3) (layer ${layer}.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
    (fp_text value "" (at 0 0) (layer ${layer}.SilkS) hide (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
    (fp_text user "BAT 1.25mm (仮)" (at 0 3 ${p.r}) (layer ${layer}.Fab) (effects (font (size 0.8 0.8) (thickness 0.12)) ${mirror}))
    (fp_text user "-" (at -0.625 -1.8 ${p.r}) (layer ${layer}.SilkS) (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
    (fp_text user "+" (at 0.625 -1.8 ${p.r}) (layer ${layer}.SilkS) (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
    (fp_line (start -2.5 -1) (end 2.5 -1) (layer ${layer}.Fab) (width 0.12))
    (fp_line (start 2.5 -1) (end 2.5 2.2) (layer ${layer}.Fab) (width 0.12))
    (fp_line (start 2.5 2.2) (end -2.5 2.2) (layer ${layer}.Fab) (width 0.12))
    (fp_line (start -2.5 2.2) (end -2.5 -1) (layer ${layer}.Fab) (width 0.12))
    (pad 1 smd rect (at -0.625 0 ${p.r}) (size 0.8 1.6) (layers ${layer}.Cu ${layer}.Paste ${layer}.Mask) ${p.neg})
    (pad 2 smd rect (at 0.625 0 ${p.r}) (size 0.8 1.6) (layers ${layer}.Cu ${layer}.Paste ${layer}.Mask) ${p.pos})
    )
  `
  }
}
