# SLKB resolution limit: audit, criterion and calculator

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24201153.svg)](https://doi.org/10.5281/zenodo.24201153)

Analysis code, stored results and the reproduction instructions accompanying the manuscript:

> **Machine-learning benchmarks for synthetic lethality have a computable resolution limit: a pre-study criterion from the sharing structure of pooled CRISPR screens**
> Sambhaji Balaso Thakar and Pradnya Namdev Ghorpade
> Submitted to *Computational Biology and Chemistry* (Elsevier), November 2026.

## What the work shows

The independent units of a combinatorial CRISPR screen resource are the connected components, *G*
in number, of its bipartite study × cell-model incidence graph. An exact, non-randomised
sign-symmetry test on *G* units has a reference distribution supported on multiples of 2^−G, so its
smallest attainable two-sided p-value is 2^(1−G). Requiring that floor to lie at or below the chosen
level gives a criterion computable from deposited metadata alone: at α = 0.05 such a test can reject
only when **G ≥ 6** two-sided, and **G ≥ 5** one-sided.

Applied to the Synthetic Lethality Knowledge Base, the eligible subset gives **G = 5** and the
complete 32-screen deposit gives **G = 3**, because 29 of its screens coalesce into a single
component. Simulating the real sharing structure under ten error laws, the type I error of every
decision rule the design admits is measured: the two that can reject at all reach **0.112** and
**0.136**, and gating on a symmetry pretest raises the conditional rate rather than restoring
control.

**No new laboratory measurements are reported.** The audit and the variance-component pilot run on
public deposited data; the type I error figures are simulations under stated generative models.

## The calculator

`analysis_code/feasibility.py` returns *G* and the attainable floor for any deposited resource:

```bash
python3 analysis_code/feasibility.py
```

It prints the minimum *G* for an exact test to be able to reject at α = 0.05, then *G*, the
component structure and the attainable floor for SLKB as a whole and for each deposited study.

## Layout

| Path | Content |
|---|---|
| `analysis_code/` | the analysis scripts, the manuscript assembler and its section sources, the verified-reference file and the tests |
| `analysis_code/feasibility.py` | the released calculator |
| `analysis_code/gate3_feasibility_sim.py` | the simulation over the real sharing structure |
| `analysis_code/run_pilot_real.py` | the variance-component pilot |
| `analysis_code/tests/` | packaged tests |
| `*.json`, `*.csv` (top level) | stored results: the feasibility table, the simulation grid, the pilot report and the per-query aggregates |
| `Statistical_Verification_Report.md`, `Reference_Verification_Report.md`, `Reproducibility_Documentation.md` | verification records |
| `Prior_Art_Comparison_2025_2026.csv` | the 2025–2026 comparison behind Discussion 5.4 |

## Reproducing

Requires Python 3 with NumPy, SciPy and pandas (`analysis_code/requirements.txt`). The packaged
tests run with:

```bash
cd analysis_code && python3 -m pytest -q tests/
```

Every simulation uses the seed recorded in its result file (20261103) and 40 000 replicates, so
reported values reproduce exactly. No tabulated value is entered by hand.

## Input data

No input data are redistributed here. The labels come from the Synthetic Lethality Knowledge Base
(Gökbağ et al., 2024, doi:10.1093/nar/gkad806) through its own deposited SQL dump; gene popularity
from NCBI Gene `gene2pubmed` and `Homo_sapiens.gene_info`; and the retrieval corpus from the PubMed
annual baseline. Each input is identified in `pilot_report_REAL.json` by its SHA-256 and download
date, so the exact version used can be recovered from its original source.

## Archived version

The version submitted with the manuscript is archived at Zenodo:
doi:[10.5281/zenodo.24201153](https://doi.org/10.5281/zenodo.24201153) (release `v1.0.0`).
The all-versions DOI is [10.5281/zenodo.24201152](https://doi.org/10.5281/zenodo.24201152).

## Licence

Code: MIT (see `LICENSE`). The stored result files are released under the same terms.
