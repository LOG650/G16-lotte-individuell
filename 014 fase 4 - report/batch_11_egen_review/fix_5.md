# Batch 11: Prosa-fikser fra uavhengig multi-agent review — Fix 5

## Context

Femte fix i batch 11 fra den uavhengige multi-agent reviewen. Fix 1
(`f9ac0b9`), fix 2 (`532832d`), fix 3 (`8f97544`) og fix 4 (`69a6657`) er
allerede committet. Innlevering 2026-06-01, branch `fase-4-rapport`.

Arbeidsflyt: én fix om gangen, vis diff før commit, egen commit per fix.
Prefiks: `multi-agent review-batch 11 fix N: …`.

## Fix 5 — MC-gjentakelse mellom 5.1.6 og 8.4

**Plasseringer:**

- [005 report/rapport.md:365](005 report/rapport.md#L365) — siste setning i
  5.1.6 Monte Carlo-modellen
- [005 report/rapport.md:824](005 report/rapport.md#L824) — bold-avsnittet
  «Deterministisk rammeverk utenfor de tre stokastiske kildene» i 8.4

**Problem:** Samme antagelse er beskrevet to ganger.

L365 (5.1.6, siste setning i avsnittet om grunnpakke-tillegget):

> Kartkontor-kapasitet og Geovekst-låseperioder holdes også konstante i
> Monte Carlo-kjøringen.

L824 (8.4, bold-avsnitt med kontekst og følger):

> **Deterministisk rammeverk utenfor de tre stokastiske kildene.** Monte
> Carlo varierer kun MIN/KM, manuell NVDB-takt og automasjonsgrad.
> Geovekst-låseperioder, kartkontor-kapasitet og fremdriftsstatus (62
> ferdig, 48 påbegynt) holdes konstante i alle 500 iterasjoner. I
> virkeligheten kan Geovekst-prosjekter forsinkes eller fremskyndes, og
> kapasiteten kan variere fra år til år … Kapasitets-sensitivitetsanalysen
> i 7.4 dekker deler av dette gapet …

L824 er den faglig riktige plassen (drøftelse av antagelser med kontekst,
følger og henvisning til 7.4). L365 er en stikk-ut-setning på slutten av et
avsnitt som ellers handler om grunnpakke-leddet (0,6510 min/km²).
Avsnittet i 5.1.6 har allerede en forward-pointer for grunnpakke
(«drøftes som forbehold i 8.2»), men ingen tilsvarende pointer for
kapasitet/Geovekst — bare en kort gjentagelse.

5.1.6's bullet-liste over L361-363 lister allerede *hva som samples*
(MIN/KM, manuell takt, automasjonsgrad). At kapasitet og Geovekst er
konstante, følger implisitt av at de ikke står i listen, og blir uansett
drøftet eksplisitt i 8.4.

## Forslag til formulering

**A — slett trailing-setningen i 5.1.6 (anbefalt):**

L365 ender med «… representerer måleusikkerhet i MIN/KM, manuell
NVDB-takt og automasjonsgrad, men ikke usikkerhet knyttet til
grunnpakke-leddet. Dette drøftes som forbehold i 8.2.» — naturlig
avslutning på grunnpakke-temaet. Den ekstra kartkontor/Geovekst-setningen
fjernes. L824 i 8.4 beholdes uendret.

*Begrunnelse:* Cleanest. Bullet-listen ovenfor sier hva som samples; alt
annet er per definisjon konstant. 8.4 har konteksten der den hører hjemme.

**B — bytt trailing-setning med kort forward-pointer:**

> «Kartkontor-kapasitet og Geovekst-låseperioder holdes også konstante;
> følgene for tolkningen av P5–P95-bånd drøftes i 8.4.»

*Begrunnelse:* Beholder antagelsen synlig i metoden + signaliserer hvor
drøftelsen er. Litt mer ord, men mindre risiko for at leseren glemmer at
kapasitet er holdt konstant.

**C — flytt setningen helt til 8.4 og slett i 5.1.6:**

Funksjonelt lik A, men reformulerer L824 til å åpne med «I Monte Carlo
holdes kartkontor-kapasitet og Geovekst-låseperioder konstante, i tillegg
til fremdriftsstatus …». Ingen netto endring i innhold, men gjør 8.4 til
*eneste* sted antagelsen står.

*Begrunnelse:* Mest renslig dedup, men endrer mer tekst (touchet både
5.1.6 og 8.4). Marginal forbedring over A.

## Valgt fremgangsmåte

**A** (bekreftet av bruker 2026-05-24) — slett trailing-setningen i 5.1.6.

Endring (én streng-erstatning):

- Gammel: `Dette drøftes som forbehold i 8.2. Kartkontor-kapasitet og Geovekst-låseperioder holdes også konstante i Monte Carlo-kjøringen.`
- Ny:     `Dette drøftes som forbehold i 8.2.`

Strengen «Kartkontor-kapasitet og Geovekst-låseperioder holdes også
konstante i Monte Carlo-kjøringen.» er unik i filen (Grep verifiseres før
edit).

## Risiko / sideeffekter

- Lav. Sletter én setning på L365; resten av 5.1.6 (avsnittet om
  grunnpakke + bullet-listen) er upåvirket. 8.4 er upåvirket.
- Mulig leser-effekt: noen lesere kunne fortsatt fått «hva er ellers
  konstant?»-spørsmål etter 5.1.6. Det er imidlertid akkurat det 8.4 er
  for — og 5.1.6's allerede eksisterende «drøftes som forbehold i 8.2»
  etablerer at 5.1.6 ikke er den uttømmende drøftelsen.
- Ingen tall endres, ingen kryssreferanser brytes.

## Critical files

- [005 report/rapport.md](005 report/rapport.md) — eneste fil som endres
  (L365, sletter siste setning i avsnittet)

## Verifisering

1. Diff viser kun én setning slettet på L365.
2. 5.1.6's bullet-liste over (1) MIN/KM, (2) manuell takt, (3)
   automasjonsgrad er uendret.
3. 8.4's bold-avsnitt om deterministisk rammeverk er uendret.
4. Visuell lesning: avsnittet i 5.1.6 ender naturlig på grunnpakke-
   pointeren («drøftes som forbehold i 8.2») uten å miste flyt.

## Commit

Branch: `fase-4-rapport` (allerede aktiv)

Foreslått commit-melding:

```
multi-agent review-batch 11 fix 5: fjern MC-gjentakelse i 5.1.6 (overlapp med 8.4)
```

## Etterarbeid

Etter commit: kopier denne planfilen som
`014 fase 4 - report/batch_11_egen_review/fix_5.md` og commit separat:

```
arkiv: batch 11 multi-agent review-plan fix 5 i 014 fase 4 - report/
```

## Resterende fikser (egne planer senere)

- Fix 6 — 9.0 L863: 10–17-mnd-påstand mangler caveat
- Fix 7 — 8.1 L761: legg til mekanisme (RISIKO: medium)
- Fix 8 — 5.1.7: definer «robust» eksplisitt
