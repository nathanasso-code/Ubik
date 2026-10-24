# Protocollo sperimentale — Nomenclatura universale e ricostruzione di matrici/card (25 ottobre 2026)

**Stato: FORMALIZZATO, NON AVVIATO.** Non eseguire workflow, non inviare richieste API, non modificare produzione. Branch di ricerca `develop/ubik-core`.

## 1. Problema e risultati di partenza
Corpus congelato: 105 notizie da 39 testi originali, estrazioni e passaggi di fonte già conservati. Il run [40127100857](https://github.com/nathanasso-code/Ubik/actions/runs/40127100857) ha testato embedding titolo+sinossi con collegamenti anche entro lo stesso `source_id`, poi una revisione LLM congiunta matrici/card. Risultati osservati: Qwen 38 matrici/67 card, DeepSeek 36 matrici/62 card; 18 chiamate per modello; Qwen 1 errore con fallback, DeepSeek 0. Qwen ha riunito le quattro card sulle farfalle monarca in una matrice; DeepSeek ne ha proposte tre. Per l'Ucraina rimane frammentazione fra finestre preliminari e potenziali contesti comuni. Non esiste ancora valutazione umana sistematica.

**Distinzione causale:** l'embedding forma gruppi candidati (cosine e collegamenti tra fonti, poi componenti transitive); il modello LLM decide **dentro ciascun gruppo** quali notizie unire in card e quali card riunire in matrici. Il modello non può unire elementi che l'algoritmo non gli presenta insieme. Il validatore controlla partizioni di ID, non verità o coerenza delle decisioni.

## 2. Ipotesi
Una grammatica informativa riutilizzabile e un vocabolario di concetti normalizzati consentono a un LLM di etichettare ciascuna notizia **senza vedere le altre**. Un successivo confronto deterministico dei campi può recuperare identità di contesto (matrici) e di fatto (card), riconoscere reazioni/relazioni e ridurre le revisioni LLM. L'ipotesi NON presume che codici opachi siano semanticamente utili agli embedding.

## 3. Grammatica universale: campi
Ogni notizia riceve un record strutturato:
- `domain_ids`: uno o più domini di conoscenza, classificazione ampia non identitaria;
- `phenomenon_id`, `object_class_id`, `subtype_id`: tipo di fenomeno e classe dell'oggetto;
- `actor_entities`, `target_entities`: entità canoniche, con ruolo e livello di certezza;
- `predicate_id`: azione/evento normalizzato (decisione, sospensione, critica, osservazione, misurazione, ecc.);
- `referent`: evento, provvedimento, studio, oggetto o processo specifico cui il fatto si riferisce; includere identificatori pubblici se presenti, altrimenti firma composta da attributi verificabili;
- `time`, `place`, `scope`, `status`: tempo, luogo, ambito e stato del fatto, con valore `unknown` quando mancante;
- `relation_to_referent`: `reports`, `reacts_to`, `supports`, `contradicts`, `updates`, `caused_by`, `about` oppure `uncertain`; non inferire causalità da mera successione;
- `factual_aspect`: quale affermazione distintiva è riportata; `epistemic_status`: dichiarazione, adozione, osservazione, contestazione, ipotesi, ecc.;
- `evidence`: `news_id`, `source_id`, citazioni originali; nessuna fonte inventata;
- `unknown_fields`, `ambiguity_flags`, `alternative_referents`: esplicitare l'incertezza.

I concetti del vocabolario sono **classi** (es. sanzioni energetiche); i referenti sono **istanze specifiche** (es. uno specifico provvedimento). Una stessa fonte può contribuire a più card e matrici. I domini multipli non definiscono da soli la matrice.

## 4. Canonicalizzazione
Usare un registro versionato di classi, sinonimi, predicati, entità e referenti. Il modello può scegliere un ID esistente o proporre un nuovo termine con descrizione testuale, ma **non può creare autonomamente un ID canonico definitivo**. Un resolver deterministico usa prima identificativi espliciti e uguaglianze di firme; un match approssimativo genera candidati, non fusioni automatiche. In assenza di data, identificativo dell'atto o altri discriminanti, astenersi dalla fusione e segnalare il caso. Due sospensioni di sanzioni dello stesso tipo non sono necessariamente lo stesso provvedimento.

## 5. Formazione delle strutture
- **Matrice candidata**: notizie/card che condividono lo stesso referente canonico specifico, o che presentano una relazione esplicita verificabile con esso. Non aggregare per il solo tema generale. Se il referente è incerto, non fondere automaticamente.
- **Card candidata**: notizie che esprimono lo stesso nucleo fattuale (referente + predicato + attore/oggetto + attributi discriminanti); le reazioni di attori diversi restano card distinte, pur condividendo matrice. Una nuova informazione sostanziale può meritare card distinta.
- **Fonte**: documento originario e relativi estratti, separati dall'identità informativa; non dedurre indipendenza editoriale da source_id diverso.
- I codici strutturati e le relazioni possono sostituire **parte** della preselezione embedding. Embedding dei descrittori testuali è un fallback di discovery; mai usare embedding di codici opachi come se esprimessero semantica.
- Confronto deterministico non equivale a prova di equivalenza fattuale: produrre anche una coda di review per casi ambigui.

## 6. Esempi diagnostici
**Sanzioni Russia/Ucraina**: A, decisione degli Stati Uniti di sospendere sanzioni energetiche alla Russia; B, critica di Zelensky a quella decisione; C, valutazione favorevole di un rappresentante russo. `predicate_id` e attori diversi; `referent` identico **solo se** il provvedimento è effettivamente lo stesso. Risultato desiderato: una matrice specifica con card separate per decisione, critica e apprezzamento. Accordo sul diesel, cessate il fuoco energetico e altri sviluppi non si uniscono per la sola appartenenza al conflitto ucraino.

**Farfalle monarca**: notizie su trasmettitori, rotte e applicazioni possono condividere il referente 'stesso studio di tracciamento' e formare card distinte nella stessa matrice; le minacce ambientali possono essere un contesto separato se non sono parte dello studio. Verificare sui passaggi originali, non imporre l'esito.

**Hard negatives**: provvedimenti diversi con stesso attore/oggetto; due studi diversi sulla stessa specie; reazioni a decisioni differenti; fonti omnibus; notizie senza data o con riferimenti ellittici.

## 7. Disegno sperimentale (non eseguito)
1. Congelare input, estratti, versioni del prompt, registro e modelli; mantenere stessi 105 `news_id`.
2. Definire una grammatica minima e un registro iniziale di concetti condivisi. Usare campi obbligatori, `unknown` e JSON validabile; evitare un vocabolario smisurato nel prompt.
3. **Braccio N1:** DeepSeek etichetta ciascuna notizia isolatamente; nessuna visione globale, nessuna revisione LLM dei gruppi; ricostruzione deterministica matrice/card.
4. **Braccio N2:** medesima procedura con Qwen per misurare stabilità inter-modello, non per costruire consenso artificiale.
5. **Braccio N3 (ablation):** stessa grammatica senza registro canonico, per stimare il contributo del vocabolario condiviso.
6. **Baseline E:** output già ottenuto da embedding + revisione congiunta LLM, senza ripetere chiamate.
7. **Fallback F, opzionale e separatamente contabilizzato:** solo elementi ambigui vengono confrontati tramite embedding dei descrittori e/o LLM; non confondere con prestazioni della sola nomenclatura.
8. Audit umano cieco delle equivalenze, relazioni e distinzioni su esempi positivi e hard negatives; annotare i casi incerti, non usarli come oro.
9. Report per ogni braccio: copertura news/source, precision/recall di matrice e card su gold verificato, false fusioni e false separazioni, stabilità dei codici, qualità referenti, costo token/chiamate/tempo, casi di astensione, provenienza e citazioni.

## 8. Criteri di successo e fallimento
Successo se la classificazione indipendente ricostruisce matrici specifiche e card distinte con qualità almeno competitiva rispetto alla baseline e minore costo totale, **senza peggiorare le false fusioni** e senza perdere evidenze. Fallimento se il modello assegna descrittori troppo generici, inventa identità canoniche, fonde provvedimenti diversi, produce referenti instabili o richiede una revisione globale quasi completa. Nessuna soglia numerica di accuratezza è fissata senza benchmark annotato.

## 9. Vincoli operativi
Nessun run avviato con questo protocollo. Nessuna chiamata a OpenRouter, nessun workflow_dispatch, nessuna modifica di produzione. Conservare il documento e la sua revisione in GitHub come specifica, non come risultato. Una eventuale implementazione successiva dovrà usare branch di ricerca e revisione separata prima dell'avvio.
