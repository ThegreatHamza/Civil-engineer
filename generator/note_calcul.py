"""Note de calcul — structure en béton armé (PDF, A4). python3 generator/note_calcul.py"""
import datetime as dt
import io
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (CondPageBreak, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer,  # noqa: E402
                                Table, TableStyle)

import calc as C  # noqa: E402
import model as M  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "plans", "Note_de_calcul_structure.pdf")
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

NAVY = colors.HexColor("#1F3B57")
LIGHT = colors.HexColor("#EEF2F6")
OKC = colors.HexColor("#1E7B34")
ST = {
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.2, leading=13, alignment=TA_JUSTIFY, spaceAfter=4),
    "h1": ParagraphStyle("h1", fontName="DVB", fontSize=13.5, leading=17, textColor=NAVY, spaceBefore=8, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="DVB", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4),
    "eq": ParagraphStyle("eq", fontName="DV", fontSize=9, leading=13.2, leftIndent=4),
    "small": ParagraphStyle("small", fontName="DV", fontSize=7.8, leading=10, textColor=colors.HexColor("#555555")),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8, leading=10),
    "cellb": ParagraphStyle("cellb", fontName="DVB", fontSize=8, leading=10, textColor=colors.white),
    "title": ParagraphStyle("title", fontName="DVB", fontSize=24, leading=30, textColor=NAVY, alignment=TA_CENTER),
    "sub": ParagraphStyle("sub", fontName="DV", fontSize=12, leading=17, alignment=TA_CENTER),
}
W = A4[0] - 36 * mm


def n(x, d=2):
    return f"{x:,.{d}f}".replace(",", " ")


def p(t, s="body"):
    return Paragraph(t, ST[s])


def ok(cond):
    return '<font color="#1E7B34"><b>✓ vérifié</b></font>' if cond else '<font color="#C00000"><b>✗ non vérifié</b></font>'


def eq(lines):
    t = Table([[Paragraph("<br/>".join(lines), ST["eq"])]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 2, NAVY),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def table(head, rows, widths, bold_last=False, align="CENTER"):
    data = [[Paragraph(h, ST["cellb"]) for h in head]]
    for r in rows:
        data.append([Paragraph(str(c), ST["cell"]) for c in r])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    sty = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#A6A6A6")),
           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if bold_last:
        sty += [("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FFF2CC"))]
    t.setStyle(TableStyle(sty))
    return t


def fig(fn, w=170, h=60):
    buf = io.BytesIO()
    f = plt.figure(figsize=(w / 25.4, h / 25.4), dpi=200)
    fn(f)
    f.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(f)
    buf.seek(0)
    return Image(buf, width=w * mm, height=h * mm)


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5})


# ------------------------------------------------------------------ figures
def fig_grid(f):
    ax = f.add_axes([0.02, 0.05, 0.96, 0.9])
    ax.set_aspect("equal")
    ax.axis("off")
    for x, xl in zip(M.XA, M.XL):
        ax.plot([x, x], [-1.2, 9.2], color="#9b2c2c", lw=0.5, ls=(0, (8, 2, 1, 2)))
        ax.text(x, 9.6, xl, ha="center", va="center", color="#9b2c2c", fontweight="bold",
                bbox=dict(boxstyle="circle", fc="white", ec="#9b2c2c", lw=0.6))
    for y, yl in zip(M.YA, M.YL):
        ax.plot([-1.2, 16.2], [y, y], color="#9b2c2c", lw=0.5, ls=(0, (8, 2, 1, 2)))
        ax.text(-1.7, y, yl, ha="center", va="center", color="#9b2c2c", fontweight="bold",
                bbox=dict(boxstyle="circle", fc="white", ec="#9b2c2c", lw=0.6))
    cols = {"S1": "#8C5A2B", "S2": "#2E75B6", "S3": "#7F7F7F"}
    for x, y in M.COLUMNS:
        t = M.footing_type(x, y)
        a = M.FOOTINGS[t][0]
        ax.add_patch(plt.Rectangle((x - a / 2, y - a / 2), a, a, fc=cols[t], alpha=0.25, ec=cols[t], lw=0.8))
        ax.add_patch(plt.Rectangle((x - 0.15, y - 0.15), 0.3, 0.3, fc="#222222"))
        ax.text(x + 0.7, y + 0.35, f"{M.YL[M.YA.index(y)]}{M.XL[M.XA.index(x)]} · {t}", fontsize=6.5)
    for y in M.YA:
        ax.plot([0, 15], [y, y], color="#1F3B57", lw=2.2, alpha=0.5)
    for x in M.XA:
        ax.plot([x, x], [0, 8], color="#36506b", lw=1.4, alpha=0.4)
    for i in range(3):
        for j in range(2):
            cx, cy = (M.XA[i] + M.XA[i + 1]) / 2, (M.YA[j] + M.YA[j + 1]) / 2
            ax.annotate("", xy=(cx, cy + 0.9), xytext=(cx, cy - 0.9),
                        arrowprops=dict(arrowstyle="<->", color="#1F3B57", lw=0.8))
            ax.text(cx + 0.2, cy, "poutrelles", fontsize=6, color="#1F3B57", va="center")
    ax.text(7.5, -0.75, "PP 30×45 // X (axes A, B, C)   ·   PS 30×35 // Y (axes 1 à 4)   ·   "
            "semelles : S1 brun, S2 bleu, S3 gris", ha="center", fontsize=6.8)
    ax.set_xlim(-2.3, 16.6)
    ax.set_ylim(-1.3, 10.1)


def fig_poutrelle(f):
    ax = f.add_axes([0.08, 0.18, 0.9, 0.72])
    P = C.P
    lw, le, q, Ma = P["lw"], P["le"], P["qu"], P["Ma"]
    xs, ms = [], []
    for i in range(101):
        x = lw * i / 100
        xs.append(x)
        ms.append(q * x * (lw - x) / 2 - Ma * x / lw)
    for i in range(101):
        x = le * i / 100
        xs.append(lw + x)
        ms.append(q * x * (le - x) / 2 - Ma * (1 - x / le))
    ax.fill_between(xs, ms, color="#2E75B6", alpha=0.25)
    ax.plot(xs, ms, color="#1F3B57", lw=1)
    ax.axhline(0, color="black", lw=0.8)
    ax.invert_yaxis()
    ax.plot([P["x0"]], [P["Mt"]], "o", color="#C00000", ms=3)
    ax.annotate(f"Mt = {P['Mt']:.2f} kN·m", (P["x0"], P["Mt"]), xytext=(P["x0"] + 0.3, P["Mt"] + 1.5))
    ax.annotate(f"Ma = −{Ma:.2f} kN·m", (lw, -Ma), xytext=(lw + 0.25, -Ma + 1.0))
    for x in (0, lw, lw + le):
        ax.plot(x, 0, marker="^", color="black", ms=6, transform=ax.transData, clip_on=False)
    ax.set_xlabel("x (m) — portées entre nus : 4.70 m et 2.70 m")
    ax.set_ylabel("M (kN·m)")
    ax.set_title("Poutrelle continue à 2 travées — diagramme des moments ELU (méthode de Caquot)", fontsize=8)
    ax.grid(alpha=0.3)


def fig_pp(f):
    ax = f.add_axes([0.08, 0.18, 0.9, 0.72])
    B = C.PP["axes"]["B"]
    L = C.PP["L"]
    sup = [-B["Ma_rive"], -B["Ma_int"], -B["Ma_int"], -B["Ma_rive"]]
    tr = [B["Mt_rive"], B["Mt_int"], B["Mt_rive"]]
    xs, ms = [], []
    for k in range(3):
        mw, me, mt = sup[k], sup[k + 1], tr[k]
        mu = (mt - (mw + me) / 2) * 4 / L ** 2
        for i in range(101):
            x = L * i / 100
            xs.append(k * 5.0 + 0.15 + x)
            ms.append(mw * (1 - x / L) + me * x / L + mu * x * (L - x))
    ax.fill_between(xs, ms, color="#8C5A2B", alpha=0.22)
    ax.plot(xs, ms, color="#5c3a1b", lw=1)
    ax.axhline(0, color="black", lw=0.8)
    ax.invert_yaxis()
    for k, m in enumerate(tr):
        ax.annotate(f"{m:.1f}", (k * 5 + 2.5, m), ha="center", va="bottom", xytext=(0, 4), textcoords="offset points")
    for k, m in enumerate(sup):
        ax.annotate(f"{m:.1f}", (k * 5, m), ha="center", va="top", xytext=(0, -4), textcoords="offset points")
    for x in (0, 5, 10, 15):
        ax.plot(x, 0, marker="^", color="black", ms=6, clip_on=False)
    ax.set_xlabel("x (m) — axes 1 à 4")
    ax.set_ylabel("M (kN·m)")
    ax.set_title("Poutre principale PP (axe B) — moments ELU, méthode forfaitaire", fontsize=8)
    ax.grid(alpha=0.3)


# ------------------------------------------------------------------ page decoration
def on_page(canv, doc):
    canv.saveState()
    if doc.page > 1:
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(0.6)
        canv.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
        canv.setFont("DV", 7.5)
        canv.setFillColor(colors.HexColor("#555555"))
        canv.drawString(18 * mm, A4[1] - 12 * mm, "Habitation individuelle R.D.C — 15.00 × 8.00 m")
        canv.drawRightString(A4[0] - 18 * mm, A4[1] - 12 * mm, "NOTE DE CALCUL — STRUCTURE BÉTON ARMÉ — Indice A")
        canv.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canv.drawString(18 * mm, 10 * mm, "Bureau d'études · Architecture & Génie civil")
        canv.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canv.restoreState()


# ------------------------------------------------------------------ content
def build():
    P, PP, PS, COL, SEI, FOOT, LONG, ACRO = C.P, C.PP, C.PS, C.COL, C.SEI, C.FOOT, C.LONG, C.ACRO
    s = []
    # ---- cover
    s += [Spacer(1, 40 * mm), p("NOTE DE CALCUL", "title"), Spacer(1, 3 * mm),
          p("STRUCTURE EN BÉTON ARMÉ", "title"), Spacer(1, 10 * mm),
          p("Construction d'une habitation individuelle en rez-de-chaussée", "sub"),
          p("3 chambres · salon · cuisine · WC · hall — emprise 15.00 × 8.00 m (entre axes)", "sub"),
          Spacer(1, 14 * mm)]
    cov = [["Règlements", "BAEL 91 mod. 99 / CBA 93 · RPA 99 version 2003 · DTR B.C 2.2"],
           ["Système porteur", "Portiques autostables en béton armé avec remplissage en maçonnerie"],
           ["Plancher", "Corps creux 20 + 4 sur poutrelles, terrasse inaccessible"],
           ["Fondations", "Semelles isolées sous poteaux, reliées par des longrines"],
           ["Plans associés", "Planches 06 à 10 du dossier de plans (indice A)"],
           ["Date / indice", f"{dt.date(2026, 11, 21):%d/%m/%Y} — indice A"]]
    t = Table([[p(f"<b>{a}</b>", "cell"), p(b, "cell")] for a, b in cov], colWidths=[40 * mm, 120 * mm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#A6A6A6")),
                           ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    s += [t, Spacer(1, 14 * mm)]
    s.append(p("<b>Sommaire</b>", "h2"))
    toc = ["1. Présentation de l'ouvrage", "2. Règlements, matériaux et hypothèses", "3. Évaluation des charges",
           "4. Prédimensionnement des éléments", "5. Calcul du plancher (poutrelles, dalle de compression)",
           "6. Calcul des poutres (PP et PS)", "7. Descente de charges et calcul des poteaux",
           "8. Étude sismique (méthode statique équivalente)", "9. Calcul des fondations (semelles, longrines)",
           "10. Calcul de l'acrotère", "11. Récapitulatif des vérifications et du ferraillage"]
    s += [p(x) for x in toc]
    s.append(Spacer(1, 8 * mm))
    s.append(p("Les plans de structure de l'indice A ont été mis à jour suite à cette note : semelles de rive "
               "portées à 1.10 m, semelles d'angle S3, longrines en 3T14 + 3T14, poutrelles en 2T12, "
               "et espacement des cadres de 8 cm en zone nodale des poutres PS.", "small"))
    s.append(PageBreak())
    s.append(CondPageBreak(70 * mm))

    # ---- 1
    s.append(p("1. Présentation de l'ouvrage", "h1"))
    s.append(p("L'ouvrage est une habitation individuelle en rez-de-chaussée de 15.00 × 8.00 m entre axes "
               "(15.30 × 8.30 m hors tout), couverte par une terrasse inaccessible. La hauteur sous plafond est de "
               "3.00 m ; le dessus de la dalle est à +3.24 m et l'acrotère culmine à +3.90 m. Le sol fini est à "
               "+0.45 m au-dessus du terrain naturel."))
    s.append(p("La structure est constituée de 12 poteaux 30 × 30 implantés sur une trame de 3 × 2 travées "
               "(axes 1–4 espacés de 5.00 m, axes A–B–C espacés de 5.00 m et 3.00 m). Les poutres principales PP "
               "(// X) portent les poutrelles du plancher ; les poutres secondaires PS (// Y) assurent le "
               "chaînage et le contreventement dans l'autre direction."))
    s.append(fig(fig_grid, 165, 95))
    s.append(p("Figure 1 — Trame structurelle, sens de portée des poutrelles et repérage des semelles.", "small"))

    # ---- 2
    s.append(CondPageBreak(55 * mm))
    s.append(p("2. Règlements, matériaux et hypothèses", "h1"))
    s.append(table(["Caractéristique", "Valeur", "Référence"], [
        ["Béton : résistance caractéristique fc28", f"{C.FC28:.0f} MPa", "C25/30, 350 kg/m³ CPJ 42.5"],
        ["Béton : résistance à la traction ft28 = 0.6 + 0.06 fc28", f"{C.FT28:.2f} MPa", "BAEL A.2.1.12"],
        ["Béton : fbu = 0.85 fc28 / (θ γb), γb = 1.5", f"{C.FBU:.2f} MPa", "BAEL A.4.3.41"],
        ["Béton : contrainte limite ELS σbc = 0.6 fc28", f"{C.SBC:.0f} MPa", "BAEL A.4.5.2"],
        ["Module d'Young instantané Eij = 11 000 fc28^(1/3)", f"{n(C.EIJ, 0)} MPa", "BAEL A.2.1.21"],
        ["Acier HA FeE400 : fe", f"{C.FE:.0f} MPa", "γs = 1.15"],
        ["Acier : fsu = fe / γs", f"{C.FSU:.1f} MPa", "BAEL A.4.3.2"],
        ["Acier : σs ELS (fissuration préjudiciable)", f"{C.SS_PREJ:.1f} MPa", "BAEL A.4.5.33, η = 1.6"],
        ["Contrainte admissible du sol", f"{C.SIGMA_SOL / 100:.2f} bar", "Hypothèse — à confirmer par étude de sol"],
        ["Enrobages", "5 cm (fondations) · 3 cm (poteaux, poutres) · 2 cm (dalles)", "BAEL A.7.1"],
        ["Zone sismique / groupe d'usage / site", "IIa / 2 / S3 (meuble)", "RPA 99 v2003 — hypothèses"],
    ], [72, 48, 54]))
    s.append(Spacer(1, 3 * mm))
    s.append(p("Fissuration peu préjudiciable pour la superstructure (éléments protégés), préjudiciable pour les "
               "fondations et l'acrotère. Combinaisons d'actions : ELU = 1.35 G + 1.5 Q ; ELS = G + Q ; "
               "accidentelles (RPA 5.2) : G + Q ± E et 0.8 G ± E."))

    # ---- 3
    s.append(CondPageBreak(55 * mm))
    s.append(p("3. Évaluation des charges", "h1"))
    s.append(p("3.1 Plancher terrasse inaccessible (DTR B.C 2.2)", "h2"))
    rows, tot = C.terrace_loads()
    s.append(table(["Couche", "Épaisseur (m)", "Poids volumique (kN/m³)", "G (kN/m²)"],
                   [[a, n(e) if e else "—", n(g, 0) if g else "—", n(v)] for a, e, g, v in rows] +
                   [["<b>Total calculé</b>", "", "", f"<b>{n(tot)}</b>"],
                    ["<b>Valeur retenue (arrondie)</b>", "", "", f"<b>G = {n(C.G_T)} · Q = {n(C.Q_T)}</b>"]],
                   [86, 26, 36, 26], bold_last=True))
    s.append(eq([f"q<sub>u</sub> = 1.35 G + 1.5 Q = 1.35 × {n(C.G_T)} + 1.5 × {n(C.Q_T)} = <b>{n(C.PU_S, 3)} kN/m²</b>",
                 f"q<sub>s</sub> = G + Q = <b>{n(C.PS_S)} kN/m²</b>"]))
    s.append(p("3.2 Murs et acrotère", "h2"))
    s.append(table(["Élément", "Composition", "G"], [
        ["Mur extérieur double cloison", " + ".join(f"{a} ({n(v)})" for a, v in C.EXT_WALL), f"{n(C.G_EXT)} kN/m²"],
        ["Cloison intérieure", " + ".join(f"{a} ({n(v)})" for a, v in C.INT_WALL), f"{n(C.G_INT)} kN/m²"],
        ["Acrotère 10 × 60", "0.10 × 0.60 × 25 + couvertine 0.10", f"{n(C.ACRO_G)} kN/m"],
    ], [42, 104, 28]))
    s.append(p("Les murs du rez-de-chaussée reposent sur les longrines et transmettent directement leur charge "
               "aux semelles ; ils ne chargent pas les poutres du plancher. Les cloisons intérieures non situées "
               "sur un axe (cuisine, WC, salon) reposent sur le dallage."))

    # ---- 4
    s.append(CondPageBreak(55 * mm))
    s.append(p("4. Prédimensionnement", "h1"))
    s.append(table(["Élément", "Critère", "Calcul", "Retenu"], [
        ["Plancher corps creux", "h<sub>t</sub> ≥ L / 22.5 (L = 4.70 m entre nus)", f"{n(4.70 / 22.5, 3)} m",
         "20 + 4 = 0.24 m"],
        ["Poutres PP (L = 5.00 m)", "L/15 ≤ h ≤ L/10 ; RPA : b ≥ 20, h ≥ 30, h/b ≤ 4", "0.33 ≤ h ≤ 0.50 m",
         "30 × 45 cm"],
        ["Poutres PS (L = 5.00 m)", "chaînage, RPA : b ≥ 20, h ≥ 30", "h ≥ 0.30 m", "30 × 35 cm"],
        ["Poteaux", "RPA zone IIa : min(b, h) ≥ 25 cm ; ≥ he / 20", f"he / 20 = {n(COL['rpa']['he20'], 3)} m",
         "30 × 30 cm"],
        ["Semelles", "A ≥ N<sub>ser</sub> / σ<sub>sol</sub> ; rigidité d ≥ (A − a) / 4", "voir § 9",
         "S1 1.20 · S2 1.10 · S3 1.00"],
    ], [33, 62, 38, 41]))

    # ---- 5
    s.append(CondPageBreak(70 * mm))
    s.append(p("5. Calcul du plancher", "h1"))
    s.append(p("5.1 Poutrelles — sollicitations", "h2"))
    s.append(p(f"Les poutrelles (entraxe {n(P['b'])} m) portent dans le sens Y et sont continues sur deux travées "
               f"(4.70 m et 2.70 m entre nus). Le rapport des portées vaut {n(P['lw'] / P['le'])} &gt; 1.25 : la "
               "méthode forfaitaire n'est pas applicable, on utilise la <b>méthode de Caquot</b> (BAEL annexe E.2)."))
    s.append(eq([f"q<sub>u</sub> = {n(C.PU_S, 3)} × {n(P['b'])} = <b>{n(P['qu'])} kN/m</b> ;   "
                 f"q<sub>s</sub> = {n(C.PS_S)} × {n(P['b'])} = {n(P['qs'])} kN/m",
                 f"M<sub>a</sub> = q (l'<sub>w</sub>³ + l'<sub>e</sub>³) / [8.5 (l'<sub>w</sub> + l'<sub>e</sub>)] = "
                 f"{n(P['qu'])} × ({n(P['lw'])}³ + {n(P['le'])}³) / [8.5 × {n(P['lw'] + P['le'])}] = "
                 f"<b>{n(P['Ma'])} kN·m</b>",
                 f"x<sub>0</sub> = l/2 − M<sub>a</sub> / (q l) = {n(P['x0'], 3)} m  →  "
                 f"M<sub>t</sub> = q x<sub>0</sub> (l − x<sub>0</sub>) / 2 − M<sub>a</sub> x<sub>0</sub> / l = "
                 f"<b>{n(P['Mt'])} kN·m</b>   (M<sub>0</sub> = {n(P['M0'])} kN·m)",
                 f"Efforts tranchants : V<sub>A</sub> = {n(P['Vw'])} kN ; V<sub>B,g</sub> = {n(P['Vb1'])} kN ; "
                 f"V<sub>B,d</sub> = {n(P['Vb2'])} kN ; V<sub>C</sub> = {n(P['Ve'])} kN"]))
    s.append(fig(fig_poutrelle, 165, 58))
    s.append(p("5.2 Poutrelles — ferraillage", "h2"))
    s.append(p(f"Section en T : b = {n(P['b'])} m, b<sub>0</sub> = {n(P['b0'])} m, h = {n(P['h'])} m, "
               f"h<sub>0</sub> = {n(P['h0'])} m, d = 0.9 h = {n(P['d'], 3)} m."))
    ft, fa = P["ft"], P["fa"]
    s.append(eq([f"Moment de la table : M<sub>tu</sub> = f<sub>bu</sub> b h<sub>0</sub> (d − h<sub>0</sub>/2) = "
                 f"{n(P['Mtu_table'], 1)} kN·m &gt; M<sub>t</sub> → l'axe neutre est dans la table : section "
                 f"rectangulaire b × h",
                 f"<b>Travée</b> : μ = M<sub>t</sub> / (b d² f<sub>bu</sub>) = {n(ft['mu'], 4)} &lt; μ<sub>l</sub> = 0.392 ; "
                 f"α = {n(ft['alpha'], 4)} ; z = {n(ft['z'], 4)} m ; "
                 f"A = M / (z f<sub>su</sub>) = <b>{n(ft['As'])} cm²</b>  →  <b>2T12 = {n(P['A_t'])} cm²</b> "
                 f"{ok(P['A_t'] >= ft['As'])}",
                 f"<b>Appui B</b> (table tendue, section b<sub>0</sub> × h) : μ = {n(fa['mu'], 4)} ; z = {n(fa['z'], 4)} m ; "
                 f"A = <b>{n(fa['As'])} cm²</b>  →  chapeau <b>2T12 = {n(P['A_a'])} cm²</b> {ok(P['A_a'] >= fa['As'])}",
                 f"Condition de non-fragilité : A<sub>min</sub> = 0.23 b<sub>0</sub> d f<sub>t28</sub> / f<sub>e</sub> = "
                 f"{n(P['Amin'])} cm² {ok(P['A_t'] >= P['Amin'])}"]))
    sh = P["sh"]
    s.append(eq([f"<b>Effort tranchant</b> : τ<sub>u</sub> = V<sub>max</sub> / (b<sub>0</sub> d) = "
                 f"{n(max(P['Vb1'], P['Vb2']) / 1000 / (P['b0'] * P['d']), 3)} MPa ≤ "
                 f"τ̄<sub>u</sub> = min(0.2 f<sub>c28</sub>/γ<sub>b</sub> ; 5 MPa) = {n(sh['tau_lim'])} MPa "
                 f"{ok(sh['tau'] <= sh['tau_lim'])}",
                 f"Étriers Ø6 (2 brins, A<sub>t</sub> = {n(sh['At'])} cm²) : A<sub>t</sub> requis = {n(sh['At_need'], 3)} cm² "
                 f"pour s<sub>t</sub> = 15 cm ≤ min(0.9 d ; 40 cm) = {n(sh['st_max'] * 100, 1)} cm "
                 f"{ok(sh['At'] >= sh['At_need'] and 0.15 <= sh['st_max'])}",
                 f"<b>ELS</b> : σ<sub>bc</sub> = {n(P['sig'])} MPa ≤ 15 MPa {ok(P['sig'] <= 15)}"]))
    s.append(p("Vérification de la flèche (BAEL B.6.5.1) — si les trois conditions sont satisfaites, le calcul de "
               "la flèche n'est pas nécessaire :"))
    s.append(table(["Condition", "Valeur", "Limite", "Résultat"],
                   [[a, n(v, 4), n(lim, 4), ok(v <= lim if "≤" in a else v >= lim)] for a, v, lim in P["fl"]],
                   [62, 34, 34, 44]))
    s.append(p("5.3 Dalle de compression", "h2"))
    s.append(eq([f"Armatures ⊥ aux poutrelles : A<sub>⊥</sub> ≥ 4 l / f<sub>e</sub> = 4 × 65 / 520 = "
                 f"{n(P['A_perp'])} cm²/ml ; armatures // : A<sub>//</sub> ≥ A<sub>⊥</sub> / 2 = {n(P['A_par'])} cm²/ml",
                 f"Treillis soudé TS Ø6 maille 20 × 20 : 5 Ø6 = {n(P['A_ts'])} cm²/ml dans les deux sens "
                 f"{ok(P['A_ts'] >= P['A_perp'])}"]))

    # ---- 6
    s.append(CondPageBreak(70 * mm))
    s.append(p("6. Calcul des poutres", "h1"))
    s.append(p("6.1 Poutres principales PP 30 × 45", "h2"))
    B = PP["axes"]["B"]
    s.append(p("Les PP reçoivent les réactions d'appui des poutrelles (par mètre linéaire : réaction / 0.65 m), "
               "leur poids propre et, en rive, l'acrotère. Poutre continue à 3 travées égales de 5.00 m "
               "(4.70 m entre nus), Q ≤ 2G, inerties constantes : <b>méthode forfaitaire</b> (BAEL B.6.2.21)."))
    s.append(table(["Axe", "p<sub>u</sub> (kN/m)", "p<sub>s</sub> (kN/m)", "M<sub>0</sub> (kN·m)",
                    "M<sub>t</sub> rive (kN·m)", "M<sub>t</sub> interm. (kN·m)", "M<sub>a</sub> interm. (kN·m)",
                    "V<sub>u</sub> (kN)"],
                   [[k, n(v["pu"]), n(v["ps"]), n(v["M0"], 1), n(v["Mt_rive"], 1), n(v["Mt_int"], 1),
                     n(v["Ma_int"], 1), n(v["Vu"], 1)] for k, v in PP["axes"].items()],
                   [12, 21, 21, 22, 24, 26, 26, 22]))
    s.append(eq([f"Axe B (le plus chargé) : α = Q / (G + Q) = {n(B['alpha'], 3)} ; "
                 f"M<sub>0</sub> = p<sub>u</sub> L² / 8 = {n(B['pu'])} × {n(PP['L'])}² / 8 = <b>{n(B['M0'], 1)} kN·m</b>",
                 f"Appuis intermédiaires : M<sub>a</sub> = 0.5 M<sub>0</sub> = <b>{n(B['Ma_int'], 1)} kN·m</b> ; "
                 f"appuis de rive : 0.15 M<sub>0</sub> = {n(B['Ma_rive'], 1)} kN·m",
                 f"Travée de rive : M<sub>t</sub> ≥ max[(1 + 0.3α) ; 1.05] M<sub>0</sub> − (M<sub>w</sub> + M<sub>e</sub>)/2 "
                 f"et ≥ (1.2 + 0.3α) M<sub>0</sub> / 2  →  <b>M<sub>t</sub> = {n(B['Mt_rive'], 1)} kN·m</b>",
                 f"Effort tranchant (1<sup>er</sup> appui intermédiaire) : V<sub>u</sub> = 1.15 p<sub>u</sub> L / 2 = "
                 f"<b>{n(B['Vu'], 1)} kN</b>"]))
    s.append(fig(fig_pp, 165, 55))
    ft, fa = PP["ft"], PP["fa"]
    s.append(eq([f"<b>Travée</b> (d = {n(PP['d'])} m, 2 lits) : μ = {n(ft['mu'], 4)} ; α = {n(ft['alpha'], 4)} ; "
                 f"z = {n(ft['z'], 4)} m ; A = <b>{n(ft['As'])} cm²</b>  →  <b>3T16 filants + 3T16 renfort = "
                 f"{n(PP['A_bot'])} cm²</b> {ok(PP['A_bot'] >= ft['As'])}",
                 f"<b>Appui intermédiaire</b> (d = 0.405 m) : μ = {n(fa['mu'], 4)} ; A = <b>{n(fa['As'])} cm²</b>  →  "
                 f"<b>3T14 filants + 3T14 chapeaux = {n(PP['A_top_sup'])} cm²</b> {ok(PP['A_top_sup'] >= fa['As'])}",
                 f"Axe A (rive) : M<sub>t</sub> = {n(PP['axes']['A']['Mt_rive'], 1)} kN·m → A = {n(PP['A_A']['As'])} cm² : "
                 "le ferraillage de l'axe B est généralisé à toutes les PP (unification).",
                 f"Non-fragilité : A<sub>min</sub> = {n(PP['Amin'])} cm² ; RPA 7.5.2.1 : A<sub>tot</sub> ≥ 0.5 % b h = "
                 f"{n(PP['rpa']['Amin'])} cm² (3T16 + 3T14 filants = {n(PP['rpa']['A_tot'])} cm²) "
                 f"{ok(PP['rpa']['A_tot'] >= PP['rpa']['Amin'])}"]))
    sh = PP["sh"]
    s.append(eq([f"<b>ELS</b> : M<sub>ser</sub> = {n(B['Mts'], 1)} kN·m → σ<sub>bc</sub> = {n(PP['sig'])} MPa ≤ 15 MPa "
                 f"{ok(PP['sig'] <= 15)}",
                 f"<b>Effort tranchant</b> : τ<sub>u</sub> = {n(sh['tau'], 3)} MPa ≤ {n(sh['tau_lim'])} MPa "
                 f"{ok(sh['tau'] <= sh['tau_lim'])} ; cadre + étrier T8 (4 brins = {n(sh['At'])} cm²) ≥ "
                 f"{n(sh['At_need'])} cm² pour s<sub>t</sub> = 15 cm {ok(sh['At'] >= sh['At_need'])}",
                 f"RPA 7.5.2.2 : zone nodale s<sub>t</sub> ≤ min(h/4 ; 12 Ø<sub>l</sub>) = "
                 f"{n(PP['rpa']['st_nod'] * 100, 1)} cm → <b>10 cm</b> ; zone courante s<sub>t</sub> ≤ h/2 = "
                 f"{n(PP['rpa']['st_cour'] * 100, 1)} cm → <b>15 cm</b> ; A<sub>t</sub> ≥ 0.003 s<sub>t</sub> b = "
                 f"{n(PP['rpa']['At_min'])} cm² {ok(sh['At'] >= PP['rpa']['At_min'])}"]))
    s.append(table(["Condition de flèche", "Valeur", "Limite", "Résultat"],
                   [[a, n(v, 4), n(lim, 4), ok(v <= lim if "≤" in a else v >= lim)] for a, v, lim in PP["fl"]],
                   [62, 34, 34, 44]))
    s.append(p("6.2 Poutres secondaires PS 30 × 35", "h2"))
    s.append(p("Les PS sont parallèles aux poutrelles : elles reçoivent leur poids propre, une bande de plancher "
               f"de {n(C.P['b'])} m et l'acrotère en rive. Poutre continue à 2 travées (4.70 et 2.70 m entre nus), "
               "méthode de Caquot."))
    s.append(eq([f"G = {n(PS['G'])} kN/m ; Q = {n(PS['Q'])} kN/m ; p<sub>u</sub> = <b>{n(PS['pu'])} kN/m</b>",
                 f"M<sub>a</sub> = <b>{n(PS['Ma'])} kN·m</b> ; M<sub>t</sub> = <b>{n(PS['Mt'])} kN·m</b> ; "
                 f"V<sub>u</sub> = {n(PS['V'])} kN",
                 f"Travée : A = {n(PS['ft']['As'])} cm² → <b>3T14 = {n(PS['A_bot'])} cm²</b> "
                 f"{ok(PS['A_bot'] >= PS['ft']['As'])} ; appui : A = {n(PS['fa']['As'])} cm² → "
                 f"<b>3T12 + 2T12 = {n(PS['A_top'])} cm²</b> {ok(PS['A_top'] >= PS['fa']['As'])}",
                 f"RPA : A<sub>tot</sub> ≥ 0.5 % b h = {n(PS['rpa']['Amin'])} cm² (filants 3T14 + 3T12 = "
                 f"{n(PS['rpa']['A_tot'])} cm²) {ok(PS['rpa']['A_tot'] >= PS['rpa']['Amin'])}",
                 f"τ<sub>u</sub> = {n(PS['sh']['tau'], 3)} MPa {ok(PS['sh']['tau'] <= PS['sh']['tau_lim'])} ; "
                 f"zone nodale s<sub>t</sub> ≤ min(h/4 ; 12 Ø<sub>l</sub>) = {n(PS['rpa']['st_nod'] * 100, 2)} cm → "
                 "<b>8 cm</b> ; zone courante ≤ h/2 → <b>15 cm</b> ; cadre T8 + épingle"]))

    # ---- 7
    s.append(CondPageBreak(70 * mm))
    s.append(p("7. Descente de charges et calcul des poteaux", "h1"))
    s.append(p("Méthode des surfaces d'influence. Les charges du plancher sont majorées pour la continuité : "
               "× 1.15 sur l'appui intermédiaire des poutrelles (2 travées, axe B) et × 1.10 sur les premiers "
               "appuis intermédiaires des PP (axes 2 et 3). Les longrines apportent leur poids et celui des murs "
               "directement aux semelles."))
    w = COL["worst"]
    s.append(p(f"7.1 Détail pour le poteau le plus chargé ({w['name']})", "h2"))
    s.append(table(["Charge", "G (kN)", "Q (kN)"],
                   [[a, n(g), n(q)] for a, g, q in w["rows"]] +
                   [["<b>Total en pied de poteau</b>", f"<b>{n(sum(r[1] for r in w['rows']))}</b>",
                     f"<b>{n(sum(r[2] for r in w['rows']))}</b>"]] +
                   [[a, n(g), n(q)] for a, g, q in w["rows2"]] +
                   [["<b>Total au niveau de la semelle</b>",
                     f"<b>{n(sum(r[1] for r in w['rows'] + w['rows2']))}</b>",
                     f"<b>{n(sum(r[2] for r in w['rows'] + w['rows2']))}</b>"]],
                   [100, 37, 37]))
    s.append(eq([f"Surface d'influence : {n(w['area'])} m², coefficient de continuité {n(w['k'])}",
                 f"N<sub>u</sub> (poteau) = 1.35 G + 1.5 Q = <b>{n(w['Ncol_u'], 1)} kN</b> ; "
                 f"N<sub>ser</sub> (poteau) = <b>{n(w['Ncol_s'], 1)} kN</b> ; "
                 f"N<sub>ser</sub> (sur semelle) = <b>{n(w['Nf_s'], 1)} kN</b>"]))
    s.append(p("7.2 Tableau de la descente de charges (12 poteaux)", "h2"))
    s.append(table(["Pot.", "S infl. (m²)", "k", "N<sub>u</sub> poteau (kN)", "N<sub>ser</sub> poteau (kN)",
                    "N<sub>ser</sub> semelle (kN)", "N<sub>u</sub> semelle (kN)", "Semelle"],
                   [[r["name"], n(r["area"]), n(r["k"]), n(r["Ncol_u"], 1), n(r["Ncol_s"], 1), n(r["Nf_s"], 1),
                     n(r["Nf_u"], 1), r["type"]] for r in C.DESC], [15, 20, 12, 24, 24, 26, 25, 18]))
    s.append(p("7.3 Vérification du poteau à la compression centrée (BAEL B.8.4)", "h2"))
    s.append(eq([f"l<sub>0</sub> = {n(COL['l0'])} m (dessus longrine → dessus dalle) ; l<sub>f</sub> = 0.7 l<sub>0</sub> = "
                 f"{n(COL['lf'])} m ; λ = l<sub>f</sub> √12 / a = <b>{n(COL['lam'], 1)}</b> &lt; 50",
                 f"α = 0.85 / [1 + 0.2 (λ/35)²] = {n(COL['alpha'], 3)} ; B<sub>r</sub> = (a − 2 cm)² = "
                 f"{n(COL['Br'], 4)} m² ; A = 8T12 = {n(COL['A'])} cm²",
                 f"N<sub>u,lim</sub> = α [B<sub>r</sub> f<sub>c28</sub> / (0.9 γ<sub>b</sub>) + A f<sub>e</sub> / γ<sub>s</sub>] = "
                 f"<b>{n(COL['Nlim'], 0)} kN</b> ≥ N<sub>u</sub> = {n(w['Ncol_u'], 1)} kN "
                 f"{ok(COL['Nlim'] >= w['Ncol_u'])}",
                 f"RPA 7.4.3.1 — effort normal réduit : ν = N<sub>d</sub> / (B<sub>c</sub> f<sub>c28</sub>) = "
                 f"{n(COL['nu'], 3)} ≤ 0.30 {ok(COL['nu'] <= 0.30)}",
                 f"RPA 7.4.2.1 : A<sub>min</sub> = 0.8 % = {n(COL['rpa']['Amin'])} cm² ≤ 8T12 = {n(COL['A'])} cm² ≤ "
                 f"A<sub>max</sub> = 4 % = {n(COL['rpa']['Amax'])} cm² {ok(COL['rpa']['Amin'] <= COL['A'])}",
                 f"Armatures transversales (RPA 7.4.2.2) : zone nodale t ≤ min(10 Ø<sub>l</sub> ; 15 cm) = "
                 f"{n(COL['rpa']['t_nod'], 0)} cm → <b>10 cm</b> ; zone courante t ≤ 15 Ø<sub>l</sub> = "
                 f"{n(COL['rpa']['t_cour'], 0)} cm → <b>15 cm</b> ; λ<sub>g</sub> = {n(COL['rpa']['lam_g'], 1)} ≥ 5 → "
                 f"A<sub>t</sub> ≥ 0.3 % t b = {n(COL['At_min'])} cm² ; cadre + losange T8 = {n(COL['At'])} cm² "
                 f"{ok(COL['At'] >= COL['At_min'])}"]))

    # ---- 8
    s.append(CondPageBreak(70 * mm))
    s.append(p("8. Étude sismique — méthode statique équivalente (RPA 99 v2003, § 4.2)", "h1"))
    s.append(p("Le bâtiment est régulier en plan et en élévation, de hauteur inférieure à 23 m en zone IIa : "
               "la méthode statique équivalente est applicable (RPA 4.1.2)."))
    s.append(table(["Paramètre", "Valeur", "Justification"], [
        ["A — coefficient d'accélération", n(SEI["A"]), "Zone IIa, groupe d'usage 2 (tableau 4.1)"],
        ["R — coefficient de comportement", n(SEI["R"], 1), "Portiques autostables avec remplissage rigide (4.3)"],
        ["Q — facteur de qualité", n(SEI["Q"]), "1 + Σ P<sub>q</sub> (hypothèse prudente)"],
        ["ξ — amortissement / η", f"{n(SEI['xi'], 0)} % / {n(SEI['eta'], 3)}", "η = √(7 / (2 + ξ)) ≥ 0.7"],
        ["T — période (C<sub>T</sub> h<sub>N</sub><sup>3/4</sup>)",
         f"{n(SEI['T'], 3)} s", f"C<sub>T</sub> = {SEI['CT']}, h<sub>N</sub> = {n(SEI['hN'])} m"],
        ["D — facteur d'amplification", n(SEI["D"], 3), f"T ≤ T<sub>2</sub> = {SEI['T2']} s (site S3) : D = 2.5 η"],
    ], [58, 30, 86]))
    s.append(Spacer(1, 3 * mm))
    s.append(table(["Poids sismique W", "kN"], [[a, n(v, 1)] for a, v in SEI["Wrows"]] +
                   [["Charges d'exploitation β Q S (β = 0.20)", n(SEI["WQ"], 1)],
                    ["<b>W total</b>", f"<b>{n(SEI['W'], 1)}</b>"]], [130, 44], bold_last=True))
    nm = C.column_NM(0.8 * min(r["Ncol_s"] for r in C.DESC), SEI["Mc"])
    s.append(eq([f"V = A D Q W / R = {n(SEI['A'])} × {n(SEI['D'], 3)} × {n(SEI['Q'])} × {n(SEI['W'], 1)} / {n(SEI['R'], 1)} = "
                 f"<b>{n(SEI['V'], 1)} kN</b> ({n(SEI['V'] / SEI['W'] * 100, 1)} % de W), dans chaque direction",
                 f"Répartition sur les 12 poteaux (rigidités égales) : V<sub>i</sub> = {n(SEI['Vc'], 2)} kN ; "
                 f"M = V<sub>i</sub> h<sub>e</sub> / 2 = <b>{n(SEI['Mc'], 2)} kN·m</b> (h<sub>e</sub> = {n(SEI['he'])} m)",
                 f"Poteau sous 0.8 G ± E (N = {n(0.8 * min(r['Ncol_s'] for r in C.DESC), 1)} kN, 3T12 par face, "
                 f"γ<sub>b</sub> = 1.15, γ<sub>s</sub> = 1) : M<sub>R</sub> = <b>{n(nm['MR'], 1)} kN·m</b> ≥ "
                 f"{n(SEI['Mc'], 2)} kN·m {ok(nm['MR'] >= SEI['Mc'])}",
                 f"Rigidité d'un poteau k = 12 E I / h<sub>e</sub>³ = {n(SEI['kcol'], 0)} kN/m ; "
                 f"δ<sub>e</sub> = {n(SEI['delta_e'] * 1000, 2)} mm ; δ<sub>k</sub> = R δ<sub>e</sub> = "
                 f"<b>{n(SEI['delta_k'] * 1000, 2)} mm</b> ≤ 1 % h<sub>e</sub> = {n(SEI['he'] * 10, 1)} mm "
                 f"{ok(SEI['delta_k'] <= SEI['he'] / 100)}",
                 f"Effet P-Δ : θ = W Δ / (V h) = {n(SEI['theta'], 4)} ≤ 0.10 → négligeable {ok(SEI['theta'] <= 0.1)}"]))
    s.append(p("La rigidité apportée par la maçonnerie de remplissage, négligée ici, réduit encore les "
               "déplacements. Le calcul est conservatif pour les poteaux (rigidités égales, sans contribution "
               "des remplissages)."))

    # ---- 9
    s.append(CondPageBreak(70 * mm))
    s.append(p("9. Calcul des fondations", "h1"))
    s.append(p("9.1 Dimensionnement des semelles isolées", "h2"))
    s.append(p(f"Fond de fouille à {n(M.Z_PROP)} m / ±0.00 (≈ 1.15 m sous le TN), béton de propreté 10 cm. "
               "La contrainte sous la semelle est calculée à l'ELS avec le poids propre de la semelle et des terres "
               f"qui la surmontent (γ = {n(C.GAMMA_SOIL, 0)} kN/m³) :  σ = (N<sub>ser</sub> + P<sub>sem</sub> + "
               f"P<sub>terre</sub>) / A² ≤ σ<sub>sol</sub> = {n(C.SIGMA_SOL, 0)} kPa."))
    s.append(table(["Pot.", "Type", "A (m)", "N<sub>ser</sub> (kN)", "P<sub>sem</sub> (kN)", "P<sub>terre</sub> (kN)",
                    "N total (kN)", "σ (kPa)", "Résultat"],
                   [[r["name"], r["type"], n(r["a"]), n(r["Nf_s"], 1), n(r["self_f"], 1), n(r["soil"], 1),
                     n(r["Nser_tot"], 1), n(r["sigma"], 1), ok(r["sigma"] <= C.SIGMA_SOL)] for r in C.DESC],
                   [14, 11, 13, 20, 19, 19, 20, 17, 32]))
    a2 = next(r for r in C.DESC if r["name"] == "A2")
    zt = M.Z_SEM_BOT + 0.35
    s_old = (a2["Nf_s"] + 1.0 * 0.35 * C.GAMMA_BA + (1.0 - 0.09) * (M.Z_TN - zt) * C.GAMMA_SOIL) / 1.0
    s.append(p(f"Note : avec des semelles de 1.00 m sous les poteaux de rive (A2, A3), la contrainte atteindrait "
               f"{n(s_old, 1)} kPa &gt; 200 kPa ; les semelles de rive S2 sont donc portées à 1.10 m.", "small"))
    s.append(p("9.2 Ferraillage des semelles (méthode des bielles, BAEL / DTU 13.12)", "h2"))
    rows = []
    for t, f in FOOT.items():
        w = f["worst"]
        rows.append([t, f"{n(f['a'])} × {n(f['a'])} × {n(f['hs'])}", ", ".join(f["cols"]), n(w["Nf_s"], 1),
                     f"{n(f['rigid'], 3)} ≤ {n(f['d'])}", n(f["A_need"]), f"{f['n']} T12 = {n(f['A'])}",
                     ok(f["A"] >= f["A_need"] and f["d"] >= f["rigid"])])
    s.append(table(["Type", "A × A × h (m)", "Poteaux", "N<sub>ser</sub> max (kN)", "(A−a)/4 ≤ d (m)",
                    "A requis (cm²)", "A prévu / sens (cm²)", "Résultat"], rows, [12, 25, 36, 19, 23, 17, 24, 18]))
    s.append(eq(["A<sub>s</sub> = N<sub>ser</sub> (A − a) / (8 d σ̄<sub>s</sub>) dans chaque direction, "
                 f"σ̄<sub>s</sub> = {n(C.SS_PREJ, 1)} MPa (fissuration préjudiciable)",
                 "Semelles rigides : d ≥ (A − a) / 4 ; ancrage des barres par crochets à 90° (l<sub>s</sub> = 40 Ø)."]))
    s.append(p("9.3 Longrines 30 × 40 (RPA 99 v2003, § 10.1.1)", "h2"))
    s.append(eq([f"Traction : F = N / α ≥ 20 kN avec α = 15 (zone IIa, site S3) : N<sub>max</sub> / 15 = "
                 f"{n(LONG['Nmax'] / 15, 1)} kN → F = {n(LONG['F'], 1)} kN → A = F / f<sub>su</sub> = "
                 f"{n(LONG['A_trac'])} cm²",
                 f"Flexion sous le mur extérieur : q<sub>u</sub> = {n(LONG['q'])} kN/m, L<sub>max</sub> = {n(LONG['L'])} m, "
                 f"M<sub>u</sub> = q L² / 10 = {n(LONG['Mu'])} kN·m → A = {n(LONG['f']['As'])} cm² par face",
                 f"Pourcentage minimal RPA : 0.6 % B = <b>{n(LONG['Amin'])} cm²</b> → <b>3T14 + 3T14 = {n(LONG['A'])} cm²</b> "
                 f"{ok(LONG['A'] >= LONG['Amin'])}",
                 f"Cadres T8, s<sub>t</sub> ≤ min(20 cm ; 15 Ø<sub>l</sub>) → <b>20 cm</b> ; longueur totale nette : "
                 f"{n(LONG['Ltot'], 1)} m"]))

    # ---- 10
    s.append(CondPageBreak(55 * mm))
    s.append(p("10. Calcul de l'acrotère", "h1"))
    s.append(eq([f"Console encastrée dans la poutre de rive, h = {n(ACRO['h'])} m, e = {n(ACRO['e'])} m ; "
                 f"W<sub>p</sub> = {n(ACRO['Wp'])} kN/ml",
                 f"Force sismique RPA 6.2.3 : F<sub>p</sub> = 4 A C<sub>p</sub> W<sub>p</sub> = 4 × 0.15 × 0.8 × "
                 f"{n(ACRO['Wp'])} = {n(ACRO['Fp'])} kN/ml ; main courante Q = 1.00 kN/ml → F = {n(ACRO['Fh'])} kN/ml",
                 f"M<sub>u</sub> = 1.5 F h = {n(ACRO['Mu'])} kN·m/ml ; N<sub>u</sub> = {n(ACRO['Nu'])} kN/ml ; "
                 f"A calculé = {n(ACRO['f']['As'], 3)} cm²/ml ; A<sub>min</sub> = {n(ACRO['Amin'])} cm²/ml",
                 f"Prévu : <b>T8 e = 20 cm (5 T8 = {n(ACRO['A'])} cm²/ml)</b> {ok(ACRO['A'] >= ACRO['Amin'])} ; "
                 f"répartition A/4 = {n(ACRO['Arep'])} → <b>4 T8</b> par face ; σ<sub>s</sub> ELS = {n(ACRO['ss'], 1)} MPa "
                 f"≤ {n(C.SS_PREJ, 1)} MPa {ok(ACRO['ss'] <= C.SS_PREJ)}"]))

    # ---- 11
    s.append(CondPageBreak(70 * mm))
    s.append(p("11. Récapitulatif", "h1"))
    s.append(p("11.1 Sections et ferraillages retenus (reportés sur les planches 07 à 10)", "h2"))
    s.append(table(["Élément", "Section", "Armatures longitudinales", "Armatures transversales"], [
        ["Poutrelles", "12 × 24 (T 65 cm)", "2T12 inf. + 1T10 sup. ; chapeau 2T12 sur appui B", "Étriers Ø6 e = 15"],
        ["Dalle de compression", "ép. 4 cm", "TS Ø6 maille 20 × 20", "—"],
        ["Poutres PP", "30 × 45", "Inf. 3T16 + 3T16 ; sup. 3T14 + chapeaux 3T14", "Cadre + étrier T8 e = 10 / 15"],
        ["Poutres PS", "30 × 35", "Inf. 3T14 ; sup. 3T12 + chapeaux 2T12", "Cadre T8 + épingle e = 8 / 15"],
        ["Poteaux", "30 × 30", "8T12", "Cadre + losange T8 e = 10 / 15"],
        *[[f"Semelles {t} ({lab})", f"{n(f['a'])} × {n(f['a'])} × {n(f['hs'])}",
           f"{f['n']}T12 e = {(f['a'] - 0.10) / (f['n'] - 1) * 100:.0f} dans les 2 sens", "Amorces 8T12, cadres T8"]
          for (t, f), lab in zip(FOOT.items(), ["B2, B3", "rive", "angle"])],
        ["Longrines", "30 × 40", "3T14 + 3T14", "Cadre T8 e = 20"],
        ["Acrotère", "10 × 60", "4 + 4 T8 filants", "T8 e = 20 (U)"],
    ], [33, 30, 66, 45]))
    s.append(p("11.2 Tableau des vérifications", "h2"))
    s.append(table(["Vérification", "Valeur", "Limite", "Résultat"],
                   [[a, n(v, 2), n(lim, 2), ok(c)] for a, v, lim, c in C.checks()], [86, 25, 25, 38]))
    s.append(Spacer(1, 5 * mm))
    s.append(p("<b>Conclusion.</b> Toutes les vérifications réglementaires sont satisfaites pour les hypothèses "
               "énoncées. Cette note est un dimensionnement d'exécution d'une construction courante ; elle doit "
               "être revue et visée par un ingénieur agréé. En particulier, la contrainte admissible du sol "
               "(2.00 bars), la classe de site (S3) et la zone sismique (IIa) devront être confirmées par l'étude "
               "géotechnique et la localisation exacte du terrain ; toute modification entraîne la reprise des "
               "§ 8 et 9."))
    return s


def main():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm,
                            bottomMargin=20 * mm, title="Note de calcul — structure béton armé",
                            author="Bureau d'études")
    doc.build(build(), onFirstPage=on_page, onLaterPages=on_page)
    return OUT


if __name__ == "__main__":
    print(main())
