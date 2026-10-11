# Ubik — Motore informativo in sei fasi (decisione progettuale, 2026-10-11)

## Obiettivo
Ingestione ampia, continuativa e sostenibile; estrazione attribuita del messaggio di ogni documento; misura osservabile della diffusione; aggregazione soltanto quando la relazione semantica è verificata; scoperta mirata di commenti e analisi; percorso autonomo per informazioni poco diffuse. Il pilota esistente (circa 2.849 URL raccolti, 106 candidati recenti nel run verificato) è una base, non una prova di copertura completa. Budget futuro per fonti premium nell'ordine di poche decine di euro al mese, non autorizzato ora.

## Fase 1 — Raccolta continuativa
- Scheduler a intervalli differenziati per feed, con HTTP conditional GET (ETag/Last-Modified), retry limitato, backoff, timeout, quota per host e report dei feed guasti; persistenza del cursore e della provenienza.
- RSS, Atom e API ufficiali prima di scraping; conservare URL, titolo, data, autori indicati dal feed, editore, lingua, abstract e data di osservazione. Non confondere editore con autore.
- Deduplica URL canonico e, separatamente, hash del contenuto; nessuna cancellazione dei diversi documenti sul medesimo evento. Archivio completo e viste tematiche separati.
- Non accedere a paywall, social chiusi o contenuti non autorizzati. Spesa esterna iniziale zero, con misurazione di chiamate e copertura.

## Fase 2 — Estrazione del messaggio
- Tre livelli, sempre dichiarati: `title_only` (non sintetizzare oltre il titolo); `feed_summary` o `abstract` (sintesi attribuita del testo disponibile); `full_text` (solo se ottenuto lecitamente, con estratti/ancore).
- Struttura: `central_message`, `supporting_evidence`, `claim_type` (fatto riportato, risultato degli autori, ipotesi, opinione, marketing), `source_basis`, `limitations`, `review_status`, `language`.
- Parsing deterministico ed estrazione economica come primo livello; LLM a basso costo solo per messaggi non ricostruibili in modo affidabile, sintesi cross-documento o testi complessi; cache per hash/versione del prompt, budget e audit dei campioni.
- Nessuna trasformazione dell'abstract di un preprint in risultato indipendentemente verificato.

## Fase 3 — Misura della diffusione
- Ricercare riferimenti al **documento** (URL, DOI, titolo, autori) e al **fatto/tesi specifica** (entità, data, azione, risultati). Non usare soltanto parole chiave generiche.
- Distinguere: `document_mentions`, `event_mentions`, `independent_origins`, `syndicated_reposts`, `citations`, `social_discussion`, `time_velocity`. Ogni conteggio richiede URL/provenienza e finestra temporale.
- Indice di attenzione separato da attendibilità e qualità: nessun conteggio stimato presentato come esaustivo. Mancanza di riscontri = `not_measured` o `no_results_in_checked_sources`, non irrilevanza.
- Misurare costi/limiti API prima di aggiungere fornitori commerciali. Effettuare ricerche mirate sui candidati, non su ogni documento a ogni ciclo.

## Fase 4 — Card epistemiche
- Cluster = stesso evento delimitato o stessa tesi/discussione **esplicitamente identificata**. Relazione generica di topic non è identità di evento.
- Card: titolo informativo, sintesi con attribuzioni e grado di evidenza, fonti originali e derivate distinte, rimandi di approfondimento, data, controversie, ultimo aggiornamento.
- Mai fondere automaticamente documenti sulla base del solo overlap lessicale; `proposed_relation` finché non c'è evidenza sufficiente. Mantenere singole card per contributi autonomi.

## Fase 5 — Ricerca mirata di discussioni
- Per le card candidate ad alta attenzione, cercare il link specifico e le espressioni della tesi su web, forum e social con API/feed pubblici disponibili e conformi.
- Conservare commenti critici e favorevoli, autore e contesto pubblico, distinguendo condivisione senza commento, opinione, contestazione documentata, correzione e ricerca indipendente.
- Nessuna equivalenza tra numero di post e consenso; no metriche di reputazione prive di benchmark.

## Fase 6 — Percorso per fonti poco diffuse
- Non penalizzare per assenza di menzioni. Ricercare citazioni DOI, bibliografie, paper correlati, implementazioni, repliche, discussioni specialistiche e collegamenti a problemi persistenti.
- Priorità esplorativa basata su originalità dichiarata, precisione del problema, accessibilità delle prove e potenziale di collegamento, **non** su verità presunta.
- Card epistemica autonoma quando esiste un contributo informativo specifico anche con una sola fonte; se emergono relazioni documentate, collegare fonti e card, senza inventare convergenza.

## Strategia economica
1. Sempre: raccogliere e memorizzare metadati e abstract una volta; riutilizzare la cache.
2. Solo novità/cambiamenti: estrazione incrementale, deduplica, traduzione su richiesta.
3. Solo candidati selezionati: ricerca esterna di rimandi e analisi AI più profonda.
4. Solo temi caldi o temi di nicchia promettenti: aggiornamenti frequenti, ricerca social e sintesi evolutiva.
5. Telemetria obbligatoria: documenti/giorno, percentuale con messaggio sufficiente, costo per documento, numero di riferimenti con URL, indipendenza delle origini, precisione delle aggregazioni, errori e falsi negativi.

## Sequenza di sviluppo verificabile
A. Prototipo di estrazione su 30 documenti con marcatura `title_only/abstract/feed_summary` e revisione manuale di accuratezza.
B. Raccolta di evidenze di rimando per 10 notizie diverse, con URL e date; distinguere stesso documento e stesso evento.
C. Creare 2–3 card reali, senza fondere articoli per sola vicinanza tematica.
D. Testare una fonte poco diffusa e una notizia ampiamente diffusa, comparando costi, lacune e qualità.
E. Solo dopo, automatizzare ranking e attivare canali social.

**Guardrail:** nessuna pubblicazione automatica, nessun numero di menzioni inventato, nessun abbonamento o spesa senza autorizzazione, nessuna modifica a produzione/main.
