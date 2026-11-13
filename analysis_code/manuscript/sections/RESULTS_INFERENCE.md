We measured the type I error of both attainable rules, and of the conjunction as first
implemented, over the real screen structure (Table 3, Figure 3).

**An implementation error, reported because it changes the numbers.** An earlier version built the
study arm from seven studies rather than five components — a variant the protocol does not specify — reporting a
worst-case size of 0.078. Re-measured here it gives size **0.081** (95 % limit 0.083) and power
0.89, while the protocol's five-component rule has size zero. Both are reported, because the
seven-study variant is what an analyst who overlooked the shared cell lines would build.

**Dependence is not the binding problem.** With symmetric errors the cell-model arm rises from
0.045 at independence to 0.081 at the strongest dependence tested, while the seven-study conjunction
stays at or below 0.037 across the grid.

**Skew is.** At independence the seven-study conjunction's size is 0.018 under normal errors, 0.028
at skewness 1.0, 0.052 under an exponential and 0.081 under *χ*^2^~1~; the cell-model arm alone reaches
0.136 across the grid (95 % limit 0.139). The binding assumption behind a sign-flip test's exactness is therefore **symmetry, not
independence** — the assumption such benchmarks almost never check — and skew is structurally likely
here, a difference in average precision being bounded and zero-inflated.

**The error law must be allowed to skew in both directions.** The two-sided sign-flip statistic is
invariant under negation of all unit values, so two-sided procedures give identical results for a
law and its mirror — which holds exactly in our output and serves as an internal check. A one-sided
procedure has no such invariance, and this study's pilot values are left-skewed, so the grid covers
five shapes and their mirrors.

**The one-sided test on five components is attainable but not valid here.** Its rejection event is exactly "all five components fall in the hypothesised direction", so its
type I error is *q*^5^ with *q* the null probability that a component value is positive. Under sign
symmetry *q* = 0.5 and the rate is 2^−5^ = 0.031; it stays at or below 0.05 only while *q* is at most
the fifth root of 0.05, which is 0.549 — weaker and more interpretable than full symmetry. Under
every **right**-skewed law tested the rule is conservative, reaching only 0.011 to 0.032. Under **left** skew it fails:
0.083 under a mirrored exponential, 0.099 under a
mirrored lognormal and **0.112** under a mirrored *χ*^2^~1~ (95 % limit 0.115). The pilot's eight cell-model values have a
sample skewness of −1.20 (Section 4.4), inside the region where this rule inflates.

**A symmetry diagnostic does not repair any of this, and the way it appears to is an artefact of
conditioning.** The diagnostic proposed as a protocol amendment withholds confirmatory status unless
the absolute sample skewness of the unit values is at most 1.0. Measured unconditionally it looks
effective: the seven-study conjunction's worst size falls from 0.081 to 0.049 and the cell-model
arm's from 0.136 to 0.096. But a confirmatory claim is made **only** when the diagnostic passes, so
the rate that describes a published claim is the rate conditional on passing, and the unconditional
figure averages in the replicates where nothing is claimed. Conditional on the diagnostic passing,
the worst measured error rate **rises** to 0.106 for the seven-study conjunction (95 % limit 0.112),
to 0.174 for the cell-model arm and to 0.136 for the one-sided component rule (Figure 3b). The gate
selects, under skew, precisely the replicates in which the sample happens to look symmetric, and
those are not the replicates in which the test behaves well. Even unconditionally the 0.049 carries a Monte-Carlo standard error of 0.0011 and an upper 95 %
limit above 0.05.

**Conclusion of this section.** No decision rule available below the resolution limit holds the
nominal level: the two that respect the dependence structure cannot reject at all, and the two that
can reject carry worst-case measured error rates of 0.112 and 0.136, rising to 0.136 and 0.174 once
the gate's conditioning is accounted for. We therefore recommend no confirmatory test for H1 at this
design, including the amendment this project itself drafted, which is retained in the record with a
recommendation **against** adoption.
