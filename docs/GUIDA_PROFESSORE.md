# Guida rapida per il relatore

Questa pagina spiega, con il minimo indispensabile, come avviare la pipeline e dove
trovare i risultati. Per i dettagli tecnici (bug noti, parametri, struttura cartelle
completa) vedi il [README.md](../README.md) principale.

## 1. Cosa fa il progetto, in una frase

Prende un tracciato EEG (formato BIDS), lo pulisce, ricostruisce l'attività alla
sorgente nel cervello, misura quanto le diverse aree comunicano tra loro
(connettività funzionale) e usa questi dati per addestrare classificatori ML che
provano a prevedere età/sesso del soggetto — con verifica statistica rigorosa
(cross-validation per-soggetto + permutation test) per evitare risultati falsati.

## 2. Come si avvia (dimostrazione rapida, ~1 minuto)

Il dataset di dimostrazione (`eeg_matchingpennies`, un soggetto) è già incluso nel
repository, non serve scaricare nulla. Da terminale, nella cartella del progetto:

```bash
cd Tesi_2.0
make run-step1   # pulizia del segnale (STEP 1)
make run-step2   # ricostruzione alla sorgente (STEP 2)
python -m pipeline_mne_bids.run_e2e_matchingpennies   # STEP 3→6 in sequenza
```

Ogni comando stampa a schermo cosa sta facendo. Alla fine, i risultati (grafici,
tabelle, matrici di connettività) sono in `reports/`.

## 3. Come si verifica che il codice funzioni davvero

```bash
make test
```

Esegue tutta la batteria di test automatici (430 test) che controllano che ogni
singolo componente (lettura dati, connettività, classificazione, statistica) dia il
risultato atteso. Se tutti i test sono verdi (`passed`), il codice è affidabile.

## 4. Dove sono i risultati scientifici veri (dataset completo, non la demo)

Il dataset scientifico è `ds005385` (Dortmund Vital Study). I risultati finali,
onesti e con tutti i limiti dichiarati, sono riassunti in un unico file pensato
apposta per la lettura da parte del relatore:

**[`reports/CLAIMS_HONEST_CONSOLIDATED_FABLE.md`](../reports/CLAIMS_HONEST_CONSOLIDATED_FABLE.md)**

Contiene: il risultato principale (classificazione del sesso dalla connettività
EEG), i tre controlli di robustezza fatti (confound età, sensibilità alla metrica,
generalizzazione su un secondo dataset indipendente) e cosa NON regge, dichiarato
esplicitamente invece che nascosto.

## 5. Come leggere il codice

Il codice è organizzato per step della pipeline, ogni cartella = uno step:

| Cartella | Step | Cosa fa |
|---|---|---|
| `pipeline_mne_bids/` | 1 | Pulizia segnale (wrapper su mne-bids-pipeline) |
| `source_reconstruction/` | 2 | Ricostruzione sorgente cerebrale (dSPM) |
| `parcellation/` | 3 | Divide il cervello in regioni (atlanti standard) |
| `connectivity/` | 4 | Calcola quanto le regioni comunicano tra loro |
| `features/` | 5 | Trasforma i segnali in numeri utilizzabili dal ML |
| `ml_training/` | 6-7 | Addestra e valuta i classificatori |
| `analysis/` | — | Statistica di supporto (intervalli di confidenza, effect size) |

Ogni file `.py` in queste cartelle inizia con una descrizione (`"""..."""`) di cosa
fa e perché, seguita da funzioni con la propria spiegazione (parametri in ingresso,
cosa restituiscono). I punti di logica meno immediati hanno un commento `#` sulla
riga interessata.

## 6. A chi chiedere

Per domande sul metodo statistico o sui limiti dei risultati, il punto di partenza
è sempre `reports/CLAIMS_HONEST_CONSOLIDATED_FABLE.md` (sezione 4 qui sopra): è
scritto apposta per anticipare le domande che un relatore fa di solito.
