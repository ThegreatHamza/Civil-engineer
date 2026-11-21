"""Excel deliverables: Devis quantitatif & estimatif (avant-métré + DQE + récapitulatif) and Planning (Gantt).

python3 generator/excel.py  ->  plans/Devis_quantitatif_estimatif.xlsx, plans/Planning_travaux.xlsx
Quantities come from the drawings (plans/). Unit prices are indicative (DA, 2026) and editable (blue cells).
"""
import datetime as dt
import os

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(__file__), "..", "plans")
F = "Arial"
NAVY = "1F3B57"
BLUE_IN = Font(name=F, size=10, color="0000FF")
GREEN = Font(name=F, size=10, color="008000")
BLACK = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
WHITE_B = Font(name=F, size=10, bold=True, color="FFFFFF")
TITLE = Font(name=F, size=14, bold=True, color=NAVY)
SUB = Font(name=F, size=10, italic=True, color="595959")
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
LOT_FILL = PatternFill("solid", fgColor="DCE6F0")
ITEM_FILL = PatternFill("solid", fgColor="F3F6F9")
TOT_FILL = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="A6A6A6")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM = '#,##0.00;-#,##0.00;"-"'
MONEY = '#,##0" DA";-#,##0" DA";"-"'
MONEY0 = '#,##0;-#,##0;"-"'

PROJECT = "Construction d'une habitation individuelle en R.D.C — 15.00 × 8.00 m (entre axes)"

# ------------------------------------------------------------------------------------------------
# Bill of quantities data: (code, designation, unit, price DA, [sub-lines]) ; lot rows: ("LOT", title)
# sub-line = (label, Nb, L, l, H) ; a value "@x.y" links to the quantity of item x.y ; "@a+@b" sums.
# ------------------------------------------------------------------------------------------------
EXT_OPEN = [("À déduire : F1 1.20×1.20", -4, None, 1.20, 1.20), ("À déduire : F2 1.40×1.20", -2, None, 1.40, 1.20),
            ("À déduire : F3 1.00×1.20", -2, None, 1.00, 1.20), ("À déduire : F4 0.60×0.60", -1, None, 0.60, 0.60),
            ("À déduire : P1 1.20×2.20", -1, None, 1.20, 2.20)]
INT_DOORS = [("À déduire : P2 0.90×2.20", -3, None, 0.90, 2.20), ("À déduire : P3 0.80×2.20", -1, None, 0.80, 2.20),
             ("À déduire : P4 0.70×2.20", -1, None, 0.70, 2.20), ("À déduire : P5 1.40×2.20", -1, None, 1.40, 2.20)]

ITEMS = [
    ("LOT", "LOT 00 — INSTALLATION DE CHANTIER"),
    ("0.1", "Installation, clôture, baraque de chantier, branchements provisoires et repli", "Ft", 150000,
     [("Forfait", 1, None, None, None)]),
    ("LOT", "LOT 01 — TERRASSEMENTS"),
    ("1.1", "Décapage de la terre végétale sur 20 cm", "m²", 150,
     [("Emprise hors-tout + 1.00 m en périphérie", 1, 17.30, 10.30, None)]),
    ("1.2", "Fouilles en puits pour semelles isolées (fond à -1.60, soit 1.15 m sous TN)", "m³", 1300,
     [("Semelles S1 (1.20 + 2×0.10)²", 2, 1.40, 1.40, 1.15), ("Semelles S2 (1.00 + 2×0.10)²", 10, 1.20, 1.20, 1.15)]),
    ("1.3", "Fouilles en tranchée pour longrines", "m³", 1300,
     [("Longrines, longueur nette entre semelles", 1, 59.20, 0.50, 0.20)]),
    ("1.4", "Remblai compacté par couches de 20 cm", "m³", 800,
     [("Volume des fouilles", 1, "@1.2+@1.3", None, None), ("À déduire : béton de propreté", -1, "@2.1", None, None),
      ("À déduire : semelles", -1, "@2.2", None, None), ("À déduire : amorces de poteaux", -1, "@2.3", None, None),
      ("Remblai intérieur sous hérisson (TN → -0.35)", 1, 14.70, 7.70, 0.10)]),
    ("1.5", "Évacuation des terres excédentaires à la décharge (foisonnement 1.25)", "m³", 600,
     [("Déblais × 1.25", 1.25, "@1.2+@1.3", None, None), ("Terre végétale décapée", 1, "@1.1", None, 0.20),
      ("À déduire : terres réutilisées en remblai", -1, "@1.4", None, None)]),
    ("LOT", "LOT 02 — INFRASTRUCTURE (BÉTON ARMÉ)"),
    ("2.1", "Béton de propreté dosé à 150 kg/m³, ép. 10 cm", "m³", 12000,
     [("Sous semelles S1", 2, 1.40, 1.40, 0.10), ("Sous semelles S2", 10, 1.20, 1.20, 0.10),
      ("Sous longrines", 1, 59.20, 0.40, 0.10)]),
    ("2.2", "Béton armé C25 pour semelles isolées (coffrage compris, hors acier)", "m³", 28000,
     [("S1 1.20 × 1.20 × 0.40", 2, 1.20, 1.20, 0.40), ("S2 1.00 × 1.00 × 0.35", 10, 1.00, 1.00, 0.35)]),
    ("2.3", "Béton armé C25 pour amorces de poteaux 30 × 30", "m³", 35000,
     [("Sur S1 (-1.10 → -0.45)", 2, 0.30, 0.30, 0.65), ("Sur S2 (-1.15 → -0.45)", 10, 0.30, 0.30, 0.70)]),
    ("2.4", "Béton armé C25 pour longrines 30 × 40", "m³", 32000,
     [("Longrines, longueur nette", 1, 59.20, 0.30, 0.40)]),
    ("2.5", "Acier HA FeE400 façonné et posé — infrastructure", "kg", 230,
     [("Semelles : ratio 70 kg/m³", 70, "@2.2", None, None), ("Amorces : ratio 130 kg/m³", 130, "@2.3", None, None),
      ("Longrines : ratio 110 kg/m³", 110, "@2.4", None, None)]),
    ("2.6", "Hérisson en pierres sèches, ép. 20 cm", "m²", 900,
     [("Surface intérieure entre murs", 1, 14.70, 7.70, None)]),
    ("2.7", "Film polyane anti-remontées", "m²", 150, [("Surface du dallage", 1, "@2.6", None, None)]),
    ("2.8", "Dallage en béton armé ép. 10 cm, treillis soudé Ø6 maille 20 × 20", "m²", 2800,
     [("Surface intérieure", 1, "@2.6", None, None)]),
    ("LOT", "LOT 03 — SUPERSTRUCTURE (BÉTON ARMÉ)"),
    ("3.1", "Béton armé C25 pour poteaux 30 × 30 (coffrage compris)", "m³", 38000,
     [("Poteaux (-0.05 → +2.79)", 12, 0.30, 0.30, 2.84)]),
    ("3.2", "Béton armé C25 pour poutres principales PP 30 × 45", "m³", 38000,
     [("Axes A, B, C : 15.30 − 4 × 0.30", 3, 14.10, 0.30, 0.45)]),
    ("3.3", "Béton armé C25 pour poutres secondaires PS 30 × 35", "m³", 38000,
     [("Axes 1 à 4 : 8.30 − 3 × 0.30", 4, 7.40, 0.30, 0.35)]),
    ("3.4", "Plancher à corps creux 20 + 4 (poutrelles, hourdis, dalle de compression + TS, étaiement)", "m²", 6500,
     [("Panneaux 4.70 × 4.70", 3, 4.70, 4.70, None), ("Panneaux 4.70 × 2.70", 3, 4.70, 2.70, None)]),
    ("3.5", "Béton armé C25 pour linteaux (appui 20 cm de chaque côté)", "m³", 35000,
     [("Linteaux extérieurs Σ(l + 0.40)", 1, 15.40, 0.30, 0.20), ("Linteaux intérieurs Σ(l + 0.40)", 1, 8.00, 0.10, 0.20)]),
    ("3.6", "Béton armé C25 pour acrotère 10 × 60", "m³", 40000,
     [("Périmètre à l'axe de l'acrotère", 1, 46.80, 0.10, 0.60)]),
    ("3.7", "Acier HA FeE400 façonné et posé — superstructure", "kg", 230,
     [("Poteaux : ratio 140 kg/m³", 140, "@3.1", None, None), ("Poutres PP : ratio 125 kg/m³", 125, "@3.2", None, None),
      ("Poutres PS : ratio 110 kg/m³", 110, "@3.3", None, None), ("Linteaux : ratio 80 kg/m³", 80, "@3.5", None, None),
      ("Acrotère : ratio 70 kg/m³", 70, "@3.6", None, None)]),
    ("LOT", "LOT 04 — MAÇONNERIE"),
    ("4.1", "Double cloison extérieure en brique creuse 15 + 10 avec lame d'air 5 cm", "m²", 3200,
     [("Façades Nord et Sud (sous PP)", 2, 14.10, None, 2.84), ("Façades Est et Ouest (sous PS)", 2, 7.40, None, 2.94),
      *EXT_OPEN, ("À déduire : linteaux extérieurs", -1, 15.40, None, 0.20)]),
    ("4.2", "Cloison intérieure en brique creuse de 10 cm", "m²", 1600,
     [("Mur entre chambres et hall (axe B)", 1, 14.10, None, 2.84), ("Murs entre chambres (axes 2 et 3)", 2, 2.70, None, 2.94),
      ("Mur du salon", 1, 4.80, None, 3.05), ("Murs cuisine / WC", 1, 9.50, None, 3.05),
      *INT_DOORS, ("À déduire : linteaux intérieurs", -1, 8.00, None, 0.20)]),
    ("LOT", "LOT 05 — ENDUITS ET REVÊTEMENTS"),
    ("5.1", "Enduit extérieur au mortier de ciment, 3 couches, finition grattée", "m²", 900,
     [("Périmètre hors-tout × (+0.15 → +3.90)", 1, 47.20, None, 3.75), *EXT_OPEN]),
    ("5.2", "Placage en pierre naturelle du soubassement, h = 0.60 m", "m²", 4500,
     [("Périmètre hors-tout", 1, 47.20, None, 0.60), ("À déduire : perron d'entrée", -1, 2.00, None, 0.45)]),
    ("5.3", "Enduit plâtre sur murs intérieurs", "m²", 700,
     [("Périmètre des locaux × hauteur sous plafond", 1, 113.00, None, 3.00), *EXT_OPEN,
      *[(lab, 2 * nb, L, l, h) for lab, nb, L, l, h in INT_DOORS],
      ("À déduire : surfaces en faïence", -1, "@5.6", None, None)]),
    ("5.4", "Enduit plâtre sous plafond", "m²", 800, [("Surface habitable (planche 01)", 1, 109.62, None, None)]),
    ("5.5", "Carrelage grès cérame 45 × 45 sur chape, y compris mortier de pose", "m²", 3500,
     [("Chambres, salon, hall", 1, 99.18, None, None)]),
    ("5.6", "Faïence murale 25 × 40", "m²", 3000,
     [("Cuisine, h = 1.60 m", 1, 11.40, None, 1.60), ("WC, h = 2.00 m", 1, 7.40, None, 2.00),
      ("À déduire : porte P3", -1, None, 0.80, 1.60), ("À déduire : porte P4", -1, None, 0.70, 2.00),
      ("À déduire : fenêtre F3 cuisine (partie basse)", -1, None, 1.00, 0.60)]),
    ("5.7", "Carrelage antidérapant 30 × 30 (cuisine et WC)", "m²", 3200,
     [("Cuisine 7.02 + WC 3.42", 1, 10.44, None, None)]),
    ("5.8", "Plinthes assorties au carrelage, h = 10 cm", "ml", 600,
     [("Périmètre des locaux carrelés grès", 1, 94.20, None, None), ("À déduire : seuils de portes", -1, 10.90, None, None)]),
    ("LOT", "LOT 06 — ÉTANCHÉITÉ ET TOITURE"),
    ("6.1", "Forme de pente en béton maigre (2 %), ép. moyenne 8 cm", "m²", 1200,
     [("Surface intérieure de l'acrotère", 1, 15.10, 8.10, None)]),
    ("6.2", "Pare-vapeur + isolation thermique 4 cm", "m²", 900, [("Surface de la terrasse", 1, "@6.1", None, None)]),
    ("6.3", "Étanchéité multicouche (3 feutres bitumés + enduits à chaud)", "m²", 2200,
     [("Surface de la terrasse", 1, "@6.1", None, None)]),
    ("6.4", "Protection lourde en gravillons roulés, ép. 5 cm", "m²", 400, [("Surface de la terrasse", 1, "@6.1", None, None)]),
    ("6.5", "Relevés d'étanchéité h ≥ 15 cm avec engravure et bande solin", "ml", 1200,
     [("Périmètre intérieur de l'acrotère", 1, 46.40, None, None)]),
    ("6.6", "Descentes d'eaux pluviales PVC Ø110, y compris moignons et colliers", "ml", 1500,
     [("4 descentes × 4.50 m", 4, 4.50, None, None)]),
    ("6.7", "Couvertine d'acrotère (chaperon préfabriqué)", "ml", 2000, [("Périmètre de l'acrotère", 1, 46.80, None, None)]),
    ("LOT", "LOT 07 — MENUISERIE (BOIS ET ALUMINIUM)"),
    ("7.1", "P1 — Porte d'entrée bois massif 1.20 × 2.20, y compris serrure 3 points", "u", 85000, [("", 1, None, None, None)]),
    ("7.2", "P2 — Porte intérieure isoplane 0.90 × 2.20", "u", 28000, [("Chambres", 3, None, None, None)]),
    ("7.3", "P3 — Porte intérieure isoplane 0.80 × 2.20", "u", 26000, [("Cuisine", 1, None, None, None)]),
    ("7.4", "P4 — Porte intérieure isoplane 0.70 × 2.20", "u", 24000, [("WC", 1, None, None, None)]),
    ("7.5", "P5 — Porte vitrée 2 vantaux 1.40 × 2.20", "u", 55000, [("Salon", 1, None, None, None)]),
    ("7.6", "F1 — Fenêtre alu 2 vantaux 1.20 × 1.20, double vitrage + volet", "u", 45000,
     [("Chambres + salon", 4, None, None, None)]),
    ("7.7", "F2 — Fenêtre alu 2 vantaux 1.40 × 1.20, double vitrage + volet", "u", 52000, [("Salon + hall", 2, None, None, None)]),
    ("7.8", "F3 — Fenêtre alu 2 vantaux 1.00 × 1.20, double vitrage", "u", 32000, [("Cuisine + chambre 03", 2, None, None, None)]),
    ("7.9", "F4 — Châssis oscillo-battant 0.60 × 0.60", "u", 15000, [("WC", 1, None, None, None)]),
    ("LOT", "LOT 08 — PLOMBERIE ET SANITAIRE"),
    ("8.1", "Réseau d'alimentation eau froide / eau chaude en multicouche", "Ft", 120000, [("Forfait", 1, None, None, None)]),
    ("8.2", "Réseau d'évacuation EU / EV en PVC jusqu'au regard", "Ft", 80000, [("Forfait", 1, None, None, None)]),
    ("8.3", "WC à l'anglaise complet avec chasse d'eau", "u", 35000, [("", 1, None, None, None)]),
    ("8.4", "Lavabo sur colonne avec robinetterie mitigeuse", "u", 22000, [("", 1, None, None, None)]),
    ("8.5", "Évier inox 2 bacs avec robinetterie", "u", 30000, [("", 1, None, None, None)]),
    ("8.6", "Chauffe-eau à gaz 10 L", "u", 45000, [("", 1, None, None, None)]),
    ("8.7", "Regard de visite 50 × 50 avec tampon", "u", 6000, [("4 descentes EP + regard de façade", 4, None, None, None)]),
    ("LOT", "LOT 09 — ÉLECTRICITÉ"),
    ("9.1", "Tableau électrique avec disjoncteur différentiel et protections", "u", 45000, [("", 1, None, None, None)]),
    ("9.2", "Point lumineux en simple allumage, encastré", "u", 3500, [("2 par grand local", 14, None, None, None)]),
    ("9.3", "Prise de courant 2P+T 16 A, encastrée", "u", 3000, [("", 22, None, None, None)]),
    ("9.4", "Prise TV / RJ45", "u", 3500, [("Salon + chambres", 4, None, None, None)]),
    ("9.5", "Mise à la terre (piquet + câble cuivre nu)", "Ft", 25000, [("Forfait", 1, None, None, None)]),
    ("LOT", "LOT 10 — PEINTURE"),
    ("10.1", "Peinture vinylique sur murs et plafonds intérieurs (2 couches)", "m²", 450,
     [("Murs (enduit plâtre)", 1, "@5.3", None, None), ("Plafonds", 1, "@5.4", None, None)]),
    ("10.2", "Peinture de façade pliolite (2 couches)", "m²", 600, [("Enduit extérieur", 1, "@5.1", None, None)]),
    ("10.3", "Peinture glycérophtalique sur menuiseries bois", "m²", 650,
     [("Portes bois P1 à P4, 2 faces", 2, 11.88, None, None)]),
]


def style_range(ws, row, c0, c1, font=None, fill=None, border=True, align=None):
    for c in range(c0, c1 + 1):
        cell = ws.cell(row=row, column=c)
        if font:
            cell.font = font
        if fill:
            cell.fill = fill
        if border:
            cell.border = BOX
        if align:
            cell.alignment = align


def header(ws, row, labels, widths=None):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = WHITE_B
        c.fill = HEAD_FILL
        c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def build_devis():
    wb = Workbook()
    # ----------------------------------- Avant-métré -----------------------------------
    mt = wb.active
    mt.title = "Avant-métré"
    mt["A1"] = "AVANT-MÉTRÉ"
    mt["A1"].font = TITLE
    mt["A2"] = PROJECT
    mt["A2"].font = SUB
    mt["A3"] = ("Quantités relevées sur les plans (planches 01 à 10). Cellules bleues = dimensions saisies "
                "(modifiables) ; cellules vertes = renvois vers une autre quantité ; partiel = Nb × L × l × H "
                "(les cases vides valent 1).")
    mt["A3"].font = SUB
    header(mt, 5, ["N°", "Désignation des ouvrages", "U", "Nb", "Long. (m)", "Larg. (m)", "Haut. (m)", "Partiel",
                   "Quantité"], [7, 62, 6, 8, 11, 11, 11, 12, 13])
    r = 6
    qrow = {}
    pending = []  # (cell, expression) resolved once all item rows are known
    for it in ITEMS:
        if it[0] == "LOT":
            mt.cell(row=r, column=1, value=it[1])
            mt.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
            style_range(mt, r, 1, 9, font=BOLD, fill=LOT_FILL)
            r += 1
            continue
        code, des, unit, price, subs = it
        mt.cell(row=r, column=1, value=code)
        mt.cell(row=r, column=2, value=des)
        mt.cell(row=r, column=3, value=unit)
        style_range(mt, r, 1, 9, font=BOLD, fill=ITEM_FILL)
        mt.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="center")
        head = r
        r += 1
        first = r
        for lab, nb, L, l, h in subs:
            mt.cell(row=r, column=2, value=("   " + lab) if lab else "   —")
            for col, val in zip(range(4, 8), (nb, L, l, h)):
                cell = mt.cell(row=r, column=col)
                if isinstance(val, str) and val.startswith("@"):
                    pending.append((cell, val))
                    cell.font = GREEN
                elif val is not None:
                    cell.value = val
                    cell.font = BLUE_IN
                cell.number_format = NUM
            mt.cell(row=r, column=8, value=f'=IF(COUNT(D{r}:G{r})=0,"",PRODUCT(D{r}:G{r}))').number_format = NUM
            style_range(mt, r, 1, 9, border=True)
            for col in (1, 2, 3, 8, 9):
                if mt.cell(row=r, column=col).font != GREEN:
                    pass
            mt.cell(row=r, column=2).font = Font(name=F, size=9, italic=True, color="404040")
            r += 1
        q = mt.cell(row=head, column=9, value=f"=ROUND(SUM(H{first}:H{r - 1}),2)")
        q.number_format = NUM
        q.font = BOLD
        qrow[code] = head
    for cell, expr in pending:
        parts = [p.strip()[1:] for p in expr.split("+")]
        cell.value = "=" + "+".join(f"I{qrow[p]}" for p in parts)
    mt.freeze_panes = "A6"
    mt.page_setup.orientation = "portrait"
    mt.page_setup.fitToWidth = 1
    mt.sheet_properties.pageSetUpPr.fitToPage = True
    mt.page_setup.fitToHeight = 0
    mt.print_title_rows = "5:5"

    # ----------------------------------- DQE -----------------------------------
    dq = wb.create_sheet("DQE")
    dq["A1"] = "DEVIS QUANTITATIF ET ESTIMATIF (DQE)"
    dq["A1"].font = TITLE
    dq["A2"] = PROJECT
    dq["A2"].font = SUB
    dq["A3"] = ("Prix unitaires (cellules bleues) indicatifs, en dinars algériens (DA) hors taxes, niveau 2026 : "
                "à actualiser selon le marché local et les offres des entreprises.")
    dq["A3"].font = SUB
    header(dq, 5, ["N°", "Désignation des ouvrages", "U", "Quantité", "P.U. HT (DA)", "Montant HT (DA)"],
           [7, 68, 6, 13, 15, 18])
    r = 6
    lot_rows = []  # (title, subtotal row)
    cur_lot, lot_first = None, None

    def close_lot(r):
        dq.cell(row=r, column=2, value=f"Sous-total {cur_lot.split(' — ')[0]}")
        dq.cell(row=r, column=6, value=f"=SUM(F{lot_first}:F{r - 1})").number_format = MONEY0
        style_range(dq, r, 1, 6, font=BOLD, fill=TOT_FILL)
        dq.cell(row=r, column=2).alignment = Alignment(horizontal="right")
        lot_rows.append((cur_lot, r))
        return r + 2

    for it in ITEMS:
        if it[0] == "LOT":
            if cur_lot:
                r = close_lot(r)
            cur_lot = it[1]
            dq.cell(row=r, column=1, value=cur_lot)
            dq.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            style_range(dq, r, 1, 6, font=BOLD, fill=LOT_FILL)
            r += 1
            lot_first = r
            continue
        code, des, unit, price, subs = it
        dq.cell(row=r, column=1, value=code).alignment = Alignment(horizontal="center", vertical="top")
        dq.cell(row=r, column=2, value=des).alignment = Alignment(wrap_text=True, vertical="top")
        dq.cell(row=r, column=3, value=unit).alignment = Alignment(horizontal="center", vertical="top")
        q = dq.cell(row=r, column=4, value=f"='Avant-métré'!I{qrow[code]}")
        q.number_format = NUM
        p = dq.cell(row=r, column=5, value=price)
        p.number_format = MONEY0
        m = dq.cell(row=r, column=6, value=f"=ROUND(D{r}*E{r},0)")
        m.number_format = MONEY0
        style_range(dq, r, 1, 6, font=BLACK)
        q.font = GREEN
        p.font = BLUE_IN
        r += 1
    r = close_lot(r)
    total_ht_row = r
    dq.cell(row=r, column=2, value="TOTAL GÉNÉRAL HT")
    dq.cell(row=r, column=6, value="=" + "+".join(f"F{x}" for _, x in lot_rows)).number_format = MONEY
    style_range(dq, r, 1, 6, font=WHITE_B, fill=HEAD_FILL)
    dq.cell(row=r, column=2).alignment = Alignment(horizontal="right")
    dq.freeze_panes = "A6"
    dq.sheet_properties.pageSetUpPr.fitToPage = True
    dq.page_setup.fitToWidth = 1
    dq.page_setup.fitToHeight = 0
    dq.print_title_rows = "5:5"

    # ----------------------------------- Récapitulatif -----------------------------------
    rc = wb.create_sheet("Récapitulatif", 0)
    rc["A1"] = "RÉCAPITULATIF DU DEVIS ESTIMATIF"
    rc["A1"].font = TITLE
    rc["A2"] = PROJECT
    rc["A2"].font = SUB
    rc["A4"] = "Paramètres"
    rc["A4"].font = BOLD
    params = [("Taux de TVA", 0.19, "TVA en vigueur en Algérie (19 %) — à adapter au pays du projet."),
              ("Provision pour imprévus", 0.05, "Hypothèse : 5 % du total HT (aléas de chantier)."),
              ("Surface bâtie hors œuvre (m²)", 126.99, "Planche 01 — 15.30 × 8.30 m."),
              ("Surface habitable (m²)", 109.62, "Planche 01 — tableau des surfaces.")]
    for i, (lab, val, note) in enumerate(params):
        rr = 5 + i
        rc.cell(row=rr, column=1, value=lab).font = BLACK
        c = rc.cell(row=rr, column=3, value=val)
        c.font = BLUE_IN
        c.fill = PatternFill("solid", fgColor="FFFF00")
        c.number_format = "0.0%" if val < 1 else "#,##0.00"
        c.comment = Comment(note, "BE")
        rc.cell(row=rr, column=4, value=note).font = SUB
        style_range(rc, rr, 1, 3)
    header_row = 10
    for i, lab in enumerate(["N°", "Lot", "Montant HT (DA)", "% du total"], 1):
        c = rc.cell(row=header_row, column=i, value=lab)
        c.font = WHITE_B
        c.fill = HEAD_FILL
        c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center")
    for col, w in zip("ABCD", [7, 58, 22, 14]):
        rc.column_dimensions[col].width = w
    r = header_row + 1
    first = r
    for title, row in lot_rows:
        num, name = title.split(" — ")
        rc.cell(row=r, column=1, value=num.replace("LOT ", "")).alignment = Alignment(horizontal="center")
        rc.cell(row=r, column=2, value=name.capitalize())
        c = rc.cell(row=r, column=3, value=f"=DQE!F{row}")
        c.number_format = MONEY0
        c.font = GREEN
        rc.cell(row=r, column=4, value=f"=IF($C${first + len(lot_rows)}=0,0,C{r}/$C${first + len(lot_rows)})").number_format = "0.0%"
        style_range(rc, r, 1, 4)
        rc.cell(row=r, column=3).font = GREEN
        r += 1
    last = r - 1
    rows = [("Total HT des travaux", f"=SUM(C{first}:C{last})", MONEY, True),
            ("Imprévus", f"=ROUND(C{r}*$C$6,0)", MONEY, False),
            ("Total HT y compris imprévus", f"=C{r}+C{r + 1}", MONEY, True),
            ("TVA", f"=ROUND(C{r + 2}*$C$5,0)", MONEY, False),
            ("TOTAL TTC", f"=C{r + 2}+C{r + 3}", MONEY, True),
            ("Ratio : coût TTC par m² bâti", f"=IF($C$7=0,0,C{r + 4}/$C$7)", MONEY, False),
            ("Ratio : coût TTC par m² habitable", f"=IF($C$8=0,0,C{r + 4}/$C$8)", MONEY, False)]
    tot_row = r
    for i, (lab, f, fmt, bold) in enumerate(rows):
        rr = r + i
        rc.cell(row=rr, column=2, value=lab)
        c = rc.cell(row=rr, column=3, value=f)
        c.number_format = fmt
        style_range(rc, rr, 1, 4, font=BOLD if bold else BLACK, fill=TOT_FILL if bold else None)
        rc.cell(row=rr, column=2).alignment = Alignment(horizontal="right")
    rc.cell(row=tot_row, column=4, value=f"=IF(C{tot_row}=0,0,SUM(D{first}:D{last}))").number_format = "0.0%"
    style_range(rc, r + 4, 1, 4, font=WHITE_B, fill=HEAD_FILL)
    rc.cell(row=r + 4, column=2).alignment = Alignment(horizontal="right")
    rr = r + len(rows) + 1
    rc.cell(row=rr, column=1, value="Arrêté le présent devis à la somme TTC de : ................................................").font = BOLD
    rc.cell(row=rr + 2, column=1, value=(
        "Notes : quantités issues de l'avant-métré (feuille « Avant-métré ») établi d'après les plans ; prix unitaires "
        "indicatifs à actualiser ; aciers estimés par ratios (kg/m³) à remplacer par les nomenclatures définitives.")).font = SUB
    rc.cell(row=rr + 3, column=1, value=(
        "Légende : bleu = saisie modifiable · vert = lien vers une autre feuille · noir = calcul · fond jaune = "
        "hypothèse clé.")).font = SUB
    # sanity: link check between DQE total and recap
    rc.cell(row=rr + 5, column=2, value="Contrôle : total DQE − total récapitulatif (doit être 0)").font = SUB
    chk = rc.cell(row=rr + 5, column=3, value=f"=DQE!F{total_ht_row}-C{tot_row}")
    chk.number_format = MONEY0
    chk.font = SUB
    rc.sheet_properties.pageSetUpPr.fitToPage = True

    path = os.path.join(OUT, "Devis_quantitatif_estimatif.xlsx")
    wb.save(path)
    return path


# ------------------------------------------------------------------------------------------------
# Planning
# ------------------------------------------------------------------------------------------------
PHASES = {
    "Préparation": "7F7F7F",
    "Gros œuvre — infrastructure": "8C5A2B",
    "Gros œuvre — superstructure": "1F3B57",
    "Maçonnerie & étanchéité": "C0504D",
    "Corps d'état secondaires": "2E75B6",
    "Finitions & réception": "548235",
}
TASKS = [  # id, task, phase, duration (working days), predecessor, lag
    (1, "Installation de chantier", "Préparation", 5, None, 0),
    (2, "Implantation, piquetage et chaises", "Préparation", 2, 1, 0),
    (3, "Décapage et terrassements généraux", "Gros œuvre — infrastructure", 3, 2, 0),
    (4, "Fouilles en puits et en tranchées", "Gros œuvre — infrastructure", 5, 3, 0),
    (5, "Béton de propreté", "Gros œuvre — infrastructure", 2, 4, 0),
    (6, "Semelles + amorces de poteaux (ferraillage, coulage)", "Gros œuvre — infrastructure", 6, 5, 0),
    (7, "Longrines (coffrage, ferraillage, coulage)", "Gros œuvre — infrastructure", 6, 6, 0),
    (8, "Remblai, hérisson, polyane et dallage", "Gros œuvre — infrastructure", 6, 7, 0),
    (9, "Poteaux RDC", "Gros œuvre — superstructure", 5, 8, 0),
    (10, "Coffrage poutres + pose poutrelles et hourdis", "Gros œuvre — superstructure", 8, 9, 0),
    (11, "Ferraillage et coulage plancher terrasse", "Gros œuvre — superstructure", 4, 10, 0),
    (12, "Cure du béton et décoffrage (≥ 21 jours)", "Gros œuvre — superstructure", 18, 11, 0),
    (13, "Acrotère", "Gros œuvre — superstructure", 3, 12, 0),
    (14, "Maçonnerie des murs extérieurs (double cloison)", "Maçonnerie & étanchéité", 10, 11, 2),
    (15, "Cloisons intérieures + linteaux", "Maçonnerie & étanchéité", 6, 14, 0),
    (16, "Forme de pente + isolation thermique", "Maçonnerie & étanchéité", 3, 13, 0),
    (17, "Étanchéité multicouche + protection gravillons", "Maçonnerie & étanchéité", 4, 16, 0),
    (18, "Descentes d'eaux pluviales", "Maçonnerie & étanchéité", 2, 17, 0),
    (19, "Électricité : saignées, gaines, boîtiers", "Corps d'état secondaires", 5, 15, 0),
    (20, "Plomberie encastrée (EF/EC, évacuations)", "Corps d'état secondaires", 5, 15, 0),
    (21, "Pose des cadres de menuiseries", "Corps d'état secondaires", 3, 15, 0),
    (22, "Enduits extérieurs au ciment", "Corps d'état secondaires", 10, 18, 0),
    (23, "Enduits plâtre intérieurs (murs + plafonds)", "Corps d'état secondaires", 12, 20, 0),
    (24, "Placage pierre du soubassement", "Corps d'état secondaires", 4, 22, 0),
    (25, "Chapes, carrelage et plinthes", "Finitions & réception", 10, 23, 0),
    (26, "Faïence cuisine et WC", "Finitions & réception", 4, 25, 0),
    (27, "Pose des menuiseries (portes, fenêtres alu)", "Finitions & réception", 5, 25, 0),
    (28, "Appareillage sanitaire et électrique", "Finitions & réception", 4, 26, 0),
    (29, "Peinture intérieure", "Finitions & réception", 10, 28, 0),
    (30, "Peinture des façades", "Finitions & réception", 6, 24, 0),
    (31, "Nettoyage, levée des réserves, réception provisoire", "Finitions & réception", 3, 29, 0),
]


def build_planning():
    wb = Workbook()
    ws = wb.active
    ws.title = "Planning"
    ws["A1"] = "PLANNING PRÉVISIONNEL DES TRAVAUX (DIAGRAMME DE GANTT)"
    ws["A1"].font = TITLE
    ws["A2"] = PROJECT
    ws["A2"].font = SUB
    inputs = [
        ("Date de démarrage (ODS)", dt.date(2027, 1, 3), "dd/mm/yyyy",
         "Hypothèse : ordre de service le dimanche 03/01/2027 — à modifier."),
        ("Décalage week-end (jours)", 1, "0",
         "1 = week-end vendredi + samedi (Algérie) ; 0 = samedi + dimanche ; 2 = jeudi + vendredi."),
    ]
    for i, (lab, val, fmt, note) in enumerate(inputs):
        r = 3 + i
        ws.cell(row=r, column=2, value=lab).font = BOLD
        c = ws.cell(row=r, column=7, value=val)
        c.font = BLUE_IN
        c.fill = PatternFill("solid", fgColor="FFFF00")
        c.number_format = fmt
        c.border = BOX
        ws.cell(row=r, column=8, value=note).font = SUB
    N = len(TASKS)
    first, last = 9, 9 + N - 1
    ws.cell(row=5, column=2, value="Date d'achèvement prévue").font = BOLD
    c = ws.cell(row=5, column=7, value=f"=MAX(H{first}:H{last})")
    c.number_format = "dd/mm/yyyy"
    c.font = BOLD
    c.border = BOX
    ws.cell(row=6, column=2, value="Délai global (jours calendaires / mois)").font = BOLD
    c = ws.cell(row=6, column=7, value=f"=G5-G3+1")
    c.number_format = "0"
    c.font = BOLD
    c.border = BOX
    c = ws.cell(row=6, column=8, value="=ROUND(G6/30.4,1)")
    c.number_format = '0.0" mois"'
    c.font = BOLD

    labels = ["ID", "Tâche", "Phase", "Durée (j. ouvr.)", "Prédécesseur (ID)", "Décalage (j. ouvr.)", "Début", "Fin"]
    widths = [5, 46, 26, 9, 11, 10, 11.5, 11.5]
    for i, (lab, w) in enumerate(zip(labels, widths), 1):
        c = ws.cell(row=8, column=i, value=lab)
        c.font = WHITE_B
        c.fill = HEAD_FILL
        c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[8].height = 42
    rng_id = f"$A${first}:$A${last}"
    rng_end = f"$H${first}:$H${last}"
    for k, (tid, name, phase, dur, pred, lag) in enumerate(TASKS):
        r = first + k
        vals = [tid, name, phase, dur, pred, lag]
        for col, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=col, value=v)
            c.border = BOX
            c.font = BLUE_IN if col in (4, 5, 6) else BLACK
            if col in (1, 4, 5, 6):
                c.alignment = Alignment(horizontal="center")
        # WORKDAY (Sat/Sun weekend) applied on dates shifted by $G$4 days -> any 2-day weekend
        ws.cell(row=r, column=7, value=(
            f'=IF(E{r}="",WORKDAY($G$3-1+$G$4,1+F{r})-$G$4,'
            f"WORKDAY(INDEX({rng_end},MATCH(E{r},{rng_id},0))+$G$4,1+F{r})-$G$4)"))
        ws.cell(row=r, column=8, value=f"=WORKDAY(G{r}+$G$4,D{r}-1)-$G$4")
        for col in (7, 8):
            c = ws.cell(row=r, column=col)
            c.number_format = "dd/mm/yy"
            c.border = BOX
            c.font = BLACK
            c.alignment = Alignment(horizontal="center")
    # Gantt: weekly columns
    W = 30
    gc0 = 9
    for w in range(W):
        col = gc0 + w
        L = get_column_letter(col)
        ws.column_dimensions[L].width = 4.2
        c7 = ws.cell(row=7, column=col, value=f"S{w + 1}")
        c7.font = Font(name=F, size=8, bold=True, color="FFFFFF")
        c7.fill = HEAD_FILL
        c7.alignment = Alignment(horizontal="center")
        c8 = ws.cell(row=8, column=col, value=f"=$G$3+{7 * w}")
        c8.number_format = "dd/mm"
        c8.font = Font(name=F, size=7, bold=True, color="FFFFFF")
        c8.fill = HEAD_FILL
        c8.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90)
        for r in range(first, last + 1):
            ws.cell(row=r, column=col).border = Border(left=Side(style="hair", color="D9D9D9"),
                                                       right=Side(style="hair", color="D9D9D9"),
                                                       top=thin, bottom=thin)
    g0, g1 = get_column_letter(gc0), get_column_letter(gc0 + W - 1)
    area = f"{g0}{first}:{g1}{last}"
    for phase, color in PHASES.items():
        formula = (f'AND($C{first}="{phase}",{g0}$8<=$H{first},{g0}$8+6>=$G{first})')
        ws.conditional_formatting.add(area, FormulaRule(formula=[formula], fill=PatternFill("solid", fgColor=color),
                                                        stopIfTrue=True))
    ws.merge_cells(start_row=6, start_column=gc0, end_row=6, end_column=gc0 + W - 1)
    t = ws.cell(row=6, column=gc0, value="Semaines (date du 1er jour de chaque semaine)")
    t.font = BOLD
    t.alignment = Alignment(horizontal="center")
    # legend
    lr = last + 2
    ws.cell(row=lr, column=2, value="Légende des phases").font = BOLD
    for i, (phase, color) in enumerate(PHASES.items()):
        ws.cell(row=lr + 1 + i, column=1).fill = PatternFill("solid", fgColor=color)
        ws.cell(row=lr + 1 + i, column=2, value=phase).font = BLACK
    nr = lr + 1 + len(PHASES) + 1
    notes = [
        "Mode d'emploi : modifier la date de démarrage (G3), le décalage week-end (G4), les durées, prédécesseurs ou "
        "décalages (cellules bleues) ;",
        "les dates de début / fin et le diagramme se recalculent automatiquement (enchaînement fin → début).",
        "Durées estimées pour une équipe de gros œuvre de 6 à 8 ouvriers et des sous-traitants CES ; jours fériés "
        "non déduits.",
        "La tâche 12 (cure ≥ 21 jours calendaires) conditionne le décoffrage du plancher avant l'acrotère et "
        "l'étanchéité.",
    ]
    for i, n in enumerate(notes):
        ws.cell(row=nr + i, column=2, value=n).font = SUB
    ws.freeze_panes = ws.cell(row=first, column=gc0)
    ws.sheet_view.zoomScale = 90
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    path = os.path.join(OUT, "Planning_travaux.xlsx")
    wb.save(path)
    return path


if __name__ == "__main__":
    print(build_devis())
    print(build_planning())
