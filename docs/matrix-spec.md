# Matrice Ubik — specifica v1 (30 ottobre 2026)

Una Matrice racconta un nucleo di interesse (una vicenda, una decisione, un conflitto) a chi ne sa poco, usando il meglio delle fonti raccolte. La produce un LLM istruito; il codice la verifica e la impagina sempre allo stesso modo. Riferimento costruito a mano: "Matrice Omnibus digitale" (artifact del 30 ottobre, versione 3).

## Divisione del lavoro

| Chi | Cosa |
| --- | --- |
| Codice | Seleziona gli elementi del nucleo; verifica le citazioni parola per parola; decide intestazione a fonte unica o fonti in calce; controlla lunghezze, numeri e date senza supporto; impagina. |
| Modello economico | Una nota per elemento: pertinenza, cosa porta di specifico, affermazioni tipizzate con citazione letterale. |
| Modello di sintesi | Una chiamata per Matrice: titolo, sintesi, punti chiave, schede, passaggi, ciascuno con i riferimenti alle note che lo sostengono. |

## Forma

1. **Titolo**: una domanda o un'affermazione che nomina il conflitto o la novità, al massimo 16 parole.
2. **Sintesi breve**: 3–4 frasi, al massimo 80 parole; cosa succede, cosa è stato deciso, chi contesta, cosa viene dopo. Visibile.
3. **Sintesi estesa**: 2–3 paragrafi, al massimo 200 parole; espandibile.
4. **Punti chiave**: fino a 3, ciascuno un titoletto e al massimo 70 parole; spiegano cosa cambia o cosa c'è in gioco per chi legge.
5. **Schede**: fino a 5, in ordine di importanza. Ognuna ha un tipo (documento, fatto, posizioni, dato, inchiesta), un nostro titolo (al massimo 18 parole), un testo di 40–80 parole e al massimo una citazione con traduzione.
   - **Fonte unica**: intestazione con nome della fonte, che cos'è, paese, data e titolo originale linkato. Lo decide il codice.
   - **Più fonti**: elencate in calce.
6. **Passaggi**: fino a 6 date con una riga ciascuna.
7. **Fonti**: chi è stato usato; quanti elementi sono stati lasciati fuori e perché, in una frase.

## Regole di scrittura

- Lettore: intelligente, poco informato sul tema. Né didascalico né telegrafico: frasi complete, un'idea per frase.
- Niente sigle isolate: si sciolgono alla prima occorrenza o si evitano. Niente numeri di articolo di legge se non spiegati.
- Fatti, numeri, date, posizioni e citazioni vengono solo dalle note, con riferimento. Il modello può aggiungere contesto e raccordi (cos'è una cosa, perché conta un ruolo) senza introdurre fatti nuovi: niente numeri, date o persone che non compaiano nelle note.
- Selezionare: meglio poche informazioni comprensibili e fondate che un collage. Pluralità sì, esibita no: le posizioni dello stesso fronte stanno in una scheda.
- Hanno precedenza: documenti primari e confronti tra testi; informazioni che solo una fonte porta; dati verificabili; inchieste; posizioni degli attori che decidono.
- Una scheda a fonte unica è il racconto di ciò che quella fonte ha portato.

## Controlli del codice

- Citazione: deve comparire parola per parola nel testo raccolto, altrimenti si toglie.
- Riferimenti: ogni scheda, punto e passaggio deve citare note esistenti; quelli senza riferimenti validi si tolgono, con registro.
- Numeri e date nei testi: devono comparire nelle note o nei testi citati; altrimenti segnalati.
- Lunghezze: oltre i limiti, segnalate (non tagliate).
- Fonte unica: se una scheda cita una sola origine, intestazione con titolo originale e link presi dai metadati, non dal modello.

## Revisione

Il codice controlla le regole di scrittura che si possono verificare: sigle non sciolte (ammesse UE, USA, IA e GDPR spiegato, o sigle sciolte tra parentesi altrove nella pagina), numeri di articoli e allegati, lunghezze, schede che non poggiano su almeno un elemento centrale per il nucleo. Se trova violazioni, una sola chiamata di revisione riscrive i campi segnalati senza toccare i riferimenti. Le violazioni prima e dopo restano registrate.

## Fedeltà

Dopo la revisione, un modello economico confronta ogni frase delle schede, dei punti chiave e dei passaggi con le affermazioni citate a sostegno e segnala ciò che è indebolito, rafforzato, senza riscontro o contraddetto. Le frasi segnalate si sostituiscono con la correzione proposta o si tolgono; tutto resta registrato.

## Confronto

Quando due o tre fronti si oppongono sullo stesso punto, una scheda di confronto li affianca graficamente; ogni lato ha la sua etichetta e le sue fonti.

## Misura

Contro il riferimento: schede del riferimento ritrovate (per contenuto), affermazioni senza supporto, leggibilità in valutazione cieca, costo. Gradini: (1) solo corpus, sintesi economica; (2) solo corpus, sintesi forte; (3) corpus più acquisizione mirata; (4) sintesi più forte.

## Risultati, 30 ottobre (Omnibus digitale)

| Gradino | Elementi | Costo | Esito |
| --- | --- | --- | --- |
| 1, solo corpus | 59 | note 0,047 $; pagina DeepSeek ~0,01 $, Sonnet ~0,10 $ | 153 citazioni, tutte letterali; struttura stabile; mancano le fonti decisive; Sonnet viola le regole sulle sigle |
| 1b, regole nel codice e revisione | 59 | revisione DeepSeek ~0,004 $, Sonnet ~0,04 $ per pagina | violazioni da 8–16 a 0–1; un caso di significato alterato ("ha votato contro" diventato "si astiene") |
| 3, più acquisizione mirata | 102 | 15 ricerche 0,001 $; note nuove 0,057 $; pagina DeepSeek ~0,02 $, Sonnet ~0,23 $ | entrano editori, industria digitale tedesca, Bundesrat, stampa FR/ES/IT; non trovati il confronto testuale di Leto e la lettera delle confederazioni |
| 4a, esempi di stile (da un'altra vicenda) | 102 | come gradino 3 | schede più concrete: numeri, ragioni delle parti; violazioni prima della revisione in calo con DeepSeek |
| 4b, più link citati negli articoli centrali | 132 | note nuove 0,04 $; pagina DeepSeek ~0,015 $, Sonnet ~0,29 $ | entrano documenti primari (mandato del Consiglio, parere delle autorità privacy, lettere aperte, inchiesta sulle lobby); la Germania che vota contro compare in entrambe |
| v2, prompt rivisto, confronto, fedeltà (DeepSeek) | 132 | ~0,017 $ per pagina con revisione e fedeltà | titoli con la questione aperta; una scheda di confronto a tre lati; il controllo di fedeltà segnala 4–10 frasi per pagina e le corregge. Limiti: le correzioni possono appiattire il titolo; restano sigle introdotte dopo la revisione; un nome tradotto male (EDRi "Centro"); la Germania resta "non a favore" quando la scheda non cita la fonte che dice "contro" |

Ricerca: Bing News consente la ricerca da robots.txt, Google News no (escluso). Gli articoli trovati si ricollegano alle testate del registro per dominio, altrimenti la stessa testata conta due volte.

Ricerca nel web generale: vietata da robots.txt di Bing, non usata. Seguire i link citati negli articoli centrali è gratuito e porta i documenti primari meglio di qualsiasi ricerca.

Spesa totale degli esperimenti sulla Matrice: circa 2,6 $.
