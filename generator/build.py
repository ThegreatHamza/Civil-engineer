"""Build the full drawing set: python3 generator/build.py  ->  plans/"""
import os
import sys

from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, os.path.dirname(__file__))
import arch  # noqa: E402
import cover  # noqa: E402
import struct_plans as st  # noqa: E402
from drawing import Sheet  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "plans")

SHEETS = [
    ("00_page_de_garde", "PAGE DE GARDE & SOMMAIRE", "GÉNÉRAL", "—", cover.sheet_cover),
    ("01_plan_rdc", "PLAN DU REZ-DE-CHAUSSÉE", "ARCHITECTURE", "1:50", arch.sheet_plan),
    ("02_plan_terrasse", "PLAN DE TERRASSE", "ARCHITECTURE", "1:50", arch.sheet_roof),
    ("03_facades_sud_est", "FAÇADES SUD & EST", "ARCHITECTURE", "1:50", arch.sheet_facades_1),
    ("04_facades_nord_ouest", "FAÇADES NORD & OUEST", "ARCHITECTURE", "1:50", arch.sheet_facades_2),
    ("05_coupes", "COUPES A-A & B-B", "ARCHITECTURE", "1:50", arch.sheet_sections),
    ("06_plan_implantation", "PLAN D'IMPLANTATION", "STRUCTURE", "1:50", st.sheet_implantation),
    ("07_plan_fondations", "PLAN DE FONDATIONS", "STRUCTURE", "1:50", st.sheet_foundations),
    ("08_plan_coffrage", "COFFRAGE PLANCHER TERRASSE", "STRUCTURE", "1:50", st.sheet_formwork),
    ("09_ferraillage_fondations_poteaux", "FERRAILLAGE FONDATIONS & POTEAUX", "STRUCTURE", "1:20 / 1:10",
     st.sheet_rebar_foundations),
    ("10_ferraillage_poutres_plancher", "FERRAILLAGE POUTRES & PLANCHER", "STRUCTURE", "1:25 / 1:10",
     st.sheet_rebar_beams),
]


def main(only=None):
    os.makedirs(os.path.join(ROOT, "png"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "dxf"), exist_ok=True)
    total = len(SHEETS) - 1
    pdf_path = os.path.join(ROOT, "Dossier_plans_habitation_RDC.pdf")
    with PdfPages(pdf_path) as pdf:
        for i, (slug, title, lot, scale, fn) in enumerate(SHEETS):
            if only and slug not in only:
                continue
            S = Sheet("A2", i, total, title, lot, scale)
            fn(S)
            S.save(pdf, os.path.join(ROOT, "png", slug + ".png"),
                   os.path.join(ROOT, "dxf", slug + ".dxf") if i else None)
            print("ok", slug)
    print("->", os.path.abspath(pdf_path))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
