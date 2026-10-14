# Verifica dei risultati E5 — 14 ottobre 2026

## Esecuzione verificata
- Workflow: https://github.com/nathanasso-code/Ubik/actions/runs/38632610923
- Esito: success.
- Artefatto: global-discovery-pilot, id 11926338683; file discovery/live-rich-pair-experiment.json.
- 24 coppie candidate, 34 URL richiesti, 17 corpi sostanziali elaborati in memoria, 8 coppie con entrambi i corpi; 14 fetch falliti e 3 corpi insufficienti.

## Coppie esaminate
Le metriche E5 sono cosine su embeddings normalizzati; la metrica «testo» è la media delle tre migliori similarità tra segmenti, non il coseno dei documenti integrali.

| Coppia (fonti) | Metadati E5 | Passaggi top-3 E5 | Differenza |
| --- | ---: | ---: | ---: |
| Starlink Ucraina (Guardian, Al Jazeera) | 0.9357 | 0.9257 | -0.0100 |
| Processo Nord Stream (BBC, DW) | 0.9399 | 0.9266 | -0.0133 |
| Starlink Ucraina (BBC, Al Jazeera) | 0.9299 | 0.9205 | -0.0094 |
| Wildlife Photographer of the Year (BBC, Guardian) | 0.9301 | 0.9480 | +0.0179 |
| Licenziamenti Netflix (BBC, Guardian) | 0.9320 | 0.9261 | -0.0059 |
| Proteste Albania (Al Jazeera, DW) | 0.9213 | 0.9235 | +0.0022 |
| Starlink Ucraina (BBC, Ars Technica) | 0.9235 | 0.9369 | +0.0134 |
| Proteste Albania (Guardian, DW) | 0.9253 | 0.9258 | +0.0005 |

Mediana metadati: **0.9300**; mediana passaggi top-3: **0.9260**. Tre coppie migliorano di oltre 0.001, quattro peggiorano e una rimane quasi invariata (soglia convenzionale, non statistica). I punteggi non sono calibrati come probabilità.

## Interpretazione
- I titoli suggeriscono sovrapposizioni tematiche credibili, ma **non costituiscono gold label** di identità evento o accordo tra affermazioni.
- Il corpo non migliora sistematicamente la similarità: non si può concludere che il rich text aumenti precisione o recall.
- Tutti i punteggi E5 sono molto alti (circa 0.92–0.95), quindi la discriminazione tra casi difficili richiede **negative pairs**, soglie calibrate e revisione indipendente.
- I tre accoppiamenti Starlink possono appartenere a un cluster informativo; non bisogna confondere il numero di coppie con il numero di eventi distinti.
- Le due coppie Albania possono riflettere sottoeventi diversi della stessa protesta; verificare temporalità, attori e localizzazione prima dell'accorpamento.
- Il dataset seleziona coppie già simili dai metadati: **selection bias**. Non include controesempi difficili o coppie casuali.
- Non è stato effettuato NLI su singole affermazioni; non esistono contraddizioni verificate.

## Prossimo esperimento falsificabile
1. Acquisire campione bilanciato: positivi editorialmente verificati, negativi vicini per tema e negativi casuali.
2. Estrarre frasi candidate dai corpi accessibili **in memoria** e collegarle a URL, posizione e tempo.
3. Confrontare separatamente «stesso evento», «stessa affermazione», «conferma», «contraddizione», «integrazione»; astensione se evidenza insufficiente.
4. Calcolare precision@k e recall con etichette indipendenti; confrontare metadati, E5 passaggi, eventuale NLI.
5. Non persistere testi non licenziati, non aggirare robots/paywall.

Questa nota sostituisce ogni interpretazione precedente che descrivesse l'esperimento E5 come ancora in corso.
