// 自動生成: tools/import_footprints.py (Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal.kicad_mod から)
// 元データ: KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)
// KiCad のライブラリ名: Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal
// Molex PicoBlade series connector, 53261-0271 (http://www.molex.com/pdm_docs/sd/532610271_sd.pdf)
//
// side: 'F' = 基板の表 / 'B' = 基板の裏 (上から見て裏返しの形になる)
// パッド番号とつながり: 1=neg, 2=pos
module.exports = {
  params: {
    designator: 'BAT',
    side: 'F',
    neg: { type: 'net', value: '' },
    pos: { type: 'net', value: '' },
  },
  body: p => {
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    const fx = v => v
    const fy = v => back ? -v : v
    const fa = v => back ? -v : v
    return `
      (module "Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal" (layer ${S}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at ${fx(0)} ${fy(-4.4)} ${p.r}) (layer ${S}.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) ${back ? '(justify mirror)' : ''}))
      (fp_text value "Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal" (at 0 0 ${p.r}) (layer ${S}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12)) ${back ? '(justify mirror)' : ''}))
      (fp_line (start ${fx(-2.235)} ${fy(-1.71)}) (end ${fx(-1.285)} ${fy(-1.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-2.235)} ${fy(-1.26)}) (end ${fx(-2.235)} ${fy(-1.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-2.235)} ${fy(2.26)}) (end ${fx(-2.235)} ${fy(2.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-2.235)} ${fy(2.71)}) (end ${fx(2.235)} ${fy(2.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-1.285)} ${fy(-1.71)}) (end ${fx(-1.285)} ${fy(-3.2)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(2.235)} ${fy(-1.71)}) (end ${fx(1.285)} ${fy(-1.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(2.235)} ${fy(-1.26)}) (end ${fx(2.235)} ${fy(-1.71)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(2.235)} ${fy(2.71)}) (end ${fx(2.235)} ${fy(2.26)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-4.73)} ${fy(-1.5)}) (end ${fx(-2.63)} ${fy(-1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.73)} ${fy(2.5)}) (end ${fx(-4.73)} ${fy(-1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.13)} ${fy(2.5)}) (end ${fx(-4.73)} ${fy(2.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.13)} ${fy(2.7)}) (end ${fx(-4.13)} ${fy(2.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.63)} ${fy(-2.1)}) (end ${fx(-1.53)} ${fy(-2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.63)} ${fy(-1.5)}) (end ${fx(-2.63)} ${fy(-2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.63)} ${fy(2.7)}) (end ${fx(-4.13)} ${fy(2.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.63)} ${fy(3.1)}) (end ${fx(-2.63)} ${fy(2.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-1.53)} ${fy(-3.7)}) (end ${fx(1.53)} ${fy(-3.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-1.53)} ${fy(-2.1)}) (end ${fx(-1.53)} ${fy(-3.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(1.53)} ${fy(-3.7)}) (end ${fx(1.53)} ${fy(-2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(1.53)} ${fy(-2.1)}) (end ${fx(2.63)} ${fy(-2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.63)} ${fy(-2.1)}) (end ${fx(2.63)} ${fy(-1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.63)} ${fy(-1.5)}) (end ${fx(4.73)} ${fy(-1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.63)} ${fy(2.7)}) (end ${fx(2.63)} ${fy(3.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.63)} ${fy(3.1)}) (end ${fx(-2.63)} ${fy(3.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.13)} ${fy(2.5)}) (end ${fx(4.13)} ${fy(2.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.13)} ${fy(2.7)}) (end ${fx(2.63)} ${fy(2.7)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.73)} ${fy(-1.5)}) (end ${fx(4.73)} ${fy(2.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.73)} ${fy(2.5)}) (end ${fx(4.13)} ${fy(2.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-3.825)} ${fy(-0.4)}) (end ${fx(-3.825)} ${fy(1.4)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3.825)} ${fy(1.4)}) (end ${fx(-3.625)} ${fy(1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3.625)} ${fy(-0.6)}) (end ${fx(-3.825)} ${fy(-0.4)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3.625)} ${fy(1.6)}) (end ${fx(-3.625)} ${fy(2.2)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3.625)} ${fy(2.2)}) (end ${fx(-2.125)} ${fy(2.2)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.125)} ${fy(-1.6)}) (end ${fx(-2.125)} ${fy(2.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.125)} ${fy(-1.6)}) (end ${fx(2.125)} ${fy(-1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.125)} ${fy(-0.6)}) (end ${fx(-3.625)} ${fy(-0.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.125)} ${fy(2.6)}) (end ${fx(2.125)} ${fy(2.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-1.125)} ${fy(-1.6)}) (end ${fx(-0.625)} ${fy(-0.892893)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-0.625)} ${fy(-0.892893)}) (end ${fx(-0.125)} ${fy(-1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(2.125)} ${fy(-1.6)}) (end ${fx(2.125)} ${fy(2.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(2.125)} ${fy(-0.6)}) (end ${fx(3.625)} ${fy(-0.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.625)} ${fy(-0.6)}) (end ${fx(3.825)} ${fy(-0.4)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.625)} ${fy(1.6)}) (end ${fx(3.625)} ${fy(2.2)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.625)} ${fy(2.2)}) (end ${fx(2.125)} ${fy(2.2)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.825)} ${fy(-0.4)}) (end ${fx(3.825)} ${fy(1.4)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.825)} ${fy(1.4)}) (end ${fx(3.625)} ${fy(1.6)}) (layer ${S}.Fab) (width 0.1))
      (pad "1" smd roundrect (at ${fx(-0.625)} ${fy(-2.4)} ${p.r + fa(0)}) (size 0.8 1.6) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.neg || ''})
      (pad "2" smd roundrect (at ${fx(0.625)} ${fy(-2.4)} ${p.r + fa(0)}) (size 0.8 1.6) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.pos || ''})
      (pad "MP" smd roundrect (at ${fx(-3.175)} ${fy(0.5)} ${p.r + fa(0)}) (size 2.1 3) (roundrect_rratio 0.119048) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "MP" smd roundrect (at ${fx(3.175)} ${fy(0.5)} ${p.r + fa(0)}) (size 2.1 3) (roundrect_rratio 0.119048) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (model "\${KICAD10_3DMODEL_DIR}/Connector_Molex.3dshapes/Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal.step")
      )
    `
  }
}
