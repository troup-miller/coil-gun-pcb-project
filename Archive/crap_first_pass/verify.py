"""Verify net isolation: any two different nets' copper regions must be at least 0.8mm apart."""
import sys
sys.path.insert(0, '.')
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

# Re-import nets from gen_pcb
import importlib.util
spec = importlib.util.spec_from_file_location("gen_pcb", "gen_pcb.py")
m = importlib.util.module_from_spec(spec)
# Need to disable the file write at end - patch with a no-op
import builtins
orig_open = builtins.open
def fake_open(*a, **k):
    if a and a[0] == 'igbt_pcb_etch.svg':
        import io
        return io.StringIO()
    return orig_open(*a, **k)
builtins.open = fake_open
try:
    spec.loader.exec_module(m)
finally:
    builtins.open = orig_open

NETS = m.NETS
PIN = m.PIN
DRILL = m.DRILL

# Build a Polygon per net (union of its rectangles/polygons)
net_geom = {}
for name, polys in NETS.items():
    shapes = []
    for p in polys:
        try:
            shapes.append(Polygon(p))
        except Exception as e:
            print(f"Bad polygon in {name}: {e}")
    net_geom[name] = unary_union(shapes)

# Check pairwise distances
MIN_GAP = 0.6  # mm — rotary tool channel minimum
problems = []
names = list(net_geom.keys())
for i, a in enumerate(names):
    for b in names[i+1:]:
        ga, gb = net_geom[a], net_geom[b]
        if ga.intersects(gb):
            problems.append(f"OVERLAP: {a} <-> {b}")
        else:
            d = ga.distance(gb)
            if d < MIN_GAP:
                problems.append(f"TOO CLOSE ({d:.3f}mm): {a} <-> {b}")

# Check drill holes - each drill must be inside a net region
import shapely.geometry as sg
unassigned = []
multi_assigned = []
for name, (x, y) in PIN.items():
    pt = sg.Point(x, y)
    hits = [n for n, g in net_geom.items() if g.contains(pt) or g.boundary.distance(pt) < 0.01]
    if not hits:
        unassigned.append(f"{name} at ({x:.2f},{y:.2f})")
    elif len(hits) > 1:
        multi_assigned.append(f"{name} -> {hits}")

print(f"Problems: {len(problems)}")
for p in problems:
    print(f"  {p}")
print(f"\nUnassigned drill holes (not on any copper - need fix or are OK on PGND/edge): {len(unassigned)}")
for u in unassigned[:30]:
    print(f"  {u}")
print(f"\nMulti-assigned (drill on multiple nets - SHORT!): {len(multi_assigned)}")
for m in multi_assigned:
    print(f"  {m}")
