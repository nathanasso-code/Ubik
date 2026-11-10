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
| Brave | Dentro il credito mensile gratuito (sette ricerche per nodo; `resolve` ne ha usate 286 una volta) | Nodi e giri del bacino |
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

L'elenco unico di Ubik: ciò che è fatto, in corso e da fare. Aggiornato il 10 novembre.

**Fatto di recente**

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
   - 21 novembre (promemoria già fissato): bilancio delle fonti in prova e nuova misura di Brave;
   - **il formato comune** (`docs/modello-dati.md`), dopo il primo passo del 10 novembre: le pipeline che scrivono
     direttamente gli oggetti, una alla volta, a partire dai nodi (le fonti descritte dentro ogni nodo diventano pezzi
     con l'id comune, una sola scheda per fonte); i nodi che ricevono come novità i pezzi delle Matrici; le proposte di
     nodo dalle Matrici a ogni settimana nuova, e la costruzione dei nodi accettati;
   - Telegram e Press corner: bilancio dopo due settimane (quanti post tenuti servono ai nodi e alle Matrici);
     Novaya Gazeta Europe da ritrovare; l'API dei dati aperti del Parlamento (solo identificativi, un'interrogazione
     per testo) da valutare;
   - un modello locale per la prima scrematura, addestrato sulle decisioni registrate (serve qualche centinaio di
     decisioni con il motivo e un computer con scheda grafica): rinviato dalla redazione a molto più avanti;
   - le strade verso le fonti provate l'11 novembre, da decidere con la redazione: le decisioni provvisoriamente prese
     da Claude sui documenti dei cinque nodi (21 da far entrare, 22 da lasciare fuori) e la loro integrazione nelle catene
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
