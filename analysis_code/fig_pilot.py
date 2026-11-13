"""Figures 5 and 6 and Table 4, from the authorised pilot output only.

Usage: python3 fig_pilot.py <pilot_report_REAL.json> <figdir> <tabledir>
Every number drawn here is read from the report; nothing is typed in.
"""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

rep = json.load(open(sys.argv[1]))
FIG = Path(sys.argv[2]); FIG.mkdir(parents=True, exist_ok=True)
TAB = Path(sys.argv[3]); TAB.mkdir(parents=True, exist_ok=True)
vc = rep["variance_components"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "figure.dpi": 600,
                     "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = {"cell": "#3f6b9c", "study": "#9c6b3f", "grey": "#8a949c", "warn": "#b3443b"}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)
    print("wrote", name)


# ---------------- Figure 5: the cluster values the design actually has ----------------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"wspace": 0.30})

for ax, key, title in [(axes[0], "cluster_value_shape_eligible",
                        "a  Eligible screens (protocol §2.1)"),
                       (axes[1], "cluster_value_shape_all",
                        "b  All deposited non-BRCA screens")]:
    sh = vc[key]
    v = pd.Series(sh["cell_model_values"], dtype=float).sort_values()
    ax.axvline(0.0, color=C["grey"], lw=0.8, ls=":")
    ax.barh(np.arange(len(v)), v.to_numpy(),
            color=[C["cell"] if x >= 0 else C["warn"] for x in v])
    ax.set_yticks(np.arange(len(v)))
    ax.set_yticklabels(v.index, fontsize=6.5)
    ax.axvline(sh["mean"], color="k", lw=1.0)
    sk = sh["skewness_sample"]
    sub = (f"G = {sh['G']}  ·  mean {sh['mean']:+.4f}  ·  SD {sh['sd']:.4f}"
           + (f"  ·  skewness {sk:+.2f}" if sk is not None else ""))
    ax.set_title(title, loc="left", fontsize=8, pad=14)
    ax.annotate(sub, xy=(0.0, 1.012), xycoords="axes fraction", ha="left", va="bottom", fontsize=6.4)
    ax.set_xlabel("mean paired difference in average precision\n(unconditioned retrieval − popularity-only)",
                  fontsize=6.8)
save(fig, "Figure_5_pilot_cluster_values")

# ---------------- Figure 6: variance components and the detectable effect ----------------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.42})
ax = axes[0]
rows = [("eligible_screens_protocol_2_1", "eligible\nscreens"),
        ("all_screens_as_authorised", "all deposited\nnon-BRCA screens"),
        ("sensitivity_popularity_minus_random", "sensitivity:\npopularity − random")]
xs = np.arange(len(rows))
pts = [vc[k]["sd_between_cell_models_point"] for k, _ in rows]
los = [vc[k]["sd_between_cell_models_ci95"][0] for k, _ in rows]
his = [vc[k]["sd_between_cell_models_ci95"][1] for k, _ in rows]
ucl = [vc[k]["sd_between_cell_models_ucl80"] for k, _ in rows]
ax.errorbar(xs, pts, yerr=[np.array(pts) - np.array(los), np.array(his) - np.array(pts)],
            fmt="o", color=C["cell"], capsize=3, lw=1, ms=4, label="point estimate, 95 % cluster bootstrap")
ax.plot(xs, ucl, "_", color=C["warn"], ms=14, mew=1.6, label="80 % upper limit (used for planning)")
ax.set_xticks(xs); ax.set_xticklabels([lab for _, lab in rows], fontsize=6.5)
ax.set_ylabel("between-cell-model SD of the\nmean paired difference", fontsize=6.8)
ax.set_ylim(0, None)
ax.set_title("a  Between-context variability", loc="left", fontsize=8)
ax.legend(frameon=False, fontsize=6.0, loc="upper right", borderaxespad=0.2)

ax = axes[1]
e = vc["eligible_screens_protocol_2_1"]
lo, hi = 1.25, 1.50
ax.axhspan(lo, hi, color=C["grey"], alpha=0.22)
ax.annotate("registered planning range\n1.25–1.50 SD", xy=(0.5, (lo + hi) / 2), xycoords=("axes fraction", "data"),
            ha="center", va="center", fontsize=6.3)
sd_pt = e["sd_between_cell_models_point"]
raw = [e["detectable_difference_at_point_sd"], e["detectable_difference_at_ucl80"]]
vals = [r / sd_pt for r in raw]          # expressed in units of the measured point SD
labs = ["at the point\nestimate of SD", "at the 80 % upper\nlimit of SD"]
ax.bar(np.arange(2), vals, width=0.45, color=[C["cell"], C["warn"]])
for i, (v, r) in enumerate(zip(vals, raw)):
    ax.annotate(f"{v:.2f} SD\n({r:.4f} AP)", (i, v), textcoords="offset points", xytext=(0, 3),
                ha="center", fontsize=6.4)
ax.set_ylim(0, max(vals) * 1.35)
ax.set_xticks(np.arange(2)); ax.set_xticklabels(labs, fontsize=6.5)
ax.set_ylabel("smallest detectable difference\n(standard deviations)", fontsize=6.8)
ax.set_title(f"b  Detection floor at G = {e['G_cell_models']}", loc="left", fontsize=8)
save(fig, "Figure_6_pilot_components_and_floor")

# ---------------- Table 4 ----------------
out = []
for k, lab in [("eligible_screens_protocol_2_1", "Eligible screens (protocol §2.1)"),
               ("all_screens_as_authorised", "All deposited non-BRCA screens"),
               ("sensitivity_popularity_minus_random", "Sensitivity: popularity-only − random")]:
    c = vc[k]
    out.append({
        "Subset": lab,
        "Contrast": ("unconditioned retrieval − popularity-only"
                     if k != "sensitivity_popularity_minus_random" else "popularity-only − random"),
        "Cell models (G)": c["G_cell_models"],
        "Informative queries": c["n_queries"],
        "Mean paired difference": round(c["mean_difference"], 4),
        "Between-cell-model SD": round(c["sd_between_cell_models_point"], 4),
        "SD, 95% cluster bootstrap": f"{c['sd_between_cell_models_ci95'][0]:.4f} to {c['sd_between_cell_models_ci95'][1]:.4f}",
        "SD, 80% upper limit": round(c["sd_between_cell_models_ucl80"], 4),
        "ICC by cell model": round(c["rho_icc_point"], 4),
        "ICC, 95% cluster bootstrap": f"{c['rho_icc_ci95'][0]:.4f} to {c['rho_icc_ci95'][1]:.4f}",
        "Effective n": round(c["n_effective"], 1),
        "Detectable difference at point SD": round(c["detectable_difference_at_point_sd"], 4),
        "Detectable difference at 80% upper limit": round(c["detectable_difference_at_ucl80"], 4),
    })
pd.DataFrame(out).to_csv(TAB / "Table_4_pilot_variance_components.csv", index=False)
print("wrote Table_4_pilot_variance_components.csv")
