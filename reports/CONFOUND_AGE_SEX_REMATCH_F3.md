# F3-bis — Neutralizzazione confound età↔sesso (age-matching)

Feature winner: **X_aparc_plv_theta**  ·  N matched: **134** (67 coppie M↔F)

## Confound d'età
- PRIMA (N=179): Mann-Whitney p = **0.0061** (M mediana 50.0 vs F 42.5) → differisce
- DOPO (age-matched): p = **0.8744** → confound RIMOSSO (diff-età media entro-coppia 0.58 anni)

## Classificazione sesso sul subset age-matched
- Balanced accuracy = **0.719**  (CI95 0.657–0.784)
- p permutation = **0.0010**  ·  null-BA media 0.502

## Verdetto
**SEGNALE DEL SESSO ROBUSTO: sopravvive alla rimozione del confound d'età.**

> Confronto: BA in CV piena N=179 = 0.795. Se BA_matched resta ben sopra 0.5 con CI95 che non tocca il caso e p significativo, la classificazione del sesso NON è un artefatto dell'età.
