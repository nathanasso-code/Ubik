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

## Estensione: accessibilità dei testi per coppie candidate

Implementato `ingestion/cross_source_pair_text_probe.py`, con selezione di **24 coppie** in tre fasce della classifica (prime 8, posizioni 26–33 e 66–73). Le richieste URL sono deduplicate e passano per il controllo robots.txt e il fetch HTTPS già esistenti; Trafilatura misura testo >=800 caratteri / 100 parole e >=1200 / 180. Report `ambiguity-pair-text-coverage.json` nel workflow `cross-source-ambiguity-pilot.yml`. Nessun corpo articolo viene persistito. Aggiunti test di URL condivisi e fetch non riuscito.

**Stato alla stesura:** run https://github.com/nathanasso-code/Ubik/actions/runs/38971480859 in corso durante il probe; non sono ancora disponibili misure finali sulle coppie con testo sufficiente. Il report misura solo accessibilità e lunghezza, non la capacità di distinguere semanticamente eventi o contraddizioni.

## Run J — paired extraction evidence (verified)

[Run 38971520106](https://github.com/nathanasso-code/Ubik/actions/runs/38971520106) **success**. Of 24 selected pairs across three similarity bands, 35 unique URLs were fetched with robots checks: 25 GET successes, 10 GET failures; 22 individual Trafilatura outputs exceeded 800 chars / 100 words; **11 of 24 pairs (45.8%)** passed the threshold on *both* sides. This is access coverage, **not verified full text** or semantic accuracy.

Examples among the 11: Al Jazeera/ABC on Katie Zacharia; BBC/France24 and BBC/DW on West Bank settler attack; Euronews/France24 on Pope Leo; BBC/Guardian on Cyprus hotel death; Guardian/BBC on UK pornography regulation. **Important hard negative candidate:** Ars Technica on Black Sea drone attacks versus DW on two ships burning in Romania's Black Sea waters: geographic/topic overlap is insufficient to merge them without claim-level verification. Titles are not evidence of a common event.

**Next gate:** preserve original URL, date, article type, and extracted claim evidence; compare same-event vs related-event vs distinct-event using the actual texts. Avoid calling the 11 pairs semantic matches or counting their article bodies as complete. The experiment stores no article bodies.

## Run K — anteprima delle card collegate (non validate)

Dai dati dell'artefatto del Run J, le 11 coppie con testo accessibile da entrambe le parti formano **6 componenti connesse** di URL, con dimensioni **5, 4, 2, 2, 2, 2**. Le componenti suggeriscono i nuclei Cisgiordania, Katie Zacharia, Papa Leone XIV, decesso a Cipro, Mar Nero e normativa britannica. Il componente Mar Nero va trattato come potenziale falso accorpamento: la connessione grafica non implica identità di evento.

Aggiunto `ingestion/preview_cross_source_cards.py` e output `ambiguity-card-preview.json` nel workflow, con link, archi e avvertenza per ogni componente. **Nessuna comparazione dei corpi articolo o validazione delle affermazioni è stata eseguita**: si tratta di card provvisorie costruite da coppie RSS con disponibilità di testo. Nuova esecuzione workflow: https://github.com/nathanasso-code/Ubik/actions/runs/38971964145 (in corso alla stesura).

## Run L — confronto transitorio delle affermazioni numeriche

Verificato [run 38972396647](https://github.com/nathanasso-code/Ubik/actions/runs/38972396647), **success**: 11 coppie, 17 URL unici con testo accessibile, 68 frasi con almeno un numero estratte temporaneamente; i testi non sono persistiti. Implementato `ingestion/cross_source_claim_alignment.py` per confrontare le frasi numeriche fra fonti, usando sovrapposizione di termini, conservando solo indici di frasi, conteggi e flag di differenza numerica, senza riportare estratti protetti nei report. `tests/test_cross_source_claim_alignment.py` verifica che il sistema **non attribuisca automaticamente contraddizioni** e si astenga quando i contesti sono dissimili.

**Importante:** questa è ancora una baseline deterministica, **non un LLM**. I risultati dei run successivi che misurano gli allineamenti vanno letti dagli artefatti CI, non dedotti dai test sintetici. La vera classificazione same-event/related/distinct e il grounding LLM restano da sperimentare.
