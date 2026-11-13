# Statistical verification report

**BRCA_RAG_ · Project 1 · 3 November 2026 · internal, not for journal upload**

This report records what was checked, how, and what is still only evidence rather than proof. It
supersedes `Statistical_Validity_and_Exchangeability_Report.md` from the 31 October package, whose
headline figures were measured on an unregistered variant of the rule (see §4).

## 1. What was re-opened and why

The 31 October package reported that the registered conjunctive rule held a worst-case simulated
type I error of 0.0496 once a symmetry diagnostic was applied, and recommended that diagnostic as a
protocol amendment. Two defects were found in that analysis.

**Defect 1 — the study arm was built from seven studies, not five components.** Three cell lines
are screened by two studies each, so studies are not mutually independent. The simulation
implemented a rule nobody had registered. The registered rule, once its study arm is pooled to the
independent units, behaves completely differently: it cannot reject at all.

**Defect 2 — the 0.0496 was an unconditional rate.** The symmetry diagnostic withholds confirmatory
status when it fails, so a published claim exists only in the subset where it passes. The rate that
describes a published claim is therefore the rate conditional on the diagnostic passing. The
unconditional figure averages in replicates where nothing is claimed, which makes a gate look
protective by construction. This is the classical pretesting problem (Rochon, Gondan & Kieser 2012,
*BMC Med Res Methodol* 12:81, PMID 22712852), not a new phenomenon, and it was overlooked.

## 2. Independent units: derivation and check

Two screens are dependent if they share a source study **or** a cell model. The mutually independent
units are therefore the connected components of the bipartite incidence graph (7 study vertices,
8 cell-model vertices, 11 screen edges), computed by union–find in
`analysis_code/gate3_feasibility_sim.py`.

**Result: five components.**

| Component | Studies (PMID) | Cell models |
|---|---|---|
| 1 | 28319113 (Shen 2017), 29452643 (Zhao 2018) | 293T, A549, HELA |
| 2 | 28319085 (Han 2017), 30033366 (Horlbeck 2018) | K562, JURKAT |
| 3 | 33956155 (Diehl 2021) | RPE1 |
| 4 | 26864203 (Wong 2016) | OVCAR8 |
| 5 | 36060092 (Tang 2022) | 22RV1 |

Checked by hand against Table 1: the three doubly-screened cell lines (A549, HELA, K562) are exactly
the edges that merge components, and 8 + 7 vertices − 11 edges + (cycles) resolves to 5.

## 3. Feasibility: arithmetic, not simulation

An exact two-sided sign-flip test by complete enumeration on *n* units has 2ⁿ sign vectors; its
attainable two-sided p-values are the even multiples of 2⁻ⁿ and its smallest attainable value is
2/2ⁿ (Nichols & Holmes 2002, PMID 11747097).

| Units | Sign vectors | Smallest two-sided p | Reaches 0.05? | Smallest one-sided p | Reaches 0.05? |
|---|---|---|---|---|---|
| 5 | 32 | **0.0625** | **No** | 0.0312 | Yes |
| 7 | 128 | 0.0156 | Yes | 0.0078 | Yes |
| 8 | 256 | 0.0078 | Yes | 0.0039 | Yes |

**Consequence.** The registered rule requires both arms at p ≤ 0.05. With the study arm pooled to
five components, that is unattainable at any data configuration: not by a larger effect, not by more
queries, not by a cleaner measurement. Size and power are both exactly zero, and the simulation
reproduces that (procedure B: 0.0000, upper 95 % limit 0.0001, at every grid point, null and
alternative alike). This is a verification of the arithmetic, not evidence for it.

## 4. Validity: measured type I error

40,000 replicates per scenario, seed 20261103, over the real screen structure; ten error laws
(normal, *t*₃, gamma shape 4, exponential, χ²₁ and the mirror image of each) crossed with a
dependence grid (study and cell-model variance shares each over 0, 0.2, 0.4). Nominal α = 0.05.
Monte-Carlo standard error at a rate of 0.05 is 0.0011.

| Procedure | Unit count | Can reject? | Worst size (95 % upper) | Gated, unconditional | **Gated, conditional on passing** | Power at 1.40 SD, normal errors, independence |
|---|---|---|---|---|---|---|
| A — conjunction, study arm as 7 studies *(unregistered variant)* | 8 × 7 | yes | 0.081 (0.083) | 0.049 | **0.106 (0.112)** | 0.886 |
| B — conjunction, study arm as 5 components *(the registered rule)* | 8 × 5 | **no** | 0.000 (0.000) | 0.000 | 0.000 | **0.000** |
| C — cell-model arm alone | 8 | yes | 0.136 (0.139) | 0.096 | **0.174 (0.180)** | 0.939 |
| D — component arm, two-sided | 5 | **no** | 0.000 (0.000) | 0.000 | 0.000 | **0.000** |
| E — component arm, one-sided | 5 | yes | 0.112 (0.115) | 0.063 | **0.136 (0.142)** | 0.768 |

The power column is the normal-errors, independence cell, which is the figure Table 3 of the
manuscript reports. `gate3_feasibility_summary.json` additionally records
`power_at_delta_independence` as the **mean over the ten error laws** at independence (0.898 for A,
0.932 for C, 0.849 for E); the two are different quantities and the manuscript uses the first.

**The 0.0496 of the 31 October package reproduces as 0.0486 for procedure A unconditionally.** It
is not a demonstration of control: its 95 % upper limit is above 0.05, and the conditional rate —
the one that describes a published claim — is 0.106.

**Procedure A is not the registered rule and is reported only because it is what an analyst who
overlooked the shared cell lines would build.**

## 5. Internal correctness checks that were run

1. **Mirror invariance.** The two-sided sign-flip statistic is invariant under negation of all unit
   values, so procedures A–D must give bit-identical results for a law and its mirror. They do, at
   every grid point. A mismatch would have indicated a tail-handling bug.
2. **One-sided rejection event.** `verify_onesided.py` confirms on 200,000 draws that
   {one-sided p ≤ 0.05} is exactly the event "all five components positive", and that the rate under
   sign symmetry is 1/32 = 0.0312 (measured 0.03112). The type I error is therefore *q*⁵ where *q*
   is the null probability of a positive component value; the rule holds the level only while *q* is
   at most the fifth root of 0.05, which is 0.5493. Measured *q* by law confirms where it fails.
3. **Observed-vector indexing.** An earlier implementation took the all-minus-one sign vector as the
   observed statistic for the one-sided test, giving power 0.0 and a wrong-tail size. Fixed and
   re-run; the fix is what the check in (2) exists to catch.
4. **Both skew directions.** The earlier error-law grid contained only symmetric and right-skewed
   laws. The pilot's own unit values have sample skewness −1.20. Mirrored laws were added, and they
   are what exposed procedure E's failure under left skew (0.052 to 0.112).

## 6. What this is not

- It is **not** a proof of type I error control for any procedure. A maximum over a finite grid of
  laws and dependence cells is not a bound over the family of distributions the data could follow.
  The negative conclusions (procedures B and D cannot reject) *are* arithmetic and do not depend on
  the simulation.
- It is **not** a hypothesis test. No average precision is read by the simulation; it reads only the
  study/cell-model membership of each screen and its informative query count.
- The 1.40 SD effect used for power is the staged recalculation from the authorised pilot, produced
  by code that is **staged, not registered**. It is a planning quantity with no operative test
  behind it.

## 7. Recommendation carried into the record

**No confirmatory test for H1 is defensible at this design**, including the symmetry-gated rule this
project itself drafted. The draft amendment is retained with a recommendation **against** adoption
(`../03_RESEARCHER_APPROVAL/Protocol_Amendment_Exchangeability_RECOMMENDED_AGAINST.md`). If the
researcher wishes to proceed, the defensible form is an **estimation report**: the contrast with a
cluster bootstrap interval over the five components, reported as descriptive, with no p-value for
H1. That is a decision for the researcher and has not been taken here.
