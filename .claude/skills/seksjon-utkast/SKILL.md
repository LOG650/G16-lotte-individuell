---
name: seksjon-utkast
description: Skriv utkast til en rapportseksjon i 005 report/rapport.md. Bruk når brukeren vil legge til eller polere innhold i en bestemt seksjon.
disable-model-invocation: true
argument-hint: "[sammendrag | abstract | 10.0 | innledning | ...]"
---

Skriv utkast til en seksjon i 005 report/rapport.md basert på argumentet brukeren ga.

Eksempler på gyldige argumenter:
- `sammendrag` (200-400 ord, norsk)
- `abstract` (~samme lengde som sammendrag, engelsk)
- `10.0` eller `konklusjon` (300-500 ord)
- `1.0` eller `innledning` (polering av eksisterende)
- `12.0` eller `vedlegg`

Prosedyre:
1. Les rapport.md for å forstå hva som allerede står i seksjonen og hvordan de øvrige seksjonene henger sammen.
2. Hent relevante tall fra `004 data/processed_data/` (oppsummering_scenarioer.csv, oppsummering_mip_vektet.csv, monte_carlo_summary.csv osv.) — verifiser tall mot CSV før de skrives inn.
3. Foreslå et utkast til brukeren FØR du skriver det inn i rapport.md. Vent på godkjenning.
4. Følg stilkravene:
   - Norsk bokmål
   - APA 7 for sitering
   - Ingen interne arbeidskoder (V1/V2, sanity_check, Bolk, jobb#, review-funn)
   - Figurtekster: kursiv, ingen kolon etter nummer, ingen avsluttende punktum
   - Konsis stil — sensor leser hovedutkast som helhet

5. Etter brukeren har godkjent, skriv inn med Edit-verktøyet.
6. Foreslå commit-melding (bruk commit-rapport-mønsteret).
