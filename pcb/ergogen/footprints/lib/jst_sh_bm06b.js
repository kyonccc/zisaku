// 自動生成: tools/import_footprints.py (JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical.kicad_mod から)
// 元データ: KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)
// KiCad のライブラリ名: Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical
// JST SH series connector, BM06B-SRSS-TB (http://www.jst-mfg.com/product/pdf/eng/eSH.pdf)
//
// side: 'F' = 基板の表 / 'B' = 基板の裏 (上から見て裏返しの形になる)
// パッド番号とつながり: 1=P1, 2=P2, 3=P3, 4=P4, 5=P5, 6=P6
module.exports = {
  params: {
    designator: 'J',
    side: 'F',
    P1: { type: 'net', value: '' },
    P2: { type: 'net', value: '' },
    P3: { type: 'net', value: '' },
    P4: { type: 'net', value: '' },
    P5: { type: 'net', value: '' },
    P6: { type: 'net', value: '' },
  },
  body: p => {
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    const fx = v => v
    const fy = v => back ? -v : v
    const fa = v => back ? -v : v
    return `
      (module "Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical" (layer ${S}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at ${fx(0)} ${fy(-3.3)} ${p.r}) (layer ${S}.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) ${back ? '(justify mirror)' : ''}))
      (fp_text value "JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical" (at 0 0 ${p.r}) (layer ${S}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12)) ${back ? '(justify mirror)' : ''}))
      (fp_line (start ${fx(-4.11)} ${fy(-0.04)}) (end ${fx(-4.11)} ${fy(1.11)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-4.11)} ${fy(1.11)}) (end ${fx(-3.06)} ${fy(1.11)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-3.06)} ${fy(1.11)}) (end ${fx(-3.06)} ${fy(2.1)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-2.94)} ${fy(-2.01)}) (end ${fx(2.94)} ${fy(-2.01)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(4.11)} ${fy(-0.04)}) (end ${fx(4.11)} ${fy(1.11)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(4.11)} ${fy(1.11)}) (end ${fx(3.06)} ${fy(1.11)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-4.9)} ${fy(-2.6)}) (end ${fx(-2.69)} ${fy(-2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.9)} ${fy(0.2)}) (end ${fx(-4.9)} ${fy(-2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.5)} ${fy(0.2)}) (end ${fx(-4.9)} ${fy(0.2)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.5)} ${fy(1.5)}) (end ${fx(-4.5)} ${fy(0.2)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-3.3)} ${fy(1.5)}) (end ${fx(-4.5)} ${fy(1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-3.3)} ${fy(2.6)}) (end ${fx(-3.3)} ${fy(1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.69)} ${fy(-2.6)}) (end ${fx(-2.69)} ${fy(-2.4)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-2.69)} ${fy(-2.4)}) (end ${fx(2.69)} ${fy(-2.4)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.69)} ${fy(-2.6)}) (end ${fx(4.9)} ${fy(-2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(2.69)} ${fy(-2.4)}) (end ${fx(2.69)} ${fy(-2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(3.3)} ${fy(1.5)}) (end ${fx(3.3)} ${fy(2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(3.3)} ${fy(2.6)}) (end ${fx(-3.3)} ${fy(2.6)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.5)} ${fy(0.2)}) (end ${fx(4.5)} ${fy(1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.5)} ${fy(1.5)}) (end ${fx(3.3)} ${fy(1.5)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.9)} ${fy(-2.6)}) (end ${fx(4.9)} ${fy(0.2)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.9)} ${fy(0.2)}) (end ${fx(4.5)} ${fy(0.2)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4)} ${fy(-1.9)}) (end ${fx(4)} ${fy(-1.9)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-4)} ${fy(1)}) (end ${fx(-4)} ${fy(-1.9)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-4)} ${fy(1)}) (end ${fx(4)} ${fy(1)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3)} ${fy(1)}) (end ${fx(-2.5)} ${fy(0.292893)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.5)} ${fy(0.292893)}) (end ${fx(-2)} ${fy(1)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(4)} ${fy(1)}) (end ${fx(4)} ${fy(-1.9)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-2.65)} ${fy(-1.55)}) (end ${fx(-2.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-2.35)} ${fy(-1.55)}) (end ${fx(-2.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-2.35)} ${fy(-0.95)}) (end ${fx(-2.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-2.65)} ${fy(-0.95)}) (end ${fx(-2.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-1.65)} ${fy(-1.55)}) (end ${fx(-1.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-1.35)} ${fy(-1.55)}) (end ${fx(-1.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-1.35)} ${fy(-0.95)}) (end ${fx(-1.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-1.65)} ${fy(-0.95)}) (end ${fx(-1.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-0.65)} ${fy(-1.55)}) (end ${fx(-0.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-0.35)} ${fy(-1.55)}) (end ${fx(-0.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-0.35)} ${fy(-0.95)}) (end ${fx(-0.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-0.65)} ${fy(-0.95)}) (end ${fx(-0.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(0.35)} ${fy(-1.55)}) (end ${fx(0.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(0.65)} ${fy(-1.55)}) (end ${fx(0.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(0.65)} ${fy(-0.95)}) (end ${fx(0.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(0.35)} ${fy(-0.95)}) (end ${fx(0.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(1.35)} ${fy(-1.55)}) (end ${fx(1.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(1.65)} ${fy(-1.55)}) (end ${fx(1.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(1.65)} ${fy(-0.95)}) (end ${fx(1.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(1.35)} ${fy(-0.95)}) (end ${fx(1.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(2.35)} ${fy(-1.55)}) (end ${fx(2.65)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(2.65)} ${fy(-1.55)}) (end ${fx(2.65)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(2.65)} ${fy(-0.95)}) (end ${fx(2.35)} ${fy(-0.95)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(2.35)} ${fy(-0.95)}) (end ${fx(2.35)} ${fy(-1.55)}) (layer ${S}.Fab) (width 0.1))
      (pad "1" smd roundrect (at ${fx(-2.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P1 || ''})
      (pad "2" smd roundrect (at ${fx(-1.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P2 || ''})
      (pad "3" smd roundrect (at ${fx(-0.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P3 || ''})
      (pad "4" smd roundrect (at ${fx(0.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P4 || ''})
      (pad "5" smd roundrect (at ${fx(1.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P5 || ''})
      (pad "6" smd roundrect (at ${fx(2.5)} ${fy(1.325)} ${p.r + fa(0)}) (size 0.6 1.55) (roundrect_rratio 0.25) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.P6 || ''})
      (pad "MP" smd roundrect (at ${fx(-3.8)} ${fy(-1.2)} ${p.r + fa(0)}) (size 1.2 1.8) (roundrect_rratio 0.208333) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "MP" smd roundrect (at ${fx(3.8)} ${fy(-1.2)} ${p.r + fa(0)}) (size 1.2 1.8) (roundrect_rratio 0.208333) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (model "\${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical.step")
      )
    `
  }
}
