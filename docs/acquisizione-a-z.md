# Ubik dalla A alla Z: acquisizione, selezione, nodi (8 novembre 2026)

Questo documento descrive il sistema com'è oggi, dall'inizio alla fine, ed è il punto di partenza per chi riprende il
lavoro in una nuova conversazione. I documenti di dettaglio restano: `docs/daily-spec.md` (Matrici),
`docs/nodi-spec.md` (nodi), `docs/acquisizione-nodi.md` (diario delle prove, con tutte le misure), `docs/modello-dati.md`.

## 1. Che cosa fa Ubik

Ubik raccoglie e ordina le notizie e il dibattito su un tema. Ha due modalità, che condividono le fonti:

| Modalità | Domanda | Prodotto |
| --- | --- | --- |
| Attualità | Che cosa è successo questa settimana? | **Matrici**: gli articoli di testate diverse sullo stesso fatto, divisi in **card** (le fonti che riportano lo stesso fatto sostanziale); le card singole per i fatti con una sola fonte |
| Conoscenza | Su che cosa ci si divide, e chi ha ragione dove si può dire? | **Nodi**: una domanda, un testo di poche affermazioni, **catene** di **anelli** (ogni anello è una fonte che risponde a un'affermazione precisa dell'anello sopra), con citazioni verificate |

Un **Topic** (per ora Intelligenza artificiale, con quattro sotto-topic: regole, lavoro, data center ed energia, diritto
d'autore; ed Euromaidan come prova storica) è il perimetro. I nodi di oggi: `weight-space` (il rapporto del MIT sulla
lettura e scrittura dei pesi), `fair-use` (addestramento e diritto d'autore), `maidan-20-febbraio`, e `inverno-ia` (solo
prova di profondità).

## 2. Dove sta ogni cosa

| Dove | Che cosa |
| --- | --- |
| `nathanasso-code/Ubik` (pubblico) | Codice della pipeline delle Matrici (`ingestion/`), prompt delle Matrici (`prompts/`), documentazione (`docs/`) |
| `nathanasso-code/ubik-corpus` (privato) | Registri delle fonti (`registry/`), corpus dei testi (`corpus/`), strumenti (`tools/`), prompt dei nodi (`prompts/`), workflow (`.github/workflows/`), richieste di esecuzione (`runs/`), risultati (`reports/`) |
| Segreti di `ubik-corpus` (solo i nomi) | `OPENROUTER_API_KEY`, `BRAVE_API_KEY`, `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, `GNEWS_API_KEY`, `UBIK_GMAIL_*`, `COURTLISTENER_API_KEY` |
| Documento «Ubik — Acquisizione delle fonti» (Claude Docs) | La versione da leggere per la redazione |
| Esploratore (artefatto) | Le Matrici e i nodi visti come pagina |

Tutto gira sui server di GitHub (Actions): il contenitore di lavoro di Claude non raggiunge le API esterne. Un'esecuzione
a pagamento parte solo da un file `runs/<nome>.request` scritto e spinto nel repository, o a mano.

## 3. Le regole che valgono ovunque

- **Fonti nuove solo con l'approvazione della redazione.** Dal 7 novembre ogni gruppo proposto entra «in prova» con i
  suoi motivi, e la redazione toglie quello che non vuole. Le fonti in prova non bastano da sole a fare una Matrice.
- **robots.txt e riserva TDM rispettati**, sempre: un sito che vieta o rifiuta (403) non si aggira, si registra.
- **Seconde copie** (decise il 9 novembre, `tools/second_copy.py`):
  - *copia ad accesso aperto*: quando l'editore di un DOI rifiuta, si usa la copia indicata da OpenAlex
    (`best_oa_location`) o da Crossref, di solito un archivio istituzionale o un preprint, cioè un sito che quella copia la
    pubblica apposta. Nel record: dove si trova e se è la versione pubblicata o il preprint;
  - *copia d'archivio* (Internet Archive): solo per le pagine che non esistono più (404, 410, dominio inesistente), e solo se
    il sito originale, quando è ancora raggiungibile, non vieta i programmi in robots.txt e non ha la riserva TDM. Anche
    web.archive.org passa il controllo di robots.txt. Nel record: «copia d'archivio» con la data della copia;
  - mai per le pagine che rifiutano (403, 401, robots.txt, riserva TDM): per quelle Ubik può mostrare al lettore il link
    alla copia dell'Internet Archive, senza raccoglierla né citarla.
- **I testi integrali restano nel repository privato.** Si mostrano sintesi di Ubik e citazioni brevi: per la stampa al
  massimo una citazione di circa 150 caratteri per articolo, per gli altri testi entro 300 (`build_model.py`,
  `shown_quote`).
- **Una citazione si mostra solo se il codice la ritrova parola per parola nel testo raccolto.** Lo stesso vale per i
  giudizi del modello: contano solo se indicano una frase che il codice ritrova.
- **Brave**: non si conservano le liste dei risultati, solo la nostra selezione. Le pagine trovate solo da Brave vivono
  nella cartella temporanea dell'esecuzione (`scout-transient/`); se non vengono scelte si contano e basta; il registro
  dell'esecuzione, che le stampa, si cancella dopo la lettura
  (`gh api -X DELETE repos/nathanasso-code/ubik-corpus/actions/runs/<id>`). Le pagine scelte portano «trovata con Brave».
- **Costi**: tetto di 20 dollari per l'ambito IA sulle chiamate ai modelli; ogni esecuzione dichiara il suo budget.
- **Si conserva fin da ora ciò che non si ricostruisce a ritroso**: le decisioni editoriali con il loro motivo (scelte,
  scarti, proposte accettate o rifiutate) e le affermazioni con la loro provenienza. Sono la base per un giudice
  addestrato sui criteri di Ubik e per un archivio delle affermazioni.
- **Un solo elenco delle cose da fare**: la sezione 10 di questo documento. Le specifiche rimandano lì; un'idea nuova
  entra nell'elenco al suo posto o non entra, e si corregge l'elenco invece di scrivere documenti nuovi.

## 4. Il corpus: la raccolta continua

### 4.1 Registri

| File | Che cosa | Livello |
| --- | --- | --- |
| `ai.json`, `ai-regulation.json` | Testate e fonti approvate (67 e 46) | approvato |
| `ai-regulation-newsletters.json`, `ai-regulation-social.json` | Newsletter (casella Gmail di Ubik) e account social | approvato |
| `ai-voices.json` | Le 42 voci (persone) approvate il 4 novembre, con i loro canali | approvato |
| `ai-probation.json` | 65 fonti in prova: blog e autori dal bacino, testate dalla verifica della copertura, sette testate italiane, Terence Tao | prova |
| `research-ai-probation.json` | 16 raccoglitori di studi: cinque categorie di arXiv, NBER, riviste via OpenAlex, i 24 studiosi trovati dalle citazioni dei nodi | prova |
| `primary-ai-probation.json` | 15 fonti primarie: notiziari di aziende (sempre «parte in causa»), AI Security Institute, GOV.UK, l'avviso EUR-Lex della redazione, il Press corner della Commissione | prova |
| `gnews-ai.json` | Quattro ricerche GNews (IA ed energia, inglese e italiano) | prova |
| `telegram-probation.json` | 12 canali pubblici di Telegram, ucraini e russi; solo i post su Euromaidan e IA (10 novembre) | prova |
| `*-candidates.json`, `bacino-ia.json` | Candidati non ancora approvati, con la storia di come sono stati trovati | — |

### 4.2 Raccolta (`tools/collect.py`, workflow `collect.yml`, ogni 12 ore dal 10 novembre)

Per ogni fonte il raccoglitore legge il canale dichiarato: feed RSS o Atom, sitemap con filtro sui percorsi
(`sitemap_filter`, per i siti senza feed: Anthropic, Artificial Analysis), filtro di OpenAlex (`openalex`: una rivista
per ISSN o un elenco di autori; si conserva l'abstract), API di arXiv, ricerche GNews (finestra di 30 ore, fino a otto
pagine, aggregatori esclusi, la testata vera come origine). Per ogni voce nuova apre la pagina dell'editore se robots.txt
lo consente e non c'è la riserva TDM, estrae il testo (trafilatura, PDF con pypdf) e lo salva in `corpus/<ambito>/` con
origine, testata, livello, data e «trovata con». Al massimo 40 voci nuove per fonte a giro. Costo: zero, tranne
l'abbonamento GNews (49,99 euro al mese, circa 32 richieste al giorno su 1.000).

Corpus all'8 novembre: circa 7.700 testi in `ai`, 5.300 in `ai-regulation`, 1.270 abstract in `ai-research`, 600 pagine
citate in `cited`, 345 testi mirati per i nodi in `targeted`.

### 4.3 Le pagine citate (`tools/fetch_cited.py`, `coverage.yml`, ogni giorno)

Il dibattito legge una coda lunghissima di siti, ciascuno citato una o due volte, che nessun abbonamento copre. Ogni
giorno si raccolgono, con le stesse regole, le pagine citate da almeno due fonti del corpus, quelle condivise da
un'antenna (sotto) e le storie sull'IA in prima pagina su Hacker News. `tools/coverage.py` misura la copertura su quattro
insiemi di riferimento: le pagine citate da due fonti sono passate dal 7% al 71% nel corpus, i link delle antenne dal 22%
all'87%, Hacker News dal 7% al 40%.

### 4.4 Il bacino delle fonti (`tools/bacino.py`, `bacino.yml`, su richiesta)

Il bacino è l'anticamera del registro: siti e persone scoperti da qualsiasi strumento, ciascuno con la sua storia. Passi:
`seed` (voci, siti dei nodi, firme), `expand` (chi seguono le voci su Bluesky, i siti che citano), `channels` (robots.txt,
feed, quota di articoli sull'IA, riserva TDM), `clean` (doppioni, rumore, classe di canale), `resolve` (Brave per chi ha
solo Bluesky), `mastodon` (account e chi seguono), `antennas` (i link condivisi da voci e antenne, in
`reports/bacino/ia-antenne.json`), `cited` (gli autori degli studi che citano o sono citati dagli studi dei nodi, da
OpenAlex), `measure` (che cosa avrebbe portato un feed in due settimane). Le **antenne** sono 186 account Bluesky e 181
Mastodon seguiti da molte voci: non sono fonti, i loro link servono a scoprire pagine. Il bacino propone; la redazione
approva.

## 5. Le Matrici della settimana

`ubik-corpus/tools/select_ai_week.py` sceglie gli articoli della finestra (corpus `ai-regulation`, `ai`, `cited`),
toglie i doppioni e applica un prefiltro per codice sui termini dell'IA. Poi `Ubik/ingestion/ubik_daily5.py`, con
DeepSeek (`deepseek/deepseek-v4.1-flash-1017` su OpenRouter, ragionamento spento):

1. **nota** per articolo: pertinenza, tipo, evento (attore, azione, oggetto, data), sintesi e citazione, sotto-topic;
2. **raggruppamento** per sotto-topic in Matrici e card, con il motivo di ogni card separata;
3. **conferma del codice**: due articoli stanno insieme solo se date e parole di attore o oggetto lo provano; servono
   almeno due origini indipendenti, e almeno un articolo da una fonte approvata o primaria (una Matrice fatta solo di
   fonti in prova si scioglie);
4. **secondo giro** sulle card singole e fusione delle Matrici gemelle; controllo delle card;
5. **filtro del sotto-topic** e **testi** (titolo neutro, essenza, testi delle card) solo dalle sintesi.

Si lancia da `runs/daily.request` (`version=5`, `label`, `tiers`, `notes`). Costo: circa 0,7 dollari per 900 articoli,
1,3 per 1.400 (la settimana del 2 novembre con tutte le fonti: 42 Matrici invece di 27). Le note si riusano finché il
prompt non cambia.

## 6. I nodi: dalla domanda alle catene

Il lavoro su un nodo ha sei passi. I primi quattro sono automatici; gli ultimi due li fa oggi Claude in conversazione.

### 6.1 La scheda del nodo (`reports/nodi/<nodo>/scout.json`)

Scritta a mano una volta: la domanda, le **ancore** (i documenti d'origine), i **termini** con cui il caso circola (in
più lingue), le ricerche per GitHub e per la letteratura, i DOI, la voce di Wikipedia, sette **ricerche per le lacune**
(`gap_queries`: una per posizione senza fonti o replica mancante), le **date** del caso quando servono (`dates`) e le
fonti già note (`known`) per misurare.

### 6.2 Lo scout (`tools/scout.py discover`, `scout.yml`, da `runs/scout.request`)

Cerca i candidati per dodici vie, tutte gratuite tranne Brave (credito mensile gratuito, sette ricerche per nodo):

| Via | Che cosa porta |
| --- | --- |
| Casa (`home`) | Le ricerche del nodo sull'indice interno del corpus (`corpus_index.py`) |
| Corpus | Gli articoli del corpus che citano le ancore, e i link che citano (forte se citato da due fonti) |
| Antenne | I link condivisi da voci e antenne |
| Hacker News | Discussioni sulle ancore e link nei commenti |
| Bluesky | Link nei post sul caso (con accesso autenticato) |
| GitHub | Repository e issue che citano le ancore: le riproduzioni |
| OpenAlex, Semantic Scholar | Letteratura sul tema e chi cita i DOI |
| Wikipedia | I riferimenti delle voci sul tema (spento nella prova di profondità) |
| Brave | Le ricerche per le lacune |
| Web | Spento: Bing vieta l'uso automatico |
| Rimbalzo (`snowball`) | Apre i 40 candidati migliori e le ancore e raccoglie i link che citano; un link citato da due pagine è forte. Dall'8 novembre legge solo il corpo del testo e, per le ancore, anche le altre pagine dello stesso archivio |

Risultato: `reports/scout/<nodo>/candidates.json` (da 700 a 1.500 candidati per nodo, ciascuno con le vie che l'hanno
trovato), senza le pagine trovate solo da Brave. `scout.py bench` confronta con le fonti note.

### 6.3 Primo livello: il filtro per codice (`tools/rank_candidates.py`)

Senza aprire le pagine, da indirizzo, titolo, menzioni e voci: nomina il caso (frasi, coppie di parole come «fair use»,
parole distintive, traslitterazioni, plurali), è uno studio, un documento ufficiale, un repository; la data del caso
nell'indirizzo; trovato cercando il caso (Bluesky, Hacker News, casa) con un titolo. Toglie piattaforme e post social,
pagine di servizio, titoli da motore di ricerca. Ogni segnale ha un peso visibile nella classifica
(`reports/scout/<nodo>/rank.json`). Tiene circa un terzo dei candidati. Costo zero.

### 6.4 Secondo livello: il giudizio (`tools/judge_candidates.py`, `prompts/judge-node.txt`)

Gira nello stesso workflow dello scout, così vede anche le pagine trovate solo da Brave. Per i primi `k` della classifica
(400-500) apre la pagina, ne prende le prime 1.400 parole e chiede a DeepSeek: è pertinente? che tipo di pagina? è
derivata da un'altra? porta prove proprie, qualcosa di nuovo per le catene del nodo, argomenti contro, fonti primarie, un
autore competente? Ogni «sì» deve citare una frase che il codice ritrova nel testo. Il codice calcola il punteggio (prove
proprie 2,5, novità 2, argomenti contro 1, autore 1, fonti primarie 0,5, più il tipo; una pagina derivata perde 2,5).

Tre fasce: **contributo** (punteggio da 5), **copertura** (pertinente, da 3 a 5: non serve al nodo, serve alle Matrici e
alle card), **scarto**.

**Setaccio**: i link citati dalle pagine «contributo» (solo nel corpo del testo) diventano i candidati del giro
successivo, in ordine di quante pagine buone li citano, fino a 250 per giro. Si ferma quando un giro non trova nulla.

Risultato in `reports/scout/<nodo>/judge.json`; i testi letti non si conservano.

### 6.5 Terzo livello: le proposte (`tools/propose_links.py`, `prompts/propose-link.txt`)

Per i contributi, DeepSeek propone l'anello nel formato del nodo (catena, che cosa afferma, relazione, citazione); il
codice controlla che la citazione sia nel testo e la regola per la stampa. Le proposte vanno in
`reports/nodi/<nodo>/proposte.json`; il nodo non si tocca.

### 6.6 Raccolta e costruzione del nodo

Le pagine scelte vanno in `reports/scout/<nodo>/pick.json`; `scout.py fetch` le raccoglie nel corpus privato
(`corpus/targeted/<nodo>/`). Claude, in conversazione, legge i testi, decide gli anelli, scrive sintesi e relazioni,
verifica sui documenti primari (le sentenze, i paper) e aggiorna `reports/nodi/<nodo>/node.json`. `tools/build_model.py`
costruisce il modello che l'esploratore mostra, con la regola delle citazioni. Le segnalazioni della redazione entrano come
`segnalazione` in `corpus/targeted/<nodo>/`.

## 7. Quanto costa

| Voce | Costo | Cresce con |
| --- | --- | --- |
| Raccolta, pagine citate, bacino, scout, primo livello | Zero (Actions gratuite) | — |
| GNews | 49,99 euro al mese | Fisso |
| Brave | Accantonato il 13 novembre: niente più credito gratuito (5 dollari ogni 1.000 ricerche, con l'obbligo di citarlo) | — |
| Exa (motore principale dal 12 novembre) | Da verificare nel pannello: il listino dice 7 dollari ogni 1.000 ricerche con 10 risultati più 1 per ogni risultato oltre il decimo (17 con i nostri 20); il consumo osservato sembrava molto più basso. I risultati dall'11° al 20° portano circa il 30% dei contributi | Ricerche dei nodi |
| Tavily (secondo motore) | Gratuito fino a 1.000 ricerche al mese (tetto nostro 900), poi 8 dollari ogni 1.000 | Ricerche dei nodi |
| Aggiornamento settimanale dei nodi | Circa 0,17 dollari a nodo per giro (piano, giudizio, voci) più 20-25 ricerche; prima settimana 0,66 dollari per quattro nodi | Nodi attivi × giri |
| Voci dai social, autori, revisione dei canali | 2-6 centesimi a nodo; meno di un centesimo per il resto | Nodi e autori nuovi |
| Matrici | 0,7-1,3 dollari a settimana per Topic | Articoli della settimana (le note sono il grosso) |
| Giudizio | 0,13-0,41 dollari per nodo, due giri (circa 0,0007 dollari a pagina; il controllo preventivo ne stima 0,0015) | Candidati × nodi × giri |
| Proposte | Circa 0,02-0,03 dollari per nodo | Contributi |
| Costruzione del nodo | Lavoro di Claude in conversazione, non misurato in dollari | È il passo che non scala |
| Proposte di nodo dalle Matrici | Circa 2 centesimi a settimana (41 Matrici, 3 centesimi per due settimane) | Matrici |
| Riferimenti descritti dagli articoli | 0,3-0,5 dollari a settimana: lettura 0,28-0,43, conferma 0,06-0,09 | Articoli che nominano uno studio, un rapporto, un sondaggio |
| Scout dei riferimenti (link degli articoli, OpenAlex, arXiv) | Circa 6 centesimi a settimana (la conferma; le ricerche sono gratuite) | Riferimenti senza documento nel corpus |
| Originali delle riprese | Circa 2 centesimi a settimana | Attribuzioni ad altre testate |
| Bibliografia dei documenti trovati (OpenAlex) | Zero | — |
| Documenti su cui poggiano le fonti di un nodo | 3-10 centesimi per nodo (16-29 fonti lette) | Fonti del nodo |
| Segnalazioni | Circa 0,2 centesimi a testo | Testi segnalati |
| Telegram nello scout | Gratuito cercare; il giudizio dei post costava circa 0,15 dollari per nodo, ora entrano solo gli articoli linkati | Nodi nelle lingue dei canali |
| GitHub Actions (repository privato) | Budget di 10 dollari al mese oltre i minuti inclusi | Esecuzioni |

Sui grandi numeri: un Topic di otto nodi costa circa 2-3 dollari al primo passaggio di giudizio e proposte, poi pochi
centesimi a nodo per gli aggiornamenti se si giudicano solo i candidati nuovi; le Matrici crescono con gli articoli. Le
leve per contenere il costo: due giri di setaccio invece di tre, il prefiltro, il riuso delle note, il giudizio solo sul
nuovo, e più avanti un modello locale per la prima scrematura.

Il conto per settimana, dall'11 novembre (un Topic, due settimane misurate): note e Matrici 0,7-1,3 dollari; riferimenti
descritti, scout dei riferimenti, originali e proposte di nodo circa 0,4-0,6 in più. Le leve già individuate, da provare
dopo aver scelto che cosa tenere: chiedere i riferimenti descritti nella stessa chiamata della nota (una chiamata invece
di due per gli articoli che nominano uno studio: circa 0,3 dollari a settimana in meno, ma le note si rifanno una
volta); confermare in una sola chiamata tutti i candidati di un articolo (lo fa già la verifica dei riferimenti); un
prefiltro più stretto per i riferimenti (oggi si legge un articolo su due); il modello locale per le conferme, che sono
domande sì o no.

**Confronto dei motori** (13 novembre, Nord Stream, stesse ricerche; contati con gli identificativi dei risultati, senza
conservare le liste). Exa ha tra i suoi risultati 313 contributi del nodo, 201 che Tavily non trova; Tavily 176, 64 che
Exa non trova. Dei 166 contributi trovati con Brave prima del 12 novembre, Exa e Tavily rifacendo le stesse ricerche ne
ritrovano 105 (Exa 88, Tavily 67): circa 61 erano solo di Brave, ma sono già nel nodo. Decisione provvisoria di Claude:
Exa principale, Tavily dentro la quota gratuita, Brave accantonato.

**Proiezione** (13 novembre, stime dai costi misurati, da rifare a ogni tappa). Un nodo nuovo costa circa 1 dollaro di
modello più 120-150 ricerche Exa (0,5-2,5 dollari secondo il prezzo vero): 1,5-3,5 dollari. Prima fase, privata
(acquisizione e costruzione, circa 300 nodi, Matrici e card per alcuni mesi): circa 650-1.250 dollari in tutto, nodi
storici costruiti con un modello avanzato esclusi. Seconda fase (20 nodi nuovi al giorno, aggiornamento dei nodi attivi
finché portano contributi, acquisizione e Matrici continue): 1.700-3.500 dollari al mese con 10 topic, 2.000-4.500 con
100 (Matrici e card crescono con gli articoli, non con i topic: un articolo si legge una volta). Le leve: il prezzo di
Exa (10 risultati invece di 20), nodi nuovi più leggeri, nodi attivi solo finché rendono. Con 100 topic l'archivio esce
da git (server, database, archivio a oggetti) e la redazione diventa il collo di bottiglia. Ipotesi della redazione, non
decisa: abbonamento a 4,99 euro al mese, obiettivo minimo 1.000 abbonati (netti circa 3,7-3,8 euro l'uno dopo IVA e
commissioni: copre la fascia bassa della seconda fase); un piano annuale accanto.

## 8. Che cosa dicono le misure (8 novembre)

**Brave nel giudizio e setaccio** (tre nodi, 0,81 dollari). Le pagine trovate solo da Brave sono tra il 13% e il 29%
dei contributi del primo giro: Brave non è sostituibile. Il setaccio funziona: il secondo giro aggiunge 43, 8 e 9
contributi, il terzo 11, 6 e 0; tra un quinto e un terzo dei contributi arriva per riferimento. Rispetto alle scelte
fatte a mano: nel MIT 16 su 23 promosse; nel fair use e nel 20 febbraio solo 2 su 13. Le cause: il taglio della classifica
(CCIA era al 479° posto), l'accesso (CourtListener vieta i programmi: 131 pagine; perma.cc e doi.org rifiutano), la
severità sulla stampa, e la variabilità di Brave e Bluesky tra un giorno e l'altro.

**Rimisura dopo le correzioni** (8 novembre, sera; scout e giudizio nello stesso giro, `k=600`, due giri, 0,90 dollari,
circa due ore).

| | MIT | Fair use | 20 febbraio |
| --- | --- | --- | --- |
| Pagine giudicate al primo giro | 373 | 600 | 378 |
| Contributi, primo giro (di cui solo da Brave) | 94 (15) | 105 (14) | 16 (6) |
| Secondo giro del setaccio | +59 | +15 | +6 |
| Contributi in tutto (prima, con tre giri) | 153 (148) | 120 (66) | 22 (25) |
| Fascia copertura | 5 | 69 | 1 |
| Scelte a mano promosse (prima) | 16 su 23 (16) | 3 su 13 (2) | 2 su 13 (2) |
| Scelte a mano in copertura | 2 | 3 | 0 |
| Costo (prima) | 0,37 $ (0,39) | 0,41 $ (0,26) | 0,13 $ (0,16) |

Che cosa è cambiato. Nel fair use i contributi quasi raddoppiano, soprattutto grazie a CourtListener: 40 chiamate (il
limite per esecuzione, raggiunto), 35 contributi tra atti RECAP e PDF; restano 97 pagine di CourtListener oltre il limite,
vietate da robots.txt. CCIA ora è promossa (il taglio della classifica era la causa). Due giri del setaccio rendono quanto
tre giri il giorno prima. Il rimbalzo sull'archivio dell'ancora ha dato 3 pagine nel 20 febbraio, tutte scartate.

Dove si perdono ora le scelte a mano: non più nel giudizio ma a monte. Non diventano candidate 2 nel MIT, 4 nel fair use
(tre memorie amicus e la Texas Law Review) e 7 nel 20 febbraio (le fonti ucraine lb.ua, texty.org.ua, Radio Svoboda, e
openDemocracy, Nonzero, Econ Journal Watch, ICCT). Altre sono bloccate dal sito: doi.org e due testate ucraine (403, 429),
TorrentFreak (riserva TDM). Una sola scelta cade al primo livello (il blog di Stanford sulla memorizzazione, al 579° posto).

Contributi del primo giro trovati da una sola via: GitHub 31, Brave 15, Bluesky 14 nel MIT; Bluesky 36, Brave 14, pagine
citate dal corpus 14, Wikipedia 11 nel fair use; Brave 6 e Wikipedia 6 nel 20 febbraio. Semantic Scholar 2 in tutto,
OpenAlex 10, le antenne nessuno.

**Precisione dei contributi** (9 novembre, fair use, campione casuale letto a mano: 30 contributi e 15 pagine della fascia
copertura). Dei 30 contributi, 18 sono davvero utili al nodo, 9 marginali (procedure, il riparto dell'accordo Bartz, una
guida del 2023 sulla registrazione), 3 sono riscritture di siti aggregatori (briefly.co, anythingengineoptimization.com,
paktechstan.com) al posto dell'originale. Stima: dei 120 contributi, circa 70 utili. La fascia copertura non è rumore:
10 pagine su 15 sono utili come copertura. Difetti trovati:
- lo stesso documento giudicato in due modi: la sentenza Bartz nella copia dell'Authors Guild prende 9,5, la stessa su
  CourtListener 4,0;
- la sentenza di Monaco su GEMA, documento primario in tedesco, finisce in copertura senza criteri compilati: nel nodo c'è
  solo un commento di Taylor Wessing;
- una sintesi rovescia l'esito: per Kadrey contro Meta scrive «nega il fair use», mentre la sentenza dà ragione a Meta. Il
  codice verifica la frase citata, non la sintesi che il modello ne ricava.

**Lingue del nodo, prima prova** (9 novembre, 20 febbraio, ucraino e russo; 0,31 dollari, la traduzione 0,001). I
contributi passano da 22 a 45: 18 in ucraino, 8 in russo (comprese testate ucraine in russo), 19 in inglese; 27 dei 39 del
primo giro arrivano solo da Brave. Entrano fonti ucraine solide che prima mancavano: Ukrainska Pravda, Babel, Slidstvo.info,
Tyzhden, Ukrinform, Ukrainska Moderna (la risposta a Katchanovski), la nota delle Nazioni Unite sulle indagini, la sentenza
nel registro dei tribunali. Le scelte a mano promosse restano 2 su 13: lb.ua (2023), ICCT, Nonzero e openDemocracy ora
vengono trovate, ma solo da Brave e non passano; texty.org.ua e l'articolo scelto di Radio Svoboda restano introvati (Radio
Svoboda entra con un altro articolo). Due problemi: la tesi di Katchanovski entra moltiplicata dalle ristampe (rama.com.ua,
stena.ee, ruskline.ru, Global Research, Canadian Dimension) e da una copia pirata del libro (dokumen.pub, ora esclusa:
`registry/excluded-hosts.json`); entrano testate statali russe (Rossijskaja Gazeta, RIA). Le traduzioni sono corrette ma a
volte calcate dall'inglese («масові вбивства на Майдані» invece di «розстріли на Майдані»): si possono correggere nel file.

**Lingue del nodo, seconda prova** (9 novembre, 20 febbraio, con le traduzioni corrette a mano). Si è fermata per il
credito OpenRouter esaurito: 121 pagine giudicate, 147 rifiutate con HTTP 402 (0,13 dollari). I giudizi riusciti sono
uniti a quelli della prima prova. Le regole nuove sono applicate senza nuove chiamate (`judge_candidates.py reband`):
- **Contributi:** 48 in tutto, 3 nuovi (Lutsenko su patrioty.org.ua, Antydot, Butusov su Glavcom), 23 in cirillico.
- **Stessa voce:** la regola funziona. Nove testi della tesi di Katchanovski diventano «ripresa», tra cui Global
  Research due volte, Canadian Dimension due volte, ruskline.ru, stena.ee, l'intervento su Umoloda e Rossijskaja Gazeta.
  Restano contributi il libro e l'articolo migliore. La recensione critica di Oylupinar resta contributo, perché ha un
  altro autore.
- **Testate di Stato:** RIA e Rossijskaja Gazeta portano l'etichetta.
- **Scelte a mano:** promosse sempre 2 su 9, cioè il rapporto del Consiglio d'Europa e Hromadske. Gli articoli di Radio
  Svoboda, lb.ua e texty.org.ua non entrano nei candidati nemmeno con i termini corretti. Il limite resta a monte: le
  ricerche gratuite in ucraino non arrivano a quegli archivi.

Il giudice ora si ferma alla prima risposta 402, e una pagina fallita per errore del modello non conta come già vista.

**Nodo leggero, prima prova** (9 novembre, fair use, dai 15 contributi migliori del giudizio; `tools/light_node.py`,
risultato in `reports/nodi/fair-use/light.md`). Tre versioni, da 1,3 a 1,8 centesimi ciascuna. Nelle prime due il modello
riceveva i 15 testi insieme: ha ignorato cinque documenti primari, tra cui le sentenze Bartz e Getty, e nella seconda la
riga di stato sbagliava su Bartz. La terza lavora in due passi (prima un estratto per fonte, con la frase verificata,
poi la sintesi dagli estratti): 7 punti, 15 citazioni su 15 ritrovate, esiti corretti per Bartz (addestramento sui libri
comprati: fair use; biblioteca di copie piratate: no), Kadrey, Thomson Reuters contro Ross, Monaco e Getty. Rispetto al
nodo pieno coglie bene tre catene su cinque (l'addestramento in sé, la provenienza dei dati, il modello contiene le opere)
e in parte le altre due: manca la diluizione del mercato, che le prime due versioni avevano. Difetti: il codice verifica
che la frase esista, non che sostenga l'esito (per la biblioteca piratata la frase descrive la biblioteca, non la
decisione); i punti cambiano da un'esecuzione all'altra e possono perdere una controversia centrale.

**Quarto nodo d'attualità, leggero** (9 novembre: «I data center dell'IA danneggiano le comunità in cui vengono
costruiti?», dalle Matrici di due settimane; cinque sotto-domande: bollette, acqua, lavoro e tasse, trasparenza, voto e
proteste; lingue de, es, nl; `reports/nodi/data-center-comunita/light.md`). Ricerca e giudizio a `k=250`, un giro: 0,17
dollari, 59 contributi, quasi tutti documenti pubblici e studi (gli ordini esecutivi di Pennsylvania e Texas, il Congressional
Research Service, il gruppo di lavoro dello Stato di Washington, la commissione dell'Assemblea di Londra, lo studio di E3 sulle
tariffe, Good Jobs First, Brookings, il Laboratorio di Berkeley, lo studio della provincia di Noord-Holland sull'acqua, il
ministero tedesco dell'Economia); 7 copie dello stesso documento riconosciute; 3 copie d'archivio di pagine scomparse. Bozza:
1,7 centesimi, 6 punti, 15 citazioni su 15 ritrovate; i 2 punti del completamento con citazioni inventate sono stati
scartati dal codice. Tre punti reggono (benefici fiscali, posti di lavoro, bollette: le due parti verificate), tre sono da
rivedere (due «contesi» senza la parte contraria, uno «aperto» su un'affermazione di parte). Manca il voto, che resta
contesto più che punto del contendere. Totale del nodo: circa 0,19 dollari.

**Verifica degli scarti** (a campione). Sotto 5 si perde circa un contributo su dieci, quasi sempre articoli pertinenti
senza prove proprie: ora sono la fascia «copertura». Al primo livello si perdevano pagine pertinenti con titoli espliciti
(«Third Circuit affirms… rejects fair use») per termini troppo stretti, e le cronache datate 20 febbraio 2014: corretto
con le coppie di parole, i plurali, le date e la via di ricerca. Nei giri del setaccio molti link erano di servizio
(schema.org, pagine «chi siamo», pubblicità): ora si leggono solo i link del corpo del testo.

**Prova di profondità** (il primo inverno dell'IA, senza Wikipedia, 0,18 dollari). Venti fonti aperte scelte da
Wikipedia e altrove come lista d'oro.

| Esito | Fonti |
| --- | --- |
| Trovate e promosse | 2: la trascrizione del dibattito Lighthill, la recensione di McCarthy |
| Trovate, fascia copertura | 1: le risposte di Sutherland e altri al rapporto |
| Trovate, bloccate dal sito | 2: il video della BBC (robots.txt), Haigh su CACM (403) |
| Trovate, non lette | 1: il robot Freddy |
| Lo stesso documento a un altro indirizzo | 3: il rapporto ALPAC (mt-archive), Agar (archivio UCL), la pagina del dibattito BBC a Edimburgo |
| Restituita da Brave ma non scelta | 1: Funding a Revolution (National Research Council) |
| Non trovate | 10: storie divulgative e retrospettive (Turing Post due volte, Computerworld 2005, Hendler 2008, AI Expert Newsletter, Open Philanthropy), la storia dell'IA a Edimburgo, due saggi di Hutchins, il memorandum di Weaver, il documento originale dell'esperimento Georgetown-IBM |

In sostanza 9 su 20 raggiunte, 10 contando quella vista e persa. In più lo scout ha trovato 20 contributi che la lista
non ha: la testimonianza di un ricercatore presente a Edimburgo nel 1972-73, l'analisi del memo di Minsky e Papert del
1971, una tesi di Edimburgo sulla controversia delle reti neurali, Minsky su Web of Stories, il saggio di Hutchins del 1996
sull'ALPAC, la critica coeva di Michie. Trova bene i documenti primari; non trova la letteratura divulgativa e le fonti
citate solo nei PDF, perché il setaccio legge i link delle pagine web e non i riferimenti bibliografici. Il setaccio si è
fermato al secondo giro (90 pagine): i contributi buoni erano quasi tutti PDF.

## 9. Giudizio e indicazioni

- **Che cosa vale**: la raccolta allargata (GNews e le fonti in prova: 42 Matrici invece di 27), le pagine citate (la
  copertura del dibattito), Brave nello scout, il giudizio (costa poco e trova molto più della ricerca a mano), il
  setaccio a due giri.
- **Che cosa rende poco, da potare se serve semplicità**: Semantic Scholar (limiti continui, quasi nulla di unico), la
  via web (spenta), le antenne dentro lo scout (da zero a un candidato per nodo: valgono per la copertura, non per i
  nodi), la ricerca per parole chiave su OpenAlex, `resolve` (96 siti, 4 feed), il terzo giro del setaccio.
- **Per la profondità storica**: tenere accesa Wikipedia (è la mappa già fatta: 17 delle 20 fonti d'oro vengono da lì) e
  aggiungere al setaccio i riferimenti bibliografici degli studi, risolti con OpenAlex o Crossref (gratuiti), e il grafo
  delle citazioni degli studi promossi (chi citano e chi li cita).
- **Per l'attualità**: oltre a ciò che c'è, il valore aggiunto viene dalle citazioni interne alle fonti (pagine citate,
  antenne, setaccio), dalle segnalazioni della redazione e, più avanti, da una comunità. Rifare lo scout sul nodo ogni
  settimana, giudicando solo i candidati nuovi, è il modo economico di tenerlo aggiornato.
- **CourtListener attraverso l'API** (approvata l'8 novembre, `tools/courtlistener.py`, segreto `COURTLISTENER_API_KEY`).
  robots.txt chiude tutto il sito ai programmi non nominati (`User-agent: *`, `Disallow: /`, che alla lettera comprende
  anche l'API) e nello stesso file li manda all'API («If you would like to crawl CourtListener, please contact us. We also
  have an extensive REST API»). Gli indirizzi dell'API, usati con il token dell'account e nei suoi limiti, sono l'unica
  eccezione al controllo di robots.txt; tutto il resto, compresi i PDF su storage.courtlistener.com, resta controllato.
  Quando il giudizio o la raccolta mirata incontrano una pagina di docket con il numero della voce, o una sentenza, la
  sostituiscono con il documento RECAP (testo estratto o PDF) o con il testo della sentenza. Piano gratuito: 5 richieste al
  minuto, 50 l'ora, 125 al giorno; al massimo 40 chiamate per esecuzione, ci si ferma al primo rifiuto. Token verificato l'8
  novembre (risposta 200). Le seconde copie (accesso aperto, archivio) seguono le regole della sezione 3.

## 10. Da fare

L'elenco unico di Ubik: ciò che è fatto, in corso e da fare. Aggiornato il 13 novembre.

**Fatto di recente**

- 13 novembre: **Mastodon, strutturale** (`tools/mastodon.py`, `tools/mastodon_voices.py`, `registry/mastodon-istanze.json`,
  `registry/mastodon-canali.json`). Niente ricerca centrale e niente ricerca libera senza account: si usano le interfacce
  pubbliche (profili, feed RSS, hashtag, elenco degli account di un'istanza, contesto di un filo), con robots.txt e con
  la scelta degli utenti (un account `noindex` o non ricercabile resta fuori). Tre parti, automatiche: (1) istituzioni:
  gli account delle istanze governative (social.bund.de, social.overheid.nl), garantiti dall'istanza e quindi
  primari; attivi negli ultimi 90 giorni e con almeno 20 post: 81 in prova (Bundesgerichtshof, ministero del digitale,
  Bundesverwaltungsgericht, garante di Berlino, CBS, Logius…), 1.614 post alla prima raccolta, ogni giorno dopo;
  (2) autori: l'account Mastodon di un autore approvato, dalla biografia di Bluesky, da un ponte Bluesky-Mastodon o
  cercandolo per nome (stesse regole di Bluesky; i casi dubbi alla revisione del modello): Schrems, Koomey, Radsch;
  (3) voci per hashtag scelti dal modello dalla domanda del nodo (salvati nella scheda del nodo), letti su 12 istanze,
  con gli stessi filtri di Bluesky (seguito più basso: 10, 30 senza competenza dichiarata): prima prova 5 voci
  sull'uso dei contenuti e 6 sul fair use (Peter Suber, heise online…), 3 centesimi. Lo scout legge i post raccolti;
  nell'esploratore ogni voce dice la sua rete. Gira ogni giorno con siti e autori e ogni settimana con i nodi. Con un
  account Mastodon nostro si potrebbe usare anche la ricerca nei post che gli autori hanno reso ricercabili (pronta:
  parte quando esistono i segreti MASTODON_TOKEN e MASTODON_INSTANCE). Decisione della redazione, stesso giorno: le
  testate tra le voci contano come fonti (il giudice dice chi parla: persona, testata, istituzione; il post di una
  testata manda il suo articolo allo scout, strada `segnalati`, `reports/scout/NODO/segnalati.json`); tolta una voce
  fuori tema (i termini d'uso di X nel nodo sul fair use) e detto al giudice che un argomento vicino non basta.
- 13 novembre: **canali Telegram approvati in automatico** (`tools/telegram_channels.py`, `registry/telegram-canali.json`),
  istituzionali e non (decisione della redazione: su una guerra video, testimonianze e geolocalizzazioni stanno spesso
  solo lì; il rumore è alto, quindi soglie strette e etichette, non esclusioni). Candidati: i canali che i canali seguiti
  inoltrano o citano (letti a ogni raccolta e a ogni ricerca, `registry/telegram-candidati.json`), i link t.me delle
  pagine del corpus, i post giudicati contributo. Si esamina un canale citato da almeno 2 fonti distinte: anteprima
  pubblica (robots.txt e riserva TDM), almeno 1.000 iscritti e 10 post, poi una chiamata sul titolo, la descrizione e
  gli ultimi post (istituzione, testata, giornalista, analista, osint, testimone, aggregatore, propaganda, spam; di chi;
  Stato; se porta materiale verificabile): spam e aggregatori fuori, il resto «in prova» con le etichette. «Primario»:
  un'istituzione il cui canale è citato da un sito governativo; i post dei canali primari, osint e testimoni diventano
  candidati essi stessi (il giudice li legge; dei video il sistema legge solo il testo intorno). I canali approvati
  entrano nella raccolta ogni 12 ore e nella ricerca dei nodi. Prima Telegram cercava solo nel primo scout di un nodo:
  ora anche nei giri della catena e in quelli settimanali (Nord Stream, primo scout: 330 candidati, 9 contributi, tra
  cui il comunicato della Procura federale tedesca). Primo giro: 112 canali citati dai 12 seguiti, 14 sopra la soglia,
  12 in prova (ministero della Difesa russo, Comitato investigativo, amministrazione di Volgograd, polizia della regione
  di Kyiv, 1° corpo «Azov» della Guardia nazionale, Zakharova, Astra, Baza, Shot, Rybar, Milinfolive), 2 aggregatori
  anonimi esclusi; 0,7 centesimi. «Primario» solo quando l'istituzione garantisce il canale: un sito governativo lo cita,
  la descrizione nomina un dominio governativo, o il sito dell'istituzione rimanda al canale (non basta dirsi
  «ufficiale»; il link al registro di Roskomnadzor non conta): per ora la sola polizia di Kyiv. Squilibrio da seguire:
  i canali seguiti sono per un quarto russi di Stato, e inoltrano soprattutto canali russi. Da fare: voci da Telegram
  con visualizzazioni e reazioni, come per Bluesky.
- 13 novembre: **controllo dell'acquisizione automatica, tre difetti corretti**. (1) Lo scout non leggeva i feed dei
  siti e degli autori approvati (circa 14.000 voci, salvate una per riga, che la strada del corpus saltava): la raccolta
  funzionava ma nessuno la usava; ora le legge (fair use: voci dal corpus da 44 a 284, 17 dai feed; uso dei contenuti
  da 0 a 31). (2) Nei nodi avviati in automatico i termini sono frasi lunghe che non comparivano mai alla lettera: ora
  una frase di tre o più parole vale quando tutte le parole sono nel testo. (3) Il confronto con Fable cercava le sue
  affermazioni nei nostri documenti con le sole parole italiane (quelle di Wikipedia avevano le parole in più lingue):
  rifatto alla pari, le affermazioni di Fable coperte dal nodo passano da 53 a 70 su 90 (20 assenti; 17 solo sue,
  prima 32); su Wikipedia noi 69, Fable 52, almeno uno dei due 74 su 93. La decisione del BGH era nel nodo per intero
  (testo tedesco e traduzione inglese), la misura non la trovava. Le assenze vere: i primi mesi (2022-2023: procura
  svedese, Säpo, lettera all'ONU, accuse russe al Regno Unito), le udienze di Amburgo, le conseguenze (sanzioni UE,
  ricorsi di Nord Stream 2 AG, governo tedesco). Per queste: il piano della catena ha due doveri nuovi (coprire tutta la
  storia della questione, fase per fase; cercare il testo integrale dei documenti che il nodo ha solo come comunicato o
  riassunto) e lo scout una strada nuova, `atti`: i numeri di causa nei documenti del nodo, risolti nelle banche dati
  ufficiali (Corte di giustizia UE: EUR-Lex dal numero CELEX; tribunali federali tedeschi: rechtsinformationen.bund.de,
  spento perché il suo robots.txt rifiuta i programmi). Prova su Nord Stream con i doveri nuovi (un giro, solo Exa):
  24 contributi nuovi (il giro settimanale ne aveva dati 13), quasi tutti nelle lacune: la chiusura dell'indagine
  svedese, il rapporto di Nord Stream AG sui crateri, gli studi sismici, il voto ONU sulla bozza russa, la sentenza
  inglese sull'assicurazione, le risposte del governo tedesco al Bundestag, le testimonianze al processo di Amburgo
  (BKA, sommozzatore della Bundeswehr), le foto della marina danese.
  Voci dai social: una voce non può ripetere una posizione già tenuta; chi non dichiara una competenza entra con criteri
  più stretti (decisione della redazione: deve dimostrare di più): il post deve portare qualcosa di verificabile (un
  documento, cifre, date, nomi, un racconto di prima mano con dettagli) e avere un seguito almeno triplo (60);
  nell'esploratore è segnato «senza competenza dichiarata». Da fare:
  l'equilibrio delle voci (sui data center quasi tutte contrarie: il pubblico di Bluesky pende da una parte; cercare con
  i termini e gli attori dell'altra parte).
- 13 novembre: **confronto dei motori e proiezione dei costi** (sezione 7): Exa principale, Tavily nella quota gratuita,
  Brave accantonato; stima delle due fasi, anche con 100 topic.
- 13 novembre: **l'aggiornamento settimanale dei nodi d'attualità, senza mano** (`tools/weekly.py`,
  `.github/workflows/settimana.yml`, `registry/nodi-attivi.json`). Le ricerche che Claude lanciava nelle sessioni le
  lancia il sistema, con gli stessi strumenti. Per ogni nodo attivo (fair use, data center, uso dei contenuti, Nord
  Stream; i nodi storici restano fuori, si costruiscono meglio con un modello avanzato): la catena in modalità
  settimanale (il piano cerca prima ciò che è successo dall'ultimo giro, poi ciò che è ancora scarno; Exa e Tavily nei
  tetti mensili; si ferma quando un giro porta meno di 5 contributi), le voci dai social, l'archivio delle pagine buone.
  Poi una volta: siti e autori approvati per criterio, canali dei nuovi autori, revisione dei canali quasi trovati fatta
  dal modello come la facevo io (sì: seguito; no: scartato; incerto: resta per Claude, 8 alla volta), feed dei nuovi
  siti. Regola nuova sugli autori: un controllo per autore approvato, ancora vivo e attivo? «no» lo rende «storico»,
  tenuto ma non seguito (Lighthill). Le voci dai social ricompongono i fili: un post seguito da risposte dello stesso
  autore diventa un testo solo, e i filtri si applicano al filo intero. Spesa: prima di partire si confronta il massimo
  possibile della settimana con un tetto (3 $; oggi al più 2,6 $ per quattro nodi a due giri); se non ci sta, resta fuori
  il nodo aggiornato più di recente. Il calendario (sabato) parte solo con `automatico: true` nel registro, che spetta
  alla redazione accendere: finora le esecuzioni a pagamento partivano solo da una richiesta. Le voci dai social sono
  nell'esploratore, sezione separata da resoconti e documenti; entrano anche i due nodi sperimentali (uso dei contenuti,
  Nord Stream, quest'ultimo come «banco di prova»).
  Prima settimana (13 novembre, a mano, un giro per nodo, solo Exa perché Tavily è quasi al tetto di novembre):
  contributi nuovi 36 fair use, 46 data center, 37 uso dei contenuti, 13 Nord Stream; voci dai social 11, 32, 10, 4,
  di cui 37 su 57 sono fili di più post; 68 siti approvati; Lighthill passato a «storico»; costo circa 0,66 $. La
  revisione dei canali fatta dal modello, provata sulle 18 voci già riviste da Claude: 16 uguali, 2 «incerte» (restano
  a Claude), nessun canale scartato da Claude accettato dal modello. La prima esecuzione aveva perso tutto al
  salvataggio (una cartella mancante): corretto, e le ricerche perse aggiunte al contatore dei motori. Le voci ora si
  sommano di settimana in settimana. Da fare: rifare la bozza leggera dei nodi quando la settimana porta molti
  contributi (oggi i contributi entrano nell'archivio e nel giudizio, non nel testo del nodo); accendere il calendario.
- 12-13 novembre: **un nodo scelto dalle Matrici e avviato senza intervento** (`tools/node_pick.py`, `nodepick` in
  `runs/week-refs.request`): per le prime 10 storie della graduatoria che non sono già nodi, il modello giudica se
  dietro l'evento c'è un dibattito che i documenti possono decidere, e ne scrive la domanda a quel livello; si sceglie
  profondità × punteggio. Scelta: i termini di Meta sull'uso dei contenuti per l'IA, riportati alla domanda sulla
  liceità dell'addestramento senza consenso (GDPR, autorità, tribunali). Domanda, sotto-domande, lingue e prime
  ricerche scritte dal modello; scout senza Wikipedia, catena con il solo Tavily: 51, poi 207 contributi in tre giri;
  bozza leggera su fonti primarie (EDPB, noyb, DPC, ANPD, tribunale tedesco).
- 13 novembre: **le pagine e i siti raggiunti dalle ricerche si tengono** (`tools/archive_node.py`, `tools/sites.py`,
  `.github/workflows/sites.yml`). Ogni pagina giudicata contributo o copertura è archiviata con il testo (recuperate
  1.273 pagine degli otto nodi, 54 non più leggibili). Approvazione automatica dei siti (criterio della redazione:
  almeno un fatto nuovo verificato per un nodo; rimozione più avanti, un sito rimosso non torna): 628 approvati, 92
  candidati; 372 con un feed, 122 con la sola sitemap. Le voci dei feed (11.976 alla prima raccolta, poi ogni giorno)
  vanno nell'indice del corpus che lo scout interroga per primo; nel giornale entrano con un criterio rigido e
  provvisorio (sito con almeno due fatti verificati, termine dell'IA nel titolo, al più 40 a settimana), mai escluse
  per sempre. Exa e Tavily al posto di Brave; tetti mensili 3.000 e 900.
- 13 novembre: **autori approvati in automatico e i loro canali** (`tools/authors.py`, `tools/author_channels.py`).
  Criterio stretto e modificabile: una persona (nome e cognome) con almeno 2 pagine che portano un fatto nuovo
  verificato, su 2 nodi o in 3 pagine, entra «in prova» (23 al primo giro); istituzioni e redazioni passano dai siti.
  Canali cercati da soli: OpenAlex per gli studiosi, Bluesky (cognome nel nome del profilo, ente nella biografia per i
  nomi comuni), pagine d'autore con feed, Substack con il cognome nell'indirizzo (una ricerca Tavily per autore): 17
  canali seguiti in automatico. Quello che serve una mano (newsletter solo email, pagine senza feed) va in
  `reports/fonti/autori-da-aggiungere.md` con il link esatto (3 voci). X e LinkedIn annotati, non chiesti: non li
  possiamo leggere. Da rivedere: autori storici (Lighthill) e qualche canale vero perso per prudenza (Schrems su
  Bluesky).
- 13 novembre: **canali quasi trovati rivisti a mano** (`reports/fonti/canali-da-rivedere.md`, 8 alla volta, da Claude
  nelle sessioni: accettati Schrems, Atkinson, Michal; scartati gli omonimi) e **voci dai social da qualsiasi account**
  (`tools/social_voices.py`, `voci=NODO` in `runs/sites.request`): ricerche brevi su Bluesky (termini del nodo, ricerche
  della catena tagliate a quattro parole, altre lingue), poi quattro filtri: almeno 25 parole proprie (un post ne tiene
  circa 50), seguito di almeno 20 (mi piace + 2×condivisioni + 2×citazioni), account con nome, biografia, 6 mesi, 50 post,
  100 follower e follower almeno metà dei seguiti, e il giudice (aggiunge una posizione, un argomento o una competenza?).
  Primo giro utile: Nord Stream 641 post, 5 voci (CORRECTIV, Brian Finucane di Crisis Group, David Puente di Open, Notes
  from Poland); nodo delle Matrici 476 post, 11 voci (Johnny Ryan di ICCL, Abeba Birhane, Nitasha Tiku del Washington
  Post, Simon McGarr, Nieman Lab); 6 centesimi. Per i post degli autori approvati il seguito si misura sulla media
  dell'autore. Fili di post e voci nell'esploratore: fatti (sopra).
- 12 novembre: **confronto con Wikipedia** (`tools/wiki_bench.py`, `bench=NODO` in `runs/week-refs.request`). Nodo
  nuovo sul sabotaggio Nord Stream costruito da zero, senza Wikipedia, senza ancore scelte a mano; solo alla fine letti i
  riferimenti delle voci in cinque lingue (en, it, de, sv, da: 429 distinti). Noi: 197 documenti, 20 in comune per
  indirizzo o titolo, 45 testate in comune. Wikipedia ha molta più stampa (401 contro 163) e le inchieste che hanno
  aperto la pista ucraina (Zeit, WSJ, Spiegel), che noi troviamo ma non possiamo leggere (robots.txt, 403), più i
  documenti dell'ONU, della NATO e del Bundestag. Noi abbiamo gli studi (18 contro 2: sismica, metano, infrasuoni) e i
  comunicati di chiusura delle indagini svedese e danese del 2024, che le voci non linkano. Costo circa 1,6 dollari
  (204 ricerche Brave, di cui 85 sprecate da un giro fallito). Limite del confronto: conta i documenti, non le risposte.
  Poi il **confronto per risposte** (`tools/wiki_claims.py`, `claims=NODO`; 15 centesimi): delle 93 affermazioni delle
  voci inglese, tedesca e italiana, i nostri documenti ne sostengono 35, in parte 18, ne contraddicono 1, non ne
  coprono 39 (stima per eccesso: la ricerca dei passaggi tra otto lingue manca ancora alcune cose che abbiamo).
  Mancano soprattutto le inchieste giornalistiche sulle tesi (navi russe e americane, Červins'kyj, CIA, Hersh dopo il
  2023), le prese di posizione istituzionali (NATO, ONU, Putin) e le conseguenze (riparazioni, forza maggiore).
  Al contrario, 59 delle nostre 89 scoperte verificate non sono nelle voci: 20 da studi, 13 da analisi, 21 da stampa.
  Lacune viste dal nodo da solo (`tools/node_gaps.py`: attori senza voce, affermazioni senza fonte propria,
  sotto-domande povere; 38 lacune, 76 ricerche): 31 contributi in più, ma copertura delle stesse 93 affermazioni
  invariata (50 contro 53: dentro il rumore della misura, che con più documenti in gara cambia i passaggi scelti).
  Terzo termine, il dossier di Fable (modello avanzato con ricerca, stesso prompt di domande;
  `tools/text_bench.py`): copre 48 affermazioni di Wikipedia contro le nostre 50, insieme 66 su 93; delle sue 90
  affermazioni noi ne copriamo 40, Wikipedia 33, 39 sono solo sue (soprattutto il processo di Amburgo e la parte
  giudiziaria); dei suoi 97 link, 7 sono anche nostri e 8 di Wikipedia. Tre strade quasi indipendenti.
  Correzione: i confronti «a affermazioni fisse» del mattino riestraevano l'elenco (il percorso del file era tagliato
  nel comando); i numeri dentro lo stesso giro restano validi, quelli tra giri no. Diagnosi delle fonti di Fable: 90
  delle sue 97 non erano mai arrivate tra i nostri candidati (61 da siti mai visti). Da qui la **ricerca a catena per
  nomi e numeri** (`tools/entity_rounds.py`, `runs/catena.request`): a ogni giro il modello legge i contributi e scrive
  le ricerche successive (persone, tribunali, numeri di causa, atti, nella lingua dei documenti); scout su Brave e web,
  giudizio delle sole pagine nuove, stop sotto 5 contributi nuovi. Nord Stream, quattro giri da 30 ricerche: contributi
  da 120 a 212 (13, 30, 30, 19 a giro; non ancora a saturazione), circa 1,2 dollari. Sulle stesse 93 affermazioni
  (davvero fisse): copertura da 53 a 62; Fable 45; insieme 69 su 93. Delle 90 di Fable ne copriamo 46 (prima 40).
  Ancora mia la partenza del nodo (domanda, sotto-domande, primo piano di ricerca) e gli esempi nelle istruzioni del
  giro: da rendere neutri e automatici prima di una prova pulita.
  Brave esaurito (402) il 12 novembre: 10 dollari in due giorni, quasi tutti per un errore (a ogni giro si aggiungevano
  le traduzioni dei vecchi piani, circa 280 ricerche in più). Corretto (`SCOUT_OWN_GAPS`, `SCOUT_OUTLETS`), e un
  contatore mensile con tetto per motore (`data/search-usage.json`). Motori nuovi: **Exa** (ricerca per significato) e
  **Tavily**, scelti con `engines=` nella richiesta della catena, anche insieme. Confronto sulle stesse 118 ricerche:
  contributi nuovi Exa 101 (77 solo suoi), Tavily 64 (40), in comune 24; ritrovati dei 212 già nel nodo: 78 e 61.
  Catena migliorata (istruzioni neutre, metà delle ricerche alle sotto-domande povere, riprese delle pagine non
  leggibili): 454 contributi, conseguenze da 40 a 67, saturazione al terzo giro. Copertura delle 93 affermazioni: 65
  dopo Exa e Tavily, 64 dopo la catena (la misura perde precisione con quasi 600 documenti: dà per assenti cose che il
  nodo ha, come le chiusure delle indagini svedese e danese); Fable 44; insieme 72. Delle 90 di Fable ne copriamo 50.
  **Misura più precisa** (`tools/wiki_claims.py`): parole pesate per rarità, copie offerte una volta, 16 passaggi
  letti prima di dire «assente», campione di 150 scoperte per la direzione inversa; e il **richiamo della misura**: 40
  frasi che sappiamo nel nodo ritrovate 40 su 40 (prova facile: frasi originali, non parafrasi). Con la misura nuova,
  stesse 93 affermazioni: noi 68 (73%), Fable 51, insieme 74 (80%); delle 90 di Fable noi 53, Wikipedia 35, 32 solo sue.
  I numeri delle misure precedenti non si confrontano con questi (la misura nuova alza tutti).
- 11 novembre: **i link dentro le fonti e la ricerca web come ultima strada.** Il registro teneva solo i link del
  riassunto del feed: metà degli articoli recenti, e tutte le pagine prese dalle citazioni, ne erano senza. Ora ogni
  pagina scaricata tiene i link del testo con le parole su cui stanno (`tools/body_links.py`), e un riferimento descritto
  prova prima il link che gli corrisponde (autore, ente, titolo, cifre nelle parole o nell'indirizzo), qualunque sito sia.
  Ultima strada, solo con indizi forti (chi l'ha pubblicato più un titolo o una cifra): una ricerca Brave, di cui si
  tiene solo il documento scelto (`web=N` nella richiesta). Prova su data center e fair use, fonti rilette: proposte da
  20 a 92 e da 32 a 93; 102 ricerche web (circa mezzo centesimo l'una) hanno trovato il documento in 70 casi. Restano
  errori da decidere: pagine che riassumono l'originale prese per l'originale (il sondaggio NBC, alcuni articoli di
  giornale) e lo stesso documento proposto per più riferimenti.
- 11 novembre: **sentenze citate e riferimenti di passaggio.** Le sentenze citate dalle fonti si cercano anche in
  CourtListener (per numero di citazione, altrimenti per nome delle parti) e, trovate, si leggono per intero: prima
  passavano solo dagli indici accademici, che non le contengono (Google v. Oracle, citata da due fonti del fair use, non
  era stata trovata; 29 sentenze su 34 «non trovate»). Nella stessa chiamata che conferma il documento, il modello dice
  se la fonte lo usa sulla questione del nodo o lo nomina di passaggio (esempio, sfondo, altro tema): quelli di passaggio
  restano registrati ma non diventano proposte. La redazione: un articolo divulgativo non si esclude in quanto tale;
  si esclude ciò che è fuori tema. Nella nota catalogata, `natura`: primaria, secondaria o mista (lettura del modello,
  non verificabile nel testo).
- 11 novembre: **atti scelti dai fascicoli delle cause** (`tools/dockets.py`, `dockets=NODO` in
  `runs/week-refs.request`): per ogni fascicolo citato nel nodo, una ricerca RECAP per tipo d'atto (pareri e sentenze,
  ordinanze, dichiarazioni e perizie di esperti, trascrizioni, memorie di terzi, citazioni, giudizio sommario); tenuti
  solo i testi di almeno 80 parole che non sono atti di procedura (sigilli, ammissioni, proroghe, cause collegate...).
  Fair use, due fascicoli: 51 chiamate, 37 documenti, 13 sostanziali (il parere sulla deposizione, le dichiarazioni di
  Feamster, Waehrer, Malhotra, Gratz, memorie e risposte alle citazioni). Gratis, ma lento: una chiamata ogni 12,5
  secondi, 125 al giorno. Solo cause americane; nell'esploratore, pagina del nodo, «Atti delle cause del nodo».
- 11 novembre: **graduatoria delle storie candidate a nodo** (`tools/node_ranking.py`, `mode=graduatoria` in
  `runs/matrix-nodes.request`): le Matrici delle settimane raggruppate in 55 storie, ciascuna misurata gratis
  (persistenza, testate indipendenti tolte le riprese, documenti, voci, lingue, divergenza) e, per le prime 15, giudicata
  dal modello (posta in gioco, valore aggiunto di un nodo; 0,6 centesimi). Pesi modificabili nel file. Nell'esploratore,
  pagina del Topic, con la decisione provvisoria di Claude per le 11 che non sono già un nodo: aprire al livello 1 le
  regole sull'IA negli Stati Uniti dopo le midterm, le conclusioni Szpunar sugli editori, l'opt-out dall'addestramento
  (con dentro il caso dei termini di Meta), i licenziamenti attribuiti all'IA (Microsoft, Canva); non ora le altre.
- 11 novembre: **schede discordi**: 14, di due tipi. Strutturale (11): il nodo nomina chi parla (l'autore, l'ente, la
  parte), il feed chi pubblica; ora la scheda ha `autore` e `testata` distinti, e le date diverse di un giorno o meno
  precise e le sezioni della stessa testata non contano come discordanze. Descrizioni diverse dello stesso autore (5):
  corrette con `tools/schede.py`. Restano 0. La nota catalogata è adottata dalle settimane dal 9 novembre.
- 11 novembre: **newsletter nei riferimenti descritti**: tutte quelle della settimana, anche fuori dalla selezione,
  lette più a fondo. Rendono poco: 26 newsletter nelle due settimane, 23 riferimenti, uno trovato; i testi raccolti
  dalla casella non sono tagliati, ma molte sono anteprime brevi (mediana 380 parole, sette su 32 sono di Politico).
- 11 novembre: **audizioni** (`tools/hearings.py`): trascrizioni e testimonianze da GovInfo per i riferimenti ad
  audizioni del Congresso; salta finché manca la chiave gratuita (api.data.gov, segreto `GOVINFO_API_KEY`). Pochi casi
  nelle due settimane (16 riferimenti che nominano commissioni o audizioni, non tutti audizioni).
- 11 novembre: **nota catalogata** (in prova, `NOTE_EXTRA=1`, `prompts/daily-v5/nota-extra.txt`): nella stessa chiamata
  della nota, i riferimenti descritti, le cifre chiave, i nomi di persone e organizzazioni e le testate a cui l'articolo
  attribuisce la notizia, ciascuno con il segno «nel testo» messo dal codice. Due prove su 50 articoli della settimana
  del 2 novembre (11 centesimi in tutto): la versione estesa costava il 70% in più della nota; quella asciutta il 31%
  (0,02 centesimi ad articolo, circa 0,30 dollari a settimana), con cifre ritrovate nel testo 124 su 134, nomi 364 su
  367, testate 30 su 31, riferimenti 37 contro i 46 della lettura separata. Sostituisce la lettura separata dei
  riferimenti (circa 0,43 dollari a settimana): il saldo è un piccolo risparmio, con cifre, nomi e testate in più per ogni
  articolo. `tools/week_refs.py` prende i riferimenti dalla nota quando ci sono. Da adottare per le settimane nuove
  (non si rifanno le vecchie): si lancia con `nota-ricca` nella richiesta del giornale.
- 11 novembre, notte: **altre strade verso le fonti**, ciascuna provata su una settimana o su due nodi.
  - **Originali delle riprese** (`tools/originals.py`): un articolo che attribuisce la storia a un'altra testata
    («secondo Bloomberg», «laut The Verge»), l'originale cercato tra le pagine di quella testata nei quattro giorni
    prima, confermato dal modello. Settimana del 2 novembre: 273 attribuzioni, 79 con candidati, 22 originali trovati (anche
    tra lingue: un articolo tedesco che riprende The Verge, uno italiano la BBC), 2 centesimi; nell'esploratore
    «Riprende:», e 7 Matrici dicono quante loro fonti riprendono un'altra fonte della stessa Matrice. Gli originali che
    mancano sono soprattutto di Bloomberg, New York Times, Reuters, Wall Street Journal, Financial Times.
  - **Documenti su cui poggiano le fonti dei nodi** (`tools/node_refs.py`). Fair use: 143 documenti
    descritti dalle sue fonti, 8 già nel nodo, 17 documenti nuovi trovati e confermati (sentenze e atti delle cause, amicus di EFF e
    Wikimedia, i paper di Creative Commons e Open Future); 20 febbraio: 92 descritti, 23 già nel nodo (un buon controllo
    del nodo), 4 trovati (tre versioni accademiche di Katchanovski e un lavoro su Odesa). 13 centesimi per i tre nodi. Le
    proposte sono nella pagina del nodo, con la decisione provvisoria di Claude (10 da far entrare, 11 da lasciare fuori).
    Poi altri tre nodi, leggendo prima le fonti senza testo nel corpus (restano in `corpus/targeted/NODO/fonti/`): data
    center 16 documenti nuovi (i due rapporti del Lawrence Berkeley National Laboratory, l'atlante del Dipartimento
    dell'Energia, i sondaggi Gallup e Heatmap, il rapporto E3, il tracker dei referendum, il white paper di Koomey
    sull'acqua), spazio dei pesi 4 (i log degli autori, uno studio su arXiv), coinvolgimento americano 2 fuori tema. In
    tutto 43 decisioni provvisorie di Claude (21 da far entrare, 22 da lasciare fuori), circa 0,35 dollari.
  - **La catena intera** per una settimana con una richiesta (`mode=tutto`): sulla settimana del 26 ottobre, 7 centesimi
    (i riferimenti erano già letti): 44 documenti in più dallo scout dei riferimenti, 5 originali, 8 lavori di sfondo; gli
    studi e documenti discussi passano da 26 a 71, quelli nelle Matrici da 4 a 8.
  - **Bibliografia dei documenti trovati** (`tools/biblio.py`, OpenAlex, gratuito): settimana del 2 novembre, 75
    documenti, 28 in OpenAlex, 746 riferimenti, 32 lavori citati da almeno due documenti (co-citati: agenti, rischi,
    benchmark), 19 documenti con citanti recenti. Da decidere come usarla: le co-citazioni come fonti di sfondo dei nodi,
    i citanti come repliche.
  - **Istituzioni e siti citati dalle fonti** (`reports/fonti/istituzioni-candidate.md`): i siti dei documenti
    confermati non ancora nei registri e le istituzioni nominate da almeno tre testate (Goldman Sachs, Gartner, Apollo,
    McKinsey, Wood Mackenzie, Öko-Institut, Tech Oversight Project…). Nessuna fonte aggiunta: l'elenco va alla redazione,
    con il bilancio delle fonti in prova del 21 novembre.
- 10 novembre: **segnalazioni** (`tools/segnalazione.py`, workflow `segnalazione.yml`: un testo in
  `runs/segnalazioni/`). Il testo non diventa una fonte (se ne tiene l'impronta): il modello elenca i riferimenti che
  descrive, il codice li cerca nell'indice del corpus e dice dove sono usati, poi in OpenAlex e arXiv. «Trovato» solo con
  un segno forte (cifra, titolo, nome inventato), altrimenti «possibile». Prima prova (un post su Facebook): 3 trovati, 4
  possibili, 0,2 centesimi; l'«epistemia» (Quattrociocchi e altri, arXiv 2512.19466) non arriva: serve lo scout. Il cuore
  (`analyze`) è separato dall'ingresso, per il riquadro dell'esploratore e poi del sito.
- 10 novembre: **studi discussi** (gratuito, nel modello): uno studio del corpus della ricerca, o una pagina di studio tra
  le pagine citate, linkato, citato per numero arXiv o per titolo dagli articoli, newsletter, post e canali della
  settimana; nell'esploratore per settimana e nelle Matrici che lo citano. Resa: 8 e 23 studi nelle due settimane, quasi
  tutti con una sola fonte e fuori dalle Matrici. Gli articoli citano gli studi descrivendoli più che linkandoli: da qui
  i **riferimenti descritti** (`tools/week_refs.py`, workflow `week-refs.yml`), un passo a parte per non toccare le note
  e le Matrici già fatte. Si leggono solo gli articoli che nominano uno studio, un rapporto, un sondaggio (417 e 721
  nelle due settimane); il modello elenca i riferimenti (814 e 1.311), il codice cerca il documento tra gli studi e le
  fonti primarie del corpus (non tra gli altri articoli, che lo riprendono), un secondo passo del modello conferma che
  il candidato è proprio quel documento. Senza la conferma, la gran parte dei «trovati» erano pagine con la stessa cifra o
  lo stesso benchmark. Risultato: 33 e 57 documenti confermati; gli studi discussi passano da 8 e 23 a 26 e 55, quelli
  nelle Matrici da 2 a 4 e 7 (le conclusioni dell'avvocato generale della Corte di giustizia, citate da cinque fonti; la
  citazione dei quotidiani contro OpenAI). Costo: 0,71 dollari per leggere, 0,15 per confermare, più 0,5 persi in un
  primo giro fermato prima di salvare (corretto: ora si salva prima). D'ora in poi, circa 0,3-0,5 dollari a settimana.
  Restano «solo riprese» i riferimenti il cui documento non è nel corpus. Lo **scout dei riferimenti**
  (`tools/ref_scout.py`, workflow `ref-scout.yml`) li cerca dal gratuito al più caro: i link dell'articolo che li
  descrive, poi OpenAlex e arXiv per studi e benchmark; il modello conferma il candidato. Prova sulla settimana del 2
  novembre: 528 riferimenti presi in esame, 304 senza alcun candidato, 224 confermati o respinti, 43 trovati (34 dai link
  degli articoli, 9 da OpenAlex), 6 centesimi. Il terzo passo, Brave per i rapporti senza titolo né link degli
  articoli nelle Matrici, è da decidere dopo il bilancio di Brave del 21 novembre.
- 10 novembre: **dalle Matrici ai nodi** (`tools/matrix_nodes.py`, workflow `matrix-nodes.yml`, su richiesta). Una
  chiamata per Matrice (almeno tre pezzi da due testate) chiede se le fonti si dividono su qualcosa che un nodo
  deciderebbe o mapperebbe; il codice tiene un lato solo se le sue citazioni sono quelle verificate dei pezzi. Prime due
  settimane: 41 Matrici lette, 3 centesimi, 17 divergenze, raggruppate per domanda in 15; 6 proposte di nodo (forza 4-5,
  non già un nodo), con la decisione provvisoria di Claude nell'esploratore (aprire il nodo o no): un punto per il nodo
  dei data center (i conti discordi delle misure locali alle midterm), un nodo unico sui licenziamenti attribuiti all'IA
  (Proton, Microsoft, Canva), un nodo sull'opt-out dall'addestramento (il token, robots.txt, il codice dell'UE); no al
  rinvio dei termini di Meta. Le altre divergenze restano sulla loro Matrice (spesso cifre riportate in modo diverso:
  utili anche a correggere le card).
- 10 novembre: **un documento, un pezzo** (primo passo del formato comune). Il modello unisce le copie dello stesso
  documento a indirizzi diversi (14: stesso articolo con un titolo nuovo nell'indirizzo, la stessa pagina in un'altra
  lingua, arXiv v1); ogni pezzo sa dove è usato (`usato_in`) e l'esploratore lo mostra accanto a ogni fonte («anche in»
  un nodo o una Matrice, «stesso documento»), con i nodi collegati tra loro (il 20 febbraio e il coinvolgimento
  americano condividono la nota dell'ONU, l'USAID e il coinvolgimento tre fonti). La selezione settimanale prende un
  articolo per documento (15 copie nella settimana del 2 novembre, quasi tutte di t3n). `tools/doc_ids.py` è comune a
  giudizio, proposte, modello e selezione.
- 10 novembre: **Telegram**, approvato dalla redazione: 12 canali pubblici ucraini e russi in prova
  (`registry/telegram-probation.json`), letti dall'anteprima pubblica `t.me/s/` (robots.txt assente, nessuna riserva TDM),
  fino a 160 post per canale a giro; si tengono solo i post dei gruppi Euromaidan e IA, cercati in ucraino e russo.
  Prima raccolta: 1.650 post letti, 22 tenuti. «майдан» è anche il nome comune della piazza: il gruppo Euromaidan chiede
  il contesto (2013-2014, nomi propri, Nuland, Janukovyč). RT in russo non ha l'anteprima pubblica: esclusa.
  Telegram è anche un **percorso dello scout** per ogni nodo: i canali approvati nelle lingue del nodo, cercati con la
  ricerca interna del canale e le parole del nodo (`telegram_terms`, scritte per il 20 febbraio e il coinvolgimento
  americano). Due giri (circa 0,7 dollari): i post sono quasi tutti notizie brevi (271 giudicati, un contributo), gli
  articoli che linkano rendono di più (5 contributi, tra cui l'inchiesta di hromadske «Кулі»). Di norma entrano solo gli
  articoli linkati; i post dove il nodo li chiede (`telegram_posts`, per i nodi d'affermazione come l'USAID).
- 10 novembre: **Press corner della Commissione**, approvato con EUR-Lex: il feed (50 voci) filtrato su IA e digitale; il
  testo intero viene dal servizio che la pagina stessa legge. La sala stampa del Parlamento risponde con un controllo
  anti-robot: esclusa, non si aggira; i testi approvati arrivano già dall'avviso EUR-Lex (101 documenti).
- 10 novembre: le **12 decisioni sui punti** dei nodi leggeri confermate dalla redazione e registrate.
- 10 novembre: **sotto-topic Economia dell'IA** nel giornale (investimenti, ricavi, valutazioni, chip, concorrenza,
  produttività; non il singolo round o il singolo prodotto). Cambia il prompt della nota: al giro successivo le note si
  rifanno (circa 0,6 dollari per una settimana).
- 10 novembre: le **seconde copie** (pagine sparite cercate nell'Internet Archive) anche nello scaricamento dello scout,
  non solo nel giudizio; il **grafo delle citazioni** cerca per titolo quando la pagina non ha DOI (sul primo inverno
  non aveva fatto consultazioni perché nessuna pagina aveva DOI): da verificare alla prossima esecuzione.
- 10 novembre: **feed fermi**: nessuno rotto. La raccolta riesce; i blog personali pubblicano di rado.
- 10 novembre: **minuti di GitHub.** Il repository privato aveva usato il 90% dei 2.000 minuti mensili; la redazione ha
  messo un budget di 10 dollari con lo stop. Tagli: raccolta ogni 12 ore invece di 6; il controllo delle fonti in prova
  parte solo quando cambiano i file dei candidati; il giudizio fa le chiamate al modello in parallelo (4 alla volta, una
  pagina scaricata alla volta: `JUDGE_PARALLEL=calls`). Prova sulle stesse 100 pagine: 145 secondi contro 319-339 in
  sequenza, voti entro il rumore del giudizio ripetuto, nessun blocco in più dai siti; scaricare in parallelo guadagna
  solo un altro 8% e resta spento.
- 10 novembre: **le decisioni nell'esploratore.** Ogni proposta e ogni novità si accetta o si rifiuta con il motivo
  (registro condiviso della pagina, scrive solo chi la modifica); Claude propone una decisione provvisoria, anche con
  correzioni (catena, posto, testo, autore, data), e la redazione la conferma o la ribalta con il proprio motivo; nel nodo
  entrano solo quelle confermate o ribaltate (`tools/record_decisions.py`, che le scrive in `decisioni.json` e nel nodo).
  Primo passaggio sui quattro nodi: 75 proposte e novità, 28 da accettare (lette le pagine prima), 47 da rifiutare. La
  lettura ha corretto 4 delle 28 sintesi (una su sette): il codice verifica che la citazione esista, non che dica ciò che
  la sintesi le fa dire.
- 10 novembre: copie a indirizzi diversi (lo stesso documento in un'altra lingua, con lo stesso DOI, arXiv o numero
  d'articolo, o lo stesso percorso senza la lingua): 48 copie in più sui quattro nodi; le proposte saltano i documenti già
  nel nodo, anche per ISBN. Al massimo 6 proposte per catena, solo dalla fascia contributo.
- 9-10 novembre: le testate del nodo nelle sue lingue, cercate con `site:` (fino a 6: due nominate nella scheda, le altre
  dal punteggio degli autori distinti pesato sul voto del giudice, due a rotazione; escluse le testate di una sola voce
  ripresa altrove). Sul 20 febbraio: scelte a mano trovate da 2 a 7 su 9, contributi da 48 a 61 (18 da quei siti).
- 9-10 novembre: nodo leggero con i gruppi di fonti che si contraddicono (ogni gruppo coperto da un punto) e la misura di
  stabilità (fair use: 4-5 punti su 6 uguali tra due esecuzioni, 5 esiti uguali); CourtListener dà la precedenza ai
  fascicoli del nodo (da misurare); InoSMI tra i media di Stato.
- 9 novembre: il nodo dei data center e le comunità (leggero, rivisto, nell'esploratore); credito OpenRouter esaurito e
  ricaricato; il nuovo nodo «Il presunto coinvolgimento americano» (Euromaidan), primo scout: 26 contributi, 0,19 dollari.

**In ordine**

1. **Dalla ricerca al nodo.** Lo scout trova di più, ma il guadagno si perde nei passi dopo. Fatto il 10 novembre:
   - la graduatoria: i riferimenti delle voci di Wikipedia senza altri segni passano il filtro, dopo tutte le altre pagine
     (primo inverno dell'IA: fonti di riferimento in graduatoria da 9 a 14 su 20; nessuna pagina già buona spinta fuori
     dalle prime 400 negli altri nodi). Un nodo storico le raggiunge con `k` più alto;
   - l'aggiornamento del nodo leggero legge una pagina nuova su cinque (da 8 a 25; prima sempre 8: sui data center 8 su
     126) e salta prima le copie delle fonti già nel nodo e le pagine già decise.

   - misurato: delle 31 pagine contributo nuove dei data center, 15 valgono per il nodo; le altre ripetono punti già
     coperti. La fascia non è troppo larga: lo spreco viene dalle ripetizioni, che l'aggiornamento ora salta prima;
   - ogni esecuzione registra il tempo di ogni fase (`timing` nel registro del giudizio): sul primo inverno lo
     scaricamento una pagina alla volta prendeva 1.161 secondi su 1.218.
2. **Le decisioni della redazione**: fatto il 10 novembre. Proposte e novità: 98 decisioni (40 accettate, 58 rifiutate;
   44 confermate dalla redazione, una ribaltata, 53 confermate da Claude su incarico), registrate nei nodi; le novità
   accettate dei data center collocate nei punti come altre fonti. Anelli già nei nodi: 109 decisioni con il motivo di
   Claude, confermate dalla redazione (106 tenuti, 3 tolti). Ogni anello, proposta o novità ha ora la sua decisione
   registrata in `reports/nodi/NODO/decisioni.json`, con chi l'ha presa. Nodi leggeri: anche i punti hanno la loro
   decisione nell'esploratore (con le altre fonti del punto); le 12 decisioni sui punti sono confermate e registrate.
3. **Il nodo «Il presunto coinvolgimento americano»**: bozza leggera (2 centesimi) e revisione fatte il 10 novembre, nell'esploratore.
   Seconda revisione il 10 novembre: aggiunto l'estratto di Texty contro il punto 5; la ripresa della Berliner Zeitung
   ha ora l'originale. Le sovvenzioni del NED 2013 non si trovano: la pagina dell'anno dà 404, l'archivio non ne ha
   copia, la ricerca delle sovvenzioni non dà testo leggibile; la copia d'archivio trovata dallo scout parte dal 2014
   (334 sovvenzioni, 22,4 milioni di dollari). Il punto sul finanziamento resta aperto. Da fare: l'originale di
   conflictmanagement.ru, se esiste.
4. **Difetti ancora aperti del giudizio e delle proposte**: le sintesi che leggono troppo (restano da controllare a mano);
   il confronto delle affermazioni con i documenti primari del corpus; il giudice che dà voti diversi allo stesso
   documento in due lingue.
5. **Il primo inverno dell'IA**: rifatto il 10 novembre con la nuova graduatoria, solo sulle pagine mai viste (358, 0,08
   dollari): le fonti di riferimento giudicate contributo passano da 4 a 6 su 20, ma le pagine nuove rendono poco (6
   contributi su 184 giudicate). I riferimenti di Wikipedia servono ai nodi storici, non vanno messi davanti negli altri.
   Il grafo delle citazioni non aveva fatto consultazioni (nessun DOI): ora cerca anche per titolo. Lo scaricamento una pagina alla volta prendeva
   quasi tutto il tempo (3,2 secondi a pagina con molti siti diversi): dal 10 novembre anche lo scaricamento va in
   parallelo (`JUDGE_PARALLEL=all`, mai due pagine dello stesso sito o servizio).
6. Il resto:
   - 21 novembre (promemoria già fissato): bilancio delle fonti in prova (la nuova misura di Brave non serve più);
   - **motori e aggiornamento settimanale**: verificare nel pannello di Exa il costo vero per ricerca (decide metà della
     proiezione) e provare 10 risultati contro 20; accendere il calendario del sabato (`automatico: true` in
     `registry/nodi-attivi.json`, decisione della redazione); rifare la bozza leggera di un nodo quando la settimana porta
     molti contributi (oggi entrano nel giudizio, non nel testo); quando un nodo esce dai nodi attivi;
   - **crescita verso molti topic**, a tappe (10, 30, 100), misurando a ogni tappa il costo per 1.000 articoli e per nodo
     e il lavoro della redazione; prima: archivio fuori da git, un server sempre acceso, un database;
   - **nodi: scelta e linguaggio** (13 novembre, indicazioni della redazione). Le proposte di nodo dalle Matrici non
     convincono: sono discrepanze di una settimana («quante TPU…», «quanti fermati…»), lontane dal lettore, scritte con
     la voce media di un modello. Indicazioni: (1) un nodo è una controversia che dura e su cui si prende posizione; le
     storie settimanali ne sono episodi, le discrepanze fatti da verificare dentro; (2) pochi nodi approfonditi, luoghi
     scelti dove concentrare la partecipazione di una comunità ancora piccola; (3) la scelta pesa quanto un evento è
     rilanciato (temperatura sui social, durata, vicinanza al lettore italiano), ma non dipende tutta dal trend: Ubik
     deve anche creare eventi che meritano di essere rilanciati, e arrivare prima; (4) titolo e sintesi devono
     agganciare: uno studio dedicato del linguaggio, capacità narrativa ed evocativa del marketing più raffinato, senza
     falso allarmismo né clickbait; la domanda nel titolo non è obbligatoria; (5) nessuna redazione umana per ora: il
     gusto della redazione entra attraverso le sue scelte (esempi, preferenze tra alternative) e le revisioni di Claude;
   - **visibilità e parte gratuita** (da ragionare con la redazione): pagine dei nodi pubbliche, con data
     d'aggiornamento, dati strutturati (`ClaimReview` per le verifiche: Fact Check Explorer di Google, chiave rinviata),
     sitemap, crawler dei modelli ammessi; a pagamento il servizio (giornale completo, seguire un nodo, archivio,
     avvisi). Dubbio aperto della redazione: se il nodo è una sintesi di fonti trovabili, un motore o un modello possono
     rifarla da sé, e pubblicarlo cede le fonti trovate con fatica; da pesare contro il traffico e le citazioni. Leva:
     i crawler che raccolgono per l'addestramento sono distinti da quelli che cercano per rispondere (OpenAI GPTBot e
     OAI-SearchBot, Anthropic ClaudeBot e Claude-SearchBot, Google-Extended per Gemini senza toccare la ricerca): si può
     chiudere l'addestramento e restare citabili; e pubblicare il nodo con le fonti principali tenendo riservati
     l'archivio completo, i documenti estratti e lo storico;
   - **il formato comune** (`docs/modello-dati.md`): fatti un documento-un pezzo (10 novembre) e il catalogo comune
     delle fonti (11 novembre, `data/schede.json`, correzioni con `tools/schede.py`; 14 schede con valori discordi da
     rivedere). Resta che le pipeline scrivano gli oggetti direttamente: si fa quando si prepara il sito; i nodi che ricevono come novità i pezzi delle Matrici; le proposte di
     nodo dalle Matrici a ogni settimana nuova, e la costruzione dei nodi accettati;
   - Telegram e Press corner: bilancio dopo due settimane (quanti post tenuti servono ai nodi e alle Matrici);
     Novaya Gazeta Europe da ritrovare; l'API dei dati aperti del Parlamento (solo identificativi, un'interrogazione
     per testo) da valutare;
   - un modello locale per la prima scrematura, addestrato sulle decisioni registrate (serve qualche centinaio di
     decisioni con il motivo e un computer con scheda grafica): rinviato dalla redazione a molto più avanti;
   - le strade verso le fonti provate l'11 novembre, da decidere con la redazione: le decisioni provvisoriamente prese
     da Claude sui documenti dei cinque nodi (21 da far entrare, 22 da lasciare fuori; 16 già confermate dalla redazione,
     registrate il 12 novembre; altre 113 provvisorie sui documenti nuovi di data center e fair use: 66 dentro, 47 fuori,
     soprattutto riprese prese per originali, doppioni, banche dati generali, temi di passaggio) e la loro integrazione nelle catene
     e nei punti; gli originali che mancano (Bloomberg, Reuters, Wall Street Journal: a pagamento, titolo e data); gli
     autori dei documenti trovati come voci candidate (bacino); lo stesso passo sulle newsletter e sui canali;
     l'automazione della catena dopo ogni giornale (oggi `mode=tutto` su richiesta);
   - registri e raccolta, ancora aperti dalla prima scheda del documento: le newsletter per le fonti bloccate (ILO, Eurofound, ETUI) e la redazione registrata come mittente delle
     segnalazioni; i feed di EurekAlert, ANSA e SINC per il registro Scienza;
   - prima del lancio pubblico: il diritto degli editori sugli estratti;
   - feed fermi di ANSA, Corriere e Wired; variabilità del raggruppamento delle Matrici; simulazione della conservazione
     dei testi (rinviata dalla redazione);
   - da valutare alle stesse regole: Common Crawl, Wikidata, le raccomandazioni di Substack; GDELT accantonato finché
     rifiuta i server di GitHub.

## 11. Come si lancia un'esecuzione

Scrivere una riga nel file di richiesta e spingerla su `main` di `ubik-corpus`:

| File | Esempio |
| --- | --- |
| `runs/scout.request` | `nodes=weight-space,fair-use mode=discover judge=yes known k=500 budget=0.6 rounds=2 <data> <motivo>` |
| `runs/judge.request` | rank, giudizio e proposte senza scout (`propose=only` per le sole proposte) |
| `runs/daily.request` | `version=5 label=… tiers=… notes=…` |
| `runs/bacino.request` | `ambito=ia steps=seed,expand,channels,clean,measure` |
| `runs/coverage.request` | `fetch=yes` per raccogliere anche le pagine citate |
| `runs/week-refs.request` | `mode=tutto weeks=2026-11-02` (riferimenti descritti, scout dei riferimenti, originali, bibliografia); `nodes=fair-use` (documenti delle fonti dei nodi); `mode=originals`, `mode=biblio`, `resolve` per un passo solo |
| `runs/matrix-nodes.request` | `weeks=… budget=0.10` (proposte di nodo dalle Matrici) |
| `runs/segnalazioni/NOME.txt` | un testo segnalato dalla redazione: i suoi riferimenti, nel corpus e fuori |

Dopo uno scout con Brave: leggere i risultati, poi cancellare l'esecuzione. Ogni commit di Claude termina con le righe
`Co-Authored-By` e `Claude-Session`.
