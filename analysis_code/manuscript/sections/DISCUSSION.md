### 5.1 What the accounting changes

A benchmark of eighteen thousand gene pairs looks like a large experiment. The accounting in
Section 4.2 says it is a small one. The usual way to evaluate a system that prioritises
synthetic-lethal partners is to pool public screens into a large set of gene pairs and treat the
pairs as replicates. Nothing is wrong with the resulting metric; what is wrong is the inference
attached to it, since pairs inside one screen share a library, a cell model, a scoring pipeline and
a publication decision. Once the biological context rather than the gene pair is the replicate, the
eligible resource holds five units, not eighteen thousand — and that number, not the pair count, is
what any exact resampling test has to work with.

### 5.2 Why a different statistic does not lift the floor

It is tempting to read a result like this as a call for a better statistic. It is not. The limit of
Section 4.2 is arithmetic: an exact two-sided sign-flip reference set on five units contains 32 vectors, so
0.0625 is the smallest two-sided p it can produce, whatever statistic, weighting or interval is
used. Procedures outside that class are not bound by the grid, but they buy nothing here: a
cluster-robust *t* on these units reaches a measured size of 0.138 under *χ*^2^~1~, and the
attainable one-sided exact rule inflates to 0.112 under exactly the left skew the pilot exhibits.
The floor is therefore a property of the exact, non-randomised tests the field actually reports,
and the alternatives to them are measured in Section 4.3 rather than assumed away.

The symmetry-gate result is the part we expect to generalise furthest, and it cautions against a
move that looks safe. Conditioning a confirmatory claim on a data-dependent diagnostic computed
from the same values changes the null distribution of the test given that a claim is made — the
classical pretesting problem [[cite:rochon]], routinely overlooked when the check is written into a
pre-registration as a safeguard. Measured unconditionally such a gate always looks protective,
because it converts some rejections into non-claims; measured conditionally — which is how a reader
encounters the literature — it can select precisely the samples in which the test misbehaves, here
roughly doubling the error rate it was introduced to control. Any pre-registration that gates
confirmatory status on an assumption check should report the conditional rate.

### 5.3 The criterion travels beyond this resource

Nothing in the derivation is specific to synthetic lethality, to CRISPR, or to retrieval. It needs
only that the evaluation units carry a known sharing structure and that the confirmatory test is
exact and sign-symmetric, which covers the permutation and sign-flip tests routinely reported on
small biomedical benchmarks. Where those conditions hold, *G* and the attainable floor follow from
metadata alone, before a system is built or a protocol frozen, so a design below the limit can be
redesigned at the planning stage rather than after a null result. The monotonicity observed in SLKB
suggests the check is most needed where benchmarks look largest.

The practical consequence for a group planning a synthetic-lethality study in a particular tumour
context is concrete: the resolution of the models available to them is computable before any screen
is chosen, so a claim that could never be supported can be restated as descriptive while that still
costs nothing. Four things are actionable. Report *G* alongside the number of gene pairs, since
shared cell lines are easy to miss and cost this design three of its eight apparent units; publish
the attainable p-grid for whatever resampling test is used; fix the label construct and the leakage
boundary before the systems exist; and, below the limit, report the contrast as an **estimation
result** — a cluster bootstrap interval over the components, labelled descriptive — not as a
test.

### 5.4 How this relates to recent work

**Evaluation-protocol audits have converged on what is split; the open question is what remains.**
Three 2026 audits reach the same verdict in different domains. In targeted protein
degradation, a hierarchical benchmark found that a conventional random split gave *R*^2^ = 0.693 while
the same models collapsed to *R*^2^ = −0.012 under leave-one-target-out evaluation [[cite:protac]]. In neuroimaging, a pipeline reporting 0.999 accuracy was traced to five
data-leakage pathways; with all five closed, a graph attention network reached an area under the
curve of 0.648 and did not outperform a support vector machine [[cite:leakbrain]]. In a food-chemistry benchmark, grouped evaluation reversed the ranking of
eighteen predictors, protocol rather than architecture dominating [[cite:leakfood]]. Each corrects *what is split and what is sampled*. None asks how many
mutually independent units survive the correction, or whether the test applied afterwards can
reject at all. The criterion given here is the question that follows theirs, answered from metadata
rather than from a re-run.

**Near-ceiling benchmark numbers and what they can support.** Nothing here disputes the
measurements reported by current SL predictors [[cite:gigcn]][[cite:felloussi]]. What this result
establishes is the resolution of the resources on which such comparisons are adjudicated: where a
resource holds three independent contexts, no exact cluster-valid test can separate two systems at
α = 0.05, however large the gap between their reported curves. The metric and the inference are
different claims, and only the second is bounded here.

**The clustered-data literature asks a complementary question.** Recent work develops score and Wald tests for whether an outcome
depends on the size of a cluster [[cite:kim_ics]], and extends the idea to sequential testing of
unit-size informativeness in three-level designs [[cite:anyaso]]. Those methods address how clusters should be weighted once an
analysis is possible. The result here is prior to that choice: the *number* of clusters bounds the
attainable p-value grid whatever the weighting, so below the resolution limit the estimand remains
estimable while no exact sign-symmetry test can reject. The two lines meet in the recommendation
adopted here — report the contrast with a cluster bootstrap interval, labelled descriptive.

### 5.5 What the criterion makes possible next

Three things follow directly, and none of them requires new mathematics.

**Resolution can be reported like any other property of a resource.** A deposit already states how
many screens, studies and cell models it contains. *G* is as cheap to compute as those counts and
says what they jointly support, so it can sit beside them in a resource paper, in a benchmark card
and in the methods section of any study that reports a resampling *p*-value over pooled screens. A
reader then sees at once whether the reported test could have rejected.

**Deposits can be designed to add resolution rather than mass.** Because a screen whose study and
cell model are both already represented can only merge components, the growth of a resource and the
growth of its resolution are different things. A consortium choosing its next models can compute,
before committing, whether a planned screen raises *G* or simply enlarges an existing component.
That turns a question usually settled by budget into one settled by arithmetic.

**The attainable-floor calculation generalises to other resampling schemes.** The grid derived here
belongs to the sign-symmetry group; the same reasoning applies wherever the reference set is
generated by a finite group acting on a known number of exchangeable units, which covers
permutation tests on grouped designs well beyond functional genomics. Working out the attainable
grids for those schemes, and measuring what their feasible rules cost under realistic dependence,
is the natural continuation of this work. The calculator released here is structured so that a new
resource, or a new incidence rule, can be dropped in without touching the inference code.

### 5.6 Limitations

**The design is small, and no analysis repairs that.** Five independent contexts are the whole of
the public resource meeting the eligibility rules.

**Components separate the dependence that metadata can see, which is not the same as independence.**
A component is defined by shared source studies and shared cell models, the two dependencies a
deposited record makes visible. Screens in different components may still share a laboratory, a
library design, an assay protocol, a scoring pipeline, overlapping gene pairs or a common
publication filter, and none of that is observable from the deposit. Treating components as mutually
independent is therefore an assumption rather than a proof, and the exactness of the sign-flip
reference distribution is conditional on it, together with sign symmetry of the component values
under the null. What the construction does establish is an upper bound on resolution: residual
dependence between components can only reduce the effective number of independent units, so the
attainable floor reported here is the most optimistic one available, not a conservative one.

**The impossibility is bounded to a class of tests.** The floor at 2^−G^ applies to exact,
non-randomised tests whose reference distribution is the sign-symmetry group on the *G* component
values. A randomised test attains any level by construction, and an asymptotic or model-based
procedure is not bound by the grid; neither is thereby valid at this sample size, and Section 4.3
measures what the attainable alternatives actually cost. Nothing here is a general impossibility
theorem about all statistical procedures.

**No BRCA-deficient breast model exists in this resource.** No public combinatorial CRISPR
synthetic-lethality screen contains a BRCA1/2-deficient breast cancer model; the nearest 2025 screen
is in MDA-MB-231, triple-negative but BRCA1/2 wild-type and selected for chemoresistance rather than
homologous-recombination status [[cite:shao]]. Nothing here supports a claim about BRCA1/2-deficient
breast cancer.

**The label is not uniform across contexts.** Each source study applied its own significance
criterion and the published call rates span 0.19 % to 63.21 %, so the estimand is a within-context
paired difference and any pooled quantity would be uninterpretable [[cite:ajmal]].

**Leakage control is partial by construction.** The corpus boundary and the exclusion of the eleven
label-generating publications are verified by set membership, but parametric memorisation by a
downstream language model cannot be excluded [[cite:li_mem]]. SLKB also names a *STAR Protocols*
article for the 22Rv1 screen with no companion primary report [[cite:tang]], so excluding the named
publication may not exclude every text describing that screen.

**The validity measurement is a model.** The simulation draws unit values from a single parametric
family, so the measured sizes are evidence, not guarantees: a maximum over a finite grid is not a
bound over the family of distributions the data could follow.

**One popularity measure, one staged component, no similarity screening.** The BioGRID host could
not be reached, so the pilot rests on the NCBI citation-count measure alone rather than the two the
protocol specifies; the gene-pair-restricted retrieval index is proved equivalent to the protocol's
index by automated test but remains a change-control item awaiting approval, every quantity
depending on it being labelled accordingly; and no licensed similarity service was available, so no
similarity score is reported. **Nothing here is a clinical result**: the
work concerns the evaluation of computational systems and supports no treatment decision.
