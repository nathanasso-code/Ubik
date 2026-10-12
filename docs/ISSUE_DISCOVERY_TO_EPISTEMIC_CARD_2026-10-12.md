# Dalla scoperta alla card epistemica — contratto proposto (2026-10-12)

**Stato:** specifica progettuale; non equivale a un sistema operativo, pubblicazione automatica o approvazione di API a pagamento.

## Decisione metodologica
La sintesi **deriva dalle fonti**. L'IA può proporre *domande e piste di ricerca* prima di aver verificato le risposte; non può presentare come accertate affermazioni non sostenute dalle evidenze raccolte. Le fonti precedono l'identificazione della questione e possono essere ampliate dopo tramite ricerca mirata. Una card può essere provvisoria e incompleta, ma non priva di attribuzione.

## Flusso minimo
1. **Osservazioni**: acquisire articoli, paper e contributi social con provenienza e URL originali; distinguere osservazione da documento.
2. **Candidate issue**: raggruppare contenuti su stesso evento/affermazione, identificare interesse e tensioni; non fondere eventi soltanto per parole chiave.
3. **Topic routing**: scegliere un topic primario esistente con motivazione e punteggio di incertezza; possibili topic secondari. Se non è chiaro, lasciare `topic_unresolved` per review; non creare topic arbitrari.
4. **Question framing**: formulare una domanda neutra e specifica. Registrare le osservazioni che hanno generato la questione.
5. **Evidence expansion**: cercare fonti primarie, misure, documenti originali, voci critiche, conferme indipendenti; le ricerche negative non dimostrano assenza di prove.
6. **Card draft**: titolo, breve sintesi argomentata, punti accertati/contestati/ignoti, legami claim-to-evidence-to-source e revisioni. Solo affermazioni supportate; altrimenti riportare l'incertezza.
7. **Editorial gate**: evitare pubblicazione automatica di accuse, causalità e affermazioni ad alto impatto senza controlli. Distinguere bozza interna da card visibile. Revisione continua quando emergono nuove evidenze.

## Entità da mantenere distinte
- `observation`: dove e quando un contenuto è stato segnalato.
- `document`: articolo, paper, post originale, dato o rapporto; URL e autore.
- `issue`: domanda aperta persistente; non coincide necessariamente con evento o topic.
- `claim`: affermazione verificabile, attribuita a una fonte.
- `evidence`: passaggio citato, dato o documento a sostegno/contrasto di un claim.
- `card_revision`: sintesi datata con motivazione delle modifiche.
- `topic`: contesto di navigazione; una issue può avere topic primario e secondari.

Una condivisione Mastodon di un articolo è un'osservazione distinta dall'articolo. Dieci condivisioni non equivalgono a dieci conferme indipendenti.

## Bozza di output per un esperimento offline
```json
{
  "schema_version": 1,
  "issue_id": "stable-identifier",
  "topic_id": "existing-topic-or-null",
  "topic_status": "proposed",
  "trigger_observation_ids": [],
  "question": "Domanda neutra?",
  "card": {
    "title": "Titolo non assertivo",
    "summary": "Sintesi attribuita e provvisoria",
    "status": "draft_review_required"
  },
  "claims": [
    {
      "text": "Affermazione verificabile",
      "status": "unverified",
      "supporting_evidence_ids": [],
      "contradicting_evidence_ids": []
    }
  ],
  "sources": [
    {
      "document_id": "document-id",
      "role": "primary_candidate",
      "primary_status": "unverified",
      "origin_observation_ids": []
    }
  ],
  "missing_evidence": [],
  "research_queries": [],
  "review_required": true
}
```

`primary_candidate` non significa fonte primaria confermata. Per esempio, un articolo che cita un report non è il report; un post che condivide una notizia non è una conferma indipendente. Le affermazioni della card devono avere evidenze esplicite e riconducibili ai documenti.

## Cosa abbiamo già
- `ingestion/contracts.py`: osservazioni provider-agnostic.
- `ingestion/topic_feed_pilot.py`: selezione per topic basata su metadata e keyword.
- `ingestion/topic_event_review.py`: candidate pair, non clustering verificato.
- `ingestion/topic_evidence.py`: estratti letterali dai feed, non claim verification.
- `ingestion/social_source_catalog.py`: prototipo di URL esterni dai post social.
- `ingestion/topic_quality_views.py`: tre livelli Esplora/Rilevanti/Essenziali offline.
- `supabase/migrations/002_source_topic_catalog.sql`: schema proposto, non applicato.
- `docs/RESEARCH_HYPOTHESIS_AI_WEB_INVESTIGATION_2026-10-12.md`: ipotesi non approvata di ricerche iterative IA.

## Prima prova sensata
Su un campione reale già acquisito del topic IA, costruire offline 5–10 *candidate issues* con osservazioni e citazioni. Valutare manualmente: issue corrette vs accorpamenti errati, routing nel topic, qualità delle domande, presenza di fonti primarie, affermazioni senza evidenza, costo e tempi. Solo dopo introdurre sintesi LLM e ricerche integrative, confrontandole con la baseline senza ricerca. **Non introdurre una card automatica in produzione prima di questa verifica.**

## Primo incremento di codice — 2026-10-12

Implementati sul branch `develop/ubik-core`:
- `ingestion/issue_candidates.py`: produce fino a 10 seed di questioni **per singolo documento** da `ingestion/topic_evidence.py`, conservando URL, estratti letterali, topic ereditato, identificativo deterministico e necessità di review.
- `ingestion/issue_candidates_cli.py`: esportazione JSON offline con `python -m ingestion.issue_candidates_cli <evidence.json> <issues.json> --limit 10`.
- `tests/test_issue_candidates.py`: casi di grounding, duplicati e input invalidi.

**Limite cruciale:** questi sono seed di domande, **non** questioni/eventi raggruppati semanticamente, non riconoscimento di controversie, non classificazione verificata di fonti primarie e non sintesi IA. Il campo `card.summary` resta `null`, `publication=blocked`, `controversy=not_assessed`. Non è stato ancora eseguito il confronto su 5–10 questioni reali del pilot né verificato un esito CI: controllare GitHub Actions e acquisire il report reale prima di dichiarare il test riuscito. Nessun servizio esterno a pagamento è stato attivato.

## Campione concreto e verifica CI (2026-10-12)

Il dossier esistente `data/ai-topic.json` contiene 30 fonti e 18 contributi social associati. La coda di revisione di 10 elementi è salvata in `data/evaluation/ai-issue-review-2026-10-12.json`. **Non** è un campione scoperto automaticamente dalla pipeline live: è ricavato dal dossier editoriale esistente e ordinato per numero di prospettive social associate. I dati non certificano controversie, identità di evento o natura primaria delle fonti.

Aggiunti `ingestion/ai_issue_review.py` e `tests/test_ai_issue_review.py` per una trasformazione riproducibile del dossier in issue seed e per mantenere separati documento originale e post social. La card non ha ancora una sintesi generata, né claim validati. L'esperimento non ha ancora verificato semanticamente i 10 candidati.

**Blocco operativo:** il workflow `Ubik Core checks` su `develop/ubik-core` risulta in **failure** per il run https://github.com/nathanasso-code/Ubik/actions/runs/38307523619 e per il successivo run del commit `d2bee108`. Il job segnala failure nel passo `Run offline source discovery tests`, ma il dettaglio dei test falliti non è stato recuperato. Non affermare che i nuovi test passino o che la baseline CI sia sana. Priorità: recuperare log/annotazioni del job e correggere la causa, quindi ripetere il test.

## Correzione metodologica — ampiezza e scelta degli argomenti (2026-10-12)

La selezione di 10 elementi dal dossier di 30 fonti **non misura le principali questioni emergenti**: è solo un campione interno di review, condizionato dalle fonti già note e dalle associazioni social già registrate. Il numero di post legati ai 30 documenti non rappresenta l'intensità pubblica dei temi. Non chiamare questo campione *trend detection*.

Per scoprire le questioni serve un universo di osservazione più ampio e distinto dalla selezione editoriale: RSS e siti originari, social (Mastodon e Bluesky), API di scoperta e, in ipotesi sperimentale separata, query di ricerca web iterative per trovare eventi sfuggiti alla lista. Aggregare prima le osservazioni in candidate issues/claims/eventi, mantenendo i documenti autonomi; solo dopo calcolare attenzione, crescita rispetto alla baseline, diffusione tra comunità e fonti indipendenti, diversità di posizioni, nuovi documenti primari, densità di evidenza e persistenza. Distinguere tre casi: un tema molto trattato, una controversia sostanziale e un documento specialistico di alto valore ma poco rilanciato. Evitare di attribuire autorità alle ripetizioni coordinate o di cancellare contributi di nicchia.

Primo benchmark appropriato: prendere l'intero corpus acquisito nella stessa finestra temporale, misurare quanti candidati emergono rispetto ai 30 selezionati, confrontare con una ricerca web esplorativa e annotare manualmente falsi positivi, topic e fonti primarie. Solo dopo calibrare soglie e costi. La ricerca IA resta ipotesi non approvata; nessun provider a pagamento va attivato sulla base di questa nota.

**CI:** il run https://github.com/nathanasso-code/Ubik/actions/runs/38307523619 segnala 195 test Python, due fallimenti in `tests/test_social_source_catalog.py`: un'espressione regolare che estrae URL fantasma e provoca duplicati. Correzione del regex effettuata nel commit `257a71ae` su `develop/ubik-core`; verificare il run successivo prima di affermare che il CI è verde.

## Espansione delle osservazioni e priorità di attenzione (2026-10-12)

Decisione sperimentale: privilegiare **(1) convergenza delle condivisioni indipendenti** e **(4) intensità/qualità del dibattito**, con segnali secondari da misurare (accelerazione rispetto a baseline, diversità delle comunità, novità probatoria e tutela delle fonti specialistiche poco popolari). Non equiparare account distinti a origini indipendenti, risposte numerose a dibattito sostanziale o attenzione a verità.

Implementati `ingestion/source_expansion_candidates.py` (estrazione offline di account Bluesky e domini da un dossier) e `ingestion/issue_attention_triage.py` (priorità fondata su gruppi di origine **esplicitamente verificati** e risposte sostanziali con ragione e URL documentati). `tests/test_source_expansion_attention.py` copre i due criteri e impedisce di promuovere automaticamente i conteggi grezzi. Dati osservati nel dossier `data/ai-topic.json`: **17 account Bluesky distinti e 11 domini sorgente candidati**; report `data/evaluation/ai-source-expansion-candidates-2026-10-12.json`. Si tratta di ampliamento della **lista di candidati**, NON di 17 nuovi account monitorati o 11 feed RSS attivati: disponibilità, pertinenza e autorizzazioni sono da verificare.

Il workflow `Ubik Core checks` è tornato verde dopo la correzione regex di `ingestion/social_source_catalog.py` (run https://github.com/nathanasso-code/Ubik/actions/runs/38310309636). I run dei nuovi moduli risultano successivi e completati con successo (es. https://github.com/nathanasso-code/Ubik/actions/runs/38311095843). Restano da realizzare: acquisizione live su un campione ampio e diversificato, classificazione qualitativa dei dibattiti, verifica di indipendenza delle condivisioni, normalizzazione delle URL esterne, misurazione dei picchi temporali, clustering delle issue e produzione di card con evidenze. Non considerare i risultati come trend detection già operativa.
