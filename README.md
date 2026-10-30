# Ubik

Aggregatore di notizie selezionate: le fonti si organizzano in fatti (card), vicende (matrici) e Topic, e l'informazione emerge dalle relazioni tra le fonti.

Riordinato il 29 ottobre 2026. Lo stato precedente dei tre rami è conservato, intero, nei rami `archive/2026-10-29-main` (vecchio sito a domande), `archive/2026-10-29-develop-ubik-core` (acquisizione e prototipi) e `archive/2026-10-29-experiment-v5.1` (pipeline v2–v5.1 con la sua cronologia).

## Stato attuale: v6 (lettura editoriale)

Dal 30 ottobre 2026 la pipeline corrente è la v6, provata sul Topic "Regole sull'IA in Europa e negli Stati Uniti".
1. **Scheda per testo**: il modello legge ogni articolo o post e ne scrive una scheda con fatti (tipo evento/rapporto, data, fonte dichiarata, citazione letterale) e tesi.
2. **Composizione settimanale**: dalle schede il modello compone la pagina (fatti, commenti, analisi, esclusi con motivo, "continua" verso i fatti della settimana prima).
3. **Controlli nel codice**: citazioni letterali, copertura, riferimenti, origini indipendenti, date e duplicati. Le violazioni lievi si correggono per rimozione (registrata); oltre 5 correzioni la pagina si ricompone (fino a 3 tentativi). I 5 fatti in evidenza sono scelti da una regola dichiarata, non dal modello.
4. **Matrici**: le vicende nascono concatenando i legami "continua" tra settimane.

Modello di produzione candidato: DeepSeek V4.1 Flash (circa 0,07 dollari a settimana). Sonnet 5.5 resta come braccio di confronto.

## Struttura

| Percorso | Contenuto | Stato |
| --- | --- | --- |
| `ingestion/ubik_v6_editorial.py` | Schede, composizione, controlli, correzione, regola di evidenza, resa | Corrente |
| `ingestion/ubik_v6_matrices.py` | Vicende tra settimane dai legami "continua" | Corrente |
| `ingestion/ubik_cost_guard.py` | Costi unitari misurati e controllo preventivo di spesa | Corrente |
| `prompts/v6.3/` | Prompt correnti (scheda uguale a v6.2; composizione con "continua") | Congelati |
| `prompts/v6/`, `prompts/v6.2/` | Varianti precedenti della v6 | Storia |
| `protocols/ubik-v6-editorial-protocol.md` | Preregistrazione e risultati v6, v6-pf, v6.2, v6.3 | — |
| `ingestion/` (altri script), `prompts/v5.1/` | Pipeline a coppie v2–v5.1, pilota di estrazione | Abbandonati, conservati come storia |
| `docs/experiment-results/`, `docs/history/` | Risultati degli esperimenti e documenti storici | — |
| `acquisition/` | Scoperta RSS, verifica del testo, Mastodon | Riferimento |
| `attacks-map/`, `scripts/`, `data/` | Mappa degli attacchi russi in Ucraina (pipeline UCDP, ogni martedì) | Conservata |
| `tests/` | Test | — |

I testi degli articoli, i registri delle fonti, la raccolta (RSS, social, newsletter) e le pagine prodotte stanno nel repository privato `ubik-corpus`; qui restano solo codice e cifre.

La documentazione di progetto vive nei documenti condivisi su Claude: "Ubik — Architettura e modello informativo", "Ubik — Acquisizione", "Ubik — Diario sperimentale", "Ubik — Riferimenti di valutazione".

## Esperimenti abbandonati

- **v2–v5.1, accorpamento a coppie**: giudizi su coppie di eventi estratti dai testi. Costosa (1,50 dollari per un solo sondaggio) e cieca al contesto. Prompt e script restano in `ingestion/` e `prompts/v5.1/`.
- **v6-pf, prefiltro**: nessun guadagno, rimosso.
- **GDELT come corroborazione**: bloccato dai limiti di frequenza sugli indirizzi di GitHub.
- **Soglie di embedding e cluster di articoli**: non distinguono fatti diversi sullo stesso tema.

## Come si esegue

Le esecuzioni a pagamento partono solo su richiesta esplicita, mai a un normale push di codice: nel repository privato si modifica `runs/v6.request` (con `variant=v63`) o si avvia il workflow a mano. Ogni fase stima la spesa prima delle chiamate e si rifiuta se supera il tetto.

Segreto richiesto nelle Actions: `OPENROUTER_API_KEY`.

## Hosting

Nessun sito è pubblicato. I progetti Vercel sono in pausa e senza costruzioni automatiche.
