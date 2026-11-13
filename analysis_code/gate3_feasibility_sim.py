"""Targeted statistical resolution for BRCA_RAG_ Gate 3.

Design-only. Reads which study and which cell model each eligible screen belongs to and
how many informative queries it carries. Reads NO observed average precision, opens no
gate, and computes no quantity for H1-H4.

Three questions:
  Q1  What is the correct number of independent sign-flip units, and what p-values are
      attainable?  (arithmetic, not simulation)
  Q2  For every candidate procedure: unconditional size, size CONDITIONAL on the symmetry
      gate passing, and power at 1.40 SD, each with a Monte-Carlo interval.
  Q3  Is any procedure attainable AND valid at this design?
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats as sps

SEED, N_SIM, DELTA, GATE, ALPHA = 20261103, 40000, 1.40, 1.0, 0.05
TBL = "/mnt/project-files/12_Q1_Manuscript_Package/02_Scientific_Results/tables/Table_1_eligible_screens.csv"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)

st = pd.read_csv(TBL); st.columns = [c.strip() for c in st.columns]
st = st.rename(columns={"PMID": "study", "Cell model": "cell_line",
                        "Queries with >=1 positive": "n_queries"})
st["study"] = st["study"].astype(str)
studies = sorted(st.study.unique()); lines = sorted(st.cell_line.unique())
si = st.study.map({s: i for i, s in enumerate(studies)}).to_numpy()
ci = st.cell_line.map({c: i for i, c in enumerate(lines)}).to_numpy()
nq = st.n_queries.to_numpy(float)
S, G, K = len(st), len(lines), len(studies)

# --- Q1: connected components of the study x cell-model bipartite graph ----------------
par = {("S", s) for s in studies} | {("C", c) for c in lines}
par = {n: n for n in par}
def find(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for _, r in st.iterrows():
    ra, rb = find(("S", r.study)), find(("C", r.cell_line))
    if ra != rb: par[ra] = rb
roots = sorted({find(("C", c)) for c in lines}, key=str)
comp_of_line = np.array([roots.index(find(("C", c))) for c in lines])
comp_of_screen = np.array([roots.index(find(("C", c))) for c in st.cell_line])
P = len(roots)

def weights(idx, m):
    W = np.zeros((S, m)); W[np.arange(S), idx] = nq; W /= W.sum(0, keepdims=True); return W
def weights_flat(idx, m):
    W = np.zeros((S, m)); W[np.arange(S), idx] = 1.0; W /= W.sum(0, keepdims=True); return W

Wc = weights(ci, G)                 # cell-model arm, 8 values
Ws = weights_flat(si, K)            # study arm, 7 values  (what the released code used)
Wp = weights_flat(comp_of_screen, P)  # component arm, 5 INDEPENDENT values

def signs(n): return np.array([[1 if (k >> j) & 1 else -1 for j in range(n)]
                               for k in range(2 ** n)], float)
Sc, Ss, Sp = signs(G), signs(K), signs(P)

def p_two(x, M):
    s = np.abs(x @ M.T); return (s >= s[:, :1] - 1e-12).mean(1)
def p_one(x, M):
    """One-sided: the observed configuration is the all-+1 sign vector, which signs()
    places LAST (k = 2**n - 1); signs()[0] is the all-MINUS-1 vector."""
    s = x @ M.T; return (s >= s[:, -1:] - 1e-12).mean(1)

def draw(rng, kind, n, size):
    if kind.endswith("_left"):          # mirror image of a law: same shape, skew reversed
        return -draw(rng, kind[:-5], n, size)
    z = rng.standard_normal((n, size))
    if kind == "normal": return z
    if kind.startswith("gamma"):
        k = float(kind[5:]); g = rng.gamma(k, 1.0, (n, size)); return (g - k) / np.sqrt(k)
    if kind == "t3": return rng.standard_t(3, (n, size)) / np.sqrt(3.0)
    if kind == "chisq1": return (z ** 2 - 1) / np.sqrt(2)
    if kind == "lognormal":
        x = np.exp(z * 0.8); m = np.exp(0.32); v = (np.exp(0.64) - 1) * np.exp(0.64)
        return (x - m) / np.sqrt(v)
    raise ValueError(kind)

def wilson(k, n):
    if n == 0: return (float("nan"), float("nan"))
    lo, hi = sps.beta.ppf(0.025, k, n - k + 1) if k else 0.0, \
             sps.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return float(lo), float(hi)

rows = []
grid = [0.0, 0.2, 0.4]
LAWS = ("normal", "t3", "gamma4", "gamma1", "lognormal", "chisq1",
        "gamma4_left", "gamma1_left", "lognormal_left", "chisq1_left")
for kind in LAWS:
    for mu in (0.0, DELTA):
        for rs in grid:
            for rc in grid:
                if rs + rc > 1: continue
                rng = np.random.default_rng(SEED)
                a = draw(rng, kind, N_SIM, K) * np.sqrt(rs)
                b = draw(rng, kind, N_SIM, G) * np.sqrt(rc)
                r = draw(rng, kind, N_SIM, S) * np.sqrt(max(0.0, 1 - rs - rc))
                scr = a[:, si] + b[:, ci] + r + mu
                xc, xs, xp = scr @ Wc, scr @ Ws, scr @ Wp

                pc2, ps2, pp2 = p_two(xc, Sc), p_two(xs, Ss), p_two(xp, Sp)
                pp1 = p_one(xp, Sp)
                agree_cs = np.sign(xc.mean(1)) == np.sign(xs.mean(1))
                skew = sps.skew(xc, axis=1, bias=False)
                gate = np.abs(skew) <= GATE

                rej = {
                    # as released: conjunction over 8 cell models x 7 studies, two-sided
                    "A_released_conjunction_8x7": (pc2 <= ALPHA) & (ps2 <= ALPHA) & agree_cs,
                    # what the manuscript actually registers: study arm pooled to components
                    "B_registered_conjunction_8x5": (pc2 <= ALPHA) & (pp2 <= ALPHA) & agree_cs,
                    # cell-model arm alone at G=8, two-sided
                    "C_cellmodel_arm_8": pc2 <= ALPHA,
                    # the only honest unit count: 5 independent components, two-sided
                    "D_component_arm_5_twosided": pp2 <= ALPHA,
                    # 5 components, ONE-sided in the hypothesised direction
                    "E_component_arm_5_onesided": pp1 <= ALPHA,
                }
                for name, rj in rej.items():
                    k = int(rj.sum()); lo, hi = wilson(k, N_SIM)
                    kg = int((rj & gate).sum()); glo, ghi = wilson(kg, N_SIM)
                    npass = int(gate.sum())
                    kc = kg; clo, chi = wilson(kc, npass) if npass else (float("nan"),) * 2
                    rows.append(dict(errors=kind, mu_in_sd=mu, rho_within_study=rs,
                                     rho_shared_line=rc, procedure=name,
                                     rate=k / N_SIM, rate_lo=lo, rate_hi=hi,
                                     gated_uncond=kg / N_SIM, gated_uncond_lo=glo, gated_uncond_hi=ghi,
                                     gated_cond=(kc / npass if npass else float("nan")),
                                     gated_cond_lo=clo, gated_cond_hi=chi,
                                     gate_pass_rate=npass / N_SIM, n_sim=N_SIM))
df = pd.DataFrame(rows)
df.to_csv(OUT / "gate3_feasibility_results.csv", index=False)

attain = {f"{n} units": {"sign_vectors": 2 ** n,
                         "smallest_two_sided_p": 2 / 2 ** n,
                         "smallest_one_sided_p": 1 / 2 ** n,
                         "two_sided_reaches_0.05": bool(2 / 2 ** n <= ALPHA),
                         "one_sided_reaches_0.05": bool(1 / 2 ** n <= ALPHA)}
          for n in (5, 7, 8)}
summary = {"what_this_is": "design-only feasibility and validity resolution for the Gate 3 rule",
           "what_this_is_not": "not a hypothesis test; no average precision is read",
           "seed": SEED, "n_sim": N_SIM, "alpha": ALPHA, "delta_in_sd": DELTA,
           "gate_threshold": GATE,
           "structure": {"screens": S, "cell_models": G, "studies": K,
                         "independent_components": P,
                         "components": [sorted(str(x[1]) for x in
                                        [n for n in par if find(n) == rt]) for rt in roots]},
           "attainable_p_grid": attain,
           "by_procedure": {}}
h0 = df[df.mu_in_sd == 0.0]; h1 = df[df.mu_in_sd == DELTA]
ind = (df.rho_within_study == 0) & (df.rho_shared_line == 0)
for proc, g in h0.groupby("procedure"):
    gi = df[(df.procedure == proc) & ind & (df.mu_in_sd == 0.0)]
    p1 = df[(df.procedure == proc) & ind & (df.mu_in_sd == DELTA)]
    summary["by_procedure"][proc] = {
        "size_worst_over_grid": round(float(g.rate.max()), 4),
        "size_worst_upper95": round(float(g.loc[g.rate.idxmax(), "rate_hi"]), 4),
        "gated_size_worst_unconditional": round(float(g.gated_uncond.max()), 4),
        "gated_size_worst_CONDITIONAL_on_gate_passing": round(float(g.gated_cond.max()), 4),
        "gated_cond_worst_upper95": round(float(g.loc[g.gated_cond.idxmax(), "gated_cond_hi"]), 4),
        "power_at_delta_independence": round(float(p1.rate.mean()), 4),
        "gated_power_at_delta_independence": round(float(p1.gated_uncond.mean()), 4),
        "size_at_independence_normal": round(float(
            gi[gi.errors == "normal"].rate.iloc[0]), 4),
    }
json.dump(summary, open(OUT / "gate3_feasibility_summary.json", "w"), indent=1)
print(json.dumps({"structure": summary["structure"]["independent_components"],
                  "attainable": attain, "by_procedure": summary["by_procedure"]}, indent=1))
