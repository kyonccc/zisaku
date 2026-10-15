// 部品の「置き場所」だけを示す枠 (パッドなし)
// XIAO・nice!view など、Ergogen に部品がないものの位置合わせ用。
// KiCad で正式なフットプリント (Seeed 公式など) に置き換えること。
//
// Params
//    width / height: 枠の大きさ (mm)
//    label: 枠の中に書く文字
//    side: 'F' (表) または 'B' (裏)
module.exports = {
  params: {
    designator: 'BOX',
    width: 10,
    height: 10,
    label: '',
    side: 'F'
  },
  body: p => {
    const w = p.width / 2
    const h = p.height / 2
    const layer = p.side == 'B' ? 'B.SilkS' : 'F.SilkS'
    const mirror = p.side == 'B' ? '(justify mirror)' : ''
    return `
      (module box (layer ${p.side}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 ${-h - 1}) (layer ${layer}) hide (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
      (fp_text value "" (at 0 0) (layer ${layer}) hide (effects (font (size 1 1) (thickness 0.15))))
      (fp_text user "${p.label}" (at 0 0 ${p.r}) (layer ${layer}) (effects (font (size 1 1) (thickness 0.15)) ${mirror}))
      (fp_line (start ${-w} ${-h}) (end ${w} ${-h}) (layer ${layer}) (width 0.15))
      (fp_line (start ${w} ${-h}) (end ${w} ${h}) (layer ${layer}) (width 0.15))
      (fp_line (start ${w} ${h}) (end ${-w} ${h}) (layer ${layer}) (width 0.15))
      (fp_line (start ${-w} ${h}) (end ${-w} ${-h}) (layer ${layer}) (width 0.15))
      )
    `
  }
}
