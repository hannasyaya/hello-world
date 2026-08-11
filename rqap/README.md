# Calculateur RQAP — régime de base, Québec 2026

Modèle de planification pour décider si — et par qui — les semaines parentales
partageables du RQAP devraient être prises, en tenant compte des plafonds de
cotisations sociales et de l'impôt.

## Utilisation

```bash
cd rqap
python3 analyse.py --salaire 100000 --salaire-conjoint 75000
python3 analyse.py --salaire 100000          # table de sensibilité si le salaire du conjoint est inconnu
```

Options : `--salaire`, `--salaire-conjoint`, `--semaines-paternite` (défaut 5),
`--semaines-maternite` (défaut 18, semaines déjà prises par le conjoint).

Si le congé enjambe deux années civiles — les prestations sont versées jusqu'à
**78 semaines après la naissance** — `deux_annees.py` compare où placer les
semaines partageables :

```bash
python3 deux_annees.py --salaire-conjoint 80000 --semaines-maternite-2026 14
```

## Ce que le modèle fait

Une semaine de congé remplace une semaine de salaire par une semaine de
prestations. Trois effets se combinent, et c'est leur interaction qui rend le
calcul non trivial :

1. **Les prestations RQAP ne sont assujetties à aucune cotisation sociale**
   (ni RRQ, ni AE, ni RQAP). Le taux de remplacement net est donc plus élevé
   que le taux brut.
2. **Baisser le salaire annuel repousse ou empêche l'atteinte des plafonds.**
   Les premières semaines de congé sont donc plus chères que les suivantes :
   elles retranchent du salaire déjà au-dessus des plafonds, sur lequel on ne
   payait presque plus de cotisations.
3. **Les prestations sont pleinement imposables**, au même taux marginal que
   le salaire qu'elles remplacent.

## Paramètres 2026

| Régime | Plafond | Taux salarié | Cotisation max |
|---|---|---|---|
| RRQ (base + 1re supp.) | 74 600 $ (MGA), exemption 3 500 $ | 6,30 % | 4 479 $ |
| RRQ (2e supp.) | 74 600 $ → 85 000 $ (MSGA) | 4,00 % | 416 $ |
| Assurance-emploi (taux Québec) | 68 900 $ | 1,30 % | 896 $ |
| RQAP | 103 000 $ | 0,430 % | 443 $ |

Régime de base : 5 semaines de paternité à 70 %, puis 32 semaines partageables
(7 à 70 %, 25 à 55 %), plus 4 semaines partageables additionnelles à 55 % si
chaque parent prend au moins 8 semaines parentales.

## Limites connues

- **`analyse.py` raisonne sur une seule année civile.** Un congé à cheval sur
  deux années étale le revenu et réduit l'impôt total — utiliser
  `deux_annees.py` dans ce cas. Les paramètres 2027 y sont supposés égaux à
  ceux de 2026 ; l'indexation d'environ 2 % joue dans le même sens pour tous
  les scénarios comparés.
- **Seuils d'impôt fédéraux 2026 non indexés** dans les sources consultées
  (marqués `APPROX` dans `parametres_2026.py`). Effet de quelques centaines de
  dollars sur les montants absolus, quasi nul sur les écarts entre scénarios.
- **Aucun crédit socio-fiscal familial** (Allocation famille, Allocation
  canadienne pour enfants, crédit pour frais de garde). Ces crédits sont
  fonction du revenu familial et **augmentent** quand le revenu baisse : le
  coût réel d'une semaine de congé est donc **plus bas** que ce que le modèle
  affiche, surtout dans les scénarios à revenu fortement réduit.
- **Aucun complément d'employeur.** Beaucoup de conventions collectives
  comblent l'écart jusqu'à 90–100 % — à vérifier avant de décider.
- Le partage base/bonifié du taux RRQ de 6,30 % est une approximation.

## Sources

- [Maximum de revenus assurables et taux de cotisation au RQAP — Revenu Québec](https://www.revenuquebec.ca/fr/entreprises/retenues-a-la-source-et-cotisations-de-lemployeur/calcul-des-retenues-et-des-cotisations/cotisations-au-rqap/maximum-de-revenus-assurables-et-taux-de-cotisation/)
- [Revenu maximal assurable RQAP — Gouvernement du Québec](https://www.quebec.ca/entreprises-et-travailleurs-autonomes/administrer-gerer/embauche-gestion-personnel/assurance-parentale/revenu-maximal-assurable)
- [Maximum des gains admissibles et taux de cotisation au RRQ — Revenu Québec](https://www.revenuquebec.ca/fr/entreprises/retenues-a-la-source-et-cotisations-de-lemployeur/calcul-des-retenues-et-des-cotisations/cotisations-au-rrq/maximum-des-gains-admissibles-et-taux-de-cotisation/)
- [Maximum de la rémunération assurable pour 2026 — Assurance-emploi, Canada](https://www.canada.ca/fr/emploi-developpement-social/programmes/assurance-emploi/ae-liste/assurance-emploi-employeurs/reduction-taux-cotisation/maximum-remuneration-assurable-2026.html)
- [Cotisations à l'assurance-emploi du Québec (T4032) — ARC](https://www.canada.ca/content/dam/cra-arc/migration/cra-arc/tx/bsnss/tpcs/pyrll/t4032/2026/t4032ei-ae-qc-26fra.pdf)
- [Régimes publics au Québec — Nouveaux paramètres 2026, PBI Actuarial](https://pbiactuarial.ca/fr/regimes-publics-au-quebec-nouveaux-parametres-2026/)
- [Paliers d'imposition Québec 2026 — CalculQC](https://calculqc.ca/blog/fiscalite/paliers-imposition-quebec-2026.html)
- [Guide sur les droits parentaux et le RQAP 2023-2028 — CSQ](https://www.lacsq.org/wp-content/uploads/2025/11/FINAL-FR-2409-21_GuideParent_FPSES.pdf)
- [Taux d'impôt fédéral et provincial combinés, Québec 2026 — EY](https://www.ey.com/content/dam/ey-unified-site/ey-com/fr-ca/services/tax/tax-calculators/2026/ey-taux-impot-quebec-2026-01-15-v1.pdf)

⚠️ Outil de planification, pas un avis fiscal. Valide les montants avec le
[simulateur officiel du RQAP](https://www.rqap.gouv.qc.ca/) avant de décider.
