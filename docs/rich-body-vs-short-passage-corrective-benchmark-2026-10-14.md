# Benchmark correttivo: input sostanziali vs passaggi brevi — 14 ottobre 2026

## Perché è stato eseguito
Il benchmark precedente su titoli non rispettava il vincolo di analizzare testi integrali o abstract approfonditi. Questo esperimento utilizza **solo testi sostanziali effettivamente conservati** nell'artefatto della run 38632610923 (file `discovery/rich-text-corpus.json`, artefatto 11926338683).

## Campione e procedura
Nove articoli scientifici Europe PMC con corpo testuale di 28–30 mila caratteri ciascuno (corpi originali talvolta più lunghi). Da ciascun corpo vengono estratte due finestre da 16 frasi: una iniziale usata come query e una circa a metà documento come target breve. Il target lungo è il resto del corpo, **escludendo il passaggio iniziale** per evitare che il confronto sia un semplice ritrovamento di testo identico.

Si confrontano 9 target positivi (stesso documento) con 72 target negativi (documenti diversi). Vettorizzazione TF-IDF con unigrammi+bigrams oppure n-grammi di caratteri 3–5; max 45.000 features, sublinear_tf; coseno. Valutazione: recall@1 e reciprocal rank medio. È un confronto **lessicale**, non E5 o NLI.

## Risultati effettivamente misurati

| Rappresentazione target | TF-IDF | Top-1 | MRR | Mediana coseno positivo | Mediana negativo |
|---|---|---:|---:|---:|---:|
| Secondo passaggio di 16 frasi | parole | 8/9 | 0,9444 | 0,0760 | 0,0304 |
| Secondo passaggio di 16 frasi | caratteri | 6/9 | 0,8333 | 0,1754 | 0,1228 |
| Corpo sostanziale senza passaggio-query | parole | 9/9 | 1,0000 | 0,1396 | 0,0394 |
| Corpo sostanziale senza passaggio-query | caratteri | 9/9 | 1,0000 | 0,3855 | 0,2201 |

## Limiti che impediscono una conclusione sul motore Ubik
1. La positività è «stesso documento», non «stesso evento» né «stessa affermazione». Non è un benchmark di contraddizioni.
2. I passaggi brevi sono porzioni del corpo, **non abstract ufficiali**.
3. I nove documenti sono un campione piccolo e tematicamente eterogeneo: i negativi non sono *hard negatives* annotati.
4. La rappresentazione lunga contiene molte più occasioni di corrispondenza lessicale; il test non isola la qualità della comprensione.
5. Non è stato misurato E5 o NLI in questo benchmark correttivo. Il confronto E5 precedente aveva otto coppie con testi sostanziali e non aveva etichette indipendenti.
6. Il risultato non giustifica un modello esclusivamente proprietario per le relazioni fra affermazioni.

## Decisione tecnica
Conservare il recupero economico TF-IDF/E5 per il primo filtro, usare estrazione di passaggi ancorati alle fonti e confrontare affermazioni specifiche con un secondo stadio NLI/LLM gratuito. Non confondere similarità tematica con conferma o contraddizione. Per decidere la sostituzione dell'LLM servono hard negatives **intra-tema** e un gold set indipendente, su documenti sostanziali effettivamente acquisiti.

## Riproducibilità
Input: https://github.com/nathanasso-code/Ubik/actions/runs/38632610923

Script di analisi locale: `ubik_rich_benchmark.py` (da trasferire nel repository per riproduzione CI). Risultati: `ubik_rich_benchmark_results.json`. La presente nota distingue esplicitamente risultati misurati da funzionalità non ancora integrate.
