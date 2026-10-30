# Storia delle direzioni

Documenti recuperati dal ramo archiviato `archive/2026-10-29-develop-ubik-core` perché spiegano svolte di
architettura che il codice attuale non racconta.

- `2026-10-21-architettura-informativa-differenziale.md`: la "direzione prioritaria di ricerca" di allora.
  Fonte = contenitore, contributo informativo = unità di analisi, card = unità editoriale; composizione
  differenziale con controllo di autonomia e copertura. Lasciata in sospeso, non respinta nel merito.
  L'esperimento di autonomia e copertura risulta lanciato ma senza risultati documentati.
- `2026-10-23-handoff-svolta-anti-duplicati.md`: la svolta verso l'identità delle notizie (priorità: niente
  card duplicate), con citazioni testuali verificate ed embedding. Da qui le linee v4 e v5.

Il 30 ottobre la direzione differenziale è stata ripresa come v6. È composizione editoriale per settimana sulle
schede delle fonti, con controlli meccanici fatti dal codice (protocollo `protocols/ubik-v6-editorial-protocol.md`).
Il motivo: con testi completi e modelli più capaci, scomporre in eventi e giudicare a coppie butta via il
contesto che serve a giudicare il valore. Gli esperimenti di metà ottobre usavano modelli economici (Qwen,
DeepSeek), e la complessità della pipeline compensava in parte la loro fragilità.
