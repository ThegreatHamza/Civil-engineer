"""Cover sheet: project identity, drawing index, key plan, general notes."""
import model as M
from drawing import ACCENT, GREY, INK, POCHE, View


def sheet_cover(S):
    import build
    S.rect(32, 300, 400, 398, fc="#f2f5f8", ec="none")
    S.rect(32, 300, 36, 398, fc=ACCENT, ec="none")
    S.text(46, 380, "DOSSIER DE PLANS", h=6, color=GREY, weight="bold")
    S.text(46, 360, "HABITATION INDIVIDUELLE EN R.D.C", h=11, weight="bold", color=ACCENT)
    S.text(46, 343, "3 chambres · salon · cuisine · WC · hall d'entrée", h=5)
    S.text(46, 327, "Emprise 15.00 × 8.00 m (entre axes)  —  Surface bâtie 126.99 m²  —  Hauteur 3.90 m",
           h=3.6, color=GREY)
    S.text(46, 312, "Architecture  ·  Structure (génie civil)  ·  Plans d'exécution", h=3.6, color=GREY)

    # key plan at 1:150
    v = View(S, ox=95, oy=130, scale=75)
    walls = M.walls_cut()
    v.geom(walls, fc=POCHE, ec=INK, lw="thin", dxf=False)
    v.geom(M.columns_geom(), fc=INK, ec=INK, lw="fine", dxf=False)
    for name, poly, (lx, ly), _ in M.ROOMS:
        c = poly.representative_point() if name == "HALL" else poly.centroid
        x, y = (11.5, 3.3) if name == "HALL" else (c.x, c.y)
        v.text(x, y, name.replace("CHAMBRE", "CH."), h=2.2, ha="center", va="center", weight="bold", dxf=False)
    v.dim([0, 3, 5, 7, 9, 10, 15], -0.9, "h", side=-1, h=2.0)
    v.dim([0, 15], -2.0, "h", side=-1, h=2.0)
    v.dim([0, 5, 8], -0.9, "v", h=2.0)
    v.dim([0, 8], -2.0, "v", h=2.0)
    v.text(16.0, 3.0, "◄ ENTRÉE", h=2.6, va="center", weight="bold", color=ACCENT, dxf=False)
    S.view_title(46, 280, "PLAN DE REPÉRAGE", "1:75", h=3.6)
    S.north_arrow(370, 255, r=8)

    rows = []
    for i, (slug, title, lot, scale, _) in enumerate(build.SHEETS):
        rows.append([f"{i:02d}", title, lot, scale, "A2", "A"])
    y = S.table(430, 398, [("N°", 10), ("Désignation", 70, "left"), ("Lot", 30), ("Échelle", 16), ("Fmt", 9),
                           ("Ind.", 9)], rows, title="SOMMAIRE DES PLANCHES", h=1.95, row_h=6.0)
    S.notes(430, y - 12, "NOTES GÉNÉRALES", [
        "1. Toutes les cotes sont en mètres, les",
        "   niveaux en mètres par rapport au ±0.00",
        "   (sol fini RDC = TN + 0.45).",
        "2. Les cotes 15.00 × 8.00 m du croquis sont",
        "   prises entre axes de poteaux.",
        "3. Ne pas mesurer sur les plans : seules les",
        "   cotes écrites font foi.",
        "4. L'entreprise doit vérifier toutes les",
        "   cotes sur site avant exécution.",
        "5. Les plans de structure constituent un",
        "   prédimensionnement (BAEL 91 / RPA 99",
        "   v2003) à valider par un ingénieur agréé",
        "   après étude géotechnique.",
        "6. Fichiers DXF fournis (unités : mètres)",
        "   pour reprise sous AutoCAD.",
        "7. Note de calcul de la structure jointe :",
        "   Note_de_calcul_structure.pdf.",
    ], h=2.1)
