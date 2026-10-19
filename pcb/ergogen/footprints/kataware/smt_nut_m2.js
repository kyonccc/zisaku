// M2 はんだ付けナット (SMT ナット) — 浮島の「下から留める」ネジを受ける。基板の裏に付ける
// kataware 用に作ったもの (販売可能)
//
// 例: Würth Elektronik WA-SMSI M2 高さ 1.5mm (9774015243)。外径 4.35mm。
// パッドの大きさは、買う品番のデータシートに合わせて KiCad で調整すること。
//
// - 穴 φ3.0: ナットの根元の突起 (φ2.8 × 1.4mm) が入る (Würth WA-SMSI M2 の推奨)
// - パッド φ5.3 (裏): ナット (外径 4.35mm) をはんだ付けする
// - どこにもつながない (ネット無し)
module.exports = {
  params: {
    designator: 'H',
    side: 'B',
  },
  body: p => {
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    return `
      (module "kataware:SMT_Nut_M2" (layer ${S}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at 0 3.6 ${p.r}) (layer ${S}.SilkS) ${p.ref_hide} (effects (font (size 0.8 0.8) (thickness 0.12)) ${back ? '(justify mirror)' : ''}))
      (fp_text value "SMT_Nut_M2" (at 0 0 ${p.r}) (layer ${S}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12))))
      (fp_circle (center 0 0) (end 2.175 0) (layer ${S}.Fab) (width 0.1))
      (fp_circle (center 0 0) (end 2.9 0) (layer ${S}.CrtYd) (width 0.05))
      (fp_circle (center 0 0) (end 2.85 0) (layer ${S}.SilkS) (width 0.12))
      (pad "" np_thru_hole circle (at 0 0 ${p.r}) (size 3.0 3.0) (drill 3.0) (layers *.Cu *.Mask))
      (pad "1" smd circle (at 0 0 ${p.r}) (size 5.3 5.3) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      )
    `
  }
}
