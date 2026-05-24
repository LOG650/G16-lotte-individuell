# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 1

## Context

Brukeren har bedt om Batch 11 med 8 prosa-fikser fra en uavhengig multi-agent
review kjørt i forrige sesjon. Reviewen identifiserte konkrete, prioriterte
forbedringer i sluttutkastet av rapport.md (branch `fase-4-rapport`,
innlevering 2026-06-01).

Arbeidsflyt brukeren har bedt om:

- **Én fix om gangen** (denne planen dekker kun fix 1)
- Vis diff før commit
- Egen commit per fix
- Mulig sesjonsbytte mellom hver

De øvrige 7 fiksene (2–8) er listet i brukerens prompt og blir tatt som
separate planer/sesjoner etterpå.

## Fix 1 — Kvantitativ presisjon i konklusjon

**Plassering:** [005 report/rapport.md:865](005 report/rapport.md#L865)

**Problem:** L865 sier "Modellens 90 %-punktestimat (6,7 år) er kvantitativt
konsistent med samferdselsavdelingens 7,22-års-beregning…". Tallet "6,7 år"
er en avrunding som blander to ulike størrelser:

- MC P50 for Middels_90: **6,67 år**
- Deterministisk heuristikk for Middels_90: **6,72 år**

Resten av rapporten er konsistent: [005 report/rapport.md:747](005 report/rapport.md#L747)
skriver eksplisitt "Modellens 90 %-estimat på 6,72 år er kvantitativt
konsistent med direkte beregning av samferdselsavdelingens parametere
(7,22 år ved 240 dager/år…)". Konklusjonen bør bruke samme verdi og
spesifisere kilden.

**Endring (én streng-erstatning):**

- Gammel: `Modellens 90 %-punktestimat (6,7 år) er kvantitativt konsistent med samferdselsavdelingens 7,22-års-beregning`
- Ny: `Modellens 90 %-punktestimat (6,72 år, deterministisk heuristikk) er kvantitativt konsistent med samferdselsavdelingens 7,22-års-beregning`

Strengen er unik i filen (verifisert under utforskning).

**Risiko / sideeffekter:**

- Lav. Strengt kvantitativ presisjon; ingen logiske eller strukturelle
  endringer. 6,72 er allerede etablert som konklusjonens prefererte
  tall i 7.6.
- Endringen forsterker konsistens mellom 7.6 (oppsummering) og 9.0
  (konklusjon), samt mellom konklusjonens første og andre avsnitt.

## Verifisering

1. Sammenlign med [oppsummering_scenarioer.csv](004 data/processed_data/oppsummering_scenarioer.csv) — Middels_90 heuristikk-varighet
2. Sammenlign med [monte_carlo_summary.csv](004 data/processed_data/monte_carlo_summary.csv) — Middels_90 P50
3. Kontroller at [005 report/rapport.md:747](005 report/rapport.md#L747) fortsatt
   bruker "6,72 år" (skal ikke endres)

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
peer review-batch 11 fix 1: presiser 6,7 -> 6,72 ar (deterministisk heuristikk) i 9.0
```

## Resterende fikser (egne planer senere)

- Fix 2 — 7.6 L749: nyanser "MIP forbedrer ikke heuristikken"
- Fix 3 — 9.0 L867: "omfordeling ikke nødvendig" for kategorisk
- Fix 4 — 5.1.5 L355: 96 %-scenarioets bakoverregning svakt forklart
- Fix 5 — MC-gjentakelse mellom 5.1.6 (L365) og 8.4 (L824)
- Fix 6 — 9.0 L863: 10–17-mnd-påstand mangler caveat
- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium)
- Fix 8 — 5.1.7: definer "robust" eksplisitt
