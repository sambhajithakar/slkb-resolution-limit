**Figure 1. The eligible design has five independent units.** The bipartite incidence graph of the
eleven eligible screens: seven source studies on the left, eight cell models on the right, one edge
per screen, and the informative query count beside each cell model. Shaded bands are the connected
components of this graph, which we take as the independent units of the design. Three cell lines
are screened by two studies each — A549 and HELA by Shen 2017 and Zhao 2018, K562 by Han 2017 and
Horlbeck 2018 — which collapses eight cell models and seven studies into five components. The two
coloured components contain all six of the non-independent screens.

**Figure 2. What the design can produce, before any system is run.** (a) The exact sign-flip
reference set is finite: at *n* units the attainable two-sided p-values are the even multiples of
2^−n^. At eight units the smallest is 0.0078 and nothing lies between 0.0156 and 0.0234; at five
units the smallest is 0.0625, which lies above the conventional threshold, so a two-sided
confirmatory claim is unattainable at any data configuration. The one-sided grid at five units
starts at 0.0312 and is attainable. (b) The smallest detectable difference as a function of the
number of independent clusters, at the point estimate of the between-cluster standard deviation and
at its 80 % one-sided upper confidence limit, which is the value the protocol requires for planning.

**Figure 3. Type I error of every decision rule available at this design.** (a) Worst measured
two-sided size over the whole dependence grid, by error law of the unit values; the ten laws are
five shapes and their mirror images, so the horizontal axis spans skewness from −3.7 to +3.7.
Procedure A is the conjunction with the study arm treated as seven independent studies; B is the
same conjunction with the study arm pooled to its five components, and is identically zero because
it cannot reject; C is the cell-model arm alone at eight values; E is the one-sided test on the five
components. The two-sided procedures are invariant under mirroring and give identical values for a
law and its mirror, which is an internal check; E is not, and fails under left skew. (b) For the
three rules that can reject: the worst size ungated, the worst size with the symmetry diagnostic
applied and counted unconditionally, and the worst size conditional on the diagnostic passing. The
conditional rate is the one that describes a published claim. Each scenario uses 40,000 replicates, seed
20261103; the Monte-Carlo standard error at a rate of 0.05 is 0.0011.

**Figure 4. Unit values measured in the authorised pilot.** The mean paired difference in per-query
average precision (unconditioned retrieval minus popularity-only) for each cell model, (a) over the
eligible screens and (b) over all deposited non-BRCA screens. The vertical line is the equal-weight
mean across cell models; the dotted line is zero. Panel annotations give the number of cell models,
the mean, the between-cell-model standard deviation and the sample skewness. The skewness is
reported as a design diagnostic for the symmetry condition examined in Section 4.3; it is not a test of any
hypothesis.
