// M2 はんだ付けナット (SMT ナット) — 浮島の「下から留める」ネジを受ける。基板の裏に付ける
// kataware 用に作ったもの (販売可能)
//
// 例: Würth Elektronik WA-SMSI (M2・高さ 1.5mm 前後) など。外径 約 3.8mm 以下の品を想定。
// パッドの大きさは、買う品番のデータシートに合わせて KiCad で調整すること。
//
// - めっきの穴 φ2.4: ネジの先がナットを通り抜けても基板に当たらない
// - パッド φ5.0 (表裏): ナットを裏にはんだ付けする。表は小さい輪だけ (プレートの下に隠れる)
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
      (fp_circle (center 0 0) (end 1.9 0) (layer ${S}.Fab) (width 0.1))
      (fp_circle (center 0 0) (end 2.75 0) (layer ${S}.CrtYd) (width 0.05))
      (fp_circle (center 0 0) (end 2.7 0) (layer ${S}.SilkS) (width 0.12))
      (pad "" thru_hole circle (at 0 0 ${p.r}) (size 5.0 5.0) (drill 2.4) (layers *.Cu ${S}.Mask ${S}.Paste))
      )
    `
  }
}
