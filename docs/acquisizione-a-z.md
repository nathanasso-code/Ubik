# Ubik dalla A alla Z: raccolta, Matrici, nodi (aggiornato al 28 novembre 2026)

Questo documento descrive il sistema com'è oggi, dall'inizio alla fine, ed è il punto di partenza per chi riprende il
lavoro in una nuova conversazione. Il 28 novembre il corpo (sezioni 0-11) è stato riscritto sul sistema attuale,
togliendo le descrizioni superate e le ripetizioni; le misure di metà novembre stanno nell'appendice A, il diario dal 9
al 28 novembre nell'appendice B, il diario delle prime prove (6-15 novembre) in
`docs/history/2026-11-acquisizione-nodi-diario.md`, ogni versione precedente nella storia del repository. Gli altri
documenti correnti: `docs/daily-spec.md` (Matrici), `docs/nodi-spec.md` (nodi), `docs/modello-dati.md` (dati del sito).
La stessa versione è nel documento «Ubik — Acquisizione delle fonti» su Claude, scheda «Dalla A alla Z (28 novembre)».

## 0. Per una nuova conversazione: leggere prima questo

### 0.1 Che cos'è Ubik e dove va

Ubik è un servizio d'informazione che seleziona fonti credibili e mostra che cosa dicono, con quali prove e con quale
interesse, lasciando giudicare al lettore. Ha due anime che condividono le stesse fonti:
- **l'aggregatore di notizie**: la raccolta continua delle fonti approvate, le **Card** (una fonte, o più fonti sullo
  stesso fatto) e le **Matrici** (i fatti della settimana accorpati attorno a un fulcro, per Topic);
- **i nodi**, il prodotto di punta: una domanda importante di un dibattito, trattata come un piccolo studio. La
  promessa: dire che cosa si sa, che cosa no e perché, e permettere di controllare tutto da sé.

Lingua: inglese quanto e più dell'italiano. I nodi saranno relativamente pochi, ma tra i migliori stati della
conoscenza disponibili su quelle questioni.

**Il nodo oggi** (formato in prova sul nodo `ia-matematica`, 27-28 novembre; da perfezionare prima di estenderlo agli
altri nodi): 6-9 **moduli**, ciascuno una sotto-domanda con una sintesi in apertura e tre parti divise con delicatezza:
**contesto** (di che cosa si parla, che cosa è successo, con una cronologia quando serve: qui il modello ha più
iniziativa), **fatti** (ancorati a studi e fonti primarie), **dibattito** (le posizioni raccontate e, sotto ciascuna, le
**voci come card**: la citazione nella lingua originale, chi parla, ruolo, data, link). Poi «Da notare» e «Manca». I
contributi sono di due specie: **nel testo**, con le note numerate (colorate per tipo di fonte), e **a latere**, una card
ciascuno (titolo, sintesi, link all'originale) in fondo al modulo; nel modulo si vedono i primi per un criterio
dichiarato (oggi il giudizio della pipeline, domani i voti), gli altri restano raggiungibili. I moduli sono i simulacri
delle Matrici, i contributi delle Card. Dettaglio: `docs/nodi-spec.md`.

**Il nodo a moduli, prima versione** (decisa tra il 23 e il 26 novembre, prima del formato in tre parti): un nodo è diviso in 6-9 moduli («matrici di nodo»), ciascuno
una sotto-domanda con una tesi in apertura, due o tre paragrafi divulgativi ma non didascalici, le fonti dentro il
testo come numeri colorati per tipo di fonte, un riquadro che mette a confronto solo cifre che misurano la stessa cosa,
«Da notare», «Manca», le voci del dibattito social tenute a parte e le Matrici collegate; la sintesi d'apertura è fatta
delle tesi dei moduli. Esempi: `ubik-corpus/reports/nodi/bolla-ia/` (la bolla dell'IA) e
`ubik-corpus/reports/nodi/delega-conoscenza/nodo.html` (delegare la conoscenza all'IA).

**La visione della redazione (26-28 novembre), da progettare, non ancora costruita:**
- ogni numero di nota apre un pannello da destra con le fonti, un modulo per proporre una modifica della frase o delle
  fonti, i commenti su quel passaggio, l'albero delle fonti che sostengono o smentiscono quella fonte;
- le modifiche proposte dagli utenti iscritti passano prima da un modello e poi dalla comunità (voto); una modifica
  approvata il modello la integra nel testo;
- ogni nodo ha una sezione commenti generale; un commento della redazione (Gio, etichetta OP) accoglie gli utenti;
- ogni modulo potrebbe essere una Matrice «di nodo», duratura nel feed dei Topic, la sola modificabile e commentabile;
- gli utenti potranno pubblicare pezzi originali (card speciali, che possono diventare fonti di un nodo); i
  contributori migliori potrebbero essere pagati;
- i nodi possono fare anche da selettori di studi scientifici su un argomento;
- abbonamenti: forse 0,99 € al mese di sostegno più uno superiore con vantaggi da definire;
- trasparenza totale dichiarata nel sito: intenzioni, solo fonti documentate, rispetto della volontà degli autori
  (robots.txt, riserve TDM), testi integrali mai mostrati.

### 0.2 Regole vincolanti per i nodi scritti in chat

Dal 26 novembre la strada principale, all'inizio, è questa: **la pipeline cerca, Claude scrive i nodi in chat con la
redazione**; la pipeline dovrà poi riprodurre questo risultato il più fedelmente possibile per i nodi che la redazione
non può seguire. Senza eccezioni:
1. **Fedeltà assoluta alle fonti: non si inventa nulla.** Ogni frase che dà un fatto, una cifra o una posizione porta la
   fonte su cui poggia; ogni numero sta nella fonte citata, come la fonte lo dà (niente conversioni, arrotondamenti che
   cambiano la cifra, calcoli nuovi se non dichiarati come «calcolo di Ubik» con i dati di partenza).
2. **La conoscenza propria del modello serve solo a cercare e a dare contesto** (definizioni, raccordi, che cosa manca),
   mai come fonte di fatti o cifre.
3. Ogni fonte entra nella pipeline (giudizio, archivio) prima di essere citata: passaggi e citazioni si mostrano solo se
   il codice li ritrova parola per parola nella pagina archiviata o nel post. Le pagine trovate da Claude in chat
   entrano dalla via `chat` (`reports/scout/NODO/proposte-chat.json`, `{"url", "perche", "titolo"}`).
4. Niente giudizi del modello come etichette: si descrive il peso delle prove e l'interesse di chi parla; un giudizio
   solo dove un documento, un dato ufficiale o uno studio chiude la questione, dicendo quale.
5. Scrittura: divulgativa, sulla falsariga di Wikipedia senza la sua lunghezza; termini spiegati dentro la frase; mai
   «trilioni» (si scrive «2.000 miliardi»); le serie di cifre in un riquadro di confronto, non elencate nel testo.
6. Il testo passa dagli stessi controlli della pipeline (`check()` di `tools/node_modules.py`: ogni numero nelle fonti
   citate dalla frase). Procedura e file: sezione 7.2.
7. Conflitto d'interessi dichiarato quando Claude scrive di Anthropic, dei suoi modelli o della coscienza delle IA.
8. **Per risparmiare, in chat Claude si sostituisce alla pipeline dove la pipeline usa modelli a pagamento costosi**
   (scrittura dei moduli, nuclei, cifre, lacune), **ma non nella ricerca**: la ricerca la fa la pipeline con tutte le
   vie, fino al pieno; quella di Claude si aggiunge (casi in divenire, reazioni nominate, fonti dubbie), non la
   sostituisce. Giudizio, archivio, documenti citati e controlli restano alla pipeline (costano poco).

### 0.3 Come si lavora

- Claude guida; la redazione (Gio, a volte Paola) approva. Sempre in italiano. Niente segreti in chat; l'indirizzo
  email di contatto non va né in chat né nel codice.
- La scelta dei nodi e le spese nuove restano alla redazione. Claude decide su fonti, documenti, novità dei nodi,
  canali e voci (delega del 14 novembre) e porta alla redazione solo i casi dubbi.
- Esecuzioni a pagamento solo da `runs/*.request` spinti su `main` di `ubik-corpus`, o a mano (sezione 11). I workflow
  cercano le parole chiave in tutto il file di richiesta, commenti compresi: nel commento non scrivere parole che sono
  anche opzioni. Mai spingere una nuova richiesta di scout mentre un'altra è in corso.
- Dopo ogni esecuzione che stampa risultati di ricerca (righe `BRAVE-ONLY`, qualunque sia il motore) il log si legge e
  si cancella: `gh api -X DELETE repos/nathanasso-code/ubik-corpus/actions/runs/<id>/logs`.
- Dopo ogni catena o aggiornamento si legge prima di tutto `reports/nodi/<nodo>/bilancio.json`.
- Ogni commit di Claude finisce con le righe `Co-Authored-By` e `Claude-Session` indicate dal sistema. Push con
  `git pull -q --rebase && git push -q origin HEAD:main`; il lavoro di prova in `.design/` (escluso dal repository).
- Un solo elenco delle cose da fare: la sezione 10. Niente documenti nuovi: si corregge questo.
- Repository: `nathanasso-code/Ubik` (pubblico: codice delle Matrici, documenti) e `nathanasso-code/ubik-corpus`
  (privato: registri, corpus, strumenti, workflow, richieste, risultati, testi integrali).

### 0.4 Stato al 28 novembre

- **Priorità della redazione: l'architettura di acquisizione delle fonti, con il nodo `ia-matematica` come
  laboratorio.** Obiettivo: come su Nord Stream, risultati pari o migliori di Wikipedia sullo stesso argomento, in modo
  strutturale e con i costi misurati. I nodi d'attualità si aggiornano ogni giorno. Rinviati: l'estensione del formato
  nuovo agli altri nodi, l'accorpamento dei moduli della delega, la scelta dei temi (trattazione a parte).
- **Nodi.** A moduli: `ia-matematica` (seconda versione scritta in chat il 28 novembre: otto moduli, circa 4.700
  parole, 63 fonti distinte nel testo, 490 contributi a latere; artefatto «Nodo IA e matematica»), `delega-conoscenza`
  (nove moduli in chat), `bolla-ia` (moduli della pipeline). Nella forma precedente (bozza a punti con catene):
  `fair-use`, `data-center-comunita`, `uso-dei-contenuti-pubblicati`, `nord-stream`, `maidan-20-febbraio`,
  `coinvolgimento-americano`, `inverno-ia`, `brain-llm`. In archivio come storia: `weight-space`, `usaid-maidan`,
  `nord-stream-cieco`.
- **Il laboratorio.** Undici giri profondi tra il 27 e il 28 novembre, 609 contributi, non ancora saturo (l'ultimo giro
  41 nuovi). Contro le stesse 127 affermazioni di cinque voci inglesi di Wikipedia: sostenute da 54 a 56, in parte da
  31 a 35, assenti da 37 a 34; riferimenti di Wikipedia trovati da 29 a 44 su 244; nostri documenti 793, 750 assenti
  dalle voci. Le assenze: reazioni nominate riportate da testate chiuse ai programmi (Nature, Al Jazeera, WSJ,
  Guardian, New York Times), la storia prima del 2026. Le ricerche restano in gran parte inglesi (23 su 29): serve un
  vincolo nel codice. Il 28 sera: tre giri con la ricerca proprietaria e tutti i risultati delle API aperti (`tutti`).
- **Autonomia per tema e registro unico** (decisione della redazione del 28 novembre, sezione 6.10): su un tema si cerca
  con le API finché portano fonti nuove, acquisendo tutto ciò che è pertinente; quando non portano più nulla di
  significativamente migliore della ricerca proprietaria, il tema è autonomo e le API servono solo di tanto in tanto.
  Si fa nel tempo, man mano che nascono nodi, non con giri a vuoto. Soglia confermata: contributi trovati solo dalle
  API sotto il 10% per tre giri di fila. Temi: i sette proposti da Claude, per ora. Punto di partenza: la ricerca
  proprietaria ritrova 95 dei 609 contributi del laboratorio (16%).
- **Crediti e spesa.** OpenRouter ricaricato il 27; GitHub Actions bloccato la notte del 28 per il tetto di spesa e
  ricaricato; Exa ricaricato con 20 $ il 28 sera dopo essere rimasto senza credito; Tavily sul piano mensile da 30 $
  (5.000 crediti a novembre, 1.465 già usati); Brave senza credito. Le chiamate ai modelli nell'ambito IA hanno superato
  il tetto di 20 $ (46,65 $ a novembre): da discutere con la redazione. **La redazione è preoccupata della spesa
  crescente**: ogni esecuzione nuova va giustificata e misurata (sezione 8).

### 0.5 Prossimi passi

1. Leggere i tre giri del 28 sera sul laboratorio (contributi in più dall'apertura di tutti i risultati, quota trovata
   solo dalle API, costo reale) e tirare le somme con la redazione su che cosa si è raccolto.
2. Il vincolo sulle lingue nel pianificatore; le parti come ancore (canali ufficiali delle istituzioni seguiti ogni
   giorno); termini GitHub da persone e progetti chiave; il controllo di credibilità degli autori e dei siti (il caso
   Nielsen; le card a latere includono aggregatori poco affidabili).
3. Il registro unico: i raccoglitori passano uno alla volta al registro (prima i siti, poi autori e canali, infine i
   topic delle Matrici); per ogni nodo nuovo, il tema e la misura di autonomia.
4. Con la redazione: che cosa entra nel testo di un modulo e che cosa resta a latere; i temi (più specifici o più
   generici, come e quando nascono); i termini di Exa sulla conservazione dei risultati.
5. Un nodo nuovo fatto con la stessa strada (ricerca della pipeline, scrittura in chat), misurato contro Wikipedia con
   i costi, quando la redazione sceglie l'argomento.
6. Il sito: prima il modello dei dati (`docs/modello-dati.md`), poi un prototipo in sola lettura dai file dei nodi.

### 0.6 Prompt per aprire una nuova chat

```
Sei Claude, alla guida del progetto Ubik con la redazione (Gio, a volte Paola). Rispondi sempre in italiano.
Prima di tutto clona i due repository (nathanasso-code/Ubik, pubblico; nathanasso-code/ubik-corpus, privato) e leggi
per intero la sezione 0 di docs/acquisizione-a-z.md, poi la sezione 10 (l'unico elenco delle cose da fare). Valgono
senza eccezioni le regole delle sezioni 0.2, 0.3 e 3: fedeltà assoluta alle fonti, niente invenzioni, citazioni
ritrovate parola per parola dal codice, robots.txt e riserve TDM rispettati, niente segreti in chat, esecuzioni a
pagamento solo da runs/*.request su main, scelta dei nodi e spese nuove alla redazione, conflitto d'interessi
dichiarato quando si parla di Anthropic. Ogni commit finisce con le righe Co-Authored-By e Claude-Session indicate
dal sistema. Dopo ogni esecuzione che stampa risultati di ricerca cancella il log con
gh api -X DELETE repos/nathanasso-code/ubik-corpus/actions/runs/<id>/logs. Dopo ogni catena leggi
reports/nodi/<nodo>/bilancio.json prima di qualsiasi altra cosa. La ricerca la fa la pipeline; in chat ti sostituisci
ai modelli a pagamento costosi (scrittura dei moduli), non alla ricerca. La redazione è attenta alla spesa: stima e
misura ogni esecuzione. Comincia dicendo in poche righe a che punto sei e qual è il prossimo passo.
```

## 1. Che cosa fa Ubik

| Anima | Domanda | Prodotto |
| --- | --- | --- |
| Aggregatore (attualità) | Che cosa è successo questa settimana? | **Matrici**: gli articoli di testate diverse sullo stesso fatto, divisi in **card**; le card singole per i fatti con una sola fonte; per Topic e sotto-topic |
| Nodi (conoscenza) | Su che cosa ci si divide, e che cosa dicono le prove? | **Moduli** su sotto-domande, con fonti nel testo, voci del dibattito e contributi a latere |

Un **Topic** è il perimetro delle Matrici (oggi Intelligenza artificiale, con i sotto-topic regole, lavoro, data center
ed energia, diritto d'autore, economia). Un **tema** (sezione 6.10) è il perimetro delle fonti: raccoglie i nodi e i
topic delle Matrici sullo stesso soggetto, perché tutti partano dalle stesse fonti.

## 2. Dove sta ogni cosa

| Dove | Che cosa |
| --- | --- |
| `nathanasso-code/Ubik` (pubblico) | Codice delle Matrici (`ingestion/`), prompt delle Matrici (`prompts/`), documenti (`docs/`) |
| `nathanasso-code/ubik-corpus` (privato) | Registri (`registry/`), corpus dei testi (`corpus/`), strumenti (`tools/`), prompt dei nodi (`prompts/`), workflow (`.github/workflows/`), richieste (`runs/`), risultati (`reports/`) |
| Segreti di `ubik-corpus` (solo i nomi) | `OPENROUTER_API_KEY`, `EXA_API_KEY`, `TAVILY_API_KEY`, `BRAVE_API_KEY` (senza credito), `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, `MASTODON_TOKEN`, `MASTODON_INSTANCE`, `GNEWS_API_KEY`, `UBIK_GMAIL_*`, `COURTLISTENER_API_KEY`, `GOVINFO_API_KEY`, `SEC_USER_AGENT` |
| Artefatti | «Nodo IA e matematica», i nodi della delega e della bolla, l'esploratore delle Matrici e dei nodi |

Tutto gira sui server di GitHub (Actions): il contenitore di lavoro di Claude non raggiunge le API esterne.

## 3. Le regole che valgono ovunque

- **Fonti nuove approvate per criterio, in automatico** (dal 13 novembre): siti, autori, canali degli autori, canali
  Telegram e account Mastodon entrano «in prova» quando passano un criterio stretto e modificabile; si tolgono dopo
  (stato «rimosso», mai riapprovato). Nessuna fonte si esclude per sempre. Le fonti in prova non bastano da sole a fare
  una Matrice.
- **robots.txt e riserva TDM rispettati**, sempre: un sito che vieta o rifiuta (403) non si aggira, si registra.
- **Seconde copie** (`tools/second_copy.py`): la copia ad accesso aperto indicata da OpenAlex o Crossref quando
  l'editore di un DOI rifiuta; la copia dell'Internet Archive solo per le pagine che non esistono più (404, 410, dominio
  inesistente) e solo se il sito originale non vieta i programmi; mai per le pagine che rifiutano (per quelle si può
  mostrare al lettore il link alla copia, senza raccoglierla né citarla).
- **CourtListener attraverso l'API** (approvata l'8 novembre, `tools/courtlistener.py`): robots.txt chiude il sito ai
  programmi e nello stesso file li manda all'API; gli indirizzi dell'API, con il token e nei suoi limiti, sono l'unica
  eccezione al controllo di robots.txt (dettaglio in appendice A.4).
- **I testi integrali restano nel repository privato.** Si mostrano sintesi e citazioni brevi (per la stampa al più
  circa 150 caratteri per articolo, per gli altri testi entro 300).
- **Una citazione, o un giudizio del modello, conta solo se il codice ritrova la frase parola per parola** nel testo
  raccolto.
- **Motori di ricerca a pagamento** (Exa, Tavily; Brave senza credito): **non si conservano le liste dei risultati**
  (i termini di Tavily e di Brave lo vietano; Exa da verificare), solo le pagine che apriamo noi e gli identificativi
  cifrati dei risultati per confrontare i motori. Le pagine aperte, con i loro link, sono nostre (archivio). Per non
  perdere i risultati pagati si aprono durante l'esecuzione (`tutti`, sezione 6.4). Tetti mensili nel codice
  (`CAPS` in `tools/scout.py`; contatore `data/search-usage.json`).
- **Costi**: ogni esecuzione dichiara il suo budget e lo confronta con una stima prima di spendere; l'aggiornamento dei
  nodi ha un tetto suo. Tetto delle chiamate ai modelli nell'ambito IA: 20 $ al mese (superato a novembre); GitHub
  Actions: 20 $ al mese oltre i minuti inclusi.
- **Si conserva ciò che non si ricostruisce a ritroso**: le decisioni editoriali con il motivo e le affermazioni con la
  loro provenienza (base per un giudice addestrato sui criteri di Ubik).

## 4. Le fonti e il corpus

### 4.1 Registri e registro unico

I registri nascono in tre generazioni: le liste per topic di ottobre (`ai.json`, `ai-regulation.json`, `science.json`
e i loro `-probation`, `-candidates`), i registri approvati per criterio dal 13 novembre (`siti.json`, `autori.json`,
`telegram-canali.json`, `mastodon-canali.json`, canali degli autori), le voci (`ai-voices.json`). Ogni raccoglitore
legge ancora i suoi.

Sopra ci sono due viste: l'**anagrafe** (`tools/anagrafe.py`, `registry/anagrafe.json`: ogni fonte una volta con uno
stato; 3.383 fonti al 28 novembre) e, dal 28 novembre, il **registro unico per tema** (`tools/registro.py`,
`registry/registro.json`, `reports/fonti/registro.md`): per ogni fonte i temi che serve, le pagine che ha dato in ogni
archivio, i nodi a cui ha contribuito, il modo in cui la raccogliamo; per ogni tema fonti, pagine, autonomia. Si
aggiorna alla fine di ogni catena e di ogni aggiornamento. Il passo successivo è che i raccoglitori leggano il registro
unico, uno alla volta (sezione 10).

I registri delle liste di ottobre (numeri di allora; oggi si allargano per criterio):

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

### 4.2 Raccolta (`tools/collect.py`, workflow `collect.yml`, ogni 12 ore)

Per ogni fonte il raccoglitore legge il canale dichiarato: feed RSS o Atom, sitemap con filtro sui percorsi
(`sitemap_filter`, per i siti senza feed: Anthropic, Artificial Analysis), filtro di OpenAlex (`openalex`: una rivista
per ISSN o un elenco di autori; si conserva l'abstract), API di arXiv, ricerche GNews (finestra di 30 ore, fino a otto
pagine, aggregatori esclusi, la testata vera come origine). Per ogni voce nuova apre la pagina dell'editore se robots.txt
lo consente e non c'è la riserva TDM, estrae il testo (trafilatura, PDF con pypdf) e lo salva in `corpus/<ambito>/` con
origine, testata, livello, data e «trovata con». Al massimo 40 voci nuove per fonte a giro. Costo: zero, tranne
l'abbonamento GNews (49,99 euro al mese, circa 32 richieste al giorno su 1.000).

Le testate seguite per sezione hanno anche il feed di tutto il sito, filtrato con le parole dei Topic
(`tools/feed_wide.py`, `registry/parole-topic.json`). Corpus al 28 novembre (documenti nell'indice): circa 24.750 in
`ai`, 11.000 in `ai-regulation`, 5.500 in `ai-research`, 2.600 in `science`, 830 pagine citate, 120.000 voci dei feed
dei siti, circa 6.300 pagine archiviate per i nodi.

### 4.3 Le pagine citate (`tools/fetch_cited.py`, `coverage.yml`, il lunedì dal 15 novembre)

Il dibattito legge una coda lunghissima di siti, ciascuno citato una o due volte, che nessun abbonamento copre. Ogni
lunedì si raccolgono, con le stesse regole, le pagine citate da almeno due fonti del corpus, quelle condivise da
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
Mastodon seguiti da molte voci: non sono fonti, i loro link servono a scoprire pagine. Il bacino propone; dal 13 novembre le fonti entrano per criterio (sezione 3).

### 4.5 I siti approvati e i loro feed (`tools/sites.py`, ogni giorno in `sites.yml`)

Ogni sito che ha dato a un nodo un contributo con un fatto nuovo verificato nel testo è approvato in automatico
(`registry/siti.json`, 1.835 siti al 28 novembre). Del sito si cerca il feed (dichiarato nella home, gli indirizzi usuali, le
sitemap di robots.txt; mai per gli archivi generali come GitHub o arXiv) e ogni giorno se ne raccolgono le voci nuove
(`corpus/siti/HOST/MESE.jsonl`: titolo, sintesi, indirizzo, data). La ricerca proprietaria (4.9) le interroga per ogni nodo; nel giornale
entrano solo le voci di siti con almeno due fatti verificati e un termine dell'IA nel titolo, fino a 40 a settimana.
Le pagine buone di ogni nodo sono conservate in `corpus/targeted/NODO/pagine/` (`tools/archive_node.py`).

### 4.6 Autori e loro canali (`tools/authors.py`, `tools/author_channels.py`, ogni giorno)

Il giudice nomina per ogni contributo l'autore competente. I nomi si normalizzano una volta (persona, istituzione o
redazione); una persona con almeno 2 pagine con un fatto nuovo verificato, e 2 nodi o 3 pagine, entra «in prova»
(`registry/autori.json`); un controllo sull'attività rende «storico» chi non è più attivo (Lighthill). Per ogni autore
si cercano i canali: OpenAlex, la pagina personale, Bluesky, Mastodon, Substack (X e LinkedIn solo annotati). I casi
incerti (un omonimo) li rivede un modello come li rivedeva Claude (17 su 18 uguali alla prova); quelli che restano
incerti vanno a Claude, 8 alla volta (`reports/fonti/canali-da-rivedere.md`).

### 4.7 Telegram e Mastodon

**Telegram** (`registry/telegram-probation.json`, 12 canali fissi; `registry/telegram-canali.json`, approvati in
automatico): i canali inoltrati o citati da quelli seguiti, dalle pagine del corpus o dal giudice; esame se citati da
almeno 2 fonti, di cui una non di Stato né di propaganda; anteprima pubblica, 1.000 iscritti, 5 post; il modello dice
che cosa sono (istituzione, testata, giornalista, analista, OSINT, testimone, aggregatore, propaganda, spam) e se un
canale serve uno Stato (il paese da solo non basta). Spam e aggregatori fuori, il resto in prova con le etichette.
«Primario» solo se l'istituzione garantisce il canale (un sito governativo lo cita, o il suo sito rimanda al canale):
i suoi post sono documenti. Raccolta ogni 12 ore.

**Mastodon** (`tools/mastodon.py`, `registry/mastodon-istanze.json`, `registry/mastodon-canali.json`): gli account
delle istanze governative (social.bund.de, social.overheid.nl: 81 in prova, primari per costruzione), raccolti per RSS
ogni giorno; l'account Mastodon degli autori approvati; robots.txt e la scelta di chi chiede di non essere indicizzato.

### 4.8 Le voci dai social (opinioni, separate da resoconti e documenti)

Per ogni nodo attivo, a ogni aggiornamento (e nelle catene con `social_voices`): Bluesky (`tools/social_voices.py`: ricerche brevi dai termini e dalla catena; i
fili dello stesso autore ricomposti), Mastodon (`tools/mastodon_voices.py`: hashtag scelti dal modello su 12 istanze e
la ricerca a testo col nostro account), Telegram (`tools/telegram_voices.py`: solo canali di giornalisti, analisti,
OSINT e testimoni, con visualizzazioni e reazioni). Filtri in ordine: lunghezza, seguito (contro bot, spam e uscite
estemporanee), account (età, post, follower), giudice (aggiunge una posizione o una competenza che le fonti non
danno?). Chi non dichiara una competenza entra solo con qualcosa di verificabile e un seguito triplo; una voce non
ripete una posizione già tenuta; le testate tra le voci diventano fonti (strada `segnalati`); un secondo passaggio
cerca le parti non ancora sentite. Le voci si sommano di settimana in settimana (`reports/nodi/NODO/voci-social.json`)
e si vedono nell'esploratore con la loro rete.

### 4.9 La ricerca proprietaria (`tools/corpus_index.py`)

Un indice a testo pieno (SQLite FTS5) su tutto ciò che Ubik ha raccolto o archiviato: corpus delle Matrici, voci dei
feed dei siti, autori, Mastodon, Telegram, pagine citate e, dal 28 novembre, le pagine archiviate di tutti i nodi
(174.625 documenti, circa un minuto per costruirlo, ricostruito a ogni esecuzione). Nelle catene è la via `home`, in
ogni giro: le stesse ricerche dei motori, con una qualsiasi delle parole e i risultati ordinati per pertinenza,
escluse le pagine del nodo stesso. È la base dell'autonomia per tema (6.10).

## 5. Le Matrici della settimana

`ubik-corpus/tools/select_ai_week.py` sceglie gli articoli della finestra (solo fonti approvate), toglie i doppioni e
applica un prefiltro sui termini dei Topic. Poi `Ubik/ingestion/ubik_daily5.py` con DeepSeek V4.1 Flash: una nota per
articolo, il raggruppamento in Matrici e card, la conferma del codice (due articoli stanno insieme solo se date e parole
lo provano; servono due origini indipendenti e una fonte approvata o primaria), un secondo giro sulle card singole, i
testi. Le grandi storie restano nel sotto-topic dove sono principalmente a tema, con rimandi negli altri. In calendario
il lunedì alle 4:23 UTC sulla settimana chiusa (`daily.yml`); a mano da `runs/daily.request`. Costo: circa 0,7-1,3 $ a
settimana. Specifica: `docs/daily-spec.md`.

I passi del modello, in breve (dettaglio in `docs/daily-spec.md`):

1. **nota** per articolo: pertinenza, tipo, evento (attore, azione, oggetto, data), sintesi e citazione, sotto-topic;
2. **raggruppamento** per sotto-topic in Matrici e card, con il motivo di ogni card separata;
3. **conferma del codice**: due articoli stanno insieme solo se date e parole di attore o oggetto lo provano; servono
   almeno due origini indipendenti, e almeno un articolo da una fonte approvata o primaria (una Matrice fatta solo di
   fonti in prova si scioglie);
4. **secondo giro** sulle card singole e fusione delle Matrici gemelle; controllo delle card;
5. **filtro del sotto-topic** e **testi** (titolo neutro, essenza, testi delle card) solo dalle sintesi.

## 6. I nodi: l'acquisizione

### 6.1 La scheda del nodo

`reports/nodi/<nodo>/node.json` e `scout.json`: la domanda, le sotto-domande (3-5 rendono meglio di 8), le lingue della
stampa del campo, i termini, le ancore, le ricerche per le lacune. Un nodo nuovo nasce dalla sola domanda
(`bootstrap` in `runs/catena.request`, domanda in `runs/domande/NODO.txt`): il modello scrive sotto-domande, lingue,
termini e prime ricerche. Nella scheda compilata a mano (i primi nodi) ci sono anche le ricerche per GitHub e per la
letteratura, i DOI, la voce di Wikipedia, le date del caso (`dates`) e le fonti già note (`known`) per misurare.

### 6.2 La catena di ricerche (`tools/entity_rounds.py`, `catena.yml`)

A ogni giro un modello economico legge che cosa dicono le fonti trovate e scrive fino a `q=` ricerche nuove. Doveri
fissi: coprire tutta la storia della questione fase per fase; cercare il testo integrale dei documenti che il nodo ha
solo come riassunto; sentire ogni parte con le sue parole, comprese le istituzioni del settore e le reazioni nominate,
nelle lingue della stampa del campo; non ricercare invano due volte lo stesso documento; seguire le **persone chiave**
(`tools/node_people.py`: le persone citate da almeno 2 fonti o autrici di almeno 2, lette dalle pagine archiviate).
Il giro si chiude con il conteggio (`tally`): ci si ferma quando un giro porta meno di `min=` contributi nuovi. Dal 28
novembre le ricerche sono **adattive**: nella stessa esecuzione un giro ha il doppio delle ricerche che hanno portato un
contributo nuovo nel giro prima (almeno 8 e un terzo di `q=`, al più `q=`; `ricerche_fruttuose` in `catena.json`).

### 6.3 Le vie dello scout (`tools/scout.py discover`)

| Via | Che cosa porta |
| --- | --- |
| `home` | La ricerca proprietaria (4.9), in ogni giro |
| `brave` (il nome è storico: sono i motori a pagamento) | Le ricerche della catena su Exa e, come complemento, Tavily (sotto) |
| `corpus`, `corpus-cited` | Gli articoli del corpus che citano le ancore e i link che citano |
| `fonti` | I link nei testi delle fonti del nodo |
| `riferimenti` | I documenti che le fonti descrivono come prova (`tools/node_refs.py`, 6.6) |
| `snowball` | I link citati dalle pagine migliori; un link citato da due pagine è forte |
| `atti`, `istituzioni` | Numeri di causa risolti su EUR-Lex; documenti di banche centrali, FMI, BIS, OCSE, uffici statistici, SEC EDGAR |
| `telegram`, `bluesky`, `hn`, `github` | Le ricerche del nodo nei canali approvati, nei post, su Hacker News, nei repository |
| `openalex`, `s2`, `wikipedia` | Letteratura; i riferimenti di Wikipedia (spenti nei banchi di prova contro Wikipedia) |
| `segnalati`, `chat` | Gli articoli postati dalle testate tra le voci; le pagine proposte da Claude in chat |
| Antenne | I link condivisi da voci e antenne (valgono per la copertura più che per i nodi) |
| Corpus (feed) | Anche le voci dei feed dei siti, degli autori e di Mastodon (dal 13 novembre) |
| `web` | Spento: Bing vieta l'uso automatico |

**Motori** (dal 28 novembre, `_complement` in `tools/scout.py`): un motore per ricerca, il secondo come complemento.
Exa cerca per primo; Tavily solo quando dei 20 risultati di Exa al massimo 8 sono pagine nuove per il nodo
(`SEARCH_COMPLEMENT_MAX`; `SEARCH_ROUTING=entrambi` torna ai due motori). Negli aggiornamenti quotidiani Exa non ha
finestra temporale e porta pagine vecchie, così entra Tavily, che la finestra ce l'ha (`SEARCH_SINCE`). Se un motore è
senza credito, si passa all'altro e il bilancio dà l'allarme.

### 6.4 Filtro e giudizio

**Primo livello, il filtro per codice** (`tools/rank_candidates.py`). Senza aprire le pagine, da indirizzo, titolo, menzioni e voci: nomina il caso (frasi, coppie di parole come «fair use»,
parole distintive, traslitterazioni, plurali), è uno studio, un documento ufficiale, un repository; la data del caso
nell'indirizzo; trovato cercando il caso (Bluesky, Hacker News, casa) con un titolo. Toglie piattaforme e post social,
pagine di servizio, titoli da motore di ricerca. Ogni segnale ha un peso visibile nella classifica
(`reports/scout/<nodo>/rank.json`). Tiene circa un terzo dei candidati. Costo zero.

**Secondo livello, il giudizio** (`tools/judge_candidates.py`, `prompts/judge-node.txt`). Gira nello stesso giro dello scout, così
vede anche le pagine trovate solo dai motori (che non si conservano). Per i primi `k=` della classifica apre la pagina, ne prende le prime 1.400 parole e chiede a DeepSeek V4.1 Flash (circa 0,0003 $ a pagina): è pertinente? che tipo di pagina? è
derivata da un'altra? porta prove proprie, qualcosa di nuovo per le catene del nodo, argomenti contro, fonti primarie, un
autore competente? Ogni «sì» deve citare una frase che il codice ritrova nel testo. Il codice calcola il punteggio (prove
proprie 2,5, novità 2, argomenti contro 1, autore 1, fonti primarie 0,5, più il peso del tipo, con analisi e opinioni
competenti a 0,8 come i resoconti dal 27 novembre; una pagina derivata perde 2,5). Le copie dello stesso documento e
le riprese di una stessa voce si riconoscono (fasce «copia» e «ripresa»).

Tre fasce: **contributo** (punteggio da 5), **copertura** (pertinente, da 3 a 5: non serve al nodo, serve alle Matrici e
alle card), **scarto**.

**Setaccio**: i link citati dalle pagine «contributo» (solo nel corpo del testo) diventano i candidati del giro
successivo, in ordine di quante pagine buone li citano, fino a 250 per giro. Si ferma quando un giro non trova nulla. Nelle catene il giudizio fa un giro solo (`rounds=1`):
il setaccio lo fanno le vie `fonti` e `snowball` del giro di catena successivo.

Risultato in `reports/scout/<nodo>/judge.json` (con le vie che hanno trovato ogni pagina); i testi delle pagine buone
si archiviano (6.5). Nelle catene il giudizio legge solo le pagine nuove (`only_new`).

Con **`tutti`** nella richiesta (dal 28 novembre) ogni pagina restituita dai motori si apre e si giudica durante
l'esecuzione, oltre ai `k=` migliori delle altre vie, e le pagine pertinenti ma sotto la fascia contributo si archiviano
comunque per il tema (`JUDGE_ALL_ENGINES`, `ARCHIVE_PERTINENT`). Prima, del laboratorio, si erano giudicate 572 pagine
sulle 5.474 restituite dai motori.

### 6.5 L'archivio

`tools/archive_node.py`: le pagine contributo e copertura (e, con `tutti`, le pertinenti) con il loro testo, in
`corpus/targeted/NODO/pagine/<sha256 dell'indirizzo canonico, 16 caratteri>.json`, dopo ogni giro.

### 6.6 I documenti citati (`tools/node_refs.py`, `tools/ref_scout.py`)

Le fonti del nodo descrivono documenti come prova (studi, sentenze, rapporti, leggi): si leggono, si cercano (link nel
testo, OpenAlex, arXiv, CourtListener, ricerca web con Exa o Tavily, `refweb=`), si confermano e passano al giudice; i
non trovati vanno al pianificatore. Due budget separati (lettura `refs=`, ricerca `find=`); i documenti decisivi per
primi. Su Nord Stream è il passo che ha reso di più.

### 6.7 Il bilancio (`tools/chain_audit.py`)

Ogni catena e ogni aggiornamento finiscono con `reports/nodi/NODO/bilancio.json` e avvisi nel workflow: saturazione,
lingue (allarme se più del 70% in una lingua), documenti citati mai cercati, vie ferme o in errore, motori senza
credito, ricerche per motore, persone chiave, e l'**autonomia** (6.10). Nato il 27 novembre, quando si è scoperto che
metà dell'architettura di Nord Stream non girava senza che nessuno se ne accorgesse.

### 6.8 L'aggiornamento dei nodi (`settimana.yml`, `tools/weekly.py`, `registry/nodi-attivi.json`)

- **Ogni giorno alle 5:17 UTC** i nodi in `quotidiani` (oggi `ia-matematica`): un giro con le impostazioni di
  `quotidiano` (20 ricerche, finestra di 2 giorni, tetto di 1 $ al giorno), persone chiave, archivio, bilancio.
- **Il sabato** i nodi in `nodi` (fair use, data center, uso dei contenuti, Nord Stream): la catena in modalità
  settimanale (prima ciò che è successo dall'ultimo giro), le voci, l'archivio, i documenti citati, poi le novità nella
  bozza (`tools/light_node.py update`), le decisioni automatiche (`tools/auto_decide.py`, le dubbie a Claude in
  `da-decidere.json`) e l'integrazione nel testo (`tools/integrate.py`). Prima di partire il massimo possibile si
  confronta con il tetto (4 $); poi siti, autori, canali.
- Il calendario è acceso (`automatico: true`, dal 15 novembre). A mano: `runs/settimana.request` (`quotidiano` per i
  nodi quotidiani).

### 6.9 Le misure contro Wikipedia (`tools/wiki_bench.py`, `runs/week-refs.request`)

Le affermazioni di una o più voci di Wikipedia (`wikiq=en:Titolo|en:Altro`), fissate una volta (`fisse=`) per misurare
sempre sulle stesse, cercate nei documenti del nodo con le parole nelle lingue del nodo; e i riferimenti in comune.
Wikipedia resta esclusa dalle vie nei banchi di prova.

### 6.10 L'autonomia per tema

Decisione della redazione del 28 novembre. Un tema (`registry/temi.json`: nodi e registri delle Matrici su uno stesso
soggetto) si acquisisce con le API finché portano fonti nuove, aprendo tutti i risultati e archiviando tutto ciò che è
pertinente. A ogni giro si conta quanti contributi nuovi hanno trovato solo le API e quanti anche la ricerca
proprietaria (`vie_contributi` in `catena.json`; `autonomia` nel bilancio; `quota_solo_api`). Il tema è **autonomo**
quando la quota resta sotto il 10% per tre giri di fila (soglia confermata dalla redazione); da allora le API servono
solo di tanto in tanto per scovare fonti nuove, e se la quota risale il tema torna in acquisizione. Si fa nel tempo,
man mano che nascono i nodi di quel tema, non con giri a vuoto. Avvertenza dal laboratorio: dopo undici giri la
maggior parte dei contributi nuovi veniva ancora da siti mai visti, quasi tutti con un solo contributo.

Temi provvisori (proposta di Claude, in uso finché la redazione non li ridefinisce): matematica, intelligenza
artificiale, economia dell'IA, regolazione e diritto dell'IA, energia e territorio, scienza, Europa orientale e
sicurezza. 374 fonti seguite non hanno ancora un tema.

### 6.11 Gli strumenti della forma precedente (catene di anelli e bozza a punti), ancora nel codice

**Proposte** (`tools/propose_links.py`, `prompts/propose-link.txt`): per i contributi, DeepSeek propone l'anello nel formato del nodo (catena, che cosa afferma, relazione, citazione); il
codice controlla che la citazione sia nel testo e la regola per la stampa. Le proposte vanno in
`reports/nodi/<nodo>/proposte.json`; il nodo non si tocca.

**Raccolta e costruzione**: le pagine scelte vanno in `reports/scout/<nodo>/pick.json`; `scout.py fetch` le raccoglie nel corpus privato
(`corpus/targeted/<nodo>/`). Claude, in conversazione, legge i testi, decide gli anelli, scrive sintesi e relazioni,
verifica sui documenti primari (le sentenze, i paper) e aggiorna `reports/nodi/<nodo>/node.json`. `tools/build_model.py`
costruisce il modello che l'esploratore mostra, con la regola delle citazioni. Le segnalazioni della redazione entrano come
`segnalazione` in `corpus/targeted/<nodo>/`.

La bozza a punti dei nodi d'attualità (`tools/light_node.py`, `runs/light.request`), le decisioni automatiche
(`tools/auto_decide.py`) e l'integrazione nel testo (`tools/integrate.py`) girano ancora nell'aggiornamento del sabato
(6.8) e producono l'esploratore (`tools/build_model.py`, `ingestion/ubik_explorer.py`).

## 7. I nodi: la scrittura

### 7.1 Dalla pipeline (`tools/node_modules.py`)

`moduli=NODO` in `runs/judge.request`: i nuclei (le sotto-domande con le fonti), le cifre con il loro contesto
(`tools/node_estimates.py`, `tools/figures.py`), le lacune (`tools/node_gaps.py`, Opus), la scrittura dei moduli
(Sonnet o Opus), i controlli `check()` (ogni numero nelle fonti citate dalla frase) e `chosen_box()` (il riquadro di
confronto solo tra cifre che misurano la stessa cosa). È la strada per i nodi che la redazione non segue; costa di più.

### 7.2 In chat (la strada principale per ora)

Esempio completo: `ubik-corpus/reports/nodi/ia-matematica/chat/`.
1. La pipeline cerca fino al pieno (catene, documenti citati, persone, voci).
2. Claude legge in chat le pagine archiviate che servono (`t.py head PREFISSO`, `t.py grep`; i prefissi sono i primi
   caratteri dello sha256 dell'indirizzo canonico).
3. Scrive i moduli in `moduli2.py`: le fonti si citano per chiave tra parentesi quadre, `[chiave]`; per ogni chiave i
   passaggi copiati dalla pagina; le voci social con `{"v": nome, "t": citazione}`, ritrovate per nome e testo in
   `voci-social.json`.
4. `build2.py` numera le fonti nell'ordine di citazione, ritrova ogni passaggio e citazione parola per parola, esegue
   `check()`, prepara le card a latere (gli altri contributi del nodo, una card ciascuno, ordinati per il punteggio del
   giudizio, senza le copie delle fonti citate) e scrive `nodo2.json`. Si pubblica solo con zero problemi.
5. `gen_page2.py` scrive `reports/nodi/NODO/nodo.html`; la pagina si guarda a schermo (desktop e telefono) e si
   pubblica come artefatto.

## 8. Quanto costa

### 8.1 Prezzi

| Voce | Prezzo |
| --- | --- |
| Modelli: DeepSeek V4.1 Flash (acquisizione, Matrici) | Giudizio circa 0,0003 $ a pagina (la stima preventiva ne conta 0,0015); piano della catena circa 0,002 $ a giro |
| Modelli: Sonnet, Opus (moduli della pipeline, lacune) | Decimi di dollaro per modulo |
| Exa | 7 $ ogni 1.000 ricerche a listino (circa 3 osservati a novembre); ricaricato con 20 $ il 28 novembre |
| Tavily | Piano mensile da 30 $ (5.000 crediti a novembre, uno per ricerca base); oltre 0,008 $ a credito |
| Brave | Senza credito; i termini vietano di conservare i risultati senza un piano apposito |
| GitHub Actions | 0,006 $ al minuto oltre la quota (runner sul computer della redazione 0,002 $ dal 1° marzo 2026); minuti di novembre circa 4.300 |
| GNews | 49,99 € al mese |

### 8.2 Stime a regime (28 novembre)

Con 2-3 nodi nuovi al giorno le quote gratuite non contano. Prima dei tagli: un nodo nuovo (ricerca della pipeline,
scrittura in chat) circa 8-9 $; un aggiornamento quotidiano circa 15-17 $ al mese per nodo; 60-90 nodi al mese,
500-800 $. **Nella stima i minuti di GitHub pesano più dei modelli.** Tagli decisi dalla redazione: (1) un motore per
ricerca con il secondo come complemento (sulle 238 ricerche del laboratorio fatte con entrambi: 425 contributi su 459
con 88 ricerche Tavily invece di 238); (3) ricerche adattive. Restano fuori: prima le vie gratuite (le lacune degli
strumenti gratuiti sono sistematiche), minuti di GitHub e due livelli di profondità (per il futuro). Aprire tutti i
risultati dei motori costa circa 2,5-3 $ in più per un nodo approfondito e 4-5 $ al mese per un nodo quotidiano. La
via d'uscita dai costi delle API è l'autonomia per tema (6.10). Le stime si rifanno con i costi misurati nel bilancio.

## 9. Che cosa dicono le misure

- **Il giudizio rende**: costa poco e trova molto più della ricerca a mano; circa 7 contributi su 10 sono davvero utili
  al nodo (campione del 9 novembre); la fascia copertura non è rumore.
- **Seguire le fonti** (link, documenti citati, persone chiave) è il passo che rende di più; i giri di catena portano
  contributi a lungo (Nord Stream 11 giri, il laboratorio 11 giri senza saturare).
- **Nord Stream** (12-15 novembre, senza Wikipedia, 93 affermazioni della voce inglese): il nodo seguito a mano ne copre
  75, quello nato dalla sola domanda 72 dopo i documenti citati, il dossier di un modello avanzato 52.
- **Il laboratorio `ia-matematica`** (27-28 novembre, 127 affermazioni di cinque voci): 56 sostenute, 35 in parte, 34
  assenti, 2 contraddette; le assenze stanno in testate chiuse ai programmi e nella storia prima del 2026.
- **Motori**: sulle stesse ricerche Exa trova più contributi di Tavily, ma Tavily ne aggiunge di suoi sparsi su ogni
  tipo di ricerca (sul laboratorio: Exa solo 365, Tavily solo 199, insieme 459); il complemento tiene il 93% con il 37%
  delle ricerche Tavily.
- **Perché l'architettura di Nord Stream era usata a metà nei nodi successivi** (scoperto il 27-28 novembre): la ricerca dei documenti
  citati si fermava in ogni catena dal 26 novembre per un riferimento scritto male (`body_links._words`, corretto) e
  la sua ricerca web passava solo da Brave, senza credito (ora Exa); i giri si fermavano a tre, lontani dal pieno; le
  ricerche erano quasi tutte in inglese; il giudice scartava le opinioni competenti; le voci social fallivano su un
  nodo nuovo. Nessuno se n'era accorto: ora ogni catena e ogni aggiornamento finiscono con un **bilancio per via**
  (`tools/chain_audit.py`, `bilancio.json`, avvisi nel workflow).
- **Dove si perde ancora**: a monte (le ricerche non arrivano a certi archivi, soprattutto non inglesi), nell'accesso
  (403, robots.txt, riserve TDM), nella lingua delle ricerche; le sintesi del modello possono rovesciare un esito anche
  quando la frase citata è vera (per questo in chat Claude rilegge le fonti).

## 10. Da fare

L'elenco unico di Ubik. Aggiornato il 28 novembre.

**In corso**
- I tre giri del 28 sera sul laboratorio, con `tutti` e la via `home`: leggere il bilancio (contributi in più, quota
  solo API, ricerche per motore, costo, minuti) e tirare le somme.
- L'aggiornamento quotidiano del laboratorio (5:17 UTC): verificare ogni giorno che parta e che il bilancio sia pulito.

**Da fare, acquisizione**
1. Vincolo sulle lingue nel pianificatore (quote di ricerche non inglesi secondo le lingue del nodo).
2. Le parti come ancore: i canali ufficiali delle istituzioni del campo seguiti ogni giorno.
3. Termini GitHub ricavati da persone e progetti chiave.
4. Controllo di credibilità di autori e siti (il caso Nielsen; aggregatori nelle card a latere).
5. Le reazioni nominate dalle testate chiuse ai programmi: cercarle in fonti leggibili (comunicati, blog degli autori,
   agenzie); la storia prima del 2026 come sotto-domanda del laboratorio.
6. Misurare nel bilancio i minuti di GitHub e il costo di ogni passo (Exa, Tavily, OpenRouter).
7. Leggere i termini di Exa sulla conservazione dei risultati.

**Da fare, registro unico e temi**
8. I raccoglitori sul registro unico, uno alla volta: siti, poi autori e canali, poi i topic delle Matrici.
9. Un tema per le 374 fonti seguite che non ne hanno; per ogni nodo nuovo, il suo tema.
10. Con la redazione, a parte: come si definiscono i temi (più specifici o più generici, come e quando nascono).

**Da fare, nodi e sito**
11. Con la redazione: che cosa entra nel testo di un modulo e che cosa resta a latere.
12. Il formato a moduli in tre parti sugli altri nodi, quando la redazione lo considera pronto; l'accorpamento dei
    moduli della delega (rinviato).
13. Il controllo di aderenza frase per frase anche per il testo scritto in chat.
14. Un nodo nuovo con la strada del laboratorio, misurato contro Wikipedia con i costi.
15. Il modello dei dati del sito e un prototipo in sola lettura (`docs/modello-dati.md`).
16. Lo studio sul linguaggio (banco di titoli e sintesi con le scelte della redazione) e sui criteri di scelta dei nodi.

**Da discutere con la redazione**
- La spesa: il tetto dei modelli nell'ambito IA (20 $) superato a novembre (46,65 $); la spesa complessiva del mese.
- Le proposte di nodo dalle Matrici, ferme in attesa dei criteri di scelta.

**Annotati per dopo**: la visibilità e la parte gratuita del sito, il diritto degli editori sugli estratti prima del
lancio, gli originali a pagamento, le newsletter per le fonti bloccate, Common Crawl, Wikidata, Substack, un modello
locale per la prima scrematura, il runner sul computer della redazione.

**Decisioni recenti** (le precedenti nell'appendice B e nella storia del repository)
- 28 novembre: autonomia per tema e registro unico; soglia del 10% per tre giri; i temi di Claude per ora; aprire tutti
  i risultati delle API (non si possono conservare); un motore per ricerca più il complemento; ricerche adattive;
  Tavily sul piano mensile, Exa ricaricato; il nodo della matematica riscritto in chat con card per voci e contributi.
- 27-28 novembre: priorità all'acquisizione con il laboratorio; confronto solo con Wikipedia; aggiornamento quotidiano
  dei nodi d'attualità; in chat la ricerca resta alla pipeline.
- 26 novembre: i nodi scritti in chat da Claude con la redazione come strada principale; la visione del sito (0.1).
- 23-26 novembre: il nodo a moduli.
- 14-15 novembre: delega a Claude sulle fonti; ciclo automatico e calendario acceso.
- 13 novembre: fonti approvate per criterio, in automatico; Exa e Tavily al posto di Brave.

## 11. Come si lancia un'esecuzione

Scrivere una riga nel file di richiesta (un commento sotto, senza parole che siano anche opzioni) e spingerla su
`main` di `ubik-corpus`:

| File | Esempio e opzioni |
| --- | --- |
| `runs/catena.request` | `nodes=ia-matematica rounds=3 tutti engines=exa,tavily q=30 k=220 budget=1.2 min=5 routes=brave,web,…`; `bootstrap` (nodo dalla sola domanda, `runs/domande/NODO.txt`), `subq=`, `first=` (budget del primo giudizio), `refs=`, `find=`, `refweb=`, `refs_first`, `social_voices`, `replay=A:B`; la via `home` si aggiunge da sola |
| `runs/settimana.request` | l'aggiornamento a mano; `quotidiano nodes=…` per i nodi quotidiani |
| `runs/week-refs.request` | `nodes=` (documenti delle fonti dei nodi), `claims=NODO bench=NODO wikiq=en:A\|en:B fisse=PATH` (misura contro Wikipedia), `textbench=`, `web=`, `budget=` |
| `runs/judge.request` | `moduli=NODO` (scrittura dalla pipeline), `nuclei_auto`, `con_stime`, `lacune`, `bench=`, `resoconto=`, `saldo_openrouter` |
| `runs/sites.request` | `archive=NODI` (archivio delle pagine buone) |
| `runs/daily.request` | le Matrici a mano: `version=5 label=… tiers=… notes=…` |
| `runs/light.request` | la bozza di un nodo nella forma precedente (`forma=descrittiva`) |
| `runs/segnalazioni/NOME.txt` | un testo segnalato dalla redazione: i suoi riferimenti, nel corpus e fuori |

Dopo un'esecuzione che stampa risultati di ricerca: leggerli e cancellare il log (0.3).

## Appendice A. Costi per voce, misure e indicazioni (8-15 novembre)

Le tabelle e le misure di metà novembre, conservate perché spiegano le scelte di oggi. Dove dicono Brave come motore,
o l'aggiornamento solo settimanale, valgono per quel momento (sezioni 6 e 8 per lo stato attuale).

### A.1 Costi per voce (metà novembre)

| Voce | Costo | Cresce con |
| --- | --- | --- |
| Raccolta, pagine citate, bacino, scout, primo livello | Zero (Actions gratuite) | — |
| GNews | 49,99 euro al mese | Fisso |
| Brave | Accantonato il 13 novembre: niente più credito gratuito (5 dollari ogni 1.000 ricerche, con l'obbligo di citarlo) | — |
| Exa (motore principale dal 12 novembre) | Da verificare nel pannello: il listino dice 7 dollari ogni 1.000 ricerche con 10 risultati più 1 per ogni risultato oltre il decimo (17 con i nostri 20); il consumo osservato sembrava molto più basso. I risultati dall'11° al 20° portano circa il 30% dei contributi | Ricerche dei nodi |
| Tavily (secondo motore) | Gratuito fino a 1.000 crediti al mese (il piano della redazione ne dà 1.500; tetto nostro 1.450), poi 8 dollari ogni 1.000; dal 28 novembre solo come complemento di Exa (sezione 0.4) | Ricerche dei nodi |
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

### A.2 Che cosa dicono le misure (8-9 novembre)

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

### A.3 Il banco di prova di Nord Stream (12-15 novembre)

Un nodo costruito da zero senza Wikipedia, misurato sulle 93 affermazioni fisse della voce inglese e confrontato con un
dossier scritto da un modello avanzato (Fable) con le sue ricerche. Con la misura alla pari (parole chiave nelle lingue
del nodo, corretta il 13 novembre): delle 93 affermazioni di Wikipedia il nodo ne copre 69, Fable 52, almeno uno dei due
74; delle 90 affermazioni di Fable il nodo ne copre 70. Le assenze vere stavano nei primi mesi del caso, nelle udienze di
Amburgo e nelle conseguenze: i doveri nuovi della catena (6.7) le hanno colmate in buona parte in un giro (24 contributi,
quasi tutti lì). Sui motori, sulle stesse ricerche: Exa 313 contributi tra i risultati (201 solo suoi), Tavily 176 (64).
**La prova pulita** (15 novembre): lo stesso caso avviato dalla sola domanda («Chi ha fatto saltare i gasdotti…»), con il
modello che scrive sotto-domande, lingue e prime ricerche, senza le fonti del nodo fatto a mano e senza Wikipedia;
quattro giri di catena, solo Exa. Risultato: 190 documenti (il nodo fatto a mano 602, in 11 giri); delle 93 affermazioni
di Wikipedia ne copre 54 (a mano 69, Fable 52, almeno uno dei due 68); delle 90 di Fable 62 (a mano 70). Le due versioni
coincidono su 53 affermazioni; quelle che solo il nodo a mano ha sono le dichiarazioni di parte (Cremlino, Zelens'kyj,
Casa Bianca su Hersh), le indagini e gli arresti in Germania e Polonia, i dettagli tecnici dei crateri e delle cariche,
l'ONU. Costo: 0,62 dollari la catena, 0,70 le due misure. In sostanza: un nodo nato da solo arriva in quattro giri al
livello del dossier di Fable; servono più giri, o una catena che chieda esplicitamente le posizioni delle parti, per
arrivare al nodo seguito a mano. Mancava la strada Telegram (l'avvio non scriveva le ricerche per Telegram): aggiunta.
Due giri in più con i doveri nuovi della catena (sentire ogni parte con le sue parole; non ricercare due volte invano lo
stesso documento) e con il piano che riprova quando riscrive ricerche già fatte (al quinto giro su 59 proposte 30 erano
ripetute: per questo le ricerche calavano da 30 a 4): 247 documenti, Wikipedia 57 su 93 (prima 54), Fable 64 su 90
(prima 62), circa 0,25 dollari. Restano fuori soprattutto le indagini e gli arresti in Germania e Polonia, le
dichiarazioni di Kyiv e della Casa Bianca, i dettagli tecnici.
Due giri che seguono le fonti del nodo (i link nei loro testi, strada `fonti`; i documenti che descrivono come prova,
`node_refs.py` dopo ogni giro, strada `riferimenti`, e quelli non trovati passati al piano): 314 documenti, circa 0,55
dollari. Poi la misura corretta: le parole delle affermazioni ora anche nelle lingue dei nodi (tedesco, svedese, danese,
polacco, russo, ucraino), le stesse per i due nodi, perché fatti che il nodo aveva in pagine tedesche o svedesi venivano
contati assenti. Con la misura corretta: nodo a mano 75 affermazioni di Wikipedia su 93, nodo nato dalla sola domanda
68 (Fable 52). La distanza scende da 15 a 7; ognuno ha affermazioni che l'altro non ha (il nodo a mano 14, quello dalla
domanda 7). Il passaggio sui documenti citati ha elencato circa 1.000 riferimenti ma ne ha cercati pochi (budget speso
nella lettura). Separati i due budget (lettura e ricerca, i documenti decisivi per primi) e rifatto: dei 1.306
riferimenti 388 erano già nel nodo, 241 trovati e confermati (149 passati al giudice nel giro dopo), 642 non trovati
e passati al piano; un giro solo ha portato 65 contributi. Il nodo nato dalla sola domanda arriva a 72 affermazioni di
Wikipedia su 93 (il nodo fatto a mano 75), circa 1,15 dollari in tutto per la prova. Seguire le fonti è il passo che ha
reso di più: da adottare nell'aggiornamento settimanale.

### A.4 Giudizio e indicazioni (8-15 novembre)

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

## Appendice B. Diario dal 9 al 28 novembre

Le voci del diario come erano nella sezione 10 prima della riscrittura del 28 novembre (le cose da fare aggiornate
sono nella sezione 10). Contengono le indicazioni della redazione sulla forma dei nodi, le procedure provate, le
misure giro per giro.

- *Su che cosa si lavora: il nodo come studio.* La redazione vuole nodi che emergano dal dibattito tra i più
  competenti di un ambito e che diano risultati paragonabili a una ricerca originale, scegliendo le questioni dove Ubik
  fa la differenza. Tre domande proposte: per molti matematici la ricerca non ha più senso? I modelli evoluti possono
  dirsi coscienti? La bolla dell'IA è destinata a scoppiare? Si è partiti dalla bolla (`ubik-corpus/reports/nodi/bolla-ia/`),
  con il massimo di automatismo.
- *Che cosa ha detto la redazione sulla forma* (in ordine): le etichette «accertato/conteso» sono giudizi del modello,
  meglio una forma descrittiva che dia il peso di documenti e fonti, con un giudizio solo in casi limitati di forte
  evidenza; i resoconti lunghi del modello forte (A/B/C) troppo lunghi, fitti di dati non essenziali e poco
  aggiornabili; quelli brevi ancora no; il prototipo a nove nuclei in tabelle «troppe tabelle»; la direzione giusta è
  quella dei **moduli** («matrici di nodo»): ogni nucleo un paragrafo discorsivo con le fonti dentro, la sintesi che
  emerge dalla somma delle parti, tabelle standardizzate con una grafica propria, una modularità trasversale con le
  Matrici. Il prototipo a moduli (24 novembre) «è la base giusta»: piacciono i numeri delle note colorati per tipo di
  fonte (potrebbero diventare punti di discussione o di modifica della comunità: ipotesi), l'eredità dei vecchi nodi
  dell'esploratore («Da notare», «Manca», l'interesse delle fonti); la grafica rischia di essere un formato che Claude
  propone di default. Indicazione del 24 sera: testo più divulgativo ma non didascalico (riferimento Wikipedia senza
  l'intenzione enciclopedica), ogni nucleo un resoconto esaustivo, i dati in sequenza presentati con una formula di
  confronto non dispersiva.
- *Il prototipo a moduli.* `ubik-corpus/reports/nodi/bolla-ia/prototipo-moduli.html` (scritto a mano da Claude dal
  materiale della pipeline; pubblicato anche come artefatto «Nodo bolla AI»). Ogni modulo: sotto-domanda, tesi in
  grassetto (le tesi in fila fanno la sintesi d'apertura), paragrafo con note numerate colorate per tipo di fonte che
  si aprono su una scheda (chi, tipo, interesse, che cosa dice, passaggio verificato, link), striscia della composizione
  delle fonti per tipo, «Da notare», «Manca», Matrici collegate; in apertura la mappa delle nove strisce; in fondo
  previsioni attribuite, metodo, conflitto d'interessi. Accanto alla pagina: `moduli-strisce.json` (composizione
  delle fonti per nucleo) e `moduli-materiale.txt` (il materiale verificato per nucleo da cui sono scritti i paragrafi).
- *Fatto il 24 sera.* (1) La bolla con le vie social che aveva Nord Stream (`runs/catena.request` con `routes=` e
  `social_voices`, nuovi il 24): 26 voci (23 Bluesky, 3 Mastodon, 0 Telegram; 12 dello stesso autore, Ed Zitron, contate
  come una voce), poi due giri su Bluesky, Hacker News, OpenAlex, link segnalati e fonti delle fonti: 440 pagine
  giudicate, contributi da 386 a 442 (Bluesky 11 su 25 giudicate, OpenAlex 21, snowball 44), meno di 0,10 $ in tutto.
  Il primo lancio si era fermato perché il giudizio stimato (0,30) superava il tetto (0,25): con molti candidati il
  tetto va alzato. (2) Seconda versione dei moduli, sullo stesso file e artefatto: testo divulgativo (i termini tecnici
  spiegati nella frase), resoconti più completi, un riquadro «a confronto» per i dati in serie (barre sulla stessa
  scala, periodo e fonte riga per riga, valori negativi e intervalli), le voci social separate dalle fonti («Nel
  dibattito»), le previsioni divise per posizione. Le strisce ora contano le fonti per parole chiave
  (`ubik-corpus/.design/proto/material.py`, locale).
- *25 novembre, notte: i moduli scritti dalla pipeline* (`tools/node_modules.py`, modo `moduli=NODO models=…
  [nuclei=…]` di `runs/judge.request`; nuclei in `reports/nodi/NODO/moduli-nuclei.json`). Per ogni nucleo il codice
  sceglie fino a 24 contributi che lo toccano (documenti e istituzioni prima) e le voci social (al massimo due post per
  autore); il modello scrive tesi, paragrafi con le fonti dentro, un riquadro di confronto, «Da notare», «Manca», voci;
  il codice controlla ancore e numeri. Indicazioni della redazione nel prompt: un pizzico più divulgativo, un po' di
  contesto per ogni nucleo. Prima prova sulla bolla: DeepSeek 0,008 $ (121 numeri, 4 non trovati nelle fonti citate, uno
  attribuito alla società sbagliata), Sonnet 0,59 $ (123, 3), Opus 1,16 $ (87, 0; il più attento alla provenienza delle
  cifre). DeepSeek va chiamato senza ragionamento e con risposta JSON (prima tornava vuoto); Opus ha ricevuto 402 da
  OpenRouter su due moduli e li ha scritti al secondo lancio. Le quattro versioni (a mano, aggiornata con più contesto, e
  i tre modelli) sono alla cieca in `reports/nodi/bolla-ia/moduli-cieco/`, la chiave in `moduli-auto/chiave-cieca.json`,
  in attesa del giudizio della redazione. Se nessun modello soddisfa: integrare un modello forte nella pipeline con un
  flusso stabile e dedicato, sostenibile se i nodi non sono troppi (indicazione della redazione). Idea annotata, da non
  sviluppare ora: ogni nucleo somiglia a una Matrice e potrebbe avere una sua indipendenza nel feed.
- *25 novembre, mattina: le stime ripulite.* La redazione ha notato che i moduli mettono insieme cifre che misurano
  cose diverse, per frammentarietà e parzialità delle fonti; mia classifica dichiarata in conflitto d'interessi: Opus,
  Sonnet, la versione a mano, DeepSeek (che scrive che le stime «convergono»). Nuovo passaggio `tools/node_estimates.py`
  (modo `con_stime` di `runs/judge.request`): tutte le pagine del nucleo, senza il tetto di 24 fonti, e gli originali
  elencati in `reports/nodi/NODO/originali-NUCLEO.txt` (per la bolla: Sequoia, Bain, J.P. Morgan, Apollo, Damodaran;
  Gartner risponde 403 e non si aggira), ogni stima in schede uguali (chi la fa, valore, che cosa misura, ambito,
  orizzonte, rendimento, originale o ripresa, frase esatta), tenuta solo se la frase è nella pagina e il numero nella
  frase, riunita per autore; il riquadro lo costruisce il codice con le sole stime annue di settore e di gruppo; il
  «calcolo di Ubik» applica il rapporto di un autore al capitale indicato da un altro. Sul nucleo dei ricavi necessari:
  51 pagine, 162 stime verificate, 0,014 $; il testo di Sonnet ora è ordinato per domanda (chi deve incassare, entro
  quando, con quale rendimento) e misura la distanza dai ricavi di oggi (`moduli-cieco/necessari-stime-ripulite.html`).
  Da fare: estrazione con i campi in italiano, il calcolo con rapporti da studi (Wachter) più che da analisi, poi gli
  altri nuclei. Regola nel prompt: mai «trilioni».
- *25 novembre, il metodo reso strutturale e il nodo intero rifatto.* `tools/node_estimates.py` per ogni nucleo: uno
  schema delle grandezze da confrontare (modello forte), le cifre di tutte le pagine del nucleo estratte contro lo schema
  (modello economico, verificate dal codice), una ricerca per ogni autore noto solo di seconda mano sul suo stesso sito
  (Exa; trovate per esempio le pagine di Goldman Sachs; Gartner e il Substack di GeometricInvestor rispondono 403 e si
  lasciano), il calcolo di Ubik solo da un rapporto vero (tra 0 e 5 dollari per dollaro). Nel riquadro il modello
  sceglie le righe tra le cifre verificate e il codice prende i valori, scarta le righe di un'altra grandezza e calcola
  la quota coperta (barra chiara: quanto servirebbe; scura: quanto c'è con lo stesso ambito; accanto le due cifre e la
  percentuale). Costi del nodo: estrazione 0,45 $ (2.112 pagine lette in nove nuclei, 1.808 cifre), scrittura Sonnet
  1,08 $, Opus 2,19 $; 6 moduli su 18 tagliati a 5.000 token, ora 9.000 e tre tentativi. Pagine:
  `moduli-cieco/nodo-opus.html`, `nodo-sonnet.html`. Da fare: i nuclei e le loro parole scelti dalla pipeline (oggi
  sono quelli scritti a mano), le grandezze che si ripetono tra nuclei (i ricavi necessari compaiono anche in chip,
  adozione, stabilità), i campi in italiano, la riga «Manca» che diventa una ricerca mirata, l'aggiornamento per
  impronta dei soli moduli con fonti nuove.
- *26 novembre, notte: il nodo sulla delega della conoscenza* (proposto dalla redazione; `runs/domande/delega-conoscenza.txt`).
  Quattro catene su tutte le vie; 225 pagine buone, quasi tutte studi; 25 voci social. Correzioni lungo la strada:
  `q=` letto da solo (con `subq=5` i giri pianificavano 5 ricerche invece di 30), caratteri surrogati dei PDF puliti
  prima della scrittura (riferimenti e archivio fallivano), il pianificatore salta i file vuoti. Nuovi passaggi:
  `tools/node_nuclei.py` (i nuclei li sceglie la pipeline: 9, tutti tenuti), lo schema di ogni nucleo esclude le
  grandezze degli altri, `tools/node_gaps.py` (la riga «Manca» diventa ricerca del giro successivo, modo `lacune`).
  SEC EDGAR: il codice usa il segreto `SEC_USER_AGENT` (da creare dalla redazione in GitHub, Settings → Secrets and
  variables → Actions); senza, salta EDGAR e lo annota. **Esauriti:** il credito OpenRouter (60 $ caricati, 59,56 usati;
  402 dopo il primo modulo), il credito Exa (402) e il tetto mensile di Tavily: le catene passano da Brave
  (`engines=brave`). Per questo, e come prova dell'idea della redazione, gli altri otto moduli li ha scritti Claude in
  chat nello stesso formato, controllati dal codice della pipeline (`reports/nodi/delega-conoscenza/chat/`, pagina
  `nodo.html`).
- *27 novembre: le opinioni argomentate sulla delega della conoscenza.* Delle 221 fonti del nodo una sola era
  un'opinione: le vie accademiche (OpenAlex, citazioni a catena, riferimenti) erano le sole attive, i motori web senza
  credito. Claude ha scritto 15 ricerche su saggi, interviste ed editoriali di persone competenti
  (`ricerche-manca.json`); con le 15 del pianificatore, le stesse 30 ricerche sono state fatte prima su Exa poi su
  Tavily (`replay=110:140`, giudice solo sulle pagine nuove): Exa 74 contributi nuovi (7 opinioni, 30 analisi), Tavily
  34 in più oltre a Exa (2 opinioni, 15 analisi, forte sulla matematica), 9 trovati da entrambi; giudice 0,11 $.
  Errori lungo la strada: il giro 8 non aveva interrogato nessun motore perché `routes=` escludeva la via della ricerca
  web, che nel codice si chiama ancora `brave` (in `routes=` va scritto `brave`); il primo confronto è stato rifiutato
  dal giudice per un tetto troppo basso (`budget=0.18` contro una stima di 0,47). Il tetto di Tavily nel codice era 900
  e fermava Tavily con credito residuo. EDGAR risponde dopo aver tolto gli a capo dal segreto (`InvalidHeader`).
  Fatto lo stesso giorno: in `tools/node_modules.py` un terzo delle fonti di ogni nucleo va ad analisi e opinioni
  (prima le opinioni finivano in «altro», ultime). Seconda versione del nodo scritta in chat
  (`reports/nodi/delega-conoscenza/chat/moduli2.py`, `build2.py`, `gen_page2.py`): ogni modulo si apre con «Le
  posizioni», chi sostiene che cosa e con quali argomenti, e i dati vengono dopo, ridotti; tre riquadri invece di otto.
  Le fonti nuove hanno passaggi copiati dalla pagina archiviata e ritrovati dal codice parola per parola; escluse le
  pagine di dubbia autenticità (un'intervista dichiarata «ricostruzione editoriale»). Da fare: filtrare le copie e i
  siti di riassunti; portare il blocco delle posizioni nella pipeline automatica (`PROMPT` di `node_modules.py`).
- *27 novembre: il nodo sull'IA e la matematica* (chiesto dalla redazione, nato dal modulo sulla matematica del nodo
  sulla delega; `runs/domande/ia-matematica.txt`, catena con tutte le vie, Exa e Tavily, voci social). Prima stesura
  scritta in chat dalle fonti del nodo sulla delega (`reports/nodi/ia-matematica/chat/`): sei moduli nel formato chiesto
  dalla redazione, **contesto** (spiega che cosa è successo, il modello ha più iniziativa), **fatti** (ancorati a studi
  e fonti primarie), **dibattito** (le posizioni raccontate e, dentro ciascuna, le citazioni letterali delle voci, saggi
  o social, al posto del blocco separato «Nel dibattito»). Ogni passaggio e ogni citazione ritrovati parola per parola.
  Proposta per il nodo sulla delega, da decidere con la redazione: da nove a sei moduli (apprendimento e competenze;
  lavoro; matematica e verifica, breve, con rimando al nodo dedicato; scienza fatta dagli agenti; dipendenza da pochi
  sistemi; previsioni), con i disaccordi distribuiti nei dibattiti di ciascun modulo.
- *27 novembre, pomeriggio: perché l'acquisizione non trovava da sola ciò che la redazione ha trovato per caso.* Tre
  cause misurate sul nodo sull'IA e la matematica. (1) **Il giudice scartava le opinioni competenti**: il saggio di
  Tao e colleghi «Egoless Mathematics» aveva 4,5 punti (sotto 5) perché ogni studio prende un punto per il tipo e
  un'opinione zero; ora analisi e opinioni pesano 0,8 e `reband` ricalcola i punteggi (9 e 8 contributi in più, nessuno
  perso). (2) **Le voci social del primo giro sono fallite** perché il nodo non aveva ancora la scheda: la catena la crea
  prima degli strumenti delle voci. (3) **Le notizie in divenire**: la catena pianifica dalla domanda del nodo, non dagli
  ultimi giorni; il caso Riemann (20-27 novembre) è entrato solo con le ricerche scritte da Claude
  (`ricerche-manca.json`). Da fare: (a) un giro di aggiornamento periodico per i nodi con un caso aperto, che cerchi
  per nomi e fatti degli ultimi giorni; (b) seguire i canali delle persone chiave del nodo (blog, Mastodon, GitHub),
  con `author_channels.py`; (c) un controllo di credibilità degli autori (affiliazione verificabile su OpenAlex o ORCID,
  istituti di una sola persona, chi dichiara di aver risolto più problemi del millennio): un articolo di J. L. Nielsen,
  che la redazione segnala come non attendibile, era entrato tra i contributi del nodo sulla delega; (d) una sezione
  «Letture» nei nodi per i saggi lunghi, che il dibattito può solo riassumere.
- *27 novembre, sera: il laboratorio dell'acquisizione (nodo ia-matematica).* Decisione della redazione: prima
  l'architettura di acquisizione ed estrazione, poi il formato (accorpamenti e formato nuovo rinviati); i nodi
  d'attualità aggiornati ogni giorno; obiettivo, come su Nord Stream, pari o meglio di Wikipedia e di un modello
  avanzato sullo stesso argomento, in modo strutturale, con i costi stimati.
  **Misura di partenza** (`wiki_bench.py` ora legge più voci: `wikiq=en:A|en:B|…`; cinque voci inglesi: Mathematics
  and artificial intelligence, Alpöge's proof of the Riemann hypothesis, List of mathematical discoveries made with
  artificial intelligence, Navier–Stokes priority controversy, Millennium Prize Problems). Documenti: 244 riferimenti
  distinti, 29 anche nostri; noi 297 documenti, 273 assenti dalle voci. Affermazioni: delle 127 delle voci il nodo ne
  sostiene 54, in parte 31, ne contraddice 4, non ne copre 37; delle nostre 150 scoperte 123 non sono nelle voci.
  Le assenze: le reazioni nominate alla disputa su Navier-Stokes (Clay Institute, AMS, Sarnak, Córdoba, Yau,
  matematici tedeschi), quelle su Riemann (Saha, Marcus, LeCun, Nuccio, Bloom), la storia prima del 2026 (AlphaTensor,
  nodi, cap set, AlphaEvolve); tra i riferimenti mancati GitHub 21, X 15 (non raggiungibile), arXiv 15, Clay 11.
  **Fatto**: (1) le persone chiave (`tools/node_people.py`, `reports/nodi/NODO/persone.json`): un modello economico
  legge ogni pagina archiviata e ne elenca le persone con un ruolo; chi è citato da due fonti o ne ha scritte due è una
  persona chiave, e il pianificatore cerca le sue parole più recenti, anche sui suoi canali (prima lettura: 248
  pagine, 188 persone, Tao 54 fonti, Alpöge 53, Buzzard 32; 0,07 $); nella catena prima di ogni giro, con l'archivio
  dopo ogni giro; (2) il dovere del pianificatore di sentire le istituzioni del campo e le reazioni nominate, nelle
  lingue della sua stampa; (3) l'**aggiornamento quotidiano** (`settimana.yml`, ogni giorno alle 05:17 UTC; nodi in
  `registry/nodi-attivi.json` → `quotidiani`, impostazioni in `quotidiano`): un giro, Tavily solo sugli ultimi due
  giorni (`SEARCH_SINCE`, `start_date`), Exa senza finestra per le pagine senza data, le vie del nodo. Prima prova
  ferma al pianificatore: credito OpenRouter esaurito (HTTP 402).
  **Da fare**: le parti come ancore (i canali ufficiali delle istituzioni del nodo seguiti ogni giorno); i termini
  GitHub dalle persone e dai progetti chiave; il controllo di credibilità degli autori; il confronto con un dossier
  scritto alla cieca da un modello avanzato in un'altra chat (`textbench=`); poi la misura ripetuta dopo una settimana
  di aggiornamenti.
  **Stima dei costi per nodo quotidiano** (dai consumi misurati): pianificazione 0,002 $ a giro; persone 0,07 $ la
  prima volta, poi meno di 0,01 al giorno; giudizio circa 0,0003 $ a pagina (120 candidati, 0,04); riferimenti fino a
  0,07; voci circa 0,03; Exa 20 ricerche, circa 0,06 $; Tavily 20 crediti (gratuiti fino a 1.500 al mese, quindi al
  massimo due nodi quotidiani senza pagare). In tutto circa 0,2 $ al giorno, 6 $ al mese per nodo; la misura contro
  Wikipedia 0,06 $; il dossier del modello avanzato, nell'abbonamento della redazione, nulla.
- *28 novembre, tarda mattina: autonomia per tema e registro unico.* Domanda della redazione: le fonti raggiunte dalle
  API sono tutte acquisite? No: 572 pagine giudicate su 5.474 restituite, le liste non conservate per i termini d'uso.
  Strategia decisa e primo codice nella sezione 0.4. Da fare: confermare temi e soglia; i raccoglitori sul registro unico;
  i termini di Exa; le card dei siti poco credibili.
- *28 novembre, mattina: il nodo della matematica riscritto e la misura.* Sezione 0.4. Da fare: le reazioni nominate
  dalle testate chiuse ai programmi arrivano solo da rassegne (Post-Cutoff): cercare le stesse parole in fonti
  leggibili (comunicati delle istituzioni, blog degli autori, agenzie); la storia prima del 2026 come sotto-domanda.
- *28 novembre, mattina: i costi a regime e due tagli.* Domanda della redazione: quanto costeranno (a) un nodo da
  zero con la pipeline, (b) un nodo da zero con la ricerca della pipeline e la scrittura in chat, (c) l'aggiornamento
  quotidiano; correzioni della redazione alle prime stime: i minuti di GitHub vanno contati, il runner proprio non è
  gratuito, nel nodo in chat la ricerca resta alla pipeline, a 2-3 nodi al giorno le quote gratuite non contano.
  Stime e tagli nella sezione 0.4 («Costi»); fatti i tagli 1 (complemento tra i motori, misurato sui dati del
  laboratorio) e 3 (ricerche adattive). Scoperto: Exa senza credito dalla notte, senza allarme (corretto il bilancio).
  La misura contro Wikipedia, bloccata alle 03:20 dal limite di GitHub, rilanciata a mano dopo la ricarica.
- *Fare un nodo in chat (idea della redazione, 26 novembre: usare l'abbonamento per i passaggi di giudizio).* La
  pipeline fa ricerca, giudizio, nuclei, estrazione delle cifre e controlli (pochi decimi di dollaro); in chat si
  scrivono i moduli. Procedura provata: (1) catena con `bootstrap` da `runs/domande/NODO.txt`; (2) `runs/judge.request`
  con `moduli=NODO nuclei_auto con_stime lacune` (o il solo modello economico); (3) in chat, per ogni nucleo, il
  materiale compatto (`reports/nodi/delega-conoscenza/chat/build.py` mostra come si assemblano fonti S, cifre E e
  voci V come fa `tools/node_modules.py`); (4) i moduli in `moduli.py` nel formato della pipeline; (5) `build.py`
  esegue `check()` e `chosen_box()` e scrive `moduli-auto/chat-claude.json`; (6) la pagina e l'artefatto. Da fare: un
  registro dei nodi generato dalla pipeline.
- *Credito OpenRouter (25 novembre).* Era finito (49,70 $ usati su 50; consumo della chiave nel mese 36,79 $); la
  redazione ha ricaricato. Il saldo si legge con `saldo_openrouter` in `runs/judge.request`.
- *Aperto con la redazione.* Un indirizzo email di contatto per lo User-Agent di SEC EDGAR (la via delle istituzioni
  riceve 403 senza), da salvare come segreto; se mettere `bolla-ia` tra i nodi attivi del giro settimanale.

**Fatto di recente**

- 22-24 novembre: **il nodo sulla bolla, dalla domanda allo studio** (`ubik-corpus`):
  - *forma descrittiva* della bozza (`tools/light_node.py`, `forma=descrittiva` in `runs/light.request` o
    `UBIK_FORMA`): punti con citazioni a favore e contro, tipo di fonte, interesse, peso, un giudizio solo per i tipi
    che giudicano; previsioni attribuite, raggruppate per posizione, con l'orizzonte solo se dichiarato; controllo sì/no
    di ogni citazione; un passaggio finale riscrive peso e stato sulle citazioni sopravvissute;
  - *sotto-domande*: a parità di spesa 8 sotto-domande danno 61 affermazioni di Wikipedia su 93 (37 piene), 5 ne
    danno 64 (44): si resta a 3-5 e si investe nel seguire le fonti (`UBIK_SUBQ`, `subq=`);
  - *la data di oggi ai planner* (`node_pick.py`, `entity_rounds.py`): le ricerche dicevano 2024 e 2025;
  - *la via delle istituzioni* (`path_istituzioni` in `tools/scout.py`): ultimi 10-K e 10-Q su SEC EDGAR delle società
    nominate in almeno tre pagine, ricerche ristrette a banche centrali, FMI, BIS, OCSE, uffici statistici e
    autorità; EDGAR risponde 403 senza un contatto nello User-Agent (aperto);
  - *ricerca approfondita* come Nord Stream (quattro giri, prima i documenti citati): pagine giudicate da 470 a 841,
    buone da 233 a 386, documenti primari da 26 a 71, 20 pubblicazioni istituzionali (BIS, FMI, BCE, Banca
    d'Inghilterra, Fed, Banca d'Italia, INSEE, BEA, ESMA, ONS, Commissione); circa 0,12 $ di giudizio. 570 pagine
    archiviate in `corpus/targeted/bolla-ia/`, 359 siti nel registro (353 approvati, 96 con feed raccolto ogni giorno),
    132 autori (19 in prova);
  - *strumenti dello studio*: `tools/figures.py` (cifre nel testo), `tools/node_genealogy.py` (genealogia delle cifre
    chiave: valore esatto più contesto), `tools/node_report.py` (resoconto del modello forte con controllo per codice
    che ogni numero stia nelle fonti citate; versioni A/B/C alla cieca, chiave a parte; forma compatta a blocchi con
    impronta, per aggiornare solo i blocchi le cui fonti cambiano; `resoconto=` in `runs/judge.request`);
  - *elenco di riferimento automatico*: `tools/competence.py` (seguito e citazioni da parte delle voci, citazioni nei
    nodi, OpenAlex, pagine verificate, ruolo dichiarato; l'attenzione a parte; `reports/bacino/competenza-ia.json`);
    da correggere: distinguere esperto, parte e cronista, misurare le relazioni tra voci, il peso di Bluesky;
  - *banco dei modelli* (`tools/model_bench.py`) e fornitore di DeepSeek con ripiego (sopra);
  - *workflow*: quando il rebase fallisce sui registri condivisi, l'ultimo tentativo tiene le righe di `main`
    (23 novembre: una catena aveva perso il nodo per un conflitto).

**Fatto di recente**

- 21 novembre: **bilancio delle fonti in prova dopo due settimane** (attività programmata del 7 novembre;
  `ubik-corpus/reports/fonti/bilancio-prova-2026-11-21.md`, gratuito). 101 fonti dei tre registri in prova: per ciascuna
  raccolti dal 7 novembre, testi, pertinenza all'IA per codice, ingresso nelle Matrici della settimana del 2 novembre
  (l'unica con tutte le fonti), uso nei nodi. Proposte: 20 da promuovere (BBC, Scientific American, Semafor, CNBC,
  Futurism, Pew, Authors Alliance, FAI, Publishing Perspectives, CCIA; i Studiosi dei nodi, arXiv cs.AI e cs.LG; EUR-Lex,
  Press corner, AI Security Institute, Hugging Face, DeepMind, NVIDIA, Google) perché hanno dato contributi ai nodi o
  pezzi alle Matrici; 2 da correggere (Microsoft AI blog senza voci; OpenAI notizie con 1.200 voci e nessun testo); le
  altre 79 in prova. Promuovere il feed conta perché il giornale legge solo gli approvati: nella settimana del 9
  novembre nessuna di queste fonti vi è entrata, anche quando il sito era già approvato in `siti.json`. La misura non
  dice ancora nulla delle testate italiane e dei feed di tutto il sito, arrivati dopo la settimana del 2 novembre. La
  misura di Brave prevista con il bilancio non si ripete: Brave è accantonato dal 13 novembre. In attesa: l'applicazione
  delle promozioni (delega a Claude) e, per misurare le fonti nuove, un giornale di confronto con tutte le fonti su una
  settimana (circa 1 dollaro, decisione della redazione).
- 15 novembre: **giornale della settimana dal 9 novembre** (936 articoli, 23 Matrici, 1,09 dollari: regole 7, data
  center ed energia 9, economia 5, lavoro e diritto d'autore 1 ciascuno) e **prova pulita di Nord Stream** (sezione 8):
  dalla sola domanda, in quattro giri, 54 affermazioni di Wikipedia su 93 (a mano 69, Fable 52). Correzioni: il primo
  giudizio di un nodo nuovo ha un tetto suo (`first=`, 0,50 dollari: il primo lancio era stato rifiutato a 0,37 su
  0,30); un nodo avviato dalla domanda riceve anche le ricerche per Telegram.
- 15 novembre: **quello che si è fatto a mano su Nord Stream, ora per ogni nodo attivo, ogni settimana**. Già
  automatici: la catena con i doveri nuovi (tutta la storia, testo integrale), le strade verso i tribunali UE, Telegram
  e gli articoli segnalati dalle testate, le voci da Bluesky, Mastodon e Telegram con l'altra parte, l'archivio. Aggiunti
  oggi all'aggiornamento settimanale: i documenti su cui poggiano le fonti (`node_refs.py`: sentenze, rapporti, leggi,
  CourtListener, link nel testo) e le novità della settimana nella bozza del nodo (`light_node.py update`). Tetto della
  settimana portato a 4 dollari (massimo teorico 3,5 per quattro nodi a due giri; la prima settimana reale è costata
  0,66). Restano fuori dall'automatico: la misura contro Wikipedia e Fable (è un banco di prova, non serve a ogni
  nodo), la nascita dei nodi nuovi (rinviata ai criteri nuovi di scelta), le decisioni sulle novità (Claude, nelle
  sessioni, per delega) e l'accensione del calendario (redazione).
- 14 novembre: **delega della redazione a Claude**. Le fonti da esaminare sono troppe per la redazione: Claude decide
  in autonomia su fonti, documenti, novità dei nodi, canali e voci, e porta alla redazione solo i casi più dubbi.
  Confermate e registrate nei nodi le 140 decisioni provvisorie di Claude sui documenti (fair use, data center,
  Maidan, coinvolgimento americano, weight space); restano alla redazione le 17 proposte di nodo dalle Matrici, perché
  la scelta dei nodi è rinviata allo studio sui criteri e sul linguaggio. La redazione può ribaltare ogni decisione
  nell'esploratore.
- 14 novembre: **voci più equilibrate, voci da Telegram, novità nei nodi**. (1) Le voci dai social cercano l'altra
  parte: dopo il primo passaggio una chiamata legge le posizioni tenute, nomina le parti non ancora sentite e scrive le
  ricerche brevi per trovarle; i loro post passano dagli stessi filtri, il giudice sa quale parte si cerca (40% del
  budget riservato; le stesse ricerche vanno alla ricerca a testo di Mastodon). Data center: 5 voci nuove da economisti,
  legislatori e proponenti (Hicks, Newsom, Dingell, Samaras, Zandi), prima quasi tutte contrarie. (2) Voci da Telegram
  (`tools/telegram_voices.py`): solo canali approvati di giornalisti, analisti, OSINT e testimoni; testate come fonti,
  istituzioni e canali di Stato come documenti di parte, propaganda fuori; almeno 40 parole, 5.000 visualizzazioni e 50
  reazioni dall'anteprima pubblica. Su Nord Stream ancora nessuna: i due canali adatti non ne parlano. (3) Errore
  corretto: la classificazione dei canali scambiava il paese per un legame di Stato, e le testate russe in esilio o di
  opposizione (Astra, The Insider, Glasnaya, Agentstvo) risultavano media di Stato; ora il legame vale solo per enti
  ufficiali, media di Stato e propaganda statale; 33 canali riclassificati (2 centesimi). (4) Bozze aggiornate con le
  novità da rivedere: data center 40, fair use, uso dei contenuti e Nord Stream 8 ciascuno.
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
    con il bilancio delle fonti in prova del 21 novembre (fatto: `reports/fonti/bilancio-prova-2026-11-21.md`).
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
  articoli nelle Matrici, era da decidere dopo il bilancio di Brave del 21 novembre, che non si è fatto perché Brave è accantonato: resta da decidere se usare Exa per quel passo.
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

**In ordine** (piano di consolidamento deciso il 15 novembre: niente strade nuove, portare quello che c'è alla
forma definitiva e automatica)

1. **Chiudere i sospesi.** Fatto il 15 novembre:
   - decisioni nei nodi: i 23 documenti di Nord Stream decisi (11 dentro: atti della Procura federale, chiusure delle
     indagini svedese e danese, studi sismici e sul metano, sentenza assicurativa di Londra, resoconto ONU; fuori copie,
     articoli, Wikipedia); le 5 affermazioni trovate solo dal nodo nato dalla domanda entrate come novità nel nodo; negli
     altri nodi non restava nulla di aperto;
   - fonti: 5 canali rivisti (2 seguiti, 3 omonimi scartati), 8 azioni sugli autori chiuse con il motivo, l'elenco delle
     istituzioni candidate chiuso (Öko-Institut e SEC approvati come siti); i candidati restanti (90 siti, 420 autori)
     non aspettano una decisione: entrano quando passano il criterio;
   - anagrafe unica delle fonti (`tools/anagrafe.py`, `registry/anagrafe.json`, `reports/fonti/anagrafe.md`): 1.869
     fonti di tutti i registri, una volta ciascuna con uno stato, rifatta ogni giorno con i siti;
   - nodi di prova in archivio (`archivio` in `registry/nodi-attivi.json`): weight space, USAID, il nodo nato dalla
     domanda; nell'esploratore in un gruppo a parte.
   Resta: il rapporto preliminare di Nord Stream AG sui crateri, oggi solo da un sito bielorusso (proposta alla redazione).
2. **Il ciclo automatico completo.** Fatto il 15 novembre, resta il rodaggio:
   - il giornale in calendario ogni lunedì alle 5:23 sulla settimana chiusa (`daily.yml`, solo fonti approvate);
   - nell'aggiornamento del sabato (`settimana.yml`), a ogni giro, i link e i documenti citati dalle fonti (strade
     `fonti` e `riferimenti`, `node_refs.py` con due budget, lettura e ricerca);
   - dopo i giri, per ogni nodo: le novità della settimana (`light_node.py update`), le decisioni automatiche
     (`tools/auto_decide.py`: novità e documenti decisi con i criteri delle decisioni registrate, le dubbie in
     `reports/nodi/NODO/da-decidere.json` per Claude) e l'integrazione nel testo (`tools/integrate.py`: ogni novità
     accettata collocata in un punto, o in un punto nuovo; i documenti accettati tra i documenti cardine; lo stato della
     questione riscritto quando cambia). Prima prova sulla coda: 28 novità collocate, un punto nuovo (moratoria sui data
     center), 95 documenti cardine, quattro stati riscritti, meno di un centesimo;
   - budget per nodo nel registro (`budget_riferimenti_usd`, `budget_ricerca_riferimenti_usd`, `budget_decisioni_usd`,
     `budget_integrazione_usd`); il massimo teorico di quattro nodi a due giri resta sotto il tetto di 4 dollari;
   - l'esploratore ripubblicato ogni lunedì alle 9:41 da un'attività programmata di Claude, dopo il giornale;
   - 15 workflow di esperimenti chiusi in `.github/workflows-archivio/` (ne restano 16).
   - (sera del 15 novembre) le testate seguite per sezione ora anche con il feed di tutto il sito, filtrato con le
     parole dei Topic (`tools/feed_wide.py`, `registry/parole-topic.json`, ogni giorno con i siti; 15 testate su 22,
     mancano The Verge, MIT Technology Review, Politico Europe, New York Times, Financial Times, senza un feed generale
     raggiungibile); il giornale tiene le grandi storie (almeno 10 testate) nel sotto-topic dove almeno un quarto degli
     articoli è principalmente a tema, e mostra negli altri sotto-topic i rimandi alle Matrici che li riguardano;
     un sotto-topic fallito non sovrascrive più quello buono.
   Resta: il rodaggio, cioè un sabato sorvegliato con il ciclo intero, e poi l'accensione del calendario
   (`automatico: true`, decisione della redazione).
3. **L'esploratore nella forma finale.** Fatto il 15 novembre:
   - una sola pagina per ogni nodo, a strati: lo stato della questione; cosa è cambiato nelle ultime due settimane
     (novità collocate, punti nuovi, documenti aggiunti); i punti del contendere con le due parti, su che cosa poggia
     l'esito e, per i nodi approfonditi, la catena di fonti che lo dimostra, sotto il punto; i documenti cardine; le
     voci; i collegamenti con Matrici e nodi; le fonti per approfondire; in fondo, chiuso, il cantiere (novità e documenti
     da decidere, proposte, atti, sotto-domande, scheda di lavoro), aperto solo quando c'è qualcosa da decidere;
   - la profondità è il lavoro fatto sul nodo, non un formato: fair use e Maidan («nodi approfonditi») hanno ora stato e
     punti in testa (per Maidan scritti da Claude dalle sue quattro catene), con le catene agganciate ai punti;
     `build_model.py` unisce la bozza (`light.json`, i punti con `chains`) e le catene; i prototipi in archivio restano
     nella forma di allora;
   - una ricerca testuale su Matrici, nodi e fonti, nel menù;
   - i codici interni delle fonti (S1, S2…) tolti dal testo mostrato.
4. **Lo studio sul linguaggio** (indicazioni della redazione del 13 novembre): un banco di 30 titoli e sintesi reali con
   varianti in registri diversi, le scelte a coppie della redazione salvate, una guida di stile ricavata dalle scelte e
   messa nei prompt; lo stesso metodo per i criteri di scelta dei nodi, sulle 17 proposte delle Matrici.
5. **I costi**, tarati su due settimane vere: il prefiltro del giornale (158 articoli su 936 senza sotto-topic annotati
   lo stesso) e il riuso delle note; il prezzo vero di Exa e la prova 10 contro 20 risultati; i minuti di GitHub (raccolta
   in parallelo e controllo di copertura settimanale già fatti il 15 novembre; resta l'indice del corpus in cache); un
   riepilogo settimanale dei costi.

22 novembre. Dal 20 sera al 22 mattina non è partito nulla: GitHub Actions aveva raggiunto il tetto di spesa di 10 $,
alzato dalla redazione a 20 $. Rilanciati raccolta, siti e aggiornamento settimanale. Lo stesso giorno: Nebius non serve
più DeepSeek V4.1 Flash e ogni chiamata riceveva 404 (anche l'aggiornamento del 21, rimasto vuoto); ora Nebius resta il
primo fornitore e gli altri seguono (`ingestion/ubik_extraction_pilot.py`, `tools/judge_candidates.py`). Prova alla
cieca dei modelli economici sulle decisioni registrate (`tools/model_bench.py`, modo `bench=` di `runs/judge.request`;
`reports/bench/`): su 180 decisioni con 40 esempi DeepSeek V4.1 Flash concorda al 77,6%, Qwen3.8 Flash al 76,2%, Claude
Haiku 5.5 al 70,7% (con 40 dubbie), Gemini 3.1 Flash Lite al 67%; GPT-5 Mini consuma la risposta nel ragionamento. Il
modello resta DeepSeek; la prova sulla scrittura (punto 4) è da fare a parte, giudicata dalla redazione. Avviato il nodo
`bolla-ia` dalla sola domanda (tipo previsione: dati separati dalle previsioni attribuite).

Fuori da questa fase: strade di ricerca nuove, nuovi tipi di fonti, il modello locale, la crescita verso molti topic, il
sito pubblico. Restano annotati per dopo: la visibilità e la parte gratuita, il diritto degli editori sugli estratti
prima del lancio, gli originali a pagamento, le newsletter per le fonti bloccate, Common Crawl, Wikidata, Substack.
