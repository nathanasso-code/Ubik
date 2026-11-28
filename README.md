# Ubik

Aggregatore di notizie selezionate: le fonti si organizzano in fatti (card), vicende (matrici) e Topic, e l'informazione emerge dalle relazioni tra le fonti.

Riordinato il 29 ottobre 2026. Lo stato precedente dei tre rami è conservato, intero, nei rami `archive/2026-10-29-main` (vecchio sito a domande), `archive/2026-10-29-develop-ubik-core` (acquisizione e prototipi) e `archive/2026-10-29-experiment-v5.1` (pipeline v2–v5.1 con la sua cronologia).

## Stato attuale (28 novembre 2026)

Ubik ha due anime che condividono le stesse fonti:
- **l'aggregatore**: la raccolta continua delle fonti approvate (testate, siti, autori, canali Telegram e Mastodon,
  approvati per criterio in automatico) e le **Matrici della settimana** per Topic, costruite dalla pipeline
  `ingestion/ubik_daily5.py` ogni lunedì (specifica: `docs/daily-spec.md`);
- **i nodi**: una domanda di un dibattito trattata come un piccolo studio, in moduli (contesto, fatti, dibattito) con
  le fonti nel testo, le voci del dibattito e i contributi a latere come card (specifica: `docs/nodi-spec.md`). La
  pipeline cerca (catene di ricerche, documenti citati, persone chiave, voci dai social, ricerca proprietaria sul
  corpus); per ora Claude scrive i moduli in chat con la redazione. Laboratorio: il nodo sull'IA e la matematica,
  misurato contro Wikipedia. I nodi d'attualità si aggiornano ogni giorno o ogni settimana.

Le fonti si raccolgono per **tema**: si cerca con le API finché portano fonti nuove, poi il tema vive delle fonti
proprie (registro unico). Modello in esercizio: DeepSeek V4.1 Flash. Il codice dei nodi e dell'acquisizione sta nel
repository privato (`tools/`); il quadro completo e l'elenco unico delle cose da fare sono in
`docs/acquisizione-a-z.md`, punto di partenza per una nuova conversazione.

## Struttura

| Percorso | Contenuto | Stato |
| --- | --- | --- |
| `ingestion/ubik_daily5.py` | Macro Topic: nota con sotto-topic, Matrici per sotto-topic, filtro del sotto-topic, pagina | Corrente |
| `ingestion/ubik_daily4.py` | Conferma del codice, secondo giro, testi | Corrente |
| `ingestion/ubik_daily2.py`, `ubik_daily3.py` | Resa delle card e della pagina (usate dalla v5) | Corrente |
| `ingestion/ubik_cost_guard.py` | Costi unitari e controllo preventivo di spesa | Corrente |
| `prompts/daily-v5/`, `prompts/daily-v4/` | Prompt correnti | Correnti |
| `docs/acquisizione-a-z.md` | **Il sistema dalla A alla Z: raccolta, Matrici, nodi, costi, misure, da fare. Punto di partenza per una nuova conversazione** | Corrente |
| `docs/daily-spec.md` | Specifica delle Matrici della settimana | Corrente |
| `docs/nodi-spec.md` | Specifica dei nodi a moduli | In prova |
| `docs/modello-dati.md` | Modello dei dati per il sito | Bozza |
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

La documentazione di riferimento è quella di questo repository (`docs/`). I documenti condivisi su Claude ("Ubik —
Architettura e modello informativo", "Ubik — Acquisizione delle fonti", "Ubik — Diario sperimentale", "Ubik —
Riferimenti di valutazione") possono essere rimasti indietro: in caso di differenza fa fede `docs/`.

## Esperimenti abbandonati

- **Matrici giornaliere v1–v3** (31 ottobre): affermazioni come unità, poi un articolo per card, poi gruppi verificati
  dal modello. Frammenti o associazioni non pertinenti; superate dalla conferma del codice.
- **Matrice lunga** (30 ottobre – 1 novembre): testi buoni, ma da mantenere a mano e non centrati sull'attualità.
- **v6** (30 ottobre): pagina settimanale composta dal modello; selezione dei fatti debole.
- **v2–v5.1, accorpamento a coppie**: giudizi su coppie di eventi estratti dai testi, costosi e ciechi al contesto.
- **GDELT come corroborazione**: bloccato dai limiti di frequenza sugli indirizzi di GitHub.
- **Soglie di embedding e cluster di articoli**: non distinguono fatti diversi sullo stesso tema.

## Come si esegue

Le esecuzioni a pagamento partono solo dal calendario dei workflow o su richiesta esplicita (un file `runs/*.request` nel
repository privato, o a mano), mai a un normale push di codice. Ogni fase stima la spesa prima delle chiamate e si
rifiuta se supera il tetto. Elenco delle richieste: `docs/acquisizione-a-z.md`, sezione 11.

## Hosting

Nessun sito è pubblicato. I progetti Vercel sono in pausa e senza costruzioni automatiche.
