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
