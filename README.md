# Ubik

Aggregatore di notizie selezionate: le fonti si organizzano in fatti (card), vicende (matrici) e Topic, e l'informazione emerge dalle relazioni tra le fonti.

Riordinato il 29 ottobre 2026. Lo stato precedente dei tre rami è conservato, intero, nei rami `archive/2026-10-29-main` (vecchio sito a domande), `archive/2026-10-29-develop-ubik-core` (acquisizione e prototipi) e `archive/2026-10-29-experiment-v5.1` (pipeline v2–v5.1 con la sua cronologia).

## Stato attuale: le Matrici della settimana per Topic

Dal 1 novembre 2026 la pipeline corrente costruisce le Matrici della settimana per ogni Topic: una nota per articolo,
il modello propone le Matrici di articoli interi, il codice conferma ogni unione con i campi strutturati delle note
(evento, nomi propri, espressioni), un secondo giro recupera le card singole. Il macro Topic Intelligenza artificiale
ha quattro sotto-topic: regole, lavoro, data center ed energia, diritto d'autore. Specifica: `docs/daily-spec.md`.

In prova dal 3 novembre una seconda modalità, la conoscenza: nodi di dibattito progettati in redazione, con catene di
smentita agganciate ad affermazioni precise e citazioni verificate. Specifica: `docs/nodi-spec.md`.

Modello in esercizio: DeepSeek V4.1 Flash, circa 0,74 dollari per una settimana di 919 articoli e quattro sotto-topic.

## Struttura

| Percorso | Contenuto | Stato |
| --- | --- | --- |
| `ingestion/ubik_daily5.py` | Macro Topic: nota con sotto-topic, Matrici per sotto-topic, filtro del sotto-topic, pagina | Corrente |
| `ingestion/ubik_daily4.py` | Conferma del codice, secondo giro, testi | Corrente |
| `ingestion/ubik_daily2.py`, `ubik_daily3.py` | Resa delle card e della pagina (usate dalla v5) | Corrente |
| `ingestion/ubik_cost_guard.py` | Costi unitari e controllo preventivo di spesa | Corrente |
| `prompts/daily-v5/`, `prompts/daily-v4/` | Prompt correnti | Correnti |
| `docs/acquisizione-a-z.md` | **Il sistema dalla A alla Z: raccolta, Matrici, nodi, costi, misure, da fare. Punto di partenza per una nuova conversazione** | Corrente |
| `docs/acquisizione-nodi.md` | Metodo dello scout e diario delle prove sull'acquisizione | Corrente |
| `docs/daily-spec.md` | Specifica delle Matrici della settimana | Corrente |
| `docs/nodi-spec.md` | Specifica dei nodi di dibattito | Prototipo |
| `ingestion/ubik_matrix.py`, `prompts/matrix-v1/` | Matrice lunga su un nucleo (`docs/history/matrix-spec.md`) | Messa da parte |
| `ingestion/ubik_daily.py`, `prompts/daily-v1/`–`daily-v3/` | Matrici giornaliere v1–v3 | Abbandonate |
| `ingestion/ubik_v6_*.py`, `prompts/v6*/`, `protocols/ubik-v6-editorial-protocol.md` | v6, composizione editoriale settimanale | Abbandonata |
| `ingestion/` (altri script), `prompts/v5.1/` | Pipeline a coppie v2–v5.1, pilota di estrazione | Abbandonati |
| `docs/experiment-results/`, `docs/history/` | Risultati degli esperimenti e documenti storici | — |
| `acquisition/` | Vecchia acquisizione | Riferimento |
| `attacks-map/`, `scripts/`, `data/` | Mappa degli attacchi russi in Ucraina (pipeline UCDP, ogni martedì) | Conservata |
| `tests/` | Test | — |

I testi degli articoli, i registri delle fonti, la raccolta (RSS, social, newsletter) e le pagine prodotte stanno nel
repository privato `ubik-corpus`; qui restano solo codice e cifre.

La documentazione di progetto vive nei documenti condivisi su Claude: "Ubik — Architettura e modello informativo",
"Ubik — Acquisizione delle fonti", "Ubik — Diario sperimentale", "Ubik — Riferimenti di valutazione".

## Esperimenti abbandonati

- **Matrici giornaliere v1–v3** (31 ottobre): affermazioni come unità, poi un articolo per card, poi gruppi verificati
  dal modello. Frammenti o associazioni non pertinenti; superate dalla conferma del codice.
- **Matrice lunga** (30 ottobre – 1 novembre): testi buoni, ma da mantenere a mano e non centrati sull'attualità.
- **v6** (30 ottobre): pagina settimanale composta dal modello; selezione dei fatti debole.
- **v2–v5.1, accorpamento a coppie**: giudizi su coppie di eventi estratti dai testi, costosi e ciechi al contesto.
- **GDELT come corroborazione**: bloccato dai limiti di frequenza sugli indirizzi di GitHub.
- **Soglie di embedding e cluster di articoli**: non distinguono fatti diversi sullo stesso tema.

## Come si esegue

Le esecuzioni a pagamento partono solo su richiesta esplicita, mai a un normale push di codice: nel repository privato si modifica `runs/daily.request` (con `version=5`) o si avvia il workflow a mano. Ogni fase stima la spesa prima delle chiamate e si rifiuta se supera il tetto.

Segreto richiesto nelle Actions: `OPENROUTER_API_KEY`.

## Hosting

Nessun sito è pubblicato. I progetti Vercel sono in pausa e senza costruzioni automatiche.
