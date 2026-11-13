# Reference verification report

**BRCA_RAG_ · Project 1 · re-verified 3 November 2026 · internal, not for journal upload**

## Summary

| | |
|---|---|
| References in the manuscript | **39** |
| Resolved against a primary service | **38 of 39** |
| Not re-verifiable from this environment today | **1** (arXiv preprint, ref 13) |
| In-text citation markers [1]–[39] all present and in first-appearance order | **yes** |
| Reference numbers with no in-text marker | **none** |

## How it was checked

**PubMed records (37 of 39).** Every PMID in the reference list was re-fetched live from NCBI
E-utilities on 3 November 2026 by `analysis_code/lit/recheck.py`; the raw response is saved as
`analysis_code/lit/recheck_2026-11-03.json`. All 37 PMIDs resolved. Titles were compared with the
stored records from 31 October by normalised sequence similarity.

- **37 of 37 titles match.**
- One apparent mismatch (PMID 42685085, Martin *et al.*) was traced to the checking script, not the
  reference: PubMed marks up the gene name inside `<ArticleTitle>`, and `findtext` returns only the
  text before the first child element, truncating the title. Re-read with `itertext()` it matches
  exactly. The script in the package is the uncorrected one and this note documents the artefact.

**bioRxiv preprint (ref 14, Prosz *et al.*).** Re-fetched live on 3 November 2026 through the
bioRxiv API. **This found an error in the 31 October reference and it has been corrected.** The
31 October entry recorded version 2 dated 11 May 2026 with seven authors including "Kilim O". The
authoritative record is **version 1, posted 30 January 2026**, with six authors in the order
Prosz AG, Sztupinszki Z, Diossy M, Zimon B, Csabai IG, Szallasi Z. The manuscript now carries the
corrected entry. The bioRxiv *web* host is not reachable from this environment, so a v2, if one
exists, could not be inspected; the API returns v1 as current.

**arXiv preprint (ref 13, AssayBench).** `arxiv.org` is outside this session's allowed network
domains and does not resolve, so this entry **could not be re-verified today**. It stands as
verified on 31 October 2026 and is labelled a preprint, not peer reviewed, in the reference list.
The author must confirm it before submission. (To re-verify it here, arxiv.org would have to be
allowed in the session's network settings.)

## Claim-level checks

- **No reference is cited for a claim it does not support.** The two statistical results the paper
  leans on are attributed, not claimed: the permutation p-value floor to Nichols & Holmes 2002
  (ref 25) and the pretesting distortion to Rochon, Gondan & Kieser 2012 (ref 26). Both DOIs were
  re-derived from `PubmedData/ArticleIdList` rather than from the article's own reference list,
  after an earlier extraction attached a reference-list DOI to Rochon.
- **Ref 39 (Shao 2025)** is cited only to support the statement that the nearest 2025 screen is in
  MDA-MB-231, which is BRCA1/2 wild-type. It is not cited as supporting any BRCA-deficient claim,
  and no such claim is made.
- **Ref 38 (Tang 2022)** is a *STAR Protocols* methods article with no companion primary report in
  PubMed. This is stated in the manuscript's limitations, because it bounds what the leakage
  exclusion can achieve.

## Status

**Reference verification: PASS with one item outstanding** — ref 13 (arXiv) not re-verifiable from
this environment. One error was found and corrected during this pass (ref 14).
