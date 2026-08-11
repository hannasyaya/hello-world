"""Parametres fiscaux et sociaux du Quebec pour l'annee 2026.

Toutes les sources sont citees dans rqap/README.md. Les valeurs marquees
APPROX sont des estimations : elles influencent le revenu net absolu de
quelques centaines de dollars, mais tres peu les ecarts entre scenarios,
qui sont le vrai objet du calcul.
"""

ANNEE = 2026
SEMAINES_PAR_AN = 52

# --- Regime de rentes du Quebec (RRQ) -------------------------------------
RRQ_EXEMPTION = 3_500.00
RRQ_MGA = 74_600.00           # maximum des gains admissibles
RRQ_MSGA = 85_000.00          # maximum supplementaire (114 % du MGA)
RRQ_TAUX_SALARIE = 0.0630     # base + premiere cotisation supplementaire
RRQ_TAUX_SUPP2 = 0.0400       # deuxieme cotisation supplementaire (MGA -> MSGA)

# Repartition base / bonifie : la portion bonifiee est deductible du revenu,
# la portion de base donne droit a un credit d'impot. APPROX sur le partage
# exact du taux de 6,30 %.
RRQ_TAUX_BASE = 0.0530
RRQ_TAUX_BONIFIE = RRQ_TAUX_SALARIE - RRQ_TAUX_BASE   # 1re cotisation supp.

# --- Assurance-emploi (taux reduit du Quebec) ------------------------------
AE_MAX_ASSURABLE = 68_900.00
AE_TAUX_SALARIE = 0.0130

# --- Regime quebecois d'assurance parentale (RQAP) -------------------------
RQAP_MAX_ASSURABLE = 103_000.00
RQAP_TAUX_SALARIE = 0.00430

# Regime de base : semaines et taux de remplacement.
RQAP_BASE_PATERNITE_SEMAINES = 5
RQAP_BASE_PATERNITE_TAUX = 0.70
RQAP_BASE_PARENTALES_70_SEMAINES = 7    # les 7 premieres semaines partageables
RQAP_BASE_PARENTALES_55_SEMAINES = 25   # les 25 suivantes
RQAP_BASE_PARENTALES_TOTAL = (
    RQAP_BASE_PARENTALES_70_SEMAINES + RQAP_BASE_PARENTALES_55_SEMAINES
)

# Bonus de partage : 4 semaines partageables de plus, a 55 %, accordees
# seulement si CHAQUE parent prend au moins 8 semaines parentales.
RQAP_BASE_BONUS_SEMAINES = 4
RQAP_BASE_BONUS_TAUX = 0.55
RQAP_BASE_BONUS_SEUIL_PAR_PARENT = 8

# --- Impot du Quebec -------------------------------------------------------
QC_PALIERS = [
    (51_780.00, 0.14),
    (103_545.00, 0.19),
    (126_000.00, 0.24),
    (float("inf"), 0.2575),
]
QC_MONTANT_PERSONNEL_BASE = 18_952.00
QC_TAUX_CREDIT = 0.14

# --- Impot federal (avant abattement du Quebec) ----------------------------
# APPROX : seuils 2026 non indexes dans les sources consultees.
FED_PALIERS = [
    (57_375.00, 0.14),
    (114_750.00, 0.205),
    (177_882.00, 0.26),
    (253_414.00, 0.29),
    (float("inf"), 0.33),
]
FED_MONTANT_PERSONNEL_BASE = 16_452.00
FED_TAUX_CREDIT = 0.14
FED_ABATTEMENT_QUEBEC = 0.165
