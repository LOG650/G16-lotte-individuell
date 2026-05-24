# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 6

## Context

Sjette fix i batch 11 fra den uavhengige multi-agent reviewen. Fix 1
(`f9ac0b9`), fix 2 (`532832d`), fix 3 (`8f97544`), fix 4 (`69a6657`) og fix
5 (`aec3e90`) er allerede committet. Innlevering 2026-06-01, branch
`fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.
Prefiks: `multi-agent review-batch 11 fix N: …`.

## Fix 6 — «10–17 måneder i alle scenarioer» mangler caveat i 9.0

**Plassering:** [005 report/rapport.md:863](005 report/rapport.md#L863)

**Problem:** Setningen lyder:

> Kartkontorene har derimot kapasitet til å fullføre arbeidet på under
> halvannet år (10–17 måneder) i alle scenarioer.

To uklarheter:

1. **Range-kilden er heterogen.** «10–17 måneder» henter nedre fra MIPs
   optimum (10–11 mnd S0–S4 deterministisk, jf. 7.2/7.4) og øvre fra
   heuristikkens MC P50 (~510 dager ≈ 17 mnd, jf. 7.2 og 7.5). Range er
   altså sammensatt av to ulike metoder/metrikker, ikke en intern
   variasjon innenfor én metode.

2. **«I alle scenarioer» er flertydig.** Påstanden gjelder de tre
   NVDB-scenarioene (Basis_85, Middels_90, Samferdsel_96). Den gjelder
   *også* S0–S4 (10–11 mnd), men S5_Alle_minus50 gir 14 mnd (jf. 7.4,
   Not Solved-status, plausibel ved matematisk minimum 14,4). 14 < 18 så
   påstanden «under halvannet år» holder rent teknisk, men S5 er ikke
   eksplisitt med i «10–17».

**Kryssreferanser:**

- [7.2 L669](005 report/rapport.md#L669) — «heuristikken ferdigstiller …
  innen ca. 16,5 måneder; MIP-planen … innen 10–11 måneder»; MC P50
  heuristikk 510 dager → MIP 409–452 dager.
- [7.4 L693-697](005 report/rapport.md#L693) — «S0–S4 holder den seg i
  området 10–11 måneder; bare i S5_Alle_minus50 forskyves den til 14
  måneder (matematisk nedre grense 14,4)».
- [7.6 L747](005 report/rapport.md#L747) — «Kartkontorene fullfører innen
  10–17 måneder i alle scenarioer» (samme uklarhet, men 7.6 er en
  oppsummering; 9.0 er konklusjonen og bør være presisjonsmessig
  selv-bærende).

## Forslag til formulering

Alle alternativer erstatter setningen på L863. Det er flere meningsfulle
caveats; jeg presenterer tre.

**A — metodecaveat (anbefalt):**

> Kartkontorene har derimot kapasitet til å fullføre arbeidet på under
> halvannet år (MIP-modellens optimum 10–11 måneder, heuristikkens
> Monte Carlo P50 ~17 måneder) i alle tre NVDB-scenarioer.

*Begrunnelse:* Adresserer pkt 1 (range-kilden). Gir leseren konteksten
for hvorfor range er bred uten å bli detaljert. Mister «10–17»-tallparet
men gjenfinner det implisitt.

**B — scenariocaveat:**

> Kartkontorene har derimot kapasitet til å fullføre arbeidet på under
> halvannet år (10–17 måneder) i alle tre NVDB-scenarioer, og innen 14
> måneder selv ved halvert kartkontor-kapasitet (S5, jf. 7.4).

*Begrunnelse:* Adresserer pkt 2. Tydeliggjør at robustheten også dekker
ekstrem kapasitetsvariasjon. Beholder «10–17»-tallparet.

**C — kombinert (begge caveats):**

> Kartkontorene har derimot kapasitet til å fullføre arbeidet på under
> halvannet år i alle tre NVDB-scenarioer (MIP-optimum 10–11 måneder,
> heuristikkens Monte Carlo P50 ~17 måneder), og innen 14 måneder selv
> ved halvert kartkontor-kapasitet (S5, jf. 7.4).

*Begrunnelse:* Mest komplett, lengst. Risikerer å bli for tett pakket for
en konklusjon-setning.

## Valgt formulering

**A** (bekreftet av bruker 2026-05-24) — metodecaveat. 7.6 L747 lar vi
stå urørt: 7.6 L749 (etter fix 2) etablerer allerede MIP-vs-heuristikk-
forskjellen lokalt, så å oppdatere L747 også ville duplisere det.

Endring (én streng-erstatning):

- Gammel: `Kartkontorene har derimot kapasitet til å fullføre arbeidet på under halvannet år (10–17 måneder) i alle scenarioer.`
- Ny:     `Kartkontorene har derimot kapasitet til å fullføre arbeidet på under halvannet år (MIP-modellens optimum 10–11 måneder, heuristikkens Monte Carlo P50 ~17 måneder) i alle tre NVDB-scenarioer.`

Strengen er unik i filen (Grep verifiseres før edit).

## Risiko / sideeffekter

- Lav. Endrer kun én setning i 9.0 første avsnitt. Resten av 9.0 og
  forbindelser til 7.2, 7.4, 7.5 er upåvirket.
- Ingen tall endres (10, 11, 17, 14 er allerede etablert i 7.x).
- 7.6 L747 har samme «10–17 måneder i alle scenarioer»-formulering. Den
  bør strengt tatt også oppdateres for full konsistens, men 7.6 er en
  oppsummering der konteksten fra 7.2/7.4 er nær, mens 9.0 er fjernet
  og bør stå alene. Forslag: la 7.6 stå urørt i denne fiksen og ta det
  som eventuell oppfølger hvis reviewen flagget begge.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L863)

## Verifisering

1. Diff viser kun én setning endret rundt L863.
2. Tall verifiseres mot 7.2 og 7.4: MIP 10–11 mnd (S0–S4), heuristikk MC
   P50 ~510 dager (~17 mnd), S5-ekstrem 14 mnd.
3. Påstanden «under halvannet år» (= 18 mnd) holder for alle nevnte tall.
4. 7.6 L747 sjekkes for konsistens; hvis reviewer flagget begge, oppdater
   begge i samme commit.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
multi-agent review-batch 11 fix 6: caveat på 10–17-mnd-påstand i 9.0
```

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_6.md` og commit separat:

```
arkiv: batch 11 multi-agent review-plan fix 6 i 014 fase 4 - report/
```

## Resterende fikser (egne planer senere)

- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium, utsatt til ny
  sesjon per brukervalg 2026-05-24)
- Fix 8 — 5.1.7: definer «robust» eksplisitt (tas etter fix 6 i samme
  sesjon)
