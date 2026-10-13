# UBIK — DOSSIER DI CONTINUITÀ E SVILUPPO
**Aggiornamento: 13 ottobre 2026. Documento di passaggio a una nuova chat.**

> LEGGERE PRIMA DI INTERVENIRE. Repository `nathanasso-code/Ubik`, branch `develop/ubik-core`. Non alterare `main`, Vercel, Supabase o il corpus di produzione senza verifiche e autorizzazione per azioni distruttive. Questo dossier integra, NON sostituisce, `docs/HANDOFF_UBIK_2026-10-12.md`, `docs/START_HERE_UBIK.md`, `docs/CORE_ARCHITECTURE.md` e `ingestion/README.md`.

## 1. Principi di prodotto: decisioni da preservare

Ubik è una piattaforma **topic-first** di informazione e discernimento assistito, con fonti originali, provenienza, sintesi verificabili e contributi umani documentati. Il precedente schema Pulse/Press/Insights è una tappa storica: **non ripristinarlo come navigazione obbligatoria**. I topic sono matrice tematica, tag cloud, fonti, card ed eventuali nuclei epistemici. Distinguere: documento, evento, questione persistente, affermazione, prova, segnalazione sociale e revisione.

Tre viste dello stesso catalogo: **Esplora → Rilevanti → Essenziali**. La promozione in Essenziali richiede revisione esplicita, non punteggio automatico di popolarità. La provenienza delle fonti e l'indipendenza dei loro contenuti sono due proprietà diverse.

Quattro segnali per priorità di revisione: (1) condivisioni di account realmente indipendenti, (2) segnalazione anche singola di account seguito, con peso normalizzato, (3) competenza/identità documentabili, (4) discussione sostanziale con evidenze. Nessuno dei quattro equivale a verità o validazione. L'utente ha **escluso la raccolta dei testi dei reply thread** dalla roadmap corrente: usare post pubblici originali e documenti, non basare il criterio 4 sui thread delle risposte.

## 2. Ricostruzione cronologica retrospettiva

Ricostruzione basata su commit e documenti presenti sul branch; non è una trascrizione integrale delle conversazioni perdute.

### Fondazioni e architettura
- Il sito ha una UI topic-first e un precedente corpus di attacchi/eventi. `assets/ubik-core.js` definisce contratti condivisi; `assets/temporal.js` e `assets/map-view.js` estraggono componenti riutilizzabili. `api/feed.js` legge ancora da Vercel Blob, non dalle nuove tabelle Supabase.
- `supabase/migrations/001_event_corpus.sql` è lo schema precedente. `002_source_topic_catalog.sql` è una **proposta non applicata** per editori, documenti, scoperte, topic, associazioni e revisioni.
- Ingestion indipendente dall'editoriale: `ingestion/contracts.py` produce osservazioni `not_assessed`, `canonical_url_hint` rimuove tracker noti ma NON dimostra identità canonica.
- Sono stati realizzati prototipi per RSS, GDELT DOC (query limitate, non firehose), Hacker News, Bluesky, Mastodon, Crossref, OpenAlex; archiviazione SHA256 locale, trasporto con retry e limiti, batch manuali con checkpoint e budget. Non esiste ancora scheduler distribuito affidabile con persistenza cloud e riconciliazione delle cancellazioni.

### 10–11 ottobre: raccolta e prototipi topic
- Il pilot RSS su fonti IA si è allargato a BBC World, Guardian World, Al Jazeera English e NYT World. Run documentato `38120774636`: 2.797 osservazioni grezze, 23/28 feed riusciti, 21 con contenuti; non 2.797 notizie uniche. Le fonti con 403 o limiti dimensione non devono essere aggirate.
- Il topic IA è stato integrato nella struttura esistente: 30 fonti/carte originali, contributi Bluesky associati, tag cloud; commit del 11 ottobre `70514f5a`, `5fc4ea56`, `8beabdc0`, `f4f8fdf3`. Il campione è **curato**, non prova di scoperta cieca.
- Il pilot editoriale `topic_feed_pilot` ha individuato ~105–106 candidati IA e mostrato 30; `topic_event_review` ha trovato solo 1 coppia per sovrapposizione titoli nel campione verificato, senza unire eventi. `topic_evidence` ha raccolto frasi estrattive da descrizioni RSS (100 con descrizioni, 5–6 title-only a seconda del run). `topic_review_priority`, `topic_editorial_worksheet` e `topic_annotation_audit` sono strumenti di revisione, non una validazione già completata.
- `ingestion/preview_html.py`, `topic_feed_preview.py` e `UBIK_ALL_SOURCES_REVIEW.html` hanno fornito anteprime offline; gli artifact GitHub scadono. La visualizzazione non implica deploy in produzione.

### 12 ottobre: discovery Mastodon e qualità
- `ingestion/mastodon_discovery.py` interroga modalità pubbliche local/federated/tag/account su istanze autorizzate; `mastodon_merge.py` deduplica URI ActivityPub. Pilot IA su Mastodon: 640 post, 602 URI unici, 38 ripetizioni; i 602 post non sono 602 articoli. La ricerca era condizionata da hashtag IA.
- `social_source_catalog.py` prototipa scoperta di editori dai link social. `topic_quality_views.py` implementa offline tre viste progressive. Il registro editori/documenti resta proposta SQL, non database live.
- Sono stati studiati i criteri di convergenza indipendente e discussione sostanziale; `topic_review_priority` non deve trasformarsi in ranking di popolarità. Esistono prototipi di lettura contesto reply nel repo (`public_thread_context.py`) ma **non sono da estendere**, in seguito a decisione utente.
- Un precedente tentativo di cercare direttamente il caso di attacchi ai data center russi e bot via web è stato rifiutato come esperimento perché **condizionava la scoperta**. La regola da allora: il topic generale è il solo seed iniziale, il resto deve emergere dai dati della pipeline.

### 12–13 ottobre: discovery cieca per topic e nuovi moduli
- `ingestion/topic_social_discovery.py`: ricerca testuale Bluesky AppView e hashtag Mastodon; estrae post pubblici, link e provenienza. `topic_social_discovery_cli.py`: esecuzione manuale esplicita, dry-run di default. `tests/test_topic_social_discovery.py`: primi test.
- Workflow `.github/workflows/topic-social-blind-pilot.yml` esegue il topic **Guerra russo-ucraina**, con alias generali Ucraina/Ukraine/Russia/Україна/Россия, senza parole chiave sull'evento data center. Il primo run `38314998550` ha prodotto **226 post e 155 URL** senza errori registrati; non è una misurazione della copertura dell'intera rete.
- `topic_query_expansion.py` deriva hashtag co-occorrenti dai post seed, richiede almeno 2 account osservati, esclude alcuni hashtag generici, limita a 8 query di secondo passaggio, conserva post di supporto. La raccolta successiva `38315953912` ha prodotto **230 post e 164 URL**.
- `topic_document_expansion.py` estrae token ripetuti dagli slug URL condivisi da almeno due account su documenti distinti, limitando le query; `topic_event_candidates.py` raggruppa in modo prudente URL con sovrapposizione di token, **senza dichiarare equivalenza semantica**. Sono presenti test `tests/test_topic_document_expansion.py`. `topic_discovery_diagnostics.py` produce metriche di copertura e limiti espliciti.
- Run ampliato `38316394327` **success**: **1.214 post, 937 URL, zero errori di acquisizione registrati**. La forte crescita non prova qualità: fra gli hashtag di espansione emersi figurano **trump, zelensky, putin**. Questo segnala un rischio concreto di **deriva tematica** verso discussioni geopolitiche generiche. I 937 URL sono indizi di documenti, non 937 notizie o fonti indipendenti.
- Il caso data center compare in un URL del campione iniziale di `5.ua`, ma la specifica controversia sulla presunta riduzione dei bot **non è stata confermata come cluster autonomo dalla pipeline**. Non attribuire a Ubik una scoperta che non è documentata.
- Le verifiche GitHub Core checks e il workflow di raccolta sopra citati risultavano riusciti al momento della ricostruzione. Le modifiche successive richiedono un nuovo controllo CI.

## 3. Diagnosi tecnica attuale — evitare falsi progressi

1. **Campionamento**: ricerca Bluesky `sort=latest`, poche pagine o una pagina per query; hashtag Mastodon su istanze limitate. Non abbiamo una copertura temporale continua, né una baseline giornaliera; la ricerca per hashtag non equivale alla ricerca di tutto il testo.
2. **Deriva**: espandere su `#trump` può recuperare molto materiale estraneo al conflitto. Imporre un test di pertinenza basato su documenti osservati e un limite di allontanamento dalla radice; conservare separatamente `seed` e `expanded`.
3. **Provenienza**: l'espansione è auditable, ma due account non equivalgono a due origini editoriali indipendenti. Mastodon può riproporre contenuti via bridge; bot, syndication e crosspost vanno distinti.
4. **Eventi**: il raggruppamento da slug URL è debole, non multilingue e può confondere temi generici. Serve estrazione di titoli/abstract verificabili e confronto semantico con controllo dei falsi positivi; non unire automaticamente documenti.
5. **Misura della discussione**: numero reply/like non significa dibattito sostanziale. Il testo del post originale può essere analizzato con attribuzione, senza recuperare i reply.
6. **Identità dei link**: gli URL canonici non sono ancora verificati via publisher; il filtro dei link HTML social può raccogliere link di profili/bridge non pertinenti. Necessaria normalizzazione conservativa e tracciamento dei redirect senza aggirare restrizioni.
7. **Persistenza**: i risultati GitHub sono artifact temporanei (attualmente retention 7 giorni nel workflow); non sono database. Non abilitare trigger automatici alla creazione topic senza code, idempotenza, quote, protezioni e schema rivisto.

## 4. Stato funzionale — cosa NON dichiarare completato

| Funzione | Stato |
| --- | --- |
| Topic-first UI e topic IA dimostrativo | Codice esistente, verificare deploy effettivo |
| RSS multi-fonte | Pilot live documentato; non scheduler universale |
| Bluesky ricerca pubblica / Mastodon hashtag | Pilot live su GitHub Actions |
| Espansione hashtag da dati | Implementata, bias/deriva non calibrati |
| Espansione da termini di URL | Implementata come euristica, non NER |
| Raggruppamento documenti stesso evento | Euristica candidata, non semantica |
| Contenuti di articoli / sintesi verificate | Non integrati in questo pilot |
| Accelerazione temporale | Non misurata |
| Indipendenza reale account/fonti | Non verificata |
| Tre viste di qualità | Prototipo offline, non UI live completa |
| Supabase catalogo fonti/topic | Migrazione proposta, non applicata |
| Trigger creazione topic e scheduler persistente | Non implementati |
| Card epistemiche automatiche validate | Non implementate |
| Recupero reply thread | Fuori roadmap per decisione utente |

## 5. Priorità di sviluppo (ordine consigliato)

1. **Correggere il drift prima di raccogliere di più**: fissare un corpus seed immutabile, distinguere query generate, misurare pertinenza e distanza dalla radice; limitare a due passaggi, evitare hashtag generalisti/personaggi non specifici come espansioni automatiche senza evidenza tematica aggiuntiva.
2. **Finestra temporale e paginazione**: supportare cursor Bluesky e max_id Mastodon con budget per query, dedup per URI e snapshot append-only; misurare distribuzione per data e copertura per lingua/istanza.
3. **Documenti ed eventi**: usare titoli e descrizioni raccolti da RSS/editori con provenance; introdurre retrieval semantico multilingue **come suggerimento di coppie** e validazione separata.
4. **Card**: separare card-documento, card-evento e nucleo epistemico; ogni sintesi deve dichiarare quali fonti sono state realmente lette e quali claim non sono verificati.
5. **Persistenza**: revisionare SQL 002, definire `topic_discovery_runs`, `query_expansions`, `post_observations`, `document_links`, `event_candidates` e politiche RLS; prima un pilota isolato.
6. **Automazione**: dopo persistenza, evento topic-created → job idempotente → snapshot → review → esposizione in Esplora. Non bloccare creazione topic su API social.
7. **Validazione**: A/B cieco su almeno due topic e finestre diverse, annotazioni umane di pertinenza, precision/recall eventi, falsi merge, origine indipendente, drift, costi e tempo.

## 6. File chiave e comandi

```sh
python -m unittest discover -s tests
node tests/ubik-core.test.cjs
python -m ingestion.topic_social_discovery_cli 'Guerra russo-ucraina' --alias Ucraina --alias Ukraine --alias Russia --alias Україна --alias Россия --limit 40 --expand --max-expansion-terms 8 --document-expansion --max-document-terms 6 --live --output blind-topic-result.json
```

L'ultimo comando **effettua chiamate live** e va usato soltanto con limiti e autorizzazioni adeguate. Per il dry-run omettere `--live`.

Run da confrontare:
- https://github.com/nathanasso-code/Ubik/actions/runs/38314998550
- https://github.com/nathanasso-code/Ubik/actions/runs/38315953912
- https://github.com/nathanasso-code/Ubik/actions/runs/38316394327

## 7. Istruzioni per la prossima chat

Leggere integralmente questo dossier e gli altri quattro documenti di continuità; verificare HEAD e ultimi workflow; **non confondere il commit con il deploy**. Continuare autonomamente su `develop/ubik-core`, un incremento testabile alla volta. Conservare gli artifact prima della scadenza, o riprodurre l'esperimento. Non utilizzare Yandex/data center/bot come query seed nella prova cieca. Il tema noto può essere controllato **solo a posteriori** come test di richiamo, senza influenzare il ranking.

Annotare ogni cambiamento in questo dossier o appendice datata, con SHA, run, dati, problemi, decisioni e passi successivi. Non promettere esecuzioni in background senza un workflow effettivo.


## 8. Aggiornamento 13 ottobre — svolta global-first (NUOVA DECISIONE)

**Decisione dell'utente:** esplorare la raccolta il più diffusamente possibile senza imporre un topic come seed; riconoscere argomenti chiave e assegnarli ai topic *a posteriori*. Architettura scelta: **global-first ibrida**, con acquisizione indipendente dai topic e approfondimenti topic-led successivi soltanto per lacune documentate. Questo **non** cambia la UI topic-first: cambia l'ordine di acquisizione e associazione.

**Nuovo codice:** `ingestion/global_discovery.py` legge snapshot compatibili con `ingestion/federate.py`, aggrega osservazioni per URL normalizzato e propone termini dai titoli senza filtro tematico. Un candidato richiede >=2 documenti e >=2 coppie connector/source; gli URL di supporto restano visibili; un repost ripetuto dello stesso documento non crea un falso segnale di convergenza. `tests/test_global_discovery.py` verifica queste proprietà. È **solo un prototipo offline lessicale**: non NER, non ricerca web globale, non eventi semanticamente verificati, non assegnazione automatica ai topic.

**Nuovo documento decisionale:** `docs/GLOBAL_DISCOVERY_ARCHITECTURE_2026-10-13.md`. Leggerlo insieme a questo dossier.

**Vincoli da preservare:** il topic-first resta la UX, non un filtro obbligatorio d'ingresso. Documenti unici possono appartenere a più topic. La raccolta globale non deve essere scambiata per un firehose universale. Non costruire card fattuali dai soli titoli o slug.

**Prossimi interventi:** integrare la raccolta diretta RSS multi-argomento con questo output in un workflow offline/live bounded; misurare due finestre temporali; introdurre eventi semantici multilingue con test di precisione e una coda di assegnazione topic revisionabile. Prima di dichiarare questo incremento validato, controllare CI del commit che lo contiene.


## 9. Incremento global-first live — 13 ottobre 2026

**Implementazione:** `ingestion/global_rss_pilot.py` riutilizza il parser RSS/Atom esistente e le protezioni HTTP, rimuove esplicitamente `topic_ids` e marca le osservazioni `global_unassigned`. `config/source-registry.global-pilot.json` definisce 10 feed in ambiti mondo/scienza/tecnologia/ambiente/economia. `.github/workflows/global-discovery-pilot.yml` esegue test, acquisizione live e `ingestion.global_discovery`, conserva due JSON come artifact GitHub a scadenza 14 giorni. Test `tests/test_global_rss_pilot.py` per topic non assegnato e budget.

**Incident e correzione:** primo run `38317565952` fallito per invocazione unittest con modulo `tests.test_global_rss_pilot` non importabile (cartella tests non package); workflow corretto a `unittest discover -s tests -p 'test_global*.py'`, commit `635a92a9`. Secondo run `38317573397`: test, acquisizione e analisi superati; al controllo dei log **10 feed configurati, 9 riusciti, 333 osservazioni e 324 URL distinti**. Il job potrebbe ancora finalizzare l'upload dell'artifact: verificare conclusione prima di dichiararlo totalmente completato.

**Interpretazione:** questa è la prima raccolta generalista effettiva **senza seed di topic**, non ancora confronto quantitativo corretto con un run topic-led sulla stessa finestra temporale. I termini emergenti dai titoli sono candidati lessicali e possono essere parole generiche; nessuna card fattuale, validazione o topic assignment automatica.

**Prossimo step obbligatorio:** usare lo stesso corpus di 324 URL come baseline, annotare pertinenza e specificità dei candidati, confrontare con una raccolta topic-led nella stessa finestra; ampliare fonti linguistiche, correggere stopword e introdurre eventi semantici multilingue. Non presentare 333 osservazioni come 333 notizie indipendenti.

Run: https://github.com/nathanasso-code/Ubik/actions/runs/38317573397


## 10. Incremento successivo — coppie evento da corpus globale

**Codice aggiunto:** `ingestion/global_event_pairs.py`, `tests/test_global_event_pairs.py`. Il workflow global-first ora esporta `global-event-pairs-review.json` accanto agli snapshot e ai termini candidati.

Il motore crea **solo proposte di coppie da revisionare** tra URL distinti di host diversi: richiede almeno due termini significativi condivisi nei titoli, weighted Jaccard >=0,44 e date di pubblicazione distanti al massimo 72 ore. Esclude parole generiche, limita la combinatoria con un indice invertito e un tetto sui termini molto frequenti. Nessuna fusione automatica, nessuna assegnazione ai topic, nessuna validazione fattuale. Questa è una baseline conservativa **non multilingue semantica**; va valutata contro annotazioni reali prima di ampliarla.

**Test regressione:** stessa storia tra editori diversi, argomenti genericamente correlati da tenere separati, finestra temporale, stesso host e data mancante. Un primo Core checks `38317793293` ha fallito sul caso di argomento generico; correzione dei termini `government`/`discusses` commit `e8a68c9d`. Nuovo run global-first `38317808123` e Core checks successivi da verificare.

**Prossima priorità:** analizzare i candidati reali e annotare falsi positivi, poi costruire una baseline di confronto global-first vs topic-led su stesso corpus/finestra, senza introdurre manualmente termini del caso di controllo.


## 11. Traguardo: prime card documentali REALI, non sintetizzate (13 ottobre 2026)

**Codice:** `ingestion/global_cards.py`, `tests/test_global_cards.py`, workflow `.github/workflows/global-discovery-pilot.yml` aggiornato. Il generatore accetta solo titoli e URL dei feed realmente acquisiti. Emette card a fonte singola o coppie suggerite dal confronto dei titoli; ogni card espone provenance e `review_status=unverified`. Produce `global-cards-preview.json` e `global-cards-preview.md` negli artifact del workflow. Non genera affermazioni fattuali, sintesi AI, assegnazioni topic o fusioni automatiche.

**Run:** https://github.com/nathanasso-code/Ubik/actions/runs/38318112930 — nei log risultano superati test, acquisizione, generazione card e upload. **24 card: 4 coppie candidate a doppia fonte e 20 card singole**. Le quattro coppie sono:
1. BBC / Al Jazeera: titoli relativi alla perquisizione dell'abitazione della deputata Ilhan Omar.
2. BBC / The Guardian: titoli relativi alla notizia sulla morte dell'attore RJ Mitte.
3. BBC / NYT: titoli su un naufragio vicino a Gibuti; BBC indica 139 morti, NYT oltre 100: la differenza è preservata, non risolta arbitrariamente.
4. BBC / Al Jazeera: titoli relativi alle dimissioni del vicecapo della polizia sudafricana.

**Interpretazione:** sono output effettivi della pipeline globale senza seed tematico, NON fatti verificati, NON quattro eventi confermati. I titoli dei feed possono contenere affermazioni errate o divergenti. Le card sono anteprime offline, **non integrate nella UI Vercel**. La successiva fase deve leggere i documenti nel rispetto delle autorizzazioni e proporre sintesi citate, con revisione di corrispondenza evento e test di precisione.

**Limitazione importante:** i 20 documenti singoli sono i primi documenti non già coperti dalle coppie secondo l'ordine di acquisizione, **non un ranking di rilevanza**.


## 12. Ricerca ibrida social→documenti→topic, associazione contestuale degli hashtag (13 ottobre)

**Chiarimento fondamentale:** le 24 card del run `38318112930` erano basate **solo su RSS**, non sui link condivisi su Bluesky/Mastodon. I precedenti pilot social raccoglievano link, ma la loro unione sistematica alla pipeline globale non era ancora implementata. Non dichiarare che le 24 card derivino dai social.

**Nuovi moduli implementati:**
- `ingestion/global_social_followup.py`: usa **termini scoperti dai titoli RSS globali**, non nomi dei topic, per query limitate di testo Bluesky e hashtag Mastodon; conserva post originali, hashtag, link condivisi ed errori. I termini sono osservati ma possono essere generici; copertura non esaustiva.
- `ingestion/hybrid_document_links.py`: unisce documenti RSS e URL condivisi nei post social, preservando provenienza, post e piattaforme; documenti solo social restano hint non verificati.
- `ingestion/hashtag_topic_routing.py`: propone relazioni hashtag→topic **esistenti** di `data/catalog.json` usando testo dei post e descrizioni/domande dei topic con TF-IDF a n-grammi di caratteri. Richiede almeno due post e due account osservati, supporta astensione, conserva URL dei post e dei documenti. **Non è ancora semantic embedding multilingue**: è similarità lessicale contestualizzata, non equivalenza concettuale verificata.
- `tests/test_hybrid_discovery.py`: test unione RSS/social, astensione e provenance delle query. Workflow `.github/workflows/global-discovery-pilot.yml` ora produce `global-social-followup.json`, `global-hybrid-links.json`, `global-hashtag-topic-review.json` come artifact oltre ai precedenti.

**Stato run:** `38318744476` era in corso alla scrittura di questo aggiornamento. Nuovo workflow con test hybrid esplicitamente inclusi commit `ddaa2cc2`; verificare run più recente prima di dichiarare successo.

**Priorità:** verificare quali hashtag abbiano davvero evidenza contestuale sufficiente; correggere l'estrazione tag dai facet Bluesky e la qualità del testo Mastodon, calibrare falsi positivi su topic reali; solo dopo introdurre embeddings multilingue e routing probabilistico con soglia di astensione. Non trasformare candidati in tag confermati senza revisione.


### Esito controllato del run ibrido corretto

Run https://github.com/nathanasso-code/Ubik/actions/runs/38318872281: fasi test, RSS, social, join, routing, card e artifact riuscite. **232 post, 169 URL social, 324 URL RSS, 0 sovrapposizioni esatte**, 63 hashtag con almeno due post/account e **0 associazioni topic sopra soglia**. Questo è un risultato valido di **astensione** e non va forzato con associazioni arbitrarie. Le query `against`, `scientists`, `review`, `airport`, `india`, `attack` erano ancora troppo ampie; è stato aggiunto un ulteriore filtro, commit `1ff84931`, da valutare in un run successivo. Un corpus così piccolo e una finestra breve possono non coprire i topic esistenti.

**Limite architetturale esplicito:** le query attuali sono token singoli, e una lista stopword che cresce manualmente non risolve il problema generale. Occorre selezione contestuale di frasi specifiche ed entità da almeno due documenti, non ulteriori blacklist come soluzione finale. Per associazione semantica multilingue serve un modello di embeddings con provenienza, calibrazione e controllo di astensione; l'attuale TF-IDF a n-grammi è solo una baseline contestuale. Non rivendicare matching semantico pieno.


## 13. Componente semantica profonda e governance dei topic (13 ottobre 2026)

**Vincolo prodotto confermato:** gli hashtag NON sono sezioni o topic. Ubik mantiene un **catalogo editoriale limitato di topic**: i documenti e gli hashtag possono essere molti, ma si collegano ai topic esistenti o restano non assegnati. Nuovi topic richiedono valutazione editoriale separata (importanza, persistenza, assenza di topic adeguato, sostenibilità della moderazione); mai generazione automatica per articolo/hashtag.

**Implementazione:** `ingestion/semantic_topic_router.py` usa un backend opzionale di **embeddings multilingue reali** `intfloat/multilingual-e5-small` (non TF-IDF). Codifica descrizioni e domande dei topic da `data/catalog.json` e hashtag **con contesto dei post**, usando il prefisso `query:` previsto per similarità simmetrica. Confronta coseno con i topic esistenti; richiede almeno due post e due account osservati, soglia prudente e distacco dal secondo classificato; altrimenti **astensione**. Ogni proposta conserva post e URL esterni; non crea topic, sezioni, né pubblica automaticamente. Il punteggio coseno NON è probabilità calibrata.

**Test:** `tests/test_semantic_topic_router.py` verifica contratto del modello, prove social, astensione per ambiguità e assenza di creazione topic. **Esecuzione modello live:** workflow manuale `.github/workflows/semantic-topic-routing-pilot.yml` installa runtime opzionale, acquisisce RSS+social global-first, genera artifact `semantic-topic-review.json`. Non è attivato automaticamente e non modifica produzione. Va eseguito esplicitamente e valutato prima di dichiarare un miglioramento quantitativo.

**Rischi aperti:** soglie 0.84 e margine 0.06 sono iniziali e **non calibrati**; E5 è retrieval semantico, non riconoscimento certo di causalità, eventi o topic. Query social globali ancora soggette a drift. Servono esempi etichettati positivi/negativi multilingue, calibrazione e un gate editoriale per nuove proposte di topic. Gli hashtag non diventano una tassonomia UI.


## 14. Razionalizzazione repository — prima fase non distruttiva

**Audit branch e PR:** API GitHub mostra solo `main` e `develop/ubik-core`; nessun PR. Non esistono branch secchi da cancellare. `main` non è stato toccato.

**Nuovo riferimento canonico:** `docs/ARCHITECTURE_CURRENT.md` mappa la pipeline globale, i moduli attivi, i prototipi storici, i workflow, il debito tecnico e i vincoli di governance (pochi topic editoriali, hashtag non sezioni). `docs/START_HERE_UBIK.md` è marcato esplicitamente come storico e reindirizza al documento canonico. I vecchi rapporti e test non sono stati eliminati senza analisi degli import: molti restano prove di regressione e dei limiti già misurati.

**Debito individuato:** il confine dichiarato in `ingestion/README.md` non corrisponde più alla collocazione dei moduli `global_cards`, `semantic_topic_router` e routing: l'area ingestion ospita anche selezione/review. Necessaria migrazione controllata verso package `discovery/` e `selection/` con wrapper compatibili, test e CI. La nuova architettura è in parte un piano, non ancora un refactor completo.

**Pulizia successiva:** generare manifest di riferimenti per moduli/documenti/workflow, classificare `active / compatibility / experimental / archived / removable`, quindi rimuovere soltanto elementi con zero dipendenze e rollback semplice. Verificare il modello multilingue su dati reali e calibrare le soglie prima di promuoverlo.


## 15. Esperimento cieco sulle relazioni e primo indizio datacenter

Nuovo `ingestion/blind_relation_hypotheses.py` con test `tests/test_blind_relation_hypotheses.py`, integrato nel workflow global-first. Non usa seed di topic, datacenter, guerra o parole del caso di controllo. Su run riuscito https://github.com/nathanasso-code/Ubik/actions/runs/38319820495 : **324 documenti RSS e 35 coppie di termini con co-occorrenze cross-publisher**. È una baseline lessicale: `relation_type=undetermined`, non supporto, contraddizione o causalità.

**Osservazione notevole:** il titolo RSS attribuito ad Ars Technica `Russia was not ready for the data center war it started with Ukraine` compare fra le evidenze della coppia `russia / ukraine`, insieme ad altri titoli di editori diversi. Il caso datacenter NON era un seed del motore. Questo dimostra l'acquisizione di un documento pertinente senza query mirata, **non** il riconoscimento della relazione epistemica, né la verifica dell'articolo, né corroborazione indipendente sul datacenter. L'accostamento è dovuto alle parole Russia/Ucraina. La valutazione retrospettiva deve essere svolta dopo aver congelato i candidati, senza cambiare le regole in funzione del caso.

Protocollo scientifico: `docs/BLIND_EPISTEMIC_DISCOVERY_PROTOCOL.md` definisce separazione blind/held-out, annotazioni delle relazioni e criteri di precisione. La pipeline E5 multilingue è ora in prova live: workflow `38319834727` (stato da verificare); nuovo job `semantic-review` nel workflow globale consuma lo stesso artifact del run di discovery, evitando differenze di campionamento, commit `08437931`. Non dichiarare esito E5 finché il job non è completato.


## 16. Blind multilingual semantic retrieval: RESULT CONFIRMED (13 October)

Run [38320346965](https://github.com/nathanasso-code/Ubik/actions/runs/38320346965), both jobs **success**. The exact semantic artifact was downloaded and inspected, not inferred from job summaries. **324 RSS documents; 1,258 cross-host semantic neighbor pairs** (cosine ≥0.72). Topic router: 79 eligible hashtags, **0 proposals, 79 abstentions**. This abstention is not evidence of calibrated precision.

**Held-out datacenter recovery (not seeded):** frozen semantic rank **59**, cosine **0.8815**, paired BBC RSS `Ukraine strikes Yandex data centre in third attack on Russian tech giant` with Ars Technica RSS `Ukraine’s drones knock out AI data center belonging to "Russia’s Google"`. Rank **63**, cosine **0.8791**, paired BBC with Ars `Russia was not ready for the data center war it started with Ukraine`. Source URLs and explicit negative examples are in `docs/BLIND_SEMANTIC_RESULT_2026-10-13.md`. This is a successful **unseeded document association**; NOT independent confirmation of the reported event, causal discovery, or source-text-based epistemic analysis. The model still makes clear false-positive links (unrelated American datacenter opposition; distinct wartime targets).

**New editorial gate:** `ingestion/epistemic_review_queue.py` produces a diverse, bounded human-review queue from the frozen semantic pairs, preserving original ranks and all source URLs. The new `semantic-pair-review-queue.json` artifact is generated by the global workflow. This is selection for review only, not a claim classifier. Additional test `tests/test_semantic_pair_review_queue.py`. Next: retrieve source bodies and explicit claims; annotate true same-event vs related context vs false positives and contradictions. No automatic topic/section creation.

**Concurrent repository changes:** a separate existing `tests/test_epistemic_review_queue.py` covers `scripts/build_epistemic_review_queue.py`; do not overwrite it or conflate its RSS observation sampling with the semantic pair queue.


## 17. Gate per affermazioni epistemiche — stato e limiti verificabili

Nuovo modulo `ingestion/epistemic_evidence_gate.py` e test `tests/test_epistemic_evidence_gate.py`: validazione conservativa di annotazioni **umane** con brani testuali verbatim, URL originali, hash SHA-256 del testo acquisito, due brani per relazioni sostanziali, due affermazioni esplicite e motivazione, identificativo del revisore. Output: `eligible_for_editorial_review`, `verified_as_true=false`, `automatic_publication=false`. Il gate NON acquisisce articoli, NON verifica autenticità o verità e NON decide automaticamente supporto/contraddizione. Nessun risultato epistemico reale è stato promosso. Contratto completo e istruzioni per altra chat: `docs/EPISTEMIC_REVIEW_CONTRACT.md`.

Workflow `38320735744` completato **success**: 324 documenti, 1.256 coppie semantiche, 60 coppie nella coda di revisione, 80 hashtag eleggibili, 0 proposte e 80 astensioni. Il benchmark cieco datacenter resta ancorato al run congelato `38320346965` (1.258 coppie) e non deve essere confuso con questa esecuzione successiva.

**PROSSIMO PASSO PRATICO:** acquisizione controllata di testi integrali accessibili (senza bypass paywall/robots, con difese SSRF), annotazione di un campione non selezionato sul caso datacenter, misure di falsi positivi e precisione; poi rifattorizzazione di moduli e documenti. Non interpretare test verdi del gate come prova che l'estrazione delle affermazioni sia stata realizzata.


## 18. Primo adattatore per testi sorgente (offline, non live)

Implementato `ingestion/authorized_source_text.py` con `tests/test_authorized_source_text.py`: da HTML ottenuto **esternamente con accesso autorizzato**, estrae passaggi testuali, esclude parti di navigazione/script, calcola hash SHA-256 e produce la mappa per il gate `ingestion/epistemic_evidence_gate.py`. Zero chiamate di rete. La flag `--authorized` è una dichiarazione dell'operatore, non un controllo automatico di licenze/robots. Non promettere acquisizione live dei corpi articolo né verifiche di claims: NON sono ancora state eseguite. Prossima implementazione: fetch HTTP con SSRF robusto (pinning IP, controlli redirect, robots/accesso, limiti dimensionali, nessun bypass paywall), poi corpus autorizzato e annotazione di coppie rappresentative. Riferimento canonico: `docs/EPISTEMIC_REVIEW_CONTRACT.md`.

Ultimo controllo prima di questo commit: `Ubik Core checks` `38321135701` success; `global-discovery-pilot` `38321098260` ancora in progress. Verificare i nuovi run prima di dichiarare test conclusi.


## 19. Prime card semantiche di scoperta — integrazione pilot (non produzione)

Decisione: procedere fino a **card di scoperta** senza fingere validazione epistemica. Creato `ingestion/semantic_discovery_cards.py`, test `tests/test_semantic_discovery_cards.py`. Consuma `semantic-pair-review-queue.json` e produce `semantic-card-previews.json` e `semantic-card-previews.md` nell'artefatto `semantic-topic-review` del workflow globale. Le card mostrano due titoli e URL originali, host editori, posizione nel ranking congelato, somiglianza numerica con avvertenza, domanda editoriale e stato `da_verificare`. Non generano affermazioni, non attestano lo stesso evento, non creano topic, non assegnano topic automaticamente e non pubblicano nella UI di produzione. Limite 24 card per pilot. Il codice si integra nel **workflow di acquisizione già esistente**, non richiede una nuova architettura di produzione.

**Non confondere:** `ingestion/global_cards.py` è la preview storica basata su similarità lessicale e titoli; `ingestion/semantic_discovery_cards.py` è la preview E5 sui vicini semantici. Entrambe sono source-grounded, ma nessuna è una card epistemica validata. La promozione richiede `epistemic_evidence_gate.py` più giudizio editoriale su testi originali. Le card restano nei workflow artifacts fino a revisione e approvazione UI.

**Prossima chat:** verificare run GitHub Actions successivo al commit `1188d7d`, scaricare `semantic-topic-review` e leggere `semantic-card-previews.md`. Se il workflow fallisce, correggere il problema senza dichiarare card generate. Poi lavorare su acquisizione autorizzata di corpi articolo e annotazione di claims. Non modificare `main` né moltiplicare i topic.


## 20. Approved HTTPS acquisition → claims → comparison worksheets (implemented, 2026-10-13)

Implemented: `ingestion/approved_https_fetch.py` (explicit publisher allowlist, affirmative rights/robots policy, robots.txt, HTTPS/TLS hostname validation with resolved-IP pinning, reject private DNS and redirects, strict size/content-type/timeouts); `ingestion/approved_claim_pipeline.py` (controlled fetch → offline article passage capture → hash-grounded sentence candidates); `ingestion/source_claim_candidates.py` (verbatim sentence candidates, NOT factual claims verified); `ingestion/source_claim_comparisons.py` (two-source editorial worksheet, defaults `insufficient_evidence`, NO automated contradiction/causality). Added mocked/synthetic tests `tests/test_approved_https_fetch.py`, `tests/test_approved_claim_pipeline.py`, `tests/test_source_claim_pipeline.py` and invoked these tests in global discovery workflow. All of this is in `develop/ubik-core`, not production.

**Critical limit:** No publisher has been preapproved; no unattended live full-article fetch has been executed; no genuine publisher claim comparison is validated. The global pilot still produces headline-based preview cards only. Do not misrepresent the new safe-fetch capability as permission to scrape arbitrary publishers. See canonical security and operating guide `docs/APPROVED_ACQUISITION_AND_CLAIMS.md`, and epistemic label contract `docs/EPISTEMIC_REVIEW_CONTRACT.md`. Confirm latest Actions run and tests before claiming successful execution.

**Next for future chat:** (1) inspect Actions after `2fc663b`, fix failing tests; (2) secure publisher-approved full-text sources (RSS syndication rights do not imply full-text rights), exercise two actual source bodies; (3) annotate and validate comparison of explicit claims, quantify errors; (4) only then generate evidence-grounded epistemic card previews and review UI integration. Never bypass publisher rights or invent verified relations.


## 21. Evidence review cards: bridge implemented, no false publication

Implemented `ingestion/evidence_review_cards.py` and `tests/test_evidence_review_cards.py`. This consumes **reviewer-annotated** pair relations plus URL-keyed full source texts and hashes, calls `epistemic_evidence_gate.validate`, rejects missing/fabricated source passages and emits an evidence card only if the source quote consistency gate passes. The resulting card explicitly states `editorial_review_required`, `relation_is_verified=false`, `claim_is_verified=false`, `automatic_publication=false`. The proposed contradiction or causal relation is still an unverified human annotation, not an accepted finding.

`ingestion/evidence_card_fixture.py` creates a **SYNTHETIC ONLY** demonstration, now uploaded by the global discovery pilot as `synthetic-evidence-review-card.json`. These example URLs and statements are fictional and are **never** real reporting. Distinguish this artifact from the live RSS/title-based `semantic-card-previews.json`. No real publisher article bodies have yet been processed through the new gate, and no factual contradictions have been established.

Full production-like chain now exists as separate opt-in components: `approved_https_fetch` → `authorized_source_text` → `source_claim_candidates` → `source_claim_comparisons` (worksheet, no automatic stance) → **human reviewer annotation** → `epistemic_evidence_gate` → `evidence_review_cards`. The manual annotation stage is intentional and cannot be silently skipped. Rights/robots approval and a reviewed network policy are required before live acquisition. See `docs/APPROVED_ACQUISITION_AND_CLAIMS.md`.


## 22. Empirical global pilot verified and unbiased review sampling (2026-10-13)

Global workflow run **38352639929** COMPLETED SUCCESSFULLY, both `discover` and `semantic-review`. Fresh snapshot: **330** RSS document hints, **1299** cross-publisher semantic title pairs, **60** heuristic review items, **24** unverified semantic preview cards, **1** proposed existing-topic association and **59** abstentions; **zero** automatically created topics. Synthetic evidence fixture reports **1** synthetic review card and **0** real publisher article bodies processed. All source safety, claim pipeline, evidence card and existing discovery unit tests executed successfully. Source: GitHub Actions run logs `https://github.com/nathanasso-code/Ubik/actions/runs/38352639929`.

Empirical example: Hurricane Simon/Tropical Storm Rachel titles from Guardian (five deaths) and Al Jazeera (two deaths) appear as a semantic pair (cosine 0.9433). This is **not a proven contradiction**: report times and count scope must be compared against full texts. Other candidate pairs: BBC/Guardian RJ Mitte titles (0.9932), BBC/Al Jazeera South African deputy police chief (0.9855), BBC/Al Jazeera French supermarket cyberattack (0.9443). These are headline-only observations, NOT factual validation.

Added `ingestion/semantic_empirical_audit.py` and `tests/test_semantic_empirical_audit.py`: seeded **uniform random sample of 30 frozen retrieved pairs** for blind human labeling, distinct from biased high/low queue. Next workflow writes `data/discovery/random-semantic-audit.json` in `semantic-topic-review` artifact. **No precision/recall estimate** before manual labels; retrieval-only random sample cannot estimate recall over all document pairs. Evaluate false-positive mechanisms and editorial utility. This is an empirical methodology milestone, not a claim-level validation result.

**Next:** inspect workflow after commit `ec574d5`, retrieve new random sample, annotate independently and compare time/agent/action/target/scope; obtain explicitly authorized article bodies and test source quote pipeline on at least two real publishers before promoting evidence cards. Keep `main` unchanged.
