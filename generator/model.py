"""Building model: single-storey house 15.00 x 8.00 m (dimensions between structural axes).

Origin (0, 0) = intersection of axes 1 / A (south-west corner). x -> east, y -> north.
The band y = 5..8 holds the three bedrooms (R1, R2, R3, 5.00 x 3.00 each);
the band y = 0..5 holds salon (3 m), kitchen (4 m), WC (2 m), and the hall with the entrance on the east facade.
"""
from shapely.geometry import LineString, box
from shapely.ops import unary_union

LX, LY = 15.0, 8.0
XA = [0.0, 5.0, 10.0, 15.0]
YA = [0.0, 5.0, 8.0]
XL = ["1", "2", "3", "4"]
YL = ["A", "B", "C"]

EXT = 0.30   # exterior walls: double brick partition 10 + 5 (air gap) + 15
INT = 0.10   # interior partitions: hollow brick 10 cm
COL = 0.30   # RC columns 30 x 30

# ---- levels (m) ----
Z_TN = -0.45          # natural ground
Z_FF = 0.00           # finished floor
Z_DALLAGE_TOP = -0.05
Z_DALLAGE_BOT = -0.15
Z_HERISSON_BOT = -0.35
Z_LONG_TOP = -0.05
Z_LONG_BOT = -0.45
Z_CEIL = 3.00         # underside of slab
Z_SLAB = 3.24         # top of structural slab (20+4)
Z_FORME = 3.36        # top of slope screed + waterproofing (average)
Z_ACRO = 3.90         # top of parapet
PP_H, PS_H = 0.45, 0.35   # beam depths (incl. slab)
Z_PP_SOF = Z_SLAB - PP_H  # 2.79
Z_PS_SOF = Z_SLAB - PS_H  # 2.89
Z_LINTEL = 2.20
Z_SEM_TOP_S1, Z_SEM_BOT = -1.10, -1.50
Z_SEM_TOP_S2 = -1.15
Z_PROP = -1.60

EXT_WALLS = [(0, 0, 15, 0), (15, 0, 15, 8), (15, 8, 0, 8), (0, 8, 0, 0)]
INT_WALLS = [(0, 5, 15, 5), (5, 5, 5, 8), (10, 5, 10, 8), (3, 0, 3, 5), (3, 2, 9, 2), (7, 0, 7, 2), (9, 0, 9, 2)]
COLUMNS = [(x, y) for y in YA for x in XA]

# Openings. o='h': wall along x at y=at ; o='v': wall along y at x=at. c = centre along wall, w = width.
OPENINGS = [
    dict(id="P1", kind="door", o="v", at=15, c=3.00, w=1.20, hinge="end", swing=-1, h=2.20, sill=0.0),
    dict(id="P2", kind="door", o="h", at=5, c=4.15, w=0.90, hinge="end", swing=1, h=2.20, sill=0.0),
    dict(id="P2", kind="door", o="h", at=5, c=5.85, w=0.90, hinge="start", swing=1, h=2.20, sill=0.0),
    dict(id="P2", kind="door", o="h", at=5, c=10.85, w=0.90, hinge="start", swing=1, h=2.20, sill=0.0),
    dict(id="P5", kind="door2", o="v", at=3, c=3.50, w=1.40, swing=-1, h=2.20, sill=0.0),
    dict(id="P3", kind="door", o="h", at=2, c=6.00, w=0.80, hinge="start", swing=-1, h=2.20, sill=0.0),
    dict(id="P4", kind="door", o="h", at=2, c=8.15, w=0.70, hinge="start", swing=-1, h=2.20, sill=0.0),
    dict(id="F1", kind="window", o="h", at=8, c=2.50, w=1.20, h=1.20, sill=1.00),
    dict(id="F1", kind="window", o="h", at=8, c=7.50, w=1.20, h=1.20, sill=1.00),
    dict(id="F1", kind="window", o="h", at=8, c=12.50, w=1.20, h=1.20, sill=1.00),
    dict(id="F1", kind="window", o="h", at=0, c=1.50, w=1.20, h=1.20, sill=1.00),
    dict(id="F2", kind="window", o="v", at=0, c=2.50, w=1.40, h=1.20, sill=1.00),
    dict(id="F2", kind="window", o="h", at=0, c=12.50, w=1.40, h=1.20, sill=1.00),
    dict(id="F3", kind="window", o="h", at=0, c=4.00, w=1.00, h=1.20, sill=1.00),
    dict(id="F3", kind="window", o="v", at=15, c=6.50, w=1.00, h=1.20, sill=1.00),
    dict(id="F4", kind="window", o="h", at=0, c=8.00, w=0.60, h=0.60, sill=1.60),
]

JOINERY = {
    "P1": ("Porte d'entrée (bois massif / métal)", "1.20 × 2.20", "—"),
    "P2": ("Porte intérieure isoplane", "0.90 × 2.20", "—"),
    "P3": ("Porte intérieure isoplane", "0.80 × 2.20", "—"),
    "P4": ("Porte intérieure isoplane", "0.70 × 2.20", "—"),
    "P5": ("Porte vitrée 2 vantaux", "1.40 × 2.20", "—"),
    "F1": ("Fenêtre 2 vantaux + volet", "1.20 × 1.20", "1.00"),
    "F2": ("Fenêtre 2 vantaux + volet", "1.40 × 1.20", "1.00"),
    "F3": ("Fenêtre 2 vantaux", "1.00 × 1.20", "1.00"),
    "F4": ("Châssis oscillo-battant", "0.60 × 0.60", "1.60"),
}

# Entrance landing (perron) on the east facade
PERRON = dict(x0=15.15, y0=2.00, y1=4.00, steps=[(15.15, 15.75, -0.02), (15.75, 16.05, -0.15), (16.05, 16.35, -0.30)])

ROOMS = [
    # name, polygon, label point, floor finish
    ("CHAMBRE 01", box(0, 5, 5, 8), (2.95, 7.35), "Carrelage grès cérame"),
    ("CHAMBRE 02", box(5, 5, 10, 8), (7.45, 7.35), "Carrelage grès cérame"),
    ("CHAMBRE 03", box(10, 5, 15, 8), (12.0, 7.35), "Carrelage grès cérame"),
    ("SALON", box(0, 0, 3, 5), (1.55, 4.35), "Carrelage grès cérame"),
    ("CUISINE", box(3, 0, 7, 2), (4.75, 1.55), "Carrelage antidérapant"),
    ("WC", box(7, 0, 9, 2), (7.88, 1.0), "Carrelage antidérapant"),
    ("HALL", unary_union([box(3, 2, 15, 5), box(9, 0, 15, 2)]), (12.1, 1.35), "Carrelage grès cérame"),
]


def is_ext(op):
    return (op["o"] == "h" and op["at"] in (0, 8)) or (op["o"] == "v" and op["at"] in (0, 15))


def thickness(op):
    return EXT if is_ext(op) else INT


def to_xy(o, along, normal):
    return (along, normal) if o == "h" else (normal, along)


def opening_cut(op, extra=0.01):
    t = thickness(op) / 2 + extra
    a, b = op["c"] - op["w"] / 2, op["c"] + op["w"] / 2
    if op["o"] == "h":
        return box(a, op["at"] - t, b, op["at"] + t)
    return box(op["at"] - t, a, op["at"] + t, b)


def columns_geom(size=COL):
    h = size / 2
    return unary_union([box(x - h, y - h, x + h, y + h) for x, y in COLUMNS])


def walls_full():
    ext = [LineString([(a, b), (c, d)]).buffer(EXT / 2, cap_style="square", join_style="mitre") for a, b, c, d in EXT_WALLS]
    itn = [LineString([(a, b), (c, d)]).buffer(INT / 2, cap_style="flat", join_style="mitre") for a, b, c, d in INT_WALLS]
    return unary_union(ext + itn)


def walls_cut():
    """Walls with openings removed and columns subtracted (columns are drawn separately)."""
    cuts = unary_union([opening_cut(o) for o in OPENINGS])
    return walls_full().difference(cuts).difference(columns_geom())


def ext_walls_geom():
    return unary_union([LineString([(a, b), (c, d)]).buffer(EXT / 2, cap_style="square", join_style="mitre")
                        for a, b, c, d in EXT_WALLS])


def net_area(poly):
    return poly.difference(unary_union([walls_full(), columns_geom()])).area


def openings_on(o, at):
    return sorted([op for op in OPENINGS if op["o"] == o and op["at"] == at], key=lambda op: op["c"])


# ---- foundations (sized in the structural calculation note, generator/calc.py) ----
FOOTINGS = {"S1": (1.20, 0.40), "S2": (1.10, 0.35), "S3": (1.00, 0.35)}  # side a (m), height h (m)


def footing_type(x, y):
    if x in (0, 15) and y in (0, 8):
        return "S3"            # corner columns
    if 0 < x < 15 and 0 < y < 8:
        return "S1"            # interior columns B2, B3
    return "S2"                # edge columns


def footing_top(x, y):
    return Z_SEM_BOT + FOOTINGS[footing_type(x, y)][1]


def longrine_spans():
    """Clear lengths of tie beams between footing faces: list of (label, length)."""
    out = []
    for y, yl in zip(YA, YL):
        for i in range(len(XA) - 1):
            a = FOOTINGS[footing_type(XA[i], y)][0] / 2 + FOOTINGS[footing_type(XA[i + 1], y)][0] / 2
            out.append((f"{yl}{XL[i]}-{yl}{XL[i + 1]}", XA[i + 1] - XA[i] - a))
    for x, xl in zip(XA, XL):
        for j in range(len(YA) - 1):
            a = FOOTINGS[footing_type(x, YA[j])][0] / 2 + FOOTINGS[footing_type(x, YA[j + 1])][0] / 2
            out.append((f"{YL[j]}{xl}-{YL[j + 1]}{xl}", YA[j + 1] - YA[j] - a))
    return out


def longrine_length():
    return round(sum(L for _, L in longrine_spans()), 2)
