# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 4

## Context

Fjerde fix i batch 11 fra den uavhengige multi-agent reviewen. Fix 1
(`f9ac0b9`), fix 2 (`532832d`) og fix 3 (`8f97544`) er allerede committet.
Mappen ble omdøpt fra `batch_11_peer_review/` til `batch_11_egen_review/` i
commit `30704db`. Innlevering 2026-06-01, branch `fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.
Prefiks fra og med fix 3: `multi-agent review-batch 11 fix N: …`.

## Fix 4 — 96 %-scenarioets «bakoverregning» er svakt forklart i 5.1.5

**Plassering:** [005 report/rapport.md:355](005 report/rapport.md#L355)

**Problem:** Rasjonale-kolonnen i tabell 5.1 (L353) sier «Optimistisk øvre
grense, bakoverregnet for å treffe et 2-års-mål», og prosateksten L355 sier:

> Samferdselsavdelingen opererer selv kun med 80–90 %. 96 %-scenarioet er
> dermed ikke deres tall, men en hypotetisk målsetning for å kvantifisere
> hva FME-automasjon på "toppkvalitet" ville kreve. Dette gir Kartverket et
> argument for FME-investering: å nå fra 85 % til 96 % automasjonsgrad
> halverer total prosjektvarighet.

«Bakoverregningen» har ingen mekanisme i prosaen. Leseren ser «hypotetisk
målsetning for å kvantifisere hva FME-automasjon på toppkvalitet ville
kreve» og må selv slutte seg til at det er en bakoverregning fra et 2-års-mål
gjennom NVDB-formelen. To uklarheter forblir:

1. *Hvordan* bakoverregnes 96 % fra et 2-års-mål? Mekanismen er
   NVDB-formelen i 5.1.4 ($\mu = \text{årsverk} \cdot \text{takt} / (1 -
   \text{auto})$), med fast manuell kapasitet 0,5 × 300 = 150 lenker/dag
   og total arbeidsmengde ~2,1 mill. lenker. Den nødvendige automasjons-
   graden for å treffe 2 år er ~96,3 %, rundet ned til 96 %.
2. *Hvorfor* gir 96 % modellresultatet 2,7 år (kap. 7.1), ikke 2? Fordi
   (a) 96 % er rundet ned fra ~96,3 %, og (b) modellens 260-dagers-
   konvensjon avviker fra samferdselsavdelingens 240 (jf. 5.1.2).

**Kryssreferanser:**

- [Tabell 5.1 L353](005 report/rapport.md#L353) — rasjonale-kolonne for 96 %
- [5.1.4 L331-339](005 report/rapport.md#L331) — NVDB-formel og parametre
- [5.1.2 L319](005 report/rapport.md#L319) — 260/240-dager-konvensjon
- [8.1 L761](005 report/rapport.md#L761) — «96 % er en hypotetisk øvre
  grense bakoverregnet mot et 2-årsmål, ikke en prognose, jf. 5.1.5»
- [7.1 / oppsummering_mip_vektet.csv] — Samferdsel_96 makespan 2,75 år

## Forslag til formulering

Alle alternativer erstatter setning to i avsnittet (den med «hypotetisk
målsetning for å kvantifisere …»). Resten av avsnittet (siste setning om
FME-investerings-argument) beholdes.

**A — mekanisme + 2,7-avvik:**

> 96 %-scenarioet er dermed ikke deres tall, men en hypotetisk målsetning
> bakoverregnet fra et 2-års-mål: gitt fast manuell kapasitet (0,5 årsverk
> × 300 lenker/dag) er ~96 % det laveste automasjonsnivået som via
> NVDB-formelen i 5.1.4 holder de gjenstående ~2,1 mill. lenkene innenfor
> 2 år. Modellens punktestimat på ~2,7 år (kap. 7.1, jf. tabell 7.1) ligger
> over 2 fordi 96 % er rundet ned fra ~96,3 % og fordi modellens
> 260-dagers konvensjon avviker fra samferdselsavdelingens 240 (jf. 5.1.2).

**B — kort: bare mekanismen, ikke 2,7 år-avviket:**

> 96 %-scenarioet er dermed ikke deres tall, men en hypotetisk målsetning
> bakoverregnet fra et 2-års-mål via NVDB-formelen i 5.1.4: ~96 %
> automasjon er det laveste nivået som med fast manuell kapasitet (0,5
> årsverk × 300 lenker/dag) holder de gjenstående ~2,1 mill. lenkene
> innenfor 2 år.

**C — bare lokal presisering uten formel-referanse:**

> 96 %-scenarioet er dermed ikke deres tall, men bakoverregnet fra et
> 2-års-mål: hvilken automasjonsgrad ville kreves for at fast manuell
> kapasitet (0,5 årsverk × 300 lenker/dag) kunne håndtere ~2,1 mill.
> gjenstående lenker innenfor 2 år? Svaret er ~96 %.

## Valgt formulering

**A** (bekreftet av bruker 2026-05-24) — forklarer bakoverregningen via
5.1.4-formelen og forklarer hvorfor modellresultatet er 2,7 år (ikke 2).
Avsnittet vokser fra 3 til 4 setninger.

Endring (én streng-erstatning):

- Gammel: `96 %-scenarioet er dermed ikke deres tall, men en hypotetisk målsetning for å kvantifisere hva FME-automasjon på "toppkvalitet" ville kreve.`
- Ny:     `96 %-scenarioet er dermed ikke deres tall, men en hypotetisk målsetning bakoverregnet fra et 2-års-mål: gitt fast manuell kapasitet (0,5 årsverk × 300 lenker/dag) er ~96 % det laveste automasjonsnivået som via NVDB-formelen i 5.1.4 holder de gjenstående ~2,1 mill. lenkene innenfor 2 år. Modellens punktestimat på ~2,7 år (kap. 7.1, jf. tabell 7.1) ligger over 2 fordi 96 % er rundet ned fra ~96,3 % og fordi modellens 260-dagers konvensjon avviker fra samferdselsavdelingens 240 (jf. 5.1.2).`

Strengen er unik i filen (verifiseres med Grep før edit).

## Risiko / sideeffekter

- Lav. Endrer kun en setning i 5.1.5; tabell 5.1 og resten av 5.1.5 er
  upåvirket. Ingen tall endres, ingen kryssreferanser brytes.
- Tallet 2,75 år (kap. 7.1, fra `oppsummering_mip_vektet.csv` Samferdsel_96)
  må verifiseres som riktig kilde. (Heuristikk gir 2,69 år; MIP 2,75 år.
  «Modellens punktestimat» er ambivalent — 2,75 er MIP, 2,69 er heuristikk.
  Anbefaling: bruk «~2,7 år» for å unngå presisjonsfordring, eller bruk
  konkret tall + spesifiser kilde.)

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L355)

## Verifisering

1. Diff viser kun én setning endret rundt L355 (pluss evt. tilføyd ekstra
   setning).
2. Sjekk at 8.1 L761 fortsatt er kompatibel (skal være det — den henviser
   til 5.1.5 og blir mer konsistent etter fiksen).
3. Sjekk at tabell 5.1 rasjonale-tekst fortsatt henger sammen med prosaen
   under (skal være det).
4. Verifiser at «2,7 år» eller spesifikt tall stemmer med
   `oppsummering_scenarioer.csv` / `oppsummering_mip_vektet.csv` for
   Samferdsel_96.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
multi-agent review-batch 11 fix 4: forklar 96 %-scenarioets bakoverregning i 5.1.5
```

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_4.md` og commit separat:

```
arkiv: batch 11 multi-agent review-plan fix 4 i 014 fase 4 - report/
```

## Resterende fikser (egne planer senere)

- Fix 5 — MC-gjentakelse mellom 5.1.6 (L365) og 8.4 (L824)
- Fix 6 — 9.0 L863: 10–17-mnd-påstand mangler caveat
- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium)
- Fix 8 — 5.1.7: definer «robust» eksplisitt
