#!/usr/bin/env python3
"""Gate 2B variance-component pilot — real data, registered estimators.

Authorisation: the researcher authorised this pilot on 25 October 2026 (non-BRCA
SLKB cell models only, legally accessible public data, the existing documented
protocol, the mandatory popularity-only and random baselines, the pre-specified
primary outcome, no fabricated values). It could not run then because every data
host was refused by the environment. The inputs are now present, so it runs here.

It tests no hypothesis, computes nothing for H1/H2/H3/H4, and opens no gate.
Everything scientific comes from REGISTERED code: `labels` (D3 = A published
calls, CC-01), `baselines.PopularityRanker`, `baselines.RandomRanker`,
`evaluation.evaluate_system` / `aggregate` / `paired_differences`, and
`stats.summarise` / `cluster_bootstrap`. The one substitution is the BM25 index
for the registered unconditioned retrieval baseline, which is replaced by the
provably equivalent `gene_index.GenePairBM25` because the full snapshot cannot be
held in memory; see that module and its two equivalence tests.

Usage:
  python3 run_pilot_real.py --slkb-sqlite SLKB.db --corpus-parts corpus_parts \
      --gene2pubmed gene2pubmed.gz --gene-info Homo_sapiens.gene_info.gz \
      --corpus-cutoff 2016-02-09 --out ../pilot_out
"""
from __future__ import annotations

import argparse, json, platform, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

REG = "/mnt/project-files/06_Implementation"
STAGED = "/mnt/project-files/PROJECT1_FINAL_PRE_GATE3_PACKAGE/01_Staging_CC02"
sys.path.insert(0, REG)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brca_rag import baselines, evaluation, labels, stats  # registered
import run_pilot as registered_driver                      # registered (for load_gene_popularity)
from gene_index import UnconditionedAdapter, build         # staged equivalence shim

ELIGIBLE = {("26864203", "OVCAR8"), ("28319085", "K562"), ("28319113", "293T"),
            ("28319113", "A549"), ("28319113", "HELA"), ("29452643", "A549"),
            ("29452643", "HELA"), ("30033366", "JURKAT"), ("30033366", "K562"),
            ("33956155", "RPE1"), ("36060092", "22RV1")}


def ucl80(sd_point: float, G: int) -> float:
    """80% one-sided upper confidence limit on an SD, chi-square, df = G-1 (registered rule)."""
    from scipy import stats as sps
    return float(sd_point * np.sqrt((G - 1) / sps.chi2.ppf(0.20, G - 1)))


def cluster_value_shape(diff: pd.DataFrame) -> dict:
    """Shape of the cell-model values: the quantity the proposed symmetry condition reads."""
    from scipy import stats as sps
    v = diff.groupby("cell_line")["diff"].mean()
    a = v.to_numpy(float)
    return {"cell_model_values": {str(k): float(x) for k, x in v.items()},
            "G": int(len(a)), "mean": float(a.mean()), "sd": float(a.std(ddof=1)),
            "skewness_sample": float(sps.skew(a, bias=False)) if len(a) > 2 else None,
            "median": float(np.median(a)),
            "note": ("reported as a design diagnostic for the proposed symmetry condition "
                     "(Amendment E, NOT IN FORCE); it is not a test of any hypothesis")}


def components(diff: pd.DataFrame, label: str, B: int) -> dict:
    y = diff["diff"].to_numpy(float)
    s = stats.summarise(y, diff["cell_line"].to_numpy())
    boot = stats.cluster_bootstrap(y, diff["cell_line"].to_numpy(), B=B)
    G = s["G"]
    sd = s["sd_between_means"]
    u = ucl80(sd, G)
    return {
        "subset": label,
        "n_queries": int(s["n_queries"]),
        "G_cell_models": int(G),
        "rho_icc_point": float(s["rho"]),
        "rho_icc_ci95": [float(np.percentile(boot[:, 0], 2.5)), float(np.percentile(boot[:, 0], 97.5))],
        "sd_between_cell_models_point": float(sd),
        "sd_between_cell_models_ci95": [float(np.percentile(boot[:, 1], 2.5)), float(np.percentile(boot[:, 1], 97.5))],
        "sd_between_cell_models_ucl80": u,
        "mean_difference": float(s["grand_mean"]),
        "n_effective": float(s["n_eff"]),
        "detectable_difference_at_point_sd": stats.detectable_difference(G, sd),
        "detectable_difference_at_ucl80": stats.detectable_difference(G, u),
        "bootstrap_resamples": int(B),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slkb-sqlite", required=True)
    ap.add_argument("--corpus-parts", required=True)
    ap.add_argument("--gene2pubmed", required=True)
    ap.add_argument("--gene-info", required=True)
    ap.add_argument("--corpus-cutoff", required=True)
    ap.add_argument("--order-seed", type=int, default=20261025)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    qs = labels.load_published_calls_from_sqlite(a.slkb_sqlite)
    f = qs.frame
    needed: dict[str, set] = {}
    for anchor, cand in zip(f["anchor_gene"].str.lower(), f["candidate_gene"].str.lower()):
        needed.setdefault(anchor, set()).add(cand)
    print(f"[{time.time()-t0:.0f}s] query set: {len(f)} directed rows, "
          f"{f.study.nunique()} studies, {f.cell_line.nunique()} cell models", flush=True)

    index, corpus_meta = build(Path(a.corpus_parts), needed)
    corpus_meta["cutoff"] = a.corpus_cutoff
    corpus_meta["eligibility_date_field"] = "PubMedPubDate PubStatus='entrez' (decision C6)"
    print(f"[{time.time()-t0:.0f}s] corpus: {corpus_meta['n_documents']} docs, "
          f"avgdl {index.avgdl:.2f}, non-zero pairs {len(index.best)}", flush=True)

    popularity, pop_meta = registered_driver.load_gene_popularity(a.gene2pubmed, a.gene_info)
    pop = baselines.PopularityRanker(popularity)
    genes = sorted(set(f["candidate_gene"]) | set(f["anchor_gene"]))
    pop_meta["coverage_of_slkb_genes"] = float(pop.coverage(genes))

    systems = {"unconditioned_retrieval": UnconditionedAdapter(index),
               "popularity_only": pop,
               "random": baselines.RandomRanker(seed=a.order_seed)}
    per_query, aggregates = {}, {}
    for name, ranker in systems.items():
        res = evaluation.evaluate_system(qs, ranker, order_seed=a.order_seed)
        res.to_csv(out / f"per_query_{name}.csv", index=False)
        per_query[name] = res
        aggregates[name] = evaluation.aggregate(res)
        print(f"[{time.time()-t0:.0f}s] {name}: {aggregates[name]}", flush=True)

    diff = evaluation.paired_differences(per_query["unconditioned_retrieval"], per_query["popularity_only"])
    diff.to_csv(out / "paired_differences_unconditioned_minus_popularity.csv", index=False)
    elig = diff[[(s, c) in ELIGIBLE for s, c in zip(diff.study, diff.cell_line)]]
    comp = {"all_screens_as_authorised": components(diff, "all deposited non-BRCA screens", min(a.bootstrap, 2000)),
            "eligible_screens_protocol_2_1": components(elig, "eligible screens (protocol §2.1)", a.bootstrap)}

    comp["cluster_value_shape_all"] = cluster_value_shape(diff)
    comp["cluster_value_shape_eligible"] = cluster_value_shape(elig)

    diff_pop_rand = evaluation.paired_differences(per_query["popularity_only"], per_query["random"])
    comp["sensitivity_popularity_minus_random"] = components(diff_pop_rand, "popularity - random, all screens", 2000)

    report = {
        "what_this_is": "the authorised Gate 2B variance-component pilot, run on real data",
        "what_this_is_not": ("not a hypothesis test, not a confirmatory analysis, not a Gate 3 run; "
                             "no H1/H2/H3/H4 quantity is computed here"),
        "authorisation": "researcher, 25 October 2026 (pilot only)",
        "run_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "registered_pair": "unconditioned_retrieval minus popularity_only",
        "label_construct": "published_call (D3 = A, CC-01)",
        "query_set": qs.summary(),
        "query_set_provenance": qs.provenance,
        "popularity": pop_meta,
        "corpus": corpus_meta,
        "aggregates": aggregates,
        "variance_components": comp,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "pandas": pd.__version__, "order_seed": a.order_seed},
        "runtime_seconds": round(time.time() - t0, 1),
    }
    json.dump(report, open(out / "pilot_report_REAL.json", "w"), indent=1, default=str)
    print(json.dumps(comp, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
