# Ubik — Regola congelata di composizione dei gruppi (livello 2)

Registrata **prima della verifica ibrida**. Integra, senza sostituire, `docs/phase1-candidate-selection-preregistered.md`.

## Distinzione fondamentale
Il recupero per coppia @5 misura le coppie *direttamente candidate*; **non** è il tetto delle coppie che potranno risultare equivalenti nei gruppi finali, poiché la transitività può ricostruire collegamenti non proposti direttamente.

## Regola principale: gruppi prudenti
Le verifiche del modello producono per ogni coppia esaminata `equivalente`, `distinta` oppure `incerta`. Le decisioni `incerta` non autorizzano fusioni.

1. Inizialmente ogni evento è un singleton.
2. Due singleton con una conferma `equivalente` formano un gruppo provvisorio di due.
3. Un evento entra in un gruppo con almeno due membri **solo** se dispone di almeno due conferme positive verso membri distinti di quel gruppo.
4. Qualsiasi decisione `distinta` fra l'evento candidato e un membro del gruppo impedisce l'ingresso; una decisione `incerta` non è positiva, ma non equivale a `distinta`.
5. Per unire due gruppi già formati, occorrono almeno due conferme positive *tra gruppi*, riferite a coppie di eventi distinte, e nessuna decisione `distinta` tra i membri dei due gruppi. Le unioni sono trattate come proposte da verificare, non come conseguenza automatica di un singolo arco.
6. Per evitare dipendenza arbitraria dall'ordine di scansione: elaborare prima le coppie confermate per similarità decrescente (pareggio per ID lessicografico), poi proporre gli ingressi e le unioni di gruppi in passaggi deterministici fino a stabilizzazione; un evento non può appartenere a due gruppi.
7. Se proposte concorrenti risultano incompatibili, **non forzare la scelta**: lasciare i membri non risolti separati e riportare il conflitto.

Questa regola è conservativa, ma non garantisce assenza di errori: due conferme positive possono essere entrambe sbagliate.

## Analisi secondaria: componenti connesse
Costruire le componenti connesse di **tutti** gli archi `equivalente` confermati, indipendentemente dalle regole prudenti, per misurare il guadagno e il rischio della transitività piena.

## Scoring sui gruppi finali
Per ogni gruppo finale, generare tutte le coppie non ordinate di membri (chiusura transitiva) e confrontarle con il riferimento congelato:
- vere positive recuperate, su 23 (e separatamente senza C);
- false fusioni tra A e B (24 possibili; soglia bloccante zero);
- altre false fusioni (soglia <=1);
- coppie non verificate direttamente ma recuperate per transitività;
- casi esclusi/ambigui B2 e S408:E6 riportati separatamente.

Valutare **entrambi** i metodi (prudente principale e componenti connesse secondarie) sugli stessi verdetti di coppia, senza cambiare soglie dopo aver visto il gold.

## Sequenza e limite
Attendere l'esito E5-small, applicare la scelta dei candidati già preregistrata, eseguire una sola fase di verifica ibrida; poi **stop al livello 2 su questo corpus** e passaggio a un nuovo gruppo di fonti. Nessuna modifica a `main`.
