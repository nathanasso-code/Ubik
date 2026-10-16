# Ubik — Decisioni di prodotto e risultati sperimentali (16 ottobre 2026)

**Stato:** documento di continuità. Distingue decisioni di direzione, ipotesi ancora reversibili e risultati effettivamente osservati. Non implica funzionalità distribuite. Ramo di sviluppo `develop/ubik-core`; i workflow sperimentali OpenRouter sono stati aggiunti su `main`, senza integrazione automatica nel feed pubblico.

## Decisione aggiornata: due percorsi informativi, nessuna perdita delle fonti fuori topic

1. **Feed generale:** contiene fonti pertinenti anche se non assegnabili ai pochi topic curati inizialmente (probabilmente la maggioranza). Ogni fonte può avere **tag descrittivi** indipendenti dal catalogo topic. Se fonti multiple descrivono la stessa notizia/evento, il feed può presentare una **card epistemica** invece di ripetere le fonti. Una fonte singola può restare visibile come fonte, senza forzare una card multi-fonte.
2. **Topic:** contenitori selezionati e relativamente rari, scelti per importanza, qualità, densità informativa, convergenza e potenziale di dibattito. La classificazione verso topic esistenti è preferibile alla creazione di topic. La ricerca semantica deve consentire sinonimi e linguaggi differenti. Un tag **non è** un topic, e un hashtag ricorrente non crea automaticamente un topic.
3. **Card epistemica:** sintetizza **una singola notizia o sviluppo** sulla base di più fonti che convergono sullo stesso fatto/evento, preservando provenienza, differenze, incertezze e fonti originali. Non fondere eventi differenti solo perché trattano lo stesso tema; non scambiare ripubblicazioni per conferme indipendenti. L'eventuale visualizzazione di una fonte singola non va confusa con una sintesi multi-fonte.
4. **Nucleo:** oggetto **molto più raro** della card, riferito a una questione/sotto-argomento circoscritto, sufficientemente importante e persistente da ospitare **molteplici notizie/card, fonti e contributi anche contraddittori**. È soprattutto uno spazio di concentrazione della comunità, con potenziali funzioni social native (discussioni, contributi, prospettive, revisione documentata). La controversia può motivarlo, ma non è requisito necessario o sufficiente. **Non serve un nucleo se il topic è già sufficientemente specifico** per concentrare informazioni e persone. Un topic può avere zero nuclei e le card possono appartenere direttamente al topic.
5. **Tag:** metadati descrittivi, trasversali, ricercabili, con sinonimi e consolidamento semantico; non sezioni obbligatorie e non tassonomia di migliaia di categorie pubbliche. Conservare la diversità utile senza creare una categoria per ogni passaggio o singola fonte.

**Sintesi funzionale:** i topic concentrano l'attenzione; le card concentrano l'informazione su una notizia; i nuclei concentrano conoscenza e comunità su questioni persistenti. Il feed generale mantiene la copertura del resto del mondo informativo.

## Regola architetturale: convergenza prima di proliferazione

- Non produrre una gerarchia pubblica autonoma per ogni documento. Prima tentare assegnazione a topic/tag/strutture già esistenti; poi individuare sinonimi, cluster e relazioni; solo infine proporre nuove strutture quando il corpus e il confronto lo giustificano.
- Separare **appartenenza tematica**, **identità della notizia/evento**, **relazioni tra affermazioni** e **validazione epistemica**. Somiglianza semantica non prova identità dell'evento; dissenso non impedisce appartenenza a un medesimo nucleo.
- Mantenere identificativi stabili, original URL, provenienza, possibilità di split/merge reversibili, contributi social associati a identità persistenti.
- Distinguere cluster tecnici provvisori, card pubbliche e nuclei pubblicati. L'emersione automatica di un cluster non pubblica un nucleo.
- Favorire la **densità utile** di fonti per topic/nucleo, non il numero assoluto di categorie. Non penalizzare fonti uniche rilevanti; conservarle nel feed generale.
- Un nucleo può essere proposto anche per dibattito intenso e qualitativamente valido, ma va evitata duplicazione di comunità già concentrate in un topic.
- Promozione, moderazione, funzioni social, criteri quantitativi e UI dei nuclei **restano aperti**. Le decisioni di questa chat sono orientamento progettuale con riserve espresse per il futuro, non specifiche irrevocabili.

## Risultati verificati OpenRouter (16 ottobre): NON confondere esecuzione riuscita e qualità validata

La chiave OpenRouter funziona in GitHub Actions; Groq aveva prodotto 403 in precedenti tentativi. L'utente ha acquistato $10 di credito OpenRouter. Nessun acquisto/ricarica automatica viene richiesto dai workflow.

- Smoke test `38874914586`: HTTP 200, modello free, 29 token, costo riportato $0.
- Mini-test semantico `38875249797`: workflow verde ma risposte semantiche nulle; **test sostanzialmente non riuscito**.
- Primo pilot gerarchico `38875616111`: 4 documenti sostanziali, Qwen3 32B, **1/4** classificazioni accettate, costo riportato **$0.0011053**.
- Run `38876789583`: **fallimento per SyntaxError introdotto nel workflow**, prima di qualsiasi inferenza. Corretto nel commit `475e6d8`.
- Pilot corretto `38876908263`: 4/4 risposte non vuote, **1/4** classificazioni accettate, costo **$0.00054044**. Il problema delle risposte vuote è stato mitigato, non quello delle evidenze.
- Pilot esteso `38877451363`: **20 documenti analizzati, 6/20 classificazioni accettate (30%), 14 respinte per citazioni non identiche al testo**, costo riportato **$0.00323699**. Acquisiti **24 testi sostanziali**, **1.013.371 caratteri originali** complessivi. Modello `qwen/qwen3-32b`; risposte presenti per tutti e 20.
- Il corpus è **Europe PMC**, con richiesta `fullTextXML`, estrazione della sezione `body`, controllo preliminare della licenza, conservazione del corpo oltre 1.000 caratteri, filtro corpus di almeno **800 caratteri**; massimo **5.000 caratteri per documento** inviati al modello. Questi sono testi scientifici, **non** un benchmark rappresentativo di notizie, social e feed generalista. I controlli licenza non sostituiscono revisione legale per pubblicazione.
- Alcune gerarchie respinte erano tematicamente plausibili ma non soddisfacevano il controllo di **citazione verbatim**. Una gerarchia individualmente plausibile non dimostra coerenza tassonomica: radici alternative quali `Medicine`, `Healthcare`, `Health Sciences`, `Artificial Intelligence` frammentano contenuti vicini.
- Le citazioni esatte proteggono dalla fabbricazione, ma il loro fallimento deve essere diagnosticato **separatamente** dalla qualità semantica. La presenza della citazione non prova verità, identità dell'evento né pertinenza della categoria.
- Workflow: `.github/workflows/openrouter-hierarchy-pilot.yml` su `main`; artifact `openrouter-hierarchy-results`. Il limite cumulativo $0.02 è un **controllo tra richieste**, non un limite di fatturazione rigido. I workflow non sono una pipeline pubblica o schedulata.

## Piano operativo successivo — ipotesi da verificare, non già implementate

1. **Correggere la diagnostica delle evidenze**: preservare risposte valide/respinte, verificare citazioni su span reali e distinguere `format_valid`, `quote_grounded`, `topic_fit`, `event_identity`, `taxonomy_consistency`. Non aggirare la verifica testuale accettando parafrasi come citazioni.
2. **Corpus eterogeneo e riproducibile**: estendere oltre Europe PMC a RSS, giornalismo, arXiv, Wikinews e contributi social, con testi integrali o abstract estesi quando disponibili, URL e diritti conservati; documentare copertura e limiti. Evitare dipendenza esclusiva da Mastodon.
3. **Esperimento A/B sulla convergenza**: gerarchie libere per documento vs routing a vocabolario controllato e consolidamento dei sinonimi, usando gli **stessi testi**. Misurare frammentazione, numero di categorie con una sola fonte, copertura, precisione per topic, falsi accorpamenti, omissioni, qualità delle evidenze e costo.
4. **Card**: raggruppare la **stessa notizia** con classificatore ibrido embedding → LLM per casi ambigui; distinguere supporto, differenza, aggiornamento, contraddizione e semplice somiglianza; produrre sintesi con citazioni verificabili.
5. **Feed generale e topic**: verificare che documenti non assegnati ai topic rimangano visibili, con tag consolidati e card quando esistono fonti ridondanti. Misurare esplicitamente il tasso di fonti fuori topic.
6. **Nuclei**: soltanto proposta/valutazione offline per questioni persistenti con più card e contributi; evitare nuclei superflui rispetto ai topic. Rimandare pubblicazione automatica, social avanzato e validazione fino a test e decisioni editoriali.
7. **Integrazione e continuità**: verificare CI, portare workflow e risultati dal `main` al ramo di sviluppo con cautela, aggiornare documenti canonici e mostrare card/feed concreti. Non dichiarare feature live senza verifica di deploy.

## Documenti da leggere insieme

- `docs/ARCHITECTURE_CURRENT.md` — stato tecnico storico (13 ottobre), non sostituisce questo aggiornamento.
- `docs/EPISTEMIC_CARDS_AND_NUCLEI.md` — decisioni precedenti e distinzione di oggetti.
- `docs/meaning-relations-hierarchical-taxonomy.md` — contratto e risultati precedenti, **superati nella strategia di categorie libere per documento**.
- `docs/HANDOFF_UBIK_2026-10-13.md` — handoff storico e dettagli pipeline.
- GitHub Actions: https://github.com/nathanasso-code/Ubik/actions

**Stato di implementazione:** documentazione aggiornata; nessuna affermazione che routing generalista, consolidamento automatico, nuclei social o card sintetiche siano già funzionanti in produzione.
