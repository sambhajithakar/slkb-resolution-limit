# Reproducibility documentation

**BRCA_RAG_ · Project 1 · 3 November 2026 · internal, not for journal upload**

## 1. What was actually executed today, and what it returned

| Suite | Location | Result |
|---|---|---|
| Registered implementation | `/mnt/project-files/06_Implementation/tests` | **107 passed** |
| Staged CC-02 implementation | `/mnt/project-files/PROJECT1_FINAL_PRE_GATE3_PACKAGE/01_Staging_CC02/tests` | **78 passed** (3 warnings) |
| Packaged analysis code | `analysis_code/tests` | **3 passed** (after repair, see §2) |

**Total: 188 passing tests, 0 failing**, all run on 3 November 2026 in this environment.

## 2. A defect found and fixed in the packaged code

`analysis_code/tests/test_gene_index.py` as shipped in the 31 October package **did not run**. It
imported a class `GeneBM25` with a `best_score` method; the packaged `gene_index.py` defines
`GenePairBM25` with a pair-keyed `score` method. The test was written against an earlier
single-gene version of the index and was never updated when the index became pair-based, so
collection failed with an `ImportError`.

This matters because the manuscript states that the gene-pair-restricted retrieval index "is proved
equivalent to the registered index for the registered query form by automated test". **That claim
was not supported by the packaged test.** It is now. The test has been rewritten against the current
API and asserts three things, all passing:

1. For every (anchor, candidate) pair the registered query form can ask about, `GenePairBM25.score`
   agrees with `baselines.UnconditionedRetrievalRanker.score` to within 1e-12 on a 400-document
   synthetic corpus.
2. A candidate that never co-occurs with the anchor scores exactly 0.0 in both.
3. `UnconditionedAdapter` satisfies the registered harness's ranker protocol and reports the
   registered system name.

The staged/registered separation claim is unaffected: that is enforced by the two tests in the
CC-02 suite, which pass.

## 3. Reproducing each number in the manuscript

All commands are run from `analysis_code/`.

| Manuscript item | Script | Output consumed |
|---|---|---|
| Table 1 (eligible screens) | `screen_table.py` | `screen_table.csv` |
| Table 2 (resource audit) | `mktables.py` | `../../01_JOURNAL_SUBMISSION/tables/Table_2_resource_audit.csv` |
| §4.2 component derivation, §4.3 all sizes, Table 3, Supplementary Table S1, Data S2 | `gate3_feasibility_sim.py` | `../gate3_feasibility_results.csv`, `../gate3_feasibility_summary.json` |
| One-sided rejection-event check and *q* by law | `verify_onesided.py` | printed to stdout |
| §4.4 variance components, Table 4 | `run_pilot_real.py` | `../pilot_report_REAL.json` |
| 1.40 SD staged power recalculation | `power_recalc_staged.py` | `../power_recalculation_STAGED.json` |
| Figure 1 | `fig1_components.py` | `../../01_JOURNAL_SUBMISSION/figures/Figure_1_design_components.*` |
| Figure 2 | `fig2_attainable.py` | `Figure_2_attainable_and_floor.*` |
| Figure 3 and Table 3 | `gate3_figure_table.py` | `Figure_3_procedure_validity.*`, `Table_3_procedure_feasibility.csv` |
| Figure 4 | `fig_pilot.py` | `Figure_4_pilot_unit_values.*` |
| Manuscript assembly, reference numbering | `manuscript/fill.py <pilot_report.json> out.md` | `manuscript/out.md` |
| Reference re-verification | `lit/recheck.py` | `lit/recheck_2026-11-03.json` |

**Determinism.** Every stochastic script takes a fixed seed. The feasibility simulation uses
`SEED = 20261103`, `N_SIM = 40000`. Re-running it reproduces the reported sizes exactly; the
Monte-Carlo standard error quoted in the paper (0.0011 at a rate of 0.05) describes how far a
*different* seed would move them, not this one.

**Environment.** Python 3.13. `analysis_code/requirements.txt` pins exact versions
(`matplotlib==3.11.2`, `numpy==2.5.3`, `pandas==3.0.5`, `pytest==9.1.1`, `scipy==1.18.1`). `pandoc` and LibreOffice produce the DOCX and the PDF proof; the
reference DOCX is `manuscript/reference_academic.docx`.

## 4. Inputs and their provenance

| Input | Source | Verification |
|---|---|---|
| SLKB SQL dump | the resource's own FigShare record, article 22902839 v1 | publisher-stated MD5 verified on download; SHA-256 of the rebuilt SQLite recorded in the pilot report |
| SLKB CSVs | SLKB download endpoints | SHA-256 recorded, re-verified 28 Oct 2026 |
| NCBI `gene2pubmed`, `Homo_sapiens.gene_info` | NCBI FTP, public domain | SHA-256 recorded; NCBI rebuilds daily and publishes no checksum, so the **download date is part of the provenance** |
| PubMed 2026 annual baseline, 1,334 files | NCBI FTP | each file verified against NCBI's published MD5 on download; SHA-256 of each recorded; content hash of the snapshot in the corpus manifest |

**Not released, by design:** no redistribution of SLKB or PubMed. Nothing DepMap-derived enters
any analysis and no DepMap licence is relied upon.

## 5. Known limits on reproducibility

- **Pins, not a lockfile.** `requirements.txt` pins direct dependencies to exact versions but does
  not pin their transitive dependencies, and no hash-checking lockfile is shipped. Numerical
  results depend on `numpy`'s `default_rng`, which is stable across versions for the explicit
  seeding used.
- **NCBI inputs are not content-addressable upstream.** `gene2pubmed` is rebuilt daily; an exact
  re-run requires the archived copy, not a fresh download.
- **Two distribution hosts were unreachable** from this environment throughout: BioGRID (which is
  why only one popularity measure exists) and several package indexes. This is an environment
  limitation, recorded rather than worked around.
- **The CC-02 retrieval index is staged, not registered.** Every quantity depending on it carries
  that label in the released output and in the manuscript.
