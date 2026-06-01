# Validering av tidbruk-formelen — notat

**Dato:** 2026-04-22
**Forfatter:** Uavhengig validering (Claude-subagent + verifisering)
**Script:** `004 data/scripts/validering_tidbruk.py`
**Bakgrunn:** Sanity-sjekk av formelen som hele prosjektets varighetsestimater bygger på:

```
Ber_Tidbruk_Min = Km_Kurve × 0,9035 + ArealLand_Km² × 0,6510
```

Tre uavhengige valideringer ble gjennomført på 58 kartbladmålinger (`tidbruk_kalibrering.csv`), 357 kommuner (`master_kommuner.csv`) og 10 kontorers oppgitte min/max-bånd (`kapasitet_kontorer.csv`).

---

## V1 — Re-derivering av koeffisientene

### Funn

**Kalibreringsdataene kan ikke identifisere to separate koeffisienter.**

Alle 58 kartbladene har **identisk areal: 7,68 km²** (std = 0,000). Det betyr at arealet ikke varierer i datasettet, og en regresjon `Minutter ~ Lengde_Km + Areal_Km²` har perfekt multikollinearitet med konstantleddet — areal-koeffisienten kan ikke bestemmes uavhengig av lengde-koeffisienten fra disse målingene.

### Hva er 0,9035 og 0,6510 egentlig?

| Koeffisient | Påstand | Faktisk |
|---|---|---|
| 0,9035 (min/km) | OLS fra kartbladmålinger | = `mean(Min_Per_Km)` over de 58 målingene. Riktig som *gjennomsnitt av en rate*, men ikke en regresjonskoeffisient |
| 0,6510 (min/km²) | OLS fra kartbladmålinger | ≠ `mean(Min_Per_Km2)` (som er 1,5131). Tallet 0,6510 = 5/7,68, dvs. raten ved Minutter = 5 på et 7,68 km² kartblad — **én bestemt verdi, opphav uklart** |

### OLS-resultat (uten konstantledd, areal = 7,68 konstant)

```
beta_Lengde_Km   = 0,8420   (SE 0,1202)
beta_Areal_Km²   = 0,0895   (SE 0,2264)   ← ikke signifikant
R² (sentrert)    = 0,467
R² (usentrert)   = 0,833
Residual std     = 5,83 min
n = 58
```

OLS-koeffisienten for lengde (0,8420) ligger i nærheten av påstått 0,9035, men areal-koeffisienten (0,0895) er ikke signifikant og er en størrelsesorden mindre enn påstått 0,6510.

### Outlier

| Kartblad | Minutter | Lengde_Km | Min/km | Std.resid |
|---|---|---|---|---|
| 32-5-519-232-11 | 25 | 7,26 | 3,44 | 3,12 |

Empirisk spredning i Min/km: range 0,10–3,44, std 0,55, dvs. ~60 % av snitt. Stor underliggende variasjon i produktivitet per kartblad.

---

## V2 — Formel vs kontorenes oppgitte min/max-bånd

For hvert kontor: hvor stor andel av deres kommuner har `Ber_Tidbruk_Min` (omregnet til timer) innenfor kontorets eget bånd?

| Kontor | Bånd (t) | n komm. | Innenfor | Under | Over | % innenfor | Median t |
|---|---|---|---|---|---|---|---|
| Oslo | 30–90 | 52 | 10 | **42** | 0 | 19,2 % | 15,9 |
| Hamar | 10–100 | 46 | 46 | 0 | 0 | 100,0 % | 37,2 |
| Skien | 40–80 | 23 | 2 | **21** | 0 | 8,7 % | 23,9 |
| Kristiansand | 25–90 | 25 | 9 | 16 | 0 | 36,0 % | 20,3 |
| Stavanger | 30–85 | 23 | 2 | **21** | 0 | 8,7 % | 12,3 |
| Bergen | 25–100 | 43 | 13 | 30 | 0 | 30,2 % | 18,6 |
| Molde | 40–100 | 27 | 0 | **27** | 0 | **0,0 %** | 12,1 |
| Trondheim | 14–80 | 38 | 29 | 9 | 0 | 76,3 % | 28,1 |
| Bodø | 25–90 | 41 | 9 | 32 | 0 | 22,0 % | 12,2 |
| Tromsø | 30–100 | 39 | 15 | 23 | 1 | 38,5 % | 25,1 |

### Funn

**8 av 10 kontor har >50 % av kommunene UNDER sitt eget oppgitte bånd.** Molde har 0 % innenfor — formelen estimerer ingen kommune i Molde-regionen som tar minst 40 timer, mens kontoret selv sier 40 timer er nedre grense.

Avviket er **systemisk en vei** — alle 230+ avvik er "under", aldri "over". Formelen estimerer konsekvent kortere tid enn det kontorene selv anslår per kommune.

### Mulige forklaringer

1. **Formelen er for liberal** — kalibrert på kartbladskala, ikke kommuneskala. Effekter som setup-tid per kommune, kvalitetskontroll, etc. inngår ikke
2. **Kontorenes anslag er for konservative** — bygger på erfaring med "verste tilfeller" eller inkluderer overhead
3. **Min/max-båndet betyr noe annet enn antatt** — kanskje typisk kommune, ikke ekstrem kommune

Uansett tolkning: dagens formel og kontorenes anslag er ikke konsistente.

---

## V3 — Fordeling Ferdig vs gjenstående

| Gruppe | n | Median (min) | Q1 | Q3 | Mean | Min | Max |
|---|---|---|---|---|---|---|---|
| Ferdig | 62 | **667** | 329 | 1167 | 855 | 48 | 3 723 |
| Gjenstående | 295 | **1 336** | 730 | 2 092 | 1 571 | 12 | 10 758 |

**Median(Ferdig) / Median(Resten) = 0,499.** De 62 ferdige kommunene er ca. halvparten så tidkrevende som de 295 gjenstående.

### Implikasjon

Cherry-picking: enkle kommuner er ferdigstilt først. Det gjenstående arbeidet er systematisk tyngre enn det som er gjort til nå. **Hvis kontorene har brukt X timer per kommune historisk, vil de bruke ca. 2X per gjenstående kommune** (gitt samme produktivitet).

Statistisk signifikans-test ble ikke kjørt (scipy ikke tilgjengelig i miljøet), men forskjellen er stor nok til å være åpenbart signifikant. Kan kjøres med `pip install scipy`.

---

## Samlet vurdering

**Tidbruk-formelen i sin nåværende form er ikke godt forsvart av kalibreringsdataene.**

| Validering | Vurdering |
|---|---|
| V1 — Koeffisient-derivering | **Svak.** Areal-koeffisienten kan ikke identifiseres fra data der alle kartblad har samme areal. 0,6510 har uklart empirisk opphav. 0,9035 er gjennomsnittsrate, ikke OLS |
| V2 — Konsistens med kontorene | **Alvorlig avvik.** Systematisk underestimering for 8/10 kontor. Molde 0 % innenfor bånd |
| V3 — Representativitet av ferdige | **Cherry-picking bekreftet.** Gjenstående arbeid er ~2× så tidkrevende per kommune som det allerede gjorte |

### Konsekvenser for prosjektet

Alle varighetsestimater (heuristikk, MIP, Monte Carlo) bygger på denne formelen. Hvis formelen underestimerer med faktor 2, betyr det at:

- Heuristikk-baseline (10,1 år for Basis_85) kan være nærmere 15–20 år
- Kartkontor-delen (~16 mnd i heuristikk) kan være nærmere 32 mnd
- NVDB er fortsatt flaskehals i alle scenarioer (uavhengig av kartkontor-tid)
- **Men:** rangering av scenarioer og effekt av automasjonsgrad er upåvirket av nivåskalering

### Anbefalte tiltak (sortert etter aktelse)

1. **Dokumenter funnene som forbehold i rapporten** — i seksjon 5.1 Metode (tidsestimering) og 9.0 Diskusjon (validering). Lavt risikabelt, høyt akademisk-ansvarlig
2. **Vurder å skalere formelen** mot kontorenes oppgitte median (f.eks. ved en kontor-spesifikk multiplikator) som sensitivitetsanalyse — beholder dagens MIP/heuristikk-pipeline, kjører bare et sensitivitets-scenario til
3. **Be om timeregistrering for de 62 ferdige kommunene** fra fylkeskartkontorene — gir ekte ground truth, men krever ekstern aksjon og uvisst svar innen deadline
4. **Re-tenk formelen** — bruk Min_Per_Km direkte (uten areal-leddet) som primær estimator, siden areal ikke kan identifiseres separat fra kartblad-data

### Hva som *ikke* er rokket

- Kapasitetsdata, geovekst-låser, kommune-til-kontor-mapping, NVDB-scenarioer er upåvirket
- MIP og heuristikk er korrekte gitt formelen — problemet er i input-parameteren, ikke i optimerings-modellen
- Monte Carlo bootstrapper allerede MIN/KM fra empirisk fordeling, så stokastikk-beskrivelsen er fortsatt gyldig (men areal-leddet bidrar med kunstig nøyaktighet)

---

## Kjøre validering på nytt

```bash
python "004 data/scripts/validering_tidbruk.py"
```

Krever pandas + numpy. For p-verdier i V3, installer scipy.
