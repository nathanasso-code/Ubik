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

## Programma di sviluppo (indicativo)

Ogni fase si misura prima della successiva; una misura deludente può cambiare l'ordine o togliere una fase.

| Fase | Cosa | Serve | Misura |
| --- | --- | --- | --- |
| 1 | Motivi della selezione registrati criterio per criterio; primo record nelle catene dai tre nodi | Nulla | Ogni scelta ha i suoi motivi |
| 2 | Bacino aggiornato da scout, lista dei link, selezioni e catene; proposte settimanali per il registro | Fase 1 | Proposte approvate |
| 3 | Brave per le lacune; Bluesky autenticato | `BRAVE_API_KEY`, `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` nei segreti di `ubik-corpus`; conferma del supporto Brave | Rifare la prova sui tre nodi |
| 4 | Indice a testo pieno sul corpus | Nulla | Ricerche risolte in casa |
| 5 | Selezione automatica a due livelli | Fase 1 | Accordo con la selezione del 6 novembre; costo per nodo |
| 6 | Sorveglianza dei nodi e stato «da aggiornare» | Fasi 3 e 5 | Aggiornamenti segnalati e confermati |

Da valutare alle stesse regole: Common Crawl, Internet Archive (anche per i collegamenti morti), Wikidata, le
raccomandazioni di Substack. GDELT resta accantonato finché rifiuta i server di GitHub.
