# Matrici della settimana — specifica (aggiornata il 4 novembre 2026)

Pipeline corrente di Ubik: `ingestion/ubik_daily5.py` (macro Topic e sotto-topic) sul motore di
`ingestion/ubik_daily4.py`. Prompt in `prompts/daily-v5/` (nota) e `prompts/daily-v4/` (raggruppamento,
secondo giro, testi). Il modello propone, il codice conferma.

## Livelli

| Livello | Definizione |
| --- | --- |
| Card | Le fonti che riportano lo stesso fatto sostanziale. In una Matrice la card unica è il default; una card separata solo per un fatto distinto (per esempio la sentenza del tribunale di Oslo dentro la vicenda dei termini di Meta) o per ciò che le altre fonti contraddicono o non hanno. Mai per angolo, enfasi o tipo di pezzo. Una fonte non si divide mai. |
| Matrice | Le card di testate diverse sullo stesso evento specifico, o su fatti strettamente legati negli stessi giorni. Almeno due origini indipendenti. |
| Topic | Un perimetro che filtra il bacino comune. Un macro Topic ha sotto-topic; un articolo può stare in più sotto-topic con la stessa nota. |

La vicenda (catena di Matrici tra settimane con uno «stato al») è sospesa finché non ha un controllo di fedeltà.

## Fasi

1. **Selezione** (`ubik-corpus/tools/select_ai_week.py`, senza modelli): gli articoli della finestra dai corpus
   `ai-regulation` e `ai`, senza doppioni per indirizzo canonico; origine, testata, livello e accesso al testo dal
   registro. **Prefiltro**: tolte le righe che si ripetono in almeno tre articoli della stessa fonte (menu, link
   correlati, piè di pagina), l'articolo passa se ha un termine IA nel titolo, tre nel testo, oppure uno nel testo
   insieme a una parola di un sotto-topic o in un testo brevissimo (post social). I termini IA comprendono le principali
   aziende e prodotti. Gli articoli scartati sono elencati nella selezione; `AI_PREFILTER=0` torna alla selezione larga.
2. **Nota** (DeepSeek, una chiamata per articolo, in parallelo): pertinenza all'IA, tipo di pezzo, evento principale
   (`actor`, `action`, `object`, `date`, nomi canonici in inglese), riferimento e sintesi in italiano, citazione
   letterale con traduzione, sotto-topic (`yes` / `partial` / `no`). `partial` solo se l'articolo porta almeno un
   fatto o argomento specifico dentro il perimetro del sotto-topic; conti, raccolte di fondi, quotazioni, chip e
   prodotti non sono energia né lavoro se l'articolo non riporta fatti su energia, data center o posti di lavoro. Le
   cifre si convertono per significato nella lingua dell'articolo; mai «bilioni» né «trilioni» («duemila miliardi»).
3. **Raggruppamento** (DeepSeek, una chiamata per sotto-topic): Matrici e card fatte di articoli interi. Ogni card
   separata dichiara il motivo: `distinct` = `fact` (fatto distinto) o `adds` (contraddice o aggiunge), con `why`.
4. **Conferma del codice** (`same_event`). Date entro 10 giorni quando note, e una prova:
   - *evento*: gli oggetti condividono una parola significativa e gli attori una, oppure gli oggetti due;
   - *nomi*: gli attori condividono un nome proprio, oppure gli oggetti due (esclusi nomi generici come
     Commissione, Congress, Journal, Media);
   - *espressione*: titolo, riferimento e oggetto condividono due parole consecutive (escluse le espressioni
     generiche; il nome della testata è tolto dal titolo).
   Le Matrici sono le componenti connesse degli articoli proposti insieme; servono almeno due origini. Le card sono
   quelle proposte dal modello, senza più divisione per tipo di pezzo.
5. **Secondo giro** (DeepSeek, una chiamata per sotto-topic): il modello rivede le card singole accanto alle Matrici
   e propone unioni. Valgono solo le prove *evento* e *nomi*. Gli articoli scartati ma legati tra loro da prove forti
   diventano una Matrice a sé. **Matrici gemelle**: due Matrici della stessa settimana sullo stesso oggetto (il rinvio
   di Meta e l'indagine della CMA sugli stessi termini) si fondono se il modello lo propone e il codice conferma una
   coppia di articoli (prova forte e una parola d'oggetto in comune oltre ai nomi degli attori); senza proposta, se
   almeno metà degli articoli di ciascuna ha una coppia con due parole d'oggetto in comune (almeno due coppie).
5b. **Controllo delle card** (`consolidate`, senza modelli): due card della stessa Matrice si fondono se due loro
   articoli hanno lo stesso attore e una parola d'oggetto in comune che non sia il nome dell'attore, e il modello non ha
   segnato nessuna delle due come distinta. È il test delle unioni applicato alle divisioni. Il registro (`cards_check`,
   `kept_distinct`) conserva le fusioni con la prova e le divisioni mantenute con il motivo.
6. **Filtro del sotto-topic**: una Matrice resta se almeno due articoli, e almeno la metà, sono `yes` per quel
   sotto-topic; altrimenti i suoi articoli tornano card singole. Il filtro si applica prima dei testi, così le Matrici
   scartate non costano nulla.
7. **Testi** (DeepSeek, una chiamata per Matrice): titolo neutro, essenza in 2–3 frasi, titolo e testo delle card
   con più fonti, solo dalle sintesi. Il codice segnala i numeri che non ritrova nelle sintesi.
8. **Pagina**: Matrici, poi card singole centrali, poi in una sezione chiusa quelle solo collegate al tema. La card
   mostra fonte, data, lingua, titolo originale, sintesi, citazione con traduzione e «testo parziale» quando il
   registro lo dichiara o il testo è breve.

Ogni collegamento registra la prova usata; il registro della pagina conserva proposte, conferme, scarti e costi.

## Sotto-topic di Intelligenza artificiale

| Chiave | Nome | Perimetro (sintesi) |
| --- | --- | --- |
| `regole` | Regole sull'IA | Leggi, regolazione, autorità, tribunali e politiche pubbliche sull'IA in Europa e negli Stati Uniti |
| `lavoro` | Lavoro e IA | Effetti dell'IA su posti, salari, assunzioni, professioni, sorveglianza dei lavoratori, sindacati, cause |
| `energia` | Data center, energia e territorio | Data center, reti, energia, acqua, emissioni, permessi, conflitti locali, lavoratori dei cantieri |
| `copyright` | Diritto d'autore, editori e dati di addestramento | Cause, licenze, opt-out e scraping, effetti dell'IA sul giornalismo e l'editoria |

Un sotto-topic nuovo = una voce in `TOPICS` con nome e perimetro; nota e selezione restano condivise.

## Esecuzione e costi

Le esecuzioni partono solo da `ubik-corpus/runs/daily.request` (`version=5`; `reuse` riusa raggruppamento e
secondo giro già pagati) o a mano. Le note si riusano finché il prompt non cambia.

Settimana 26 ottobre – 1 novembre 2026: 919 articoli, 653 sull'IA, 0,62 $ di note e 0,12 $ per quattro sotto-topic
(raggruppamento, secondo giro, testi): 0,74 $. Risultato: Regole 7 Matrici, Lavoro 5, Data center ed energia 4,
Diritto d'autore 8.

## Prefiltro, misura sulla settimana di prova

Confronto con le note già pagate della settimana 26 ottobre – 1 novembre (932 articoli candidati): il prefiltro ne
toglie 263; dei 266 giudicati estranei all'IA ne toglie 215, dei 375 centrati sull'IA ne perde 4, dei 83 articoli
nelle Matrici ne perde 3 (uno per Matrice, ciascuna resta con almeno due testate). Risparmio atteso sulle note: circa
un quarto.

## Da fare

- Valutare un sotto-topic Economia dell'IA per gli articoli senza sotto-topic (168 nella settimana di prova).
