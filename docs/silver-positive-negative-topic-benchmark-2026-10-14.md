# Esperimento su coppie positive e negative — 14 ottobre 2026

## Origine
Artefatto reale GitHub Actions run 38632610923, global-discovery-pilot (11926338683). File `discovery/global-rss-pilot.json`, `discovery/hybrid-event-review.json`, `discovery/live-rich-pair-experiment.json`.

## Metodo
Dalle prime 24 coppie candidate sono stati ricavati 34 URL distinti. Assegnazione *silver* manuale di famiglie tematiche usando i titoli: naufragio antico, Starlink Ucraina, Sally Rooney, arresto giornalista giapponese, Nord Stream, salute del Papa, concorso fotografia, Netflix, proteste Albania, accordo diesel USA-Russia.

Sono state escluse dal test le 24 coppie originarie. Tra le combinazioni rimanenti: 29 coppie nella stessa famiglia e 29 coppie di famiglie differenti, campionate con seed 42. Nessun URL ha ricevuto etichette di famiglia in conflitto. TF-IDF unigrammi+bigrams, stopword inglesi, `sublinear_tf=True`, similarità coseno; metriche ROC-AUC e average precision.

## Risultati
| Misura | Titolo | Titolo + descrizione |
|---|---:|---:|
| ROC-AUC | 0.9976 | 1.0000 |
| Average precision | 0.9977 | 1.0000 |
| Mediana similarità coppie stesso tema | 0.1046 | 0.1217 |
| Mediana similarità coppie temi diversi | 0.0000 | 0.0000 |

**Non interpretare come accuratezza su eventi o affermazioni**: le etichette sono ricavate dai titoli e le coppie negative non rappresentano controesempi semantici difficili.

### Esperimento E5 già eseguito
24 coppie candidate; 34 URL richiesti; 17 testi sostanziali letti in memoria; 8 coppie con due testi. Sulle otto coppie: mediana E5 metadati 0.9300; mediana E5 media top-3 segmenti 0.9260; differenza mediana appaiata -0.0027; quattro aumenti e quattro diminuzioni.

**Limite fondamentale:** non sono disponibili embeddings di testi sostanziali per coppie negative, quindi non si può calcolare AUC E5 corpo vs metadati sullo stesso benchmark positivo/negativo. Non sono state verificate contraddizioni fattuali o equivalenza di singole affermazioni.

## Interpretazione e decisione
L'esperimento mostra che su un campione piccolo e tematicamente separabile, i metadati bastano già per distinguere argomenti. Il passo successivo realmente discriminante è costruire *hard negatives* nello stesso tema e annotare indipendentemente identità evento, identità affermazione e relazioni di supporto/contraddizione. Per confrontare E5 corpo e metadati correttamente occorre acquisire in memoria anche i corpi delle coppie negative.

## Riproducibilità
Snapshot: https://github.com/nathanasso-code/Ubik/actions/runs/38632610923

I risultati sono un benchmark esplorativo con etichette *silver*, non una misura di qualità editoriale validata.
