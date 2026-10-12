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
