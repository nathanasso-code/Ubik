# Ipotesi di ricerca — Web research assistita dall'IA per Ubik
**Data:** 2026-10-12  
**Stato:** PROPOSTA SPERIMENTALE, NON APPROVATA COME ROADMAP, NON IMPLEMENTATA, NON DISTRIBUITA.

## Motivazione
L'utente ha osservato che una domanda aperta rivolta a un assistente dotato di ricerca web — per esempio «quali notizie, controversie e punti di vista sull'IA sono emersi negli ultimi sette giorni?» — può produrre risultati più ricchi del feed derivato dai connettori gratuiti già configurati. Questo è un **problema da misurare**, non una superiorità empiricamente dimostrata. Gli RSS e le API acquisiscono soprattutto da sorgenti/query predefinite; un sistema di ricerca guidato da domande può generare query, cercare lacune, confrontare interpretazioni e recuperare documenti primari.

## Ipotesi
Integrare, **senza sostituire**, la raccolta multicanale con una capacità di ricerca web assistita da LLM, periodica per topic e/o attivata da questioni emergenti. Le ricerche devono produrre evidenze e metadati riutilizzabili nell'archivio indipendente, non risposte effimere rigenerate per ogni visualizzazione.

### Modalità da confrontare
- **A — Baseline esistente:** RSS, Mastodon, Bluesky, GDELT, scientific APIs e selezione documentata.
- **B — Ricerca guidata:** stessa finestra temporale e stesso topic, query formulate dall'IA, recupero di fonti primarie e voci critiche, confronto e sintesi citata.
- **C — Ibrido (eventuale):** segnali del sistema A che attivano ricerche B mirate, più ricerche periodiche a budget limitato.

## Caso studio suggerito
Topic IA: «Notizie, controversie e punti di vista emersi nell'ultima settimana». Ulteriore caso studio cross-topic: presunti attacchi a infrastrutture digitali russe, riduzione di traffico automatizzato e ipotesi di diminuzione di bot di disinformazione. Separare in modo verificabile: **evento infrastrutturale**, **metrica del traffico**, **attribuzione causale a bot politici**. Non assumere che il calo di crawler equivalga al calo di account di propaganda. Non considerare le descrizioni discusse in chat come fatti verificati nel repository: prima di usarle nel benchmark, raccogliere fonti e dati originali datati.

## Pipeline ipotizzata (non esistente)
1. Monitoraggio leggero, rilevazione di picchi, convergenze e divergenze; confronto con baseline storiche, non solo volume grezzo.
2. Riconoscimento di eventi e **affermazioni specifiche**, con genealogia delle fonti; evitare di confondere stessa notizia, stesso evento e stessa tesi.
3. Generazione di una **domanda verificabile e neutra** quando vi sia interesse e incertezza sufficienti.
4. Ricerca investigativa mirata: fonti primarie, controevidenze, riscontri indipendenti, misure alternative, limiti dei dati.
5. Sintesi con legami claim-evidence-source, grado di incertezza, citazioni, query e ricerche senza esito, data e revisione.
6. Possibile card epistemica evolutiva, **non automatica né obbligatoria**; selezione editoriale e criteri di pubblicazione da definire.

## Questioni economiche e tecniche da verificare
Un abbonamento consumer ChatGPT (circa 20 EUR/mese nel caso discusso) **non concede** capacità API equivalenti o utilizzo commerciale illimitato. I costi di un servizio autonomo includono chiamate di ricerca, token di modelli, recupero documenti, storage, retry, hosting, limiti provider e carico per topic/utenti. Eventuali tariffe e nomi dei modelli menzionati in chat **non sono prezzi verificati in questo documento**: ricontrollare i listini ufficiali al momento della valutazione, senza basare la roadmap su stime illustrative. Prevedere cache, deduplicazione, budget per topic, priorità alle questioni con valore informativo e limiti di spesa rigidi. L'accesso dei modelli a ricerca web può differire da quello dell'interfaccia ChatGPT; verificare funzioni, licenze, attribuzione e disponibilità.

## Protocollo di valutazione prima di decidere
- Congelare finestre temporali, topic e criteri di pertinenza per A/B; mantenere log di query, risultati e costi.
- Costruire un insieme di riferimento annotato: questioni significative, fonti primarie, prospettive contrarie, duplicati, falsi positivi e lacune.
- Misurare: copertura di questioni rilevanti, precisione delle fonti, varietà di origini **indipendenti**, capacità di recuperare obiezioni sostanziali, accuratezza e citabilità delle affermazioni, costo e latenza per indagine.
- Verificare anche falsi nessi causali, hallucination, bias di ricerca, ricerche negative non conclusive e riproducibilità.
- Solo dopo una valutazione esplicita scegliere se e come implementare la modalità B o C.

## Confini e decisione
**Nessuna approvazione allo sviluppo è implicita.** Non modificare API di produzione, frequenze di acquisizione, schema DB, UI o provider a pagamento sulla base di questa nota. Le implementazioni già presenti restano la baseline da preservare. Una nuova chat deve presentare questa idea come **ipotesi da validare**, non come prossimo step confermato.
