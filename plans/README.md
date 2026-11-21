# Dossier de plans — Habitation individuelle R.D.C (15.00 × 8.00 m)

| N° | Planche | Lot | Échelle |
|----|---------|-----|---------|
| 00 | Page de garde & sommaire | Général | — |
| 01 | Plan du rez-de-chaussée (cotes, surfaces, menuiseries) | Architecture | 1:50 |
| 02 | Plan de terrasse (pentes, EP) | Architecture | 1:50 |
| 03 | Façades Sud & Est (principale) | Architecture | 1:50 |
| 04 | Façades Nord & Ouest | Architecture | 1:50 |
| 05 | Coupes A-A & B-B | Architecture | 1:50 |
| 06 | Plan d'implantation (axes, coordonnées poteaux) | Structure | 1:50 |
| 07 | Plan de fondations + détail semelle | Structure | 1:50 / 1:20 |
| 08 | Plan de coffrage plancher terrasse | Structure | 1:50 |
| 09 | Ferraillage fondations, poteaux, longrines | Exécution | 1:20 / 1:5 |
| 10 | Ferraillage poutres, plancher 20+4, acrotère | Exécution | 1:25 / 1:10 |

- `Dossier_plans_habitation_RDC.pdf` — dossier complet, format A2 paysage (impression vectorielle).
- `png/` — aperçus de chaque planche.
- `dxf/` — fichiers DXF (unités : mètres, calques A-* architecture / S-* structure) pour AutoCAD.

Régénérer : `pip install matplotlib ezdxf shapely && python3 generator/build.py`

Les plans de structure sont un **prédimensionnement** (BAEL 91 / RPA 99 v2003, σsol = 2 bars supposé)
à faire vérifier par un ingénieur agréé après étude de sol.

## Fichiers Excel

- `Devis_quantitatif_estimatif.xlsx`
  - **Récapitulatif** : total par lot, imprévus 5 %, TVA 19 %, TTC, ratios DA/m².
  - **DQE** : 64 articles en 11 lots, quantité × P.U. = montant.
  - **Avant-métré** : détail Nb × L × l × H tiré des plans.
  - Les prix unitaires (en bleu) sont indicatifs (DA HT, 2026) et modifiables : tout se recalcule.
- `Planning_travaux.xlsx` — diagramme de Gantt de 31 tâches, enchaînées fin → début avec décalages.
  - Les dates se calculent à partir de la date d'ODS (G3) et du week-end (G4 : 1 = vendredi-samedi).

Régénérer : `python3 generator/excel.py`
