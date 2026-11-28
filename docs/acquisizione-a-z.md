# Ubik dalla A alla Z: raccolta, Matrici, nodi (aggiornato al 28 novembre 2026)

Questo documento descrive il sistema com'è oggi, dall'inizio alla fine, ed è il punto di partenza per chi riprende il
lavoro in una nuova conversazione. È stato riscritto il 28 novembre togliendo i rami abbandonati: il diario completo
delle prove e delle decisioni fino a quel giorno resta nella storia del repository (`git log -p docs/acquisizione-a-z.md`)
e, per il periodo 6-15 novembre, in `docs/history/2026-11-acquisizione-nodi-diario.md`. Gli altri documenti correnti:
`docs/daily-spec.md` (Matrici), `docs/nodi-spec.md` (nodi), `docs/modello-dati.md` (dati del sito, bozza).

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
termini e prime ricerche.

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

**Decisioni recenti** (le precedenti nella storia del repository)
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
