# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 3

## Context

Tredje fix i batch 11 fra multi-agent reviewen. Fix 1 (presiser 6,72 år i 9.0)
ble committet som `f9ac0b9`. Fix 2 (nyanser MIP-utsagn i 7.6 — verifiserer
makespan, forbedrer kartkontor-ferdigprofil) ble committet som `532832d`.
Innlevering 2026-06-01, branch `fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.

## Fix 3 — «omfordeling ikke nødvendig» er for kategorisk i 9.0

**Plassering:** [005 report/rapport.md:867](005 report/rapport.md#L867)

**Problem:** Konklusjonens andre avsnitt sier:

> Omfordeling av kommuner mellom kartkontor er derimot ikke nødvendig:
> forskjellen mellom heuristikkens og MIP-modellens makespan er under 2,2 %
> i alle scenarioer, og MIP bekrefter dermed at den geografiske
> ansvarstildelingen er nær-optimal.

Formuleringen er kategorisk om at omfordeling *ikke er nødvendig*, men resten
av rapporten kvalifiserer dette tydelig — det er ikke nødvendig *for
makespan/total varighet*, men MIP-planen leverer faktisk en komprimert
kartkontor-ferdigprofil (P50 Monte Carlo 510 → 409–452 dager) som har
organisatorisk verdi. Etter fix 2 i 7.6 er denne dobbeltheten enda tydeligere
markert ellers i rapporten, og 9.0 bør speile det.

**Kryssreferanser som setter konteksten:**

- [7.3 L683](005 report/rapport.md#L683) — «ingen kommuner *må* omfordeles
  for å oppnå optimal makespan»; «hovedsakelig tie-breakere for
  kartkontor-ferdigtid».
- [7.6 L749 (etter fix 2)](005 report/rapport.md#L749) — «MIP-modellen
  verifiserer heuristikkens makespan og viser at kartkontor-fasen kunne vært
  kortere»; «de 27–71 omfordelingene er tie-breakers, ikke nødvendige for
  makespan»; «MIPs reelle gevinst er en mer komprimert kartkontor-ferdigprofil
  (Monte Carlo P50 ned fra 510 til 409–452 dager)».
- [8.3 L791](005 report/rapport.md#L791) — «omfordelingene i modellen er
  tie-breakers og ikke nødvendige for makespan, kan Kartverket med fordel
  velge å ikke implementere dem … ingen tid går tapt».
- [8.5 L828](005 report/rapport.md#L828) — MIP-planen gir
  «komprimert kartkontor-ferdigprofil: 2–3 måneder før heuristikken … Ingen
  av disse reduserer totalvarigheten, men begge har organisatorisk verdi».
- [8.6 pkt 4 L847](005 report/rapport.md#L847) — «Behold geografisk
  kartkontor-tildeling. MIP viser at omfordeling ikke er nødvendig. Spar
  organisatorisk kostnad ved å ikke flytte kommuner mellom kontor.»

8.6 pkt 4 har samme kategoriske formulering, men der er det greit fordi det
er punktanbefaling som *konkluderer* etter at nyansene er etablert i 7.6 og
8.5. I 9.0 er det første gang leseren møter omfordelingsspørsmålet, og
formuleringen bør være presisjonsmessig konsistent med 7.6 fix 2.

## Forslag til formulering

Tre alternativer, alle endrer kun setningen på L867 (resten av avsnittet er
upåvirket). Strengen «Omfordeling av kommuner mellom kartkontor er derimot
ikke nødvendig» er unik i filen (Grep verifisert).

**A — minimal kvalifikasjon (anbefalt):**

> Omfordeling av kommuner mellom kartkontor er derimot ikke nødvendig for
> total varighet: forskjellen mellom heuristikkens og MIP-modellens makespan
> er under 2,2 % i alle scenarioer, og MIP bekrefter at den geografiske
> ansvarstildelingen er nær-optimal for makespan.

*Begrunnelse:* Legger til to korte kvalifikatorer («for total varighet»,
«for makespan») som speiler 7.3/7.6/8.3 uten å gjenfortelle MIP-gevinsten i
konklusjonen. Behold konklusjonens karakter av punchline.

**B — full nyanse med MIP-gevinsten gjentatt:**

> Omfordeling av kommuner mellom kartkontor er derimot ikke nødvendig for
> total varighet: forskjellen mellom heuristikkens og MIP-modellens makespan
> er under 2,2 % i alle scenarioer, og MIP bekrefter at den geografiske
> ansvarstildelingen er nær-optimal for makespan. MIP-planen komprimerer
> riktignok kartkontor-ferdigprofilen med 2–3 måneder (jf. 7.6), men dette
> endrer ikke totalvarigheten.

*Begrunnelse:* Speiler 7.6 fix 2 og 8.5 direkte i konklusjonen. Mer komplett,
men gjør avsnittet lengre — tar plass fra «tre grep»-tråden.

**C — bytt «ikke nødvendig» til «gir liten gevinst»:**

> Omfordeling av kommuner mellom kartkontor gir derimot liten gevinst på
> totalvarigheten: forskjellen mellom heuristikkens og MIP-modellens makespan
> er under 2,2 % i alle scenarioer, og MIP bekrefter at den geografiske
> ansvarstildelingen er nær-optimal for makespan.

*Begrunnelse:* Erstatter «ikke nødvendig» (kategorisk) med «liten gevinst»
(graderbart). Minst tekstendring og mest nøytral, men «liten gevinst på
totalvarigheten» kan virke vagere enn det 2,2 %-tallet faktisk støtter.

## Valgt formulering

**A** — minimal kvalifikasjon (bekreftet av bruker 2026-05-24).

Endring (én streng-erstatning):

- Gammel: `Omfordeling av kommuner mellom kartkontor er derimot ikke nødvendig: forskjellen mellom heuristikkens og MIP-modellens makespan er under 2,2 % i alle scenarioer, og MIP bekrefter dermed at den geografiske ansvarstildelingen er nær-optimal.`
- Ny:     `Omfordeling av kommuner mellom kartkontor er derimot ikke nødvendig for total varighet: forskjellen mellom heuristikkens og MIP-modellens makespan er under 2,2 % i alle scenarioer, og MIP bekrefter at den geografiske ansvarstildelingen er nær-optimal for makespan.`

Endringer i strengen: tilføyer «for total varighet» etter «ikke nødvendig»;
fjerner «dermed» (overflødig etter kvalifikatoren); tilføyer «for makespan» på
slutten. Strengen er unik i filen (Grep verifisert).

## Risiko / sideeffekter

- Lav. Endrer kun én setning i ett avsnitt; resten av avsnittet og resten av
  9.0 er kompatible.
- Konsistens-forbedring mot 7.3, 7.6 (post-fix 2), 8.3, 8.5.
- Ingen tall endres, ingen kryssreferanser brytes, ingen påvirkning på 10.0
  Bibliografi eller figurnummerering.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L867)

## Verifisering

1. Diff viser kun én setning endret rundt L867.
2. Sjekk at 7.3, 7.6, 8.3, 8.5 og 8.6 pkt 4 fortsatt er kompatible (ingen
   endring der).
3. Visuell lesning: andre avsnitt i 9.0 skal fortsatt lese som tre-grep-punchline +
   en kvalifisert «omfordeling-er-ikke-en-fjerde-spak»-presisering.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Commit-melding (faktisk brukt):

```
multi-agent review-batch 11 fix 3: kvalifiser «omfordeling ikke nødvendig» i 9.0 (for makespan / total varighet)
```

Bruker presiserte 2026-05-24 at reviewen i batch 11 er en uavhengig
multi-agent review hun kjørte selv, ikke en ekstern peer review. Prefiks er
derfor endret fra fix 1/fix 2-mønsteret («peer review-batch 11 …») til
«multi-agent review-batch 11 …» fra og med fix 3. Mappen
`batch_11_peer_review/` ble omdøpt til `batch_11_egen_review/` i egen commit
før fix 3-committen.

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_3.md` og commit separat med
melding:

```
arkiv: batch 11 multi-agent review-plan fix 3 i 014 fase 4 - report/
```

## Resterende fikser (egne planer senere)

- Fix 4 — 5.1.5 L355: 96 %-scenarioets bakoverregning svakt forklart
- Fix 5 — MC-gjentakelse mellom 5.1.6 (L365) og 8.4 (L824)
- Fix 6 — 9.0 L863: 10–17-mnd-påstand mangler caveat
- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium)
- Fix 8 — 5.1.7: definer «robust» eksplisitt
