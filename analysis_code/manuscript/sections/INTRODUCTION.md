Synthetic lethality underlies one of the few genuinely selective strategies in cancer therapy, and
its computational discovery is a crowded field. Reviews place context dependence at its centre
[[cite:chang]]: the same gene pair can be lethal in one lineage and inert in another, with
KRAS-driven dependencies sharing almost no hits across permissive lineages [[cite:martin]] and
genome-scale maps identifying determinants of cell-line-specific dependency
[[cite:billmann_cell]].

Two newer developments make the evaluation question urgent. Retrieval-augmented and agentic systems
are now applied to SL reasoning and to oncology recommendation, and are reported to work well
[[cite:slmerk]][[cite:jun]][[cite:zarfati]][[cite:medea]]. At the same time, general-purpose
language models rank genes from public CRISPR screens better than chance with no retrieval at all,
and their performance tracks how often a gene has been written about
[[cite:neeley]][[cite:stoeger]], while their citation of supporting references needs separate
assessment [[cite:wu_source]][[cite:lai]]. If apparent skill can be produced by
gene popularity, and if the screens a system is evaluated on are published and therefore plausibly
inside its pretraining corpus [[cite:li_mem]], a benchmark that controls for neither cannot
distinguish evidence retrieval from recall.

Almost every benchmark in this area answers that concern with design choices — splitting, negative
sampling, popularity controls — and then computes a p-value over gene pairs. That last step is the
one we examine. Gene pairs within a screen share a library, a cell model, a scoring pipeline and a
publication decision; the biological contexts, not the pairs, are the replicates. Making that
substitution turns a question about a particular benchmark into a question with an arithmetic
answer: **how much can a given resource resolve at all?**

We set out to build a leakage-controlled benchmark for genetic-context-conditioned retrieval of SL
partners, with the analysis plan fixed in an internal written protocol before any system under test
was built. That protocol accompanies this submission. It has **not** been filed with a public
registry and is not frozen, so the study is pre-specified but not pre-registered, and nothing here
is described as prospectively registered. Four hypotheses were specified in advance in that
protocol, none of which is tested in this paper: that conditioning retrieval on declared
genetic state improves average precision over unconditioned retrieval and over popularity-only
ranking (H1, primary inferential, a null permitted and expected); that cluster-level,
leakage-controlled evaluation changes a fixed reference system's measured performance (H2); that an
agentic critic does not beat a deterministic evidence checker at matched cost (H3, requiring human
adjudication); and that performance differs across the pretraining boundary (H4).

Before any system was built, we carried out the work this paper reports: an audit of the resource,
a derivation of its resolution limit, a measurement of the type I error of every rule that can
reject at that resolution, and a variance-component pilot on real data. The limit is a property of
the resource rather than of this project, it is computable from deposited metadata, and it decides
in advance which confirmatory claims a benchmark built on that resource could ever support. We
report it before running the comparison, because a detection floor published in advance has a
defined meaning that one discovered after a null result does not.
