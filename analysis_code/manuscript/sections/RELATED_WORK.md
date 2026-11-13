Four lines of work bound this contribution, and each already did something we do not claim.

**Screen-level benchmarking of language models.** AssayBench frames each of 1,920 screens as a
gene-ranking problem, finds zero-shot generalist models beating biology-specific models, and
associates a gene's publication count with model performance, which it attributes to likely
pretraining exposure [[cite:assaybench]]. Prosz et al. show open-weight models reconstruct
genome-wide knockout screens better than chance [[cite:prosz]]. Those results are why the
popularity-only baseline is mandatory here and why a null for H1 is anticipated in the protocol. Neither
reports a cluster-level inferential statement, an attainable p-grid, or a detection floor fixed
before the systems were run.

**Split design and negative sampling.** Selection bias is known to change conclusions in SL
prediction [[cite:seale]][[cite:feng]][[cite:tepeli]][[cite:musl]] and in related
pair-prediction tasks [[cite:bernett]]; a 2026 roadmap states best practice explicitly
[[cite:noh]], and degree and popularity bias are well established in network biology
[[cite:zietz]][[cite:yilmaz]][[cite:bonner]]. None of that is claimed here as a discovery; the
addition is orthogonal, since those literatures correct *what is split and what is sampled* and
leave untouched *what counts as a replicate* when the result is tested.

**Model families and the numbers they now report.** A 2026 review records that graph neural
networks have become the standard architecture for computational SL prediction
[[cite:felloussi]], and current models report performance near the ceiling of the available
benchmarks: GiGCN, a signed-network framework, reports an area under the receiver operating
characteristic curve of 0.978 and an area under the precision–recall curve of 0.944
[[cite:gigcn]]. Reported performance is likewise high for retrieval-augmented and agentic systems
[[cite:slmerk]][[cite:jun]][[cite:zarfati]][[cite:medea]][[cite:neeley]][[cite:lai]]. The
contribution here is not a better such system, and no such system is built.

**The resource itself.** Interaction-scoring choices materially change which pairs a combinatorial
screen calls synthetic-lethal [[cite:ajmal]], which argues for tying labels to each source study's
own published call, as this protocol does.

**Two statistical results we rely on rather than claim.** That a permutation p-value cannot fall
below the reciprocal of the reference-set size is standard [[cite:nichols]]. That a preliminary
assumption check distorts the conditional error rate of the test that follows is also established:
Rochon et al. showed that a Shapiro–Wilk pretest raises the subsequent t-test's conditional type I
error to 0.11–0.17 on exponential data [[cite:rochon]], and Shamsudheen and Hennig treat such
combined procedures generally [[cite:shamsudheen]]. We claim neither phenomenon as new.

The gap sits across all four lines of work: no existing study turns these into a **pre-study
criterion** for a screen resource — how many mutually independent contexts it contains, what an
exact resampling test on that many units can attain, and what the rules that *can* reject cost when
the unit values are skewed. Those questions have arithmetic and measurable answers, and we give
them, together with the calculator that answers the first for any resource.
