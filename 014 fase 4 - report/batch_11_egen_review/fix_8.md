# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 8

## Context

Åttende fix i batch 11 (fix 7 er hoppet over til ny sesjon pga. medium-
risiko). Fix 1–6 er committet (`f9ac0b9`, `532832d`, `8f97544`, `69a6657`,
`aec3e90`, `e1f6aa8`). Innlevering 2026-06-01, branch `fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.
Prefiks: `multi-agent review-batch 11 fix N: …`.

## Fix 8 — Definer «robust» eksplisitt i 5.1.7

**Plassering:** [005 report/rapport.md:371](005 report/rapport.md#L371) —
slutten av første underavsnitt i 5.1.7 Validitet og reliabilitet («Intern
validitet»).

**Problem:** Ordet «robust» brukes flere ganger uten eksplisitt
definisjon:

- [5.1.7 L371](005 report/rapport.md#L371): «hovedfunnet om
  NVDB-flaskehalsen er robust på tvers av store endringer i
  inputantagelser»
- [7.6 L751](005 report/rapport.md#L751): «**Resultatet er robust mot
  rimelige forstyrrelser.**»
- [8.1 L761](005 report/rapport.md#L761): «Modellen leverer et klart og
  robust hovedbudskap»
- [9.0 L863](005 report/rapport.md#L863) (etter fix 6): «Resultatet er
  robust mot kapasitetsforstyrrelser …»

«Robust» kan bety mange ting: at punktestimatet ikke endres, at den
kvalitative slutningen overlever, at konfidensintervallene er smale, at
modellen tåler datafeil. Reviewen flagget at en eksplisitt definisjon
mangler — leseren må ellers selv slutte hva som menes fra konteksten.

I 5.1.7 er definisjonen mest hjemme: dette er metode-seksjonen om
validitet, og «robust» introduseres her som en *egenskap* sensitivitets-
analysene er ment å bekrefte. En kort parentes eller en setning rett etter
L371-bruken vil etablere termen for alle senere bruk.

## Forslag til formulering

Plassering: rett etter setningen «… bekrefter at hovedfunnet om
NVDB-flaskehalsen er robust på tvers av store endringer i
inputantagelser.» (samme avsnitt).

**A — kort parentes inne i eksisterende setning (anbefalt):**

> «… bekrefter at hovedfunnet om NVDB-flaskehalsen er robust på tvers av
> store endringer i inputantagelser (med *robust* menes her at den
> kvalitative slutningen overlever variasjon, ikke at punktestimatet er
> uendret).»

*Begrunnelse:* Plasserer definisjonen presist der termen introduseres.
Kort, fanger den viktigste distinksjonen (kvalitativ slutning vs
punktestimat). Avsnittet vokser med én parentes.

**B — kort ny setning etter eksisterende:**

> «… bekrefter at hovedfunnet om NVDB-flaskehalsen er robust på tvers av
> store endringer i inputantagelser. *Robust* brukes her om at den
> kvalitative slutningen (NVDB er flaskehalsen, ikke kartkontor-fasen)
> overlever variasjon, selv om absolutte punktestimater varierer.»

*Begrunnelse:* Tydeligere strukturelt skille mellom kontekstuell bruk og
definisjon. Litt lengre. Henviser eksplisitt til hovedfunnet.

**C — minimal: bare parentes etter første bruk:**

> «… bekrefter at hovedfunnet om NVDB-flaskehalsen er robust (kvalitativ
> slutning uendret, ikke nødvendigvis punktestimat) på tvers av store
> endringer i inputantagelser.»

*Begrunnelse:* Korteste form. Mister noe presisjon men er
plassmessig kompakt.

## Valgt formulering

**A** (bekreftet av bruker 2026-05-24) — kort parentes inne i
eksisterende setning.

Endring (én streng-erstatning):

- Gammel: `bekrefter at hovedfunnet om NVDB-flaskehalsen er robust på tvers av store endringer i inputantagelser.`
- Ny:     `bekrefter at hovedfunnet om NVDB-flaskehalsen er robust på tvers av store endringer i inputantagelser (med *robust* menes her at den kvalitative slutningen overlever variasjon, ikke at punktestimatet er uendret).`

Strengen er unik i filen (Grep verifiseres før edit).

## Risiko / sideeffekter

- Lav. Endrer kun én setning i 5.1.7 første avsnitt. Resten av 5.1.7 og
  alle senere bruk av «robust» (7.6, 8.1, 9.0) blir nå dekket av denne
  definisjonen.
- Ingen tall endres, ingen kryssreferanser brytes.
- Senere bruk av «robust» blir mer presisjonsmessig forankret uten at
  selve setningene må endres.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L371)

## Verifisering

1. Diff viser kun én setning endret rundt L371 (tilføyd parentes).
2. Sjekk at 7.6 L751, 8.1 L761, 9.0 L863 fortsatt er kompatible (skal
   være det — definisjonen er forenelig med hvordan termen brukes der).
3. Visuell lesning: avsnittet om Intern validitet flyter fortsatt naturlig
   etter at parentesen er tilført.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
multi-agent review-batch 11 fix 8: definer «robust» eksplisitt i 5.1.7
```

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_8.md` og commit separat:

```
arkiv: batch 11 multi-agent review-plan fix 8 i 014 fase 4 - report/
```

## Resterende fikser

- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium, utsatt til ny
  sesjon per brukervalg 2026-05-24)
