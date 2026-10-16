# Primo benchmark LLM sulle coppie cross-source

## Baseline deterministica verificata
[Run #38972739584](https://github.com/nathanasso-code/Ubik/actions/runs/38972739584), success:
- 24 coppie campionate da 1.091 URL RSS; 11 coppie con entrambi i testi sopra 800 caratteri e 100 parole.
- 17 URL accessibili per queste coppie, 68 frasi numeriche.
- Allineamento lessicale di frasi numeriche: **4 coppie** con almeno un allineamento candidato, **8 allineamenti** totali, **7 differenze numeriche candidate**. Nessuna differenza è stata automaticamente dichiarata contraddizione.
- I numeri misurano copertura di un algoritmo lessicale, non accuratezza semantica.

## Primo confronto con modello linguistico
Implementato `ingestion/cross_source_llm_adjudication.py` e workflow `.github/workflows/cross-source-llm-adjudication.yml`. Il workflow usa il segreto esistente `UBIK_LLM_API_KEY`, endpoint Groq OpenAI-compatible e modello `llama-3.3-70b-versatile`. Budget **massimo quattro coppie per run**, testi transitori (fino a 7.000 caratteri per articolo), risposte JSON con relazione `same_event`, `related_distinct_event`, `different_event` o `uncertain`, più due citazioni testuali. Le citazioni sono verificate come sottostringhe esatte del testo estratto e **non persistite**; sono salvati solo giudizio proposto, motivazione breve, dettagli differenziali e esito di grounding. Le proposte non diventano accorpamenti automatici.

**Prima esecuzione avviata:** https://github.com/nathanasso-code/Ubik/actions/runs/38973064675. Non attribuire al modello alcun esito prima del completamento del run e dell'esame dell'artefatto.

## Limiti
- Il modello non fornisce automaticamente etichette gold; occorre valutazione manuale dei casi e delle differenze.
- Un grounding tramite substring non garantisce interpretazione corretta della citazione.
- Il modello potrebbe rifiutare la richiesta, incontrare errori API o ottenere testi insufficienti; registrare errori senza presentare il run come successo semantico.
