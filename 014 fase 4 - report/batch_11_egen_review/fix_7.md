# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 7

## Context

Sjuende fix i batch 11 fra den uavhengige multi-agent reviewen, og den
**eneste fiksen markert RISIKO: medium** i den opprinnelige review-listen
fordi den tilfører nytt innholdsbærende prosa-innhold (ikke bare en
kvalifisering eller deduplisering). Fix 1–6 og 8 er allerede committet
(fix 7 ble utsatt til ny sesjon i fix 6/fix 8). Innlevering 2026-06-01,
branch `fase-4-rapport`.

Arbeidsflyt: vis diff før commit, egen commit. Prefiks:
`multi-agent review-batch 11 fix 7: …`. Lukker batch 11.

## Fix 7 — 8.1 L761: legg til mekanisme for hovedbudskapet

**Plassering:** [005 report/rapport.md:761](005 report/rapport.md#L761) —
første avsnitt i 8.1 «Hovedbudskapet til Kartverket».

**Problem:** Avsnittet erklærer at NVDB er flaskehalsen og angir at det
gjelder uansett scenario og uansett rimelige kapasitetsforstyrrelser,
men forklarer ikke *hvorfor* det er slik. Reviewen flagget at
hovedbudskapet trenger en eksplisitt mekanisme-setning som forankrer
påstanden i NVDB-formelen (5.1.4) og i den strukturelle kapasitets-
asymmetrien (én manuell flaskehals nedstrøms vs. 10 parallelle kontor
oppstrøms). 7.6 L747 etablerer *funnet* men ikke mekanismen; 8.1 er
naturlig sted for forklaringen i diskusjonen.

**Kryssreferanser:**

- [5.1.4 L333-339](005 report/rapport.md#L333) — NVDB-formelen
  μ = (årsverk × manuell takt) / (1 − automasjonsgrad). Eksplisitt
  notert at konklusjonen «automasjonsgrad er dominerende usikkerhetskilde»
  delvis følger analytisk fra formelen.
- [4.0 L114](005 report/rapport.md#L114) — «80–90 % av lenkene legges inn
  maskinelt og resterende 10–20 % må håndteres manuelt av en dedikert
  bemanning på 0,5 årsverk».
- [6.0 L447](005 report/rapport.md#L447) — «Total årlig kapasitet
  kartkontor: 327 ukesverk (12 262 timer)».
- [5.1.4 L341](005 report/rapport.md#L341) — «300 lenker/person/dag,
  0,5 årsverk».
- [5.1.5 L355](005 report/rapport.md#L355) — bruker allerede formelen til
  å forklare at 96 % er den hypotetiske terskelen for 2-års-målet.
- [7.6 L747](005 report/rapport.md#L747) — «total varighet bestemmes
  nesten utelukkende av automasjonsgrad og manuell NVDB-kapasitet …
  kartkontorene fullfører innen 10–17 måneder; NVDB-fasen alene krever
  2,7–10,2 år».

**Risiko (medium):** Selv om mekanismen er underforstått i flere
underseksjoner, er en eksplisitt formulering ny prosa. Risikomomenter:

1. Numerisk presisjon mot 5.1.4-formelen og 7.x-resultatene.
2. Unngå å duplisere det 7.6 L747 og 8.1 L763 (kalibrerings-avsnittet)
   allerede sier.
3. Plassere setningen slik at flyten i avsnittet ikke brytes (avsnittet
   bygger: påstand → robusthet → driverne → anbefaling; mekanismen
   passer best mellom påstand og robusthet).

## Forslag til formulering

Den nye setningen plasseres rett etter åpningssetningen «Modellen
leverer et klart og robust hovedbudskap: **NVDB-overføringen er
flaskehalsen, ikke kartkontor-fasen**.» og før «Dette holder uansett
hvilket av de tre scenarioene …». Avsnittet vokser med én setning.

Tre alternativer:

**A — strukturell asymmetri (anbefalt):**

> Mekanismen er strukturell: NVDB-formelen μ = (årsverk × manuell takt)
> / (1 − automasjonsgrad) (jf. 5.1.4) gjør at den manuelle restandelen
> av lenkene må passere ett team på 0,5 årsverk uansett hvor effektivt
> FME håndterer resten, mens kartkontor-arbeidet fordeles på 10
> parallelle kontor med samlet 327 ukesverk/år. Én sekvensiell
> flaskehals nedstrøms står mot 10 parallelle kapasitetspunkter
> oppstrøms, og asymmetrien sikrer at NVDB-tiden dominerer i alle
> realistiske automasjonsregimer.

*Begrunnelse:* Bygger eksplisitt på 5.1.4-formelen og kjente
kapasitetstall (327 ukesverk, 0,5 årsverk). Plasserer mekanismen som
strukturell, ikke som kalibrerings-artefakt. To setninger.

**B — konkret 90 %-eksempel:**

> Mekanismen kan illustreres direkte ved 90 %-scenarioet: ~10 % av de
> 2,1 mill. gjenstående lenkene må behandles manuelt og passere ett
> team på 0,5 årsverk × 300 lenker/dag = 150 lenker/dag, hvilket alene
> tilsvarer flere år arbeid (jf. 5.1.4). Kartkontor-arbeidet fordeles
> derimot på 10 parallelle kontor med samlet 327 ukesverk/år, og
> leveres på 10–17 måneder. Asymmetrien er strukturell — én sekvensiell
> flaskehals mot 10 parallelle kapasitetspunkter — ikke et resultat av
> kalibreringsvalg.

*Begrunnelse:* Mer konkret og tallrik, men risikerer å duplisere
arithmetikken i 8.1 L763-avsnittet (kalibreringen). «Flere år» er
upresist (faktisk 5–6 år for manuelt alene ved 90 %), men presisjon her
ville lagt for stor vekt på enkelttall.

**C — minimal, ren formel-referanse:**

> Mekanismen er strukturell asymmetri: NVDB-formelen (5.1.4) bundler
> flaskehalsen til den manuelle restandelen av lenkene gjennom ett team
> på 0,5 årsverk, mens kartkontor-arbeidet er fordelt på 10 parallelle
> kontor (samlet 327 ukesverk/år).

*Begrunnelse:* Korteste form. Én setning. Mister «hvorfor automasjon
ikke redder situasjonen» (FME uendelig rask, men manuell tail
gjenstår), men gjenfinner det implisitt via formel-henvisningen.

## Valgt formulering

**A** (bekreftet av bruker 2026-05-25) — strukturell asymmetri.

Endring (én streng-erstatning, setningen tilføyes etter den fete
påstanden og før «Dette holder uansett …»):

- Gammel:
  `Modellen leverer et klart og robust hovedbudskap: **NVDB-overføringen er flaskehalsen, ikke kartkontor-fasen**. Dette holder uansett hvilket av de tre scenarioene som realiseres`
- Ny:
  `Modellen leverer et klart og robust hovedbudskap: **NVDB-overføringen er flaskehalsen, ikke kartkontor-fasen**. Mekanismen er strukturell: NVDB-formelen μ = (årsverk × manuell takt) / (1 − automasjonsgrad) (jf. 5.1.4) gjør at den manuelle restandelen av lenkene må passere ett team på 0,5 årsverk uansett hvor effektivt FME håndterer resten, mens kartkontor-arbeidet fordeles på 10 parallelle kontor med samlet 327 ukesverk/år. Én sekvensiell flaskehals nedstrøms står mot 10 parallelle kapasitetspunkter oppstrøms, og asymmetrien sikrer at NVDB-tiden dominerer i alle realistiske automasjonsregimer. Dette holder uansett hvilket av de tre scenarioene som realiseres`

Strengen er unik i filen (Grep verifiseres før edit).

## Risiko / sideeffekter

- Medium. Eneste fiks i batch 11 som tilfører ny innholdsbærende prosa.
- Numeriske referanser (327 ukesverk, 0,5 årsverk, NVDB-formel) er
  verifisert mot 5.1.4, 6.0 tabell og 4.0.
- Risiko for duplisering med 7.6 og 8.1 L763 vurdert; valgt formulering
  fokuserer på *mekanisme* (hvorfor), mens 7.6 etablerer *funn* (hva)
  og L763 etablerer *kalibrering* (mot eksternt tallgrunnlag).
- Andre underseksjoner som refererer 8.1 (5.1.5 «Dette gir Kartverket
  et argument for FME-investering») er ikke berørt.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (én streng-erstatning i 8.1 L761)

## Verifisering

1. Diff viser kun én setning tilføyd i 8.1 første avsnitt.
2. Numerisk kryss-sjekk: 327 ukesverk (jf. 6.0 L447), 0,5 årsverk
   (4.0 L114, 5.1.4 L341), 10 kontor (5.2.1, 6.0), NVDB-formel
   (5.1.4 L333).
3. Visuell lesning: avsnittet flyter naturlig fra påstand → mekanisme
   → robusthet → anbefaling.
4. Sjekk at ingen tall i 8.1 L763 (kalibreringen) blir motsagt.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
multi-agent review-batch 11 fix 7: mekanisme-setning for NVDB-flaskehals i 8.1
```

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_7.md` og commit separat:

```
arkiv: batch 11 multi-agent review-plan fix 7 i 014 fase 4 - report/
```

## Resterende fikser

Ingen — fix 7 lukker batch 11.
