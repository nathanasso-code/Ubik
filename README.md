# Ubik

Aggregatore di notizie selezionate: le fonti si organizzano in fatti (card), vicende (matrici) e Topic, e l'informazione emerge dalle relazioni tra le fonti.

Riordinato il 29 ottobre 2026. Lo stato precedente dei tre rami è conservato, intero, nei rami `archive/2026-10-29-main` (vecchio sito a domande), `archive/2026-10-29-develop-ubik-core` (acquisizione e prototipi) e `archive/2026-10-29-experiment-v5.1` (pipeline v2–v5.1 con la sua cronologia).

## Struttura

| Cartella | Contenuto | Stato |
| --- | --- | --- |
| `ingestion/` | Estrazione e accorpamento: versione corrente v5.1 (`ubik_v51_prompts`, `ubik_ukraine_v51_*`), moduli comuni (`ubik_v5_extraction_validator`, `ubik_monarch_v5_rejudge_core` per recupero E5 e gruppi prudenti, `ubik_part_of_validator_v5`, `ubik_matrix_composer_v5`, `ubik_ukraine_v5_model_audit`, `ubik_shared_origin_v5`, `ubik_acquisition_provenance_v5`) e gli script delle versioni precedenti (v2–v5, piloti monarca, bracci dei giudici) come storia | Corrente: v5.1 |
| `prompts/v5.1/` | Prompt congelati di estrazione e giudizio, letti dagli script con controllo SHA-256 | Congelati |
| `protocols/` | Protocolli preregistrati | — |
| `docs/experiment-results/v5.1/` | Risultati della diagnosi sull'Ucraina, con `SHA256SUMS` e `ukraine-v51-report.md` | — |
| `acquisition/` | Scoperta RSS, verifica del testo accessibile, Mastodon, registri delle fonti | Riferimento, da rifare |
| `attacks-map/`, `scripts/`, `data/` | Mappa degli attacchi russi in Ucraina e pipeline UCDP, aggiornata ogni martedì | Conservata |
| `tests/` | Test del compositore v5 | — |

La documentazione di progetto vive nei documenti condivisi su Claude: "Ubik — Architettura e modello informativo", "Ubik — Diario sperimentale", "Ubik — Riferimenti di valutazione".

## Come si esegue la pipeline v5.1

Le esecuzioni a pagamento partono solo su richiesta esplicita, mai a un normale push di codice: si aggiunge o modifica il file `runs/<workflow>.request` (o si avvia il workflow a mano).

1. `runs/ukraine-v51-extraction.request` — estrazione (Sonnet 5.5).
2. Mappatura cieca degli eventi sul riferimento, congelata con hash prima dei giudizi.
3. `runs/ukraine-v51-pairs.request` — coppie candidate (E5-small, nessuna chiamata al modello).
4. `runs/ukraine-v51-judges.request` — giudici Sonnet e DeepSeek V4.1 Flash.
5. Valutazione: `python -m ingestion.ubik_ukraine_v51_evaluate ...`.

Segreto richiesto nelle Actions: `OPENROUTER_API_KEY`.

## Hosting

Nessun sito è pubblicato. I progetti Vercel sono in pausa e senza costruzioni automatiche.
