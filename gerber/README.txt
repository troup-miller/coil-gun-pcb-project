IGBT PCB Gerber Files — KNOWN-BROKEN v4 SNAPSHOT
==================================================

DO NOT FAB FROM THESE FILES.

These are the in-progress PCB layout files from v4 of the iteration.
They contain three confirmed shorts.  They are kept in this folder for
visual reference only.

The AUTHORITATIVE deliverable is the schematic in the parent folder:
  ../igbt_schematic.svg     (vector — open in browser or vector editor)
  ../igbt_schematic.png     (rendered preview)
  ../igbt_schematic_notes.md (pin-by-pin netlist, BOM, design calcs, layout rules)
  ../CLAUDE.md              (handoff context for future Claude Code sessions)

Files in this gerber/ folder:
  igbt_pcb.GTL  Top copper       (top-layer routing)
  igbt_pcb.GBL  Bottom copper    (PGND pour with anti-pads)
  igbt_pcb.GTS  Top soldermask
  igbt_pcb.GBS  Bottom soldermask
  igbt_pcb.GTO  Top silkscreen
  igbt_pcb.GKO  Board outline
  igbt_pcb.DRL  Excellon drill   (all 44 through-holes, plated)

KNOWN SHORTS (visible in Top Cu when rendered in a Gerber viewer):

  1. KELVIN_RETURN bridge through Rgate1 pad
     - Veeterm-east bridge rect(37.5, 17.0, 12.0, 1.9) spans
       X=31.5..43.5 at Y=16.05..17.95
     - Rgate1 pad is centered at (38, 17) — directly in the bridge path
     - Result: KELVIN_RETURN and GATE_DRIVE are tied together at Rgate1
     - This is the issue you flagged before handoff

  2. VCC TP-stub through GATE_DRIVE bridge
     - VCC stub down to TP_VCC extends Y=8.5..12.5 at X=33.75..36.25
     - GATE_DRIVE horizontal bridge to R_gate1 runs Y=10.5..13.5
       in roughly the same X range
     - They overlap at Y=10.5..12.5 → VCC shorted to GATE_DRIVE
     - This is what you saw as "P5/P6 shorted to P8/V+" in the viewer

  3. R_brake2 / D_fly cathode islands not connected on top copper
     - Top-layer FLYBACK_HIGH strip is broken by the D_fly anode pin row
     - R_brake2 pad and D_fly Pin 2 (cathode) pad sit as floating
       islands with no top-layer connection between them
     - This is what you saw as "D_fly appears to have only one pin
       throughhole" — the cathode pad has no copper continuity

OTHER NOTES:

  - The D_fly cathode pin is intentionally bent forward 4 mm from the
    anode row (drilled at Y=34 instead of Y=38) — this was a deliberate
    layout choice to get clean isolation between anode and cathode pads
    on a TO-220 with 2.54 mm pin pitch.  The schematic accounts for this.

  - The bottom layer (.GBL) is a continuous PGND pour with anti-pads
    around every non-PGND through-hole.  This part is clean and would
    work fine — the shorts are on the top layer.

  - All annular rings are ≥ 0.5 mm (well above the 0.25 mm requirement).

  - All 8 HCPL-3120 pins are drilled, including the two NC pins (P1, P4).

RECOMMENDED PATH FORWARD:

  Use the schematic (../igbt_schematic.svg and ../igbt_schematic_notes.md)
  as the source of truth and re-route the PCB in proper EDA software
  (KiCad, Altium, EasyEDA, or PCBWay's own design service).  The
  schematic is logical-only and has zero of the shorts above.
