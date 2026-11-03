# Nodi di dibattito — specifica del prototipo (3 novembre 2026)

Seconda modalità di Ubik accanto all'attualità (Matrici della settimana, `docs/daily-spec.md`): la conoscenza.
Un Topic è una mappa di pochi nodi progettati in redazione; ogni nodo è una domanda su cui il racconto si divide.
Dati dei prototipi nel repository privato (`ubik-corpus/reports/nodi/`).

## Struttura

| Elemento | Definizione |
| --- | --- |
| Topic | Mappa di 6–8 nodi (per Euromaidan: motivo scatenante, eventi salienti, massacro del 20 febbraio, presunto golpe, presunto coinvolgimento americano, peso dell'estrema destra, conseguenze immediate). |
| Nodo di fatto | Una domanda su cosa è accaduto o perché (di fatto, causale, conteso). Si scompone in catene e anelli, con verifiche sui documenti primari. |
| Nodo d'analisi | Una domanda aperta su cui contano le interpretazioni (per esempio: un risultato di ricerca segna un salto qualitativo?). Raccoglie opinioni di valore senza scomporle: l'unità è la voce. |
| Voce | Nel nodo d'analisi: chi è e perché conta, la tesi in due righe, una o due citazioni verificate, il link. Relazioni tra voci: risponde a, concorda, contesta, estende. I fatti che una voce dichiara (per esempio una riproduzione di esperimenti) portano l'etichetta «dichiarato». |
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
- Registro delle voci per Topic, accanto a quello delle testate: venti-quaranta persone approvate dalla redazione,
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

## Prossimi passi

1. Bozza del registro delle voci per l'Intelligenza artificiale, da approvare.
2. Primo nodo d'analisi: il paper MIT «Sparks of Weight-Space Programming» (novembre 2026), con un'analisi segnalata
   dalla redazione di chi ha riprodotto parte degli esperimenti.
3. Ricostruire il nodo del 20 febbraio con un modello forte dalle stesse fonti e confrontarlo con la versione cieca.
4. Costruire il nodo «Il presunto coinvolgimento americano», con le affermazioni in circolazione agganciate.
