# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 2

## Context

Andre fix i batch 11 fra multi-agent reviewen i forrige sesjon (jf. plan
`vi-skal-starte-batch-mutable-peacock.md`). Fix 1 (presiser 6,7 → 6,72 år i
9.0) ble committet som `f9ac0b9`. Innlevering 2026-06-01, branch
`fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.

## Fix 2 — Nyanser «MIP forbedrer ikke heuristikken» i 7.6

**Plassering:** [005 report/rapport.md:749](005 report/rapport.md#L749)

**Problem:** Bold-setningen «MIP-modellen verifiserer heuristikken; den
forbedrer den ikke.» er for kategorisk. Resten av samme avsnitt motsier
den: «MIPs reelle gevinst er en mer komprimert kartkontor-ferdigprofil
(Monte Carlo P50 ned fra 510 til 409–452 dager …)». MIP er marginalt
dårligere på makespan (artefakt av månedlig oppløsning), men *reelt* bedre
på kartkontor-ferdigprofil. Bold-setningen bør speile denne dobbeltheten i
stedet for å påstå «ingen forbedring».

7.1 L651 er allerede konsistent med den nyanserte lesningen («MIP-modellens
bidrag er altså todelt: den leverer en uavhengig verifikasjon av
heuristikken, og den leverer en komprimert kartkontor-ferdigprofil via
lex-opt-prioritet»).

**Endring (én streng-erstatning):**

- Gammel: `**MIP-modellen verifiserer heuristikken; den forbedrer den ikke.**`
- Ny:     `**MIP-modellen verifiserer heuristikkens makespan og forbedrer kartkontor-ferdigprofilen.**`

Strengen er unik i filen (verifisert med Grep, kun L749).

**Risiko / sideeffekter:**

- Lav. Endringen rammer kun bold-åpningen av tredje hovedfunn-avsnitt i 7.6.
- Resten av avsnittet (under 2,2 % differanse på makespan, omfordelinger
  som tie-breakers, P50 510 → 409–452) støtter den nye formuleringen
  direkte.
- Konsistent med 7.1 L651 («MIP-modellens bidrag er altså todelt …») og
  med 7.5 L717 («Kartkontor-fasen blir derimot merkbart raskere på
  MIP-planen»).
- Ingen tall endres, ingen kryssreferanser brytes.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L749)

## Verifisering

1. Diff viser kun én linje endret rundt L749.
2. Sjekk at 7.1 L651 og 7.5 L717 fortsatt er kompatible (skal være det —
   ingen endring der).
3. Visuell lesning: avsnittet (L749) skal nå flyte naturlig fra bold til
   forklaring uten indre motsigelse.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
peer review-batch 11 fix 2: nyanser MIP-utsagn i 7.6 (verifiserer makespan, forbedrer kartkontor-ferdigprofil)
```

## Resterende fikser (egne planer senere)

- Fix 3 — 9.0 L867: «omfordeling ikke nødvendig» for kategorisk
- Fix 4 — 5.1.5 L355: 96 %-scenarioets bakoverregning svakt forklart
- Fix 5 — MC-gjentakelse mellom 5.1.6 (L365) og 8.4 (L824)
- Fix 6 — 9.0 L863: 10–17-mnd-påstand mangler caveat
- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium)
- Fix 8 — 5.1.7: definer «robust» eksplisitt
