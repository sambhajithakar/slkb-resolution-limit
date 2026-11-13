The pilot was authorised in advance and tests no hypothesis; its contrast is the protocol's planning
pair, unconditioned retrieval minus popularity-only. It ran on the full deposited label set, the
real NCBI popularity measure and the real date-bounded corpus — <<nfiles>> PubMed baseline files,
each verified against NCBI's MD5, yielding <<ndocs>> documents eligible at the <<cutoff>> boundary.
Full output is given in Supplementary Results.

**Absolute performance is high for every system, including the no-information baseline.** Over all
deposited non-BRCA screens the cluster-weighted mean average precision is 0.600 for unconditioned
BM25 retrieval, 0.581 for popularity-only and 0.554 for random ranking at prevalence — the last far
above zero because several screens pair short candidate lists with high published SL call rates, so
an absolute score here is close to uninterpretable without its random reference. The retrieval
advantage over popularity is small and, on the eligible screens, negative: the mean paired
difference is <<mean>> average-precision points across <<gword>> cell models and <<nq>> informative
queries, reported with its sign and testing nothing.

**Between-context variability is the quantity that matters, and it is estimated imprecisely.** The
between-cell-model standard deviation of the mean paired difference is <<sd>> (95 % cluster
bootstrap <<sdlo>> to <<sdhi>>; 80 % one-sided upper limit <<ucl>>), and the intraclass correlation
by cell model is <<icc>> (interval <<icclo>> to <<iccci>>, including zero). The effect of that
clustering is the headline of this section: <<nq>> queries carry an effective sample size of
<<neff>>, a reduction of about twenty-sevenfold. Under the recalculation rule fixed before the pilot
ran, the design would reach 80 % power at a true effect of **1.40 standard deviations** — a planning
quantity without an operative test behind it, since Section 4.2 shows the conjunctive rule cannot reject.
It was produced by **staged code that the protocol does not cover**, labelled as such in the released output.

**The measured skew is left-handed, which is the direction that breaks the one-sided rule.** The
sample skewness of the eight eligible cell-model values is <<skew>>, and over all 21 deposited cell
models it is +4.24 (Figure 4). Two consequences follow for Section 4.3: the symmetry diagnostic drafted as
a protocol amendment uses a threshold of 1.0 in absolute value, so on the first real values it meets
it would withhold the confirmatory label; and the sign of that skew places the design inside the
region where the one-sided five-component rule inflates rather than the region where it is
conservative. Nothing is decided by these values, but they are the only empirical information available about the
shape of the unit-value distribution, and they point the wrong way for both rules.
