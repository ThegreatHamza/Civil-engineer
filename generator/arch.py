"""Architecture sheets: ground-floor plan, roof plan, facades, sections."""
import math

import model as M
from drawing import ACCENT, AXIS, CONC, GLASS, GREY, INK, LIGHT, POCHE, View

FURN = dict(lw="fine", ec=GREY, layer="A-FURN")


# =====================================================================================
# Plan helpers
# =====================================================================================
def draw_openings(v, symbols=True):
    for op in M.OPENINGS:
        t = M.thickness(op)
        a, b = op["c"] - op["w"] / 2, op["c"] + op["w"] / 2
        o, at = op["o"], op["at"]
        T = lambda al, nm: M.to_xy(o, al, nm)  # noqa: E731
        if op["kind"] == "window":
            # wall faces through the opening + glazing + sill
            v.line([T(a, at - t / 2), T(b, at - t / 2)], lw="fine", layer="A-WIND")
            v.line([T(a, at + t / 2), T(b, at + t / 2)], lw="fine", layer="A-WIND")
            v.poly([T(a, at - 0.03), T(b, at - 0.03), T(b, at + 0.03), T(a, at + 0.03)], fc=GLASS, ec=INK,
                   lw="fine", layer="A-WIND", z=5)
            v.line([T(op["c"], at - 0.03), T(op["c"], at + 0.03)], lw="fine", layer="A-WIND")
            # exterior sill (appui) projecting 3 cm
            out = -1 if at == 0 else 1
            v.line([T(a - 0.03, at + out * (t / 2 + 0.03)), T(b + 0.03, at + out * (t / 2 + 0.03))], lw="fine",
                   layer="A-WIND")
            v.line([T(a - 0.03, at + out * t / 2), T(a - 0.03, at + out * (t / 2 + 0.03))], lw="fine", layer="A-WIND")
            v.line([T(b + 0.03, at + out * t / 2), T(b + 0.03, at + out * (t / 2 + 0.03))], lw="fine", layer="A-WIND")
        else:
            s = op["swing"]
            face = at + s * t / 2
            leaves = [(a, b - a, 1)] if op["kind"] == "door" and op["hinge"] == "start" else \
                     [(b, b - a, -1)] if op["kind"] == "door" else \
                     [(a, (b - a) / 2, 1), (b, (b - a) / 2, -1)]
            for hinge, w, d in leaves:
                # leaf
                v.poly([T(hinge, face), T(hinge + d * 0.04, face), T(hinge + d * 0.04, face + s * w),
                        T(hinge, face + s * w)], fc="white", ec=INK, lw="thin", layer="A-DOOR", z=6)
                # swing arc
                pts = []
                for i in range(25):
                    ang = math.radians(90 * i / 24)
                    al = hinge + d * w * math.sin(ang)
                    nm = face + s * w * math.cos(ang)
                    pts.append(T(al, nm))
                v.line(pts, lw="hair", color=GREY, layer="A-DOOR")
            # threshold line
            v.line([T(a, at), T(b, at)], lw="hair", color=LIGHT, ls="dash", layer="A-DOOR")
        if symbols:
            # joinery tag outside / beside the opening
            out = 1 if (at in (8, 15) and M.is_ext(op)) else -1 if M.is_ext(op) else -op.get("swing", 1)
            off = t / 2 + 0.38
            x, y = T(op["c"], at + out * off)
            v.label_box(x, y, op["id"], h=1.9, pad=0.7, layer="A-TEXT")


def draw_furniture(v):
    f = FURN
    # Chambre 01 : double bed, night tables, wardrobe
    v.rect(0.15, 5.75, 2.05, 7.15, **f)
    v.rect(0.18, 5.82, 0.60, 6.42, **f)
    v.rect(0.18, 6.48, 0.60, 7.08, **f)
    v.line([(0.75, 5.75), (2.05, 6.45)], lw="hair", color=LIGHT, layer="A-FURN")
    v.rect(0.15, 7.30, 0.60, 7.75, **f)
    v.rect(0.15, 5.15, 0.60, 5.60, **f)
    v.rect(4.35, 6.25, 4.95, 7.85, **f)
    v.line([(4.35, 6.25), (4.95, 7.85)], lw="hair", color=LIGHT, layer="A-FURN")
    v.line([(4.35, 7.85), (4.95, 6.25)], lw="hair", color=LIGHT, layer="A-FURN")
    # Chambre 02
    v.rect(8.05, 5.75, 9.95, 7.15, **f)
    v.rect(9.40, 5.82, 9.88, 6.42, **f)
    v.rect(9.40, 6.48, 9.88, 7.08, **f)
    v.line([(8.05, 6.45), (9.25, 5.75)], lw="hair", color=LIGHT, layer="A-FURN")
    v.rect(9.50, 7.30, 9.95, 7.75, **f)
    v.rect(5.05, 6.30, 5.65, 7.85, **f)
    v.line([(5.05, 6.30), (5.65, 7.85)], lw="hair", color=LIGHT, layer="A-FURN")
    v.line([(5.05, 7.85), (5.65, 6.30)], lw="hair", color=LIGHT, layer="A-FURN")
    v.rect(6.40, 7.30, 7.60, 7.85, **f)  # desk under window
    v.rect(6.80, 6.85, 7.20, 7.25, **f)
    # Chambre 03
    v.rect(13.40, 5.95, 14.80, 7.85, **f)
    v.rect(13.47, 7.35, 14.07, 7.78, **f)
    v.rect(14.13, 7.35, 14.73, 7.78, **f)
    v.line([(13.40, 6.95), (14.80, 6.55)], lw="hair", color=LIGHT, layer="A-FURN")
    v.rect(12.85, 7.40, 13.30, 7.85, **f)
    v.rect(10.05, 6.30, 10.65, 7.85, **f)
    v.line([(10.05, 6.30), (10.65, 7.85)], lw="hair", color=LIGHT, layer="A-FURN")
    v.line([(10.05, 7.85), (10.65, 6.30)], lw="hair", color=LIGHT, layer="A-FURN")
    # Salon : sofa, armchair, coffee table, TV unit
    v.rect(0.15, 0.55, 1.00, 2.95, **f)
    v.rect(0.15, 0.55, 0.40, 2.95, **f)
    v.rect(0.15, 0.55, 1.00, 0.80, **f)
    v.rect(0.15, 2.70, 1.00, 2.95, **f)
    v.rect(1.35, 1.20, 1.95, 2.25, **f)
    v.rect(0.25, 3.35, 1.05, 4.15, **f)
    v.rect(0.25, 3.35, 0.45, 4.15, **f)
    v.rect(2.50, 0.60, 2.95, 2.40, **f)
    # Kitchen : L-shaped worktop, sink, hob, fridge
    v.poly([(3.05, 0.15), (6.25, 0.15), (6.25, 0.75), (3.65, 0.75), (3.65, 1.60), (3.05, 1.60)], **f)
    v.rect(3.60, 0.22, 4.40, 0.68, **f)
    v.rect(3.66, 0.27, 3.97, 0.63, **f)
    v.rect(4.03, 0.27, 4.34, 0.63, **f)
    v.rect(5.10, 0.20, 5.80, 0.70, **f)
    for cx, cy in [(5.28, 0.33), (5.62, 0.33), (5.28, 0.57), (5.62, 0.57)]:
        v.circle(cx, cy, 0.08, **f)
    v.rect(6.30, 0.15, 6.95, 0.80, **f)
    v.line([(6.30, 0.15), (6.95, 0.80)], lw="hair", color=LIGHT, layer="A-FURN")
    v.text(6.62, 0.47, "R", h=1.6, ha="center", va="center", color=GREY, layer="A-FURN")
    # WC : toilet + wash basin
    v.rect(8.25, 0.15, 8.70, 0.33, **f)
    v.poly([(8.475 + 0.19 * math.cos(math.radians(a)), 0.60 + 0.27 * math.sin(math.radians(a)))
            for a in range(0, 360, 12)], **f)
    v.poly([(7.05, 1.05), (7.45, 1.05), (7.50, 1.25), (7.45, 1.45), (7.05, 1.45)], **f)
    v.circle(7.25, 1.25, 0.09, **f)
    # Hall : dining table with 6 chairs
    v.rect(6.20, 3.05, 7.80, 3.95, **f)
    for cx in (6.55, 7.00, 7.45):
        v.rect(cx - 0.20, 2.62, cx + 0.20, 2.98, **f)
        v.rect(cx - 0.20, 4.02, cx + 0.20, 4.38, **f)
    # Hall : entrance console + plants
    v.rect(14.40, 0.40, 14.85, 1.80, **f)
    v.circle(14.45, 4.55, 0.25, **f)
    v.circle(3.50, 4.55, 0.25, **f)


def draw_perron(v, fill=True):
    p = M.PERRON
    v.rect(p["x0"], p["y0"], 16.35, p["y1"], fc="white" if fill else "none", ec=INK, lw="thin", layer="A-WALL")
    for x0, x1, z in p["steps"][1:]:
        v.line([(x0, p["y0"]), (x0, p["y1"])], lw="thin", layer="A-WALL")
    v.line([(15.45, 3.0), (16.25, 3.0)], lw="fine", layer="A-TEXT")
    v.poly([(15.35, 3.0), (15.48, 3.06), (15.48, 2.94)], fc=INK, ec=INK, lw="hair", layer="A-TEXT")
    v.text(16.30, 3.10, "3 marches", h=1.7, ha="right", layer="A-TEXT")


def plan_dims(v):
    # South
    xs = [-0.15] + sum([[op["c"] - op["w"] / 2, op["c"] + op["w"] / 2] for op in M.openings_on("h", 0)], []) + [15.15]
    v.dim(xs, -0.85, "h", ext_from=-0.15, side=-1)
    v.dim([0, 3, 5, 7, 9, 10, 15], -1.40, "h", ext_from=-0.15, side=-1)
    v.dim([0, 15], -1.95, "h", ext_from=-0.15, side=-1)
    # North
    xs = [-0.15] + sum([[op["c"] - op["w"] / 2, op["c"] + op["w"] / 2] for op in M.openings_on("h", 8)], []) + [15.15]
    v.dim(xs, 8.85, "h", ext_from=8.15)
    v.dim([0, 5, 10, 15], 9.40, "h", ext_from=8.15)
    v.dim([0, 15], 9.95, "h", ext_from=8.15)
    # West
    ys = [-0.15] + sum([[op["c"] - op["w"] / 2, op["c"] + op["w"] / 2] for op in M.openings_on("v", 0)], []) + [8.15]
    v.dim(ys, -0.85, "v", ext_from=-0.15)
    v.dim([0, 5, 8], -1.40, "v", ext_from=-0.15)
    v.dim([0, 8], -1.95, "v", ext_from=-0.15)
    # East
    ys = [-0.15] + sum([[op["c"] - op["w"] / 2, op["c"] + op["w"] / 2] for op in M.openings_on("v", 15)], []) + [8.15]
    v.dim(ys, 16.85, "v", ext_from=16.40, side=-1)
    v.dim([0, 5, 8], 17.40, "v", ext_from=16.40, side=-1)
    v.dim([0, 8], 17.95, "v", ext_from=16.40, side=-1)


def plan_axes(v, xr=(-2.6, 10.6), yr=(-2.6, 18.6)):
    for x, lab in zip(M.XA, M.XL):
        v.axis((x, xr[0]), (x, xr[1]), lab)
    for y, lab in zip(M.YA, M.YL):
        v.axis((yr[0], y), (yr[1], y), lab)


def section_mark(v, p0, p1, label, look, ext=0.6):
    """Cut line with arrows. look = (dx, dy) unit direction the viewer looks at."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    v.line([p0, p1], lw="fine", ls="axis", color=ACCENT, layer="A-SECT", z=6)
    for (px, py), sg in ((p0, 1), (p1, -1)):
        v.line([(px, py), (px + sg * ux * ext, py + sg * uy * ext)], lw="xthick", color=ACCENT, layer="A-SECT", z=7)
        ax_, ay_ = px + sg * ux * ext * 0.45, py + sg * uy * ext * 0.45
        a = 0.55
        tip = (ax_ + look[0] * a, ay_ + look[1] * a)
        v.line([(ax_, ay_), tip], lw="med", color=ACCENT, layer="A-SECT", z=7)
        nx, ny = -look[1], look[0]
        v.poly([tip, (tip[0] - look[0] * 0.22 + nx * 0.1, tip[1] - look[1] * 0.22 + ny * 0.1),
                (tip[0] - look[0] * 0.22 - nx * 0.1, tip[1] - look[1] * 0.22 - ny * 0.1)], fc=ACCENT, ec=ACCENT,
               lw="hair", layer="A-SECT", z=7)
        lx, ly = px - sg * ux * 0.35 + look[0] * 0.05, py - sg * uy * 0.35 + look[1] * 0.05
        v.circle(lx - sg * ux * 0.0, ly, v.m(3.0), fc="white", ec=ACCENT, lw="thin", layer="A-SECT", z=7)
        v.text(lx, ly, label, h=3.0, ha="center", va="center", weight="bold", color=ACCENT, layer="A-SECT")


# =====================================================================================
# Sheet 01 : ground-floor plan
# =====================================================================================
def sheet_plan(S):
    v = View(S, ox=86, oy=150, scale=50)
    walls = M.walls_cut()
    ext = M.ext_walls_geom()
    # exterior walls: poché + air-gap line ; interior partitions lighter
    v.geom(walls.intersection(ext), fc=POCHE, ec=INK, lw="thick", layer="A-WALL", z=4)
    v.geom(walls.difference(ext), fc="#e4e4e4", ec=INK, lw="med", layer="A-WALL", z=4)
    v.geom(M.columns_geom(), fc=INK, ec=INK, lw="thin", layer="A-COLS", z=5)
    draw_openings(v)
    draw_furniture(v)
    draw_perron(v)
    plan_axes(v)
    plan_dims(v)

    # room labels
    for name, poly, (lx, ly), finish in M.ROOMS:
        area = M.net_area(poly)
        v.text(lx, ly, name, h=3.0, ha="center", weight="bold", layer="A-ROOM")
        v.text(lx, ly - 0.22, f"S = {area:.2f} m²", h=2.2, ha="center", va="top", layer="A-ROOM")
        if name != "WC":
            v.text(lx, ly - 0.50, finish, h=1.7, ha="center", va="top", color=GREY, layer="A-ROOM",
                   style="italic")
    v.plan_level(9.6, 3.55, "±0.00")
    v.plan_level(15.25, 2.25, "-0.02")
    v.plan_level(15.6, -0.55, "TN -0.45")
    v.text(15.75, 4.55, "ENTRÉE", h=2.6, weight="bold", ha="center", layer="A-ROOM")

    section_mark(v, (12.5, -3.2), (12.5, 11.2), "A", (-1, 0))
    section_mark(v, (-2.65, 2.9), (18.65, 2.9), "B", (0, 1))

    S.view_title(86 - 2.6 * 20 + 4, 393, "PLAN DU REZ-DE-CHAUSSÉE", "1:50")
    S.north_arrow(40, 360)

    # ---- right column : tables ----
    x0 = 473
    rows, tot = [], 0
    for name, poly, _, _ in M.ROOMS:
        a = M.net_area(poly)
        tot += a
        rows.append([name.title() if name != "WC" else "WC", f"{a:.2f}"])
    rows.append(["Surface habitable", f"{tot:.2f}"])
    emprise = (15.30 * 8.30)
    rows.append(["Surface bâtie (hors œuvre)", f"{emprise:.2f}"])
    y = S.table(x0, 392, [("Local", 72, "left"), ("Surface (m²)", 36, "center")], rows,
                title="TABLEAU DES SURFACES", h=2.2, row_h=5.2, bold_last=True)

    jr = []
    counts = {}
    for op in M.OPENINGS:
        counts[op["id"]] = counts.get(op["id"], 0) + 1
    for k in sorted(M.JOINERY):
        d, dim, sill = M.JOINERY[k]
        jr.append([k, d, dim, sill, counts.get(k, 0)])
    y = S.table(x0, y - 12, [("Rep.", 10), ("Désignation", 45, "left"), ("l × h (m)", 23), ("Allège", 14), ("Nb", 8)],
                jr, title="TABLEAU DES MENUISERIES", h=1.85, row_h=5.0)

    # legend
    y -= 12
    S.text(x0, y, "LÉGENDE", h=3.0, weight="bold", color=ACCENT)
    items = [
        (POCHE, "thick", "Mur extérieur ép. 30 cm (double cloison\nbrique 15 + vide d'air 5 + brique 10)"),
        ("#e4e4e4", "med", "Cloison intérieure brique creuse ép. 10 cm"),
        (INK, "thin", "Poteau en béton armé 30 × 30 cm"),
    ]
    y -= 6
    for fc, lw, txt in items:
        S.rect(x0, y - 3, x0 + 9, y + 1, fc=fc, ec=INK, lw=lw)
        S.text(x0 + 12, y + 1, txt, h=2.0, va="top")
        y -= 9.5
    S.line([(x0, y), (x0 + 9, y)], lw="fine", color=AXIS, ls="axis")
    S.text(x0 + 12, y, "Axe de structure (cotes entre axes)", h=2.0, va="center")
    y -= 6
    S.line([(x0, y), (x0 + 9, y)], lw="xthick", color=ACCENT)
    S.text(x0 + 12, y, "Trait de coupe", h=2.0, va="center")
    y -= 9
    S.notes(x0, y, "NOTES", [
        "1. Cotes en mètres.",
        "2. Les cotes 15.00 × 8.00 m sont prises entre axes",
        "   des poteaux ; hors-tout = 15.30 × 8.30 m.",
        "3. Hauteur sous plafond : 3.00 m.",
        "4. Linteaux des portes : +2.20 m.",
        "5. Orientation supposée : chambres au Nord.",
    ], h=2.0)


# =====================================================================================
# Sheet 02 : roof (terrace) plan
# =====================================================================================
def sheet_roof(S):
    v = View(S, ox=86, oy=150, scale=50)
    o, i = -0.15, -0.05
    v.rect(o, o, 15 - o, 8 - o, fc="#f4f4f4", ec=INK, lw="thick", layer="A-ROOF")
    v.rect(i, i, 15 - i, 8 - i, fc="#fbfbfb", ec=INK, lw="thin", layer="A-ROOF")
    # gravel protection texture
    v.rect(i, i, 15 - i, 8 - i, fc="none", ec="none", hatch="..", hcolor="#c8c8c8", layer="A-ROOF", z=3)
    # slope ridges (lines from corners to central ridge)
    v.line([(i, i), (4.0, 4.0), (11.0, 4.0), (15 - i, i)], lw="fine", color=GREY, ls="dash", layer="A-ROOF")
    v.line([(i, 8 - i), (4.0, 4.0)], lw="fine", color=GREY, ls="dash", layer="A-ROOF")
    v.line([(15 - i, 8 - i), (11.0, 4.0)], lw="fine", color=GREY, ls="dash", layer="A-ROOF")
    # downpipes in the 4 corners
    for cx, cy in [(0.25, 0.25), (14.75, 0.25), (0.25, 7.75), (14.75, 7.75)]:
        v.circle(cx, cy, 0.11, fc="white", ec=INK, lw="thin", layer="A-ROOF")
        v.circle(cx, cy, 0.05, fc=INK, ec=INK, lw="hair", layer="A-ROOF")
    for (x, y, ang, lab) in [(7.5, 1.9, -90, "2 %"), (7.5, 6.1, 90, "2 %"), (2.0, 4.0, 180, "2 %"), (13.0, 4.0, 0, "2 %"),
                             (4.5, 1.2, -90, "2 %"), (10.5, 1.2, -90, "2 %"), (4.5, 6.8, 90, "2 %"),
                             (10.5, 6.8, 90, "2 %")]:
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        p0 = (x - dx * 0.7, y - dy * 0.7)
        p1 = (x + dx * 0.7, y + dy * 0.7)
        v.line([p0, p1], lw="thin", layer="A-ROOF")
        nx, ny = -dy, dx
        v.poly([p1, (p1[0] - dx * 0.25 + nx * 0.09, p1[1] - dy * 0.25 + ny * 0.09),
                (p1[0] - dx * 0.25 - nx * 0.09, p1[1] - dy * 0.25 - ny * 0.09)], fc=INK, ec=INK, lw="hair",
               layer="A-ROOF")
        v.text(x + nx * 0.18, y + ny * 0.18, lab, h=2.0, ha="center", va="center", rot=0, layer="A-ROOF")
    v.text(7.5, 4.35, "TERRASSE INACCESSIBLE", h=3.4, ha="center", weight="bold", layer="A-ROOF")
    v.text(7.5, 3.95, "Étanchéité multicouche + protection gravillons ép. 5 cm", h=2.2, ha="center", va="top",
           layer="A-ROOF")
    for cx, cy in [(0.25, 0.25), (14.75, 0.25), (0.25, 7.75), (14.75, 7.75)]:
        sx = 1 if cx < 7 else -1
        sy = 1 if cy < 4 else -1
        v.leader([(cx + sx * 0.08, cy + sy * 0.08), (cx + sx * 0.9, cy + sy * 0.9), (cx + sx * 1.6, cy + sy * 0.9)],
                 "EP Ø110 PVC", h=2.0, ha="left" if sx > 0 else "right")
    v.leader([(5.0, 8.0 - 0.10), (5.6, 8.55), (6.2, 8.55)], "Acrotère BA ép. 10 cm, H = 0.60 m", h=2.0)
    plan_axes(v, xr=(-1.9, 10.0), yr=(-1.9, 16.9))
    v.dim([-0.15, 15.15], -0.9, "h", ext_from=-0.15, side=-1)
    v.dim([0, 5, 10, 15], -1.45, "h", ext_from=-0.15, side=-1)
    v.dim([-0.15, 8.15], -0.9, "v", ext_from=-0.15)
    v.dim([0, 5, 8], -1.45, "v", ext_from=-0.15)
    v.plan_level(1.2, 4.0, "+3.90 acrotère")
    S.view_title(60, 393, "PLAN DE TERRASSE (TOITURE)", "1:50")
    S.north_arrow(40, 360)
    S.notes(466, 392, "COMPOSITION DE LA TERRASSE", [
        "(du haut vers le bas)",
        "· Protection lourde : gravillons roulés 5 cm",
        "· Étanchéité multicouche (3 couches",
        "  feutre bitumé + 2 enduits à chaud)",
        "· Écran pare-vapeur",
        "· Isolation thermique liège / polystyrène 4 cm",
        "· Forme de pente béton maigre (2 %),",
        "  ép. moyenne 8 cm",
        "· Plancher corps creux 20 + 4",
        "· Enduit plâtre sous plafond 2 cm",
    ], h=2.1)
    S.notes(466, 300, "NOTES", [
        "1. Pente minimale 2 % vers les",
        "   descentes d'eaux pluviales (EP).",
        "2. 4 descentes EP Ø110 PVC dans les",
        "   angles, raccordées au regard pied",
        "   de chute.",
        "3. Relevés d'étanchéité h ≥ 15 cm",
        "   protégés par engravure + bande",
        "   solin dans l'acrotère.",
        "4. Cotes en mètres.",
    ], h=2.1)


# =====================================================================================
# Elevations
# =====================================================================================
def window_elev(v, h0, h1, z0, z1, two=True):
    v.rect(h0, z0, h1, z1, fc="white", ec=INK, lw="thin", layer="A-ELEV", z=5)
    f = 0.06
    v.rect(h0 + f, z0 + f, h1 - f, z1 - f, fc=GLASS, ec=INK, lw="fine", layer="A-ELEV", z=5.2)
    if two and (h1 - h0) > 0.7:
        hm = (h0 + h1) / 2
        v.line([(hm, z0 + f), (hm, z1 - f)], lw="thin", layer="A-ELEV", z=5.4)
        for a, b in ((h0 + f, hm), (hm, h1 - f)):
            v.line([(a + 0.1, z1 - f - 0.12), (a + 0.28, z1 - f - 0.30)], lw="hair", color=GREY, layer="A-ELEV", z=5.4)
    # sill + lintel band
    v.rect(h0 - 0.05, z0 - 0.05, h1 + 0.05, z0, fc="#bdbdbd", ec=INK, lw="fine", layer="A-ELEV", z=5.3)


def door_elev(v, h0, h1, z0, z1, glazed=False):
    v.rect(h0, z0, h1, z1, fc="#efe6d8", ec=INK, lw="thin", layer="A-ELEV", z=5)
    f = 0.06
    v.rect(h0 + f, z0, h1 - f, z1 - f, fc="#e3d3bb", ec=INK, lw="fine", layer="A-ELEV", z=5.2)
    w = h1 - h0
    if w > 1.0:  # entrance: main leaf + side panel
        hm = h0 + 0.85
        v.line([(hm, z0), (hm, z1 - f)], lw="thin", layer="A-ELEV", z=5.4)
        for a, b in ((h0 + f, hm), (hm, h1 - f)):
            v.rect(a + 0.10, z0 + 1.10, b - 0.10, z1 - f - 0.15, fc=GLASS, ec=INK, lw="hair", layer="A-ELEV", z=5.5)
            v.rect(a + 0.10, z0 + 0.15, b - 0.10, z0 + 0.95, fc="none", ec=INK, lw="hair", layer="A-ELEV", z=5.5)
        v.line([(hm - 0.10, z0 + 1.0), (hm - 0.10, z0 + 1.15)], lw="med", layer="A-ELEV", z=5.6)


def facade(v, L, ops, title_side_left, steps=None, steps_front=None):
    """Generic facade. L = length (axis to axis). ops = list of (h0, h1, kind, z0, z1)."""
    e = 0.15
    # ground
    v.line([(-e - 1.2, M.Z_TN), (L + e + 1.2, M.Z_TN)], lw="xthick", layer="A-ELEV", z=6)
    v.rect(-e - 1.2, M.Z_TN - 0.12, L + e + 1.2, M.Z_TN, fc="none", ec="none", hatch="////", hcolor=LIGHT,
           layer="A-ELEV", z=2)
    # wall body
    v.rect(-e, M.Z_TN, L + e, M.Z_ACRO, fc="#f7f3ec", ec=INK, lw="thick", layer="A-ELEV", z=3)
    # plinth (soubassement en pierre)
    v.rect(-e, M.Z_TN, L + e, 0.15, fc="#d9d2c5", ec=INK, lw="thin", layer="A-ELEV", z=3.5)
    v.rect(-e, M.Z_TN, L + e, 0.15, fc="none", ec="none", hatch="---", hcolor="#a99f8c", layer="A-ELEV", z=3.6)
    # slab band (bandeau) + parapet coping
    v.rect(-e - 0.03, M.Z_CEIL + 0.0, L + e + 0.03, M.Z_SLAB + 0.06, fc="#e9e2d6", ec=INK, lw="thin", layer="A-ELEV",
           z=3.7)
    v.rect(-e - 0.04, M.Z_ACRO - 0.06, L + e + 0.04, M.Z_ACRO, fc="#d0d0d0", ec=INK, lw="thin", layer="A-ELEV", z=3.8)
    # corner pilasters (columns expressed)
    for hx in [0, L]:
        pass
    for h0, h1, kind, z0, z1 in ops:
        if kind == "door":
            door_elev(v, h0, h1, z0, z1)
        else:
            window_elev(v, h0, h1, z0, z1)
    if steps_front:
        a, b = steps_front
        for (x0, x1, z) in [(-0.02, 0, 0), (-0.15, 0, 0), (-0.30, 0, 0)]:
            pass
        v.rect(a, M.Z_TN, b, -0.02, fc="#e8e8e8", ec=INK, lw="thin", layer="A-ELEV", z=6)
        for z in (-0.15, -0.30):
            v.line([(a, z), (b, z)], lw="thin", layer="A-ELEV", z=6.1)
    if steps:
        # steps seen in profile, list of (h0, h1, ztop)
        for h0, h1, zt in steps:
            v.rect(min(h0, h1), M.Z_TN, max(h0, h1), zt, fc="#e8e8e8", ec=INK, lw="thin", layer="A-ELEV", z=6)


def elev_levels(v, x, side=-1):
    for z, t in [(M.Z_ACRO, "+3.90"), (M.Z_SLAB, "+3.24"), (2.20, "+2.20"), (1.00, "+1.00"), (0.0, "±0.00"),
                 (M.Z_TN, "-0.45")]:
        v.level(x, z, t, side=side, length_mm=14)


def elev_dims(v, x, zs, side=-1):
    v.dim(zs, x, "v", side=side, h=2.0)


def facade_est(v):
    # Viewer east, looking west: left = south (y=0), right = north (y=8). h = y
    ops = []
    for op in M.openings_on("v", 15):
        a, b = op["c"] - op["w"] / 2, op["c"] + op["w"] / 2
        ops.append((a, b, "door" if op["kind"].startswith("door") else "win", op["sill"], op["sill"] + op["h"]))
    facade(v, 8.0, ops, True, steps_front=(2.0, 4.0))
    v.text(3.0, -0.75, "Perron 3 marches", h=1.9, ha="center", va="top", color=GREY, layer="A-ELEV")
    elev_levels(v, -0.15 - 0.2, side=-1)
    v.dim([M.Z_TN, 0, 1.0, 2.2, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 8.15 + 0.7, "v", side=-1, h=1.9)
    v.dim([-0.15, 2.4, 3.6, 6.0, 7.0, 8.15], M.Z_TN - 0.55, "h", side=-1, h=1.9)
    for y, lab in zip(M.YA, M.YL):
        v.axis((y, M.Z_TN - 1.0), (y, M.Z_TN - 1.0 + 0.001), lab, ends=(True, False))


def facade_ouest(v):
    # looking east: left = north (y=8), right = south. h = 8 - y
    ops = []
    for op in M.openings_on("v", 0):
        a, b = 8 - (op["c"] + op["w"] / 2), 8 - (op["c"] - op["w"] / 2)
        ops.append((a, b, "win", op["sill"], op["sill"] + op["h"]))
    facade(v, 8.0, ops, True)
    elev_levels(v, -0.15 - 0.2, side=-1)
    v.dim([M.Z_TN, 0, 1.0, 2.2, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 8.15 + 0.7, "v", side=-1, h=1.9)
    v.dim([-0.15, 4.8, 6.2, 8.15], M.Z_TN - 0.55, "h", side=-1, h=1.9)
    for y, lab in zip(M.YA, M.YL):
        v.axis((8 - y, M.Z_TN - 1.0), (8 - y, M.Z_TN - 1.0 + 0.001), lab, ends=(True, False))


def facade_sud(v):
    # looking north: h = x
    ops = []
    for op in M.openings_on("h", 0):
        a, b = op["c"] - op["w"] / 2, op["c"] + op["w"] / 2
        ops.append((a, b, "win", op["sill"], op["sill"] + op["h"]))
    facade(v, 15.0, ops, True, steps=[(15.15, 16.35, -0.30), (15.15, 16.05, -0.15), (15.15, 15.75, -0.02)])
    elev_levels(v, -0.15 - 0.2, side=-1)
    xs = [-0.15] + sum([[a, b] for a, b, *_ in ops], []) + [15.15]
    v.dim(xs, M.Z_TN - 0.55, "h", side=-1, h=1.9)
    v.dim([0, 3, 5, 7, 9, 10, 15], M.Z_TN - 1.05, "h", side=-1, h=1.9)
    v.dim([M.Z_TN, 0, 1.0, 1.6, 2.2, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 16.35 + 0.8, "v", side=-1, h=1.9)
    for x, lab in zip(M.XA, M.XL):
        v.axis((x, M.Z_TN - 1.5), (x, M.Z_TN - 1.5 + 0.001), lab, ends=(True, False))


def facade_nord(v):
    # looking south: h = 15 - x
    ops = []
    for op in M.openings_on("h", 8):
        a, b = 15 - (op["c"] + op["w"] / 2), 15 - (op["c"] - op["w"] / 2)
        ops.append((a, b, "win", op["sill"], op["sill"] + op["h"]))
    facade(v, 15.0, ops, True, steps=[(-0.15, -1.35, -0.30), (-0.15, -1.05, -0.15), (-0.15, -0.75, -0.02)])
    elev_levels(v, -1.35 - 0.2, side=-1)
    xs = [-0.15] + sum([[a, b] for a, b, *_ in ops], []) + [15.15]
    v.dim(xs, M.Z_TN - 0.55, "h", side=-1, h=1.9)
    v.dim([0, 5, 10, 15], M.Z_TN - 1.05, "h", side=-1, h=1.9)
    v.dim([M.Z_TN, 0, 1.0, 2.2, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 15.15 + 0.7, "v", side=-1, h=1.9)
    for x, lab in zip(M.XA, M.XL):
        v.axis((15 - x, M.Z_TN - 1.5), (15 - x, M.Z_TN - 1.5 + 0.001), lab, ends=(True, False))


def facade_legend(S, x, y):
    S.text(x, y, "FINITIONS DE FAÇADE", h=3.0, weight="bold", color=ACCENT)
    items = [("#f7f3ec", None, "Enduit extérieur au mortier de ciment, 3 couches,\nfinition grattée, teinte blanc cassé"),
             ("#d9d2c5", "---", "Soubassement : placage pierre naturelle h = 0.60 m"),
             ("#e9e2d6", None, "Bandeau de rive en béton, peinture façade"),
             ("#d0d0d0", None, "Couvertine d'acrotère (chaperon béton)"),
             (GLASS, None, "Menuiseries aluminium laqué, double vitrage 4/16/4"),
             ("#e3d3bb", None, "Porte d'entrée bois massif")]
    y -= 7
    for fc, hatch, txt in items:
        S.rect(x, y - 3.5, x + 10, y + 1, fc=fc, ec=INK, lw="fine", hatch=hatch, hcolor="#a99f8c")
        S.text(x + 13, y + 1, txt, h=2.0, va="top")
        y -= 10


def sheet_facades_1(S):
    v1 = View(S, ox=75, oy=268, scale=50)
    facade_sud(v1)
    S.view_title(45, 392, "FAÇADE SUD (LATÉRALE — CUISINE / SALON)", "1:50")
    v2 = View(S, ox=75, oy=95, scale=50)
    facade_est(v2)
    S.view_title(45, 198, "FAÇADE PRINCIPALE EST (ENTRÉE)", "1:50")
    facade_legend(S, 300, 190)


def sheet_facades_2(S):
    v1 = View(S, ox=100, oy=268, scale=50)
    facade_nord(v1)
    S.view_title(45, 392, "FAÇADE NORD (CHAMBRES)", "1:50")
    v2 = View(S, ox=75, oy=95, scale=50)
    facade_ouest(v2)
    S.view_title(45, 198, "FAÇADE POSTÉRIEURE OUEST", "1:50")
    facade_legend(S, 300, 190)


# =====================================================================================
# Sections
# =====================================================================================
def earth(v, h0, h1, z):
    v.rect(h0, z - 0.25, h1, z, fc="none", ec="none", hatch="////", hcolor=LIGHT, layer="A-SECT-EARTH", z=1.5)
    v.line([(h0, z), (h1, z)], lw="thick", layer="A-SECT", z=6)


def conc(v, x0, z0, x1, z1, z=5):
    v.rect(x0, z0, x1, z1, fc=CONC, ec=INK, lw="thick", hatch="////", hcolor="#8f8f8f", layer="A-SECT-CONC", z=z,
           dxf_pattern="ANSI31")


def masonry(v, x0, z0, x1, z1, z=4.5):
    v.rect(x0, z0, x1, z1, fc=POCHE, ec=INK, lw="thick", layer="A-SECT-MAS", z=z)


def section_common(v, L, walls_cut, beams_cut, beyond, footings_beyond, ext_steps=False, openings_cut=()):
    """Generic section. walls_cut: list of (pos, thickness). beams_cut: list of (pos, depth).
    openings_cut: list of (pos, thick, z0, z1, kind)."""
    e = 0.15
    # earth + ground line outside
    earth(v, -e - 1.6, -e, M.Z_TN)
    earth(v, L + e, L + e + (2.4 if ext_steps else 1.6), M.Z_TN)
    # hidden foundations beyond
    for pos, size, ztop in footings_beyond:
        v.rect(pos - size / 2, M.Z_SEM_BOT, pos + size / 2, ztop, fc="none", ec=GREY, lw="fine", ls="hidden",
               layer="A-SECT-HID")
        v.rect(pos - size / 2 - 0.1, M.Z_PROP, pos + size / 2 + 0.1, M.Z_SEM_BOT, fc="none", ec=GREY, lw="fine",
               ls="hidden", layer="A-SECT-HID")
        v.rect(pos - 0.15, ztop, pos + 0.15, M.Z_LONG_BOT, fc="none", ec=GREY, lw="fine", ls="hidden",
               layer="A-SECT-HID")
    # soil below dallage (fill) + hérisson
    v.rect(-e, M.Z_HERISSON_BOT, L + e, M.Z_DALLAGE_BOT, fc="none", ec="none", hatch="oo", hcolor="#b5b5b5",
           layer="A-SECT", z=2)
    v.rect(-e, -1.75, L + e, M.Z_HERISSON_BOT, fc="none", ec="none", hatch="..", hcolor="#cdcdcd", layer="A-SECT", z=1.2)
    # dallage + chape
    conc(v, -e, M.Z_DALLAGE_BOT, L + e, M.Z_DALLAGE_TOP)
    v.rect(-e, M.Z_DALLAGE_TOP, L + e, 0.0, fc="white", ec=INK, lw="fine", layer="A-SECT", z=5)
    # longrines cut under walls
    for pos, t in walls_cut:
        conc(v, pos - 0.15, M.Z_LONG_BOT, pos + 0.15, M.Z_LONG_TOP, z=5.5)
    # slab
    conc(v, -e, M.Z_CEIL, L + e, M.Z_SLAB)
    # beams
    for pos, d in beams_cut:
        conc(v, pos - 0.15, M.Z_SLAB - d, pos + 0.15, M.Z_SLAB, z=5.5)
    # walls cut (full height between floor and beam soffit)
    for pos, t in walls_cut:
        bd = dict(beams_cut).get(pos, 0.24)
        masonry(v, pos - t / 2, 0.0 if t < 0.2 else M.Z_LONG_TOP, pos + t / 2, M.Z_SLAB - bd)
    # openings cut in walls
    for pos, t, z0, z1, kind in openings_cut:
        v.rect(pos - t / 2, z0, pos + t / 2, z1, fc="white", ec="white", lw="fine", layer="A-SECT", z=5.6)
        v.line([(pos - t / 2, z0), (pos - t / 2, z1)], lw="fine", layer="A-SECT", z=5.7)
        v.line([(pos + t / 2, z0), (pos + t / 2, z1)], lw="fine", layer="A-SECT", z=5.7)
        conc(v, pos - t / 2, z1, pos + t / 2, z1 + 0.20, z=5.8)  # lintel
        if kind == "win":
            v.rect(pos - t / 2 - 0.03, z0 - 0.05, pos + t / 2 + 0.03, z0, fc="#bdbdbd", ec=INK, lw="fine",
                   layer="A-SECT", z=5.8)
            v.rect(pos - 0.03, z0, pos + 0.03, z1, fc=GLASS, ec=INK, lw="fine", layer="A-SECT", z=5.9)
        else:
            v.rect(pos - 0.03, z0, pos + 0.03, z1, fc="#e3d3bb", ec=INK, lw="fine", layer="A-SECT", z=5.9)
    # acrotères
    for x0 in (-e, L + e - 0.10):
        conc(v, x0, M.Z_SLAB, x0 + 0.10, M.Z_ACRO, z=5.5)
        v.rect(x0 - 0.04, M.Z_ACRO - 0.06, x0 + 0.14, M.Z_ACRO, fc="#d0d0d0", ec=INK, lw="thin", layer="A-SECT", z=6)
    # terrace layers
    v.poly([(-0.05, M.Z_SLAB), (L + 0.05, M.Z_SLAB), (L + 0.05, M.Z_SLAB + 0.08), (L / 2, M.Z_FORME + 0.04),
            (-0.05, M.Z_SLAB + 0.08)], fc="#ededed", ec=INK, lw="fine", layer="A-SECT", z=5)
    v.poly([(-0.05, M.Z_SLAB + 0.08), (L / 2, M.Z_FORME + 0.04), (L + 0.05, M.Z_SLAB + 0.08),
            (L + 0.05, M.Z_SLAB + 0.13), (L / 2, M.Z_FORME + 0.09), (-0.05, M.Z_SLAB + 0.13)], fc="#9e9e9e", ec=INK,
           lw="fine", layer="A-SECT", z=5)
    # relevés d'étanchéité
    for x0 in (-0.05, L + 0.05 - 0.02):
        v.rect(x0, M.Z_SLAB + 0.08, x0 + 0.02, M.Z_SLAB + 0.30, fc="#6e6e6e", ec="none", layer="A-SECT", z=6)
    # ceiling plaster
    v.line([(-0.0, M.Z_CEIL - 0.02), (L, M.Z_CEIL - 0.02)], lw="hair", color=GREY, layer="A-SECT")
    for b in beyond:
        b(v)
    # steps
    if ext_steps:
        for x0, x1, z in M.PERRON["steps"]:
            conc(v, L + e, M.Z_TN, x1, z, z=5.2)
        conc(v, L + e, M.Z_TN, M.PERRON["steps"][0][1], -0.02, z=5.3)


def section_levels(v, x, side=-1):
    for z, t in [(M.Z_ACRO, "+3.90"), (M.Z_SLAB, "+3.24"), (M.Z_CEIL, "+3.00"), (0.0, "±0.00"),
                 (M.Z_TN, "-0.45 TN"), (M.Z_SEM_BOT, "-1.50")]:
        v.level(x, z, t, side=side, length_mm=15)


def section_AA(v):
    """Cut x = 12.50 looking west. h = y."""
    walls = [(0, M.EXT), (5, M.INT), (8, M.EXT)]
    beams = [(0, M.PP_H), (5, M.PP_H), (8, M.PP_H)]
    ops = [(0, M.EXT, 1.0, 2.2, "win"), (8, M.EXT, 1.0, 2.2, "win")]

    def beyond(v):
        # PS beam at axis 3 seen beyond
        v.line([(0.15, M.Z_PS_SOF), (4.85, M.Z_PS_SOF)], lw="fine", layer="A-SECT-BEY")
        v.line([(5.15, M.Z_PS_SOF), (7.85, M.Z_PS_SOF)], lw="fine", layer="A-SECT-BEY")
        # column B3 seen
        v.rect(4.85, 0, 5.15, M.Z_PP_SOF, fc="none", ec=INK, lw="fine", layer="A-SECT-BEY")
        # wall x = 10 (R3 west wall) with R3 door seen beyond in wall y=5 : show WC east wall (x=9) in hall
        v.rect(0.15, 0.0, 2.05, M.Z_CEIL, fc="none", ec=GREY, lw="fine", layer="A-SECT-BEY")
        v.text(1.1, 1.5, "Mur WC\n(au-delà)", h=1.8, ha="center", va="center", color=GREY, layer="A-SECT-BEY")
        v.text(3.5, 1.5, "HALL", h=2.8, ha="center", weight="bold", layer="A-SECT")
        v.text(6.5, 1.5, "CHAMBRE 03", h=2.8, ha="center", weight="bold", layer="A-SECT")
    fb = [(0, 1.0, M.Z_SEM_TOP_S2), (5, 1.2, M.Z_SEM_TOP_S1), (8, 1.0, M.Z_SEM_TOP_S2)]
    section_common(v, 8.0, walls, beams, [beyond], fb, openings_cut=ops)
    section_levels(v, -1.9)
    v.dim([M.Z_SEM_BOT, M.Z_TN, 0, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 9.6, "v", side=-1, h=1.9)
    v.dim([0, 1.0, 2.2, M.Z_CEIL], 9.0, "v", side=-1, h=1.9)
    v.dim([0, 5, 8], -2.25, "h", side=-1, h=1.9)
    for y, lab in zip(M.YA, M.YL):
        v.axis((y, -1.85), (y, 4.35), lab, ends=(False, True))


def section_BB(v):
    """Cut y = 2.90 looking north. h = x."""
    walls = [(0, M.EXT), (3, M.INT), (15, M.EXT)]
    beams = [(0, M.PS_H), (5, M.PS_H), (10, M.PS_H), (15, M.PS_H)]
    ops = [(0, M.EXT, 1.0, 2.2, "win"), (3, M.INT, 0.0, 2.2, "door"), (15, M.EXT, 0.0, 2.2, "door")]

    def beyond(v):
        # PP beam along axis B seen
        v.line([(0.15, M.Z_PP_SOF), (14.85, M.Z_PP_SOF)], lw="fine", layer="A-SECT-BEY")
        for x in (5, 10):
            v.rect(x - 0.15, 0, x + 0.15, M.Z_PP_SOF, fc="none", ec=INK, lw="fine", layer="A-SECT-BEY")
        for a, b in [(3.70, 4.60), (5.40, 6.30), (10.40, 11.30)]:
            v.rect(a, 0, b, 2.20, fc="#efe6d8", ec=INK, lw="fine", layer="A-SECT-BEY", z=4)
            v.rect(a + 0.05, 0, b - 0.05, 2.15, fc="none", ec=GREY, lw="hair", layer="A-SECT-BEY", z=4)
        v.text(1.5, 1.45, "SALON", h=2.8, ha="center", weight="bold", layer="A-SECT")
        v.text(8.0, 1.45, "HALL", h=2.8, ha="center", weight="bold", layer="A-SECT")
        for xm, lab in [(4.15, "P2"), (5.85, "P2"), (10.85, "P2")]:
            v.text(xm, 2.35, lab, h=1.8, ha="center", color=GREY, layer="A-SECT-BEY")
    fb = [(0, 1.0, M.Z_SEM_TOP_S2), (5, 1.2, M.Z_SEM_TOP_S1), (10, 1.2, M.Z_SEM_TOP_S1), (15, 1.0, M.Z_SEM_TOP_S2)]
    # longrines are cut on all four Y-axes
    section_common(v, 15.0, walls, beams, [beyond], fb, ext_steps=True, openings_cut=ops)
    for x in (5, 10):
        conc(v, x - 0.15, M.Z_LONG_BOT, x + 0.15, M.Z_LONG_TOP, z=5.5)
    section_levels(v, -1.9)
    v.dim([M.Z_SEM_BOT, M.Z_TN, 0, M.Z_CEIL, M.Z_SLAB, M.Z_ACRO], 17.6, "v", side=-1, h=1.9)
    v.dim([0, 2.2, M.Z_CEIL], 17.0, "v", side=-1, h=1.9)
    v.dim([0, 3, 5, 10, 15], -2.25, "h", side=-1, h=1.9)
    for x, lab in zip(M.XA, M.XL):
        v.axis((x, -1.85), (x, 4.35), lab, ends=(False, True))


def sheet_sections(S):
    v1 = View(S, ox=80, oy=280, scale=50)
    section_BB(v1)
    S.view_title(45, 392, "COUPE B-B", "1:50")
    v2 = View(S, ox=80, oy=95, scale=50)
    section_AA(v2)
    S.view_title(45, 205, "COUPE A-A", "1:50")
    x0, y = 300, 200
    y = S.notes(x0, y, "COMPLEXES CONSTRUCTIFS", [
        "TERRASSE : gravillons 5 cm / étanchéité multicouche /",
        "  isolation 4 cm / forme de pente 2 % / plancher corps",
        "  creux 20+4 / enduit plâtre 2 cm.",
        "MUR EXTÉRIEUR : enduit ciment 2 cm / brique 15 /",
        "  lame d'air 5 / brique 10 / enduit plâtre 1.5 cm.",
        "SOL RDC : carrelage + mortier de pose 5 cm / dallage",
        "  BA ép. 10 cm (TS Ø6 maille 20×20) / film polyane /",
        "  hérisson en pierres sèches 20 cm / remblai compacté.",
        "FONDATIONS : semelles isolées BA sous poteaux,",
        "  reliées par longrines 30×40 ; gros béton/propreté",
        "  dosé à 150 kg/m³ ép. 10 cm.",
    ], h=2.05)
    S.text(x0, y - 8, "LÉGENDE DES HACHURES", h=3.0, weight="bold", color=ACCENT)
    y -= 15
    for fc, hatch, txt in [(CONC, "////", "Béton armé coupé"), (POCHE, None, "Maçonnerie coupée"),
                           ("white", "oo", "Hérisson en pierres sèches"), ("white", "////", "Terrain naturel")]:
        S.rect(x0, y - 3.5, x0 + 10, y + 1, fc=fc, ec=INK, lw="fine", hatch=hatch, hcolor="#8f8f8f")
        S.text(x0 + 13, y - 1.2, txt, h=2.1, va="center")
        y -= 7
    S.line([(x0, y), (x0 + 10, y)], lw="fine", color=GREY, ls="hidden")
    S.text(x0 + 13, y, "Semelles au-delà (cachées)", h=2.1, va="center")
