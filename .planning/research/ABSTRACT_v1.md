---
type: manuscript
status: draft
section: abstract
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-32
tags: [eeg, source-fc, ml]
version: v1
language: english
target_journal: Journal of Neural Engineering
word_count_target: 230-280
date: 2026-05-01
---
# Abstract — EEG Source-Space Functional Connectivity Classification: A Modular, Reproducible Pipeline

**Background.** Electroencephalography (EEG) source-level functional connectivity (FC)
offers a neuroanatomically interpretable approach to cognitive state classification,
yet the absence of reproducible, end-to-end pipelines that jointly standardize source
reconstruction, multi-atlas parcellation, and classifier benchmarking limits
methodological comparability across studies.

**Objective.** We present a modular pipeline extending MNE-BIDS-Pipeline for EEG
source-space FC classification, enabling systematic and reproducible benchmarking of
analysis choices across all major methodological axes.

**Methods.** Raw EEG data are preprocessed using MNE-BIDS-Pipeline v1.10.1 with
standardized artifact rejection and epoching. Source reconstruction employs dynamic
Statistical Parametric Mapping (dSPM) on the fsaverage template brain with ad-hoc
noise covariance estimation. Label time courses are extracted via four cortical atlases
— Desikan-Killiany (68 ROI), Destrieux (148 ROI), Schaefer-100, and Schaefer-200 —
using mean-flip aggregation to mitigate dipole sign ambiguity. Spectral FC matrices
are computed across seven phase-based metrics (wPLI, debiased wPLI², PLV, corrected
imaginary PLV, PLI, coherence, imaginary coherence) and five canonical frequency bands
(delta through gamma) using MNE-Connectivity v0.8. Classification employs five
scikit-learn algorithms (Logistic Regression, SVM, MLP, Random Forest, Gradient
Boosting) validated through Leave-One-Subject-Out cross-validation with 1000-permutation
testing and Benjamini-Hochberg FDR correction, yielding a systematic 700-run benchmark.

**Results.** Preliminary validation on the EEG matching pennies dataset (one subject,
smoke-test only) confirms end-to-end pipeline integrity across all 700 configurations
without critical failures. Classification accuracy on this single-subject baseline is
expected near chance and carries no statistical significance; publishable results are
pending application to a multi-subject resting-state dataset (candidate: ds005385 or
LEMON) once the final dataset selection is confirmed.

**Conclusion.** The proposed framework provides a transparent, version-controlled, and
test-covered infrastructure for systematic EEG source-space FC benchmarking, facilitating
reproducible comparison of parcellation strategies, connectivity metrics, and classifier
choices in future cognitive neuroimaging research.
