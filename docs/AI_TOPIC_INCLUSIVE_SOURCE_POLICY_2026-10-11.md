# Ubik — Politica di ampia inclusione e revisione personale (2026-10-11)

**Decisione:** prima ampliare il catalogo, poi eventualmente filtrare o aggregare. Il pilota da 30 card resta solo una vista; non è un limite all'archivio o alla lista fornita al revisore.

## Esclusioni sicure applicabili subito
1. **Record tecnicamente inutilizzabili**: URL mancante/non HTTP(S) o titolo vuoto; registrare quanti e perché. Non equivale a dichiarare non valida la fonte.
2. **Stesso identico URL acquisito più volte**: una riga-documento con tutte le provenienze conservate; non sopprimere URL diversi che descrivono lo stesso evento.
3. **Errore verificabile di recupero**: non spacciare una richiesta fallita per una fonte letta; mantenere il report di errore e consentire nuovi tentativi.
4. **Limite di visualizzazione**: non è un'esclusione editoriale. Non usare l'età, il prestigio del publisher, l'assenza di abstract, il numero di citazioni o la mancanza di copertura indipendente per scartare il documento.

## Non escludere automaticamente
- Paper arXiv senza peer review; analisi e opinioni di esperti; comunicazioni delle aziende; documenti unici; notizie non ancora corroborate; articoli datati; documenti senza tag specifici; testi non inglesi; contenuti con segnale AI incerto.
- Una fonte potenzialmente irrilevante per il topic può rimanere in catalogo con `needs_topic_review` anziché scomparire.
- Non confondere fonte, autore, editore e origine indipendente.

## Tre esportazioni complementari nel workflow
- `UBIK_ALL_SOURCES_REVIEW.csv` e `.json`: **tutti i documenti validi acquisiti** dalle fonti configurate, senza filtro temporale o di pertinenza, con URL originale, descrizione, provenienza e suggerimento tematico; dimensione variabile in base al live run.
- `UBIK_ALL_AI_TOPIC_SOURCES.csv`: **tutti** i candidati del filtro AI esistente (nell'ultimo run circa 105), non solo 30. Questo filtro euristico mantiene per ora una finestra di 14 giorni: **non** è un catalogo completo di tutta l'AI acquisita. Per recuperare falsi negativi consultare il catalogo generale.
- `UBIK_TOPIC_AI_REVIEW.html`: solo 30 elementi visibili per il prototipo, senza effetto sugli altri due file.

**Importante:** l'archivio può includere migliaia di documenti fuori tema perché alcune fonti configurate sono generaliste. Non descriverli come migliaia di articoli AI. Nessuna valutazione automatica di qualità o verità. Non è stata ancora dimostrata una copertura completa del panorama internazionale: i feed che falliscono, le fonti non configurate e i contenuti non RSS restano lacune.

## Prossima verifica
Verificare la riuscita della nuova GitHub Action e i conteggi effettivi dei tre export. Far leggere all'utente la lista ampia prima di introdurre ulteriori filtri. Successivamente annotare errori osservati e discutere aggregazione e selezione a partire da esempi concreti.
