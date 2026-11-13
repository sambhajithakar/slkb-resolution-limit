"""Figure 1: study design and data flow. Schematic only - every count shown is read from
the audit and pilot outputs passed on the command line, never typed in."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
rep = json.load(open(sys.argv[2]))
st = pd.read_csv(sys.argv[3])
cm = rep["corpus"]; qs = rep["query_set"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "figure.dpi": 600,
                     "savefig.bbox": "tight"})
C = {"data": "#dde6ee", "proc": "#eef1e9", "out": "#f4e7e2", "edge": "#44515c", "txt": "#1d2227"}

fig, ax = plt.subplots(figsize=(7.2, 4.9))
ax.set_xlim(0, 10); ax.set_ylim(-0.05, 6.6); ax.axis("off")


def box(x, y, w, h, title, body, kind):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.10",
                                fc=C[kind], ec=C["edge"], lw=0.8))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=8, fontweight="bold",
            color=C["txt"])
    ax.text(x + w / 2, y + h - 0.52, body, ha="center", va="top", fontsize=6.8, color=C["txt"],
            linespacing=1.45)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9,
                                 lw=0.9, color=C["edge"], shrinkA=1, shrinkB=1))


n_src = sum(int(v) for v in rep["query_set_provenance"]["source_rows_by_study"].values())
box(0.1, 4.7, 4.5, 1.7, "SLKB deposited database",
    f"official FigShare SQL dump, MD5 verified\n{n_src:,} deposited screened pairs, 11 source studies\n"
    f"label = each study's own published SL call\n(no threshold set or derived here)", "data")
box(5.4, 4.7, 4.5, 1.7, "PubMed 2026 annual baseline",
    f"{cm['n_files']:,} files, each MD5-verified on download\n"
    f"eligibility date = Entrez date (cut-off {cm['cutoff']})\n"
    f"{cm['n_documents']:,} documents in the frozen snapshot\nall 11 label-generating papers excluded", "data")

box(0.1, 2.9, 4.5, 1.45, "Eligibility (fixed in advance)",
    f"≥10 candidates per anchor, ≥10 relevant pairs,\nprevalence window\n"
    f"→ {len(st)} screens · {st.cell_line.nunique()} cell models · {st.study.nunique()} source studies\n"
    f"→ {int(st.n_queries_all.sum()):,} queries, {int(st.n_queries.sum()):,} with a positive", "proc")
box(5.4, 2.9, 4.5, 1.45, "Registered baselines",
    "popularity-only (NCBI gene2pubmed)\nrandom at prevalence\nunconditioned retrieval (BM25, anchor term)\n"
    "candidate order randomised, ties break on symbol", "proc")

box(0.1, 1.45, 4.5, 1.2, "Pilot (authorised 25 Oct 2026)",
    "variance components of the registered pair\nunconditioned − popularity, by cell model\n"
    "cluster bootstrap; no hypothesis tested", "out")
box(5.4, 1.45, 4.5, 1.2, "Design-only simulation",
    "type I error of each arm and of the conjunction\nover the real screen structure\n"
    "dependence × error law × heteroscedasticity", "out")

box(0.1, 0.05, 9.8, 1.15, "Confirmatory evaluation — REGISTERED, NOT RUN",
    "systems under test are not built; no confirmatory p-value, interval or claim exists\n"
    "requires a signed analysis plan, a dated protocol freeze, named and consenting\n"
    "H3 adjudicators, and explicit permission to begin", "proc")

arrow(2.35, 4.7, 2.35, 4.35); arrow(7.65, 4.7, 7.65, 4.35)
arrow(4.6, 3.6, 5.4, 3.6)
arrow(2.35, 2.9, 2.35, 2.68); arrow(7.65, 2.9, 7.65, 2.68)
arrow(2.35, 1.45, 2.35, 1.22); arrow(7.65, 1.45, 7.65, 1.22)
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"Figure_1_design_and_data_flow.{ext}")
print("wrote Figure_1_design_and_data_flow")
