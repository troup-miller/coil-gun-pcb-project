"""
v4.2 PCB rework — IGBT low-side switching module.

Run with KiCad 10's bundled Python:
    "/mnt/c/Program Files/KiCad/10.0/bin/python.exe" rework_pcb.py

Changes vs v4.1:
1. Brake resistor R5 moved out of ballast position; D1+R5 in series across Q1
   collector-emitter (anode at Collector, cathode -> R5 -> Power-Emitter/PGND).
2. TVS D2 replaced with axial through-hole P6KE18CA (DO-15).
3. Snubber R4+C1 placed directly above Q1 PE/Collector pins.
4. HCPL-3120 decoupling caps C2/C3 hugging U1 pins 5 and 8.
5. R3 (gate-emitter pulldown) tight to Q1 Gate/Kelvin-E.
6. R2 (gate series) between U1 Vo and Q1 Gate.
7. J4 (PSU-) and J5 (Load-) on south edge for 14 AWG soldered leads.
8. All existing tracks stripped; new routing + PGND zone fills on F.Cu and B.Cu.
"""
import pcbnew
import os
import sys

mm = pcbnew.FromMM

PCB_IN  = 'C:/users/troup/repos/coil-gun-sandbox/pcb_mask_designs/cowork_layout-4pin/v4_deliverables/kicad/igbt_pcb.kicad_pcb'
PCB_OUT = PCB_IN  # save in place
FP_ROOT = 'C:/Program Files/KiCad/10.0/share/kicad/footprints'

# -----------------------------------------------------------------------------
# Layout — (x_mm, y_mm, rotation_deg). Coordinates are footprint origin.
# Board outline is (0,0) to (100,70).
# -----------------------------------------------------------------------------
PLACEMENTS = {
    # COLD / control side (left, x < 33). Isolation gap at x ~= 33..38.
    'J1':  (3.0,    6.46, 0),    # RPi GPIO header (pin1=INPUT_VPLUS at y=3.92, pin2=INPUT_GND at y=9.0)
    'R1':  (8.0,    4.0,  0),    # 180R input current limiter — horizontal (pads at 8 and 18.16)
    'U1':  (22.0,   6.0,  0),    # HCPL-3120 DIP-8 (pin1=(22,6), pin8=(29.62,6), pin5=(29.62,13.62))
    'C2':  (33.0,   9.81, 90),   # 0.1uF ceramic, vertical, across U1 pins 5 and 8
    'C3':  (38.0,   9.81, 90),   # 10uF bulk, vertical (5mm east of C2 to clear courtyard)
    'J2':  (47.0,   3.0,  0),    # +15V driver supply terminal — top edge east of C3
    'J3':  (47.0,  16.0,  0),    # Vee/KE driver return terminal — top-mid east of U1
    # HOT / power side (right, x > 38)
    'Q1':  (45.0,  38.0,  0),    # IGBT TO-247-4 (pin1=G@45, 2=KE@50.08, 3=PE@52.62, 4=C@55.16)
    'R2':  (38.0,  35.0,  0),    # 10R/2W gate-series — vertical-mount axial L7.0mm pads (0,-4)/(0,+4)
    'D2':  (43.0,  45.0,  0),    # TVS axial DO-15 (P6KE18CA), pads (0,0)/(10.16,0)
    'R3':  (43.0,  49.0,  0),    # 1.5k gate-emitter pulldown, axial horizontal
    'C1':  (62.0,  46.0,  90),   # snubber cap 0.47uF/600V — vertical, top pad ~at Q1 PE row
    'R4':  (66.0,  46.35, 90),   # snubber damper 20R/30W — vertical, top pad ~at Q1 Collector row
    'D1':  (75.0,  32.0,  0),    # flyback diode TO-220-3 (1=A, 2=K, 3=A) — body sticks UP, leads down at Y=32 row
    'R5':  (77.54, 51.5,  90),   # brake resistor — vertical, top pad ~4.2mm south of D1.2 (clear of D1 courtyard at Y<=33.55)
    # External heavy-current terminals — south edge, accessible to 14+ AWG solder leads
    'J4':  (50.0,  64.0,  0),    # PSU- pad
    'J5':  (95.0,  64.0,  0),    # Load- pad (= COLLECTOR), east edge for 14 AWG access
    # Test points — placed in clear zones away from rails
    'TP1': (54.0,   3.0,  0),    # VCC (top edge, east of J2)
    'TP2': (47.0,  22.0,  0),    # KE probe (away from COL rail at X=55.16)
    'TP3': (45.0,  29.0,  0),    # GATE probe (above Q1.1)
    'TP4': (33.0,  22.0,  0),    # spare KE probe (south of C2)
    'TP5': (70.0,  22.0,  0),    # COLLECTOR probe (north of D1)
    'TP6': (84.0,  47.0,  0),    # Brake intermediate (D1 cathode / R5 top pad)
    'TP7': (28.0,  60.0,  0),    # PGND
    'TP8': (50.0,  60.0,  0),    # PGND
    'TP9': (80.0,  60.0,  0),    # PGND
}

# Pad-net topology fix + physical-orientation pad swaps for tighter routing.
# (ref, pad_num, new_net_name). Pads not listed retain their current nets.
# Note: caps / resistors are symmetric — swapping pad-net assignments shifts
# which physical end of the part ends up on which net, without changing the
# circuit. Used here to put the "right" pad nearest the right neighbour.
PAD_NET_UPDATES = [
    # D1: anodes (pins 1, 3) now at COLLECTOR; cathode (pin 2) at brake intermediate
    ('D1',  '1', 'COLLECTOR'),
    ('D1',  '2', 'FLYBACK_HIGH'),
    ('D1',  '3', 'COLLECTOR'),
    # R5: in series with D1 cathode -> PGND.
    # In this layout R5 is vertical with pad 2 at the NORTH side (adjacent to
    # D1.2 cathode at Y=32) and pad 1 at the SOUTH side (drops into PGND pour).
    ('R5',  '1', 'POWER_GROUND'),
    ('R5',  '2', 'FLYBACK_HIGH'),
    # J5 (Load-) is now directly the COLLECTOR node (no ballast)
    ('J5',  '1', 'COLLECTOR'),
    # TP6 probes the brake intermediate
    ('TP6', '1', 'FLYBACK_HIGH'),
    # Snubber: physical layout swap so SNUB_INTERMEDIATE pads of R4 and C1 face
    # each other, and the PGND/Collector pads land where the rail/pour is.
    # R4 vertical: pad 1 at Y=46.35 (south), pad 2 at Y=33.65 (north).
    #   We want COLLECTOR side at NORTH (so the COLLECTOR rail at Y=29 taps it).
    #   We want SNUB_INTERMEDIATE side at SOUTH (so it pairs with C1.1).
    ('R4',  '1', 'SNUB_INTERMEDIATE'),
    ('R4',  '2', 'COLLECTOR'),
    # C1 vertical: pad 1 at Y=53.6 (south), pad 2 at Y=38.4 (north — just below Q1.3 PE row).
    #   We want PE/PGND side at NORTH (so it ties to Q1.3 via PGND pour).
    #   We want SNUB_INTERMEDIATE side at SOUTH (so it pairs with R4.1).
    ('C1',  '1', 'SNUB_INTERMEDIATE'),
    ('C1',  '2', 'POWER_GROUND'),
    # C2 (decoupling) swap so VCC is on the NORTH pad (closer to U1.8 at Y=6)
    # and KE is on the SOUTH pad (closer to U1.5 at Y=13.62).
    ('C2',  '1', 'KELVIN_RETURN'),
    ('C2',  '2', 'VCC'),
    ('C3',  '1', 'KELVIN_RETURN'),
    ('C3',  '2', 'VCC'),
]

# Track widths (mm). All ≥ 1.0 to satisfy 'Default' netclass min width.
TRACK_WIDTH_SIGNAL = 1.0
TRACK_WIDTH_GATE   = 1.0
TRACK_WIDTH_VCC    = 1.5
# Power widths for the flyback current path. The brake/freewheel path carries
# the coil's ≤75 A peak field-collapse current; we widen the rail anywhere
# unconstrained, and step down only at footprints whose adjacent-pad geometry
# forces it. Widths assume 0.5 mm board minimum clearance (≈400 V surface
# flashover dry, OK for the 650 V switch under transient conditions).
TRACK_WIDTH_POWER  = 2.0     # near-pad sections (Q1.3 PE side, D1.1↔D1.2↔D1.3 corridor)
TRACK_WIDTH_TRUNK  = 3.0     # COLLECTOR trunk + flyback exit to J5 (Load-)

# -----------------------------------------------------------------------------

# Footprint cache built once after all add/remove operations; populated in main().
_FP_BY_REF = {}

def find_fp(b, ref):
    if _FP_BY_REF:
        return _FP_BY_REF.get(ref)
    for fp in b.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    return None

def rebuild_fp_cache(b):
    _FP_BY_REF.clear()
    for fp in b.GetFootprints():
        _FP_BY_REF[fp.GetReference()] = fp

def add_track(b, layer, net, x1_mm, y1_mm, x2_mm, y2_mm, width_mm):
    seg = pcbnew.PCB_TRACK(b)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1_mm), mm(y1_mm)))
    seg.SetEnd  (pcbnew.VECTOR2I(mm(x2_mm), mm(y2_mm)))
    seg.SetWidth(mm(width_mm))
    seg.SetLayer(layer)
    seg.SetNet(net)
    b.Add(seg)
    return seg

def add_track_xy(b, layer, net, x1_nm, y1_nm, x2_nm, y2_nm, width_mm):
    seg = pcbnew.PCB_TRACK(b)
    seg.SetStart(pcbnew.VECTOR2I(x1_nm, y1_nm))
    seg.SetEnd  (pcbnew.VECTOR2I(x2_nm, y2_nm))
    seg.SetWidth(mm(width_mm))
    seg.SetLayer(layer)
    seg.SetNet(net)
    b.Add(seg)
    return seg

def add_via(b, x_mm, y_mm, net, drill_mm=0.4, size_mm=0.8):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
    v.SetDrill(mm(drill_mm))
    v.SetWidth(mm(size_mm))
    v.SetNet(net)
    b.Add(v)
    return v

def add_zone(b, layer, net, outline_points_mm, clearance_mm=0.3, min_thickness_mm=0.25, thermal_gap_mm=0.4):
    """Create a ZONE bound to `net`, on `layer`, with polygonal outline (mm)."""
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetLocalClearance(mm(clearance_mm))
    z.SetMinThickness(mm(min_thickness_mm))
    z.SetThermalReliefGap(mm(thermal_gap_mm))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    z.SetMinIslandArea(mm(0.05) * mm(0.05))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    # Build outline as a fresh chain in z.Outline()
    outline = z.Outline()
    outline.RemoveAllContours()
    outline.NewOutline()
    for (x, y) in outline_points_mm:
        outline.Append(mm(x), mm(y))
    # IMPORTANT: in KiCad 10's pcbnew API, SetNetCode resets to 0 if called on a
    # not-yet-board-attached zone. SetNet attaches the NETINFO_ITEM directly.
    z.SetNet(net)
    b.Add(z)
    return z


def main():
    b = pcbnew.LoadBoard(PCB_IN)
    print(f"Loaded: {len(list(b.GetFootprints()))} footprints, "
          f"{len(list(b.GetTracks()))} tracks, {b.GetAreaCount()} zones")

    # NETNAMES_MAP is keyed by wxString, easier to look up via FindNet
    def NET(name):
        n = b.FindNet(name)
        if n is None:
            raise RuntimeError(f"net not found: {name!r}")
        return n
    nets = {n: NET(n) for n in [
        'INPUT_VPLUS', 'INPUT_GND', 'LED_ANODE', 'VCC', 'KELVIN_RETURN',
        'GATE', 'GATE_DRIVE_HOT', 'COLLECTOR', 'FLYBACK_HIGH',
        'SNUB_INTERMEDIATE', 'POWER_GROUND',
    ]}
    F_Cu = pcbnew.F_Cu
    B_Cu = pcbnew.B_Cu

    # -------------------------------------------------------------------------
    # 1. Replace D2 SMD footprint with axial DO-15 P6KE18CA
    # -------------------------------------------------------------------------
    d2_old = find_fp(b, 'D2')
    if d2_old:
        d2_new = pcbnew.FootprintLoad(os.path.join(FP_ROOT, 'Diode_THT.pretty'),
                                       'D_DO-15_P10.16mm_Horizontal')
        if not d2_new:
            sys.exit("ERROR: could not load Diode_THT:D_DO-15_P10.16mm_Horizontal")
        d2_new.SetReference('D2')
        d2_new.SetValue('P6KE18CA')
        # D2 is a bidirectional TVS; nets carry over: pin1=GATE, pin2=KELVIN_RETURN
        for pad in d2_new.Pads():
            if pad.GetNumber() == '1':
                pad.SetNet(nets['GATE'])
            else:
                pad.SetNet(nets['KELVIN_RETURN'])
        b.Remove(d2_old)
        b.Add(d2_new)
        print("[1] D2 replaced: SMBJ18CA (D_SMB) -> P6KE18CA (DO-15 axial THT)")

    # -------------------------------------------------------------------------
    # 2. Apply pad-net topology updates
    # -------------------------------------------------------------------------
    print("[2] Topology fixes:")
    for ref, pad_num, new_net_name in PAD_NET_UPDATES:
        fp = find_fp(b, ref)
        if not fp:
            print(f"    WARN: {ref} not found"); continue
        net = nets.get(new_net_name)
        if not net:
            print(f"    WARN: net {new_net_name!r} missing"); continue
        for pad in fp.Pads():
            if pad.GetNumber() == pad_num:
                old = pad.GetNetname()
                pad.SetNet(net)
                print(f"    {ref}.{pad_num}: {old} -> {new_net_name}")

    # -------------------------------------------------------------------------
    # 3. Reposition footprints
    # -------------------------------------------------------------------------
    moved = 0
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if ref in PLACEMENTS:
            x, y, rot = PLACEMENTS[ref]
            # Set rotation BEFORE position so the position is the final origin
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            moved += 1
        elif ref == '':
            # The unreferenced PGND mounting-hole pad — move it to the bottom-
            # right corner so it stays as a tie-point but doesn't crowd J5/J4.
            fp.SetPosition(pcbnew.VECTOR2I(mm(75.0), mm(64.0)))
            moved += 1
    print(f"[3] Repositioned {moved} footprints")

    # -------------------------------------------------------------------------
    # 4. Strip ALL existing tracks (segments + vias)
    # -------------------------------------------------------------------------
    # Strip via DeleteAllTracks-equivalent: snapshot list, then remove
    # (caller holds Python references that prevent SwigPyObject churn)
    tracks_snapshot = [t for t in b.GetTracks()]
    n_stripped = len(tracks_snapshot)
    for t in tracks_snapshot:
        b.Remove(t)
    print(f"[4] Stripped {n_stripped} tracks/vias")

    # Rebuild footprint cache after add/remove of D2
    rebuild_fp_cache(b)
    print(f"    FP cache: {len(_FP_BY_REF)} refs")

    # Also remove any existing zones (use Zones() iterator — returns proper ZONE objects)
    zones_snapshot = [z for z in b.Zones()]
    for z in zones_snapshot:
        b.Remove(z)
    print(f"    Removed {len(zones_snapshot)} existing zones")

    # -------------------------------------------------------------------------
    # 5. Add new routing
    # -------------------------------------------------------------------------
    # Helper: get pad world position by ref + pad-number
    def P(ref, num):
        fp = find_fp(b, ref)
        if not fp: raise RuntimeError(f"missing {ref}")
        for pad in fp.Pads():
            if pad.GetNumber() == num:
                return pad.GetPosition()
        raise RuntimeError(f"missing pad {ref}.{num}")

    def line(layer, net_name, *waypoints, width=TRACK_WIDTH_SIGNAL):
        """Connect a sequence of (x_mm, y_mm) or VECTOR2I waypoints with track segments."""
        net = nets[net_name]
        pts = []
        for w in waypoints:
            if isinstance(w, pcbnew.VECTOR2I):
                pts.append(w)
            else:
                pts.append(pcbnew.VECTOR2I(mm(w[0]), mm(w[1])))
        for i in range(len(pts) - 1):
            seg = pcbnew.PCB_TRACK(b)
            seg.SetStart(pts[i]); seg.SetEnd(pts[i+1])
            seg.SetWidth(mm(width))
            seg.SetLayer(layer)
            seg.SetNet(net)
            b.Add(seg)

    # =========================================================================
    # ROUTING — F.Cu carries all signal traces + COLLECTOR / brake / snubber.
    # B.Cu is the dedicated PGND pour with through-board stitching vias.
    # F.Cu PGND zone covers the south half of the hot side around Q1/snubber/J4.
    # PE / C1.1 / R5.2 / J4 / etc. join PGND via the zone fill (thermal relief).
    # =========================================================================
    # Cache pad positions
    j11 = P('J1','1'); j12 = P('J1','2')
    r11 = P('R1','1'); r12 = P('R1','2')
    u12 = P('U1','2'); u13 = P('U1','3'); u15 = P('U1','5')
    u16 = P('U1','6'); u17 = P('U1','7'); u18 = P('U1','8')
    c21 = P('C2','1'); c22 = P('C2','2')
    c31 = P('C3','1'); c32 = P('C3','2')
    j2  = P('J2','1'); j3  = P('J3','1')
    tp1 = P('TP1','1')

    q11 = P('Q1','1'); q12 = P('Q1','2'); q13 = P('Q1','3'); q14 = P('Q1','4')
    r21 = P('R2','1'); r22 = P('R2','2')
    d21 = P('D2','1'); d22 = P('D2','2')
    r31 = P('R3','1'); r32 = P('R3','2')
    c11 = P('C1','1'); c12 = P('C1','2')
    r41 = P('R4','1'); r42 = P('R4','2')
    d11 = P('D1','1'); d12 = P('D1','2'); d13 = P('D1','3')
    r51 = P('R5','1'); r52 = P('R5','2')
    j4  = P('J4','1'); j5  = P('J5','1')
    tp3 = P('TP3','1'); tp5 = P('TP5','1'); tp6 = P('TP6','1')

    # --- COLD-SIDE signal nets ---
    # INPUT_VPLUS: J1.1 (3,3.92) -> R1.1 (8,4)
    line(F_Cu, 'INPUT_VPLUS', j11, (3.0, 4.0), r11, width=TRACK_WIDTH_SIGNAL)
    # LED_ANODE: R1.2 (18.16,4) -> U1.2 (22, 8.54). L-route.
    line(F_Cu, 'LED_ANODE',  r12, (18.16, 8.54), u12, width=TRACK_WIDTH_SIGNAL)
    # INPUT_GND: J1.2 (3,9) -> U1.3 (22, 11.08). L-route.
    line(F_Cu, 'INPUT_GND',  j12, (3.0, 11.08), u13, width=TRACK_WIDTH_SIGNAL)

    # --- VCC trunk along TOP of board (Y=3) ---
    # After pad-net swap, C2.2 (Y=4.81) and C3.2 (Y=7.31) carry VCC, both close
    # to U1.8 (Y=6).
    line(F_Cu, 'VCC', j2, tp1, width=TRACK_WIDTH_VCC)                     # J2 (47,3) -> TP1 (54,3)
    line(F_Cu, 'VCC', j2, (29.62, 3.0), u18, width=TRACK_WIDTH_VCC)       # trunk J2 west to U1.8 column
    # Decap caps beside U1.8: short jumps from U1.8 north to each VCC pad.
    line(F_Cu, 'VCC', u18, (29.62, 4.81), c22, width=TRACK_WIDTH_VCC)     # U1.8 -> C2.2 (N pad)
    line(F_Cu, 'VCC', c22, (38.0, 4.81), c32, width=TRACK_WIDTH_VCC)      # C2.2 -> C3.2

    # --- KELVIN_RETURN: single trunk east from U1.5, branches to decap / Kelvin
    # lane / external J3 ---
    # All three KE branches used to leave U1.5 heading east on overlapping
    # copper. One shared trunk now feeds C2.1 (north stub), the Kelvin sense
    # lane (south stub), and J3 (east stub), preserving the star reference at
    # U1.5 while eliminating redundant copper.
    line(F_Cu, 'KELVIN_RETURN', u15, (35.0, 13.62), width=TRACK_WIDTH_VCC)
    # Decap branch: north stub from trunk at X=33 to C2.1, then west to C3.1.
    line(F_Cu, 'KELVIN_RETURN', (33.0, 13.62), c21, width=TRACK_WIDTH_VCC)
    line(F_Cu, 'KELVIN_RETURN', c21, c31, width=TRACK_WIDTH_VCC)
    # J3 (Vee terminal) joins the trunk's south arm at (35, 16).
    line(F_Cu, 'KELVIN_RETURN', j3, (35.0, 16.0), width=TRACK_WIDTH_VCC)
    # Kelvin sense lane continues SOUTH from the shared trunk at (35, 13.62),
    # then east at Y=19, then south to Q1.2.
    line(F_Cu, 'KELVIN_RETURN',
         (35.0, 13.62),
         (35.0, 19.0),
         (50.08, 19.0),
         (50.08, 38.0),
         q12,
         width=TRACK_WIDTH_GATE)
    # Gate-emitter pulldown / TVS connections at Q1.2 side.
    # L-route to clear Q1.3 PE pad (Q1.2-D2.2 direct diagonal previously triggered
    # a clearance violation against Q1.3).
    line(F_Cu, 'KELVIN_RETURN', q12, (50.08, 45.0), d22, width=TRACK_WIDTH_GATE)   # Q1.2 -> D2.2
    line(F_Cu, 'KELVIN_RETURN', d22, r32, width=TRACK_WIDTH_GATE)                   # D2.2 -> R3.2
    # Test point stubs
    line(F_Cu, 'KELVIN_RETURN', P('TP4','1'), c21, width=TRACK_WIDTH_SIGNAL)       # TP4 (33, 22) -> C2.1 (33, 9.81)
    line(F_Cu, 'KELVIN_RETURN', P('TP2','1'), (47.0, 19.0), width=TRACK_WIDTH_SIGNAL)  # TP2 (47, 22) -> KE lane at (47, 19)

    # --- GATE_DRIVE_HOT: U1.6 + U1.7 -> R2.1, all on B.Cu ---
    # Drop south through U1.6 (same net, OK to land on its pad) before heading
    # south-east. Bend at (33.5, 12.5) keeps the trace >0.5mm clear of U1.5
    # (KE) pad and >0.5mm clear of C2's pads (both at X=33).
    line(B_Cu, 'GATE_DRIVE_HOT', u17, u16, (33.5, 12.5), r21, width=TRACK_WIDTH_GATE)

    # --- GATE: R2.2 -> Q1.1 + D2.1 + R3.1, TP3 tap ---
    line(F_Cu, 'GATE', r22, q11, width=TRACK_WIDTH_GATE)                    # R2.2 (38,39) -> Q1.1 (45,38)
    # Q1.1 (45, 38) -> D2.1 (43, 45). L-route.
    line(F_Cu, 'GATE', q11, (45.0, 42.0), (43.0, 42.0), d21, width=TRACK_WIDTH_GATE)
    line(F_Cu, 'GATE', d21, r31, width=TRACK_WIDTH_GATE)                    # D2.1 -> R3.1 (both at X=43)
    # TP3 (45, 29) probes GATE — tap from Q1.1 going north
    line(F_Cu, 'GATE', q11, (45.0, 29.0), width=TRACK_WIDTH_SIGNAL)

    # --- COLLECTOR rail / flyback path — widened for ≤75 A peak ---
    # Variable-width: narrow only where pads force it (Q1.3 PE adjacency, D1
    # cathode adjacency). Everywhere else, 3 mm trunk.
    # Step 1: Q1.4 (55.16, 38) → (55.16, 35). 2 mm wide to clear Q1.3 PE.
    line(F_Cu, 'COLLECTOR', q14, (55.16, 35.0), width=TRACK_WIDTH_POWER)
    # Step 2: trunk (55.16, 35) → (88, 24) → (88, 60) → diagonal → J5.
    # 3 mm wide for the full unconstrained run, including the J5 exit lead.
    line(F_Cu, 'COLLECTOR',
         (55.16, 35.0),
         (55.16, 24.0),
         (88.0,  24.0),
         (88.0,  60.0),
         (95.0,  64.0),
         j5,
         width=TRACK_WIDTH_TRUNK)
    # Tap to R4 COL pad (R4.2 at (66, 33.65)) — 3 mm tap, no adjacent obstacles.
    line(F_Cu, 'COLLECTOR', (66.0, 24.0), r42, width=TRACK_WIDTH_TRUNK)
    # Taps to D1.1 (75, 32) and D1.3 (80.08, 32) — narrowed to 2 mm so each
    # tap clears D1.2 (FH cathode) at (77.54, 32) by ≥ 0.5 mm.
    line(F_Cu, 'COLLECTOR', (75.0,  24.0), d11, width=TRACK_WIDTH_POWER)
    line(F_Cu, 'COLLECTOR', (80.08, 24.0), d13, width=TRACK_WIDTH_POWER)
    # TP5 (70, 22) test-point stub to rail
    line(F_Cu, 'COLLECTOR', P('TP5','1'), (70.0, 24.0), width=TRACK_WIDTH_SIGNAL)

    # --- FLYBACK_HIGH (brake intermediate): D1.2 → R5.2 ---
    # 2 mm wide between D1.1/D1.3 pads (each ≥ 0.5 mm clear of trace edges).
    # Carries the full coil flyback current through D1+R5 to PGND.
    line(F_Cu, 'FLYBACK_HIGH', d12, r52, width=TRACK_WIDTH_POWER)
    # TP6 (84, 47) — signal stub eastward from R5.2 (south of D1.3 pad).
    line(F_Cu, 'FLYBACK_HIGH', r52,
         (77.54, 36.0),
         (84.0, 36.0),
         (84.0, 47.0),
         width=TRACK_WIDTH_SIGNAL)

    # --- SNUB_INTERMEDIATE: R4.1 (66, 46.35) -> C1.1 (62, 53.6) (post-pad-swap) ---
    line(F_Cu, 'SNUB_INTERMEDIATE', r41, (62.0, 46.35), c11, width=TRACK_WIDTH_GATE)

    # POWER_GROUND pads (Q1.3, C1.1, R5.2, J4, TP7-9) join via PGND zone fill — no
    # explicit tracks needed. Zone clearance keeps them isolated from COLLECTOR/FLYBACK_HIGH.

    # -------------------------------------------------------------------------
    # 6. Add PGND zone fills (F.Cu south region + full B.Cu)
    # -------------------------------------------------------------------------
    pgnd = nets['POWER_GROUND']
    # F.Cu: hot-side PGND pour with FULL (solid) connection — high-current path
    # benefits from low impedance over thermal-relief spokes. North edge Y=37
    # captures Q1.3 (PE) and snubber row. West edge X=22 captures TP7 (28,60).
    z_f = add_zone(b, F_Cu, pgnd, [
        (22.0, 37.0),
        (99.5, 37.0),
        (99.5, 69.5),
        (22.0, 69.5),
    ])
    z_f.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    # B.Cu: full-board pour minus a 0.5mm edge keepout. Thermal-relief on this
    # pour to keep solderability for through-hole pads.
    add_zone(b, B_Cu, pgnd, [
        (0.5, 0.5),
        (99.5, 0.5),
        (99.5, 69.5),
        (0.5, 69.5),
    ])

    # -------------------------------------------------------------------------
    # 7. Stitching vias from F.Cu PGND pour to B.Cu PGND pour
    # -------------------------------------------------------------------------
    # Stitching grid — avoid:
    #   X=88 (COLLECTOR rail), X=66 (R4 column), X=62 (C1 column),
    #   X=77.54 (R5 column), and existing pads.
    stitch_xy = [
        (40, 60), (45, 60), (55, 60), (70, 60),
        (35, 55), (45, 55), (55, 55), (70, 55),
        (35, 50), (45, 50), (55, 50), (70, 50),
    ]
    for (x, y) in stitch_xy:
        add_via(b, x, y, pgnd, drill_mm=0.4, size_mm=0.8)

    # -------------------------------------------------------------------------
    # 8. Refill zones and save
    # -------------------------------------------------------------------------
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())

    pcbnew.SaveBoard(PCB_OUT, b)
    print(f"[OK] Saved: {PCB_OUT}")


if __name__ == '__main__':
    main()
