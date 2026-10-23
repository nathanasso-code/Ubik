# Ubik — handoff sperimentale e decisioni (23 ottobre 2026)

## Stato e obiettivo
Progetto Ubik: piattaforma di informazione, selezione e confronto documentato; topic curati con nuvole di tag, fonti originali, card per notizie fondamentali e nuclei per questioni persistenti. Sviluppo sperimentale su `develop/ubik-core`; non alterare `main` salvo workflow infrastrutturali autorizzati. Obiettivo immediato: ridurre duplicati di una stessa notizia, conservando integralmente la sintesi e le evidenze specifiche di ciascuna fonte, e verificare il compromesso con accorpamenti di sviluppi distinti ma strettamente collegati.

## Decisione di prodotto aggiornata
L'utente considera **più dannoso frammentare una notizia equivalente in più card** che accorpare occasionalmente notizie differenti ma correlate, quando una sintesi di card accurata può esprimere chiaramente tutti gli sviluppi. Questa è una preferenza di progettazione, NON un risultato misurato. Penalizzare in valutazione i falsi split più dei falsi merge, ma evitare che la card inventi un unico evento o perda distinzioni fattuali. Ogni notizia di origine conserva ID, titolo, sintesi, fonte e citazioni testuali; una fonte può comparire in più card.

## Corpus congelato
39 fonti originali, 105 notizie fondamentali estratte, 35 fonti rappresentate nelle card, 4 senza notizie; estrazione e verifica letterale effettuate precedentemente. Grounded DeepSeek: run 39822649930, artifact `grounded-global-news-cards`, 57 card, 46 chiamate API per l'intera estrazione + raggruppamento (NON tutte di clustering), 13 errori. L'evidenza letterale è verificata rispetto al testo estratto nei primi 7000 caratteri, non è una verifica indipendente della verità del contenuto.

## Esperimenti conclusi
1. Neural embedding senza nuove chiamate API: run 39834686597, artifact `neural-embedding-cards`. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, embedding titolo + sintesi, clustering gerarchico complete linkage, soglia 0.79: 73 card. I 105 elementi e gli allegati di fonte sono preservati.
2. Due varianti con titolo addizionale generato da DeepSeek PER OGNI notizia/sintesi (non per articolo o card), embedding locale, candidate graph con soglia 0.68, e verifica DeepSeek dei gruppi candidati. Run 39838631095, artifact `two-track-deepseek-results`, codice `ingestion/frozen_two_track_deepseek_cards.py`.
   - A, `summary`: titolo aggiuntivo + titolo notizia + sintesi; 147 coppie candidate, 12 componenti esaminate, 67 card.
   - B, `source_text`: titolo aggiuntivo + titolo notizia + testo integrale disponibile (tagliato a 7000 caratteri); 418 coppie candidate, 11 componenti esaminate, 68 card.
   - 30 chiamate API DeepSeek totali condivise tra generazione titoli e verifiche, NON per variante. Le due varianti condividono i titoli generati. 105 notizie iniziali; preservati oggetti fonte/sintesi/evidenza.
   - Il testo integrale della stessa fonte viene riutilizzato per ogni notizia estratta da quella fonte, con rischio di similarità tematica artificiale. Il maggior numero di coppie candidate di B NON dimostra maggiore precisione. Nessuna delle due varianti è stata validata con un gold standard umano.
   - DeepSeek interviene sui componenti di candidati, non su tutte le 5460 coppie possibili; massimo 50 revisioni per variante. Componenti grandi vengono divise in batch da 15 e non si accorpano attraverso batch non confrontati. Componenti non revisionate restano singole. La logica di candidate graph non garantisce recall perfetto: coppie sotto soglia non vengono viste da DeepSeek.

## Prossimo esperimento prioritario: estratti testuali specifici
Sostituire B con C: **titolo aggiuntivo specifico + estratti testuali originali pertinenti a quella notizia**, non tutto il testo dell'articolo. Usare gli intervalli `start/end` delle citazioni letterali verificate nell'estrazione per recuperare dal testo della fonte il passaggio esatto, ampliato da contesto locale prima/dopo (finestra esplicita, per esempio 250–500 caratteri per lato; evitare sezioni non pertinenti). Più citazioni per una notizia: deduplicare/accorpare finestre sovrapposte. Non inventare estratti; se la citazione manca o non corrisponde, registrare il problema e usare fallback controllato alla sintesi, distinguendo gli esiti. Conservare sempre testo, offset e quote originali.
Confrontare C contro A sullo STESSO corpus e con titoli identici; misurare numero coppie candidate, gruppi verificati, card, falsi split, falsi merge, copertura, chiamate e token/costo; per valutazione corretta creare almeno un campione annotato manualmente di coppie equivalenti, correlate ma distinte e non correlate. Aggiungere una baseline senza titolo aggiuntivo per misurare l'effetto reale del titolo. Non chiamare un esperimento implementato/eseguito finché non è effettivamente avvenuto.

## Pipeline candidata
Acquisizione lecita testi e abstract estesi -> estrazione LLM di notizie fondamentali, con titolo/sintesi/evidenza letterale -> titolo aggiuntivo specifico (opzionale da validare) -> embedding locale per recuperare candidati -> verifica semantica LLM mirata, con preferenza anti-duplicati -> costruzione card e sintesi multi-sviluppo che non cancelli differenze -> allegati immutati per ciascuna fonte. Soglie e politica di raggruppamento da misurare, non fissare dogmaticamente.

## Esecuzione e infrastruttura
GitHub repo `nathanasso-code/Ubik`. Il workflow esistente `.github/workflows/refresh-ucdp.yml` su `main` offre avvio manuale degli esperimenti, facendo checkout di `develop/ubik-core`; run manuale riuscito 39838631095. Il nuovo `ubik-experiment-runner.yml` non compariva in Actions nonostante il file su main; evitare di moltiplicare workflow per test. Il ramo sviluppo ha avuto code eccessive di workflow su push; verificare trigger e costi prima di ulteriori commit. Per l'esperimento C modificare il runner già registrato, mantenendo l'aggiornamento UCDP schedulato separato. Il precedente esperimento neurale `ingestion/frozen_neural_embedding_cards.py` è disponibile sul ramo sviluppo.

## Criticità metodologiche
- Numero di card inferiore non equivale automaticamente a qualità superiore; tuttavia il prodotto dà maggior peso alla riduzione delle card duplicate, senza accettare sintesi fuorvianti.
- Titolo aggiuntivo è una variabile sperimentale: non attribuirgli benefici senza baseline controllata.
- In C l'estratto va selezionato PER NOTIZIA, non PER ARTICOLO.
- Le fonti non rappresentate e le notizie escluse per assenza di citazioni sono problemi di estrazione, non di clustering.
- Contare chiamate API e token per fase, distinguendo generazione titoli e revisione gruppi; embeddings locali non richiedono API esterne.
- Non cambiare codice di produzione né proclamare qualità verificata sulla base del solo successo GitHub Actions.

## Collegamenti utili
- Grounded extraction: https://github.com/nathanasso-code/Ubik/actions/runs/39822649930
- Neural baseline: https://github.com/nathanasso-code/Ubik/actions/runs/39834686597
- Two-track DeepSeek: https://github.com/nathanasso-code/Ubik/actions/runs/39838631095
- Runner registrato: https://github.com/nathanasso-code/Ubik/actions/workflows/refresh-ucdp.yml

## Aggiornamento successivo — esperimenti A/B con Qwen per evidenze (23 ottobre)
Nuovo script `ingestion/frozen_qwen_passages_two_track.py` (commit `696a93a`) e opzione manuale `qwen-evidence-two-track` nel workflow già registrato `.github/workflows/refresh-ucdp.yml` su `main` (commit `9231404`). **Preparati ma NON ancora eseguiti**.
- A: titolo addizionale specifico per ciascuna notizia fondamentale + titolo notizia + sintesi; embedding locale, DeepSeek per gruppi candidati.
- B: stessi titoli + estratti letterali selezionati da Qwen per la singola notizia, verificati come sottostringhe del testo originale con offset start/end; embedding locale, DeepSeek per gruppi candidati. Fallback alla sintesi in assenza di estratti verificati, marcato `missing`.
- Qwen seleziona i passaggi una volta per fonte con elenco delle notizie estratte; i passaggi validati sono salvati come documentazione associata alle notizie in **entrambi** i risultati, indipendentemente dalla performance del clustering.
- Endpoint OpenRouter e segreto `OPENROUTER_API_KEY`, modello Qwen configurato `qwen/qwen3-32b`; verificare disponibilità e costi al run. Non attribuire a Qwen i raggruppamenti precedenti: erano di DeepSeek.
- Nuova preferenza: falsi split più penalizzati dei falsi merge occasionali, se il titolo e la sintesi della card distinguono espressamente sviluppi correlati. **Problema implementativo ancora aperto**: lo script attuale riutilizza il titolo del primo membro e NON genera una sintesi globale nuova della card; non interpretare i risultati come card editoriali finite.
- Esempi verificati nell'artefatto run 39838631095: `summary-1-0` quattro fonti su deforestazione brasiliana; `summary-5-0` quattro fonti sulla condanna in Messico; `summary-7-0` cinque fonti sulle dimissioni ospedaliere; `source_text-3-14` fonde tre dichiarazioni differenti di Zelensky da S408; `source_text-3-20` fonde la sospensione sanzioni USA con la reazione russa. Gli esempi sono contenuti nel corpus sperimentale, non fatti di cronaca indipendentemente verificati.
