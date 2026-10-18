// 自動生成: tools/import_footprints.py (SW_SPDT_PCM12.kicad_mod から)
// 元データ: KiCad 標準ライブラリ (CC-BY-SA 4.0 + 例外)
// KiCad のライブラリ名: Button_Switch_SMD:SW_SPDT_PCM12
// Ultraminiature Surface Mount Slide Switch, right-angle, https://www.ckswitches.com/media/1424/pcm.pdf
//
// side: 'F' = 基板の表 / 'B' = 基板の裏 (上から見て裏返しの形になる)
// パッド番号とつながり: 1=from, 2=to, 3=off
module.exports = {
  params: {
    designator: 'PWR',
    side: 'F',
    from: { type: 'net', value: '' },
    off: { type: 'net', value: '' },
    to: { type: 'net', value: '' },
  },
  body: p => {
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    const fx = v => v
    const fy = v => back ? -v : v
    const fa = v => back ? -v : v
    return `
      (module "Button_Switch_SMD:SW_SPDT_PCM12" (layer ${S}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at ${fx(0)} ${fy(-3.2)} ${p.r}) (layer ${S}.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) ${back ? '(justify mirror)' : ''}))
      (fp_text value "SW_SPDT_PCM12" (at 0 0 ${p.r}) (layer ${S}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12)) ${back ? '(justify mirror)' : ''}))
      (fp_line (start ${fx(-3.45)} ${fy(-0.07)}) (end ${fx(-3.45)} ${fy(0.72)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-2.85)} ${fy(1.73)}) (end ${fx(2.85)} ${fy(1.73)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-1.6)} ${fy(-1.12)}) (end ${fx(0.1)} ${fy(-1.12)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-1.4)} ${fy(1.73)}) (end ${fx(-1.4)} ${fy(3.02)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-1.4)} ${fy(3.02)}) (end ${fx(-1.2)} ${fy(3.23)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-1.2)} ${fy(3.23)}) (end ${fx(-0.3)} ${fy(3.23)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-0.1)} ${fy(3.02)}) (end ${fx(-0.3)} ${fy(3.23)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-0.1)} ${fy(3.02)}) (end ${fx(-0.1)} ${fy(1.73)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(1.4)} ${fy(-1.12)}) (end ${fx(1.6)} ${fy(-1.12)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(3.45)} ${fy(0.72)}) (end ${fx(3.45)} ${fy(-0.07)}) (layer ${S}.SilkS) (width 0.12))
      (fp_line (start ${fx(-4.4)} ${fy(-2.45)}) (end ${fx(4.4)} ${fy(-2.45)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-4.4)} ${fy(2.1)}) (end ${fx(-4.4)} ${fy(-2.45)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-1.65)} ${fy(2.1)}) (end ${fx(-4.4)} ${fy(2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-1.65)} ${fy(3.4)}) (end ${fx(-1.65)} ${fy(2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(1.65)} ${fy(2.1)}) (end ${fx(1.65)} ${fy(3.4)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(1.65)} ${fy(3.4)}) (end ${fx(-1.65)} ${fy(3.4)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.4)} ${fy(-2.45)}) (end ${fx(4.4)} ${fy(2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(4.4)} ${fy(2.1)}) (end ${fx(1.65)} ${fy(2.1)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-3.35)} ${fy(-1)}) (end ${fx(-3.35)} ${fy(1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-3.35)} ${fy(1.6)}) (end ${fx(3.35)} ${fy(1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-1.4)} ${fy(1.65)}) (end ${fx(-1.4)} ${fy(2.95)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-1.4)} ${fy(2.95)}) (end ${fx(-1.2)} ${fy(3.15)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-1.2)} ${fy(3.15)}) (end ${fx(-0.35)} ${fy(3.15)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-0.35)} ${fy(3.15)}) (end ${fx(-0.15)} ${fy(2.95)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-0.15)} ${fy(2.95)}) (end ${fx(-0.1)} ${fy(2.9)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(-0.1)} ${fy(2.9)}) (end ${fx(-0.1)} ${fy(1.6)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.35)} ${fy(-1)}) (end ${fx(-3.35)} ${fy(-1)}) (layer ${S}.Fab) (width 0.1))
      (fp_line (start ${fx(3.35)} ${fy(1.6)}) (end ${fx(3.35)} ${fy(-1)}) (layer ${S}.Fab) (width 0.1))
      (pad "" smd rect (at ${fx(-3.65)} ${fy(-0.78)} ${p.r + fa(0)}) (size 1 0.8) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "" smd rect (at ${fx(-3.65)} ${fy(1.43)} ${p.r + fa(0)}) (size 1 0.8) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "" np_thru_hole circle (at ${fx(-1.5)} ${fy(0.33)} ${p.r + fa(0)}) (size 0.9 0.9) (drill 0.9) (layers *.Cu *.Mask))
      (pad "" np_thru_hole circle (at ${fx(1.5)} ${fy(0.33)} ${p.r + fa(0)}) (size 0.9 0.9) (drill 0.9) (layers *.Cu *.Mask))
      (pad "" smd rect (at ${fx(3.65)} ${fy(-0.78)} ${p.r + fa(0)}) (size 1 0.8) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "" smd rect (at ${fx(3.65)} ${fy(1.43)} ${p.r + fa(0)}) (size 1 0.8) (layers ${S}.Cu ${S}.Mask ${S}.Paste))
      (pad "1" smd rect (at ${fx(-2.25)} ${fy(-1.43)} ${p.r + fa(0)}) (size 0.7 1.5) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.from || ''})
      (pad "2" smd rect (at ${fx(0.75)} ${fy(-1.43)} ${p.r + fa(0)}) (size 0.7 1.5) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.to || ''})
      (pad "3" smd rect (at ${fx(2.25)} ${fy(-1.43)} ${p.r + fa(0)}) (size 0.7 1.5) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.off || ''})
      (model "\${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step")
      )
    `
  }
}
