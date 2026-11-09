# Modello dei dati — bozza (aggiornata il 6 novembre 2026)

Scopo: un formato unico da cui si generano tutte le pagine di Ubik (Topic, Matrici, card, nodi), l'esploratore
privato e, più avanti, il sito. Oggi ogni prototipo ha un JSON suo (`daily-v5-*.json`, `node-cieco.json`,
`fair-use-*.json`, `claim.json`) e un HTML scritto a mano: ogni cambio di struttura va rifatto pagina per pagina.
Il formato serve anche a tenere sotto controllo il cantiere: ogni oggetto dice in che stato è, quanto è costato e
cosa manca.

## Regola Topic / nodo (decisa il 4 novembre 2026)

| | Topic | Nodo |
| --- | --- | --- |
| Che cos'è | Un'area d'attenzione stabile | Una domanda su cui fonti credibili si dividono |
| Si giudica su | Flusso di notizie da testate diverse per mesi (orientativo: 20 articoli a settimana da 5 testate indipendenti) e interesse | Si formula come domanda; c'è un disaccordo reale o un'affermazione contestata in circolazione; esistono documenti o voci di valore che lo ancorano |
| Contiene | Sotto-topic, Matrici della settimana, card, nodi | Catene e anelli (nodo di fatto) o voci (nodo d'analisi), affermazioni in circolazione |
| Numero | Pochi (5–8 al lancio) | Senza tabella di marcia fissa; ogni nodo costa e va scelto |

Due modalità di Topic: **d'attualità** (flusso, Matrici, qualche nodo; es. Intelligenza artificiale) e **di
conoscenza** (nessun flusso, una mappa di nodi; es. Euromaidan). Un nodo che genera molte domande e un flusso suo
può diventare Topic. I nodi nascono da una Matrice in cui le fonti si dividono, da un'affermazione in circolazione o
dalla mappa che la redazione disegna per un Topic di conoscenza.

## Oggetti

Ogni oggetto ha `id` stabile, `asof` (data dell'ultimo aggiornamento) e un blocco `cantiere` (sotto).

| Oggetto | Campi principali | Dove sta oggi |
| --- | --- | --- |
| `fonte` | id, origin, nome, tipo, livello, lingua, accesso al testo (pieno/parziale), canale (feed, newsletter, social, ricerca) | registri in `ubik-corpus/registry/` |
| `voce` | id, nome, ruolo, posizione, sotto-topic, canali → fonti | `registry/ai-voices.json` |
| `pezzo` | id, fonte, url, data, titolo originale, lingua, testo parziale sì/no. Il testo resta solo nel corpus privato. Tipi di provenienza: feed, newsletter, ricerca, scout, segnalazione della redazione, documento primario (`corpus/documents/`) | corpus privato |
| `nota` | pezzo, tipo (cronaca, analisi…), evento, sintesi, citazione verificata con traduzione, sotto-topic | `notes-v5.json` |
| `card` | pezzi, titolo, testo (solo se più fonti) | dentro le Matrici |
| `matrice` | id, settimana, sotto-topic, titolo, essenza, card, origini, numeri non ritrovati, nodi collegati | `daily-v5-*.json` |
| `topic` | id, nome, modalità (attualità/conoscenza), perimetro, sotto-topic, nodi, voci | `TOPICS` in `ubik_daily5.py`, mappe nei documenti |
| `nodo` | id, topic, tipo (fatto/analisi), domanda, testo da cui parte tutto (affermazioni → catene), catene, domande aperte, affermazioni in circolazione. Un'architettura sola per tutti i tipi (6 novembre): catene di anelli con relazioni | `reports/nodi/<nodo>/` (`node.json`; per il 20 febbraio `node-cieco.json`) |
| `catena` | id, domanda, stato (aperta/chiusa/stallo), sintesi, anelli | dentro il nodo |
| `anello` | pezzo, cosa afferma, citazione verificata, relazione con l'anello sopra | dentro la catena |
| `relazione` | da, a, verbo (conferma, contesta, smentisce, estende, risponde a…), tipo (dichiarata, ricostruita, verifica di Ubik, simulata), nota | `relations`, `rel` |
| `affermazione` | chi, testo, diffusione, anelli toccati, dove regge e dove no | `claim.json` |
| `nodo leggero` | domanda, stato in una riga con le sue fonti, punti del contendere (affermazione, fonte a favore e contro con citazione verificata, esito: accertato, smentito, conteso, aperto; che cosa deciderebbe), documenti cardine, per approfondire, decisioni della redazione con il motivo, ancore che lo legano alle Matrici (9 novembre) | `reports/nodi/<nodo>/light.json` |

Le fonti dei nodi oggi sono descritte dentro ciascun nodo (`who`, `kind`, `url`): diventano `pezzo` con un id
comune, così la stessa fonte compare in Matrici, nodi e voci senza doppioni.

## Cantiere

Ogni oggetto porta:

```json
"cantiere": {
  "stato": "bozza | verificato | pubblicato | da aggiornare | sospeso",
  "costruito": {"data": "2026-11-04", "come": "pipeline daily-v5 | a mano | modello", "modello": "deepseek-v4", "prompt_sha256": "…", "codice": "commit"},
  "costo_usd": 0.03,
  "verifiche": ["citazioni ritrovate 8/8", "numeri non ritrovati 0"],
  "da_fare": ["manca la decisione d'appello"]
}
```

L'esploratore ne ricava la vista d'insieme: cosa c'è, in che stato, quanto è costato, cosa manca.

## Pubblico e privato

- Privato (`ubik-corpus/data/`): tutti gli oggetti, con i rimandi ai testi del corpus.
- Esportazione pubblicabile (`ubik-corpus/export/`): solo campi pubblicabili, cioè sintesi, citazioni brevi
  verificate con traduzione, link, date, relazioni. Mai testi interi.
- Le pagine (artefatti oggi, sito domani) si generano solo dall'esportazione.

## Passi

1. Convertire i dati esistenti: Topic IA e la settimana 26 ottobre, i nodi fair use, 20 febbraio e USAID. Fatto il
   4 novembre (`ubik-corpus/tools/build_model.py`); il 6 novembre i nodi usano tutti lo stesso convertitore a catene.
2. Esploratore privato generato dall'esportazione: Topic → Matrici → nodi, con la vista del cantiere. Fatto
   (`ingestion/ubik_explorer.py`). Le card mostrano una sintesi comune e l'elenco delle fonti; il dettaglio per
   fonte resta come controllo.
Il resto (le pipeline che scrivono direttamente il formato al posto dei JSON di oggi) è
nell'elenco unico: `docs/acquisizione-a-z.md`, sezione 10.
