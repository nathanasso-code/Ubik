# Esperimento empirico: ambiguità fra fonti, 16 ottobre 2026

## Risultato eseguito
[GitHub Actions run #38970603252](https://github.com/nathanasso-code/Ubik/actions/runs/38970603252): **success**.

- 36 feed configurati, 34 con successo; 1.165 osservazioni RSS, **1.091 URL distinti**, 15 domini.
- Analisi di candidati **fra domini diversi** con TF-IDF sparso su titolo e descrizione RSS (titolo pesato doppio).
- **155.816 coppie** con almeno un contributo lessicale condiviso (non 155.816 coppie di notizie equivalenti). Classifica delle prime 100 nell'artefatto `ambiguity-candidate-pairs.json`.
- Nessuna API LLM, costo LLM zero. Questa prova **non usa testi integrali** e **non misura precisione semantica**, recall o correttezza degli accorpamenti. Serve a costruire una selezione empirica di casi ridondanti e difficili.

## Esempi realmente emersi (score non probabilistico)

| Coppia | Score TF-IDF | Osservazione da verificare |
|---|---:|---|
| [France 24: Sally Rooney](https://www.france24.com/en/video/20261016-sally-rooney-s-books-no-longer-sold-in-uk-over-support-for-banned-pro-palestinian-group) ↔ [NPR](https://www.npr.org/2026/10/16/nx-s1-6004838/sally-rooney-books-uk-palestinian-action-support) | 0,7035 | Candidato a stesso evento con formulazioni diverse |
| [Al Jazeera: Katie Zacharia](https://www.aljazeera.com/news/2026/10/16/white-house-press-secretary-katie-zacharia-fired-after-five-days-on-the-job?traffic_source=rss) ↔ [ABC Australia](https://www.abc.net.au/news/2026-10-17/katie-zacharia-let-go-white-house/107278730) | 0,6693 | Titoli molto simili |
| [BBC: attacco in Cisgiordania](https://www.bbc.co.uk/news/videos/cqn06zx2r15jo?at_medium=RSS&at_campaign=rss) ↔ [France 24](https://www.france24.com/en/middle-east/20261016-us-journalist-injured-during-israeli-settler-attack-on-west-bank-olive-harvest) | 0,6365 | Stesso contesto, enfasi su soggetti diversi; video vs articolo |
| [BBC: crollo scuola Pakistan](https://www.bbc.co.uk/news/articles/cked326llddgo?at_medium=RSS&at_campaign=rss) ↔ [NYT](https://www.nytimes.com/2026/10/15/world/asia/pakistan-school-collapse.html) | 0,5514 | Titoli riportano **33** contro **32** vittime; non classificare automaticamente come contraddizione |

## Interpretazione
Il confronto dimostra che una selezione multi-fonte con casi di potenziale ridondanza e differenze sottili è **tecnicamente ottenibile** sul corpus reale. **Non dimostra** che il modello sappia ancora distinguere correttamente stesso fatto, sviluppo successivo, evento correlato e contraddizione.

## Prossimo esperimento necessario
1. Utilizzare le 100 coppie candidate come coda di analisi, campionando anche coppie difficili a score intermedio e negativi.
2. Recuperare i testi via Trafilatura dove permesso da robots e dal sito; registrare tipo di fonte (articolo, video, abstract).
3. Confrontare **affermazioni specifiche** e numeri, non soltanto la similarità globale.
4. Registrare etichette revisionate (stesso evento, correlato, diverso, non decidibile), precisione per categoria e costi.
5. Non pubblicare corpi protetti nei report o nei commit.

## Artefatti
Workflow `.github/workflows/cross-source-ambiguity-pilot.yml`; `ingestion/cross_source_candidate_mining.py`; `ingestion/render_cross_source_review.py`. I run più recenti producono anche `ambiguity-review.md` con 40 coppie navigabili.
