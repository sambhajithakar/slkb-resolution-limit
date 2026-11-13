# Analysis code released with the manuscript

**BRCA_RAG_ · Project 1 · 31 October 2026**

Everything here reproduces a number that appears in the manuscript, the supplement, a figure or a
table. Nothing here is a system under test, and nothing here runs the confirmatory analysis — that
code does not exist yet, by design.

## What depends on what

| Script | Produces | Needs |
|---|---|---|
| `corpus_worker.py` | the date-bounded PubMed snapshot, as per-file parts plus a manifest | network access to NCBI's baseline FTP mirror; the staged `pubmed_to_jsonl` parser; `leakage_exclusion_list.csv` |
| `gene_index.py` | the gene-pair-restricted BM25 index used by the pilot's retrieval arm | the corpus parts |
| `screen_table.py` | `screen_table.csv` → `Table_1_eligible_screens.csv` | the rebuilt SLKB SQLite database |
| `run_pilot_real.py` | `pilot_report_REAL.json`, the per-query CSVs and the paired differences | SLKB SQLite, the corpus parts, NCBI `gene2pubmed` and `Homo_sapiens.gene_info` |
| `exchangeability_sim.py` | `exchangeability_results.csv` (294 scenarios), `exchangeability_summary.json` → Table 3 | `Table_1_eligible_screens.csv` only — it reads no observed value |
| `figures_design.py` | Figures 2, 3 and 4 | the screen table and the simulation results |
| `fig1_design.py` | Figure 1 | the pilot report and the screen table |
| `fig_pilot.py` | Figures 5 and 6 and Table 4 | the pilot report |
| `mktables.py`, `mkpriorart.py` | Tables 1–3 and the prior-art comparison | as above |
| `lit/search.py`, `lit/build_refs.py` | the 2025–2026 literature search and the verified reference records | network access to NCBI E-utilities |

## Commands, in order

```bash
python3 corpus_worker.py --out corpus_parts --cutoff 2016-02-09 \
    --exclude leakage_exclusion_list.csv
python3 screen_table.py --slkb-sqlite SLKB.db --out screen_table.csv
python3 -m pytest tests/ -q                      # equivalence tests for the restricted index
python3 run_pilot_real.py --slkb-sqlite SLKB.db --corpus-parts corpus_parts \
    --gene2pubmed gene2pubmed.gz --gene-info Homo_sapiens.gene_info.gz \
    --corpus-cutoff 2016-02-09 --out ../
python3 exchangeability_sim.py ../tables/Table_1_eligible_screens.csv .
python3 figures_design.py ../figures .
python3 fig1_design.py ../figures ../pilot_report_REAL.json screen_table.csv
python3 fig_pilot.py ../pilot_report_REAL.json ../figures ../tables
```

## Two things to know before running any of it

**Registered code is not in this folder.** The scientific estimators — the label loader, the
baselines, `evaluate_system`, `aggregate`, `paired_differences`, `summarise`, `cluster_bootstrap`
and the exact sign-flip machinery — live in the project's registered implementation tree and are
imported from it by `run_pilot_real.py`. That separation is deliberate and two automated tests
enforce it: no registered module imports staged code, and no staged module is executable as a
script.

**One substitution is staged, not registered.** `gene_index.py` replaces the registered in-memory
BM25 index, because the full snapshot does not fit in memory. It is proved equivalent to the
registered index for the registered query form by `tests/test_gene_index.py`, which asserts
agreement within 1e-12 for every anchor and candidate, including an absent gene, and equality of
`avgdl`. The substitution is recorded as change-control item CC-2026-10-31-03 and is **awaiting
approval**. If it is declined, the pilot's retrieval arm is withdrawn and the
popularity-versus-random contrast, which does not use it, still stands; that contrast is reported
separately for exactly this reason.

## Environment

Python 3.13 with numpy, pandas, scipy and matplotlib. Seeds are the registered ones: 20261025 for
candidate order and the random baseline, 20261028 for the staged power and dependence code, and
20261031 for the validity simulation.
