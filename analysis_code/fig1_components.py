"""Figure 1: the eligible design as a bipartite graph of source studies and cell models,
with its five connected components. Reads Table 1 only."""
import sys
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
                     "figure.dpi": 600, "savefig.bbox": "tight"})
st = pd.read_csv("/mnt/project-files/12_Q1_Manuscript_Package/02_Scientific_Results/tables/Table_1_eligible_screens.csv")
st.columns = [c.strip() for c in st.columns]
st = st.rename(columns={"Source study": "study", "Cell model": "cell",
                        "Queries with >=1 positive": "npos",
                        "Published SL call rate (%)": "rate"})

COMP = [(["Shen 2017", "Zhao 2018"], ["293T", "A549", "HELA"]),
        (["Han 2017", "Horlbeck 2018"], ["K562", "JURKAT"]),
        (["Diehl 2021"], ["RPE1"]),
        (["Wong 2016"], ["OVCAR8"]),
        (["Tang 2022"], ["22RV1"])]
COL = ["#c1583a", "#1b6ca8", "#8a8f98", "#8a8f98", "#8a8f98"]
SPREAD = 1.35   # vertical space between nodes inside a component

fig, ax = plt.subplots(figsize=(7.2, 4.1))
ypos, y = {}, 0.0
study_xy, cell_xy = {}, {}
for ci, ((studies, cells), col) in enumerate(zip(COMP, COL)):
    h = max(len(studies), len(cells))
    top = y
    for i, s in enumerate(studies):
        study_xy[s] = (0.0, y + ((h - len(studies)) / 2 + i) * SPREAD)
    for i, c in enumerate(cells):
        cell_xy[c] = (1.0, y + ((h - len(cells)) / 2 + i) * SPREAD)
    ax.add_patch(FancyBboxPatch((-0.40, top - 0.52), 1.80, (h - 1) * SPREAD + 1.04,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=col, ec="none", alpha=0.08, zorder=0))
    ax.annotate(f"component {len(COMP) - ci}", (1.52, top + (h - 1) * SPREAD / 2), va="center",
                fontsize=7.5, color=col, fontweight="bold")
    y += (h - 1) * SPREAD + 1.55

for _, r in st.iterrows():
    x0, y0 = study_xy[r.study]; x1, y1 = cell_xy[r.cell]
    ax.plot([x0 + 0.17, x1 - 0.17], [y0, y1], lw=1.0, color="#999999", zorder=1)
for s, (x, yy) in study_xy.items():
    ax.annotate(s, (x, yy), ha="center", va="center", fontsize=7.2, zorder=2,
                bbox=dict(boxstyle="round,pad=0.26", fc="white", ec="#555555", lw=0.7))
for c, (x, yy) in cell_xy.items():
    n = int(st[st.cell == c].npos.sum())
    ax.annotate(f"{c}\n{n} queries", (x, yy), ha="center", va="center", fontsize=6.8, zorder=2,
                bbox=dict(boxstyle="round,pad=0.26", fc="#f4f4f4", ec="#555555", lw=0.7))
ax.annotate("7 source studies", (0.0, y - 0.35), ha="center", fontsize=8, fontweight="bold")
ax.annotate("8 cell models", (1.0, y - 0.35), ha="center", fontsize=8, fontweight="bold")
ax.annotate("5 independent units", (1.52, y - 0.35), ha="left", fontsize=8, fontweight="bold")
ax.set_xlim(-0.55, 2.35); ax.set_ylim(-0.9, y + 0.1)
ax.axis("off")
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"Figure_1_design_components.{ext}")
plt.close(fig); print("wrote Figure_1_design_components")
