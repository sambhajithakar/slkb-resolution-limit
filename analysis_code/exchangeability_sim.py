"""Exchangeability / type I error sensitivity for the D1 = C conjunctive sign-flip rule.

Design-only simulation: reads the real eligible screen structure (study, cell model,
number of informative queries), never any observed AP value. Extends the staged
CC-02 dependence_sensitivity with (i) two-sided claims, (ii) heteroscedastic screens
(variance falling with the number of informative queries), and (iii) skewed,
non-sign-symmetric errors. Seeds fixed. Output: exchangeability_results.csv/.json
"""
import json, sys
import numpy as np, pandas as pd

SEED = 20261031
N_SIM = 20000
st = pd.read_csv(sys.argv[1])
st["study"] = st["study"].astype(str)
studies = sorted(st.study.unique()); lines = sorted(st.cell_line.unique())
si = st.study.map({s: i for i, s in enumerate(studies)}).to_numpy()
ci = st.cell_line.map({c: i for i, c in enumerate(lines)}).to_numpy()
nq = st.n_queries.to_numpy(float)
S = len(st)
Wc = np.zeros((S, len(lines))); Wc[np.arange(S), ci] = nq; Wc /= Wc.sum(0, keepdims=True)
Ws = np.zeros((S, len(studies))); Ws[np.arange(S), si] = 1.0; Ws /= Ws.sum(0, keepdims=True)

def signs(G):
    return np.array([[1 if (k >> j) & 1 else -1 for j in range(G)] for k in range(2 ** G)], float)
Sc, Ss = signs(len(lines)), signs(len(studies))

def p2(x, M):  # two-sided exact enumeration p, statistic |mean|
    stat = np.abs(x @ M.T)
    return (stat >= stat[:, :1] - 1e-12).mean(1)

def draw(rng, kind, n, size):
    z = rng.standard_normal((n, size))
    if kind == "normal":
        return z
    if kind.startswith("gamma"):   # skewness 2/sqrt(k), mean 0, var 1
        k = float(kind[5:]); g = rng.gamma(k, 1.0, (n, size)); return (g - k) / np.sqrt(k)
    if kind == "t3":   # symmetric, heavy-tailed, var 1
        return rng.standard_t(3, (n, size)) / np.sqrt(3.0)
    if kind == "chisq1":   # strongly right-skewed, mean 0, var 1
        return (z ** 2 - 1) / np.sqrt(2)
    if kind == "lognormal":
        x = np.exp(z * 0.8); m = np.exp(0.32); v = (np.exp(0.64) - 1) * np.exp(0.64)
        return (x - m) / np.sqrt(v)
    raise ValueError(kind)

def run(rho_s, rho_c, kind="normal", hetero=False, n=N_SIM, seed=SEED):
    rng = np.random.default_rng(seed)
    if rho_s + rho_c > 1: return None
    a = draw(rng, kind, n, len(studies)) * np.sqrt(rho_s)
    b = draw(rng, kind, n, len(lines)) * np.sqrt(rho_c)
    r = draw(rng, kind, n, S) * np.sqrt(1 - rho_s - rho_c)
    if hetero:  # residual SD proportional to 1/sqrt(informative queries), rescaled to mean variance 1
        sc = 1 / np.sqrt(nq); sc /= np.sqrt((sc ** 2).mean()); r = r * sc
    scr = a[:, si] + b[:, ci] + r
    xc, xs = scr @ Wc, scr @ Ws
    pc, ps = p2(xc, Sc), p2(xs, Ss)
    mc, ms = xc.mean(1), xs.mean(1)
    cell2 = pc <= 0.05; study2 = ps <= 0.05
    conj2 = cell2 & study2 & (np.sign(mc) == np.sign(ms))
    conj1 = conj2 & (mc > 0)
    from scipy import stats as sps
    tc = mc / (xc.std(1, ddof=1) / np.sqrt(xc.shape[1])); pt = 2 * sps.t.sf(np.abs(tc), xc.shape[1] - 1)
    return dict(rho_within_study=rho_s, rho_shared_line=rho_c, errors=kind, heteroscedastic=hetero,
                size_cell_two_sided=cell2.mean(), size_study_two_sided=study2.mean(),
                size_conjunction_two_sided=conj2.mean(), size_conjunction_one_sided_positive=conj1.mean(),
                size_cell_paired_t_two_sided=(pt <= 0.05).mean(),
                size_cell_one_sided_positive=(cell2 & (mc > 0)).mean(),
                arm_mean_correlation=float(np.corrcoef(mc, ms)[0, 1]),
                mc_se_at_0p05=float(np.sqrt(0.05 * 0.95 / n)), n_sim=n)

rows = []
grid = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6]
for kind in ("normal", "t3", "gamma16", "gamma4", "gamma1", "lognormal", "chisq1"):
    for hetero in (False, True):
        for rs in grid:
            for rc in grid:
                out = run(rs, rc, kind, hetero)
                if out: rows.append(out)
df = pd.DataFrame(rows)
df.to_csv("exchangeability_results.csv", index=False)
summ = {}
for (kind, het), g in df.groupby(["errors", "heteroscedastic"]):
    summ[f"{kind}|hetero={het}"] = {
        "max_cell_two_sided": round(g.size_cell_two_sided.max(), 4),
        "max_study_two_sided": round(g.size_study_two_sided.max(), 4),
        "max_conjunction_two_sided": round(g.size_conjunction_two_sided.max(), 4),
        "max_cell_paired_t": round(g.size_cell_paired_t_two_sided.max(), 4),
        "at_independence": g[(g.rho_within_study == 0) & (g.rho_shared_line == 0)][
            ["size_cell_two_sided", "size_study_two_sided", "size_conjunction_two_sided", "size_cell_paired_t_two_sided"]].round(4).to_dict("records")[0],
        "worst_cell_cell": g.loc[g.size_cell_two_sided.idxmax(), ["rho_within_study", "rho_shared_line"]].to_dict(),
    }
json.dump({"seed": SEED, "n_sim": N_SIM, "structure": {"screens": S, "cell_models": len(lines), "studies": len(studies)},
           "summary": summ}, open("exchangeability_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
