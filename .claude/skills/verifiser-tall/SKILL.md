---
name: verifiser-tall
description: Verifiser et bestemt tall eller påstand i rapporten mot CSV-kilder. Bruk når noen lurer på om et tall stemmer, eller når et tall ser feil ut.
argument-hint: "[tall, setning eller spørsmål]"
---

Verifiser tallet eller påstanden brukeren har spurt om mot CSV-ene i `004 data/processed_data/`.

Prosedyre:
1. Identifiser hvilke CSV-er tallet kan komme fra (oppsummering_*, monte_carlo_*, master_kommuner, kapasitet_kontorer, tidbruk_*).
2. Les relevante CSV-er.
3. Hvis tallet er en utledet verdi (f.eks. faktor, prosent, sum, kvotient), regn ut fra rådata.
4. Sammenlign med hva som står i rapport.md (bruk Grep til å finne forekomstene).
5. Rapporter:
   - Status: korrekt / avvik / ikke verifiserbart
   - CSV-kilde
   - Beregning hvis utledet
   - Hvilke linjer i rapporten som inneholder tallet

Eksempler på spørsmål:
- "stemmer 327 ukesverk?" → sum kapasitet_kontorer.Kapasitet_Ukesverk
- "er det riktig at 54 % av kommuner = 80 % lenker?" → Pareto-utregning fra master_kommuner
- "er P95 Basis_85 13,28 år?" → monte_carlo_summary.csv
