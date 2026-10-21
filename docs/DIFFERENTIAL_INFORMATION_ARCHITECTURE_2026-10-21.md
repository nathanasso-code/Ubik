# Ubik — Architettura informativa differenziale e direzione sperimentale (21 ottobre 2026)

> **Direzione prioritaria di ricerca.** Il benchmark **identità fini + composizione differenziale** è probabilmente il risultato qualitativamente più promettente ottenuto finora nel riconoscimento delle differenze informative e nella generazione di sintesi distinte anche con fonti sovrapposte. Questa è una valutazione qualitativa provvisoria, **non** una superiorità quantitativa dimostrata né una pipeline pronta per la produzione. Va preservato il principio architetturale e verificato contro i testi originali.

## Obiettivo espresso per Ubik

Non massimizzare il numero di card né raggruppare automaticamente gli articoli più simili. **Massimizzare le card pertinenti**, riducendo accorpamenti impropri, separazioni superflue, omissioni sostanziali e ripetizioni. Due fonti molto simili possono contenere contributi diversi; due fonti con focus diversi possono concorrere alla stessa sintesi. Una fonte può sostenere più card, ma le card devono distinguersi per ciò che **raccontano**, non per le fonti elencate.

**Principio guida:** la fonte è il contenitore; l'affermazione/contributo informativo è l'unità di analisi; la card è l'unità editoriale di presentazione. Sono i nuclei informativi a determinare quali fonti sostengono una card, non viceversa.

## Architettura logica (non equivale al numero di chiamate)

1. **Acquisizione e provenienza:** conservare URL, titolo, testo/abstract esteso, fonte, qualità dell'estrazione; escludere navigazione, sidebar e contenuti estranei. La soglia di 800 caratteri non certifica da sola la qualità.
2. **Interpretazione indipendente delle fonti:** sintesi fedele, focus centrale, identità/affermazioni fini e contributi distintivi; non perdere le differenze sostanziali.
3. **Relazioni fra informazioni:** equivalenza, sovrapposizione, complementarità, differenza e contraddizione, senza trasformare ogni differenza in una card.
4. **Composizione differenziale:** costruire sintesi coerenti, ciascuna centrata su uno sviluppo informativo sostanzialmente autonomo. Le fonti possono ricorrere fra card, le sintesi no. Non forzare eventi estranei in un'unica card.
5. **Controllo di autonomia:** prima di tenere due card separate, chiedere se fonderle farebbe perdere una distinzione sostanziale o produrrebbe semplicemente una sintesi migliore. Accorpare dettagli naturalmente complementari; separare sviluppi realmente autonomi.
6. **Controllo di copertura:** destinare ogni identità a una card, oppure classificarla come ridondante, secondaria, o importante ma omessa. Le omissioni importanti richiedono revisione. Validare contro il testo originale, non soltanto contro l'output LLM.

## Evidenze empiriche e limiti

- **Identità fini originali:** 39 fonti, 8 contesti, 296 identità estratte, 55 chiamate nella fase di estrazione. Run [39315292356](https://github.com/nathanasso-code/Ubik/actions/runs/39315292356).
- **Composizione differenziale dalle identità fini:** 8 ulteriori chiamate, 42 card (35 multi-fonte) e 115 identità non assegnate a card, secondo l'artifact dell'esperimento. Run [39481724930](https://github.com/nathanasso-code/Ubik/actions/runs/39481724930). **Totale storico: 63 chiamate.** Le 115 identità non assegnate NON equivalgono automaticamente a 115 fatti importanti perduti: possono essere ridondanti, secondarie o effettivamente omesse. Non è stato effettuato un audit completo della loro importanza.
- **Focus + sintesi in una chiamata per contesto:** 8 chiamate, 16 card, 37/39 fonti restituite e cinque contesti senza card. Run [39484188764](https://github.com/nathanasso-code/Ubik/actions/runs/39484188764). Ridurre troppo le chiamate può compromettere la copertura.
- **Due passaggi (interpretazione + composizione):** workflow [39618122791](https://github.com/nathanasso-code/Ubik/actions/runs/39618122791), concluso con successo tecnico; la qualità editoriale va valutata separatamente.
- **Errore tipico di granularità:** due fonti NPR quasi duplicate sulle farfalle monarca generano diverse card sui dettagli del medesimo progetto. La differenza di dettagli non implica automaticamente autonomia giornalistica.
- **Rischio opposto:** contesti complessi come sanzioni Russia/Ucraina contengono reazioni e conseguenze che non devono essere cancellate soltanto per ridurre il numero di card.

## Nuovo esperimento: autonomia + audit esaustivo

Codice: `ingestion/frozen_qwen_autonomy_audit.py`; workflow: `.github/workflows/ubik-autonomy-audit.yml`.

Si riutilizzano le identità fini congelate per un confronto controllato. Per ciascuno degli 8 contesti:

- **Chiamata 1:** composizione differenziale con vincolo di autonomia sostanziale; no card per dettagli marginali, no fusioni di sviluppi non correlati.
- **Chiamata 2:** revisione indipendente delle card proposte e classificazione **esaustiva** delle identità: assegnata a card, ridondante, secondaria, importante ma scoperta. Gli ID non contabilizzati sono segnalati separatamente; nessun taglio silenzioso a 160 identità.

**Budget sperimentale previsto:** 16 nuove chiamate; **71 chiamate equivalenti** se si includono le 55 già sostenute per l'estrazione iniziale. Non è ancora l'architettura ottimizzata di produzione. Il valore del test è isolare l'effetto del controllo editoriale, prima di tentare una compressione dell'estrazione.

**Metriche primarie:** falsi accorpamenti, false separazioni, card non autonome, fatti importanti omessi, supporto effettivo nel testo originale, ridondanza delle sintesi. **Metriche secondarie:** numero di card, numero di chiamate, token e costo. Un numero maggiore di card non indica automaticamente un risultato migliore.

## Stato e decisioni

- **Promettente / direzione da seguire:** identità informative fini → relazioni → composizione differenziale → controllo autonomia/copertura.
- **Implementato sperimentalmente:** estrazione e composizione; nuovo benchmark di revisione editoriale.
- **Non ancora dimostrato:** superiorità statistica sulle alternative; classificazione perfetta delle 115 identità; ottimizzazione del costo end-to-end; fedeltà verificata manualmente per tutte le card; robustezza su corpus ampio e vivo.
- **Non fare:** assumere che una fonte possa appartenere a una sola card; imporre quote fisse di card; confondere somiglianza di argomento con identità dello sviluppo; scartare informazioni senza traccia; promuovere un esperimento a pipeline di produzione senza validazione.

Prossimo passo: confrontare le card revisionate con il benchmark delle 42 card **sulle stesse fonti originali**, classificando casi concreti di miglioramento e regressione; poi ridurre il costo dell'estrazione senza sacrificare le differenze riconosciute.
