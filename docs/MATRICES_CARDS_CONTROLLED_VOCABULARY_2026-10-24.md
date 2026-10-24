# Ubik — Matrici, card e vocabolario informativo (24 ottobre 2026)

## Stato
Nota di continuità e proposta di ricerca, **non** modifica all'architettura di produzione. Branch sperimentale `develop/ubik-core`. Il corpus congelato contiene 105 notizie da 39 testi originali; nel confronto più recente le due braccia usano le **stesse estrazioni DeepSeek**. Conservare sempre `news_id`, `source_id`, sintesi, citazioni letterali e provenienza. Distinguere notizia (affermazione), card (unità fattuale) e matrice (contesto specifico che può contenere più card).

## Risultati verificati
- Run indipendente Qwen/Qwen vs DeepSeek/DeepSeek: https://github.com/nathanasso-code/Ubik/actions/runs/40090764027 ; script `ingestion/frozen_independent_qwen_deepseek.py`. Qwen 60/105 estrazioni, 41 card, 27 componenti; DeepSeek 105/105, 61 card, 38 componenti. Retry di estrazioni omesse aggiunto successivamente sul branch, non confondere con questo run.
- Run di raggruppamento sulle medesime sintesi DeepSeek: https://github.com/nathanasso-code/Ubik/actions/runs/40115580134 ; script `ingestion/frozen_shared_deepseek_matrices.py`. Qwen 69 card, DeepSeek 64; 38 componenti/matrici candidate comuni. Le matrici di questo run sono **soltanto componenti embedding riutilizzate**, non decisioni semantiche convalidate.
- Esempi qualitativi: farfalle monarca suddivise in quattro componenti nonostante la ricorrenza delle stesse fonti; Ucraina con una componente estesa, semanticamente eterogenea, contenente molte card. La precedente costruzione delle componenti collegava direttamente solo `source_id` differenti con cosine >=0.68; le unioni erano transitive. Questo ostacola il raggruppamento per comune ricerca e può produrre macrocomponenti.
- Nuovo esperimento predisposto, **esecuzione non ancora verificata** al momento della redazione: `ingestion/frozen_joint_matrices_cards.py`, scelta workflow `joint-matrices-cards` in `.github/workflows/refresh-ucdp.yml`. Ricalcola candidati includendo coppie della stessa fonte con similarità >=0.35 e altre coppie >=0.68; limita le finestre di revisione a 28 notizie con splitting euristico per gruppi e chiede a Qwen/DeepSeek, con identico input DeepSeek, di produrre **matrici e card insieme in una sola revisione LLM**. Il limite può spezzare matrici corrette; le soglie non sono calibrate. Il workflow è manuale, non produzione.

## Nuova ipotesi: vocabolario informativo controllato
L'utente propone di attribuire a ciascuna sintesi un'etichetta distintiva/codice, riutilizzabile per matrice e card, al posto di un embedding su titoli ambigui. **Ipotesi da sperimentare, non soluzione dimostrata.**

Separare due oggetti:
1. **Codice canonico strutturato**, per uguaglianza, indicizzazione e relazioni esplicite, per esempio `dominio / entita / contesto-evento / aspetto-fattuale`. Il codice evento condiviso può definire una matrice candidata, il codice aspetto distingue sottocard. Gli identificativi canonici devono provenire da un registro stabile, non da stringhe liberamente inventate da ciascuna chiamata LLM.
2. **Descrittore semantico breve, normalizzato e leggibile**, utile per embedding, scoperta di nuovi contesti e risoluzione di sinonimi. Un codice arbitrario come `EVT-00482` non contiene di per sé semantica interpretabile dall'embedding: applicare embedding esclusivamente ai codici opachi rischia di peggiorare il recupero.

Possibile pipeline economica: estrazione di sintesi ed evidenze -> assegnazione/normalizzazione di descrittori e codici (preferibilmente nella stessa chiamata di estrazione, per non aumentare le chiamate) -> lookup nel registro dei contesti noti e confronto esatto dei codici -> embedding solo per descrittori nuovi/ambigui -> revisione LLM congiunta matrici+card nei casi incerti -> aggiornamento controllato del registro. La visione d'insieme può essere approssimata tramite recupero di candidati dal registro; evitare l'invio dell'intero corpus a ogni richiesta. Permettere più matrici per uno stesso articolo, senza duplicare o perdere la provenienza delle singole affermazioni.

### Esperimento comparativo proposto, non ancora implementato
Confrontare sullo stesso corpus e su coppie annotate:
A. embedding titolo+sinossi;
B. embedding di descrittori brevi controllati;
C. assegnazione codice canonico + lookup esatto + embedding di fallback;
D. revisione congiunta matrice/card su componenti preliminari.

Misurare recall dei veri contesti, false unioni (soprattutto Ucraina), false separazioni (soprattutto farfalle monarca), accuratezza delle card, copertura `news_id`, stabilità dei codici tra run, numero chiamate, token e costo effettivo. Il costo dell'assegnazione delle etichette **non è gratuito** se richiede nuove chiamate: conteggiarlo nel totale. Un codice uguale non prova indipendenza o verità delle fonti.

## Vincoli
- Non promuovere un risultato senza audit manuale su casi positivi, negativi difficili e casi incerti.
- Nessuna fonte persa; conservare estratti verificati e identificativi originali.
- Non confondere topic generale, matrice specifica, card fattuale, documento e fonte indipendente.
- Non dichiarare che il workflow congiunto è riuscito senza controllare run e artifact.
- Non modificare automaticamente main/applicazione di produzione.
