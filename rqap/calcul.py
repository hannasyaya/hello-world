"""Moteur de calcul : cotisations, impots et prestations RQAP (regime de base).

Le modele raisonne sur une annee civile complete. Une semaine de conge
remplace une semaine de salaire par une semaine de prestations : le salaire
annuel baisse, ce qui repousse (ou empeche) l'atteinte des plafonds de
cotisation, et les prestations ne sont assujetties a aucune cotisation
sociale.
"""

from dataclasses import dataclass

import parametres_2026 as p


def _impot_paliers(revenu, paliers):
    impot = 0.0
    plancher = 0.0
    for plafond, taux in paliers:
        if revenu <= plancher:
            break
        impot += (min(revenu, plafond) - plancher) * taux
        plancher = plafond
    return impot


@dataclass
class Cotisations:
    rrq: float
    ae: float
    rqap: float

    @property
    def total(self):
        return self.rrq + self.ae + self.rqap


def cotisations_sociales(salaire):
    """Cotisations du salarie. Seul le SALAIRE cotise, jamais les prestations."""
    rrq_base = max(0.0, min(salaire, p.RRQ_MGA) - p.RRQ_EXEMPTION) * p.RRQ_TAUX_SALARIE
    rrq_supp2 = max(0.0, min(salaire, p.RRQ_MSGA) - p.RRQ_MGA) * p.RRQ_TAUX_SUPP2
    return Cotisations(
        rrq=rrq_base + rrq_supp2,
        ae=min(salaire, p.AE_MAX_ASSURABLE) * p.AE_TAUX_SALARIE,
        rqap=min(salaire, p.RQAP_MAX_ASSURABLE) * p.RQAP_TAUX_SALARIE,
    )


def semaine_ou_plafond_atteint(salaire_annuel, plafond):
    """Semaine de l'annee ou le cumul de paie atteint un plafond (None si jamais)."""
    if salaire_annuel <= plafond:
        return None
    return plafond / (salaire_annuel / p.SEMAINES_PAR_AN)


def _parts_rrq(salaire):
    """Separe la cotisation RRQ en portion creditable et portion deductible."""
    assiette_base = max(0.0, min(salaire, p.RRQ_MGA) - p.RRQ_EXEMPTION)
    creditable = assiette_base * p.RRQ_TAUX_BASE
    deductible = assiette_base * p.RRQ_TAUX_BONIFIE
    deductible += max(0.0, min(salaire, p.RRQ_MSGA) - p.RRQ_MGA) * p.RRQ_TAUX_SUPP2
    return creditable, deductible


def impot_total(salaire, prestations):
    """Impot federal (apres abattement) + provincial sur salaire + prestations."""
    cot = cotisations_sociales(salaire)
    rrq_creditable, rrq_deductible = _parts_rrq(salaire)

    revenu_imposable = salaire + prestations - rrq_deductible
    # Cotisations donnant droit a un credit non remboursable aux deux paliers.
    credits = rrq_creditable + cot.ae + cot.rqap

    qc = _impot_paliers(revenu_imposable, p.QC_PALIERS)
    qc -= (p.QC_MONTANT_PERSONNEL_BASE + credits) * p.QC_TAUX_CREDIT
    qc = max(0.0, qc)

    fed = _impot_paliers(revenu_imposable, p.FED_PALIERS)
    fed -= (p.FED_MONTANT_PERSONNEL_BASE + credits) * p.FED_TAUX_CREDIT
    fed = max(0.0, fed) * (1 - p.FED_ABATTEMENT_QUEBEC)

    return qc + fed


def prestations_parentales(salaire_annuel, semaines_a_70, semaines_a_55):
    """Prestations brutes du regime de base, plafonnees au maximum assurable."""
    hebdo_assurable = min(salaire_annuel, p.RQAP_MAX_ASSURABLE) / p.SEMAINES_PAR_AN
    return hebdo_assurable * (0.70 * semaines_a_70 + 0.55 * semaines_a_55)


@dataclass
class Resultat:
    salaire_brut: float
    prestations_brutes: float
    cotisations: float
    impot: float

    @property
    def revenu_brut(self):
        return self.salaire_brut + self.prestations_brutes

    @property
    def revenu_net(self):
        return self.revenu_brut - self.cotisations - self.impot


def annee(salaire_plein_temps, semaines_conge, semaines_a_70=0, semaines_a_55=0):
    """Simule une annee civile avec `semaines_conge` semaines sans salaire.

    `semaines_a_70` et `semaines_a_55` decrivent le taux de remplacement des
    semaines de conge prises pendant cette annee (paternite et 7 premieres
    semaines partageables a 70 %, le reste a 55 %).
    """
    semaines_travaillees = p.SEMAINES_PAR_AN - semaines_conge
    salaire = salaire_plein_temps * semaines_travaillees / p.SEMAINES_PAR_AN
    prestations = prestations_parentales(salaire_plein_temps, semaines_a_70, semaines_a_55)
    cot = cotisations_sociales(salaire)
    return Resultat(
        salaire_brut=salaire,
        prestations_brutes=prestations,
        cotisations=cot.total,
        impot=impot_total(salaire, prestations),
    )
