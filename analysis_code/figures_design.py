"""Publication figures that depend only on the design and on the simulations in this folder.
No study result, no confirmatory outcome. Outputs PNG (600 dpi) and PDF."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "legend.fontsize": 7, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 600, "savefig.bbox": "tight"})
C = {"cell": "#1b6ca8", "study": "#c1583a", "conj": "#2f6d4f", "t": "#7a6ea8", "ref": "#555555"}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}")
    plt.close(fig)
    print("wrote", name)


res = pd.read_csv("exchangeability_results.csv")
st = pd.read_csv(sys.argv[2])

# ---- Figure: size vs dependence, symmetric errors; and size vs skew ----
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
ax = axes[0]
g = res[(res.errors == "normal") & (~res.heteroscedastic) & (res.rho_shared_line == 0.0)]
for k, lab in (("size_cell_two_sided", "cell-model arm"), ("size_study_two_sided", "study arm"),
               ("size_conjunction_two_sided", "conjunction (claim rule)"),
               ("size_cell_paired_t_two_sided", "paired $t$, cell-model arm")):
    key = {"size_cell_two_sided": "cell", "size_study_two_sided": "study",
           "size_conjunction_two_sided": "conj", "size_cell_paired_t_two_sided": "t"}[k]
    ax.plot(g.rho_within_study, g[k], "o-", ms=3, lw=1.2, color=C[key], label=lab)
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.annotate("nominal 0.05", (0.45, 0.052), fontsize=6.5, color=C["ref"])
ax.set_xlabel(r"within-study correlation $\rho_{\mathrm{study}}$  (shared-line $\rho=0$)")
ax.set_ylabel("type I error, two-sided")
ax.set_title("a  Dependence, with symmetric errors", loc="left")
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylim(0, 0.18); ax.legend(frameon=False)

ax = axes[1]
order = [("normal", "normal\n0"), ("t3", "$t_3$\n0"), ("gamma16", "gamma\n0.5"),
         ("gamma4", "gamma\n1.0"), ("gamma1", "expon.\n2.0"), ("chisq1", "$\\chi^2_1$\n2.8"),
         ("lognormal", "lognorm.\n2.9")]
x = np.arange(len(order)); w = 0.27
for off, col, kk, lab in [(-w, "size_cell_two_sided", "cell", "cell-model arm"),
                          (0.0, "size_study_two_sided", "study", "study arm"),
                          (w, "size_conjunction_two_sided", "conj", "conjunction")]:
    v = [res[(res.errors == e) & (~res.heteroscedastic) & (res.rho_within_study == 0) &
             (res.rho_shared_line == 0)][col].iat[0] for e, _ in order]
    ax.bar(x + off, v, w, color=C[kk], label=lab)
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.set_xticks(x); ax.set_xticklabels([l for _, l in order], fontsize=6)
ax.set_xlabel("error distribution of the cluster values, and its skewness")
ax.set_title("b  Skew, at independence", loc="left")
ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylim(0, 0.18)
ax.legend(frameon=False)
fig.subplots_adjust(wspace=0.28)
save(fig, "Figure_3_inference_validity")

# ---- Figure: the four candidate confirmatory procedures ----
alt = pd.read_csv("alternative_procedures_results.csv")
PROC = [("P1_conjunction", "conjunction\n(registered)", "conj"),
        ("P2_conjunction_gated", "conjunction +\nsymmetry gate", "cell"),
        ("P3_conjunction_signtest", "conjunction of\nsign tests", "study"),
        ("P4_cell_wilcoxon", "Wilcoxon,\ncell-model arm", "t")]
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.30})
h0 = alt[alt.mu_in_sd == 0.0]
h1 = alt[(alt.mu_in_sd > 0) & (alt.rho_within_study == 0) & (alt.rho_shared_line == 0)]
laws = [("normal", "normal"), ("t3", "$t_3$"), ("gamma4", "gamma"),
        ("gamma1", "expon."), ("lognormal", "lognorm."), ("chisq1", "$\\chi^2_1$")]
x = np.arange(len(laws)); w = 0.2
ax = axes[0]
for i, (col, lab, kk) in enumerate(PROC):
    v = [h0[h0.errors == e][col].max() for e, _ in laws]
    ax.bar(x + (i - 1.5) * w, v, w, color=C[kk], label=lab.replace("\n", " "))
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.set_xticks(x); ax.set_xticklabels([l for _, l in laws], fontsize=6.5)
ax.set_ylabel("worst measured size over the\ndependence grid, two-sided", fontsize=7)
ax.set_title("a  Only the gated rule holds below 0.05", loc="left")
ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylim(0, 0.14)
ax.legend(frameon=False, fontsize=5.8, ncol=2)
ax = axes[1]
for i, (col, lab, kk) in enumerate(PROC):
    v = [h1[h1.errors == e][col].iat[0] for e, _ in laws]
    ax.bar(x + (i - 1.5) * w, v, w, color=C[kk])
ax.axhline(0.80, ls="--", lw=0.9, color=C["ref"])
ax.annotate("target 80 %", (-0.45, 1.10), fontsize=6.5, color=C["ref"])
ax.set_xticks(x); ax.set_xticklabels([l for _, l in laws], fontsize=6.5)
ax.set_ylabel("power at the recalculated\neffect of 1.40 SD", fontsize=7)
ax.set_title("b  and it costs power to do so", loc="left")
ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylim(0, 1.22)
fig.text(0.5, -0.07, "error distribution of the cluster values", ha="center", fontsize=8)
save(fig, "Figure_7_candidate_procedures")

# ---- Figure: attainable p-grid and detection floor vs G ----
from scipy import stats as sps
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
ax = axes[0]
for G, col in ((8, C["cell"]), (7, C["study"]), (5, C["t"])):
    p = np.array([2 * k / 2 ** G for k in range(1, 9)])
    ax.plot(range(1, 9), p, "o-", ms=3, lw=1.2, color=col, label=f"G = {G}")
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.annotate(r"$\alpha=0.05$", (6.2, 0.056), fontsize=6.5, color=C["ref"])
ax.set_yscale("log"); ax.set_xlabel("rank of the attainable two-sided $p$-value")
ax.set_ylabel("attainable $p$"); ax.set_title("a  Exact reference set is finite", loc="left")
ax.legend(frameon=False)

ax = axes[1]
Gs = np.arange(4, 23)
floor_pt = [(sps.t.ppf(0.975, G - 1) + sps.t.ppf(0.80, G - 1)) / np.sqrt(G) for G in Gs]
ucl = [np.sqrt((G - 1) / sps.chi2.ppf(0.20, G - 1)) for G in Gs]
ax.plot(Gs, floor_pt, "-", lw=1.4, color=C["cell"], label="at the point SD")
ax.plot(Gs, np.array(floor_pt) * np.array(ucl), "-", lw=1.4, color=C["study"],
        label="at the 80 % upper limit on the SD")
for G in (5, 7, 8):
    i = list(Gs).index(G)
    ax.plot([G], [floor_pt[i]], "o", ms=4, color=C["cell"])
    ax.annotate(f"G={G}: {floor_pt[i]:.2f} SD", (G + 0.3, floor_pt[i] + 0.04), fontsize=6.5)
ax.set_xlabel("number of independent clusters, $G$")
ax.set_ylabel("detectable difference (between-cluster SD)")
ax.set_title("b  Detection floor is a property of the design", loc="left")
ax.legend(frameon=False)
save(fig, "Figure_4_detection_floor")

# ---- Figure: screen structure ----
fig, ax = plt.subplots(figsize=(7.2, 3.1))
st = st.sort_values(["study", "cell_line"]).reset_index(drop=True)
y = np.arange(len(st))
ax.barh(y, st.n_queries_all, color="#cdd9e5", label="queries in the screen")
ax.barh(y, st.n_queries, color=C["cell"], label="queries with at least one positive")
ax.set_yticks(y)
ax.set_yticklabels([f"{r.cell_line}  ·  {r.study}" for r in st.itertuples()], fontsize=6.5)
for i, r in enumerate(st.itertuples()):
    ax.annotate(f"published SL rate {r.prevalence*100:.2f}%", (st.n_queries_all.max() * 0.52, i),
                va="center", fontsize=6)
ax.set_xlabel("number of queries (anchor genes)")
ax.set_title("Eligible screens: 11 screens, 8 cell models, 7 source studies", loc="left")
ax.legend(frameon=False, loc="lower right")
ax.invert_yaxis()
save(fig, "Figure_2_screen_structure")
