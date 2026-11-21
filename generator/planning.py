"""Detailed works schedule.

Outputs
  plans/Planning_travaux.xlsx : "Gantt détaillé" (day-by-day grid), "Planning" (data + CPM), "Diagramme" (Excel chart)
  plans/Planning_Gantt.pdf/.png : printable A2 Gantt diagram (critical path, dependencies, milestones)

Scheduling rules (identical in Python and in the Excel formulas):
  * finish-to-start links (up to 2 predecessors) + lag in working days;
  * working calendar = Excel WORKDAY (Sat/Sun off) applied on dates shifted by SHIFT days
    (SHIFT = 1 -> Friday/Saturday weekend, as in Algeria);
  * milestones have a duration of 0 and sit on the finish date of their predecessors.
"""
import datetime as dt
import os

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.marker import DataPoint
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(__file__), "..", "plans")
START = dt.date(2027, 1, 3)
SHIFT = 1

F = "Arial"
NAVY = "1F3B57"
PHASES = [  # key, title, colour
    ("A", "PRÉPARATION DU CHANTIER", "7F7F7F"),
    ("B", "TERRASSEMENTS & FONDATIONS", "8C5A2B"),
    ("C", "STRUCTURE BÉTON ARMÉ (SUPERSTRUCTURE)", "1F3B57"),
    ("D", "MAÇONNERIE", "BF8F00"),
    ("E", "ÉTANCHÉITÉ DE LA TERRASSE", "7030A0"),
    ("F", "CORPS D'ÉTAT SECONDAIRES", "2E75B6"),
    ("G", "FINITIONS & RÉCEPTION", "548235"),
]
PCOL = {k: c for k, _, c in PHASES}
CRIT = "C00000"

# id, task, phase, duration (working days, 0 = milestone), predecessors, lag
TASKS = [
    (1, "◆ Ordre de service (ODS) — démarrage des travaux", "A", 0, [], 0),
    (2, "Installation de chantier (clôture, baraque, eau, électricité)", "A", 4, [1], 0),
    (3, "Implantation des axes, chaises et nivellement", "A", 2, [2], 0),
    (4, "Décapage de la terre végétale", "B", 2, [3], 0),
    (5, "Fouilles en puits pour semelles", "B", 4, [4], 0),
    (6, "Fouilles en tranchée pour longrines", "B", 2, [5], 0),
    (7, "Réception des fonds de fouille (BET / labo)", "B", 1, [6], 0),
    (8, "Béton de propreté", "B", 1, [7], 0),
    (9, "Ferraillage semelles + amorces de poteaux", "B", 3, [8], 0),
    (10, "Coffrage et coulage semelles + amorces", "B", 2, [9], 0),
    (11, "Coffrage et ferraillage des longrines", "B", 3, [10], 0),
    (12, "Coulage des longrines", "B", 1, [11], 0),
    (13, "Remblai compacté (après décoffrage)", "B", 2, [12], 2),
    (14, "Hérisson en pierres sèches + film polyane", "B", 2, [13], 0),
    (15, "Dallage BA ép. 10 cm", "B", 2, [14], 0),
    (16, "◆ Fin de l'infrastructure", "B", 0, [15], 0),
    (17, "Ferraillage et coffrage des poteaux", "C", 3, [16], 0),
    (18, "Coulage des poteaux", "C", 1, [17], 0),
    (19, "Coffrage des poutres + étaiement du plancher", "C", 4, [18], 1),
    (20, "Pose des poutrelles et des hourdis", "C", 3, [19], 0),
    (21, "Ferraillage poutres + treillis de la dalle de compression", "C", 3, [20], 0),
    (22, "Réception du ferraillage (BET)", "C", 1, [21], 0),
    (23, "Coulage du plancher terrasse", "C", 1, [22], 0),
    (24, "Cure du béton (arrosage pendant 7 jours)", "C", 6, [23], 0),
    (25, "Décoffrage et désétaiement (≥ 21 jours après coulage)", "C", 2, [23], 16),
    (26, "Acrotère (coffrage, ferraillage, coulage)", "C", 3, [25], 0),
    (27, "◆ Fin du gros œuvre", "C", 0, [26], 0),
    (28, "Murs extérieurs en double cloison", "D", 10, [23], 3),
    (29, "Linteaux BA des ouvertures", "D", 2, [28], 0),
    (30, "Cloisons intérieures en brique de 10", "D", 6, [29], 0),
    (31, "Forme de pente (2 %)", "E", 2, [27], 0),
    (32, "Pare-vapeur + isolation thermique", "E", 1, [31], 0),
    (33, "Étanchéité multicouche + relevés", "E", 3, [32], 0),
    (34, "Protection gravillons + couvertines d'acrotère", "E", 2, [33], 0),
    (35, "Descentes d'eaux pluviales", "E", 2, [34], 0),
    (36, "◆ Bâtiment hors d'eau", "E", 0, [35, 30], 0),
    (37, "Électricité : saignées, gaines, boîtiers", "F", 5, [30], 0),
    (38, "Plomberie encastrée (EF / EC, évacuations)", "F", 5, [30], 0),
    (39, "Pose des précadres de menuiseries", "F", 2, [30], 0),
    (40, "Réseaux extérieurs et regards", "F", 3, [35], 0),
    (41, "Enduits plâtre intérieurs (murs + plafonds)", "F", 12, [37, 38], 0),
    (42, "Enduits extérieurs au mortier de ciment", "F", 10, [36], 0),
    (43, "Placage pierre du soubassement", "F", 4, [42], 0),
    (44, "Chapes, carrelage et plinthes", "G", 10, [41], 0),
    (45, "Faïence cuisine et WC", "G", 4, [44], 0),
    (46, "Pose des menuiseries aluminium et des portes", "G", 5, [44, 39], 0),
    (47, "Appareillage sanitaire", "G", 2, [45], 0),
    (48, "Appareillage électrique + tableau", "G", 2, [45], 0),
    (49, "Peinture intérieure (2 couches)", "G", 10, [47, 48], 0),
    (50, "Peinture des façades", "G", 6, [43], 0),
    (51, "Nettoyage de fin de chantier", "G", 2, [49, 50], 0),
    (52, "Essais, levée des réserves", "G", 2, [51], 0),
    (53, "◆ Réception provisoire", "G", 0, [52], 0),
]


# ------------------------------------------------------------------ calendar (mirrors Excel WORKDAY) --
def _is_work(d):
    return (d + dt.timedelta(days=SHIFT)).weekday() < 5


def workday(d, n):
    """Excel WORKDAY(d+SHIFT, n) - SHIFT."""
    step = 1 if n > 0 else -1
    k = abs(n)
    while k:
        d += dt.timedelta(days=step)
        if _is_work(d):
            k -= 1
    return d


def networkdays(a, b):
    n, d = 0, a
    while d <= b:
        n += _is_work(d)
        d += dt.timedelta(days=1)
    return n


def schedule():
    S = {}
    for tid, name, ph, dur, preds, lag in TASKS:
        if not preds:
            s = workday(START - dt.timedelta(days=1), 1)
        else:
            me = max(S[p]["end"] for p in preds)
            s = me if dur == 0 else workday(me, 1 + lag)
        e = s if dur == 0 else workday(s, dur - 1)
        S[tid] = dict(start=s, end=e, dur=dur, preds=preds, lag=lag, name=name, ph=ph, succ=[])
    for tid, t in S.items():
        for p in t["preds"]:
            S[p]["succ"].append(tid)
    pend = max(t["end"] for t in S.values())
    for tid in sorted(S, reverse=True):
        t = S[tid]
        if t["succ"]:
            cands = []
            for j in t["succ"]:
                sj = S[j]
                cands.append(sj["ls"] if sj["dur"] == 0 else workday(sj["ls"], -1 - sj["lag"]))
            t["lf"] = min(cands)
        else:
            t["lf"] = pend
        t["ls"] = t["lf"] if t["dur"] == 0 else workday(t["lf"], -(t["dur"] - 1))
        t["float"] = networkdays(t["end"], t["lf"]) - 1 if _is_work(t["end"]) else networkdays(t["end"], t["lf"])
        t["crit"] = t["float"] <= 0
    return S, pend


# ------------------------------------------------------------------ Excel ------------------------------
thin = Side(style="thin", color="A6A6A6")
hair = Side(style="hair", color="D0D0D0")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def _f(**kw):
    return Font(name=F, size=kw.pop("size", 9), **kw)


def _head(ws, row, col, val, w=None, rot=0):
    c = ws.cell(row=row, column=col, value=val)
    c.font = _f(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.border = BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True, text_rotation=rot)
    if w:
        ws.column_dimensions[get_column_letter(col)].width = w
    return c


def _layout():
    """Rows (phase headers + tasks) in display order."""
    rows = []
    for key, title, _ in PHASES:
        rows.append(("phase", key, title))
        rows += [("task", t) for t in TASKS if t[2] == key]
    return rows


def build_planning():
    S, pend = schedule()
    rows = _layout()
    FIRST = 10
    LAST = FIRST + len(rows) - 1
    rowof = {}
    for i, r in enumerate(rows):
        if r[0] == "task":
            rowof[r[1][0]] = FIRST + i
    succ = {tid: S[tid]["succ"] for tid in S}

    wb = Workbook()
    gt = wb.active
    gt.title = "Gantt détaillé"
    pl = wb.create_sheet("Planning")
    ch = wb.create_sheet("Diagramme")

    # ============================ Planning (data + CPM) ============================
    pl["A1"] = "PLANNING DES TRAVAUX — DONNÉES ET CALCUL DU CHEMIN CRITIQUE"
    pl["A1"].font = Font(name=F, size=14, bold=True, color=NAVY)
    pl["A2"] = "Construction d'une habitation individuelle en R.D.C — 15.00 × 8.00 m"
    pl["A2"].font = _f(italic=True, color="595959")
    inputs = [
        (3, "Date de démarrage (ODS)", START, "dd/mm/yyyy", "Hypothèse : ODS le dimanche 03/01/2027 — à modifier."),
        (4, "Décalage week-end (jours)", SHIFT, "0",
         "1 = week-end vendredi + samedi (Algérie) ; 0 = samedi + dimanche ; 2 = jeudi + vendredi."),
    ]
    for r, lab, val, fmt, note in inputs:
        pl.cell(row=r, column=2, value=lab).font = _f(bold=True)
        c = pl.cell(row=r, column=4, value=val)
        c.font = _f(color="0000FF", bold=True)
        c.fill = PatternFill("solid", fgColor="FFFF00")
        c.number_format = fmt
        c.border = BOX
        pl.cell(row=r, column=5, value=note).font = _f(italic=True, color="595959")
    pl.cell(row=5, column=2, value="Date d'achèvement prévue").font = _f(bold=True)
    pl.cell(row=6, column=2, value="Délai global (j. calendaires / j. ouvrables / mois)").font = _f(bold=True)
    pl.cell(row=7, column=2, value="Nombre de tâches critiques").font = _f(bold=True)
    H = "$H${}:$H${}".format(FIRST, LAST)
    A = "$A${}:$A${}".format(FIRST, LAST)
    c = pl.cell(row=5, column=4, value=f"=MAX({H})")
    c.number_format = "dd/mm/yyyy"
    pl.cell(row=6, column=4, value="=D5-D3+1").number_format = '0" j"'
    pl.cell(row=6, column=5, value="=NETWORKDAYS(D3+D4,D5+D4)").number_format = '0" j.o."'
    pl.cell(row=6, column=6, value="=ROUND(D6/30.4,1)").number_format = '0.0" mois"'
    pl.cell(row=7, column=4, value=f'=COUNTIFS($M${FIRST}:$M${LAST},"Oui",$C${FIRST}:$C${LAST},"<>Phase")')
    for rr in (5, 6, 7):
        for cc in (4, 5, 6):
            cell = pl.cell(row=rr, column=cc)
            if cell.value is not None:
                cell.font = _f(bold=True)
                cell.border = BOX

    cols = [("ID", 5), ("Tâche", 50), ("Phase", 7), ("Durée (j.o.)", 7), ("Préd. 1", 6), ("Préd. 2", 6),
            ("Décalage (j.o.)", 7), ("Début au plus tôt", 10.5), ("Fin au plus tôt", 10.5), ("Début au plus tard", 10.5),
            ("Fin au plus tard", 10.5), ("Marge totale (j.o.)", 7.5), ("Critique", 7.5), ("Avancement", 8.5)]
    for i, (lab, w) in enumerate(cols, 1):
        _head(pl, 9, i, lab, w)
    pl.row_dimensions[9].height = 40
    s = "$D$4"
    for i, r in enumerate(rows):
        R = FIRST + i
        if r[0] == "phase":
            key, title = r[1], r[2]
            ph_rows = [rowof[t[0]] for t in TASKS if t[2] == key]
            a, b = min(ph_rows), max(ph_rows)
            vals = {1: key, 2: title, 3: "Phase",
                    4: f"=NETWORKDAYS(H{R}+{s},I{R}+{s})",
                    8: f"=MIN(H{a}:H{b})", 9: f"=MAX(I{a}:I{b})",
                    13: f'=IF(COUNTIF(M{a}:M{b},"Oui")>0,"Oui","Non")',
                    14: f"=IF(SUM(D{a}:D{b})=0,0,SUMPRODUCT(D{a}:D{b},N{a}:N{b})/SUM(D{a}:D{b}))"}
            for col in range(1, 15):
                c = pl.cell(row=R, column=col, value=vals.get(col))
                c.font = _f(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=PCOL[key])
                c.border = BOX
            for col in (8, 9):
                pl.cell(row=R, column=col).number_format = "dd/mm/yy"
            pl.cell(row=R, column=14).number_format = "0%"
            continue
        tid, name, ph, dur, preds, lag = r[1]
        p1 = preds[0] if preds else None
        p2 = preds[1] if len(preds) > 1 else None
        maxend = (f"MAX(IFERROR(INDEX({H.replace('H', 'I')},MATCH(E{R},{A},0)),0),"
                  f"IFERROR(INDEX({H.replace('H', 'I')},MATCH(F{R},{A},0)),0))")
        start = (f'=IF(AND(E{R}="",F{R}=""),WORKDAY($D$3-1+{s},1)-{s},'
                 f"IF(D{R}=0,{maxend},WORKDAY({maxend}+{s},1+G{R})-{s}))")
        end = f"=IF(D{R}=0,H{R},WORKDAY(H{R}+{s},D{R}-1)-{s})"
        # backward pass: successors are fixed from the network data
        if succ[tid]:
            terms = [f"IF(D{rowof[j]}=0,J{rowof[j]},WORKDAY(J{rowof[j]}+{s},-1-G{rowof[j]})-{s})" for j in succ[tid]]
            lf = "=" + (terms[0] if len(terms) == 1 else "MIN(" + ",".join(terms) + ")")
        else:
            lf = "=$D$5"
        ls = f"=IF(D{R}=0,K{R},WORKDAY(K{R}+{s},-(D{R}-1))-{s})"
        flt = f"=NETWORKDAYS(I{R}+{s},K{R}+{s})-IF(WEEKDAY(I{R}+{s},2)<6,1,0)"
        crit = f'=IF(L{R}<=0,"Oui","Non")'
        vals = [tid, name, ph, dur, p1, p2, lag, start, end, ls, lf, flt, crit, 0]
        for col, v in enumerate(vals, 1):
            c = pl.cell(row=R, column=col, value=v)
            c.border = BOX
            c.font = _f(color="0000FF") if col in (4, 5, 6, 7, 14) else _f()
            if col != 2:
                c.alignment = Alignment(horizontal="center")
        for col in (8, 9, 10, 11):
            pl.cell(row=R, column=col).number_format = "dd/mm/yy"
        pl.cell(row=R, column=14).number_format = "0%"
        if dur == 0:
            pl.cell(row=R, column=2).font = _f(bold=True, color=CRIT)
    pl.conditional_formatting.add(f"M{FIRST}:M{LAST}", FormulaRule(
        formula=[f'AND($M{FIRST}="Oui",$C{FIRST}<>"Phase")'], font=Font(color=CRIT, bold=True),
        fill=PatternFill("solid", fgColor="FCE4E4")))
    nr = LAST + 2
    for k, txt in enumerate([
        "Mode d'emploi : modifier la date de démarrage (D3), le décalage week-end (D4), les durées, prédécesseurs, "
        "décalages et l'avancement (cellules bleues) ; dates, marges et Gantt se recalculent.",
        "Liaisons fin → début (2 prédécesseurs max). Le calcul « au plus tard » utilise la liste des successeurs du "
        "réseau initial : si vous changez un prédécesseur, vérifiez les marges.",
        "Durées pour une équipe de gros œuvre de 6 à 8 ouvriers + sous-traitants CES ; jours fériés non déduits.",
    ]):
        pl.cell(row=nr + k, column=2, value=txt).font = _f(italic=True, color="595959")
    pl.freeze_panes = pl.cell(row=FIRST, column=3)

    # ============================ Gantt détaillé (day-by-day) ============================
    days = (pend - START).days + 12
    C0 = 9  # first calendar column (I)
    gt["A1"] = "DIAGRAMME DE GANTT DÉTAILLÉ — PLANNING PRÉVISIONNEL DES TRAVAUX"
    gt["A1"].font = Font(name=F, size=14, bold=True, color=NAVY)
    gt["A2"] = ("Construction d'une habitation individuelle en R.D.C — calendrier jour par jour "
                "(données et paramètres : feuille « Planning »)")
    gt["A2"].font = _f(italic=True, color="595959")
    for r, cl, lab, f, fmt in [(3, 2, "Démarrage :", "=Planning!D3", "dd/mm/yyyy"),
                               (4, 2, "Achèvement :", "=Planning!D5", "dd/mm/yyyy"),
                               (5, 2, "Délai :", "=Planning!D6", '0" jours calendaires"'),
                               (3, 6, "W-E :", "=Planning!D4", '"décalage "0')]:
        gt.cell(row=r, column=cl, value=lab).font = _f(bold=True)
        c = gt.cell(row=r, column=cl + 2 if cl == 2 else 7, value=f)
        c.number_format = fmt
        c.font = _f(bold=True, color="008000")
    # legend (top right)
    leg = [("Tâche (couleur de la phase)", PCOL["C"]), ("Tâche critique (marge nulle)", CRIT),
           ("Partie réalisée (avancement)", "262626"), ("Récapitulatif de phase", "404040"),
           ("Jour non ouvré (week-end)", "E7E6E6")]
    for k, (lab, col) in enumerate(leg):
        cc = C0 + 2 + k * 14
        gt.cell(row=3, column=cc).fill = PatternFill("solid", fgColor=col)
        gt.cell(row=3, column=cc + 1, value=lab).font = _f(size=8)
    gt.cell(row=4, column=C0 + 2, value="◆").font = _f(bold=True, color=CRIT, size=11)
    gt.cell(row=4, column=C0 + 3, value="Jalon").font = _f(size=8)

    hdr = [("ID", 4.5), ("Tâche", 46), ("Ph.", 4), ("Durée", 6), ("Début", 8.5), ("Fin", 8.5), ("Marge", 6),
           ("Avanc.", 6.5)]
    for i, (lab, w) in enumerate(hdr, 1):
        gt.merge_cells(start_row=6, start_column=i, end_row=9, end_column=i)
        _head(gt, 6, i, lab, w)
    gt.row_dimensions[8].height = 13
    # calendar header rows: 6 month, 7 week, 8 date (day number), 9 weekday letter
    for k in range(days):
        col = C0 + k
        L = get_column_letter(col)
        gt.column_dimensions[L].width = 2.6
        d = f"Planning!$D$3+{k}"
        m = gt.cell(row=6, column=col, value=f'=IF(OR({k}=0,DAY({d})=1),{d},"")')
        m.number_format = "mmm yyyy"
        w = gt.cell(row=7, column=col, value=f'=IF(MOD({k},7)=0,"S"&({k}/7+1),"")')
        dd = gt.cell(row=8, column=col, value=f"={d}")
        dd.number_format = "d"
        wd = gt.cell(row=9, column=col, value=f'=CHOOSE(WEEKDAY({L}$8),"D","L","M","M","J","V","S")')
        for c, sz in ((m, 8), (w, 7), (dd, 7), (wd, 7)):
            c.font = _f(size=sz, bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=NAVY if c is not wd else "2F5577")
            c.alignment = Alignment(horizontal="left" if c is m else "center", vertical="center")
        for r in range(FIRST, LAST + 1):
            gt.cell(row=r, column=col).border = Border(left=hair, right=hair, top=hair, bottom=hair)
    gt.row_dimensions[6].height = 15
    for i, r in enumerate(rows):
        R = FIRST + i
        if r[0] == "phase":
            key = r[1]
            vals = [f"=Planning!A{R}", f"=Planning!B{R}", "P", f"=Planning!D{R}", f"=Planning!H{R}",
                    f"=Planning!I{R}", "", f"=Planning!N{R}"]
            for col, v in enumerate(vals, 1):
                c = gt.cell(row=R, column=col, value=v)
                c.font = _f(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=PCOL[key])
                c.border = BOX
            gt.row_dimensions[R].height = 15
        else:
            tid, name, ph, dur, *_ = r[1]
            vals = [f"=Planning!A{R}", f"=Planning!B{R}", ph, f"=Planning!D{R}", f"=Planning!H{R}",
                    f"=Planning!I{R}", f"=Planning!L{R}", f"=Planning!N{R}"]
            for col, v in enumerate(vals, 1):
                c = gt.cell(row=R, column=col, value=v)
                c.font = _f(bold=dur == 0, color=CRIT if dur == 0 else "000000")
                c.border = BOX
                if col != 2:
                    c.alignment = Alignment(horizontal="center")
            if dur == 0:
                for k in range(days):
                    col = C0 + k
                    L = get_column_letter(col)
                    c = gt.cell(row=R, column=col, value=f'=IF({L}$8=$E{R},"◆","")')
                    c.font = _f(bold=True, color=CRIT, size=10)
                    c.alignment = Alignment(horizontal="center", vertical="center")
        for col in (5, 6):
            gt.cell(row=R, column=col).number_format = "dd/mm/yy"
        gt.cell(row=R, column=8).number_format = "0%"
        gt.cell(row=R, column=7).number_format = "0"
    g0 = get_column_letter(C0)
    g1 = get_column_letter(C0 + days - 1)
    area = f"{g0}{FIRST}:{g1}{LAST}"
    inr = f"AND({g0}$8>=$E{FIRST},{g0}$8<=$F{FIRST},$D{FIRST}>0)"
    done = f"{g0}$8<$E{FIRST}+$H{FIRST}*($F{FIRST}-$E{FIRST}+1)"
    rules = [
        (f'AND($C{FIRST}="P",{g0}$8>=$E{FIRST},{g0}$8<=$F{FIRST})', "404040"),
        (f"AND({inr},{done})", "262626"),
        (f'AND({inr},Planning!$M{FIRST}="Oui")', CRIT),
    ]
    rules += [(f'AND({inr},$C{FIRST}="{k}")', c) for k, _, c in PHASES]
    rules += [(f"WEEKDAY({g0}$8+$G$3,2)>5", "E7E6E6")]
    for formula, colr in rules:
        gt.conditional_formatting.add(area, FormulaRule(formula=[formula], fill=PatternFill("solid", fgColor=colr),
                                                        stopIfTrue=True))
    # weekend shading also in header weekday letters
    gt.conditional_formatting.add(f"{g0}9:{g1}9", FormulaRule(
        formula=[f"WEEKDAY({g0}$8+$G$3,2)>5"], fill=PatternFill("solid", fgColor="8EA9C1")))
    gt.freeze_panes = gt.cell(row=FIRST, column=C0)
    gt.sheet_view.zoomScale = 85
    gt.page_setup.orientation = "landscape"
    gt.page_setup.paperSize = gt.PAPERSIZE_A3
    gt.sheet_properties.pageSetUpPr.fitToPage = True
    gt.page_setup.fitToWidth = 1
    gt.page_setup.fitToHeight = 1
    gt.print_title_cols = "A:H"

    # ============================ Diagramme (native Excel chart) ============================
    ch["A1"] = "DIAGRAMME DE GANTT (GRAPHIQUE EXCEL)"
    ch["A1"].font = Font(name=F, size=14, bold=True, color=NAVY)
    ch["A2"] = "Données liées à la feuille « Planning » ; barres rouges = chemin critique."
    ch["A2"].font = _f(italic=True, color="595959")
    for i, (lab, w) in enumerate([("Tâche", 52), ("Début", 11), ("Durée (j. cal.)", 11)], 1):
        _head(ch, 4, i, lab, w)
    tasks_only = [t for t in TASKS]
    for k, t in enumerate(tasks_only):
        R = 5 + k
        pr = rowof[t[0]]
        ch.cell(row=R, column=1, value=f'=Planning!A{pr}&" - "&Planning!B{pr}').font = _f(color="008000")
        c = ch.cell(row=R, column=2, value=f"=Planning!H{pr}")
        c.number_format = "dd/mm/yy"
        c.font = _f(color="008000")
        ch.cell(row=R, column=3, value=f"=MAX(Planning!I{pr}-Planning!H{pr}+1,0.6)").font = _f()
    n = len(tasks_only)
    bc = BarChart()
    bc.type = "bar"
    bc.grouping = "stacked"
    bc.overlap = 100
    bc.gapWidth = 40
    bc.title = "Planning prévisionnel des travaux"
    bc.roundedCorners = False
    data = Reference(ch, min_col=2, max_col=3, min_row=4, max_row=4 + n)
    cats = Reference(ch, min_col=1, min_row=5, max_row=4 + n)
    bc.add_data(data, titles_from_data=True)
    bc.set_categories(cats)
    bc.series[0].graphicalProperties.noFill = True
    bc.series[0].graphicalProperties.line.noFill = True
    s1 = bc.series[1]
    s1.graphicalProperties.solidFill = PCOL["C"]
    for k, t in enumerate(tasks_only):
        col = CRIT if S[t[0]]["crit"] and t[3] > 0 else ("000000" if t[3] == 0 else PCOL[t[2]])
        pt = DataPoint(idx=k)
        pt.graphicalProperties = GraphicalProperties(solidFill=col)
        s1.dPt.append(pt)
    bc.y_axis.scaling.min = (START - dt.date(1899, 12, 30)).days
    bc.y_axis.scaling.max = (pend - dt.date(1899, 12, 30)).days + 3
    bc.y_axis.majorUnit = 7
    bc.y_axis.number_format = "dd/mm"
    bc.x_axis.scaling.orientation = "maxMin"
    bc.x_axis.delete = False
    bc.y_axis.delete = False
    bc.legend = None
    bc.width = 34
    bc.height = 26
    ch.add_chart(bc, "E4")

    for w in (pl, ch):
        w.page_setup.orientation = "landscape"
        w.page_setup.paperSize = w.PAPERSIZE_A3
        w.sheet_properties.pageSetUpPr.fitToPage = True
        w.page_setup.fitToWidth = 1
        w.page_setup.fitToHeight = 1
    path = os.path.join(OUT, "Planning_travaux.xlsx")
    wb.save(path)
    return path


# ------------------------------------------------------------------ PDF Gantt -------------------------
def build_gantt_pdf():
    import matplotlib.patches as mp
    from matplotlib.backends.backend_pdf import PdfPages

    from drawing import ACCENT, GREY, INK, Sheet

    S, pend = schedule()
    rows = _layout()
    sh = Sheet("A2", 1, 1, "PLANNING DES TRAVAUX (GANTT)", "PLANNING", "—")
    ax = sh.ax
    # geometry (paper mm)
    xl, xc = 25.0, 205.0          # table left, chart left
    xr = 580.0
    ytop, ybot = 372.0, 92.0
    ndays = (pend - START).days + 6
    dx = (xr - xc) / ndays
    rh = (ytop - ybot) / len(rows)

    def X(d):
        return xc + (d - START).days * dx

    sh.view_title(25, 395, "DIAGRAMME DE GANTT DÉTAILLÉ — PLANNING PRÉVISIONNEL DES TRAVAUX", None, h=4.6)
    crit_n = sum(1 for t in S.values() if t["crit"] and t["dur"] > 0)
    sh.text(25, 384, f"Démarrage (ODS) : {START:%d/%m/%Y}    ·    Réception provisoire : {pend:%d/%m/%Y}    ·    "
                     f"Délai : {(pend - START).days + 1} jours calendaires ({networkdays(START, pend)} jours ouvrables, "
                     f"≈ {((pend - START).days + 1) / 30.4:.1f} mois)    ·    {crit_n} tâches critiques    ·    "
                     "Week-end : vendredi + samedi", h=2.6, color=GREY)
    # header bands
    hy0 = ytop
    sh.rect(xl, hy0, xr, hy0 + 12, fc="#1F3B57", ec=INK, lw="thin")
    for x0, lab in [(xl, "N°"), (xl + 7, "Tâche"), (xc - 62, "Durée"), (xc - 47, "Début"), (xc - 29, "Fin"),
                    (xc - 12, "Marge")]:
        sh.text(x0 + 1.2, hy0 + 6, lab, h=2.3, va="center", weight="bold", color="white")
    # months / weeks
    d = START
    while d <= START + dt.timedelta(days=ndays - 1):
        if d == START or d.day == 1:
            nxt = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
            x1 = min(X(nxt), xr)
            sh.line([(X(d), hy0 + 6), (X(d), hy0 + 12)], lw="fine", color="white")
            mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                    "novembre", "décembre"][d.month - 1]
            sh.text((X(d) + x1) / 2, hy0 + 9, f"{mois} {d.year}", h=2.3, ha="center", va="center", weight="bold",
                    color="white")
        d += dt.timedelta(days=1)
    for k in range(0, ndays, 7):
        x = xc + k * dx
        sh.line([(x, ybot), (x, hy0 + 6)], lw="hair", color="#9aa9b8")
        sh.text(x + 3.5 * dx, hy0 + 3, f"S{k // 7 + 1}", h=1.9, ha="center", va="center", color="white")
    sh.line([(xc, hy0 + 6), (xr, hy0 + 6)], lw="fine", color="white")
    # weekend shading
    for k in range(ndays):
        dd = START + dt.timedelta(days=k)
        if not _is_work(dd):
            sh.rect(xc + k * dx, ybot, xc + (k + 1) * dx, ytop, fc="#efefef", ec="none", z=1)
    # rows
    ypos = {}
    for i, r in enumerate(rows):
        y1 = ytop - i * rh
        y0 = y1 - rh
        yc = (y0 + y1) / 2
        if r[0] == "phase":
            key, title = r[1], r[2]
            ts = [S[t[0]] for t in TASKS if t[2] == key]
            a, b = min(t["start"] for t in ts), max(t["end"] for t in ts)
            col = "#" + PCOL[key]
            sh.rect(xl, y0, xc, y1, fc=col, ec="none", z=2)
            sh.text(xl + 1.2, yc, key, h=2.3, va="center", weight="bold", color="white")
            sh.text(xl + 8, yc, title, h=2.3, va="center", weight="bold", color="white")
            sh.text(xc - 56, yc, f"{networkdays(a, b)} j", h=2.0, ha="center", va="center", color="white",
                    weight="bold")
            sh.text(xc - 38, yc, f"{a:%d/%m/%y}", h=2.0, ha="center", va="center", color="white")
            sh.text(xc - 20.5, yc, f"{b:%d/%m/%y}", h=2.0, ha="center", va="center", color="white")
            bx0, bx1 = X(a), X(b) + dx
            hh = rh * 0.22
            sh.rect(bx0, yc - hh, bx1, yc + hh, fc="#262626", ec="none", z=5)
            for xx in (bx0, bx1):
                ax.add_patch(mp.Polygon([(xx - 1.1, yc - hh), (xx + 1.1, yc - hh), (xx, yc - hh - 1.6)],
                                        closed=True, fc="#262626", ec="none", zorder=5))
            sh.line([(xl, y0), (xr, y0)], lw="fine", color=GREY)
            continue
        tid, name, ph, dur, preds, lag = r[1]
        t = S[tid]
        ypos[tid] = yc
        if i % 2:
            sh.rect(xl, y0, xc, y1, fc="#f6f8fa", ec="none", z=1.5)
        crit = t["crit"]
        color = "#" + (CRIT if crit and dur > 0 else PCOL[ph])
        sh.text(xl + 1.2, yc, str(tid), h=2.0, va="center", color=INK)
        nm = name.replace("◆ ", "")
        sh.text(xl + 7, yc, nm if len(nm) <= 58 else nm[:56] + "…", h=2.0, va="center",
                weight="bold" if dur == 0 else "normal", color="#" + CRIT if dur == 0 else INK)
        sh.text(xc - 56, yc, f"{dur} j" if dur else "—", h=2.0, ha="center", va="center")
        sh.text(xc - 38, yc, f"{t['start']:%d/%m/%y}", h=2.0, ha="center", va="center")
        sh.text(xc - 20.5, yc, f"{t['end']:%d/%m/%y}", h=2.0, ha="center", va="center")
        sh.text(xc - 5.5, yc, f"{t['float']}" if dur else "", h=2.0, ha="center", va="center",
                color="#" + CRIT if crit else INK, weight="bold" if crit else "normal")
        if dur == 0:
            xm = X(t["start"]) + dx
            r_ = rh * 0.42
            ax.add_patch(mp.Polygon([(xm, yc + r_), (xm + r_, yc), (xm, yc - r_), (xm - r_, yc)], closed=True,
                                    fc="#" + CRIT, ec=INK, lw=0.4, zorder=7))
            lab = f"{nm}  {t['start']:%d/%m}"
            right = xm + r_ + 1.2 + len(lab) * 1.2 > xr
            sh.text(xm - r_ - 1.2 if right else xm + r_ + 1.2, yc, lab, h=1.9, va="center", weight="bold",
                    color="#" + CRIT, z=8, ha="right" if right else "left")
        else:
            bx0, bx1 = X(t["start"]), X(t["end"]) + dx
            hh = rh * 0.32
            sh.rect(bx0, yc - hh, bx1, yc + hh, fc=color, ec=INK, lw="hair", z=5)
            # free float bar (total float shown as thin line)
            if t["float"] > 0:
                sh.line([(bx1, yc), (X(t["lf"]) + dx, yc)], lw="thin", color=GREY, ls="dot", z=4)
                sh.line([(X(t["lf"]) + dx, yc - hh * 0.6), (X(t["lf"]) + dx, yc + hh * 0.6)], lw="thin",
                        color=GREY, z=4)
            if bx1 - bx0 > 7:
                sh.text((bx0 + bx1) / 2, yc, f"{dur} j", h=1.7, ha="center", va="center", color="white",
                        weight="bold", z=6)
        sh.line([(xl, y0), (xr, y0)], lw="hair", color="#d0d0d0", z=1.6)
    # dependency arrows (finish -> start)
    for tid, t in S.items():
        for p in t["preds"]:
            pt = S[p]
            x0 = X(pt["end"]) + (dx if pt["dur"] else dx)
            y0 = ypos[p]
            x1 = X(t["start"]) + (dx if t["dur"] == 0 else 0)
            y1 = ypos[tid]
            critlink = pt["crit"] and t["crit"]
            colr = "#" + CRIT if critlink else "#7f7f7f"
            xm = max(x0 + 0.8, x1 - 0.8) if x1 - x0 > 1.6 else x0 + 0.8
            pts = [(x0, y0), (xm, y0), (xm, y1 + (rh * 0.36 if y1 < y0 else -rh * 0.36))]
            if x1 > xm + 0.4:
                pts = [(x0, y0), (xm, y0), (xm, y1), (x1, y1)]
            sh.line(pts, lw="hair", color=colr, z=4.5)
            ex, ey = pts[-1]
            if len(pts) == 4:
                ax.add_patch(mp.Polygon([(ex, ey), (ex - 1.0, ey + 0.5), (ex - 1.0, ey - 0.5)], closed=True,
                                        fc=colr, ec="none", zorder=4.6))
            else:
                sgn = -1 if y1 < y0 else 1
                ax.add_patch(mp.Polygon([(ex, ey), (ex - 0.5, ey - sgn * 1.0), (ex + 0.5, ey - sgn * 1.0)],
                                        closed=True, fc=colr, ec="none", zorder=4.6))
    sh.rect(xl, ybot, xr, ytop + 12, fc="none", ec=INK, lw="thin", z=9)
    for x in (xl + 6, xc - 63, xc - 48, xc - 29, xc - 12, xc):
        sh.line([(x, ybot), (x, ytop + (12 if x != xc else 12))], lw="fine", color=GREY, z=9)
    # legend
    lx, ly = 25, 82
    sh.text(lx, ly, "LÉGENDE", h=3.0, weight="bold", color=ACCENT)
    items = [("rect", "#" + PCOL["C"], "Tâche (couleur de sa phase)"), ("rect", "#" + CRIT, "Tâche critique (marge nulle)"),
             ("sum", "#262626", "Récapitulatif de phase"), ("dia", "#" + CRIT, "Jalon"),
             ("float", GREY, "Marge totale disponible"), ("link", "#7f7f7f", "Liaison fin → début (rouge si critique)"),
             ("rect", "#efefef", "Jour non ouvré (vendredi, samedi)")]
    for k, (kind, col, lab) in enumerate(items):
        cx = lx + (k % 4) * 95
        cy = ly - 8 - (k // 4) * 7
        if kind == "rect":
            sh.rect(cx, cy - 1.5, cx + 10, cy + 1.5, fc=col, ec=INK, lw="hair")
        elif kind == "sum":
            sh.rect(cx, cy - 0.8, cx + 10, cy + 0.8, fc=col, ec="none")
        elif kind == "dia":
            ax.add_patch(mp.Polygon([(cx + 5, cy + 2), (cx + 7, cy), (cx + 5, cy - 2), (cx + 3, cy)], closed=True,
                                    fc=col, ec=INK, lw=0.4, zorder=7))
        elif kind == "float":
            sh.line([(cx, cy), (cx + 10, cy)], lw="thin", color=col, ls="dot")
            sh.line([(cx + 10, cy - 1), (cx + 10, cy + 1)], lw="thin", color=col)
        else:
            sh.line([(cx, cy + 1.5), (cx + 4, cy + 1.5), (cx + 4, cy - 1.5), (cx + 10, cy - 1.5)], lw="thin", color=col)
        sh.text(cx + 13, cy, lab, h=2.2, va="center")
    sh.notes(25, 58, "HYPOTHÈSES", [
        "Équipe de gros œuvre de 6 à 8 ouvriers, sous-traitants pour les corps d'état secondaires ; jours fériés non "
        "déduits.",
        "Décoffrage du plancher ≥ 21 jours calendaires après coulage (BAEL) ; maçonnerie démarrée 3 jours après le "
        "coulage du plancher.",
        "Planning modifiable dans « Planning_travaux.xlsx » (durées, liaisons, date d'ODS, avancement).",
    ], h=2.2)
    pdf_path = os.path.join(OUT, "Planning_Gantt.pdf")
    with PdfPages(pdf_path) as pdf:
        sh.save(pdf, os.path.join(OUT, "png", "Planning_Gantt.png"), None, dpi=130)
    return pdf_path


if __name__ == "__main__":
    print(build_planning())
    print(build_gantt_pdf())
