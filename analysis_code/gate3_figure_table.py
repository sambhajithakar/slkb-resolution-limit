"""Figure 3 and Table 3 of the revised manuscript: feasibility and validity of every
candidate confirmatory rule at the real design. Reads only the design-only simulation."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

SRC = Path(sys.argv[1]); OUTF = Path(sys.argv[2]); OUTT = Path(sys.argv[3])
OUTF.mkdir(parents=True, exist_ok=True); OUTT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "legend.fontsize": 7, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 600, "savefig.bbox": "tight"})
C = {"A": "#c1583a", "B": "#2f6d4f", "C": "#1b6ca8", "E": "#7a6ea8", "ref": "#555555"}

df = pd.read_csv(SRC / "gate3_feasibility_results.csv")
summ = json.load(open(SRC / "gate3_feasibility_summary.json"))
h0 = df[df.mu_in_sd == 0.0]
h1 = df[df.mu_in_sd == 1.40]

LAW = [("normal", "norm\n0.0"), ("t3", "$t_3$\n0.0"),
       ("gamma4_left", "$\\Gamma_4$\n$-1.0$"), ("gamma4", "$\\Gamma_4$\n$+1.0$"),
       ("gamma1_left", "exp\n$-2.0$"), ("gamma1", "exp\n$+2.0$"),
       ("chisq1_left", "$\\chi^2_1$\n$-2.8$"), ("chisq1", "$\\chi^2_1$\n$+2.8$"),
       ("lognormal_left", "LN\n$-3.7$"), ("lognormal", "LN\n$+3.7$")]
PROC = [("A_released_conjunction_8x7", "A", "conjunction, study arm as 7 studies"),
        ("B_registered_conjunction_8x5", "B", "conjunction, study arm as 5 components"),
        ("C_cellmodel_arm_8", "C", "cell-model arm alone, 8 values"),
        ("E_component_arm_5_onesided", "E", "one-sided, 5 components")]

fig, axes = plt.subplots(1, 2, figsize=(7.3, 3.5),
                         gridspec_kw={"width_ratios": [1.65, 1.0], "wspace": 0.42})
ax = axes[0]
x = np.arange(len(LAW)); w = 0.21
for i, (key, ck, lab) in enumerate(PROC):
    v = [h0[(h0.errors == e) & (h0.procedure == key)].rate.max() for e, _ in LAW]
    ax.bar(x + (i - 1.5) * w, v, w, color=C[ck], label=f"{ck}  {lab}")
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.annotate("nominal 0.05", (len(LAW) - 1.1, 0.053), fontsize=6, color=C["ref"])
ax.annotate("B is zero at every law:\nit can never reject", (1.9, 0.158),
            fontsize=6, color=C["B"], ha="center")
ax.annotate("", xy=(1.5, 0.004), xytext=(1.9, 0.150),
            arrowprops=dict(arrowstyle="->", color=C["B"], lw=0.8))
ax.set_xticks(x); ax.set_xticklabels([l for _, l in LAW], fontsize=5.6)
ax.set_xlabel("error law of the cluster values, and its skewness")
ax.set_ylabel("type I error, worst over dependence")
ax.set_title("a  Every attainable rule exceeds the nominal level", loc="left", fontsize=8.5)
ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylim(0, 0.215)
ax.legend(frameon=False, loc="upper left", fontsize=5.8, handlelength=1.2,
          borderpad=0.1, labelspacing=0.25)

ax = axes[1]
sub = [("A_released_conjunction_8x7", "A"), ("C_cellmodel_arm_8", "C"),
       ("E_component_arm_5_onesided", "E")]
x2 = np.arange(len(sub)); w2 = 0.26
unc = [h0[h0.procedure == k].rate.max() for k, _ in sub]
gun = [h0[h0.procedure == k].gated_uncond.max() for k, _ in sub]
gcd = [h0[h0.procedure == k].gated_cond.max() for k, _ in sub]
for off, v, c, lab in ((-w2, unc, "#b0b0b0", "ungated"),
                       (0.0, gun, "#6f9ec4", "gated, unconditional"),
                       (w2, gcd, "#c1583a", "gated, given the gate passed")):
    ax.bar(x2 + off, v, w2, color=c, label=lab)
    for xi, vi in zip(x2 + off, v):
        ax.annotate(f"{vi:.3f}", (xi, vi + 0.004), ha="center", fontsize=5.4)
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.set_xticks(x2); ax.set_xticklabels([c for _, c in sub])
ax.set_xlabel("procedure")
ax.set_ylabel("type I error, worst overall")
ax.set_title("b  The gate moves the error,\n    it does not remove it", loc="left", fontsize=8.5)
ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylim(0, 0.215)
ax.legend(frameon=False, fontsize=5.8, loc="upper left", handlelength=1.2,
          borderpad=0.1, labelspacing=0.25)
for ext in ("png", "pdf"):
    fig.savefig(OUTF / f"Figure_3_procedure_validity.{ext}")
plt.close(fig); print("wrote Figure_3_procedure_validity")

# ---- Table 3 -------------------------------------------------------------------------
rows = []
NAMES = {"A_released_conjunction_8x7":
         "Conjunction, cell-model arm (8) and study arm treated as 7 independent studies",
         "B_registered_conjunction_8x5":
         "Conjunction, cell-model arm (8) and study arm pooled to its 5 independent components",
         "C_cellmodel_arm_8": "Cell-model arm alone, 8 values, two-sided",
         "D_component_arm_5_twosided": "Component arm alone, 5 values, two-sided",
         "E_component_arm_5_onesided": "Component arm alone, 5 values, one-sided"}
GRID = {"A_released_conjunction_8x7": "0.0078 (cell) and 0.0156 (study)",
        "B_registered_conjunction_8x5": "0.0078 (cell) and 0.0625 (components)",
        "C_cellmodel_arm_8": "0.0078", "D_component_arm_5_twosided": "0.0625",
        "E_component_arm_5_onesided": "0.0312"}
for key, name in NAMES.items():
    g0 = h0[h0.procedure == key]; g1 = h1[h1.procedure == key]
    ind1 = g1[(g1.rho_within_study == 0) & (g1.rho_shared_line == 0) & (g1.errors == "normal")]
    rows.append({
        "Procedure": name,
        "Smallest attainable two-sided p": GRID[key],
        "Can reach 0.05": "no" if g0.rate.max() == 0 else "yes",
        "Size, normal errors, independence": round(float(
            g0[(g0.errors == "normal") & (g0.rho_within_study == 0)
               & (g0.rho_shared_line == 0)].rate.iloc[0]), 4),
        "Size, worst over all laws and dependence": round(float(g0.rate.max()), 4),
        "Upper 95 % limit on that worst size": round(float(g0.loc[g0.rate.idxmax(), "rate_hi"]), 4),
        "Gated size, unconditional, worst": round(float(g0.gated_uncond.max()), 4),
        "Gated size, conditional on the gate passing, worst": round(float(g0.gated_cond.max()), 4),
        "Power at 1.40 SD, normal errors, independence": round(float(ind1.rate.iloc[0]), 4),
    })
t = pd.DataFrame(rows)
t.to_csv(OUTT / "Table_3_procedure_feasibility.csv", index=False)
print(t.to_string(index=False))
