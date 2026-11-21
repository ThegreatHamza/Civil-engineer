"""Structural / execution sheets: setting-out, foundations, formwork, reinforcement details.

Pre-design hypotheses (to be checked by the engineer of record):
  concrete C25/30 (fc28 = 25 MPa), steel HA FeE400, soil bearing 2.0 bar,
  BAEL 91 mod. 99 / CBA 93, RPA 99 v.2003 (zone IIa assumed).
"""
import math

from shapely.geometry import box
from shapely.ops import unary_union

import model as M
from arch import plan_axes
from drawing import ACCENT, CONC, GREY, INK, REBAR, View

SEM = {(x, y): (M.footing_type(x, y), *M.FOOTINGS[M.footing_type(x, y)]) for x, y in M.COLUMNS}
FOUND_FC = "#ececec"


def col_label(x, y):
    return f"{M.YL[M.YA.index(y)]}{M.XL[M.XA.index(x)]}"


def columns(v, hatch=True):
    for x, y in M.COLUMNS:
        v.rect(x - 0.15, y - 0.15, x + 0.15, y + 0.15, fc="#3a3a3a", ec=INK, lw="thin", layer="S-COLS", z=7)


def axis_dims(v, top=False):
    v.dim([0, 5, 10, 15], -0.95, "h", ext_from=-0.75, side=-1)
    v.dim([0, 15], -1.5, "h", ext_from=-0.75, side=-1)
    v.dim([0, 5, 8], -0.95, "v", ext_from=-0.75)
    v.dim([0, 8], -1.5, "v", ext_from=-0.75)


def struct_notes(S, x, y, extra=()):
    return S.notes(x, y, "HYPOTHÈSES & MATÉRIAUX", [
        "Règlements : BAEL 91 mod. 99 / CBA 93,",
        "  RPA 99 version 2003 (zone IIa supposée).",
        "Béton : C25/30, fc28 = 25 MPa, dosé 350 kg/m³",
        "  (CPJ 42.5). Béton de propreté : 150 kg/m³.",
        "Acier : HA FeE400 (fe = 400 MPa) ;",
        "  treillis soudé TS Ø6 FeE520.",
        "Sol : σ adm = 2.00 bars (à confirmer par",
        "  l'étude géotechnique / essais de sol).",
        "Enrobages : fondations 5 cm, poteaux /",
        "  poutres 3 cm, dalles 2 cm.",
        "Charges terrasse : G = 6.50 kN/m², Q = 1.00 kN/m².",
        *extra,
    ], h=2.05)


def warning(S, x, y):
    S.rect(x - 2, y - 17, x + 108, y + 4, fc="#fff4e5", ec="#c77700", lw="thin")
    S.text(x, y, "IMPORTANT", h=2.6, weight="bold", color="#9a5b00", va="top")
    S.text(x, y - 4.5, "Prédimensionnement établi pour un RDC sans\nétage. À vérifier et viser par un ingénieur\n"
           "agréé avant exécution (étude de sol, note de calcul).", h=2.0, va="top")


# =====================================================================================
# 06 - Setting-out plan
# =====================================================================================
def sheet_implantation(S):
    v = View(S, ox=86, oy=150, scale=50)
    # building outline (outer faces) dashed
    v.rect(-0.15, -0.15, 15.15, 8.15, fc="none", ec=GREY, lw="thin", ls="dash", layer="S-OUTL")
    plan_axes(v)
    # control diagonals
    v.line([(0, 0), (15, 8)], lw="fine", color=ACCENT, ls="dash", layer="S-IMPL")
    v.line([(0, 8), (15, 0)], lw="fine", color=ACCENT, ls="dash", layer="S-IMPL")
    ang = math.degrees(math.atan2(8, 15))
    v.text(6.0, 3.35, "Diagonale A1–C4 = 17.00 m", h=2.3, rot=ang, color=ACCENT, layer="S-IMPL")
    v.text(9.6, 4.95, "Diagonale C1–A4 = 17.00 m", h=2.3, rot=-ang, ha="right", color=ACCENT, layer="S-IMPL",
           va="top")
    columns(v)
    for x, y in M.COLUMNS:
        v.line([(x - 0.3, y), (x + 0.3, y)], lw="hair", color="white", layer="S-IMPL", z=8)
        v.line([(x, y - 0.3), (x, y + 0.3)], lw="hair", color="white", layer="S-IMPL", z=8)
        lx = x + (0.25 if x < 15 else -0.25)
        v.text(lx, y + 0.22, col_label(x, y), h=2.3, ha="left" if x < 15 else "right", weight="bold",
               layer="S-TEXT")
        v.text(lx, y - 0.22, f"({x:.2f} ; {y:.2f})", h=1.8, ha="left" if x < 15 else "right", va="top",
               color=GREY, layer="S-TEXT")
    # origin
    v.circle(0, 0, 0.32, fc="none", ec=ACCENT, lw="med", layer="S-IMPL")
    v.leader([(-0.2, -0.2), (-1.0, -0.6), (-1.6, -0.6)], "", h=2.0)
    v.text(-1.7, -0.45, "Point origine O", h=2.2, ha="right", weight="bold", color=ACCENT, layer="S-IMPL")
    v.text(-1.7, -0.75, "(0.00 ; 0.00)", h=2.0, ha="right", va="top", color=ACCENT, layer="S-IMPL")
    # profiles boards (chaises d'implantation)
    for x in M.XA:
        for yy in (-2.15, 10.15):
            v.rect(x - 0.4, yy - 0.04, x + 0.4, yy + 0.04, fc="#b48b5a", ec=INK, lw="fine", layer="S-IMPL")
            v.circle(x, yy, 0.05, fc=INK, ec=INK, lw="hair", layer="S-IMPL")
    for y in M.YA:
        for xx in (-2.15, 17.15):
            v.rect(xx - 0.04, y - 0.4, xx + 0.04, y + 0.4, fc="#b48b5a", ec=INK, lw="fine", layer="S-IMPL")
            v.circle(xx, y, 0.05, fc=INK, ec=INK, lw="hair", layer="S-IMPL")
    v.dim([0, 5, 10, 15], -0.95, "h", ext_from=-0.3, side=-1)
    v.dim([0, 15], -1.5, "h", ext_from=-0.3, side=-1)
    v.dim([0, 5, 8], -0.95, "v", ext_from=-0.3)
    v.dim([0, 8], -1.5, "v", ext_from=-0.3)
    v.dim([-0.15, 15.15], 8.85, "h", ext_from=8.3)
    v.dim([-0.15, 8.15], 16.0, "v", ext_from=15.3, side=-1)
    S.view_title(60, 393, "PLAN D'IMPLANTATION DES AXES ET POTEAUX", "1:50")
    S.north_arrow(40, 360)

    rows = [[col_label(x, y), f"{x:.2f}", f"{y:.2f}", "30 × 30"] for x, y in M.COLUMNS]
    yb = S.table(473, 392, [("Poteau", 22), ("X (m)", 24), ("Y (m)", 24), ("Section", 32)], rows,
                 title="COORDONNÉES DES POTEAUX", h=2.2, row_h=5.2)
    yb = S.notes(473, yb - 10, "PROCÉDURE D'IMPLANTATION", [
        "1. Matérialiser le point O (axes 1 / A) et",
        "   la direction de l'axe A.",
        "2. Implanter les axes 1 à 4 et A à C au",
        "   théodolite / ruban (cotes entre axes).",
        "3. Contrôler l'équerrage par les diagonales :",
        "   A1–C4 = C1–A4 = 17.00 m (tol. ± 1 cm).",
        "4. Reporter les axes sur des chaises",
        "   d'implantation placées à 1.50 m minimum",
        "   au-delà des fouilles (clous + cordeaux).",
        "5. Niveau de référence ±0.00 = sol fini RDC",
        "   = TN + 0.45 m (à caler sur repère fixe).",
    ], h=2.05)
    S.text(473, yb - 6, "LÉGENDE", h=3.0, weight="bold", color=ACCENT)
    S.rect(473, yb - 15, 482, yb - 11, fc="#b48b5a", ec=INK, lw="fine")
    S.text(486, yb - 13, "Chaise d'implantation", h=2.1, va="center")
    S.rect(474.5, yb - 23, 479.5, yb - 18, fc="#3a3a3a", ec=INK, lw="fine")
    S.text(486, yb - 20.5, "Poteau BA 30 × 30", h=2.1, va="center")


# =====================================================================================
# 07 - Foundation plan
# =====================================================================================
def foundation_geoms():
    sems = {}
    for (x, y), (name, a, h) in SEM.items():
        sems[(x, y)] = box(x - a / 2, y - a / 2, x + a / 2, y + a / 2)
    strips = []
    for y in M.YA:
        strips.append(box(0, y - 0.15, 15, y + 0.15))
    for x in M.XA:
        strips.append(box(x - 0.15, 0, x + 0.15, 8))
    long_ = unary_union(strips).difference(unary_union(list(sems.values())))
    return sems, long_


def coupe_type_foundation(S, v, a=1.20, hs=0.40, ztop=M.Z_SEM_TOP_S1):
    # Section through a footing + tie-beam + slab on grade (1:20). h = horizontal
    # earth
    v.rect(-1.0, M.Z_PROP - 0.15, 1.0, M.Z_TN, fc="none", ec="none", hatch="..", hcolor="#cdcdcd", layer="S-SECT", z=1)
    v.line([(-1.0, M.Z_TN), (-0.15, M.Z_TN)], lw="thick", layer="S-SECT")
    # lean concrete
    v.rect(-a / 2 - 0.10, M.Z_PROP, a / 2 + 0.10, M.Z_SEM_BOT, fc="#f2f2f2", ec=INK, lw="thin", hatch="..",
           hcolor=GREY, layer="S-SECT", z=3)
    # footing + starter column + tie beam (side)
    v.rect(-a / 2, M.Z_SEM_BOT, a / 2, ztop, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, ztop, 0.15, M.Z_LONG_BOT, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, M.Z_LONG_BOT, 1.0, M.Z_LONG_TOP, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, M.Z_LONG_TOP, 0.15, 0.35, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.break_line((-0.25, 0.35), (0.25, 0.35))
    v.break_line((1.0, M.Z_LONG_BOT - 0.08), (1.0, M.Z_LONG_TOP + 0.08))
    # slab on grade on the inside (right)
    v.rect(0.15, M.Z_HERISSON_BOT, 1.0, M.Z_DALLAGE_BOT, fc="none", ec="none", hatch="oo", hcolor="#b5b5b5",
           layer="S-SECT", z=2)
    v.rect(0.15, M.Z_DALLAGE_BOT, 1.0, M.Z_DALLAGE_TOP, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3.2)
    v.rect(0.15, M.Z_DALLAGE_TOP, 1.0, 0.0, fc="white", ec=INK, lw="fine", layer="S-SECT", z=3.2)
    # rebars
    c = 0.05
    xs = [-a / 2 + c + i * (a - 2 * c) / math.ceil((a - 2 * c) / 0.15 - 1e-9) for i in range(math.ceil((a - 2 * c) / 0.15 - 1e-9) + 1)]
    for xx in xs:
        v.dot(xx, M.Z_SEM_BOT + c + 0.018, 0.007)
    v.line([(-a / 2 + c, M.Z_SEM_BOT + c + 0.25), (-a / 2 + c, M.Z_SEM_BOT + c), (a / 2 - c, M.Z_SEM_BOT + c),
            (a / 2 - c, M.Z_SEM_BOT + c + 0.25)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    for xx in (-0.115, 0.115):
        sg = -1 if xx < 0 else 1
        v.line([(xx + sg * 0.30, M.Z_SEM_BOT + c + 0.03), (xx, M.Z_SEM_BOT + c + 0.03), (xx, 0.35)], lw="thick",
               color=REBAR, layer="S-REBAR", z=8)
    for z in [ztop - 0.05] + [ztop + 0.10 + 0.10 * i for i in range(int((0.35 - ztop - 0.12) / 0.10))]:
        v.line([(-0.12, z), (0.12, z)], lw="thin", color=REBAR, layer="S-REBAR", z=8)
    for z in (M.Z_LONG_BOT + 0.04, M.Z_LONG_TOP - 0.04):
        v.line([(0.15, z), (1.0, z)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    for xx in [0.3, 0.5, 0.7, 0.9]:
        v.line([(xx, M.Z_LONG_BOT + 0.035), (xx, M.Z_LONG_TOP - 0.035)], lw="thin", color=REBAR, layer="S-REBAR",
               z=8)
    # levels / dims
    for z, t in [(0.0, "±0.00"), (M.Z_TN, "-0.45 TN"), (ztop, f"{ztop:+.2f}"), (M.Z_SEM_BOT, "-1.50"),
                 (M.Z_PROP, "-1.60")]:
        v.level(-a / 2 - 0.15 if z < M.Z_TN else -0.6, z, t, side=-1, length_mm=11, h=2.0)
    v.dim([-a / 2, a / 2], M.Z_PROP - 0.2, "h", side=-1, h=2.0)
    v.dim([M.Z_SEM_BOT, ztop], a / 2 + 0.25, "v", side=-1, h=2.0)
    v.leader([(0.3, M.Z_SEM_BOT + 0.07), (0.85, M.Z_SEM_BOT + 0.25), (1.05, M.Z_SEM_BOT + 0.25)],
             "Nappe inf. 9T12 e=14\n(2 directions)", h=1.9)
    v.leader([(0.115, -0.75), (0.5, -0.95), (1.05, -0.95)], "Amorces 8T12", h=1.9)
    v.leader([(0.6, M.Z_LONG_TOP - 0.04), (0.75, 0.25), (1.05, 0.25)], "Longrine 30×40", h=1.9)


def sheet_foundations(S):
    v = View(S, ox=86, oy=150, scale=50)
    sems, long_ = foundation_geoms()
    v.geom(long_, fc="#f6f6f6", ec=INK, lw="med", layer="S-LONG", z=3)
    for (x, y), g in sems.items():
        name, a, h = SEM[(x, y)]
        v.geom(g, fc=FOUND_FC, ec=INK, lw="thick", layer="S-SEM", z=4)
        v.geom(g.buffer(0.10, join_style="mitre"), fc="none", ec=GREY, lw="fine", ls="hidden", layer="S-PROP", z=3.5)
        dx = 0.12 if x < 15 else -0.12
        v.text(x + (a / 2 - 0.05) * (1 if x < 15 else -1), y - a / 2 + 0.08, name, h=2.6,
               ha="right" if x < 15 else "left", weight="bold", layer="S-TEXT")
        _ = dx
    columns(v)
    plan_axes(v, yr=(-2.6, 16.6))
    axis_dims(v)
    # footing dims on two examples
    v.dim([4.4, 5.6], 4.0, "h", ext_from=4.4, side=-1, h=2.0)
    v.dim([4.4, 5.6], 5.95, "v", ext_from=5.6, side=-1, h=2.0)
    v.dim([-0.5, 0.5], 8.85, "h", ext_from=8.5, h=2.0)
    # tie-beam labels
    for (x, y, rot) in [(2.5, 0.2, 0), (7.5, 5.2, 0), (12.5, 8.2, 0), (2.5, 5.2, 0)]:
        v.text(x, y, "L 30×40", h=2.1, ha="center", rot=rot, layer="S-TEXT")
    for (x, y) in [(0.2, 2.5), (5.2, 2.5), (10.2, 2.5), (14.8, 2.5), (5.2, 6.5)]:
        v.text(x, y, "L 30×40", h=2.1, ha="center", rot=90, va="bottom" if x < 15 else "top", layer="S-TEXT")
    v.text(7.5, 2.6, "DALLAGE BA ép. 10 cm sur hérisson 20 cm", h=2.6, ha="center", color=GREY, layer="S-TEXT")
    v.text(7.5, 2.25, "(TS Ø6 maille 20×20, film polyane)", h=2.1, ha="center", va="top", color=GREY, layer="S-TEXT")
    # section marker for the type detail
    v.line([(4.0, 5.0), (3.2, 5.0)], lw="xthick", color=ACCENT, layer="S-SECT")
    v.label_box(2.9, 5.0, "D1", h=2.3)
    S.view_title(60, 393, "PLAN DE FONDATIONS", "1:50")
    S.north_arrow(40, 360)

    # type detail at 1:20
    vd = View(S, ox=508, oy=343, scale=20)
    coupe_type_foundation(S, vd)
    S.view_title(473, 393, "DÉTAIL D1 — SEMELLE S1", "1:20", h=3.3)
    rows = [["S1", "centraux", "2", "1.20×1.20×0.40", "9T12 e=14 (2 dir.)"],
            ["S2", "de rive", "6", "1.10×1.10×0.35", "8T12 e=14 (2 dir.)"],
            ["S3", "d'angle", "4", "1.00×1.00×0.35", "7T12 e=15 (2 dir.)"],
            ["L", "tous axes", f"{M.longrine_length():.1f} ml", "0.30×0.40", "3T14 + 3T14"]]
    y = S.table(437, 232, [("Rep.", 10), ("Poteaux", 16), ("Nb", 12), ("A×B×h (m)", 32), ("Armatures", 36)], rows,
                title="TABLEAU DES FONDATIONS", h=2.0, row_h=5.2)
    y = struct_notes(S, 473, y - 10, extra=(
        "Fond de fouille : -1.60 m / sol fini (≈ 1.15 m",
        "  sous TN), sur bon sol après purge.",
        "Longrines : arase supérieure à -0.05 m.",
    ))
    warning(S, 473, y - 4)


# =====================================================================================
# 08 - Formwork plan (roof slab)
# =====================================================================================
def poutrelle_positions(x0, x1, sp=0.65):
    n = int((x1 - x0) / sp) + 1
    start = x0 + ((x1 - x0) - (n - 1) * sp) / 2
    return [start + i * sp for i in range(n)]


def sheet_formwork(S):
    v = View(S, ox=86, oy=150, scale=50)
    v.rect(-0.15, -0.15, 15.15, 8.15, fc="white", ec=INK, lw="thick", layer="S-SLAB", z=2)
    v.rect(-0.05, -0.05, 15.05, 8.05, fc="none", ec=GREY, lw="fine", ls="dash", layer="S-ACRO", z=2.2)
    # beams
    beams = []
    for y in M.YA:
        for i in range(3):
            beams.append(("PP", box(M.XA[i] + 0.15, y - 0.15, M.XA[i + 1] - 0.15, y + 0.15)))
    for x in M.XA:
        for j in range(2):
            beams.append(("PS", box(x - 0.15, M.YA[j] + 0.15, x + 0.15, M.YA[j + 1] - 0.15)))
    for kind, g in beams:
        v.geom(g, fc="#dfe7ee" if kind == "PP" else "#eef2f5", ec=INK, lw="med", layer="S-BEAM", z=4)
    columns(v)
    # poutrelles (joists) spanning along Y between PP beams
    for i in range(3):
        for j in range(2):
            x0, x1 = M.XA[i] + 0.15, M.XA[i + 1] - 0.15
            y0, y1 = M.YA[j] + 0.15, M.YA[j + 1] - 0.15
            for px in poutrelle_positions(x0, x1):
                v.rect(px - 0.06, y0 - 0.08, px + 0.06, y1 + 0.08, fc="none", ec=GREY, lw="hair",
                       layer="S-POUT", z=3)
            # direction symbol + label
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            L = (y1 - y0) * 0.33
            v.line([(cx, cy - L), (cx, cy + L)], lw="med", color=ACCENT, layer="S-TEXT", z=6)
            for sg in (-1, 1):
                tip = (cx, cy + sg * L)
                v.poly([tip, (cx - 0.09, cy + sg * (L - 0.25)), (cx + 0.09, cy + sg * (L - 0.25))], fc=ACCENT,
                       ec=ACCENT, lw="hair", layer="S-TEXT", z=6)
            v.label_box(cx, cy, "Plancher 20+4", h=2.2, layer="S-TEXT")
            v.text(cx + 0.18, cy - 0.45, f"L = {y1 - y0 + 0.3:.2f}", h=1.9, ha="left", va="top", color=GREY,
                   layer="S-TEXT")
    # beam labels
    for y, nm in zip(M.YA, ["PP1", "PP2", "PP3"]):
        for i in range(3):
            xm = (M.XA[i] + M.XA[i + 1]) / 2
            v.text(xm, y + 0.2 if y < 8 else y - 0.2, f"{nm} (30×45)", h=2.1, ha="center",
                   va="bottom" if y < 8 else "top", weight="bold", color=ACCENT, layer="S-TEXT", z=8)
    for x, nm in zip(M.XA, ["PS1", "PS2", "PS3", "PS4"]):
        for j in range(2):
            ym = (M.YA[j] + M.YA[j + 1]) / 2
            v.text(x, ym, f"{nm} (30×35)", h=1.8, ha="center", va="center", rot=90,
                   weight="bold", color="#36506b", layer="S-TEXT", z=8)
    v.text(15.3, 8.3, "Acrotère BA 10×60 en rive", h=1.9, color=GREY, layer="S-TEXT")
    plan_axes(v, yr=(-2.6, 16.6))
    axis_dims(v)
    v.dim([-0.15, 15.15], 8.85, "h", ext_from=8.3)
    v.dim([-0.15, 8.15], 16.0, "v", ext_from=15.3, side=-1)
    S.view_title(60, 393, "PLAN DE COFFRAGE — PLANCHER HAUT RDC (TERRASSE)", "1:50")
    S.north_arrow(40, 360)
    rows = [["Poteaux P", "30 × 30", "12", "+3.24"],
            ["Poutres principales PP", "30 × 45", "9 travées", "+3.24"],
            ["Poutres secondaires PS", "30 × 35", "8 travées", "+3.24"],
            ["Plancher corps creux", "20 + 4", "≈ 115 m²", "+3.24"],
            ["Acrotère", "10 × 60", "46.6 ml", "+3.90"]]
    y = S.table(437, 392, [("Élément", 50, "left"), ("Section (cm)", 24), ("Qté", 20), ("Arase", 16)], rows,
                title="TABLEAU DES ÉLÉMENTS", h=2.0, row_h=5.4)
    y = S.notes(473, y - 10, "NOTES DE COFFRAGE", [
        "1. Poutrelles préfabriquées (ou coulées en",
        "   place) espacées de 65 cm, portée // Y,",
        "   appui ≥ 10 cm sur les poutres PP.",
        "2. Entrevous (hourdis) béton 20 × 20 × 53.",
        "3. Dalle de compression 4 cm armée TS Ø6",
        "   maille 20 × 20 (FeE520).",
        "4. Toutes les arases supérieures des",
        "   poutres = dessus dalle +3.24.",
        "5. Étaiement : 1 file d'étais à mi-portée",
        "   pour portées > 4.00 m, décoffrage ≥ 21 j.",
        "6. Prévoir les réservations EP Ø110 aux",
        "   4 angles avant bétonnage.",
    ], h=2.05)
    y = struct_notes(S, 473, y - 6)
    warning(S, 473, y - 4)


# =====================================================================================
# Reinforcement helpers
# =====================================================================================
def rc_section(v, b, h, top, bot, cover=0.03, st_d=0.008, title=None, S=None, slab=None, label_side=1,
               notes_top=None, notes_bot=None, stirrup_txt=None):
    """top/bot: list of layers, each (n, dia_m). Draws concrete, stirrups, bars and labels."""
    if slab:
        v.rect(-b / 2 - 0.15, h - slab, b / 2 + 0.15, h, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=2)
        v.break_line((-b / 2 - 0.15, h - slab - 0.03), (-b / 2 - 0.15, h + 0.03))
        v.break_line((b / 2 + 0.15, h - slab - 0.03), (b / 2 + 0.15, h + 0.03))
    v.rect(-b / 2, 0, b / 2, h, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    c = cover
    v.rect(-b / 2 + c, c, b / 2 - c, h - c, fc="none", ec=REBAR, lw="thin", layer="S-REBAR", z=6)
    # hook of stirrup
    v.line([(-b / 2 + c, h - c - 0.04), (-b / 2 + c + 0.04, h - c - 0.08)], lw="thin", color=REBAR, layer="S-REBAR",
           z=6)
    v.line([(-b / 2 + c + 0.04, h - c), (-b / 2 + c + 0.08, h - c - 0.04)], lw="thin", color=REBAR, layer="S-REBAR",
           z=6)

    def layer_pos(n, d, zc):
        x0 = -b / 2 + c + st_d + d / 2
        x1 = b / 2 - c - st_d - d / 2
        return [(x0 + (x1 - x0) * i / (n - 1), zc) for i in range(n)] if n > 1 else [(0, zc)]

    zc = c + st_d
    for k, (n, d) in enumerate(bot):
        zz = zc + d / 2 + k * (d + 0.025)
        for p in layer_pos(n, d, zz):
            v.dot(*p, d / 2)
    zc = h - c - st_d
    for k, (n, d) in enumerate(top):
        zz = zc - d / 2 - k * (d + 0.025)
        for p in layer_pos(n, d, zz):
            v.dot(*p, d / 2)
    # central tie (épingle)
    if bot and bot[0][0] >= 3:
        v.line([(0, c + 0.005), (0, h - c - 0.005)], lw="thin", color=REBAR, layer="S-REBAR", z=6)
    v.dim([-b / 2, b / 2], -0.06, "h", side=-1, h=1.9, fmt="{:.2f}")
    v.dim([0, h], -b / 2 - 0.07, "v", side=1, h=1.9)
    xl = b / 2 + 0.10
    if notes_top:
        v.leader([(b / 2 - c - 0.02, h - c - 0.02), (xl, h - 0.02), (xl + 0.08, h - 0.02)], notes_top, h=1.9)
    if notes_bot:
        v.leader([(b / 2 - c - 0.02, c + 0.02), (xl, 0.02), (xl + 0.08, 0.02)], notes_bot, h=1.9)
    if stirrup_txt:
        v.leader([(b / 2 - c, h / 2), (xl, h / 2), (xl + 0.08, h / 2)], stirrup_txt, h=1.9)


def col_section(v, a=0.30, c=0.03, d=0.012):
    v.rect(-a / 2, -a / 2, a / 2, a / 2, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    i = a / 2 - c
    v.rect(-i, -i, i, i, fc="none", ec=REBAR, lw="thin", layer="S-REBAR", z=6)
    j = i - 0.008 - d / 2
    v.poly([(0, j), (j, 0), (0, -j), (-j, 0)], fc="none", ec=REBAR, lw="thin", layer="S-REBAR", z=6)
    for px in (-j, 0, j):
        for pz in (-j, 0, j):
            if px == 0 and pz == 0:
                continue
            v.dot(px, pz, d / 2)
    v.dim([-a / 2, a / 2], -a / 2 - 0.05, "h", side=-1, h=1.9)
    v.dim([-a / 2, a / 2], -a / 2 - 0.05, "v", side=1, h=1.9)
    v.leader([(j, j), (a / 2 + 0.06, a / 2 + 0.04), (a / 2 + 0.10, a / 2 + 0.04)], "8 T12", h=2.0)
    v.leader([(i, -i * 0.3), (a / 2 + 0.06, -0.02), (a / 2 + 0.10, -0.02)], "Cadre T8", h=2.0)
    v.leader([(j / 2, -j / 2), (a / 2 + 0.06, -a / 2 + 0.02), (a / 2 + 0.10, -a / 2 + 0.02)], "Losange T8", h=2.0)


def footing_plan(v, a, sp=0.15, c=0.05):
    v.rect(-a / 2 - 0.10, -a / 2 - 0.10, a / 2 + 0.10, a / 2 + 0.10, fc="none", ec=GREY, lw="fine", ls="hidden",
           layer="S-SECT")
    v.rect(-a / 2, -a / 2, a / 2, a / 2, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    n = math.ceil((a - 2 * c) / sp - 1e-9)
    pos = [-a / 2 + c + i * (a - 2 * c) / n for i in range(n + 1)]
    for p in pos:
        v.line([(-a / 2 + c, p), (a / 2 - c, p)], lw="thin", color=REBAR, layer="S-REBAR", z=6)
        v.line([(p, -a / 2 + c), (p, a / 2 - c)], lw="thin", color=REBAR, layer="S-REBAR", z=6)
    v.rect(-0.15, -0.15, 0.15, 0.15, fc="#3a3a3a", ec=INK, lw="thin", layer="S-SECT", z=7)
    v.dim([-a / 2, a / 2], -a / 2 - 0.12, "h", side=-1, h=2.0)
    v.dim([-a / 2, a / 2], -a / 2 - 0.12, "v", side=1, h=2.0)
    v.text(0, a / 2 + 0.06, f"{n + 1} T12 e={(a - 2 * c) / n * 100:.0f} (×2 directions)", h=2.0, ha="center",
           layer="S-TEXT")
    return n + 1


def footing_section(v, a, hs, sp=0.15, c=0.05):
    v.rect(-a / 2 - 0.10, -0.10, a / 2 + 0.10, 0, fc="#f2f2f2", ec=INK, lw="thin", hatch="..", hcolor=GREY,
           layer="S-SECT", z=2)
    v.rect(-a / 2, 0, a / 2, hs, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, hs, 0.15, hs + 0.45, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.break_line((-0.22, hs + 0.45), (0.22, hs + 0.45))
    n = math.ceil((a - 2 * c) / sp - 1e-9)
    for i in range(n + 1):
        v.dot(-a / 2 + c + i * (a - 2 * c) / n, c + 0.018, 0.006)
    v.line([(-a / 2 + c, c + hs * 0.6), (-a / 2 + c, c), (a / 2 - c, c), (a / 2 - c, c + hs * 0.6)], lw="thick",
           color=REBAR, layer="S-REBAR", z=8)
    for xx in (-0.115, 0.115):
        sg = -1 if xx < 0 else 1
        v.line([(xx + sg * 0.25, c + 0.03), (xx, c + 0.03), (xx, hs + 0.45)], lw="thick", color=REBAR,
               layer="S-REBAR", z=8)
    for z in [hs - 0.05, hs + 0.10, hs + 0.25, hs + 0.40]:
        v.line([(-0.12, z), (0.12, z)], lw="thin", color=REBAR, layer="S-REBAR", z=8)
    v.dim([-a / 2, a / 2], -0.32, "h", side=-1, h=2.0)
    v.dim([0, hs], a / 2 + 0.12, "v", side=-1, h=2.0)
    v.dim([-0.10, 0], -a / 2 - 0.15, "v", side=1, h=1.8, labels=["0.10"])
    v.text(0, -0.12, "Béton de propreté ép. 10 cm", h=1.8, ha="center", va="top", color=GREY, layer="S-TEXT")


def sheet_rebar_foundations(S):
    # ---- column elevation 1:20 ----
    v = View(S, ox=100, oy=190, scale=20)
    a, hs, zt = 1.20, 0.40, M.Z_SEM_TOP_S1
    v.rect(-a / 2 - 0.1, M.Z_PROP, a / 2 + 0.1, M.Z_SEM_BOT, fc="#f2f2f2", ec=INK, lw="thin", hatch="..",
           hcolor=GREY, layer="S-SECT", z=2)
    v.rect(-a / 2, M.Z_SEM_BOT, a / 2, zt, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, zt, 0.15, M.Z_PP_SOF, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.55, M.Z_LONG_BOT, -0.15, M.Z_LONG_TOP, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3)
    v.rect(0.15, M.Z_LONG_BOT, 0.55, M.Z_LONG_TOP, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3)
    v.rect(-0.55, M.Z_PP_SOF, 0.55, M.Z_SLAB, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3)
    for xx in (-0.55, 0.55):
        v.break_line((xx, M.Z_LONG_BOT - 0.05), (xx, M.Z_LONG_TOP + 0.05))
        v.break_line((xx, M.Z_PP_SOF - 0.05), (xx, M.Z_SLAB + 0.05))
    v.line([(-0.9, M.Z_TN), (-0.55, M.Z_TN)], lw="thick", layer="S-SECT")
    v.line([(0.55, 0.0), (0.9, 0.0)], lw="fine", layer="S-SECT")
    c = 0.05
    v.line([(-a / 2 + c, M.Z_SEM_BOT + 0.25), (-a / 2 + c, M.Z_SEM_BOT + c), (a / 2 - c, M.Z_SEM_BOT + c),
            (a / 2 - c, M.Z_SEM_BOT + 0.25)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    for i in range(9):
        v.dot(-a / 2 + c + i * (a - 2 * c) / 8, M.Z_SEM_BOT + c + 0.018, 0.006)
    # longitudinal bars with feet and top anchorage
    for xx in (-0.115, 0.0, 0.115):
        sg = -1 if xx < 0 else 1
        foot = [(xx + sg * 0.30, M.Z_SEM_BOT + c + 0.03)] if xx != 0 else []
        top = [(xx, M.Z_SLAB - 0.04), (xx - sg * 0.25 if xx else xx, M.Z_SLAB - 0.04)] if xx else [(xx, M.Z_SLAB - 0.04)]
        v.line(foot + [(xx, M.Z_SEM_BOT + c + 0.03)] + top, lw="thick", color=REBAR, layer="S-REBAR", z=8)
    # stirrups : zone nodale e=10 (60 cm) near both ends, courante e=15
    zb, ztop_c = M.Z_LONG_TOP, M.Z_PP_SOF
    zs = []
    z = zb + 0.05
    while z < zb + 0.60:
        zs.append(z)
        z += 0.10
    z = zs[-1] + 0.15
    while z < ztop_c - 0.60:
        zs.append(z)
        z += 0.15
    z = ztop_c - 0.60
    while z < M.Z_SLAB - 0.05:
        zs.append(z)
        z += 0.10
    z = zt + 0.05
    while z < zb:
        zs.append(z)
        z += 0.15
    for z in zs:
        v.line([(-0.12, z), (0.12, z)], lw="thin", color=REBAR, layer="S-REBAR", z=8)
    # dims & labels
    v.dim([zt, M.Z_LONG_TOP, M.Z_LONG_TOP + 0.60, M.Z_PP_SOF - 0.60, M.Z_PP_SOF, M.Z_SLAB], 0.45, "v", side=-1, h=1.9,
          labels=["0.65", "0.60", f"{(M.Z_PP_SOF - 0.60) - (M.Z_LONG_TOP + 0.60):.2f}", "0.60", "0.45"])
    v.text(0.62, M.Z_LONG_TOP + 0.30, "Zone nodale\nCad. T8 e=10", h=1.9, va="center", layer="S-TEXT")
    v.text(0.62, 1.30, "Zone courante\nCad. T8 e=15", h=1.9, va="center", layer="S-TEXT")
    v.text(0.62, M.Z_PP_SOF - 0.30, "Zone nodale\nCad. T8 e=10", h=1.9, va="center", layer="S-TEXT")
    v.leader([(0.0, 0.8), (-0.45, 1.0), (-0.55, 1.0)], "8 T12", h=2.1, ha="right")
    v.leader([(0.12, M.Z_SLAB - 0.04), (-0.35, M.Z_SLAB + 0.25), (-0.45, M.Z_SLAB + 0.25)], "Ancrage 40Ø", h=1.9,
             ha="right")
    v.leader([(-0.40, M.Z_SEM_BOT + 0.08), (-0.75, -1.85), (-0.85, -1.85)], "Retours 30 cm", h=1.9, ha="right")
    for z, t in [(M.Z_SLAB, "+3.24"), (M.Z_PP_SOF, "+2.79"), (0.0, "±0.00"),
                 (zt, "-1.10"), (M.Z_SEM_BOT, "-1.50")]:
        v.level(-0.62, z, t, side=-1, length_mm=12, h=1.9)
    v.text(0, M.Z_SLAB + 0.12, "PP 30×45", h=1.9, ha="center", layer="S-TEXT")
    v.text(-0.35, M.Z_LONG_BOT - 0.03, "L 30×40", h=1.9, ha="center", va="top", layer="S-TEXT")
    S.view_title(32, 393, "POTEAU P 30×30 — ÉLÉVATION", "1:20", h=3.4)
    # cut mark 1-1
    v.line([(-0.25, 1.6), (-0.17, 1.6)], lw="xthick", color=ACCENT)
    v.line([(0.17, 1.6), (0.25, 1.6)], lw="xthick", color=ACCENT)
    v.text(-0.27, 1.6, "1", h=2.6, ha="right", va="center", weight="bold", color=ACCENT)
    v.text(0.27, 1.6, "1", h=2.6, ha="left", va="center", weight="bold", color=ACCENT)

    # ---- column section 1:5 ----
    vs = View(S, ox=200, oy=330, scale=5)
    col_section(vs)
    S.view_title(165, 393, "COUPE 1-1 POTEAU", "1:5", h=3.4)

    # ---- tie beam section 1:5 ----
    vl = View(S, ox=200, oy=150, scale=5)
    rc_section(vl, 0.30, 0.40, [(3, 0.014)], [(3, 0.014)], cover=0.03, notes_top="3 T14", notes_bot="3 T14",
               stirrup_txt="Cad. T8 e=20 + épingle")
    S.view_title(165, 255, "LONGRINE L 30×40", "1:5", h=3.4)

    # ---- footings 1:20 ----
    for (xo, name) in [(325, "S1"), (420, "S2")]:
        a, hs = M.FOOTINGS[name]
        vp = View(S, ox=xo, oy=335, scale=20)
        footing_plan(vp, a)
        S.view_title(xo - 35, 393, f"SEMELLE {name} — VUE EN PLAN", "1:20", h=3.2)
        vc = View(S, ox=xo, oy=170, scale=20)
        footing_section(vc, a, hs)
        S.view_title(xo - 35, 268, f"SEMELLE {name} — COUPE", "1:20", h=3.2)
        if name == "S2":
            a3, h3 = M.FOOTINGS["S3"]
            S.text(xo - 35, 110, f"Semelle S3 (angles) : {a3:.2f} × {a3:.2f} × {h3:.2f} m, 7 T12 e=15 (×2 dir.),",
                   h=2.1, color=GREY)
            S.text(xo - 35, 106, "disposition identique à S2.", h=2.1, color=GREY)

    rows = [["1", "Semelle S1", "T12", "9+9 / u", "1.40", "2"],
            ["2", "Semelles S2 / S3", "T12", "8+8 / 7+7", "1.30 / 1.20", "6 / 4"],
            ["3", "Poteau (long.)", "T12", "8 / u", "5.60", "12"],
            ["4", "Poteau (cadre+los.)", "T8", "≈ 36 / u", "1.10+0.85", "12"],
            ["5", "Longrine (long.)", "T14", "6 / travée", "5.70", "17"],
            ["6", "Longrine (cadres)", "T8", "≈ 24 / trav.", "1.30", "17"]]
    y = S.table(473, 393, [("N°", 7), ("Élément", 36, "left"), ("Ø", 10), ("Nb barres", 22), ("L (m)", 18),
                                ("Nb él.", 13)], rows, title="NOMENCLATURE DES ACIERS (indicative)", h=1.9,
                row_h=5.2)
    y = struct_notes(S, 473, y - 10, extra=(
        "Recouvrements : 40Ø en zone IIa (RPA).",
        "Crochets à 135° sur cadres, retour 10Ø.",
    ))
    warning(S, 473, y - 4)


# =====================================================================================
# 10 - Beams & slab reinforcement
# =====================================================================================
def beam_elev(v, H, bars, cuts, label, en=0.10):
    """Elevation of an end span (axis 1 -> axis 2) + start of next span with break line. h = x."""
    Lr = 6.00
    v.rect(-0.15, 0, Lr, H, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(-0.15, -0.60, 0.15, 0, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3)
    v.rect(4.85, -0.60, 5.15, 0, fc=CONC, ec=INK, lw="thin", layer="S-SECT", z=3)
    for x0 in (-0.15, 4.85):
        v.break_line((x0 - 0.05, -0.60), (x0 + 0.35, -0.60))
    v.break_line((Lr, -0.05), (Lr, H + 0.05))
    c = 0.035
    # bottom bars
    bt, b2, tp, ch = bars["bot"], bars.get("bot2"), bars["top"], bars["chap"]
    v.line([(-0.12, c + 0.25), (-0.12, c), (Lr, c)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    if b2:
        v.line([(0.50, c + 0.035), (4.50, c + 0.035)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    v.line([(-0.12, H - c - 0.25), (-0.12, H - c), (Lr, H - c)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    v.line([(-0.10, H - c - 0.20), (-0.10, H - c - 0.035), (1.25, H - c - 0.035)], lw="thick", color=REBAR,
           layer="S-REBAR", z=8)
    v.line([(5 - 1.5, H - c - 0.035), (Lr, H - c - 0.035)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    # stirrups
    xs = []
    for a, b in [(0.15, 4.85), (5.15, Lr)]:
        x = a + 0.05
        while x < min(a + 2 * H, b):
            xs.append(x)
            x += en
        x = xs[-1] + 0.15
        while x < b - 2 * H and x < b:
            xs.append(x)
            x += 0.15
        if b < Lr:
            x = b - 2 * H
            while x < b - 0.02:
                xs.append(x)
                x += en
    for x in xs:
        v.line([(x, c - 0.01), (x, H - c + 0.01)], lw="fine", color=REBAR, layer="S-REBAR", z=7)
    # labels (circled numbers)
    lab = [(1.6, c, "①", bt), (3.7, c + 0.035, "②", b2), (2.9, H - c, "③", tp), (0.6, H - c - 0.035, "④", ch),
           (4.2, H - c - 0.035, "④", ch)]
    for x, z, n, txt in lab:
        if not txt:
            continue
        up = z > H / 2
        zz = H + 0.20 if up else -0.22
        v.line([(x, z), (x + 0.25, zz)], lw="hair", layer="S-TEXT")
        v.text(x + 0.27, zz, f"{n} {txt}", h=2.0, va="center", layer="S-TEXT")
    v.dim([0, 5], -0.75, "h", side=-1, h=2.0)
    v.dim([0.15, 0.15 + 2 * H, 4.85 - 2 * H, 4.85], H + 0.55, "h", h=1.9,
          labels=[f"{2 * H:.2f}", f"{4.7 - 4 * H:.2f}", f"{2 * H:.2f}"])
    v.dim([3.5, 5.0], H + 0.95, "h", h=1.9, color=GREY)
    v.text(5.1, H + 0.99, "(chapeau 3.00 m, symétrique / axe 2)", h=1.8, color=GREY, layer="S-TEXT")
    v.dim([-0.15, 1.25], H + 0.95, "h", h=1.9, color=GREY)
    v.dim([0, H], -0.5, "v", side=1, h=1.9)
    for x, lab_ in zip([0, 5], ["A", "B"] if label == "PS" else ["1", "2"]):
        v.axis((x, -0.98), (x, -0.62), lab_, ends=(True, False), r_mm=3.5)
    for x, n in cuts:
        for z0, z1 in ((-0.12, -0.02), (H + 0.02, H + 0.12)):
            v.line([(x, z0), (x, z1)], lw="xthick", color=ACCENT)
        v.text(x + 0.05, H + 0.10, n, h=2.4, weight="bold", color=ACCENT)
    v.text(0.35, -0.30, f"Zone nodale : cad.+étr. T8 e={en * 100:.0f} sur 2h\nZone courante : e=15", h=1.8, ha="left",
           va="top", color=GREY, layer="S-TEXT")


def slab_detail(v):
    """Section through hollow-block slab 20+4 (1:10). Width shown 1.30 m (2 bays)."""
    W = 1.30
    v.rect(0, 0.20, W, 0.24, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    for i in range(3):
        px = 0.0 + 0.65 * i
        # poutrelle (inverted T) : talon 12 x 4 + âme
        v.poly([(px - 0.06, 0), (px + 0.06, 0), (px + 0.06, 0.04), (px + 0.04, 0.05), (px + 0.04, 0.20),
                (px - 0.04, 0.20), (px - 0.04, 0.05), (px - 0.06, 0.04)], fc=CONC, ec=INK, lw="thick",
               layer="S-SECT", z=3)
        v.dot(px - 0.03, 0.025, 0.006)
        v.dot(px + 0.03, 0.025, 0.006)
        v.dot(px, 0.17, 0.005)
        v.line([(px - 0.03, 0.025), (px, 0.17), (px + 0.03, 0.025)], lw="fine", color=REBAR, layer="S-REBAR", z=8)
    for i in range(2):
        x0 = 0.065 + 0.65 * i
        x1 = x0 + 0.52
        v.rect(x0, 0.0, x1, 0.20, fc="#f3eee6", ec=INK, lw="thin", layer="S-SECT", z=2.5)
        for k in range(3):
            xa = x0 + 0.03 + k * 0.165
            v.rect(xa, 0.03, xa + 0.135, 0.17, fc="white", ec=INK, lw="fine", layer="S-SECT", z=2.6)
    v.line([(0, 0.22), (W, 0.22)], lw="thin", color=REBAR, layer="S-REBAR", z=8)
    for k in range(7):
        v.dot(0.05 + 0.20 * k, 0.215, 0.003)
    v.break_line((-0.03, -0.03), (-0.03, 0.27))
    v.break_line((W + 0.03, -0.03), (W + 0.03, 0.27))
    v.line([(0, -0.02), (W, -0.02)], lw="fine", color=GREY, layer="S-SECT")
    v.dim([0, 0.65, 1.30], -0.08, "h", side=-1, h=2.0)
    v.dim([0, 0.20, 0.24], W + 0.10, "v", side=-1, h=2.0)
    v.leader([(0.9, 0.22), (1.0, 0.36), (1.06, 0.36)], "Dalle de compression 4 cm + TS Ø6 maille 20×20", h=1.9)
    v.leader([(0.33, 0.10), (0.33, 0.33), (0.39, 0.33)], "Entrevous (hourdis) 20×20×53", h=1.9)
    v.leader([(0.65, 0.04), (0.45, -0.20), (0.39, -0.20)],
             "Poutrelle : 2T12 inf. + 1T10 sup. + étriers Ø6 e=15 ; chapeau 2T12 sur appui B",
             h=1.9, ha="right")
    v.text(0, -0.02, "Enduit plâtre 2 cm", h=1.8, va="top", color=GREY, layer="S-TEXT")


def acrotere_detail(v):
    v.rect(-0.40, 0, 0.10, 0.24, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(0, -0.21, 0.10 + 0.20, 0.24, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(0.20, 0.24, 0.30, 0.90, fc=CONC, ec=INK, lw="thick", layer="S-SECT", z=3)
    v.rect(0.16, 0.84, 0.34, 0.90, fc="#d0d0d0", ec=INK, lw="thin", layer="S-SECT", z=4)
    v.break_line((-0.40, -0.02), (-0.40, 0.26))
    v.break_line((-0.02 + 0.0, -0.21), (0.32, -0.21))
    # terrace layers
    v.poly([(-0.40, 0.24), (0.20, 0.24), (0.20, 0.32), (-0.40, 0.34)], fc="#ededed", ec=INK, lw="fine",
           layer="S-SECT", z=3)
    v.poly([(-0.40, 0.34), (0.20, 0.32), (0.20, 0.37), (-0.40, 0.39)], fc="#9e9e9e", ec=INK, lw="fine",
           layer="S-SECT", z=3)
    v.rect(0.18, 0.32, 0.20, 0.55, fc="#6e6e6e", ec="none", layer="S-SECT", z=4)
    # rebars
    v.line([(0.23, 0.05), (0.23, 0.86), (0.27, 0.86), (0.27, 0.05)], lw="thick", color=REBAR, layer="S-REBAR", z=8)
    for z in (0.40, 0.55, 0.70, 0.83):
        v.dot(0.235 + 0.0, z, 0.004)
        v.dot(0.265, z, 0.004)
    v.dim([0.20, 0.30], 0.98, "h", h=1.9)
    v.dim([0.24, 0.90], 0.42, "v", side=-1, h=1.9)
    v.leader([(0.27, 0.65), (0.45, 0.72), (0.50, 0.72)], "T8 e=20 (cadre en U)", h=1.9)
    v.leader([(0.265, 0.55), (0.45, 0.56), (0.50, 0.56)], "4+4 T8 filants", h=1.9)
    v.leader([(0.19, 0.50), (-0.05, 0.50), (-0.10, 0.50)], "Relevé d'étanchéité", h=1.9, ha="right")
    v.leader([(0.25, 0.88), (0.05, 0.98), (0.0, 0.98)], "Couvertine", h=1.9, ha="right")
    v.text(0.15, -0.05, "PP 30×45", h=1.9, ha="center", va="top", layer="S-TEXT")


def sheet_rebar_beams(S):
    v1 = View(S, ox=55, oy=330, scale=25)
    beam_elev(v1, M.PP_H, dict(bot="3T16 filants", bot2="3T16 renfort L=4.00", top="3T14 filants",
                               chap="3T14 chapeaux"), [(1.0, "1"), (2.5, "2")], "PP")
    S.view_title(32, 393, "POUTRE PRINCIPALE PP (30×45) — TRAVÉE DE RIVE", "1:25", h=3.4)
    for i, (xo, nm, top, bot) in enumerate([(345, "1-1 (appui)", [(3, 0.014), (3, 0.014)], [(3, 0.016)]),
                                             (415, "2-2 (travée)", [(3, 0.014)], [(3, 0.016), (3, 0.016)])]):
        vs = View(S, ox=xo, oy=320, scale=10)
        rc_section(vs, 0.30, 0.45, top, bot, slab=0.24)
        S.text(xo, 382, f"COUPE {nm}", h=2.8, weight="bold", color=ACCENT, ha="center")
        S.text(xo, 377, "Éch. 1:10", h=2.0, color=GREY, ha="center")
    v2 = View(S, ox=55, oy=210, scale=25)
    beam_elev(v2, M.PS_H, dict(bot="3T14 filants", bot2=None, top="3T12 filants", chap="2T12 chapeaux"),
              [(1.0, "3"), (2.5, "4")], "PS", en=0.08)
    S.view_title(32, 275, "POUTRE SECONDAIRE PS (30×35) — TRAVÉE DE RIVE", "1:25", h=3.4)
    for i, (xo, nm, top, bot) in enumerate([(345, "3-3 (appui)", [(3, 0.012), (2, 0.012)], [(3, 0.014)]),
                                             (415, "4-4 (travée)", [(3, 0.012)], [(3, 0.014)])]):
        vs = View(S, ox=xo, oy=205, scale=10)
        rc_section(vs, 0.30, 0.35, top, bot, slab=0.24)
        S.text(xo, 258, f"COUPE {nm}", h=2.8, weight="bold", color=ACCENT, ha="center")
        S.text(xo, 253, "Éch. 1:10", h=2.0, color=GREY, ha="center")
    v3 = View(S, ox=60, oy=105, scale=10)
    slab_detail(v3)
    S.view_title(32, 160, "COUPE SUR PLANCHER CORPS CREUX 20+4", "1:10", h=3.4)
    v4 = View(S, ox=300, oy=95, scale=10)
    acrotere_detail(v4)
    S.view_title(262, 160, "DÉTAIL ACROTÈRE", "1:10", h=3.4)

    rows = [["PP", "30×45", "3T16 + 3T16", "3T14 + 3T14 ch.", "T8 e=10/15"],
            ["PS", "30×35", "3T14", "3T12 + 2T12 ch.", "T8 e=8/15"],
            ["Poutrelle", "12×20", "2T12", "1T10 + ch. 2T12", "Ø6 e=15"],
            ["Dalle comp.", "ép. 4", "TS Ø6 20×20", "—", "—"],
            ["Acrotère", "10×60", "4+4 T8", "—", "T8 e=20"]]
    y = S.table(473, 393, [("Élément", 18, "left"), ("b×h", 13), ("Inférieur", 25), ("Supérieur", 28),
                           ("Transv.", 20)], rows, title="RÉCAPITULATIF DES ARMATURES", h=1.85, row_h=5.2)
    import calc as C
    B = C.PP["axes"]["B"]
    y = S.notes(473, y - 10, "PRINCIPE DE CALCUL (PP axe B)", [
        f"p_u = {B['pu']:.1f} kN/m (réactions des poutrelles + p.p.)",
        f"Méthode forfaitaire : M0 = {B['M0']:.1f} kN·m",
        f"M travée de rive = {B['Mt_rive']:.1f} kN·m → A = {C.PP['ft']['As']:.2f} cm²",
        f"M appui = {B['Ma_int']:.1f} kN·m → A = {C.PP['fa']['As']:.2f} cm²",
        f"Prévu : 6T16 = {C.PP['A_bot']:.2f} cm² / 6T14 = {C.PP['A_top_sup']:.2f} cm²",
        "Détail complet : Note de calcul, § 6.",
    ], h=2.05)
    y = struct_notes(S, 473, y - 6)
    warning(S, 473, y - 4)
