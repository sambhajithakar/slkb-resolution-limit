### 3.1 Data source and the label construct

Labels come from the Synthetic Lethality Knowledge Base (SLKB) [[cite:slkb]], through its officially
deposited SQL dump rather than any mirror. A pair is relevant in a cell model when **the source
study published it as a significant SL hit for that model**, as deposited in
`cdko_original_sl_results.SL_or_not`. No threshold is set by this protocol and none is derived from
any observed score distribution.

This was chosen over a recomputed interaction score because it is the call the source authors made
under their own quality control, it removes the need to declare a score direction and threshold, and
it avoids a hazard in the deposit reported in Section 4.1. The criterion is not uniform across screens
(Table 1), which is acceptable only because the estimand is a *within*-context paired difference.
Isogenic differential dependency is never described as synthetic lethality, and
homologous-recombination-deficiency scars never as functional repair status.

### 3.2 Units, eligibility and the number of independent contexts

A **query** is one (cell model, anchor gene) pair; the candidates are the partner genes screened
with that anchor in that model, and only those. Pairs are symmetrised. A query with no relevant
candidate has undefined average precision and is counted and excluded. A screen contributes queries
only if its library gives at least ten candidate partners per anchor on average, it carries at least
ten relevant pairs, and its published SL call rate lies inside the pre-specified prevalence
window. Applying these rules, **eleven screens from seven source studies
covering eight cell models** are eligible (Table 1)
[[cite:wong]][[cite:han]][[cite:shen]][[cite:najm]][[cite:zhao]][[cite:horlbeck]][[cite:thompson]][[cite:diehl]][[cite:parrish]][[cite:ito]][[cite:tang]].

The number of mutually independent units is neither eight nor seven. Two screens share no source of
dependence only if they share neither a source study nor a cell model, so the independent units are
the connected components of the bipartite incidence graph whose vertices are the studies and cell
models and whose edges are the screens, computed by union–find (Figure 1). This is a property of
the resource, fixed before any system exists, and it sets the sample size for every statement in
Section 4.2 and Section 4.3. The computation does not depend on this protocol's eligibility rules, so we apply it twice: to the
eleven eligible screens, and to all 32 of the deposit. The calculator is released with the code.

### 3.3 Retrieval corpus and leakage control

The corpus is a hashed, date-bounded snapshot of the PubMed annual baseline. A publication's
eligibility date is the `PubMedPubDate` carrying `PubStatus="entrez"`, chosen on measured
completeness: it is present in essentially every sampled record, while the `pubmed` status date is
absent in roughly one record in seven. A record without a usable Entrez date is rejected and
counted, never back-filled.

All eleven label-generating publications are excluded from every snapshot, audited by set
membership before any ranking is computed; the list also carries the resource paper and the derived
benchmark papers. Parametric memorisation of SL biology by a downstream language model cannot be
excluded, and is reported as a limitation rather than engineered around.

### 3.4 Systems, baselines and candidate ordering

Three baselines are mandatory. **Popularity-only** ranks candidates by gene popularity alone, on
two independent measures — NCBI `gene2pubmed` citation count and BioGRID interaction degree —
reported separately and never averaged. **Random at prevalence** is the no-information reference.
**Unconditioned retrieval** is Okapi BM25 over the frozen snapshot queried on the anchor gene alone.
The systems under test are built only after the protocol is frozen, so none is added after results
are seen, and a system that cannot beat popularity-only carries no information about genetic-state
conditioning whatever its absolute score. Candidate order is randomised per query with a
pre-specified seed, identically for every system; ties break on the gene symbol.

### 3.5 Primary outcome, estimand and the protocol's test

The primary outcome is per-query average precision with binary relevance over the full ranked
candidate list. The estimand for a system contrast is the **equal-weight mean over eligible contexts
of the within-context mean per-query average-precision difference**: a study's value is the
equal-weight mean of its screens' and a screen's that of its queries. Equal weighting at both levels
is deliberate, because one study contributes three of the eleven screens.

The protocol's test on each arm is an **exact sign-flip test by complete enumeration** of all 2^n^
sign vectors for n units, two-sided, statistic the absolute mean, ties counted as extreme. A
confirmatory claim requires **both** arms to reach p ≤ 0.05 and both means to share the sign of the
effect; otherwise no claim is made and the failing condition is named. Intervals invert the
enumerated test, widened to the enclosing breakpoints; where the attainable grid cannot support the
requested level, no interval is reported and the level is never silently reduced. The enumeration is
exact only when the joint null is sign-flip invariant, which requires independence across units and
symmetry of each unit value.

### 3.6 Feasibility and validity of the candidate decision rules

Two questions are answered before any data are used. **Feasibility** is the arithmetic of Section 4.2: a
rule is infeasible at level α whenever the floor its unit count implies exceeds α, at any data
configuration whatsoever. **Validity** is measured by simulation over the real screen structure. The simulation reads only
which study and cell model each eligible screen belongs to and how many informative queries it
carries; it reads no average precision and computes no quantity for H1 to H4. Unit values are a
study effect plus a cell-model effect plus a residual, crossing a dependence grid (each variance
share over 0, 0.2, 0.4) with ten error laws, run under no effect and at 1.40 between-cell-model
standard deviations so size and power are measured on the same replicates. Each scenario uses 40,000 replicates, seed 20261103.

Two features of this grid matter. The ten laws comprise five shapes and their **mirror images**, so
left and right skew are both represented. And for the proposed symmetry diagnostic we report the
rejection rate both unconditionally and **conditional on the diagnostic passing**, the latter being
the rate that describes published claims.

### 3.7 The variance-component pilot

The pilot estimates the between-cell-model standard deviation of the protocol's planning contrast,
the intraclass correlation by cell model and the two dependence parameters the power rule needs,
each with a cluster bootstrap and an identification flag. Where a parameter cannot be estimated
reliably the limitation is reported and **no value is invented**. The pilot tests no hypothesis.

### 3.8 Human adjudication for H3

The truth set for H3 may not be derived from either verifier's decision rule nor from any model
under test, which would make the deterministic checker correct by construction. Two independent
human adjudicators plus a named tie-breaker grade a pre-specified random sample under blinding,
Cohen's κ reported against a declared minimum of 0.60; protocol and forms are supplementary. **No
adjudicator has been identified or consented, no human label exists, and no model judgement is
substituted for one.**

### 3.9 Reproducibility

Every input carries a recorded checksum and retrieval date, and the analysis code, its tests and
the exact commands are released with the manuscript. Automated tests keep protocol-specified code separate
from staged code awaiting approval.
