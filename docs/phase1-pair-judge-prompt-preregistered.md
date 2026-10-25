# Ubik — Prompt congelato per verifica ibrida livello 2
Registrato dopo la selezione E5-small ma **prima di qualunque chiamata di verifica LLM**.

## Modello
`anthropic/claude-sonnet-5.5` via OpenRouter, con `temperature: 0` dove supportato. Nessun modello alternativo scelto in base ai risultati. Una coppia per richiesta; nessun contesto globale.

## Ordinamento e dati
Ogni coppia è ordinata per `qualified_id` crescente, indipendentemente dalla similarità. Ogni evento fornisce esclusivamente: `qualified_id`, `actor`, `action`, `object`, `time`, `actuality`, `evidence`. Eventuali valori assenti restano null o stringhe vuote. Non includere gold, gruppo di riferimento, similarità, altre coppie, altri verdetti, esempi tratti dal corpus o identità di matrice.

## System prompt (letterale)
You are an independent event-identity judge. Decide whether two descriptions from different sources refer to the SAME concrete real-world event or act. The descriptions can emphasize different facets of the same act, but thematic similarity, shared actors, related consequences, reactions, or temporal proximity are NOT sufficient. A reaction to an act is distinct from the act. Two distinct official actions are distinct even if both concern sanctions, diesel, or Russia. Use only the two supplied event records. If evidence is insufficient to establish identity, answer uncertain rather than guessing. Do not infer hidden facts or use any other comparisons. Return only valid JSON with keys "decision" and "reason". Decision must be one of "equivalent", "distinct", "uncertain". Reason must be a brief explanation (max 40 words).

## User prompt (template letterale)
Event A:
{JSON record of lower qualified_id with exactly qualified_id, actor, action, object, time, actuality, evidence}

Event B:
{JSON record of higher qualified_id with exactly qualified_id, actor, action, object, time, actuality, evidence}

Decide whether A and B describe the same concrete event. Output only JSON.

## Tracciabilità
Salvare **ogni risposta grezza** prima di parsing e validazione, con modello, coppia, prompt version, decisione e motivazione. Non correggere decisioni dopo il confronto con il gold. Per fallimenti API/parsing registrare `uncertain` e errore; non sostituire con un altro modello senza un nuovo protocollo.

## Valutazione
1. Per ciascuna coppia verificata, classificare la decisione rispetto alle coppie positive congelate, A/B negative e altre negative certe; B2 e S408:E6 restano categorie escluse/ambigue.
2. Riportare matrice delle decisioni per coppia, falsi equivalenti, falsi distinti, incerti, accuratezza sulle coppie etichettabili.
3. Valutare separatamente gruppi prudenti (principale) e componenti connesse (secondario) sulle coppie **implicate dalla chiusura transitiva**, includendo falsi A/B e altre false fusioni.
4. Nessuna scelta post-hoc di soglia, prompt, modello o ordinamento.

## Limite
Una sola prova ibrida sul corpus; poi stop al livello 2 e nuovo gruppo di fonti.
