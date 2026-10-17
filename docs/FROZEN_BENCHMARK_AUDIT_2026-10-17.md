# Ubik — Audit comparativo congelato (17 ottobre 2026)

## Esito operativo e limiti

**Non esiste ancora una prova che uno dei metodi end-to-end sia il migliore.** I precedenti esperimenti su 43 fonti con testi estesi e quello metadata-first su 979 fonti non condividono un campione valutato con gli stessi criteri. Il confronto diretto dei loro tassi di accorpamento sarebbe metodologicamente scorretto.

È stato introdotto un **benchmark riproducibile a 23 fonti** con input bloccati agli artifact GitHub del 17 ottobre: corpus metadata-first del run 39052746507 e output critico del run 39063389188. Codice `ingestion/frozen_comparison_benchmark.py`, workflow `.github/workflows/frozen-method-comparison.yml`. I 23 articoli erano **già stati selezionati da Qwen**, perciò il campione è intenzionale, non rappresentativo. Le etichette sono una prima lettura editoriale dei metadati, non un gold standard indipendente o verificato su testi integrali.

### Misurazione riproducibile del sottoinsieme

- 23 fonti, 253 coppie possibili.
- 238 coppie valutabili; 15 coppie interne al caso della raccolta delle olive lasciate **indeterminate**.
- **TF-IDF, sole coppie direttamente candidate:** 34 TP, 14 FP, 6 FN, 184 TN; precisione 70,8%, recall 85,0% **sul sottoinsieme selezionato**.
- **Qwen, dopo consolidamento e revisione critica:** 40 TP, 0 FP, 0 FN, 198 TN; precisione e recall 100% **sulle etichette preliminari**. Questi numeri NON dimostrano un'accuratezza reale del 100%: le etichette sono ricavate dagli stessi titoli e descrizioni esaminati dal modello, e il caso più controverso è escluso dalla metrica.
- Le 14 coppie candidate false del filtro lessicale includono **foto del Papa vs dimissione** e **delegazione europea vs attacco ai raccoglitori**. È corretto che il filtro le recuperi come candidati, purché non diventino card automaticamente.
- **Il confronto fra i 43 URL del precedente esperimento full-text e questi 23 URL ha intersezione zero**: non esiste una comparazione A/B dei due metodi.

### Esame editoriale delle decisioni del vecchio metodo

Il run 39041792692 proponeva 4 card su 43 fonti. Due richiedono particolare cautela:
1. `D14` BBC: *Trump waives several Russia sanctions as row with Zelensky intensifies* + `D32` Guardian: *The Guardian view on Trump’s deal with Putin: grim and grubby, but not gamechanging*. **Sospetto falso accorpamento**: notizia e commento/editoriale non condividono necessariamente uno sviluppo specifico. Non dichiarato errore certo senza lettura integrale.
2. `D18` BBC: *BBC Inside Science* + `D38` Guardian: *How an accelerating Earth led experts to adopt the leap hour*. **Identità non dimostrata dai metadati**, poiché il titolo BBC è generico; serve il contenuto della puntata.
3. `D16` BBC video haze + `D29` France24 salute pubblica + `D43` Guardian dry ice: **possibile fusione di sviluppi distinti** di una stessa crisi, da verificare.
4. `D20` Deutsche Welle proteste studentesche Albania + `D7` Al Jazeera reazione del premier: **possibile fusione fra evento e reazione**, da verificare.

### Esame editoriale del nuovo metodo

Run 39063389188: 6 card candidate su 23 fonti. Separazione Papa dimissioni (9 fonti) / foto (2) plausibile; farfalle NPR (2) probabile duplicazione editoriale, non corroborazione indipendente; Guardian podcast/video (2) stesso tema/contenuto in formati differenti; delegazione europea (2) apparentemente stesso episodio. **Sei fonti sugli attacchi durante la raccolta delle olive restano non confermate come unico incidente**: la somiglianza di protagonisti, periodo e contesto non basta. Non assegnare a queste sei fonti una conferma di SAME_EVENT finché non sono confrontati testi originali, data, luogo e vittime.

### Costo e complessità

Il nuovo percorso ha almeno quattro trasformazioni: recupero TF-IDF, valutazione Qwen per finestre, consolidamento dei conflitti, revisione critica Qwen. Le 19 finestre Qwen hanno generato 20 proposte e 57 sovrapposizioni; il consolidamento ha prodotto 5 casi e la revisione finale 6 card. **Il consolidamento corregge un problema introdotto dalle finestre sovrapposte**, non è prova di maggiore accuratezza rispetto al vecchio percorso. Si sono verificati un timeout di 35 minuti e fallimenti di configurazione YAML, oltre a iterazioni di debugging. Non è disponibile una contabilizzazione monetaria finale omogenea dei due metodi.

### Raccomandazione provvisoria

1. **Conservare** il recupero economico metadata-first per scala e per coprire fonti senza testo integrale.
2. **Semplificare** la fase LLM: preferire una singola valutazione per componente candidata, con split esplicito; eliminare le finestre ripetute se non producono un miglioramento misurato. Non pubblicare automaticamente.
3. **Usare testi integrali/abstract estesi** per casi ambigui, ad alto impatto e per sintesi verificabili.
4. **Non proclamare vincitore** finché vecchio metodo full-text, metadata-only e ibrido non sono eseguiti sugli stessi documenti e sullo stesso gold standard cieco.
5. Congelare un corpus stratificato con veri negativi difficili, duplicati, sviluppi correlati, casi multi-editore e fonti fuori dalle proposte attuali; doppia etichettatura indipendente con `SAME_EVENT`, `RELATED_DISTINCT`, `TOPIC_ONLY`, `INSUFFICIENT`. Misurare precision, recall, pairwise F1, cluster impurity, tempo, token e costo fatturato. Non usare le predizioni dei modelli come verità di riferimento.

**Decisione:** il percorso metadata-first + revisione mirata è il candidato architetturale più promettente per rapporto costi/scalabilità, **non ancora il metodo vincitore per accuratezza dimostrata**.
