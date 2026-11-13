"""Equivalence test: GenePairBM25 reproduces the REGISTERED UnconditionedRetrievalRanker exactly.

The registered ranker scores a candidate gene by the best-matching document that
mentions it, with the query built from the anchor gene alone. The gene-pair-restricted
index stores, for each needed (anchor, candidate) pair, the maximum anchor BM25
contribution over documents containing both. These must agree bit-for-bit for every
pair the registered query form can ask about, and both must return 0.0 for a candidate
that never co-occurs with the anchor.

Run with:  python3 -m pytest tests -q      (from analysis_code/)
"""
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, "/mnt/project-files/06_Implementation")

from brca_rag import baselines  # noqa: E402  (registered implementation)
from gene_index import GenePairBM25, UnconditionedAdapter  # noqa: E402

GENES = ["brca1", "brca2", "parp1", "atm", "tp53", "rad51", "kras"]
WORDS = ["cells", "tumour", "assay", "loss", "screen", "repair", "mouse"]


def _corpus(seed: int = 7, n_docs: int = 400):
    rng = random.Random(seed)
    docs = {}
    for i in range(n_docs):
        toks = [rng.choice(WORDS) for _ in range(rng.randint(5, 40))]
        for g in GENES:
            if rng.random() < 0.3:
                toks += [g] * rng.randint(1, 4)
        rng.shuffle(toks)
        docs[f"d{i}"] = toks
    return docs


def _build(docs):
    """Registered index + ranker, and the lean pair index over the same documents."""
    reg_index = baselines.BM25Index(docs)
    # keyed by the candidate symbol exactly as the harness passes it (upper case)
    gene_to_docs = {g.upper(): [d for d, t in docs.items() if g in t] for g in GENES}
    reg = baselines.UnconditionedRetrievalRanker(index=reg_index, gene_to_docs=gene_to_docs)

    df = Counter()
    for t in docs.values():
        df.update(set(t))
    n_docs = len(docs)
    total_len = sum(len(t) for t in docs.values())
    lean = GenePairBM25(n_docs, total_len, {g: df[g] for g in GENES})
    needed = {a: {c for c in GENES if c != a} for a in GENES}
    for toks in docs.values():
        tfs = Counter(x for x in toks if x in GENES)
        if tfs:
            lean.add_document(len(toks), dict(tfs), needed)
    return reg, lean


def test_lean_index_matches_registered_scores():
    docs = _corpus()
    reg, lean = _build(docs)
    candidates = [g.upper() for g in GENES] + ["ABSENT1"]
    checked = 0
    for anchor in GENES:
        want = reg.score("ANY_CELL_LINE", anchor, candidates)
        got = lean.score(anchor, candidates)
        for c, a, b in zip(candidates, want, got):
            if c.lower() == anchor:
                continue  # self-pair; never a candidate for its own anchor
            assert abs(a - b) < 1e-12, (anchor, c, a, b)
            checked += 1
    assert checked > 0


def test_absent_candidate_scores_zero_in_both():
    docs = _corpus()
    reg, lean = _build(docs)
    assert reg.score("ANY", "brca1", ["ABSENT1"])[0] == 0.0
    assert lean.score("brca1", ["ABSENT1"])[0] == 0.0


def test_adapter_drives_the_registered_harness_protocol():
    docs = _corpus()
    reg, lean = _build(docs)
    adapter = UnconditionedAdapter(lean)
    assert adapter.name == "unconditioned_retrieval" == reg.name
    cands = ["PARP1", "ATM"]
    assert adapter.score("ANY", "brca1", cands) == lean.score("brca1", cands)
