"""A gene-pair-restricted BM25 index that reproduces the registered
`UnconditionedRetrievalRanker` scores exactly, without holding the whole corpus.

Why a restricted index is sufficient, and exactly equivalent
-----------------------------------------------------------
The registered ranker (`brca_rag/baselines.py`) builds its query from the anchor
gene alone and scores a candidate by the best BM25 score, for that single anchor
term, among the documents that mention the candidate:

    score(cand) = max_{d : cand in d} idf(anchor) * tf_d(anchor) * (k1+1)
                  / (tf_d(anchor) + k1 * (1 - b + b * |d| / avgdl))

A document that does not contain the anchor token contributes 0, so only
documents containing BOTH the anchor and the candidate can give a non-zero
score. Therefore it suffices to keep

  * n and the sum of document lengths  -> avgdl, identical to the full index,
  * the document frequency of every gene token -> idf, identical,
  * for each document holding at least two distinct SLKB gene tokens, its length
    and the term frequencies of those tokens.

Everything else is provably irrelevant: it scores 0 in the registered
implementation too. `tests/test_gene_index.py` asserts bit-level agreement with
the registered class on a synthetic corpus.
"""
from __future__ import annotations

import math
import pickle
from pathlib import Path


class GenePairBM25:
    def __init__(self, n_docs: int, total_len: int, df: dict, k1: float = 1.2, b: float = 0.75):
        self.k1, self.b, self.n = k1, b, n_docs
        self.avgdl = (total_len / n_docs) if n_docs else 0.0
        self.idf = {t: math.log(1.0 + (n_docs - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.best: dict[tuple[str, str], float] = {}
        self.n_docs_used = 0

    def add_document(self, dl: int, tfs: dict, needed: dict) -> None:
        """Update the best score for every needed (anchor, candidate) pair in this document."""
        toks = tfs.keys()
        if len(toks) < 2:
            return
        used = False
        for anchor in toks:
            cands = needed.get(anchor)
            if not cands:
                continue
            f = tfs[anchor]
            idf = self.idf.get(anchor, 0.0)
            s = idf * f * (self.k1 + 1.0) / (f + self.k1 * (1.0 - self.b + self.b * dl / (self.avgdl or 1.0)))
            if s <= 0.0:
                continue
            for c in toks:
                if c == anchor or c not in cands:
                    continue
                k = (anchor, c)
                if s > self.best.get(k, 0.0):
                    self.best[k] = s
                used = True
        if used:
            self.n_docs_used += 1

    def score(self, anchor: str, candidates) -> list[float]:
        a = anchor.lower()
        return [self.best.get((a, c.lower()), 0.0) for c in candidates]


class UnconditionedAdapter:
    """Ranker-protocol adapter so the REGISTERED evaluation harness can drive this index."""

    name = "unconditioned_retrieval"

    def __init__(self, index: GenePairBM25):
        self.index = index

    def score(self, cell_line, anchor, candidates):
        return self.index.score(anchor, candidates)


def aggregates(parts: list[Path]) -> tuple[int, int, dict]:
    from collections import Counter
    n = 0
    total = 0
    df: Counter = Counter()
    for p in parts:
        r = pickle.load(open(p, "rb"))
        n += r["n_eligible"]
        total += r["total_len"]
        df.update(r["df"])
    return n, total, dict(df)


def build(parts_dir: Path, needed: dict) -> tuple[GenePairBM25, dict]:
    parts = sorted(parts_dir.glob("*.pkl"))
    n, total, df = aggregates(parts)
    idx = GenePairBM25(n, total, df)
    meta = {"n_files": len(parts), "n_documents": n, "total_tokens": total,
            "n_gene_tokens_with_df": len(df), "files": []}
    n_multi = 0
    for p in parts:
        r = pickle.load(open(p, "rb"))
        for _pmid, _pub, dl, tfs in r["docs"]:
            if len(tfs) >= 2:
                n_multi += 1
                idx.add_document(dl, tfs, needed)
        m = {k: r[k] for k in ("file", "md5", "sha256", "n_eligible", "total_len", "stats", "rejects")}
        m["n_deleted_citations"] = len(r["deleted"])
        meta["files"].append(m)
    meta["n_documents_with_two_or_more_gene_tokens"] = n_multi
    meta["n_documents_contributing_a_pair_score"] = idx.n_docs_used
    meta["n_pairs_with_nonzero_score"] = len(idx.best)
    return idx, meta
