"""Ou placer les semaines partageables : 2026, 2027, ou a cheval ?

Le RQAP verse les prestations jusqu'a 78 semaines apres la naissance. Un bebe
ne en janvier 2026 laisse donc jusqu'a l'ete 2027 pour ecouler les semaines,
et le choix de l'annee civile change l'impot total.

Deux forces opposees :
  - Une semaine de conge coute MOINS cher quand le taux marginal d'impot est
    ELEVE (le salaire abandonne est davantage impose).
  - Une semaine de conge coute MOINS cher quand on est SOUS les plafonds de
    cotisation (on economise jusqu'a 8,03 % au lieu de 0,43 %).

Usage :
    python3 deux_annees.py --salaire-conjoint 80000 --semaines-maternite-2026 14
"""

import argparse

import calcul
import parametres_2026 as p


def fmt(x):
    return f"{x:>12,.0f} $".replace(",", " ")


def _deux_ans(salaire, sem_reservees_2026, sem_2026, sem_2027, sem_70_dispo=0):
    """Net cumule sur 2026 + 2027 pour un parent.

    Les semaines a 70 % sont consommees en premier, dans l'ordre chronologique.
    Les parametres 2027 sont supposes egaux a ceux de 2026 (l'indexation
    d'environ 2 % joue dans le meme sens pour tous les scenarios compares).
    """
    a70_2026 = min(sem_2026, sem_70_dispo)
    a70_2027 = min(sem_2027, sem_70_dispo - a70_2026)

    an1 = calcul.annee(
        salaire,
        sem_reservees_2026 + sem_2026,
        semaines_a_70=sem_reservees_2026 + a70_2026,
        semaines_a_55=sem_2026 - a70_2026,
    )
    an2 = calcul.annee(
        salaire, sem_2027,
        semaines_a_70=a70_2027,
        semaines_a_55=sem_2027 - a70_2027,
    )
    return an1.revenu_net + an2.revenu_net


def rapport(salaire_a, salaire_b, sem_pat, sem_mat_2026, sem_a, sem_b):
    print("=" * 78)
    print("OU PLACER LES SEMAINES PARTAGEABLES (net cumule 2026 + 2027)")
    print("=" * 78)
    print(f"Toi  : {salaire_a:,.0f} $".replace(",", " ")
          + f", {sem_pat} sem. paternite en 2026, {sem_a} sem. partageables")
    print(f"Elle : {salaire_b:,.0f} $".replace(",", " ")
          + f", {sem_mat_2026} sem. maternite en 2026, {sem_b} sem. partageables")
    print()

    print("--- TOI : ou placer tes", sem_a, "semaines ? ---")
    print(f"{'En 2026':>10}{'En 2027':>10}{'Net 2026+2027':>18}{'Ecart':>14}")
    print("-" * 78)
    ref_a = None
    for x in range(0, sem_a + 1, 2):
        net = _deux_ans(salaire_a, sem_pat, x, sem_a - x,
                        sem_70_dispo=p.RQAP_BASE_PARENTALES_70_SEMAINES)
        ref_a = net if ref_a is None else ref_a
        print(f"{x:>10}{sem_a - x:>10}{fmt(net)}{fmt(net - ref_a)}")

    print()
    print("--- ELLE : ou placer ses", sem_b, "semaines ? ---")
    print(f"{'En 2026':>10}{'En 2027':>10}{'Net 2026+2027':>18}{'Ecart':>14}")
    print("-" * 78)
    ref_b = None
    max_2026 = min(sem_b, p.SEMAINES_PAR_AN - sem_mat_2026)
    for x in range(0, max_2026 + 1, 4):
        net = _deux_ans(salaire_b, sem_mat_2026, x, sem_b - x)
        ref_b = net if ref_b is None else ref_b
        print(f"{x:>10}{sem_b - x:>10}{fmt(net)}{fmt(net - ref_b)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salaire", type=float, default=100_000)
    ap.add_argument("--salaire-conjoint", type=float, default=80_000)
    ap.add_argument("--semaines-paternite", type=int, default=5)
    ap.add_argument("--semaines-maternite-2026", type=int, default=14)
    ap.add_argument("--sem-partagees-a", type=int, default=8)
    ap.add_argument("--sem-partagees-b", type=int, default=28)
    args = ap.parse_args()

    rapport(args.salaire, args.salaire_conjoint, args.semaines_paternite,
            args.semaines_maternite_2026, args.sem_partagees_a, args.sem_partagees_b)


if __name__ == "__main__":
    main()
