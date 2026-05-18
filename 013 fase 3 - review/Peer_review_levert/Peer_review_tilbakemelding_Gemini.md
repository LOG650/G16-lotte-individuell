# Peer-review-rapport: LOG650 - Våren 2026

## 1. Forsideopplysninger

*   **Gruppe som vurderer:** Lotte Picard
*   **Gruppe som blir vurdert:** Kjetil Tronstad Lund
*   **Tittel på rapporten som vurderes:** "Optimal lagerbeholdning for BiteBurst: En SARIMA-basert tilnærming til prognose og sikkerhetslager"
*   **Dato:** 7. mai 2026

---

## 2. Helhetsinntrykk

Rapporten er svært velskrevet, metodisk grundig og demonstrerer en tydelig rød tråd fra problemstilling til konklusjon. Bruken av SARIMA-modellering for å løse et konkret logistikkproblem (lageroptimalisering) i en kontrollert simulering (Big Ambitions) er både original og faglig relevant. Hovedstyrkene ligger i den detaljerte metodebeskrivelsen, den systematiske evalueringen mot en naiv baseline, og den ærlige diskusjonen rundt modellens begrensninger – spesielt knyttet til trendende etterspørsel i vekstfaser. Rapporten fremstår som faglig moden og holder et høyt nivå for emnet.

---

## 3. Områdevis vurdering

### Innledning
*   **Styrker:** Innledningen gir en god kontekstualisering av lagerstyringsproblematikken (stockout vs. overstocking). Problemstillingen i kapittel 1.1 er presis og støttes av to operative delspørsmål som styrer analysen.
*   **Forbedringspunkter:** Ingen vesentlige forbedringsbehov her. Avgrensningene i kapittel 1.2 er fornuftige og bidrar til å fokusere rapporten.

### Litteraturgjennomgang og teoretisk forankring
*   **Styrker:** God dekning av sentral litteratur innen tidsrekkeanalyse (Box-Jenkins, Hyndman) og lagerstyringsteori (Silver et al., Chopra & Meindl). Det teoretiske grunnlaget for SARIMA og sikkerhetslager (kapittel 3) er pedagogisk forklart og direkte knyttet til den praktiske anvendelsen.
*   **Forbedringspunkter:** Koblingen mellom statistisk usikkerhet (prediksjonsintervaller) og sikkerhetslager er et sterkt punkt som kunne vært enda tydeligere fremhevet som det metodiske valget i litteraturgjennomgangen.

### Metode
*   **Styrker:** Metodekapittelet er svært sterkt. Beskrivelsen av datarensing (3-sigma-regel) og håndtering av registreringsfeil (Tabell 3) gir høy troverdighet til datagrunnlaget. Valget av SARIMA er godt begrunnet gjennom stasjonæritetstesting (ADF) og ACF-analyse.
*   **Forbedringspunkter:** Det nevnes at 3-sigma-regelen ble brukt til å flagge utliggere. Det kunne vært spesifisert mer eksplisitt om disse ble erstattet med lineær interpolering eller gjennomsnitt, selv om Tabell 3 antyder manuelle korreksjoner av åpenbare tastefeil.

### Analyse og resultater
*   **Styrker:** Presentasjonen av resultatene i kapittel 8 er oversiktlig og grundig. Bruken av MAPE for evaluering er standard, men inkluderingen av en naiv baseline (Tabell 9b) er et svært godt grep som dokumenterer modellens faktiske nytteverdi. Residualdiagnostikken (Ljung-Box) i kapittel 7.5 viser en profesjonell tilnærming til statistisk validering.
*   **Forbedringspunkter:** For produktene med høy MAPE (f.eks. Salat i HK/MH og Pommes frites i GM/MH), kunne man vurdert å inkludere en kort kommentar i resultatkapittelet om hvordan disse spesifikke anbefalingene bør håndteres operasjonelt (f.eks. med et manuelt "erfaringspåslag").

### Diskusjon
*   **Styrker:** Kapittel 9.2 gir en utmerket refleksjon over SARIMA-modellens reaktive natur ved brå trendskifter, med Murray Hill som et konkret case. Dette viser god forståelse for modellens begrensninger. Diskusjonen om overføringsverdi til reelle data (kap. 9.5) er nøktern og realistisk.
*   **Forbedringspunkter:** Diskusjonen er omfattende og god. Man kunne kanskje utdypet noe mer hvordan man i praksis ville implementert den "periodiske reestimeringen" i en operasjonell hverdag.

### Konklusjon
*   **Styrker:** Konklusjonen oppsummerer funnene knyttet til begge delspørsmål på en konsis måte. Den gir klare anbefalinger for videre arbeid, som inkludering av eksogene variabler (SARIMAX).
*   **Forbedringspunkter:** Ingen spesielle merknader.

### Skriveflyt, formelle aspekter og helhetsvurdering
*   **Styrker:** Språket er presist, akademisk og fritt for unødvendig fyllmasse. Referansebruken (APA 7) er konsistent og korrekt. Strukturen følger kravene i veiledningen perfekt.
*   **Forbedringspunkter:** Figurhenvisningene (f.eks. Figur 1-4) fungerer godt i teksten, men pass på at de faktiske filstiene (f.eks. `plots/HK_French.png`) er tilgjengelige i den endelige leveransen.

---
**Konklusjon:** Dette er en meget solid rapport som viser høy grad av refleksjon og teknisk ferdighet.
