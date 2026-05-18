#!/usr/bin/env python3
BW, BH = 100, 70

PIN = {
    'RPi+': (5.00, 7.50), 'RPi-': (5.00, 12.58),
    'Rin1': (9.00, 7.50), 'Rin2': (17.00, 7.50),
    'U1P1': (18.73, 7.19), 'U1P2': (18.73, 9.73),
    'U1P3': (18.73, 12.27), 'U1P4': (18.73, 14.81),
    'U1P5': (26.35, 14.81), 'U1P6': (26.35, 12.27),
    'U1P7': (26.35, 9.73), 'U1P8': (26.35, 7.19),
    'V15term': (32.00, 7.19), 'Veeterm': (32.00, 17.00),
    'Rgate1': (38.00, 17.00), 'Rgate2': (38.00, 25.00),
    'Rge1': (38.00, 31.50), 'Rge2': (43.45, 31.50),
    'TVS1': (35.50, 34.50), 'TVS2': (40.50, 34.50),
    'Q1G': (38.00, 38.00), 'Q1KE': (43.45, 38.00),
    'Q1PE': (48.90, 38.00), 'Q1C': (54.35, 38.00),
    'Csnub1': (48.90, 24.00), 'Csnub2': (64.10, 24.00),
    'Rsnub1': (54.35, 30.00), 'Rsnub2': (60.15, 30.00),
    'Rbrake1': (67.00, 38.00), 'Rbrake2': (78.50, 38.00),
    'Dfly1': (84.00, 38.00),
    'Dfly2': (86.54, 34.00),    # cathode BENT FORWARD 4 mm for isolation
    'Dfly3': (89.08, 38.00),
    'PSUneg': (20.00, 60.00), 'Loadneg': (95.00, 60.00),
    'TP_VCC': (35.00, 11.00), 'TP_VEE': (44.50, 15.00),
    'TP_GATE': (35.00, 21.50), 'TP_KE': (44.50, 21.50),
    'TP_COL': (60.00, 33.50), 'TP_FBK': (75.00, 33.75),
    'TP_PGND_A': (32.00, 50.00), 'TP_PGND_B': (72.00, 55.00), 'TP_PGND_C': (88.00, 48.00),
}

DRILL = {
    'RPi+': 1.5, 'RPi-': 1.5, 'Rin1': 1.0, 'Rin2': 1.0,
    'U1P1': 0.9, 'U1P2': 0.9, 'U1P3': 0.9, 'U1P4': 0.9,
    'U1P5': 0.9, 'U1P6': 0.9, 'U1P7': 0.9, 'U1P8': 0.9,
    'V15term': 1.5, 'Veeterm': 1.5,
    'Rgate1': 1.0, 'Rgate2': 1.0, 'Rge1': 1.2, 'Rge2': 1.2,
    'TVS1': 1.0, 'TVS2': 1.0,
    'Q1G': 1.6, 'Q1KE': 1.6, 'Q1PE': 1.6, 'Q1C': 1.6,
    'Csnub1': 1.5, 'Csnub2': 1.5, 'Rsnub1': 1.0, 'Rsnub2': 1.0,
    'Rbrake1': 1.2, 'Rbrake2': 1.2,
    'Dfly1': 1.4, 'Dfly2': 1.4, 'Dfly3': 1.4,
    'PSUneg': 3.2, 'Loadneg': 3.2,
    'TP_VCC': 0.9, 'TP_VEE': 0.9, 'TP_GATE': 0.9, 'TP_KE': 0.9,
    'TP_COL': 0.9, 'TP_FBK': 0.9,
    'TP_PGND_A': 0.9, 'TP_PGND_B': 0.9, 'TP_PGND_C': 0.9,
}

def rect(cx, cy, w, h):
    return [(cx-w/2, cy-h/2), (cx+w/2, cy-h/2), (cx+w/2, cy+h/2), (cx-w/2, cy+h/2)]

NETS = {}

NETS['INPUT_VPLUS'] = [rect(7.0, 7.50, 8.5, 3.6)]

NETS['LED_ANODE'] = [
    rect(17.87, 8.46, 4.6, 3.5),
    rect(18.73, 9.73, 2.4, 2.4),
]

NETS['INPUT_GND'] = [rect(11.87, 12.55, 18.0, 3.0)]

NETS['VCC'] = [
    rect(29.17, 7.19, 7.4, 3.4),
    rect(35.0, 11.0, 2.5, 2.5),
    [(28, 8.6), (36.3, 8.6), (36.3, 12.3), (33.8, 12.3), (33.8, 8.6)],
]

NETS['GATE_DRIVE'] = [
    rect(26.35, 11.00, 3.5, 3.6),
    [(28.10, 9.40), (39.20, 13.40), (39.20, 18.60), (36.80, 18.60),
     (36.80, 14.20), (28.10, 11.60)],
    rect(38.00, 21.00, 3.6, 9.0),
    rect(35.0, 21.5, 2.5, 2.5),
    [(33.75, 20.75), (39.80, 20.75), (39.80, 22.25), (33.75, 22.25)],
    rect(38.0, 31.5, 5.0, 14.0),
    rect(35.50, 34.50, 2.5, 2.5),
    [(34.25, 33.75), (40.50, 33.75), (40.50, 35.25), (34.25, 35.25)],
    rect(38.0, 38.0, 5.0, 3.0),
]

NETS['KELVIN_RETURN'] = [
    rect(26.35, 14.81, 3.5, 3.6),
    [(28.10, 13.20), (33.50, 13.20), (33.50, 18.40), (28.10, 18.40)],
    rect(32.00, 17.00, 3.0, 3.0),
    rect(44.50, 15.00, 2.5, 2.5),
    [(33.50, 16.20), (46.00, 16.20), (46.00, 13.80), (33.50, 13.80)],
    rect(43.45, 28.00, 5.0, 24.0),
    rect(40.50, 34.50, 2.5, 2.5),
    [(39.25, 33.75), (45.95, 33.75), (45.95, 35.25), (39.25, 35.25)],
]

NETS['POWER_GROUND'] = [
    # Bottom plane (X = 4..89, Y = 40..67)
    rect(46.50, 53.50, 85.0, 27.0),
    # PGND finger UP from Q1 P3 to C_snub1
    rect(48.90, 31.50, 4.6, 15.0),
    rect(48.90, 24.00, 5.0, 4.5),
    # D_fly anode fingers - shrunken so cathode bridge can pass between
    rect(84.00, 40.00, 3.0, 6.0),                # Dfly1 anode finger
    rect(89.08, 40.00, 3.0, 6.0),                # Dfly3 anode finger
]

NETS['COLLECTOR'] = [
    rect(54.35, 38.00, 4.5, 3.0),
    rect(54.35, 33.50, 4.0, 7.0),                # FIX: covers Rsnub1 at Y=30 (Y range 30..37)
    rect(60.7, 38.00, 14.0, 3.0),
    rect(67.00, 38.00, 4.0, 3.0),
    rect(60.0, 33.5, 2.5, 2.5),
    [(58.75, 32.25), (61.25, 32.25), (61.25, 36.5), (52.35, 36.5),
     (52.35, 35.0), (58.75, 35.0)],
]

NETS['SNUBBER_INTERMEDIATE'] = [
    rect(60.15, 30.00, 3.0, 3.0),
    rect(64.10, 24.00, 3.0, 3.0),
    # Diagonal connector from R_snub2 to C_snub2
    [(58.85, 30.75), (62.85, 24.75), (65.40, 24.75),
     (65.40, 23.25), (62.85, 23.25), (61.65, 28.50), (58.85, 29.25)],
]

NETS['FLYBACK_HIGH'] = [
    # Rbrake2 pad
    rect(78.50, 38.00, 4.0, 3.0),
    # Stub up from Rbrake2 pad to the main FB strip
    rect(78.50, 36.50, 4.0, 3.0),
    # Main horizontal strip (Y=32.5..35) running TP_FBK -> over D_fly anodes -> right edge
    rect(82.50, 33.75, 23.0, 2.5),               # X = 71..94
    # TP_FBK pad (already inside strip)
    rect(75.00, 33.75, 2.5, 2.5),
    # Dfly2 cathode pad (at bent-forward position Y=34)
    rect(86.54, 34.00, 3.0, 2.5),
    # Right-edge finger from strip down to Loadneg
    rect(94.50, 50.00, 5.0, 30.0),               # X = 92..97, Y = 35..65
    rect(95.00, 60.00, 6.0, 6.0),                # Loadneg pad
]

SILK_RECTS = [
    (5.0, 10.04, 6.0, 8.5), (13.0, 7.5, 7.0, 2.6), (22.5, 11.0, 9.5, 9.5),
    (38.0, 21.0, 2.6, 7.5), (40.7, 31.5, 5.45, 2.6), (38.0, 34.5, 5.0, 2.6),
    (46.18, 55.0, 15.6, 21.0), (56.50, 24.0, 18.2, 5.6), (57.25, 30.0, 5.8, 2.6),
    (72.75, 38.0, 15.0, 2.6), (86.54, 50.0, 10.0, 15.5),
    (20.0, 64.5, 8.0, 5.0), (95.0, 64.5, 8.0, 5.0),
]
SILK_LABELS = [
    (7.0, 5.0, 'INPUT_V+', 1.1), (7.0, 16.0, 'INPUT_GND', 1.1),
    (35.0, 3.5, 'VCC +15V', 1.1), (32.0, 19.5, 'KELVIN_RTN', 1.1),
    (46.0, 26.5, 'KELVIN', 0.9), (31.0, 28.0, 'GATE_DRIVE', 1.0),
    (50.0, 45.0, 'PGND  (Net 3)', 1.4),
    (60.0, 27.5, 'COLLECTOR', 0.9), (64.5, 21.0, 'SNUB_INT', 0.9),
    (80.0, 31.0, 'FLYBACK_HIGH', 1.0),
    (50.0, 38.0, 'IGBT G KE PE C', 0.7),
    (87.0, 34.0, 'CAT (bent)', 0.6),
]

def pstr(pts):
    return ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)

out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>']
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {BW} {BH}" width="{BW}mm" height="{BH}mm">')
out.append('<title>IGBT Low-Side Switching PCB - Etch Guide v2</title>')
out.append('<desc>Black=no copper. White=copper. Drill=black dots. Units mm.</desc>')
out.append(f'<rect id="background" x="0" y="0" width="{BW}" height="{BH}" fill="black"/>')
out.append('<g id="copper" fill="white" stroke="none" shape-rendering="crispEdges">')
for n, polys in NETS.items():
    out.append(f'<g id="net-{n}">')
    for p in polys:
        out.append(f'<polygon points="{pstr(p)}"/>')
    out.append('</g>')
out.append('</g>')
out.append('<g id="drills" fill="black" stroke="none">')
for n, (x, y) in PIN.items():
    r = DRILL.get(n, 0.8) / 2.0
    out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}"/>')
out.append('</g>')
out.append('<g id="silk" fill="none" stroke="#666" stroke-width="0.15" opacity="0.55">')
for cx, cy, w, h in SILK_RECTS:
    out.append(f'<rect x="{cx-w/2:.3f}" y="{cy-h/2:.3f}" width="{w:.3f}" height="{h:.3f}"/>')
out.append('</g>')
out.append('<g id="labels" fill="#bcd" font-family="sans-serif" opacity="0.85">')
for cx, cy, txt, sz in SILK_LABELS:
    out.append(f'<text x="{cx:.3f}" y="{cy:.3f}" text-anchor="middle" font-size="{sz}">{txt}</text>')
out.append('</g>')
out.append('<g id="reg" stroke="black" stroke-width="0.2" fill="none">')
for cx, cy in [(2.5,2.5),(BW-2.5,2.5),(2.5,BH-2.5),(BW-2.5,BH-2.5)]:
    out.append(f'<line x1="{cx-1.5}" y1="{cy}" x2="{cx+1.5}" y2="{cy}"/>')
    out.append(f'<line x1="{cx}" y1="{cy-1.5}" x2="{cx}" y2="{cy+1.5}"/>')
out.append('</g>')
out.append('</svg>')

with open('/tmp/igbt_pcb_etch.svg', 'w') as f:
    f.write('\n'.join(out))
print(f'wrote {len(out)} lines; {len(NETS)} nets; {len(PIN)} pins')
