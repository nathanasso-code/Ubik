# Modello dei dati — bozza (aggiornata il 28 novembre 2026)

Scopo: un formato unico da cui si generano tutte le pagine di Ubik (Topic, Matrici, card, nodi) e, più avanti, il
sito. Oggi ogni prodotto ha un JSON suo (le Matrici `daily-v5-*.json`, i nodi `nodo2.json` o `moduli-auto/*.json`, i
nodi nella forma precedente `node.json` e `light.json`) e una pagina generata da uno script suo. È il passo 6 della
sezione 0.5 di `docs/acquisizione-a-z.md`: prima il modello dei dati, poi un prototipo del sito in sola lettura.

## Regola Topic, tema, nodo

| | Topic | Tema | Nodo |
| --- | --- | --- | --- |
| Che cos'è | Il perimetro delle Matrici: un'area con un flusso di notizie da testate diverse | Il perimetro delle fonti: nodi e topic delle Matrici sullo stesso soggetto (`registry/temi.json`) | Una domanda su cui fonti credibili si dividono |
| Contiene | Sotto-topic, Matrici, card | Fonti, pagine archiviate, misura di autonomia | Moduli, voci, contributi a latere |
| Chi lo decide | La redazione | Provvisori di Claude, da ridefinire con la redazione | La redazione |

## Oggetti

Ogni oggetto ha `id` stabile, `asof` (data dell'ultimo aggiornamento) e un blocco `cantiere` (sotto).

| Oggetto | Campi principali | Dove sta oggi |
| --- | --- | --- |
| `fonte` | id, nome, tipo (testata, sito, autore, voce, canale, istituzione), stato, temi, modo di raccolta, pagine per archivio, nodi | `registry/registro.json` (vista sopra i registri) |
| `pezzo` | id, fonte, url, data, titolo, lingua, testo pieno o parziale (il testo resta nel corpus privato), copie dello stesso documento | corpus privato; `data/schede.json` (una scheda per documento) |
| `nota` | pezzo, tipo, evento, sintesi, citazione verificata, sotto-topic | note delle Matrici |
| `card` | pezzi, titolo, testo (solo se più fonti) | dentro le Matrici |
| `matrice` | id, settimana, sotto-topic, titolo, essenza, card, origini, nodi collegati | `daily-v5-*.json` |
| `topic` | id, nome, sotto-topic, temi | `TOPICS` in `ubik_daily5.py` |
| `tema` | id, nome, nodi, registri delle Matrici, stato (in acquisizione, autonomo), misure di autonomia per giro | `registry/temi.json`, `registry/registro.json` |
| `nodo` | id, tema, domanda, apertura, moduli, conflitto d'interessi | `reports/nodi/<nodo>/` |
| `modulo` | id, nodo, sotto-domanda, sintesi, contesto, cronologia, fatti, posizioni, da notare, manca, fonti citate, contributi a latere | `nodo2.json` |
| `passaggio` | modulo, testo della frase, note (fonti), passaggi delle fonti su cui poggia | dentro il modulo |
| `posizione` | modulo, titolo, resoconto, voci | dentro il modulo |
| `voce` | chi, ruolo, data, citazione, rete o fonte, link | `voci-social.json` e fonti archiviate |
| `contributo a latere` | modulo, pezzo, titolo, sintesi, tipo, punteggio della pipeline, voti | `nodo2.json` (`a_latere`) |
| `proposta di modifica` | passaggio, utente, testo proposto, fonti nuove, esito del modello, voti, esito | da progettare |
| `commento` | passaggio o nodo, utente, testo, risposte | da progettare |
| `voto` | utente, oggetto (proposta, contributo a latere), valore | da progettare |
| `utente` | id, iscrizione, abbonamento, etichetta (OP per la redazione), contributi | da progettare |

La stessa fonte compare in Matrici, nodi e voci con lo stesso `pezzo`: le copie dello stesso documento a indirizzi
diversi sono un pezzo solo (`tools/doc_ids.py`), e una correzione della scheda (`tools/schede.py`) vale ovunque.

## Cantiere

Ogni oggetto porta:

```json
"cantiere": {
  "stato": "bozza | verificato | pubblicato | da aggiornare | sospeso",
  "costruito": {"data": "2026-11-28", "come": "pipeline | in chat | a mano", "modello": "…", "codice": "commit"},
  "costo_usd": 0.03,
  "verifiche": ["passaggi ritrovati 100/100", "numeri non ritrovati 0"],
  "da_fare": ["…"]
}
```

## Pubblico e privato

- Privato (`ubik-corpus`): tutti gli oggetti, con i rimandi ai testi del corpus.
- Pubblicabile: solo sintesi, citazioni brevi verificate, link, date, relazioni. Mai testi interi.
- Le pagine (artefatti oggi, sito domani) si generano solo dalla parte pubblicabile.

## Passi

1. Fatto (4-11 novembre): il convertitore dei dati esistenti (`tools/build_model.py`), l'esploratore privato
   (`ingestion/ubik_explorer.py`), un documento un pezzo (`tools/doc_ids.py`), il catalogo comune delle schede
   (`data/schede.json`, `tools/schede.py`).
2. Da fare: gli oggetti del nodo a moduli (modulo, passaggio, posizione, voce, contributo a latere) scritti direttamente
   da `build2.py` e da `tools/node_modules.py` nello stesso formato.
3. Da progettare con la redazione: proposte di modifica, commenti, voti, utenti, abbonamenti.
4. Un prototipo del sito in sola lettura generato da questi oggetti.
