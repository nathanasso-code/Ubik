# Nodi di dibattito — specifica del prototipo (aggiornata il 6 novembre 2026)

Seconda modalità di Ubik accanto all'attualità (Matrici della settimana, `docs/daily-spec.md`): la conoscenza.
Un Topic è una mappa di pochi nodi progettati in redazione; ogni nodo è una domanda su cui il racconto si divide.
Regola Topic / nodo, modalità del Topic (attualità, conoscenza) e formato dei dati: `docs/modello-dati.md`.
Dati dei prototipi nel repository privato (`ubik-corpus/reports/nodi/`). Acquisizione dei contributi: `docs/acquisizione-nodi.md`.

**Un'architettura sola (decisa il 6 novembre 2026).** Ogni nodo, di fatto o d'analisi, usa quella del nodo sul 20 febbraio:
un testo da cui parte tutto, catene di anelli e relazioni tipizzate tra fonti. Lo spettro di posizioni del primo
prototipo sul fair use è superato: il nodo è stato convertito il 6 novembre (`reports/nodi/fair-use/node.json`).

## Struttura

| Elemento | Definizione |
| --- | --- |
| Topic | Mappa di 6–8 nodi (per Euromaidan: motivo scatenante, eventi salienti, massacro del 20 febbraio, presunto golpe, presunto coinvolgimento americano, peso dell'estrema destra, conseguenze immediate). |
| Nodo di fatto | Una domanda su cosa è accaduto o perché (di fatto, causale, conteso). Si scompone in catene e anelli, con verifiche sui documenti primari. |
| Nodo d'analisi | Una domanda aperta su cui contano le interpretazioni (per esempio: un risultato di ricerca segna un salto qualitativo?). Stessa struttura del nodo di fatto: le voci sono anelli, collegati da relazioni (risponde a, contesta, riproduce, estende); un nodo su uno studio ha in più le catene di verifica (cosa regge alla riproduzione). |
| Voce | Una persona del registro che compare come anello: chi è e perché conta, la tesi in due righe, una o due citazioni verificate, il link. Relazioni tra voci: risponde a, concorda, contesta, estende. I fatti che una voce dichiara (per esempio una riproduzione di esperimenti) portano l'etichetta «dichiarato». |
| Testo da cui parte tutto | Poche affermazioni basate sulle fonti; ognuna rimanda alle catene che la sostengono. Più che discorsivo, è la sintesi delle catene. Nel nodo d'analisi mappa le posizioni: dove le voci convergono, dove si dividono e su cosa; non stabilisce il vero. |
| Catena | Sequenza di anelli: ogni fonte risponde a un'affermazione precisa della fonte sopra. Stato: aperta, chiusa, stallo. Sintesi di una o due frasi e cosa la scioglierebbe. |
| Anello | La fonte intera, ciò che afferma in quella catena, la citazione verificata con traduzione, la relazione con l'anello sopra (verbo e tipo). |
| Affermazione in circolazione | Un post o una dichiarazione che tocca il nodo: una riga con chi, quanta diffusione, quali anelli tocca, dove regge e dove no. Non diventa un nodo suo. |

Un nodo d'analisi può affiancare un fatto dell'attualità (una card o una Matrice): è la discussione degli esperti su quel fatto.

Tipi di relazione: **dichiarata** (la fonte cita quella a cui risponde), **ricostruita** (il collegamento l'ha fatto Ubik),
**verifica di Ubik** (lettura del documento primario), **simulata** (contributo scritto da Ubik dove manca una risposta
esterna, dichiarato come tale; tiene il posto della comunità).

## Fonti

- Si cercano per domanda, non dai feed: documenti primari, la versione più forte di ogni tesi, le verifiche indipendenti.
- Opinioni solo se di valore e non ridondanti. Media di Stato solo come voce di parte dichiarata.
- Registro delle voci per Topic, accanto a quello delle testate (per l'IA: `ubik-corpus/registry/ai-voices.json`,
  42 voci approvate il 4 novembre 2026, ciascuna con i suoi canali: feed, newsletter, social, ricerca per domanda).
  Criteri da rendere espliciti per le prossime approvazioni: competenza dimostrata sul tema (ricerca, pratica,
  giornalismo di settore), argomenti propri e non rilanci, citazioni e verifiche ricostruibili, posizione dichiarata
  quando è di parte; il registro deve coprire le posizioni in disaccordo, non solo le più vicine al consenso.
  Venti-quaranta persone approvate dalla redazione,
  ognuna con i suoi canali raccoglibili (blog, Substack, Bluesky, Mastodon, YouTube, podcast). La qualità si decide
  sulla persona, non sul singolo testo. Si allarga dalle voci che le voci citano; dopo un fatto importante si cerca
  chi del registro ne ha scritto. Testi segnalati dalla redazione: testo e link, conservati nel corpus privato,
  pubblicati solo come citazioni brevi più link.
- Raccolta mirata senza modelli: `reports/nodi/<nodo>/seeds.json` e il workflow `fetch.yml` del repository privato.
  Le citazioni si mostrano solo se ritrovate parola per parola nei testi raccolti; le fonti non raccolte si riassumono
  senza virgolettati.
- Video: rimando con link, punto del filmato, cosa mostra e cosa dimostra; trascrizione assistita (per esempio Gemini)
  dichiarata come tale finché il passaggio non è controllato.
- Obsolescenza: copia al momento della raccolta, con data e impronta. Da fare: segnalare i collegamenti morti e
  rimandare a una copia d'archivio pubblica.

## Prototipi

| Nodo | Struttura | Esito |
| --- | --- | --- |
| Addestramento e diritto d'autore (2 novembre) | Spettro di quattro posizioni, 22 fonti, 25 relazioni, 5 contributi simulati | Funziona come mappa, ma una lista di fonti per tema raccoglie materiale poco rilevante |
| Il massacro del 20 febbraio, Topic Euromaidan (3 novembre) | Tre catene, 11 fonti, 8 citazioni verificate | Versione cieca registrata prima delle fonti della redazione (impronta f9484416035d) |
| Il massacro del 20 febbraio, ampliato (5–6 novembre) | Tre catene, 24 anelli: testo integrale della sentenza (catena sull'Hotel Ukraina chiusa) e sei fonti dallo scout | Le perizie balistiche, l'appello annunciato e la letteratura dominata da un autore entrano nelle catene |
| Addestramento e diritto d'autore, convertito (6 novembre) | Cinque catene, 33 anelli, 26 fonti; i contributi simulati non sono stati riportati | Stessa architettura del 20 febbraio; aggiunti Lemley e Casey, EFF 2025, Courthouse News, FSF |
| Leggere e scrivere i pesi: il rapporto del MIT (6 novembre) | Sei catene, 30 anelli, 13 fonti, tutte le citazioni verificate | Primo nodo costruito con lo scout: le repliche indipendenti ridimensionano il risultato su Qwen |

## Prossimi passi

1. Selezione automatica dei candidati dello scout a due livelli (modello economico per scartare, modello forte per
   mettere in relazione), misurata contro la selezione fatta in conversazione il 6 novembre: darà il costo vero di un
   nodo. Il nodo sul paper del MIT è stato costruito il 6 novembre con lo scout e la selezione in conversazione.
2. Ricostruire il nodo del 20 febbraio con un modello forte dalle stesse fonti e confrontarlo con la versione cieca.
3. Costruire il nodo «Il presunto coinvolgimento americano», con le affermazioni in circolazione agganciate.

## Costi stimati (4 novembre 2026)

I tre prototipi sono stati costruiti in conversazione: costo non misurato. Stima per un nodo automatico (una ventina
di ricerche, 15–25 fonti lette): 1,8–2,5 $ con un modello di punta, 1–1,3 $ con un modello intermedio, 0,5–0,9 $ a due
livelli. Le Matrici della settimana costano 0,74 $ per 900 articoli e quattro sotto-topic. Nessuna tabella di marcia
fissa per i nodi: ognuno va scelto, e si aggiorna con le sole fonti nuove invece di ricostruirlo.

## Citazioni mostrate (8 novembre 2026)

I testi integrali restano nel corpus privato; nelle pagine si mostrano sintesi di Ubik e citazioni brevi. Regola applicata
dal codice (`ubik-corpus/tools/build_model.py`, `shown_quote`), per nodi e card:

| Fonte | Citazioni mostrate |
| --- | --- |
| Articoli di giornale e stampa di settore (diritto degli editori, art. 43-bis della legge sul diritto d'autore) | Al massimo una per articolo, entro circa 150 caratteri (gli «estratti molto brevi») |
| Studi, blog, memorie, documenti delle parti | Citazione per discussione (art. 70), entro 300 caratteri |
| Atti ufficiali (sentenze, leggi, documenti delle istituzioni) | Entro 300 caratteri; non protetti dal diritto d'autore |

Una citazione oltre la regola resta nel file privato del nodo e non si mostra; l'anello mantiene la sintesi e il link. Il
cantiere del nodo dice quante citazioni sono state nascoste.
