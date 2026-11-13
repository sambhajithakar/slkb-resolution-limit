"""Candidate confirmatory procedures under skew and dependence, on the real design.

Design-only, like `exchangeability_sim.py`: reads which study and which cell model each
eligible screen belongs to and how many informative queries it carries, and reads no
observed average precision. It opens no gate and consumes no researcher degree of freedom.

Four procedures are compared on identical replicates:

  P1  registered conjunction of exact sign-flip tests (both arms p<=0.05, signs agree)
  P2  P1 gated on a pre-specified symmetry diagnostic (Amendment E, |skew| <= 1.0 on the
      eight cell-model values); a replicate only counts as a confirmatory claim if the
      gate passes AND P1 rejects
  P3  conjunction of exact two-sided sign tests (binomial) on each arm
  P4  cell-model Wilcoxon signed-rank, for reference

Each is measured under mu = 0 (no effect) and at mu = DELTA standard deviations, the
effect the pre-specified recalculation puts at 80% power, so the cost of each procedure
in power is measured alongside its size.

IMPORTANT, and the reason this script exists: under a skewed mean-zero law the null
"mean = 0" does not imply "median = 0". P3 and P4 therefore test a different null, and
their rejection rate under skew is not a type I error for the registered estimand. The
output records this in `addresses_null` so the numbers cannot be read as if the four
procedures were interchangeable.

Usage: python3 alternatives_sim.py <Table_1_eligible_screens.csv> <outdir>
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

SEED = 20261031
N_SIM = 20000
DELTA = 1.40          # the recalculated detectable effect, in between-cell-model SD units
GATE = 1.0            # Amendment E's symmetry threshold
ALPHA = 0.05

st = pd.read_csv(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
st.columns = [c.strip() for c in st.columns]
st = st.rename(columns={"PMID": "study", "Cell model": "cell_line",
                        "Queries with >=1 positive": "n_queries"})
st["study"] = st["study"].astype(str)

studies = sorted(st.study.unique()); lines = sorted(st.cell_line.unique())
si = st.study.map({s: i for i, s in enumerate(studies)}).to_numpy()
ci = st.cell_line.map({c: i for i, c in enumerate(lines)}).to_numpy()
nq = st.n_queries.to_numpy(float)
S, G, K = len(st), len(lines), len(studies)

Wc = np.zeros((S, G)); Wc[np.arange(S), ci] = nq; Wc /= Wc.sum(0, keepdims=True)
Ws = np.zeros((S, K)); Ws[np.arange(S), si] = 1.0; Ws /= Ws.sum(0, keepdims=True)


def signs(n: int) -> np.ndarray:
    return np.array([[1 if (k >> j) & 1 else -1 for j in range(n)] for k in range(2 ** n)], float)


Sc, Ss = signs(G), signs(K)


def p_signflip(x: np.ndarray, M: np.ndarray) -> np.ndarray:
    stat = np.abs(x @ M.T)
    return (stat >= stat[:, :1] - 1e-12).mean(1)


def p_signtest(x: np.ndarray) -> np.ndarray:
    """Exact two-sided binomial sign test; zeros counted against rejection."""
    n = x.shape[1]
    pos = (x > 0).sum(1)
    neg = (x < 0).sum(1)
    m = pos + neg                                  # drop exact zeros, as the sign test does
    k = np.minimum(pos, neg)
    out = np.ones(len(x))
    for mm in np.unique(m):
        sel = m == mm
        if mm == 0:
            continue
        out[sel] = np.clip(2 * sps.binom.cdf(k[sel], mm, 0.5), 0, 1)
    return out


def draw(rng, kind, n, size):
    z = rng.standard_normal((n, size))
    if kind == "normal":
        return z
    if kind.startswith("gamma"):
        k = float(kind[5:]); g = rng.gamma(k, 1.0, (n, size)); return (g - k) / np.sqrt(k)
    if kind == "t3":
        return rng.standard_t(3, (n, size)) / np.sqrt(3.0)
    if kind == "chisq1":
        return (z ** 2 - 1) / np.sqrt(2)
    if kind == "lognormal":
        x = np.exp(z * 0.8); m = np.exp(0.32); v = (np.exp(0.64) - 1) * np.exp(0.64)
        return (x - m) / np.sqrt(v)
    raise ValueError(kind)


def run(rho_s, rho_c, kind, mu, n=N_SIM, seed=SEED):
    rng = np.random.default_rng(seed)
    if rho_s + rho_c > 1:
        return None
    a = draw(rng, kind, n, K) * np.sqrt(rho_s)
    b = draw(rng, kind, n, G) * np.sqrt(rho_c)
    r = draw(rng, kind, n, S) * np.sqrt(max(0.0, 1 - rho_s - rho_c))
    scr = a[:, si] + b[:, ci] + r + mu
    xc, xs = scr @ Wc, scr @ Ws
    mc, ms = xc.mean(1), xs.mean(1)
    agree = np.sign(mc) == np.sign(ms)

    p1 = (p_signflip(xc, Sc) <= ALPHA) & (p_signflip(xs, Ss) <= ALPHA) & agree
    skew = sps.skew(xc, axis=1, bias=False)
    gate = np.abs(skew) <= GATE
    p2 = p1 & gate
    p3 = (p_signtest(xc) <= ALPHA) & (p_signtest(xs) <= ALPHA) & agree
    p4 = sps.wilcoxon(xc, axis=1, zero_method="zsplit", mode="exact"
                      ).pvalue <= ALPHA if False else np.array(
        [sps.wilcoxon(row, zero_method="zsplit").pvalue for row in xc[:2000]]) <= ALPHA

    return dict(rho_within_study=rho_s, rho_shared_line=rho_c, errors=kind, mu_in_sd=mu,
                P1_conjunction=float(p1.mean()),
                P2_conjunction_gated=float(p2.mean()),
                P3_conjunction_signtest=float(p3.mean()),
                P4_cell_wilcoxon=float(p4.mean()),
                gate_pass_rate=float(gate.mean()),
                mean_sample_skew=float(skew.mean()),
                n_sim=n, n_sim_P4=2000)


rows = []
grid = [0.0, 0.2, 0.4]
for kind in ("normal", "t3", "gamma4", "gamma1", "lognormal", "chisq1"):
    for mu in (0.0, DELTA):
        for rs in grid:
            for rc in grid:
                out = run(rs, rc, kind, mu)
                if out:
                    rows.append(out)
df = pd.DataFrame(rows)
df.to_csv(OUT / "alternative_procedures_results.csv", index=False)

summary = {
    "what_this_is": "design-only comparison of candidate confirmatory procedures",
    "what_this_is_not": "not a hypothesis test; no observed average precision is read",
    "seed": SEED, "n_sim": N_SIM, "n_sim_P4": 2000, "alpha": ALPHA,
    "delta_in_sd": DELTA, "gate_threshold": GATE,
    "structure": {"screens": S, "cell_models": G, "studies": K},
    "addresses_null": {
        "P1_conjunction": "mean of cluster values = 0, exact under independence AND symmetry",
        "P2_conjunction_gated": "same null; confirmatory status withheld when the sample "
                                "skewness of the cell-model values exceeds the pre-set threshold",
        "P3_conjunction_signtest": "MEDIAN of cluster values = 0 — a DIFFERENT null. Under a "
                                   "skewed mean-zero law its rejection rate is not a type I "
                                   "error for the registered estimand",
        "P4_cell_wilcoxon": "median = 0 AND symmetry; it assumes exactly what is in question",
    },
    "by_error_law": {},
}
for kind, g in df.groupby("errors"):
    h0 = g[g.mu_in_sd == 0.0]
    h1 = g[g.mu_in_sd == DELTA]
    ind0 = h0[(h0.rho_within_study == 0) & (h0.rho_shared_line == 0)]
    summary["by_error_law"][kind] = {
        "skewness_of_cluster_values_mean": round(float(h0.mean_sample_skew.mean()), 3),
        "size_at_independence": {k: round(float(ind0[k].iloc[0]), 4) for k in
                                 ("P1_conjunction", "P2_conjunction_gated",
                                  "P3_conjunction_signtest", "P4_cell_wilcoxon")},
        "size_worst_over_dependence_grid": {k: round(float(h0[k].max()), 4) for k in
                                            ("P1_conjunction", "P2_conjunction_gated",
                                             "P3_conjunction_signtest", "P4_cell_wilcoxon")},
        "power_at_delta_independence": {k: round(float(
            h1[(h1.rho_within_study == 0) & (h1.rho_shared_line == 0)][k].iloc[0]), 4) for k in
            ("P1_conjunction", "P2_conjunction_gated",
             "P3_conjunction_signtest", "P4_cell_wilcoxon")},
        "gate_pass_rate_under_null": round(float(ind0.gate_pass_rate.iloc[0]), 4),
    }
json.dump(summary, open(OUT / "alternative_procedures_summary.json", "w"), indent=1)
print(json.dumps(summary["by_error_law"], indent=1))
