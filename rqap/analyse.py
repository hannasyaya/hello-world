"""Analyse : faut-il prendre les semaines parentales partageables ?

Usage :
    python analyse.py --salaire 100000 --salaire-conjoint 75000
    python analyse.py --salaire 100000            # table de sensibilite
"""

import argparse

import calcul
import parametres_2026 as p


def fmt(x):
    return f"{x:>12,.0f} $".replace(",", " ")


def semaine_en_date(semaine):
    """Approximation : convertit un numero de semaine en mois/jour."""
    mois = [
        "janvier", "fevrier", "mars", "avril", "mai", "juin",
        "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
    ]
    jour_annee = semaine * 7
    idx = min(int(jour_annee // 30.44), 11)
    jour = int(jour_annee - idx * 30.44) + 1
    return f"{jour} {mois[idx]}"


def section(titre):
    print()
    print("=" * 78)
    print(titre)
    print("=" * 78)


def rapport_plafonds(salaire_plein_temps, semaines_conge_deja):
    section("1. QUAND LES COTISATIONS S'ARRETENT")
    salaire = salaire_plein_temps * (p.SEMAINES_PAR_AN - semaines_conge_deja) / p.SEMAINES_PAR_AN
    print(f"Salaire annuel effectif ({semaines_conge_deja} semaines sans paie) : {fmt(salaire)}")
    print()
    plafonds = [
        ("Assurance-emploi", p.AE_MAX_ASSURABLE, p.AE_TAUX_SALARIE),
        ("RRQ - base (MGA)", p.RRQ_MGA, p.RRQ_TAUX_SALARIE),
        ("RRQ - 2e plafond (MSGA)", p.RRQ_MSGA, p.RRQ_TAUX_SUPP2),
        ("RQAP", p.RQAP_MAX_ASSURABLE, p.RQAP_TAUX_SALARIE),
    ]
    print(f"{'Cotisation':<26}{'Plafond':>14}{'Taux':>9}   Atteint")
    print("-" * 78)
    for nom, plafond, taux in plafonds:
        sem = calcul.semaine_ou_plafond_atteint(salaire, plafond)
        quand = f"~{semaine_en_date(sem)}" if sem else "JAMAIS (plafond > salaire)"
        print(f"{nom:<26}{plafond:>12,.0f} $".replace(",", " ") + f"{taux:>8.3%}   {quand}")

    cot = calcul.cotisations_sociales(salaire)
    print("-" * 78)
    print(f"{'Total cotisations':<26}{fmt(cot.total)}")


def rapport_marginal(salaire_plein_temps, semaines_conge_deja):
    section("2. COUT NET D'UNE SEMAINE PARENTALE SUPPLEMENTAIRE (pour toi)")
    base = calcul.annee(
        salaire_plein_temps,
        semaines_conge_deja,
        semaines_a_70=semaines_conge_deja,
    )
    print(f"Reference : {semaines_conge_deja} semaines de paternite, revenu net {fmt(base.revenu_net)}")
    print()
    print(f"{'Sem.':>5}{'Taux':>7}{'Salaire brut':>15}{'Prestations':>14}"
          f"{'Revenu net':>14}{'Cout/sem.':>13}")
    print("-" * 78)

    precedent = base.revenu_net
    for k in range(1, p.RQAP_BASE_PARENTALES_TOTAL + 1):
        r = calcul.annee(
            salaire_plein_temps,
            semaines_conge_deja + k,
            semaines_a_70=semaines_conge_deja + min(k, p.RQAP_BASE_PARENTALES_70_SEMAINES),
            semaines_a_55=max(0, k - p.RQAP_BASE_PARENTALES_70_SEMAINES),
        )
        cout = precedent - r.revenu_net
        taux = "70 %" if k <= p.RQAP_BASE_PARENTALES_70_SEMAINES else "55 %"
        if k <= 10 or k % 4 == 0 or k == p.RQAP_BASE_PARENTALES_TOTAL:
            print(f"{k:>5}{taux:>7}{fmt(r.salaire_brut)}{fmt(r.prestations_brutes)}"
                  f"{fmt(r.revenu_net)}{fmt(cout)}")
        precedent = r.revenu_net

    total = base.revenu_net - precedent
    print("-" * 78)
    print(f"Prendre les {p.RQAP_BASE_PARENTALES_TOTAL} semaines partageables coute {fmt(total)} net sur l'annee.")


def _parent(salaire, semaines_reservees, semaines_partagees, semaines_70_dispo):
    """Annee d'un parent : ses semaines reservees (70 %) + ses semaines partagees.

    `semaines_70_dispo` est le nombre de semaines partageables a 70 % encore
    disponibles pour ce parent (les 7 premieres appartiennent a la famille).
    """
    a_70 = min(semaines_partagees, max(0, semaines_70_dispo))
    return calcul.annee(
        salaire,
        semaines_reservees + semaines_partagees,
        semaines_a_70=semaines_reservees + a_70,
        semaines_a_55=semaines_partagees - a_70,
    )


def _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, sem_a, sem_b):
    """Revenu net combine du couple. A sert les semaines a 70 % en premier."""
    ra = _parent(salaire_a, sem_pat, sem_a, p.RQAP_BASE_PARENTALES_70_SEMAINES)
    reste_70 = p.RQAP_BASE_PARENTALES_70_SEMAINES - min(sem_a, p.RQAP_BASE_PARENTALES_70_SEMAINES)
    rb = _parent(salaire_b, sem_mat, sem_b, reste_70)
    return ra.revenu_net + rb.revenu_net


def rapport_couple(salaire_a, salaire_b, sem_pat, sem_mat):
    section("3. QUI DEVRAIT PRENDRE LES SEMAINES PARTAGEABLES ?")
    print(f"Parent A (toi) : {fmt(salaire_a)} + {sem_pat} sem. de paternite")
    print(f"Parent B       : {fmt(salaire_b)} + {sem_mat} sem. de maternite")
    print()
    print(f"{'Sem. partagees':>15}{'Prises par A':>15}{'Prises par B':>15}"
          f"{'Net du couple':>16}{'Ecart':>13}")
    print("-" * 78)

    reference = _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, 0, 0)
    for total_sem in (0, 8, 16, 24, 32):
        for preneur in ("A", "B"):
            if total_sem == 0 and preneur == "B":
                continue
            sem_a = total_sem if preneur == "A" else 0
            sem_b = total_sem if preneur == "B" else 0
            net = _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, sem_a, sem_b)
            print(f"{total_sem:>15}{sem_a:>15}{sem_b:>15}{fmt(net)}{fmt(net - reference)}")


def rapport_sensibilite(salaire_a, sem_pat, sem_mat):
    section("3. SENSIBILITE AU SALAIRE DU CONJOINT (16 semaines partagees)")
    print("Ecart de revenu net du couple selon qui prend les 16 semaines.")
    print("Un ecart positif = il vaut mieux que ce soit le parent B qui les prenne.")
    print()
    print(f"{'Salaire parent B':>18}{'Si A les prend':>18}{'Si B les prend':>18}{'Avantage B':>16}")
    print("-" * 78)

    for salaire_b in (45_000, 60_000, 75_000, 90_000, 100_000, 120_000):
        net_si_a = _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, 16, 0)
        net_si_b = _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, 0, 16)
        print(f"{fmt(salaire_b):>18}{fmt(net_si_a)}{fmt(net_si_b)}{fmt(net_si_b - net_si_a)}")


def rapport_bonus(salaire_a, salaire_b, sem_pat, sem_mat):
    """Effet de seuil : 8 semaines chacun debloquent 4 semaines de plus."""
    section("4. LE SEUIL DES 8 SEMAINES (bonus de partage)")
    seuil = p.RQAP_BASE_BONUS_SEUIL_PAR_PARENT
    print(f"Si CHAQUE parent prend au moins {seuil} semaines parentales, le couple")
    print(f"obtient {p.RQAP_BASE_BONUS_SEMAINES} semaines partageables de plus a "
          f"{p.RQAP_BASE_BONUS_TAUX:.0%}.")
    print()

    print(f"{'Scenario':<44}{'Sem. totales':>14}{'Net du couple':>16}")
    print("-" * 78)
    scenarios = [
        ("A prend 4, B prend 28  (pas de bonus)", 4, 28),
        (f"A prend {seuil}, B prend 24  (BONUS debloque)", seuil, 24),
        (f"A prend {seuil}, B prend 28  (bonus utilise)", seuil, 28),
        ("A prend 16, B prend 20  (bonus utilise)", 16, 20),
    ]
    for label, sem_a, sem_b in scenarios:
        net = _net_couple(salaire_a, salaire_b, sem_pat, sem_mat, sem_a, sem_b)
        print(f"{label:<44}{sem_a + sem_b:>14}{fmt(net)}")
    print()
    print("Le bonus n'est pas de l'argent gratuit : ce sont 4 semaines de conge")
    print("payees a 55 % de plus, donc du temps en famille achete au meme prix")
    print("marginal que les autres semaines a 55 %.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salaire", type=float, default=100_000)
    ap.add_argument("--salaire-conjoint", type=float, default=None)
    ap.add_argument("--semaines-paternite", type=int, default=5)
    ap.add_argument("--semaines-maternite", type=int, default=18,
                    help="semaines de maternite deja prises par le conjoint")
    args = ap.parse_args()

    print(f"RQAP {p.ANNEE} - regime de base - Montreal")
    rapport_plafonds(args.salaire, args.semaines_paternite)
    rapport_marginal(args.salaire, args.semaines_paternite)
    if args.salaire_conjoint:
        rapport_couple(args.salaire, args.salaire_conjoint,
                       args.semaines_paternite, args.semaines_maternite)
        rapport_bonus(args.salaire, args.salaire_conjoint,
                      args.semaines_paternite, args.semaines_maternite)
    else:
        rapport_sensibilite(args.salaire, args.semaines_paternite,
                            args.semaines_maternite)


if __name__ == "__main__":
    main()
