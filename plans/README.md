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

## Note de calcul

- `Note_de_calcul_structure.pdf` — note de calcul BA (10 pages, A4) :
  - charges, prédimensionnement ;
  - poutrelles (Caquot), poutres PP (forfaitaire) et PS ;
  - descente de charges des 12 poteaux, poteaux (BAEL + RPA) ;
  - étude sismique (méthode statique équivalente) ;
  - semelles S1 / S2 / S3, longrines, acrotère ;
  - tableau récapitulatif des vérifications.
- Calculs dans `generator/calc.py` (les plans 07 à 10 et le devis en reprennent les résultats).
- Régénérer : `python3 generator/note_calcul.py`

## Fichiers Excel

- `Devis_quantitatif_estimatif.xlsx`
  - **Récapitulatif** : total par lot, imprévus 5 %, TVA 19 %, TTC, ratios DA/m².
  - **DQE** : 64 articles en 11 lots, quantité × P.U. = montant.
  - **Avant-métré** : détail Nb × L × l × H tiré des plans.
  - Les prix unitaires (en bleu) sont indicatifs (DA HT, 2026) et modifiables : tout se recalcule.
- `Planning_travaux.xlsx` — planning détaillé, 53 tâches en 7 phases :
  - **Gantt détaillé** : grille jour par jour (mois, semaines, jours), week-ends grisés,
    barres par phase, chemin critique en rouge, jalons ◆, avancement.
  - **Planning** : saisies (durées, 2 prédécesseurs, décalages, avancement) et calcul automatique
    des dates au plus tôt / au plus tard, des marges et du chemin critique.
  - **Diagramme** : graphique de Gantt Excel natif.
- `Planning_Gantt.pdf` (+ `png/Planning_Gantt.png`) — diagramme de Gantt A2 imprimable avec les liaisons.

Régénérer : `python3 generator/excel.py`
