"""Figure 2: the attainable p-grid and the detection floor, both properties of the design."""
import sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sps

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "axes.labelsize": 8, "legend.fontsize": 7, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 600, "savefig.bbox": "tight"})
C = {"cell": "#1b6ca8", "study": "#c1583a", "comp": "#2f6d4f", "one": "#7a6ea8", "ref": "#555555"}

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.33})
ax = axes[0]
for n, col, lab in ((8, C["cell"], "8 cell models, two-sided"),
                    (7, C["study"], "7 studies, two-sided"),
                    (5, C["comp"], "5 components, two-sided")):
    p = np.array([2 * k / 2 ** n for k in range(1, 9)])
    ax.plot(range(1, 9), p, "o-", ms=3.2, lw=1.2, color=col, label=lab)
p1 = np.array([k / 2 ** 5 for k in range(1, 9)])
ax.plot(range(1, 9), p1, "s--", ms=3.2, lw=1.1, color=C["one"], label="5 components, one-sided")
ax.axhline(0.05, ls="--", lw=0.9, color=C["ref"])
ax.annotate(r"$\alpha = 0.05$", (5.9, 0.057), fontsize=6.5, color=C["ref"])
ax.annotate("0.0625", (1.0, 0.0625), fontsize=6.5, color=C["comp"],
            xytext=(1.45, 0.105), arrowprops=dict(arrowstyle="->", color=C["comp"], lw=0.8))
ax.set_yscale("log")
ax.set_xlabel("rank of the attainable $p$-value")
ax.set_ylabel("attainable $p$")
ax.set_title("a  The exact reference set is finite", loc="left")
ax.legend(frameon=False, fontsize=6.3, loc="lower right")

ax = axes[1]
ns = np.arange(4, 23)
floor_pt = np.array([(sps.t.ppf(0.975, n - 1) + sps.t.ppf(0.80, n - 1)) / np.sqrt(n) for n in ns])
ucl = np.array([np.sqrt((n - 1) / sps.chi2.ppf(0.20, n - 1)) for n in ns])
ax.plot(ns, floor_pt, "-", lw=1.4, color=C["cell"], label="at the point SD")
ax.plot(ns, floor_pt * ucl, "-", lw=1.4, color=C["study"],
        label="at the 80 % upper limit on the SD")
for n in (7, 8):
    i = list(ns).index(n)
    ax.plot([n], [floor_pt[i]], "o", ms=4, color=C["cell"])
    ax.annotate(f"n={n}: {floor_pt[i]:.2f} SD", (n + 0.4, floor_pt[i] + 0.05), fontsize=6.5)
i5 = list(ns).index(5)
ax.plot([5], [floor_pt[i5]], "x", ms=6, color=C["comp"], mew=1.6)
ax.annotate("n=5: no two-sided\ndetectable effect exists", (5.4, floor_pt[i5] + 0.10),
            fontsize=6.5, color=C["comp"])
ax.set_xlabel("number of mutually independent units, $n$")
ax.set_ylabel("detectable difference (between-unit SD)")
ax.set_title("b  The detection floor follows from $n$", loc="left")
ax.legend(frameon=False, fontsize=6.5)
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"Figure_2_attainable_and_floor.{ext}")
plt.close(fig); print("wrote Figure_2_attainable_and_floor")
