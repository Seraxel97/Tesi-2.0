# ALTO-3 — Sensitivity classificazione sesso alla metrica di connettività

Stessa banda (**theta**) e atlante (**aparc**), stesso classificatore/CV/permutation. Cambia SOLO la metrica. PLV = winner (sensibile a volume-conduction); wPLI/imcoh = robuste (ignorano interazioni a lag-zero).

| Metrica | Volume-conduction | BA sesso | CI95 | p_perm |
|---|---|---|---|---|
| plv | sensibile | **0.795** | 0.744–0.843 | 0.0010 |
| wpli | robusta | **0.570** | 0.515–0.627 | 0.0240 |
| imcoh | robusta | **0.574** | 0.515–0.627 | 0.0240 |

PLV (winner) BA = 0.795 · robuste (media wPLI/imcoh) BA = 0.572.
Effetto sopra-il-caso conservato con metriche robuste: **24%** (PLV 0.295 → robuste 0.072).

## Verdetto
**SEGNALE PARZIALMENTE REALE MA PLV GONFIATO DA VOLUME-CONDUCTION: con wPLI/imcoh il sesso resta decodificabile sopra il caso (BA≈0.57, p<0.05) ma l'effetto sopra-il-caso crolla da 0.295 (PLV) a 0.072 (solo il 24% conservato) → il BA-headline PLV 0.795 è sostanzialmente inflazionato dalla conduzione spuria a lag-zero. Limitazione da dichiarare in evidenza.**

> Se wPLI e imcoh restano ben sopra 0.5 con CI95 che non tocca il caso e p significativo, la classificazione del sesso riflette connettività fisiologica reale, non un artefatto di volume conduction del PLV.
