The deposited dump of `cdko_original_sl_results` holds 280,483 screened gene pairs across the
eleven source studies. `SL_or_not` takes exactly two values, with no nulls, no missing gene symbol
and no self-pairs, so the intended label construct is available directly without recomputing any
interaction score (Table 2). Three properties of the deposit constrain how it may be used, found by
this audit rather than from the resource description.

First, **4,101 `gene_pair_id` values are shared by two or more source studies**, so a join on
`gene_pair_id` alone — the key the deposited schema invites — can attach one study's score to
another study's pair. Every query here is keyed on `(study, cell model, anchor, candidate)`, and a
repeat carrying two labels inside one screen stops the run rather than resolving by row order.

Second, **score coverage is partial and study-dependent**. A total of 261,958 distinct
`gene_pair_id` values carry a GEMINI score, and Han 2017 has none of its own: all 20,791 of its rows are unscored. Any
protocol defining relevance by a recomputed score silently drops that study; using each study's own
published call keeps it.

Third, **the published SL call rate spans two and a half orders of magnitude**, from 0.19 % in Han's
K562 screen to 63.21 % in Diehl's RPE1 screen (Table 1). The label is not uniform across contexts,
which is why the estimand is an equal-weight mean of *within*-context paired differences: it
requires only that the label be fixed inside a context.

Two further findings are recorded. The 786-O cell model of Najm 2018 is a **true published zero**
rather than a missing record, so it is excluded on the published result and not on a data error;
SLKB's study table misprints it as "876O", which would defeat a name-based join. And leakage control
was verified as a set operation rather than asserted, the check running before any ranking and
failing the run rather than warning.
