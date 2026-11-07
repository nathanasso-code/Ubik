# Acquisizione per i nodi — metodo (6 novembre 2026)

Il limite principale di ogni nodo è trovare i contributi di qualità. I feed portano solo ciò che le fonti approvate
pubblicano; la ricerca a mano non si replica. Il metodo parte da un'osservazione: i contributi buoni si trovano seguendo
chi cita, risponde e riproduce, più che cercando per argomento.

Strumento: `ubik-corpus/tools/scout.py`, workflow `scout.yml` (su richiesta, `runs/scout.request`). Nessun modello,
solo servizi gratuiti; ogni indirizzo di servizio passa prima per robots.txt, e un servizio che rifiuta o chiede
l'accesso viene saltato e registrato. Le API esterne non sono raggiungibili dal contenitore di lavoro, quindi lo scout
gira su GitHub come la raccolta.

## Punto di partenza: `reports/nodi/<nodo>/scout.json`

| Campo | Cosa contiene |
| --- | --- |
| `anchors` | I documenti d'origine del nodo: il paper, la sentenza, il rapporto (indirizzi) |
| `terms` | I nomi con cui il caso circola, in più lingue |
| `github_terms`, `scholar_terms`, `dois` | Ricerche per repository, letteratura scientifica, citazioni di un DOI |
| `wikipedia` | Lingua e ricerca della voce di Wikipedia sul tema (i suoi riferimenti sono una mappa già fatta) |
| `gap_queries` | Ricerche web mirate, una per lacuna del nodo (una posizione senza fonti, una replica mancante) |
| `known` | Le fonti scelte a mano: servono a misurare il metodo |

## Percorsi

1. **Corpus** (le voci come antenne): gli articoli del corpus privato che citano un'ancora o ne parlano, e i link che
   citano. Un link citato da due fonti diverse è un segnale forte; se le fonti sono voci del registro, più forte.
2. **Hacker News**: discussioni sulle ancore e link nei commenti.
3. **Bluesky**: link condivisi nei post sul caso, con il riconoscimento delle voci che vi scrivono.
4. **GitHub**: repository e issue che citano le ancore, dove stanno le riproduzioni.
5. **OpenAlex e Semantic Scholar**: letteratura sul tema e chi cita i DOI delle ancore.
6. **Wikipedia**: i link esterni delle voci sul tema.
7. **Web**: ricerca Bing (RSS) solo per le lacune dichiarate.

Ogni candidato registra tutti i percorsi che l'hanno trovato e chi lo cita; il punteggio cresce con il numero di
percorsi, di fonti e di voci. Il punteggio ordina, non decide.

## Selezione e raccolta

La selezione dei candidati la fa oggi Claude in conversazione, con criteri espliciti: porta prove o dati propri
(documenti, cifre, riproduzioni)? l'autore è identificabile e competente sul punto? discute la posizione opposta? cita
le fonti primarie? I candidati scelti vanno in `reports/scout/<nodo>/pick.json` e `scout.py fetch` li raccoglie nel
corpus privato con le regole del raccoglitore. Le fonti nuove restano soggette all'approvazione della redazione.

Le segnalazioni della redazione (un testo letto sui social, un documento salvato) entrano come `segnalazione` in
`corpus/targeted/<nodo>/`, con provenienza dichiarata.

## Misura

`scout.py bench NODO` confronta i candidati con le fonti scelte a mano (`known`), escludendo i testi raccolti a mano
per quel nodo. Due numeri: quante fonti scelte a mano il metodo ritrova, e quanti candidati vanno scartati per
ognuno buono.

## Prima prova (6 novembre 2026)

Tre nodi: il 20 febbraio e il fair use, già costruiti a mano (la prova), e il rapporto del MIT sullo spazio dei pesi
(nuovo). Due versioni dello scout; la seconda filtra il rumore (issue di GitHub che non citano l'ancora, font e
servizi delle pagine), abbassa il peso di Wikipedia, registra gli autori, riprova sui limiti di frequenza e aggiunge
il secondo giro di citazioni.

| | 20 febbraio | Fair use | MIT |
| --- | --- | --- | --- |
| Candidati | 748 | 1.423 | 501 |
| Fonti scelte a mano ritrovate (stessa opera, anche a un altro indirizzo) | 3 su 10 | 9 su 22 | 1 su 2 |
| Candidati letti per la selezione | circa 80 | circa 80 | circa 70 |
| Scelti e raccolti | 9 (6 testi salvati) | 8 (4) | 15 (13) |
| Entrati nel nodo | 6 | 4 | 12, più Willison dal corpus e Gilestro dalla segnalazione |

Cosa trova bene:
- documenti primari al posto delle pagine di seconda mano (le sentenze Bartz e Kadrey, il rapporto integrale
  dell'Ufficio del copyright, il rapporto del Consiglio d'Europa), soprattutto attraverso Wikipedia;
- la letteratura accademica (OpenAlex): per il 20 febbraio mostra che 24 dei 25 lavori più pertinenti sono di un solo
  autore, un fatto rilevante per il nodo;
- le riproduzioni indipendenti (GitHub): per il MIT tre repliche, una con lo stesso modello, che cambiano la
  sostanza del nodo;
- i lavori precedenti e le critiche, attraverso le discussioni su Hacker News e i link delle voci (Honnibal dai link
  di Willison, Krentsel da un commento).

Cosa non trova:
- le analisi della settimana su riviste e blog (Risch, StopFake, openDemocracy; le memorie di ottobre 2026 sul fair
  use). Serve un motore di ricerca: Bing vieta in robots.txt l'uso automatico della ricerca, quindi il percorso web è
  rimasto spento;
- Bluesky: la ricerca pubblica ora chiede l'accesso (403);
- Semantic Scholar limita le richieste senza chiave (429).

Rispetto delle regole nella raccolta: CourtListener vieta in robots.txt, TorrentFreak dichiara la riserva TDM,
SSRN, Taylor & Francis e un sito ucraino rifiutano (403). Nessuno è stato aggirato.

Costo: zero (nessun modello, servizi gratuiti, Actions). Tempo: circa tre minuti per nodo per la ricerca; la
selezione, fatta da Claude in conversazione, è la parte lunga.

## Secondo giro: Brave e Bluesky (7 novembre)

Chiave Brave e account Bluesky di Ubik (password per le app) nei segreti di `ubik-corpus`. Bluesky ora cerca con
l'accesso; Brave serve solo per le ricerche sulle lacune (sette per nodo).

| | 20 febbraio | Fair use | MIT |
| --- | --- | --- | --- |
| Fonti scelte a mano ritrovate, per indirizzo | 3 su 10 (prima 1) | 11 su 22 (prima 6) | 1 su 2 |
| Stessa opera anche a un altro indirizzo | 4 su 10 | 14 su 22 | 1 su 2, più Goedecke (la lacuna del 6 novembre) |
| Candidati da Bluesky | 50 | 290 | 93 |
| Candidati da Brave | 85 | 123 | 65 |

Bluesky ha trovato le memorie di ottobre sul fair use (EFF, Wikimedia, Kelly, Authors Alliance) e il testo di
Goedecke; Brave ha trovato Risch, il capitolo di Katchanovski del 2024, la sua critica a SITU, le rassegne delle oltre 50
memorie nella causa contro OpenAI e sei riproduzioni del paper del MIT. Il rumore di Brave è alto: decine di pagine
divulgative scritte per i motori di ricerca.

**Risultati di Brave.** Quelli trovati solo da Brave non entrano nel repository: lo scout li stampa nel registro
dell'esecuzione, la selezione li legge, e dopo la selezione l'esecuzione viene cancellata
(`gh api -X DELETE repos/nathanasso-code/ubik-corpus/actions/runs/<id>`). Restano le pagine scelte e raccolte, con
«trovata con Brave». Costo del giro: 21 ricerche, dentro il credito mensile gratuito.

**Che cosa è entrato nei nodi (7 novembre).** 17 pagine scelte, 15 raccolte (Publishers Weekly vieta in robots.txt, Econ Journal Watch non è più all'indirizzo), 10 entrate nei nodi; ogni citazione è
ritrovata parola per parola nel testo raccolto.

| Nodo | Entrate | Effetto sul nodo |
| --- | --- | --- |
| MIT | Goedecke, R&D World, quattro repliche su GitHub | La catena su Qwen si chiude: la modifica pubblicata si riproduce (50-51%), ma con il ragionamento spento il modello di base fa già il 45%, e una replica ottiene la stessa modifica con script, senza Astra. Nuova catena: la modifica dei pesi al posto dell'addestramento, con due repliche che arrivano a esiti diversi su compiti diversi |
| Fair use | Publishing Perspectives, CCIA, Foundation for American Innovation | Le 51 memorie di terzi nella causa contro OpenAI, lo studio sulla diluizione escluso dalle prove, una teoria nuova sul quarto fattore |
| 20 febbraio | Katchanovski e Abrahms (2024) | Nuova catena: lo studio scrive che il processo ha confermato i «cecchini georgiani»; la sentenza ammette la deposizione e la dichiara smentita. La verifica è sul testo integrale già nel corpus |

Scartate dopo la lettura: una pagina divulgativa scritta per i motori di ricerca e un saggio che ripete argomenti già
nel nodo (MIT); la pagina di EFF che contiene solo il collegamento al PDF (fair use); Nonzero (testo riservato agli
abbonati) e openDemocracy (87 parole raccolte, già nel nodo da un'altra pagina) per il 20 febbraio. Brave ha
portato 9 delle 10 entrate; Bluesky una, Goedecke.

## Il bacino delle fonti e la qualità (proposta del 6 novembre)

Ogni strumento di ricerca serve a scoprire fonti, non è un archivio da cui dipendere. Il bacino estende la lista dei
link e le fonti in prova: siti e autori scoperti da qualsiasi strumento, ciascuno con la sua storia. Il passaggio al
registro resta una decisione della redazione, su proposta motivata.

Si conservano la selezione di Ubik e le pagine raccolte dalla fonte, con la provenienza («trovata con…»); non le liste
restituite dagli strumenti, che alcune condizioni d'uso vietano di conservare (Brave, nei piani senza diritti di
conservazione) e che comunque non servono.

Oggi il punteggio dello scout misura quanto un contributo è stato trovato, non quanto vale. La qualità si propone su
due piani:

| Piano | Criterio | Come si verifica |
| --- | --- | --- |
| Contributo | Rimanda a fonti primarie | Codice: quota di link verso sentenze, paper, dati, atti, repository |
| Contributo | Porta prove proprie | Modello economico, con la frase che lo dimostra |
| Contributo | Discute la posizione opposta | Modello, con la frase |
| Contributo | Autore identificabile e competente | Modello e registro |
| Contributo | Citazioni e numeri ritrovati | Codice |
| Fonte | Esito delle selezioni, con i motivi | Codice, dal bacino |
| Fonte | Citata dalle voci e dalle fonti già scelte | Codice |
| Fonte | Record nelle catene (affermazioni confermate o smentite) | Codice, dai nodi |
| Fonte | Trasparenza e interessi in causa | Controllo una tantum; gli interessi si etichettano |

Un giudizio del modello conta solo se indica la frase e il codice la ritrova nel testo. La posizione sostenuta non
pesa. I numeri si mostrano scomposti e propongono, non decidono.

## Il bacino dell'IA: primo giro (7 novembre)

Strumento: `ubik-corpus/tools/bacino.py`, workflow `bacino.yml` (su richiesta, `runs/bacino.request`), archivio
`registry/bacino-ia.json`. Nessun modello; costo zero. I passi:

| Passo | Cosa fa |
| --- | --- |
| `seed` | Le 42 voci approvate, i siti dei nodi, le firme degli articoli del corpus |
| `expand` | Chi seguono le voci su Bluesky (almeno 3 voci), i siti che le voci citano (almeno 2), gli autori di OpenAlex sui sottotopic |
| `channels` | Per ogni sito: robots.txt, feed dichiarati o agli indirizzi usuali, quota di articoli sull'IA, riserva TDM, data dell'ultimo articolo |
| `clean` | Esclude domini già nel registro, doppioni dello stesso dominio, rumore residuo (testate generaliste, aziende, CDN, documenti primari, feed dei commenti); assegna a ogni voce una classe di canale |
| `measure` | Che cosa avrebbero portato i feed in due settimane (26 ottobre - 7 novembre): articoli, quanti sull'IA, quanti su una Matrice della settimana o su un nodo. Solo titolo, link e data; nulla entra nel corpus |

Ogni voce conserva come è stata trovata, da chi e con quali segnali; esclusioni e doppioni restano registrati con il
motivo.

| | Voci |
| --- | --- |
| Nel bacino | 1.736 (42 approvate) |
| Già fonti del registro, doppioni | 28, 13 |
| Feed attivo sull'IA (almeno 30% degli articoli, ultimo articolo entro 120 giorni) | 39 |
| Feed attivo su altro | 64 |
| Solo Bluesky | 832 (186 seguiti da almeno 5 voci) |
| Solo OpenAlex | 311 |
| Firme delle testate già approvate | 305 |

Cosa dice la misura:
- i 103 feed attivi hanno pubblicato 808 articoli in due settimane, 185 sull'IA; quasi tutti nuovi rispetto alle
  Matrici (4 articoli su una Matrice della settimana del 26 ottobre, 1 su un nodo). Il confronto usa i nomi propri
  dei titoli: è indicativo;
- gli autori singoli scrivono poco (da zero a cinque articoli in due settimane): il loro valore è l'analisi, non la
  copertura delle notizie. Per i nodi servono più come antenne e come spazio di ricerca che come abbonamento;
- Bluesky è la fonte migliore di nomi: chi è seguito da molte voci è quasi sempre pertinente (ricercatori, giornalisti
  specializzati, centri studi), con qualche eccezione da togliere a mano (politici, umoristi, omonimi);
- i link citati dalle voci sono utili dopo la pulizia (METR, Epoch, LessWrong, Dwarkesh, Marginal Revolution);
- OpenAlex, cercato per parole chiave sui lavori più citati, porta soprattutto autori di rassegne generiche e di
  settori lontani. Risultato negativo: va rifatto partendo dalle citazioni dei documenti dei nodi.

La proposta per la redazione è in `reports/bacino/ia-proposta.json`, a gruppi e con i motivi: 18 siti e autori in
prova, 6 in prova con l'interesse in causa dichiarato, 15 non proposti, 186 account Bluesky come antenne (i link che
condividono entrano nel bacino e nello scout, nessun testo raccolto né pubblicato).

**Approvazione e secondo giro (7 novembre, sera).** La redazione ha approvato i gruppi 1 e 2 (24 fonti in prova,
`registry/ai-probation.json`, raccolte dal giro successivo) e le 186 antenne. Tre passi nuovi:

| Passo | Cosa fa | Esito del primo giro |
| --- | --- | --- |
| `resolve` | Brave per chi ha solo il profilo Bluesky: una ricerca per nome; si tiene solo il sito che passa una regola (cognome nel dominio, nome nel titolo, niente pagine profonde), non le liste | 286 ricerche, 96 siti, a campione tutti corretti; ma pochi feed: 4 sull'IA. I giornalisti scrivono sulle testate, i siti personali sono spesso pagine di presentazione |
| `mastodon` | Account Mastodon di voci, antenne e fonti in prova (descrizioni Bluesky, link rel="me" dei siti, registro); chi seguono, dai server; feed RSS di ogni account | 15 account di partenza, 7.749 account visti, 1.224 candidati (seguiti da almeno 2); 24 nuovi feed attivi sull'IA (Doctorow, Matthew Green, Citizen Lab, Open Rights Group, Rachel Thomas…) |
| `antennas` | I link condivisi su Bluesky da voci e antenne negli ultimi 14 giorni, in `reports/bacino/ia-antenne.json` (link e titoli delle schede, nessun testo); un sito diventa candidato se tre account ne condividono link sull'IA; lo scout li legge come percorso «antenne» | 998 link dopo la pulizia, 166 sull'IA (la settimana delle elezioni pesa); 14 siti candidati |

`clean` ora unisce anche la stessa persona trovata su Bluesky e su Mastodon (stesso nome completo). Il bacino conta
3.109 voci, 2.487 candidate. Seconda proposta (14 fonti, da Mastodon e dalle antenne) in prova lo stesso giorno, con Terence Tao (blog e Mastodon), segnalato dalla redazione. Dal 7 novembre la regola è questa: ogni gruppo proposto dal bacino entra in prova con i suoi motivi registrati, e la redazione toglie quello che non vuole. Prima raccolta: 40 fonti in prova, 39 con articoli (Future of Life Institute non risponde in tempo), circa 800 testi entrati nel corpus e nell'indice interno.

## Programma di sviluppo (indicativo)

Ogni fase si misura prima della successiva; una misura deludente può cambiare l'ordine o togliere una fase.

| Fase | Cosa | Serve | Misura |
| --- | --- | --- | --- |
| 1 | Motivi della selezione registrati criterio per criterio; primo record nelle catene dai tre nodi | Nulla | Ogni scelta ha i suoi motivi |
| 2 | Bacino aggiornato da scout, lista dei link, selezioni e catene; proposte settimanali per il registro (primo giro sull'IA il 7 novembre: semi, Bluesky, link delle voci, canali, misura) | Fase 1 | Proposte approvate; articoli pertinenti dei feed in prova |
| 3 | Brave per le lacune; Bluesky autenticato (attivi dal 7 novembre) | `BRAVE_API_KEY`, `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` nei segreti di `ubik-corpus`; conferma del supporto Brave | Rifare la prova sui tre nodi |
| 4 | Indice a testo pieno sul corpus (attivo dal 7 novembre, `tools/corpus_index.py`); poi esteso ai feed in prova e ai link delle antenne | Nulla | Quota di ricerche risolte in casa rispetto a Brave |
| 5 | Selezione automatica a due livelli | Fase 1 | Accordo con la selezione del 6 novembre; costo per nodo |
| 6 | Sorveglianza dei nodi e stato «da aggiornare» | Fasi 3 e 5 | Aggiornamenti segnalati e confermati |

Modelli locali: un modello piccolo che gira su un computer della redazione può filtrare e classificare i testi del corpus senza che escano dalle nostre macchine, e con strumenti come Soup (addestramento su portatile con poca memoria video) si può addestrare sulle selezioni registrate per la prima scrematura della fase 5. Serve prima qualche centinaio di selezioni con i motivi, e un computer con scheda grafica: i server di GitHub non ne hanno.

Da valutare alle stesse regole: Common Crawl, Internet Archive (anche per i collegamenti morti), Wikidata, le
raccomandazioni di Substack. GDELT resta accantonato finché rifiuta i server di GitHub.
