**A resource's statistical resolution is fixed by its sharing structure, and is computable in
advance.** For a set of screens each identified by a source study and a cell model, two screens are
free of shared dependence only if they share neither, so the mutually independent units are the
connected components of the bipartite study-by-cell-model incidence graph; write *G* for their
number. An exact two-sided sign-flip test by complete enumeration on *G* units has a reference set
of 2^G^ sign vectors, so its attainable p-values are the even multiples of 2^−G^ and its smallest
attainable value is 2 × 2^−G^; the one-sided counterpart attains 2^−G^ [[cite:nichols]]. Requiring that
floor to lie at or below α yields a criterion that can be evaluated before any system is built, any
ranking is scored or any effect size is assumed: **at α = 0.05 an exact two-sided test can reject
only when *G* ≥ 6, and a one-sided test only when *G* ≥ 5** (Table 3, Figure 2a). Below those
thresholds the size and the power of the test are identically zero — not small, zero — irrespective
of effect size, of measurement quality, and of how many gene pairs the resource contains. We call the smallest *G* that clears the threshold the **resolution limit** at level α, and release
the union–find calculator that returns *G* and the attainable floor for any deposited resource.

**The eligible design sits one unit below that limit.** Eleven screens from seven source studies and
eight cell models satisfy the pre-specified eligibility rules (Table 1). They contribute 1,662 queries, of which 1,114 are informative; the remaining 548 have undefined
average precision and are counted and excluded rather than scored as zero. The set contains 18,526
directed positive pairs. Three cell lines are screened by two studies each — A549 and HELA by Shen 2017 and Zhao 2018,
K562 by Han 2017 and Horlbeck 2018 — so neither the eight cell models nor the seven studies are
mutually independent. The components number **G = 5** (Figure 1): Shen 2017 and Zhao 2018 with 293T,
A549 and HELA; Han 2017 and Horlbeck 2018 with K562 and JURKAT; and the singletons Diehl 2021 with
RPE1, Wong 2016 with OVCAR8, and Tang 2022 with 22RV1. The smallest attainable two-sided p is
therefore 0.0625.

**The full deposit resolves less, not more.** Applying the calculator to all 32 screens deposited in
SLKB — ten source studies across 22 cell models — returns **G = 3**, because 29 of the 32 screens
join into a single component spanning eight studies and 19 cell models, leaving only Horlbeck 2018
(JURKAT, K562) and Tang 2022 (22RV1) outside it. No individual deposited study exceeds *G* = 1.
Enlarging the set from the eleven eligible screens to all 32 therefore *reduces* the number of
independent units from five to three and raises the attainable two-sided floor from 0.0625 to 0.25.
This is not an artefact of our eligibility rules, but neither is it a law. Adding a screen whose
source study and cell model are both already represented adds an edge between existing vertices, and
an edge can merge two components but never split one, so *G* can only fall or stay level. Adding a
screen that brings in a study and a cell model touching nothing already present instead adds a new
vertex pair and a new component, raising *G* by one. Monotone decrease therefore holds **conditional
on the vertex set being fixed**, and *G* rises only through screens that are disjoint from everything
already deposited. In SLKB the first case is what occurs: 29 of the 32 screens attach to material
already present. Pooling across resources to raise the nominal sample size is therefore liable to
lower *G* in practice, and with it the resolution, but a genuinely independent new context raises
it.

**What this fixes for the protocol's rule.** The protocol's claim rule requires both arms to reach
p ≤ 0.05 simultaneously. Once the study arm is pooled to the five components that the dependence
structure requires, its smallest attainable p is 0.0625, so the conjunction cannot be satisfied **at
any data configuration whatsoever** — not by a larger effect, not by a cleaner measurement, not by
more queries. In simulation its rejection rate is identically zero under every error law and every
dependence cell tested, under the null and at an effect of 1.40 standard deviations alike (Table 3,
procedure B); its power is zero because its size is zero. The obvious repair fails to the same
arithmetic: pooling the *cell-model* arm to independent units gives the same five components, since
it is the same graph (Table 3, procedure D). Only two rules can reject at all — the cell-model arm
treated as eight independent values, and a one-sided test on the five components, whose smallest
attainable p is 2^−5^ = 0.0312. Section 4.3 measures what those two cost.

The detection floor follows the same arithmetic (Figure 2b): about 1.15 standard deviations at
eight clusters, 1.56 at the 80 % upper limit the protocol requires, and none at five. These floors
are published rather than discovered after a null result.
