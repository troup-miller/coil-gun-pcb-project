# IGBT PCB — KiCad Project Hand-off

This folder contains a KiCad 7+ project generated from the validated schematic
(`../igbt_schematic.svg` and `../igbt_schematic_notes.md`).

The goal: give you a clean starting point that you open in KiCad, refine,
and route into fab-ready Gerbers, rather than wrestling with the hand-rolled
Gerbers in `../gerber/` which had three known shorts.

## Files

| File | Purpose |
|------|---------|
| `igbt_pcb.kicad_pro` | KiCad project file. Open this in KiCad first. |
| `igbt_pcb.kicad_pcb` | PCB layout with all 26 components placed at their intended positions, ratsnest visible, **no traces yet**. Open in pcbnew. |
| `igbt_pcb.net` | KiCad EESchema-format netlist. 11 nets, 46 pin connections. Defines what connects to what. |
| `igbt_pcb_bom.csv` | Bill of materials with refdes, value, footprint, description. |

## How to use

### Path A: Open the PCB and route directly (fastest)

1. Open KiCad → File → Open Project → select `igbt_pcb.kicad_pro`
2. Open the PCB editor (pcbnew): click `igbt_pcb.kicad_pcb`
3. Components are pre-placed at the coordinates from the schematic intent.
4. **Update footprints from library:** Tools → Update Footprints from Library.
   The footprint *names* in this file are real KiCad library names; pcbnew
   will pull in proper pad geometry, courtyards, silk, etc. on this step.
5. Look at the ratsnest (thin blue lines between pads). Route them as traces
   using your preferred method:
   - Manual: select start pad, "X" to draw track, follow ratsnest
   - Autorouter: Tools → External Plugin → FreeRouting (if installed)
   - Or export to FreeRouting (.dsn export), route, re-import the .ses session
6. Layout intent priorities (from `../igbt_schematic_notes.md` §6):
   - Bottom layer (B.Cu): fill with a continuous **POWER_GROUND** zone (Add Filled Zone → Net = POWER_GROUND → layer = B.Cu)
   - Snubber loop (C1↔R4↔Q1.P3/P4) area < 2 cm²
   - Kelvin lane (Q1.P2 → R3.P2 → D2.P2 → C2.P2 → C3.P2 → U1.P5 → J3) thin and dedicated
   - Twisted pair GATE/KELVIN running from U1 down to Q1
   - Decap caps C2 and C3 within 5 mm of U1.P8/P5
7. Run DRC (design rule check): Inspect → Design Rules Checker.
   Project rules are pre-set: min clearance 0.5 mm, min annular ring 0.25 mm.
8. Generate Gerbers: File → Plot → Layers: F.Cu, B.Cu, F.SilkS, F.Mask, B.Mask, Edge.Cuts → Plot. Then File → Plot → Generate Drill Files.
9. Zip the Gerber + drill files and upload to PCBWay.

### Path B: Import netlist into a fresh KiCad project (cleanest)

If you'd rather start with a clean slate:

1. Open KiCad → New Project → `igbt_pcb_v2.kicad_pro`
2. Open the schematic editor (eeschema). Don't bother drawing — File → Import → Non-KiCad Netlist → select `igbt_pcb.net`. KiCad will create components based on the netlist.
3. Open pcbnew → File → Update PCB from Schematic. Components appear; place them following layout intent.
4. Continue as in Path A from step 5.

## Footprints used (all from KiCad's default libraries)

| Refdes | Component | Footprint |
|--------|-----------|-----------|
| Q1 | MM75GAU65BKX IGBT | `Package_TO_SOT_THT:TO-247-4_Vertical` |
| U1 | HCPL-3120 driver | `Package_DIP:DIP-8_W7.62mm` |
| D1 | C3D30065D FW diode | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| D2 | SMBJ18CA TVS | `Diode_SMD:D_SMB` |
| C1 | 0.47µF snubber pulse cap | `Capacitor_THT:C_Rect_L18.0mm_W5.0mm_P15.00mm` |
| C2 | 0.1µF decap | `Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm` |
| C3 | 10µF decap | `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm` |
| R1–R3 | Axial resistors | `Resistor_THT:R_Axial_DIN0207_*` |
| R4 | MP930 snubber damper | `Resistor_THT:R_Axial_DIN0411_*` |
| R5 | Braking resistor | `Resistor_THT:R_Axial_DIN0414_*` |
| J1 | RPi 2-pos terminal | `Connector_PinHeader_5.08mm:PinHeader_1x02_P5.08mm_Vertical` |
| J2, J3 | 1-pos terminals | `TerminalBlock:TerminalBlock_bornier-1_P5.08mm` |
| J4, J5 | 16 AWG wire holes | `TestPoint:TestPoint_THTPad_D4.0mm_Drill3.2mm` |
| TP1–TP9 | Voltmeter probe points | `TestPoint:TestPoint_Pad_D1.5mm` |

If any footprint isn't found in your KiCad install, substitute with the
nearest equivalent — pad pitches are documented in the BOM CSV.

## Net summary

11 nets. The critical isolation requirement:
**KELVIN_RETURN** and **POWER_GROUND** share no copper. They meet only inside Q1's die.

| Net | Members (refdes.pin) |
|-----|----------------------|
| INPUT_VPLUS | J1.1, R1.1 |
| INPUT_GND | J1.2, U1.3 |
| LED_ANODE | R1.2, U1.2 |
| VCC | U1.8, J2.1, C2.1, C3.1, TP1.1 |
| KELVIN_RETURN | U1.5, J3.1, C2.2, C3.2, R3.2, D2.2, Q1.2, TP2.1, TP4.1 |
| GATE_DRIVE_HOT | U1.6, U1.7, R2.1 |
| GATE | R2.2, R3.1, D2.1, Q1.1, TP3.1 |
| POWER_GROUND | J4.1, Q1.3, C1.1, D1.1, D1.3, TP7.1, TP8.1, TP9.1 |
| COLLECTOR | Q1.4, R4.1, R5.1, TP5.1 |
| SNUB_INTERMEDIATE | R4.2, C1.2 |
| FLYBACK_HIGH | R5.2, D1.2, J5.1, TP6.1 |

## Pre-set design rules

The project file ships with these constraints baked in:

- Min copper-to-copper clearance: **0.5 mm**
- Min track width: 0.3 mm
- Min through-hole diameter: 0.3 mm
- Min hole-to-hole spacing: 0.25 mm
- Min annular ring: **0.25 mm**

These match the spec you gave me earlier.

## Verification before fab

After routing, before exporting Gerbers, run all three:
1. **DRC (Design Rule Check)** — must report 0 unresolved violations
2. **ERC (Electrical Rules Check)** — verify nothing was disconnected during placement
3. **3D viewer** — visually confirm component placement makes physical sense

Then plot Gerbers with the following layers selected:
- F.Cu, B.Cu, F.SilkS, F.Mask, B.Mask, Edge.Cuts
- Drill: File → Generate Drill Files → Excellon, Metric units

## Known unknowns

The same five open questions from `../igbt_schematic_notes.md` §8 apply:
switching frequency, coil inductance, brake-resistor value, TVS necessity,
isolated 15 V supply spec.
