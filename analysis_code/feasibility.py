"""Design-feasibility calculator for combinatorial screen resources.

For any set of screens, each identified by (study, cell_model), the mutually
independent evaluation units are the connected components of the bipartite
study x cell-model incidence graph.  An exact sign-flip (or any exact
sign-symmetry) test on G such units attains two-sided p-values that are even
multiples of 2**-G, so its smallest attainable two-sided p is 2**(1-G) and its
smallest attainable one-sided p is 2**-G.  A confirmatory test at level alpha
is therefore ARITHMETICALLY IMPOSSIBLE -- size and power identically zero --
whenever that floor exceeds alpha, regardless of effect size or sample size.
"""
import csv, math, json, collections

ALPHA = 0.05


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def components(screens):
    """screens: iterable of (study, cell_model). Returns list of component dicts."""
    uf = UF()
    for s, c in screens:
        uf.union(("S", s), ("C", c))
    comp = collections.defaultdict(lambda: {"studies": set(), "cells": set(), "screens": 0})
    for s, c in set(screens):
        k = uf.find(("S", s))
        comp[k]["studies"].add(s)
        comp[k]["cells"].add(c)
        comp[k]["screens"] += 1
    return [
        {"studies": sorted(v["studies"]), "cells": sorted(v["cells"]), "n_screens": v["screens"]}
        for v in comp.values()
    ]


def feasibility(G, alpha=ALPHA):
    two = 2.0 ** (1 - G) if G > 0 else 1.0
    one = 2.0 ** (-G) if G > 0 else 1.0
    return {
        "G": G,
        "min_p_two_sided": two,
        "min_p_one_sided": one,
        "two_sided_feasible": two <= alpha,
        "one_sided_feasible": one <= alpha,
    }


def min_G(alpha=ALPHA):
    """Smallest G for which each test can ever reject at level alpha."""
    g2 = next(g for g in range(1, 64) if 2.0 ** (1 - g) <= alpha)
    g1 = next(g for g in range(1, 64) if 2.0 ** (-g) <= alpha)
    return g2, g1


def load_slkb(path):
    screens = set()
    by_study = collections.defaultdict(set)
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            s = (row["study_origin"] or "").strip()
            c = (row["cell_line_origin"] or "").strip()
            if s and c:
                screens.add((s, c))
                by_study[s].add((s, c))
    return screens, by_study


if __name__ == "__main__":
    g2, g1 = min_G()
    print(f"alpha = {ALPHA}")
    print(f"minimum G for an exact two-sided test to be able to reject: {g2}")
    print(f"minimum G for an exact one-sided test to be able to reject: {g1}")
    print()

    screens, by_study = load_slkb(
        "/mnt/project-files/uploads/SLKB_2026-10-28/SLKB_calculated_scores.csv")

    rows = []

    def add(label, scr):
        comps = components(scr)
        f = feasibility(len(comps))
        rows.append({
            "resource": label,
            "n_screens": len(set(scr)),
            "n_studies": len({s for s, _ in scr}),
            "n_cell_models": len({c for _, c in scr}),
            **f,
            "components": comps,
        })

    add("SLKB (whole resource, all screens)", screens)
    for s in sorted(by_study):
        add(f"SLKB study PMID {s}", by_study[s])

    print(f"{'resource':<40}{'scr':>5}{'std':>5}{'cell':>6}{'G':>4}"
          f"{'min p (2s)':>12}{'2s?':>6}{'1s?':>6}")
    for r in rows:
        print(f"{r['resource']:<40}{r['n_screens']:>5}{r['n_studies']:>5}"
              f"{r['n_cell_models']:>6}{r['G']:>4}{r['min_p_two_sided']:>12.4f}"
              f"{'YES' if r['two_sided_feasible'] else 'NO':>6}"
              f"{'YES' if r['one_sided_feasible'] else 'NO':>6}")

    with open("feasibility_results.json", "w") as fh:
        json.dump({"alpha": ALPHA, "min_G_two_sided": g2, "min_G_one_sided": g1,
                   "rows": rows}, fh, indent=2)
