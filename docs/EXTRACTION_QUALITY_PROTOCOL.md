# Ubik — protocollo di validazione della qualità estrattiva

**Stato: protocollo definito; revisione umana non ancora eseguita.**

## Obiettivo
Distinguere i segnali automatici di testo sostanziale dalla reale qualità di estrazione. Il confronto riguarda gli stessi URL e la stessa risposta HTML acquisita rispettando robots.txt, senza aggirare blocchi o salvare corpi di articoli protetti.

## Evidenza disponibile (16 ottobre 2026)
- Run [38968334318](https://github.com/nathanasso-code/Ubik/actions/runs/38968334318): 90 URL, soglia uniforme >=1200 caratteri e >=180 parole. HTML 40, Trafilatura 64, Readability 60; HTML+Trafilatura 65.
- Run [38968901524](https://github.com/nathanasso-code/Ubik/actions/runs/38968901524): HTML 40, Trafilatura 64 (25 aggiuntivi), Readability 61 (24 aggiuntivi). Nei 25 aggiuntivi di Trafilatura, zero segnali per le tre euristiche: frasi boilerplate predefinite, frasi lunghe duplicate, assenza di frasi lunghe.
- Queste euristiche **non verificano** pertinenza, completezza, contaminazione semantica, diritti o accuratezza.

## Revisione manuale proposta
Campione stratificato dei 25 URL aggiuntivi, includendo ogni editore con recuperi, più controlli positivi HTML e controlli negativi. La revisione deve essere eseguita su contenuti accessibili lecitamente, visualizzati transitoriamente, senza committare testi protetti.

Per ogni URL registrare: `url`, `publisher`, `reviewer`, `review_date`, `article_identity_match` (sì/no/incerto), `lead_present` (sì/no/incerto), `ending_present` (sì/no/incerto), `boilerplate_contamination` (nessuna/minore/alta/incerto), `article_body_sufficient_for_claims` (sì/no/incerto), `notes_without_copyrighted_excerpts`. Confrontare l'estrazione con la pagina originale ove possibile; non assumere che un testo lungo sia integrale.

## Criteri di avanzamento
Calcolare il numero di URL revisionati, quota di testo pertinente, contaminazione elevata, incertezza e accordo fra revisori (se almeno due). Non definire una percentuale di accuratezza senza un campione di riferimento. Usare i testi per analisi di affermazioni soltanto se il riferimento all'articolo è confermato e il testo è sufficientemente pertinente; le citazioni richiedono controlli separati di grounding.

## Architettura e costi
Trafilatura è l'estrattore principale candidato; Readability fallback; parser HTML baseline. L'estrazione resta locale e a costo LLM zero. Il contenuto protetto non deve essere ripubblicato né salvato nei report. Conservare URL, hash e metriche; i diritti di riutilizzo richiedono valutazione distinta.

## Prossimo esperimento
1. Revisione qualitativa stratificata dei 25 candidati con protocollo sopra.
2. Misurazione del guadagno **validato** rispetto ai 40 HTML baseline.
3. Benchmark semantico locale-first su documenti con contenuto sufficiente e provenienza verificata; distinguere recall dei candidati, precisione degli accorpamenti, grounding delle affermazioni e costo per decisione.
