// 自動生成: tools/import_footprints.py (XIAO-nRF52840-Plus-SMD.kicad_mod から)
// 元データ: Seeed Studio OPL_Kicad_Library (https://github.com/Seeed-Studio/OPL_Kicad_Library) CC-BY-SA 4.0
// KiCad のライブラリ名: Seeed_Studio_XIAO_Series:XIAO-nRF52840-Plus-SMD
// 
//
// side: 'F' = 基板の表 / 'B' = 基板の裏 (上から見て裏返しの形になる)
// パッド番号とつながり: 1=D0, 2=D1, 3=D2, 4=D3, 5=D4, 6=D5, 7=D6, 8=D7, 9=D8, 10=D9, 11=D10, 12=V3V3, 13=GND, 14=VBUS, 15=D11, 16=D12, 17=D13, 18=D14, 19=D15, 20=D16, 21=D17, 22=D18, 23=D19, 24=SWDIO, 25=SWDCLK, 26=EN, 27=GND, 28=BATP, 29=GND
module.exports = {
  params: {
    designator: 'MCU',
    side: 'F',
    BATP: { type: 'net', value: '' },
    D0: { type: 'net', value: '' },
    D1: { type: 'net', value: '' },
    D10: { type: 'net', value: '' },
    D11: { type: 'net', value: '' },
    D12: { type: 'net', value: '' },
    D13: { type: 'net', value: '' },
    D14: { type: 'net', value: '' },
    D15: { type: 'net', value: '' },
    D16: { type: 'net', value: '' },
    D17: { type: 'net', value: '' },
    D18: { type: 'net', value: '' },
    D19: { type: 'net', value: '' },
    D2: { type: 'net', value: '' },
    D3: { type: 'net', value: '' },
    D4: { type: 'net', value: '' },
    D5: { type: 'net', value: '' },
    D6: { type: 'net', value: '' },
    D7: { type: 'net', value: '' },
    D8: { type: 'net', value: '' },
    D9: { type: 'net', value: '' },
    EN: { type: 'net', value: '' },
    GND: { type: 'net', value: '' },
    SWDCLK: { type: 'net', value: '' },
    SWDIO: { type: 'net', value: '' },
    V3V3: { type: 'net', value: '' },
    VBUS: { type: 'net', value: '' },
  },
  body: p => {
    const back = p.side == 'B'
    const S = back ? 'B' : 'F'
    const O = back ? 'F' : 'B'
    const fx = v => v
    const fy = v => back ? -v : v
    const fa = v => back ? -v : v
    return `
      (module "Seeed_Studio_XIAO_Series:XIAO-nRF52840-Plus-SMD" (layer ${S}.Cu) (tedit 0)
      ${p.at}
      (fp_text reference "${p.ref}" (at ${fx(11.225)} ${fy(-0.075)} ${p.r}) (layer ${S}.SilkS) ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15)) ${back ? '(justify mirror)' : ''}))
      (fp_text value "XIAO-nRF52840-Plus-SMD" (at 0 0 ${p.r}) (layer ${S}.Fab) hide (effects (font (size 0.8 0.8) (thickness 0.12)) ${back ? '(justify mirror)' : ''}))
      (fp_line (start ${fx(-10.414)} ${fy(-6.985)}) (end ${fx(-10.414)} ${fy(6.985)}) (layer ${S}.SilkS) (width 0.1))
      (fp_line (start ${fx(-8.509)} ${fy(-8.89)}) (end ${fx(8.636)} ${fy(-8.89)}) (layer ${S}.SilkS) (width 0.1))
      (fp_line (start ${fx(-8.509)} ${fy(8.89)}) (end ${fx(8.636)} ${fy(8.89)}) (layer ${S}.SilkS) (width 0.1))
      (fp_line (start ${fx(10.541)} ${fy(-4.495)}) (end ${fx(11.551272)} ${fy(-4.491272)}) (layer ${S}.SilkS) (width 0.127))
      (fp_line (start ${fx(10.541)} ${fy(6.985)}) (end ${fx(10.541)} ${fy(-6.985)}) (layer ${S}.SilkS) (width 0.1))
      (fp_line (start ${fx(11.551)} ${fy(4.504)}) (end ${fx(10.541)} ${fy(4.504)}) (layer ${S}.SilkS) (width 0.127))
      (fp_line (start ${fx(12.051)} ${fy(-3.991272)}) (end ${fx(12.051)} ${fy(4.004)}) (layer ${S}.SilkS) (width 0.127))
      (fp_arc (start ${fx(-10.414)} ${fy(-6.985)}) (mid ${fx(-9.856038)} ${fy(-8.332038)}) (end ${fx(-8.509)} ${fy(-8.89)}) (layer ${S}.SilkS) (width 0.1))
      (fp_arc (start ${fx(-8.509)} ${fy(8.89)}) (mid ${fx(-9.856038)} ${fy(8.332038)}) (end ${fx(-10.414)} ${fy(6.985)}) (layer ${S}.SilkS) (width 0.1))
      (fp_arc (start ${fx(8.64)} ${fy(-8.89)}) (mid ${fx(9.987038)} ${fy(-8.332038)}) (end ${fx(10.545)} ${fy(-6.985)}) (layer ${S}.SilkS) (width 0.1))
      (fp_arc (start ${fx(10.541)} ${fy(6.985)}) (mid ${fx(9.983024)} ${fy(8.332024)}) (end ${fx(8.636)} ${fy(8.89)}) (layer ${S}.SilkS) (width 0.1))
      (fp_arc (start ${fx(11.551272)} ${fy(-4.491272)}) (mid ${fx(11.904644)} ${fy(-4.344724)}) (end ${fx(12.051)} ${fy(-3.991272)}) (layer ${S}.SilkS) (width 0.127))
      (fp_arc (start ${fx(12.051)} ${fy(4.004)}) (mid ${fx(11.904524)} ${fy(4.357524)}) (end ${fx(11.551)} ${fy(4.504)}) (layer ${S}.SilkS) (width 0.127))
      (fp_circle (center ${fx(9.408)} ${fy(-7.826)}) (end ${fx(9.662)} ${fy(-7.826)}) (layer ${S}.SilkS) (width 0.5))
      (fp_circle (center ${fx(10.125)} ${fy(-9.1)}) (end ${fx(10.379)} ${fy(-9.1)}) (layer ${S}.SilkS) (width 0.5))
      (fp_line (start ${fx(-10.4)} ${fy(-8.9)}) (end ${fx(10.55)} ${fy(-8.9)}) (layer ${S}.CrtYd) (width 0.05))
(fp_line (start ${fx(10.55)} ${fy(-8.9)}) (end ${fx(10.55)} ${fy(8.9)}) (layer ${S}.CrtYd) (width 0.05))
(fp_line (start ${fx(10.55)} ${fy(8.9)}) (end ${fx(-10.4)} ${fy(8.9)}) (layer ${S}.CrtYd) (width 0.05))
(fp_line (start ${fx(-10.4)} ${fy(8.9)}) (end ${fx(-10.4)} ${fy(-8.9)}) (layer ${S}.CrtYd) (width 0.05))
      (fp_line (start ${fx(-10.4)} ${fy(-8.9)}) (end ${fx(10.55)} ${fy(-8.9)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(10.55)} ${fy(-8.9)}) (end ${fx(10.55)} ${fy(8.9)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(10.55)} ${fy(8.9)}) (end ${fx(-10.4)} ${fy(8.9)}) (layer ${S}.Fab) (width 0.1))
(fp_line (start ${fx(-10.4)} ${fy(8.9)}) (end ${fx(-10.4)} ${fy(-8.9)}) (layer ${S}.Fab) (width 0.1))
      (pad "1" smd roundrect (at ${fx(7.62)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D0 || ''})
      (pad "2" smd roundrect (at ${fx(5.08)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D1 || ''})
      (pad "3" smd roundrect (at ${fx(2.54)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D2 || ''})
      (pad "4" smd roundrect (at ${fx(0)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D3 || ''})
      (pad "5" smd roundrect (at ${fx(-2.54)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D4 || ''})
      (pad "6" smd roundrect (at ${fx(-5.08)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D5 || ''})
      (pad "7" smd roundrect (at ${fx(-7.62)} ${fy(-8.255)} ${p.r + fa(90)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D6 || ''})
      (pad "8" smd roundrect (at ${fx(-7.62)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D7 || ''})
      (pad "9" smd roundrect (at ${fx(-5.08)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D8 || ''})
      (pad "10" smd roundrect (at ${fx(-2.54)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D9 || ''})
      (pad "11" smd roundrect (at ${fx(0)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D10 || ''})
      (pad "12" smd roundrect (at ${fx(2.54)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.V3V3 || ''})
      (pad "13" smd roundrect (at ${fx(5.08)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.GND || ''})
      (pad "14" smd roundrect (at ${fx(7.62)} ${fy(8.255)} ${p.r + fa(270)}) (size 2.032 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.VBUS || ''})
      (pad "15" smd roundrect (at ${fx(6.35)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D11 || ''})
      (pad "16" smd roundrect (at ${fx(3.81)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D12 || ''})
      (pad "17" smd roundrect (at ${fx(1.27)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D13 || ''})
      (pad "18" smd roundrect (at ${fx(-1.27)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D14 || ''})
      (pad "19" smd roundrect (at ${fx(-3.81)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D15 || ''})
      (pad "20" smd roundrect (at ${fx(-6.35)} ${fy(-8.655)} ${p.r + fa(90)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D16 || ''})
      (pad "21" smd roundrect (at ${fx(-6.35)} ${fy(8.655)} ${p.r + fa(270)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D17 || ''})
      (pad "22" smd roundrect (at ${fx(-3.81)} ${fy(8.655)} ${p.r + fa(270)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D18 || ''})
      (pad "23" smd roundrect (at ${fx(-1.27)} ${fy(8.655)} ${p.r + fa(270)}) (size 1.232 0.95) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.D19 || ''})
      (pad "24" smd circle (at ${fx(8.5725)} ${fy(-1.27)} ${p.r + fa(270)}) (size 1.7 1.7) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.SWDIO || ''})
      (pad "25" smd circle (at ${fx(8.5725)} ${fy(1.27)} ${p.r + fa(270)}) (size 1.7 1.7) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.SWDCLK || ''})
      (pad "26" smd circle (at ${fx(6.0325)} ${fy(-1.27)} ${p.r + fa(270)}) (size 1.7 1.7) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.EN || ''})
      (pad "27" smd circle (at ${fx(6.0325)} ${fy(1.27)} ${p.r + fa(270)}) (size 1.7 1.7) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.GND || ''})
      (pad "28" smd roundrect (at ${fx(-5.517823)} ${fy(-0.993988)} ${p.r + fa(180)}) (size 2.5 1.1) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.BATP || ''})
      (pad "29" smd roundrect (at ${fx(-5.517823)} ${fy(1.006012)} ${p.r + fa(180)}) (size 2.5 1.1) (roundrect_rratio 0.1) (layers ${S}.Cu ${S}.Mask ${S}.Paste) ${p.GND || ''})
      (pad "28" thru_hole circle (at ${fx(-5.517823)} ${fy(-0.993988)} ${p.r}) (size 1.1 1.1) (drill 0.7) (layers *.Cu *.Mask) ${p.BATP || ''})
      )
    `
  }
}
