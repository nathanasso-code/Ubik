# Matrici della settimana — specifica (2 novembre 2026)

Pipeline corrente di Ubik: `ingestion/ubik_daily5.py` (macro Topic e sotto-topic) sul motore di
`ingestion/ubik_daily4.py`. Prompt in `prompts/daily-v5/` (nota) e `prompts/daily-v4/` (raggruppamento,
secondo giro, testi). Il modello propone, il codice conferma.

## Livelli

| Livello | Definizione |
| --- | --- |
| Card | Una o più fonti che trattano lo stesso aspetto in modo sovrapponibile. Una fonte sola è una card; una fonte non si divide mai. |
| Matrice | Le card di testate diverse sullo stesso evento specifico, o su fatti strettamente legati negli stessi giorni. Almeno due origini indipendenti. |
| Topic | Un perimetro che filtra il bacino comune. Un macro Topic ha sotto-topic; un articolo può stare in più sotto-topic con la stessa nota. |

La vicenda (catena di Matrici tra settimane con uno «stato al») è sospesa finché non ha un controllo di fedeltà.

## Fasi

1. **Selezione** (`ubik-corpus/tools/select_ai_week.py`, senza modelli): gli articoli della finestra che parlano di
   IA, dai corpus `ai-regulation` e `ai`, senza doppioni per indirizzo canonico; origine, testata, livello e
   accesso al testo dal registro.
2. **Nota** (DeepSeek, una chiamata per articolo, in parallelo): pertinenza all'IA, tipo di pezzo, evento principale
   (`actor`, `action`, `object`, `date`, nomi canonici in inglese), riferimento e sintesi in italiano, citazione
   letterale con traduzione, sotto-topic (`yes` / `partial` / `no`). Le cifre si convertono per significato nella
   lingua dell'articolo; mai «bilioni».
3. **Raggruppamento** (DeepSeek, una chiamata per sotto-topic): Matrici e card fatte di articoli interi.
4. **Conferma del codice** (`same_event`). Date entro 10 giorni quando note, e una prova:
   - *evento*: gli oggetti condividono una parola significativa e gli attori una, oppure gli oggetti due;
   - *nomi*: gli attori condividono un nome proprio, oppure gli oggetti due (esclusi nomi generici come
     Commissione, Congress, Journal, Media);
   - *espressione*: titolo, riferimento e oggetto condividono due parole consecutive (escluse le espressioni
     generiche; il nome della testata è tolto dal titolo).
   Le Matrici sono le componenti connesse degli articoli proposti insieme; servono almeno due origini. Le card sono
   gli articoli che il modello ha messo nella stessa card e che sono dello stesso tipo (cronaca, reazione, lettura).
5. **Secondo giro** (DeepSeek, una chiamata per sotto-topic): il modello rivede le card singole accanto alle Matrici
   e propone unioni. Valgono solo le prove *evento* e *nomi*. Gli articoli scartati ma legati tra loro da prove forti
   diventano una Matrice a sé.
6. **Filtro del sotto-topic**: una Matrice resta se almeno due articoli, e almeno la metà, sono `yes` per quel
   sotto-topic; altrimenti i suoi articoli tornano card singole.
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

## Da fare

- Nota più stretta su «in parte» (conti, prodotti e chip non sono energia né lavoro) e «duemila miliardi» invece di
  «trilioni».
- Filtro iniziale più severo: 266 articoli su 919 non parlavano di IA ma hanno pagato la nota.
- Scrivere i testi solo per le Matrici che superano il filtro del sotto-topic.
- Valutare un sotto-topic Economia dell'IA per gli articoli senza sotto-topic (168 nella settimana di prova).
