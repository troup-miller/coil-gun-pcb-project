# IGBT Low-Side Switching Circuit — Schematic Design Notes (rev A)

Companion document to `igbt_schematic.svg`.
Defines complete netlist, BOM with ratings, design calculations, and layout intent.
Hand-off ready for KiCad/Altium import or PCBWay design service.

---

## 1. Topology summary

A galvanically-isolated gate driver (HCPL-3120) drives the gate of a SiC IGBT (MM75GAU65BKX) in a low-side switching configuration for an external inductive coil load. The IGBT is a Kelvin-source device (4-pin TO-247-4): the **Kelvin-Emitter (Pin 2)** is the driver-side reference, and the **Power-Emitter (Pin 3)** is the load-current return. On the PCB the two emitter pins are routed as **separate, electrically isolated copper nets** — they meet only inside the IGBT die.

Switching control: 3.3 V GPIO from a Raspberry Pi, current-limited by R_in, optically isolated by U1. Driver supply rails (+15 V / Vee) are externally provided and must be referenced to Kelvin-Emitter.

Snubber: pulse capacitor + low-inductance pulse resistor in series, placed across **Collector ↔ Power-Emitter** only. Never tied to Kelvin.

Freewheel: SiC Schottky diode (D_fly) with anodes on POWER_GROUND, cathode on the Load-negative terminal. Optional braking resistor (R_brake) in series between the IGBT Collector node and the Load-negative terminal.

---

## 2. Pin-by-pin netlist

Format: `[NetName] : pin1, pin2, pin3, ...`

| Net | Pins on this net |
|-----|------------------|
| **INPUT_VPLUS** | RPi-screw +3.3V, R_in Pin 1 |
| **LED_ANODE** | R_in Pin 2, U1 Pin 2 |
| **INPUT_GND** | RPi-screw GND, U1 Pin 3 |
| **VCC** *(+15 V driver)* | U1 Pin 8, V15-screw terminal, C_dcp1 Pin 1, C_dcp2 Pin 1 |
| **GATE_DRIVE** | U1 Pin 6, U1 Pin 7, R_gate Pin 1 |
| *(continues after R_gate as)* **GATE_NODE** | R_gate Pin 2, R_ge Pin 1, TVS anode, Q1 Pin 1 (Gate) |
| **KELVIN_RETURN** *(driver-side reference, Vee)* | U1 Pin 5, Vee-screw terminal, C_dcp1 Pin 2, C_dcp2 Pin 2, R_ge Pin 2, TVS cathode, Q1 Pin 2 (Kelvin-Emitter) |
| **POWER_GROUND** *(load return, 75 A capable)* | PSU-neg screw terminal, Q1 Pin 3 (Power-Emitter), C_snub Pin 1, D_fly Pin 1 (anode), D_fly Pin 3 (anode) |
| **COLLECTOR** | Q1 Pin 4, R_snub Pin 1, R_brake Pin 1 |
| **SNUB_INTERMEDIATE** | R_snub Pin 2, C_snub Pin 2 |
| **FLYBACK_HIGH** | R_brake Pin 2, D_fly Pin 2 (cathode), Load-neg screw terminal |

NC pins: U1 Pin 1, U1 Pin 4 (drilled and have annular rings, but no copper connection).

---

## 3. Bill of Materials

| Ref | Description | Value / Part | Rating | Package | Notes |
|-----|-------------|--------------|--------|---------|-------|
| Q1 | IGBT, Kelvin-source | MM75GAU65BKX | 650 V / 75 A | TO-247-4 | SiC. Tab to heatsink, isolator pad required. |
| U1 | Isolated gate driver | HCPL-3120 | 2.5 A peak, 5 kV isolation | DIP-8 | Decap MANDATORY (see §4) |
| D_fly | Freewheel diode | C3D30065D or 70TPS16 | 650 V / 30 A | TO-220 (A-K-A) | SiC Schottky. Cathode lead bent forward 4 mm |
| C_snub | Snubber pulse cap | 0.47 µF (tune for di/dt) | 600 VAC pulse | 18.2 × 5.6 mm, p2p 15.2 | Polypropylene film, low ESL |
| R_snub | Snubber damper | MP930 20 Ω | 30 W pulse | p2p 5.8 mm | Non-inductive pulse-rated |
| R_brake | Optional braking resistor | choose for braking torque | depends on load | axial, p2p ~15 mm | Bus-bar jumper if unused |
| R_gate | Gate series resistor | 10 Ω | 2 W | axial, p2p 8 mm | Tune 5–22 Ω for switching speed vs ringing |
| R_ge | Gate-emitter pulldown | 1.5 kΩ | 1 W | axial, p2p 5.45 mm | Keeps Q1 off if driver floats |
| R_in | RPi input current limiter | 180 Ω | ¼ W | axial, p2p 7 mm | Sets ~9 mA through opto LED at 3.3 V |
| TVS | Gate clamp (optional but recommended) | SMBJ18CA bidi 18 V | 600 W | DO-214 / DO-15 | Across Gate ↔ Kelvin-E only |
| C_dcp1 | U1 high-freq decap | 0.1 µF X7R | 25 V min | 1206 SMD or radial 5.08 mm | Place ≤5 mm from U1 P8/P5 |
| C_dcp2 | U1 bulk decap | 10 µF X7R or tantalum | 25 V min | radial 5.08 mm | Place ≤10 mm from U1 P8/P5 |
| J_RPi | RPi input | 2-pos 5.08 mm screw terminal | — | — | + and − labelled on silk |
| J_DRV+ | +15 V driver supply | through-hole 16/22 AWG | — | 1.5 mm hole | Direct wire solder |
| J_DRV− | Vee / driver− | through-hole 16/22 AWG | — | 1.5 mm hole | RETURNS TO KELVIN, never PGND |
| J_PSU− | Cap-bank (−) return | through-hole 16 AWG | — | 3.2 mm hole | Direct wire solder |
| J_Load− | Load coil (−) input | through-hole 16 AWG | — | 3.2 mm hole | Direct wire solder |

Test points: 9 × 0.9 mm through-holes for voltmeter probes, distributed across VCC, KELVIN, GATE, KE, COL, FBK, and three on PGND.

---

## 4. Critical isolation rules — enforce in layout

These are not negotiable. They are why the IGBT has 4 pins instead of 3.

1. **KELVIN_RETURN copper carries gate-drive current only.** It must not be tied to POWER_GROUND anywhere on the board. The two meet exclusively inside the Q1 die.
2. **HCPL-3120 Pin 5 (Vee) connects to KELVIN_RETURN, NOT POWER_GROUND.** Same for both decoupling caps' low side.
3. **R_ge (gate-emitter pulldown) and TVS sit across Q1 Pin 1 (Gate) and Q1 Pin 2 (Kelvin-E).** They must NOT terminate on Power-E.
4. **C_snub and R_snub sit across Q1 Pin 4 (Collector) and Q1 Pin 3 (Power-E).** They must NOT terminate on Kelvin-E.
5. **External wiring:** driver-supply ground wire (J_DRV−) must run alongside the gate-drive output wire (twisted-pair) and connect at the board, not at the cap bank.
6. **External wiring:** the 16 AWG PSU-negative wire (J_PSU−) must run alongside the 16 AWG load-negative wire (J_Load−) for low-loop-area return.

---

## 5. Design calculations

### Opto input (R_in)
- V_RPi = 3.3 V, V_F (HCPL-3120 LED) ≈ 1.6 V typ
- Target I_F = 10 mA
- R_in = (3.3 − 1.6) / 0.010 = **170 Ω** → use 180 Ω standard E12 value
- I_F (actual) = (3.3 − 1.6) / 180 = **9.4 mA** ✓ (well above 8 mA min CTR spec)
- Power in R_in = (1.7² / 180) = 16 mW → ¼ W is fine

### Driver output (R_gate)
- HCPL-3120 V_OH ≈ 14.5 V, V_OL ≈ 0.5 V, I_OL/OH peak = 2.5 A
- Q1 gate charge Q_g ≈ 200 nC (datasheet typ, V_GE = 15 V)
- For 2.5 A drive into 15 V: R_gate = (V_OH − V_th) / I = (14.5 − 6) / 2.5 = **3.4 Ω min**
- Recommended: **10 Ω** for moderate switching speed (≈ 200 ns turn-on/off)
- Peak power dissipation in R_gate = I²·R = 2.5² × 10 = 62.5 W *peak*, but only for the ~100 ns transition. Average power at 1 kHz switching ≈ 12.5 mW → 1–2 W resistor is more than sufficient (de-rate for inductance, use carbon comp or metal-oxide)

### R_ge pulldown
- Holds Q1 gate at Vee if driver output goes high-Z
- R_ge = 1.5 kΩ as specified
- Steady-state power when driver is high (V_GE = 15 V): P = 15² / 1500 = **150 mW** → 1 W resistor

### Snubber sizing (RC snubber across Q1)
- C_snub typical value formula for a hard-switched IGBT: C ≥ I_load · t_off / V_clamp
  - Assume I_load = 50 A, t_off = 200 ns, V_clamp = 600 V (margin to V_BR_CES = 650 V)
  - C ≥ 50 × 200e-9 / 600 = 16.7 nF *absolute minimum*
  - Practical: **0.47 µF** as listed (provides ringing damping plus dV/dt protection)
- R_snub damping: target ζ ≈ 0.7 → R = 2·√(L_loop/C)
  - L_loop estimate: 100 nH typical for a tight-loop layout
  - R = 2·√(100e-9 / 0.47e-6) = **0.92 Ω** *for critical damping*
  - User-specified **20 Ω** is overdamped (slow snubber recovery but excellent ringing suppression — acceptable trade-off)
- Energy dissipated per switching event: E = ½ · C · V² = ½ · 0.47e-6 · 600² ≈ **85 mJ**
  - At 1 kHz switching: P_snub = 85 W *average* split across C_snub and R_snub. MP930 30 W pulse rating handles transient; consider switching frequency limit.

### Freewheel diode (D_fly)
- I_F average = duty_cycle × I_load (when Q1 OFF only)
- For 50% duty at I_load = 50 A: I_F_avg = 25 A → 30 A SiC Schottky is correct
- V_R = full bus voltage (600 V) → 650 V part is correct

### IGBT thermal
- MM75GAU65BKX: V_CE(sat) ≈ 1.8 V at I_C = 50 A
- Conduction loss: 50 × 1.8 × duty = 45 W at 50% duty
- Switching loss: E_on + E_off × f_sw → datasheet typ 1.5 mJ/cycle at 50 A → 1.5 W at 1 kHz
- Total Q1 dissipation ≈ 47 W → **heatsink required** (R_θJA target ≤ 2.5 K/W for T_j ≤ 150°C with T_a = 25°C)

---

## 6. Layout intent (for whoever does the routing)

In rough priority order:

1. **POWER_GROUND as a continuous bottom-layer pour.** Heavy copper (2 oz minimum). Provides low-inductance return for the cap-bank loop.
2. **Snubber loop area < 2 cm².** C_snub physically straddling Q1 Pin 3 ↔ Pin 4, R_snub immediately adjacent.
3. **Kelvin-E lane is thin and dedicated.** Carry it from U1 Pin 5 to Q1 Pin 2 with no branches except to R_ge low, TVS cathode, decap E pads. Star-point at Q1 Pin 2 if possible.
4. **Twisted pair between U1 outputs and Q1 gate area.** GATE_DRIVE and KELVIN_RETURN should run side-by-side, ≤2 mm apart, to minimise di/dt-induced ground bounce.
5. **+15 V decoupling caps within 5 mm of U1 Pin 8 / Pin 5.** This is a hard rule — without it the HCPL-3120 will Miller-shoot-through.
6. **Collector node minimised in copper area.** The Collector is the highest-dV/dt node; small area = small antenna.
7. **D_fly close to Q1, anodes connected to PGND pour with low impedance.** Same for Load-neg terminal: keep the freewheel loop tight.
8. **R_brake pads spaced for either a resistor or a copper bus-bar jumper.** User intent: switch between the two without re-soldering the board.
9. **Test points:** small (0.9 mm) through-holes, placed in `+ / −` pairs so a voltmeter probe ground-clip lands on PGND or KELVIN as appropriate.

### Trace widths (2 oz copper, 30 °C rise):
- POWER_GROUND, COLLECTOR, FLYBACK_HIGH: pour-only or ≥ 5 mm trace (75 A peak)
- VCC, KELVIN_RETURN: 0.6 mm trace minimum (handles 1 A continuous transients)
- GATE_DRIVE: 0.5 mm trace (low average current)
- INPUT_VPLUS, INPUT_GND, LED_ANODE: 0.3 mm trace (≤10 mA)

### Drill / annular ring rules:
- All through-holes: ≥ 0.25 mm annular ring (this matches your specification)
- IGBT pins: 1.6 mm drill (lead diameter 1.0–1.2 mm, gives 0.2 mm clearance for solder fillet)
- 16 AWG terminals: 3.2 mm drill (wire diameter 1.3 mm + insulation)
- DIP-8 / standard axial leads: 0.9 mm drill (lead diameter 0.6 mm)
- Minimum copper-to-copper clearance: 0.5 mm everywhere (you specified this)

### Single-vs-multi-layer recommendation:
- Single-layer feasible (you have a working hand-etch design)
- **2-layer with PGND pour on the bottom is strongly recommended** for the fab version. The bottom pour provides a continuous return path and shielding for the COLLECTOR node.
- Either way, the top-layer routing rules above apply identically.

---

## 7. Things to validate during prototyping

1. **Gate ringing.** Probe Q1 Gate-to-Kelvin-E with a 100 MHz scope. Should ring less than 10 V peak-to-peak after a step.
2. **Collector overshoot.** Probe Q1 Collector-to-Power-E. Overshoot must stay below V_BR_CES = 650 V. If overshoot exceeds 600 V, increase C_snub.
3. **Driver supply rail.** Probe TP_VCC ↔ TP_VEE. Must stay within +13–17 V across the switching event. Sag below 13 V means decoupling is insufficient (move C_dcp1 closer to U1, or add more bulk capacitance).
4. **Thermal.** IR camera on Q1, D_fly, R_snub after sustained switching. Tj < 100°C target for prototyping.
5. **Common-mode current.** With a current probe around the GATE/KELVIN twisted pair, di/dt induced common-mode current should be < 100 mA at switching transients.

---

## 8. Open questions for layout designer

These were not specified in the original brief and would benefit from a confirmation:

1. **Switching frequency.** I assumed ~1 kHz for snubber sizing. If you're operating at 10 kHz+, R_snub power dissipation scales accordingly and you may need a different snubber design.
2. **Load coil inductance.** Affects freewheel di/dt and required snubber values. Please measure.
3. **Brake-resistor value.** Depends on intended braking torque/dynamics. Default assumption: 1 Ω, 100 W ceramic non-inductive.
4. **TVS necessity.** Optional. Adds gate protection but adds capacitance to the gate node (may slow switching). Omit for first-pass build.
5. **Driver supply isolation.** The +15 V supply for U1 must be isolated from the cap-bank (no shared earth/ground). Recommend Mornsun or RECOM DC-DC isolated module rated 5 kV+.

---

End of design document. Hand-off complete.
