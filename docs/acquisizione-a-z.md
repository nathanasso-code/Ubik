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
| `primary-ai-probation.json` | 14 fonti primarie: notiziari di aziende (sempre «parte in causa»), AI Security Institute, GOV.UK, l'avviso EUR-Lex della redazione | prova |
| `gnews-ai.json` | Quattro ricerche GNews (IA ed energia, inglese e italiano) | prova |
| `*-candidates.json`, `bacino-ia.json` | Candidati non ancora approvati, con la storia di come sono stati trovati | — |

### 4.2 Raccolta (`tools/collect.py`, workflow `collect.yml`, ogni sei ore)

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

Sui grandi numeri: un Topic di otto nodi costa circa 2-3 dollari al primo passaggio di giudizio e proposte, poi pochi
centesimi a nodo per gli aggiornamenti se si giudicano solo i candidati nuovi; le Matrici crescono con gli articoli. Le
leve per contenere il costo: due giri di setaccio invece di tre, il prefiltro, il riuso delle note, il giudizio solo sul
nuovo, e più avanti un modello locale per la prima scrematura.

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
  novembre (risposta 200). Da valutare: le copie dell'Internet Archive per le pagine rifiutate.

## 10. Da fare

L'elenco unico di Ubik: ciò che è fatto, in corso e da fare. Aggiornato il 9 novembre.

**Fatto di recente**

- 8 novembre sera: giudizio rilanciato sui tre nodi, 0,90 dollari (sezione 8). Il giudizio non è più il collo di
  bottiglia: le scelte a mano si perdono a monte (lo scout non le trova) o per l'accesso.

**In ordine**

1. **Precisione dei contributi** (in corso, senza costi): lettura a campione dei contributi e della fascia copertura del
   fair use, per sapere quanti sono davvero utili. Finora si era controllata solo la parte scartata.
2. **Ricerca nelle lingue del nodo** (in corso), come parte stabile dello scout: ogni nodo dichiara le lingue originali
   della vicenda, e lo scout cerca in automatico anche in quelle. Prima prova: il 20 febbraio, in ucraino e russo (7 scelte
   a mano mai trovate). Insieme: il limite di CourtListener, dando la precedenza agli atti dei casi (le memorie amicus del
   fair use); per doi.org, la copia ad accesso aperto indicata da OpenAlex o Crossref. Le copie dell'Internet Archive per i
   siti che rifiutano solo con una decisione della redazione, perché la regola dice che un rifiuto non si aggira.
3. **Potare le vie che rendono poco** (sezione 9). Le misure dell'8 sera confermano Semantic Scholar (2 contributi unici
   in tutto) e le antenne dentro lo scout (nessuno; restano per la copertura delle Matrici). Da separare prima di
   decidere: la ricerca per parole chiave su OpenAlex dalle citazioni degli studi d'ancora (10 contributi unici in
   tutto). Poi `resolve` (la ricerca dei siti con Brave) e il terzo giro del setaccio (due giri rendono quanto tre).
   Decisione della redazione.
4. **La bozza automatica del nodo, in forma leggera.** È il passo che manca: oggi le proposte aggiungono anelli a catene
   esistenti, ma nessuno passo genera catene, sintesi, testo di partenza ed elenchi di ciò che è aperto. Senza questo il
   punto 5 non si può fare. Il nodo leggero è la forma più semplice del passo e il formato per la maggior parte dei nodi:
   - la domanda e lo stato in una riga;
   - da tre a sei punti del contendere, ciascuno con l'affermazione, la fonte migliore a favore e quella contro con una
     citazione verificata dal codice, l'esito (accertato, smentito, conteso, aperto) e che cosa deciderebbe la questione;
   - da due a quattro documenti cardine (sentenze, rapporti, studi che contengono già la controversia);
   - la verifica di Ubik solo sui punti decidibili con un documento primario del corpus;
   - «Per approfondire»: i contributi non usati.
   Si perdono il dialogo tra le fonti, i passaggi di provenienza e la coda lunga; l'esito dichiarato evita il falso
   equilibrio. Costo stimato: circa 0,10 dollari di ricerca (un giro di setaccio, `k` 200-300) e una bozza di DeepSeek dai
   15 contributi migliori, rivista solo sui punti contesi; aggiornamento con lo scout settimanale sui soli candidati nuovi.
   Prova: la versione leggera del fair use contro quella piena (quanti punti principali coglie, con quale esito, a che
   costo), sotto 0,30 dollari. Come si scelgono i nodi: le Matrici segnalano gratis le controversie che tornano ogni
   settimana con fonti di parti diverse; lì si apre un nodo leggero, che diventa pieno solo se resta caldo e ha punti
   verificabili.
5. **Un quarto nodo d'attualità** costruito con la pipeline dall'inizio, scelto dalle Matrici come al punto 4: il banco
   di prova del metodo e delle proposte.
6. **Difetti delle proposte** emersi lì e nei tre nodi: doppioni dello stesso documento, un limite di proposte per catena,
   l'etichetta per la propaganda di Stato (lavoro di codice); il confronto delle affermazioni con i documenti primari del
   corpus (il pezzo più difficile, quasi certamente con il modello). Poi le proposte nell'esploratore, da accettare o
   rifiutare con il motivo registrato (sezione 3).
7. **I riferimenti dei PDF e il grafo delle citazioni** (OpenAlex o Crossref, gratuiti) nel setaccio; Wikipedia accesa
   sui temi storici; poi di nuovo la prova di profondità con Wikipedia accesa e spenta.
8. Il resto:
   - 9 novembre (promemoria già fissato, nella conversazione da cui è partito): il giro delle Matrici sulla settimana
     intera, dal 2 al 9 novembre, e la ripubblicazione della pagina; le correzioni che chiedeva sono già fatte;
   - 21 novembre (promemoria già fissato): bilancio delle fonti in prova e nuova misura di Brave;
   - il nodo «Il presunto coinvolgimento americano» (Euromaidan): lavoro di contenuto su un tema storico, con semi e
     affermazione di partenza già pronti; da non confondere con il quarto nodo d'attualità;
   - i canali pubblici di Telegram, ucraini e russi: fonte nuova, da approvare;
   - le pipeline che scrivono direttamente il formato comune (`docs/modello-dati.md`) al posto dei JSON di oggi;
   - un sotto-topic Economia dell'IA per gli articoli senza sotto-topic (168 nella settimana di prova);
   - un modello locale per la prima scrematura, addestrato sulle decisioni registrate (serve qualche centinaio di
     decisioni con il motivo e un computer con scheda grafica);
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

Dopo uno scout con Brave: leggere i risultati, poi cancellare l'esecuzione. Ogni commit di Claude termina con le righe
`Co-Authored-By` e `Claude-Session`.
