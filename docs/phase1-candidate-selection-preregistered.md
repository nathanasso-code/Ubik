# Ubik — scelta candidati ibrido, preregistrazione

Registrata prima di consultare i risultati embedding E5-small.

## Misure secondarie
Per ciascun metodo, a K=3 e K=5, calcolare:
- recall direzionale sulle 46 direzioni delle 23 coppie positive;
- recall per coppia: una coppia positiva conta come recuperata se compare nella top-K di almeno uno dei due eventi;
- numero di coppie candidate distinte tra fonti diverse;
- elenco delle coppie positive non recuperate.

## Regola di scelta, fissata prima di leggere gli embedding
Per il sistema ibrido usare **un solo metodo**: quello con il più alto recall per coppia a K=5 tra TF-IDF originale, TF-IDF action+object ed E5-small action+object. A parità, preferire TF-IDF (originale prima del canonico) perché più semplice ed economico. Non adottare l'unione dei metodi nel test primario. L'unione può essere riportata soltanto come analisi secondaria diagnostica, non come metodo scelto.

La scelta sul gold rende il risultato del successivo ibrido una valutazione *esplorativa sul corpus congelato*, non una stima imparziale della generalizzazione. Nessuna ottimizzazione di soglie o regole di clustering sul gold. Passare poi a nuove fonti.

## Baseline, calcolata prima di leggere embedding
- TF-IDF originale: @3 14/23 coppie, 71 candidate distinte; @5 18/23 coppie, 112 candidate distinte; direzionale @3 23/46 e @5 30/46.
- TF-IDF action+object: @3 15/23 coppie, 71 candidate distinte; @5 16/23 coppie, 112 candidate distinte; direzionale @3 23/46 e @5 28/46.

### Coppie positive non recuperate a K=5
TF-IDF originale:
- S188:E2 — S433:E4
- S382:E5 — S387:E2
- S383:E2 — S387:E2
- S387:E2 — S433:E4
- S408:E4 — S433:E3

TF-IDF canonico:
- S188:E1 — S465:E2
- S188:E2 — S387:E2
- S188:E2 — S433:E4
- S382:E5 — S387:E2
- S383:E2 — S387:E2
- S387:E2 — S433:E4
- S408:E4 — S433:E3

Nota: la coppia C (S382:E1 — S387:E4) è recuperata a K=5 in entrambe le baseline.

## Limite operativo
Completare embedding e verifica ibrida; poi stop al livello 2 sul corpus attuale e passaggio a nuove fonti.
