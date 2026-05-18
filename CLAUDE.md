# CLAUDE.md — IGBT Switching PCB Project

Handoff memory for Claude Code sessions continuing this project.

---

## Project at a glance

**Goal:** Design a high-power low-side IGBT switching circuit for an inductive coil load. The user (Troup) is moving from a "dead-bug" perfboard prototype to a manufactured PCB.

**Status:** Schematic + design notes complete. Hand-off ready. The user explicitly chose to stop after schematic and route the board themselves (probably in KiCad, then PCBWay).

**Active deliverables:** `igbt_schematic.svg`, `igbt_schematic_notes.md` — these are the authoritative documents. Everything else in this folder is historical iteration.

---

## File inventory (what's what)

### Primary deliverables (ship these)
- **`igbt_schematic.svg`** — visual schematic, 1600×1100 viewBox, all components labeled with values/ratings
- **`igbt_schematic.png`** — rendered PNG of the above for preview
- **`igbt_schematic_notes.md`** — **the authoritative document.** Pin-by-pin netlist, full BOM with part numbers + ratings, isolation rules, design calculations (R_in, R_gate, R_ge, snubber, D_fly, thermal), layout intent priority list, validation tests, 5 open questions

### Earlier iterations (historical, can be deleted)
- `igbt_pcb_etch.svg`, `gen_pcb.py`, `preview.png` — hand-etch single-sided design (v1 deliverable, superseded)
- `etch_only.svg`, `etch_only.png` — etch-only render of v1
- `render_top.png`, `render_bot.png`, `render_both.png` — Gerber renders during the abandoned PCB-fab iteration
- `verify.py`, `__pycache__/` — verification scripts

### Working scripts (in /tmp, not persistent across sessions)
- `/tmp/gen_pcb.py` — etch SVG generator
- `/tmp/gen_gerber.py`, `gen_gerber_v2.py`, `gen_v4.py` — abandoned Gerber generators
- `/tmp/gen_schematic.py` — generates `igbt_schematic.svg` (regenerate if needed)
- `/tmp/pcbway/` — abandoned Gerber output (v4 with one remaining clearance bug)

---

## Critical design constraints (DO NOT VIOLATE)

These came directly from the user and must be respected by any layout iteration.

1. **Kelvin-Emitter and Power-Emitter are two separate nets.** They meet ONLY inside the Q1 die. Never tie them together on the board.
2. **HCPL-3120 Pin 5 (Vee) connects to Kelvin-Emitter, NOT Power-Emitter.** Same for both decoupling caps' low side.
3. **R_ge (gate pulldown) and TVS sit across Gate ↔ Kelvin-E only.** Not Power-E.
4. **Snubber (C_snub in series with R_snub) sits across Collector ↔ Power-E only.** Not Kelvin-E.
5. **All through-holes:** ≥0.25 mm annular ring.
6. **All inter-net clearances:** ≥0.5 mm (so soldermask flows in cleanly).
7. **HCPL-3120 has all 8 pins drilled**, including the two NC pins (P1, P4). They get isolated annular pads.
8. **Crossovers (if needed):** the user will bridge with copper solder-wick mesh, not vias on hand-etch. For pro fab, use proper vias.

## IGBT pinout (MM75GAU65BKX, TO-247-4)

- Pin 1 = Gate
- Pin 2 = Kelvin Emitter (driver reference)
- Pin 3 = Power Emitter (load return)
- Pin 4 = Collector
- 5.45 mm pin pitch

## D_fly pinout (SiC, TO-220, A-K-A)

- Pin 1 = Anode (PGND)
- Pin 2 = Cathode (Flyback-high)
- Pin 3 = Anode (PGND)
- **In layout, bend Pin 2 forward ~4 mm** so its pad sits at a different Y from the anodes — this avoids the impossibly-tight 2.54 mm isolation channel.

## HCPL-3120 pinout (DIP-8)

- Pin 1 = NC (drill anyway)
- Pin 2 = LED Anode (input)
- Pin 3 = LED Cathode (input)
- Pin 4 = NC (drill anyway)
- Pin 5 = Vee (output side reference — Kelvin-E!)
- Pin 6 = Vo (output)
- Pin 7 = Vo (tied to P6)
- Pin 8 = Vcc (+15 V)

---

## Netlist summary (full version in `igbt_schematic_notes.md`)

| Net | Carries | Notes |
|-----|---------|-------|
| INPUT_VPLUS | ~10 mA from RPi 3.3 V | Cold/isolated |
| INPUT_GND | ~10 mA return | Cold; never join PGND |
| LED_ANODE | ~9 mA | R_in → U1 P2 |
| VCC | ~150 mA peak | +15 V to U1 P8, decap MANDATORY |
| KELVIN_RETURN | ≤150 mA gate current | Vee, U1 P5, R_ge low, Q1 P2, decap E. **NO LOAD CURRENT.** |
| GATE_DRIVE | 2.5 A transient | U1 P6/7 → R_gate → Q1 P1 |
| POWER_GROUND | ≤75 A | PSU(−), Q1 P3, C_snub low, D_fly anodes. Heavy. |
| COLLECTOR | 0..650 V swing | Q1 P4, R_snub hi, R_brake hi. Small area = small antenna. |
| SNUB_INTERMEDIATE | transient | R_snub low ↔ C_snub low |
| FLYBACK_HIGH | ≤75 A on freewheel | R_brake low, D_fly cathode, Load(−) |

---

## Conversation history / decisions made

1. **First pass:** Hand-etched single-sided board, 100×70 mm. Output: `igbt_pcb_etch.svg`. User signed off on this version.

2. **Second pass:** User requested Gerber for PCBWay. Started a 2-layer fab version with PGND pour on bottom, +decap caps added near U1.

3. **Bugs found during Gerber generation:**
   - "Needle points" from arbitrary polygons (fixed by using only axis-aligned rectangles)
   - Sub-0.5 mm clearances between adjacent net columns (fixed by narrowing pad columns to 4 mm)
   - U1 LED_ANODE pad shorted to U1P1 NC pad (fixed by moving Rin2 west to X=15 and shrinking NC pads to 1.4 mm)
   - VCC stub passed through GATE_DRIVE bridge (fixed by moving TP_VCC up to Y=4)
   - **Unresolved:** the Veeterm-east-bridge from (32,17) to the Kelvin column at X=43.45 passes directly through Rgate1 at (38,17). Routing around it requires either narrow traces (instead of broad pours) or moving U1.

4. **Hand-off decision:** Rather than keep iterating, user chose schematic-only deliverable. Routing is now the user's job (or PCBWay's design service).

---

## User preferences (from their settings)

- More technical detail is better
- Include code snippets wherever applicable
- Full-module code examples are preferred over diff-style edits
- When prompts are ambiguous, ASK rather than guess
- When analysis is inconclusive, ASK rather than guess

The user explicitly said "STOP AND ASK if confused" mid-project, and prefers to be in the driver's seat for design decisions.

---

## Open questions (asked of user, not yet answered)

These appear in `igbt_schematic_notes.md` §8 but were never resolved:

1. **Switching frequency.** Assumed 1 kHz for snubber/thermal calcs. Could be much higher.
2. **Load coil inductance.** Affects required snubber/freewheel sizing.
3. **Brake resistor value.** Default assumption: 1 Ω, 100 W ceramic non-inductive.
4. **TVS necessity.** Optional gate-clamp; user noted "Gate TVS diode" in original Plan-B description but didn't specify part.
5. **Driver supply isolation.** Recommended isolated 15 V DC-DC (Mornsun/RECOM rated 5 kV+) but not confirmed.

If a future session picks this up for layout, ask the user about these before committing geometry.

---

## If you're continuing this project

**Most likely next-step requests from the user:**

1. **"Help me lay this out in KiCad."** → Reference `igbt_schematic_notes.md` for netlist. Walk through component placement following the priority list in §6 (PGND pour first, then snubber loop, then Kelvin lane, etc.).

2. **"Pick component values for switching frequency X."** → Recalculate snubber sizing using formulas in §5. Larger frequency → smaller C_snub OR pulse-rated R_snub becomes a power problem.

3. **"Help me build a prototype to validate the schematic."** → Reference the dead-bug instructions in the original conversation. The user already has a working perfboard version they want to replace.

4. **"What's wrong with my switching waveform?"** → Use the validation tests in §7 of the notes file. Gate ringing, Collector overshoot, supply rail sag are the usual suspects.

**Stay away from:**
- Don't try to re-do the Gerber generation unless explicitly asked. The user moved away from that path.
- Don't change the isolation rules. They're load-bearing.
- Don't guess component values without checking the calculations file.

---

End of handoff memory.
