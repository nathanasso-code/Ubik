# Nodi — specifica (aggiornata il 28 novembre 2026)

Quadro completo del sistema, dall'acquisizione alla scrittura: `docs/acquisizione-a-z.md` (sezioni 6 e 7). Dati dei
nodi nel repository privato (`ubik-corpus/reports/nodi/<nodo>/`). Questa specifica descrive il formato in prova sul
nodo `ia-matematica` (27-28 novembre), da perfezionare prima di estenderlo agli altri nodi. Le architetture precedenti
(lo spettro di posizioni del 2 novembre, le catene di anelli del 6 novembre, la bozza a punti del 9-15 novembre, ancora
in uso per i nodi d'attualità non riscritti) sono nella storia del repository.

## Che cos'è un nodo

Una domanda importante di un dibattito, trattata come un piccolo studio: dice che cosa si sa, che cosa no e perché, con
le prove e l'interesse di chi parla, e permette di controllare tutto. I nodi sono relativamente pochi e scelti dalla
redazione; nascono da una Matrice in cui le fonti si dividono, da un caso in corso o da una domanda della redazione.
Ogni nodo appartiene a un **tema** (`ubik-corpus/registry/temi.json`), che ne condivide le fonti con gli altri nodi e
con le Matrici dello stesso soggetto.

## Struttura

| Elemento | Definizione |
| --- | --- |
| Domanda e apertura | La domanda del nodo, una presentazione di poche righe (con il conflitto d'interessi quando c'è), la sintesi: le frasi d'apertura dei moduli, ciascuna un link al suo modulo |
| Modulo | Una sotto-domanda (6-9 per nodo). Sintesi in apertura, poi tre parti divise con delicatezza (un filo sottile e un'etichetta piccola): contesto, fatti, dibattito. In fondo «Da notare», «Manca», la striscia «Su che cosa si regge» (fonti citate per tipo) e i contributi a latere |
| Contesto | Di che cosa si parla e che cosa è successo, con i termini spiegati; una cronologia quando serve. Qui il modello ha più iniziativa, ma ogni fatto porta la sua fonte |
| Fatti | Ciò che studi, documenti e fonti primarie stabiliscono, con le cifre come le fonti le danno |
| Dibattito | Le posizioni, ciascuna con un titolo, un resoconto in italiano e le card delle voci |
| Voce (card) | La citazione nella lingua originale, chi parla, ruolo, data, il numero della nota e il link all'originale. Da un saggio o articolo archiviato, o da un post (Bluesky, Mastodon, Telegram) raccolto in `voci-social.json` |
| Contributo nel testo | Una fonte citata da una frase: nota numerata, colorata per tipo (documento ufficiale, istituzione, studio, analisi, opinione, dichiarazione di parte, stampa); il numero apre la scheda della fonte (chi, tipo, interesse, che cosa dice, il passaggio su cui poggia la frase, il link) |
| Contributo a latere (card) | Un contributo del nodo pertinente al modulo ma non citato nel testo: titolo, sintesi della pipeline, sito, tipo, link. Una card, un contributo. Nel modulo i primi quattro, gli altri dietro un pulsante. Ordine: il giudizio della pipeline finché non ci sono voti dei lettori, poi i più votati |
| Da notare | Ciò che il lettore deve sapere per pesare il modulo: chi ha prodotto i risultati, conflitti d'interessi, limiti delle fonti |
| Manca | Ciò che le fonti raccolte non coprono, detto apertamente |

I moduli sono i simulacri delle Matrici; i contributi, esterni o degli utenti, i simulacri delle Card (nelle Matrici una
card può aggregare fonti ridondanti, nel nodo no).

Da decidere con la redazione: il criterio per cui un contributo entra nel testo o resta a latere (oggi: nel testo le
fonti che sostengono un fatto o una posizione, tutto il resto a latere); se filtrare per credibilità i siti delle card.

## Regole

- Fedeltà assoluta alle fonti: niente invenzioni, ogni frase con un fatto o una cifra ha la sua fonte, ogni numero sta
  nella fonte citata come la fonte lo dà. La conoscenza del modello solo per cercare e dare contesto.
- Passaggi e citazioni si mostrano solo se il codice li ritrova parola per parola nella pagina archiviata o nel post.
- Niente etichette di giudizio del modello («accertato», «conteso»): si descrivono il peso delle prove e l'interesse di
  chi parla; un giudizio solo dove un documento, un dato ufficiale o uno studio chiude la questione, dicendo quale.
- Le serie di cifre vanno in un riquadro di confronto, solo tra cifre che misurano la stessa cosa.
- Scrittura divulgativa, sulla falsariga di Wikipedia senza la sua lunghezza (il laboratorio: circa 4.700 parole per
  otto moduli); termini spiegati dentro la frase.
- Conflitto d'interessi dichiarato quando chi scrive (Claude) parla di Anthropic, dei suoi modelli o della coscienza
  delle IA.

## Citazioni mostrate

I testi integrali restano nel corpus privato. Regola per nodi e card:

| Fonte | Citazioni mostrate |
| --- | --- |
| Articoli di giornale e stampa di settore (diritto degli editori, art. 43-bis della legge sul diritto d'autore) | Al massimo una per articolo, entro circa 150 caratteri |
| Studi, blog, memorie, documenti delle parti | Citazione per discussione (art. 70), entro 300 caratteri |
| Atti ufficiali (sentenze, leggi, documenti delle istituzioni) | Entro 300 caratteri |
| Post pubblici | La parte del post che porta la posizione, con il link |

## File di un nodo (`ubik-corpus/reports/nodi/<nodo>/`)

| File | Che cosa |
| --- | --- |
| `node.json`, `scout.json` | Domanda, sotto-domande, lingue, termini, ancore |
| `catena.json`, `bilancio.json`, `persone.json` | Giri di ricerca, bilancio dell'ultima esecuzione, persone chiave |
| `voci-social.json` | Le voci raccolte dai social |
| `chat/moduli2.py`, `chat/build2.py`, `chat/gen_page2.py`, `chat/nodo2.json` | I moduli scritti in chat, i controlli, la pagina (procedura: `acquisizione-a-z.md`, 7.2) |
| `moduli-auto/` | I moduli scritti dalla pipeline (`tools/node_modules.py`) |
| `nodo.html` | La pagina, pubblicata come artefatto |
| `wiki-claims*.json`, `wiki-bench*.json` | Le misure contro Wikipedia |
| `light.json`, `light.md` | La bozza a punti dei nodi nella forma precedente |

Le pagine giudicate stanno in `ubik-corpus/reports/scout/<nodo>/judge.json`, quelle archiviate in
`ubik-corpus/corpus/targeted/<nodo>/pagine/`.
