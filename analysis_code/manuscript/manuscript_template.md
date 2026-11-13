---
title: "Machine-learning benchmarks for synthetic lethality have a computable resolution limit: a pre-study criterion from the sharing structure of pooled CRISPR screens"
---

**Running title.** A resolution limit for synthetic-lethality benchmarks

**Authors.** Sambhaji Balaso Thakar^1,2,\*^, Pradnya Namdev Ghorpade^1,2^

^1^Advanced Bioinformatics, Data Science and Generative AI Unit, Aditya BioNova Analytics, Thakar
Mala Road, At/Post Haroli, Taluka Shirol, Kolhapur 416102, Maharashtra, India

^2^Oncology Clinical Trial Analytics & Research Unit, Aditya BioNova Analytics, Thakar Mala Road,
At/Post Haroli, Taluka Shirol, Kolhapur 416102, Maharashtra, India

\*Corresponding author: Sambhaji Balaso Thakar; e-mail: drsambhajithakar@adityabionova.com;
Tel.: +91 79727 89927

**E-mail addresses.** drsambhajithakar@adityabionova.com (S.B. Thakar);
gpradnya1@gmail.com (P.N. Ghorpade)

**ORCID.** Sambhaji Balaso Thakar 0000-0002-0423-2015; Pradnya Namdev Ghorpade 0000-0001-6593-825X

**Article type.** Original research

## Abstract

**Objective.** Computational discovery of synthetic-lethal (SL) gene pairs now reports
near-perfect benchmark performance, with graph-neural models exceeding 0.97 AUROC on public
combinatorial CRISPR screens — screens that share cell models and source studies, and so are not
independent. We asked how much inferential resolution such a resource contains, and whether it can
be established before a study runs.

**Methods.** We represent a resource as a bipartite incidence graph linking source studies to cell
models, and identify its mutually independent units with that graph's connected components, G in
number. For an exact sign-symmetry test on G units the attainable p-values are multiples of 2⁻ᴳ,
which places a floor on what the resource can resolve. We derive that floor, release it as an open
calculator, apply it to the deposited Synthetic Lethality Knowledge Base, and measure every
attainable rule's type I error by simulation over the real screen structure.

**Results.** {{ABS_RESULTS}}

**Conclusion.** {{ABS_CONCLUSION}}

**Keywords.** synthetic lethality; machine learning; CRISPR screens; benchmark design; cancer
genomics; cluster-level inference; permutation tests; type I error

## Statement of Significance

| | |
|---|---|
| **Problem** | Benchmarks for synthetic-lethal partner retrieval pool public CRISPR screens into tens of thousands of gene pairs treated as independent replicates. |
| **What is already known** | Split design, negative sampling and popularity bias change conclusions here, and scoring choices change which pairs a screen calls synthetic-lethal. |
| **What this paper adds** | A resource's **resolution limit**: the number of mutually independent contexts it holds, read from deposited metadata, fixes the smallest p-value an exact sign-symmetry test attains, so at α = 0.05 it needs six contexts to reject. We release the calculator and the public SL resource's profile — five contexts for the eligible design, three for the whole deposit, so enlarging it lowers resolution — and show that gating on a symmetry diagnostic raises the conditional error rate. |
| **Who benefits** | Anyone building or reviewing a small-sample benchmark that reports a permutation p-value over dependent biological units, and any group choosing cell models for a synthetic-lethality study, who can check the resolution available before committing. |

## 1. Introduction

{{INTRODUCTION}}

## 2. Related work

{{RELATED_WORK}}

## 3. Methods

{{METHODS}}

## 4. Results

### 4.1 The resource supports the intended labels, and carries three hazards

{{RESULTS_AUDIT}}

### 4.2 The resolution limit, and the resolution profile of SLKB

{{RESULTS_DESIGN}}

### 4.3 No attainable decision rule holds the nominal level

{{RESULTS_INFERENCE}}

### 4.4 Variance-component pilot on real data

{{RESULTS_PILOT}}

### 4.5 Status of the confirmatory evaluation

{{RESULTS_STATUS}}

## 5. Discussion

{{DISCUSSION}}

## 6. Conclusion

{{CONCLUSIONS}}

## Declarations

{{DECLARATIONS}}

## References

{{REFERENCES}}

## Figure legends

{{FIGURE_LEGENDS}}

## Table legends

{{TABLE_LEGENDS}}
