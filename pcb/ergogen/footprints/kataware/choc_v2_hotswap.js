// kataware: Kailh Choc v2 (PG1353) ホットスワップ用フットプリント (ソケットは基板の裏)
//
// Ergogen v4.1.0 内蔵の choc フットプリント (MIT License, Copyright (c) Bán Dénes) をもとに
// kataware 用に変更したもの:
//   - 中心の穴を Choc v2 用の 5.0mm に変更
//   - Choc v2 の角の足用の穴 (直径 1.6mm) を追加
//   - 側面の足 (±5.5mm) の穴は 5ピン版のために残す
//
// Nets
//    from: ソケットのパッド1 (列の線)
//    to:   ソケットのパッド2 (ダイオードへ)
module.exports = {
  params: {
    designator: 'S',
    from: undefined,
    to: undefined
  },
  body: p => `
    (module kataware_choc_v2_hotswap (layer F.Cu) (tedit 0)
    ${p.at}
    (fp_text reference "${p.ref}" (at 0 8.6) (layer B.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
    (fp_text value "" (at 0 0) (layer F.SilkS) hide (effects (font (size 1 1) (thickness 0.15))))

    ${''/* プレートの穴 (13.8mm 角) の目安 */}
    (fp_line (start -6.9 -6.9) (end 6.9 -6.9) (layer Dwgs.User) (width 0.12))
    (fp_line (start 6.9 -6.9) (end 6.9 6.9) (layer Dwgs.User) (width 0.12))
    (fp_line (start 6.9 6.9) (end -6.9 6.9) (layer Dwgs.User) (width 0.12))
    (fp_line (start -6.9 6.9) (end -6.9 -6.9) (layer Dwgs.User) (width 0.12))

    ${''/* 中心の穴 (Choc v2) */}
    (pad "" np_thru_hole circle (at 0 0) (size 5 5) (drill 5) (layers *.Cu *.Mask))
    ${''/* 側面の足 (5ピン版) */}
    (pad "" np_thru_hole circle (at 5.5 0) (size 1.9 1.9) (drill 1.9) (layers *.Cu *.Mask))
    (pad "" np_thru_hole circle (at -5.5 0) (size 1.9 1.9) (drill 1.9) (layers *.Cu *.Mask))
    ${''/* Choc v2 の角の足 */}
    (pad "" np_thru_hole circle (at -5 5.15) (size 1.6 1.6) (drill 1.6) (layers *.Cu *.Mask))

    ${''/* ホットスワップソケット (Kailh CPG135001S30) の穴とパッド: 基板の裏 */}
    (pad "" np_thru_hole circle (at 5 -3.75) (size 3 3) (drill 3) (layers *.Cu *.Mask))
    (pad "" np_thru_hole circle (at 0 -5.95) (size 3 3) (drill 3) (layers *.Cu *.Mask))
    (pad 1 smd rect (at -3.275 -5.95 ${p.r}) (size 2.6 2.6) (layers B.Cu B.Paste B.Mask) ${p.from})
    (pad 2 smd rect (at 8.275 -3.75 ${p.r}) (size 2.6 2.6) (layers B.Cu B.Paste B.Mask) ${p.to})
    )
  `
}
