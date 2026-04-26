# LOG650 Prosjekt - Kontekst for Claude

## Om prosjektet

**Tittel:** Kvalitetsheving av FKB-TraktorvegSti før implementering i NVDB
**Fag:** LOG650 Logistikk og KI (Høgskolen i Molde)
**Prosjektleder:** Lotte Picard (individuelt prosjekt - G16-lotte-individuell)
**Kunde:** Statens Kartverk, Region og Samfunnskontakt
**Periode:** 12.01.2026 – 01.06.2026
**Nåværende fase:** Fase 3 - Gjennomføring

### Problemstilling

Kartverkets 10 fylkeskartkontor skal kvalitetsheve datasettet FKB-TraktorvegSti før det overføres til NVDB (Nasjonal vegdatabank). Dette er et **ressursallokering- og produksjonsplanleggingsproblem**:
- Fordele 357 kommuner til 10 kontorer med varierende kapasitet
- Bestemme rekkefølge og timing
- Ta hensyn til Geovekst-kartleggingsprosjekter som låser kommuner i perioder
- Minimere total prosjektvarighet, balansere arbeidsbelastning

### Produksjonskjede

```
Kartkontor (kvalitetsheving) → Samferdselsavdelingen (NVDB-overføring via FME)
```

- **Kartkontor:** 10 kontorer, ulik kapasitet (ukesverk), manuell redigering
- **NVDB-overføring:** 2 stillinger × 25% = 0,5 årsverk. FME-automatisert, rest manuelt. 300-400 lenker/person/dag.
- **Status per april 2026:** 62 ferdig kvalitetshevet, 48 påbegynt, 247 ikke startet. **Ingen** er overført til NVDB ennå.

## Mappestruktur

```
G16-lotte-individuell/
├── CLAUDE.md                        ← Denne filen
├── STATUS.md                        ← Levende statusdokument (auto-generert)
├── 000 templates/
│   └── Mal prosjekt LOG650 v2.docx
├── 001 info/
├── 002 meetings/
├── 003 references/
├── 004 data/
│   ├── raw_data/                    ← Rådata + kartverket_fylker.geojson
│   ├── processed_data/              ← Vaskede data + resultatdata
│   │   ├── master_kommuner.csv
│   │   ├── kapasitet_kontorer.csv
│   │   ├── geovekst_prosjekter.csv
│   │   ├── nvdb_overfoering.csv
│   │   ├── tidbruk_kalibrering.csv        (58 kartbladmålinger)
│   │   ├── tidbruk_konstanter.csv         (0,9035 og 0,6510)
│   │   ├── tidsplan_<scenario>.csv        (heuristikk-output)
│   │   ├── kapasitetsbruk_per_uke_*.csv
│   │   ├── flaskehals_nvdb_*.csv
│   │   ├── oppsummering_scenarioer.csv
│   │   ├── monte_carlo_*.csv              (summary, varigheter, per_kommune, ko_percentiles)
│   │   ├── oppsummering_tidbruk_sensitivitet_heur.csv  (jobb #1, 2026-04-23)
│   │   ├── monte_carlo_tidbruk_summary.csv             (jobb #1, 2026-04-23)
│   │   ├── monte_carlo_tidbruk_varigheter.csv          (jobb #1, 2026-04-23)
│   │   ├── tidsplan_<scenario>_skala<X>.csv            (jobb #1, 6 filer)
│   │   ├── monte_carlo_automasjon_summary.csv          (jobb #2, 2026-04-23)
│   │   ├── monte_carlo_automasjon_varigheter.csv       (jobb #2, 2026-04-23)
│   │   ├── tidsplan_mip_vektet_<scenario>.csv          (MIP-output, Bolk A)
│   │   ├── oppsummering_mip_vektet.csv                 (MIP per-scenario sammendrag)
│   │   ├── sammenligning_heuristikk_mip_vektet.csv     (heuristikk vs MIP)
│   │   ├── mip_sensitivitet_<variant>_<scenario>.csv   (Bolk B, 18 filer)
│   │   ├── oppsummering_sensitivitet.csv               (Bolk B sammendrag)
│   │   ├── monte_carlo_mip_*.csv                       (Bolk D, summary/varigheter/per_kommune/ko_percentiles)
│   │   ├── arkiv_pre_kalibrering/         (utdaterte MIP-CSV fra pre-kalibrering 2026-04-19)
│   │   ├── arkiv_pre_230_fiks/            (42 resultat-CSV fra før 260-fiks 2026-04-23)
│   │   └── arkiv_pre_245_fiks/            (53 resultat-CSV fra før 245-fiks 2026-04-24)
│   ├── scripts/
│   │   ├── vask_og_strukturer.py    ← Hovedscript for datavask
│   │   ├── heuristikk.py            ← Regelbasert baseline-simulering
│   │   ├── monte_carlo.py           ← Usikkerhetsanalyse (500 iter × 3 scenarioer)
│   │   ├── mip_modell.py            ← MILP-modell (PuLP/CBC) for Bolk A
│   │   ├── mip_kapasitet_sensitivitet.py ← Kapasitets-sensitivitet (Bolk B)
│   │   ├── monte_carlo_mip.py       ← Monte Carlo på MIP-tildeling (Bolk D)
│   │   ├── heuristikk_tidbruk_sensitivitet.py  ← Tidbruk-skalering (jobb #1)
│   │   ├── monte_carlo_tidbruk_sensitivitet.py ← Tidbruk-skalering MC (jobb #1)
│   │   ├── monte_carlo_automasjon_sensitivitet.py ← AUTOMASJON_STD-sensitivitet (jobb #2)
│   │   ├── figurer.py               ← Genererer deskriptive figurer (1-6)
│   │   ├── figurer_resultater.py    ← Resultatfigurer fra heuristikk (7-10)
│   │   ├── figurer_usikkerhet.py    ← Usikkerhetsfigurer fra MC (11-13)
│   │   ├── figurer_mip.py           ← MIP-figurer (14-19, 17 reservert)
│   │   ├── sanity_check_data.py     ← Datavask-integritetsjekk (lagt til 2026-04-25)
│   │   ├── sanity_check_mip.py      ← MIP-bibetingelse-sjekk mot tidsplan (lagt til 2026-04-25)
│   │   ├── generer_status.py        ← Genererer STATUS.md fra prosjektplan.json
│   │   └── generer_master_data.py   ← Eldre script (referanse)
│   └── generer_excel_med_faner.py   ← Datainnsamlingsmal
├── 005 report/
│   ├── rapport.md                   ← Rapport (1.0-9.0 utkast ferdig; 1.4-9.6 polert; 10.0/12.0/sammendrag/abstract gjenstår)
│   └── figurer/                     ← PNG-figurer (1-19, 17 droppet)
├── 011 fase 1 - proposal/
│   └── proposal.md                  ← Godkjent proposal
├── 012 fase 2 - plan/
│   ├── prosjektstyringsplan_utfylt.md
│   ├── Gannt.pdf
│   └── prosjektplan.json            ← Single source of truth for prosjektstatus
├── 013 fase 3 - review/
└── 014 fase 4 - report/
```

## Datakilder (rådata)

| Fil | Innhold |
|-----|---------|
| `data.csv` | Fremdriftsstatus per kommune (Ferdig/Påbegynt/Ikke påbegynt). Fra samferdselsavd. PowerBI-rapport |
| `Antall objekter per kommune.csv` | Arbeidsmengde i **antall lenker** (ikke km) per kommune - 355 rader |
| `20250903StatistikkTraktorvegSti.xlsx` | Kommunemapping, km_kurve, beregnet tidsbruk. **MERK:** fylkesnr/fylkesnavn er feil/shufflet og må ignoreres |
| `Datainnsamling_TraktorvegSti.xlsx` | Kapasitet (ukesverk), min/max tidsbruk per kontor, Geovekst-prosjekter per kommune. 10 ark. Kristiansand-arket er tomt. |
| `Agder_prosjekter.csv` | Geovekst LACIAG61, LACIAG63 - supplerer Datainnsamling |
| `Rogaland_prosjekter.csv` | Geovekst LACIRO61, LACIRO62 - supplerer Datainnsamling |
| `kartverket_fylker.geojson` | Norges fylker fra Geonorge (CC BY 4.0), til kart |

## Behandlede data (output)

Produsert av `004 data/scripts/vask_og_strukturer.py`:

| Fil | Innhold |
|-----|---------|
| `master_kommuner.csv` | 357 rader - KomNr, Kommune, Fylke, Kartkontor, Km_Kurve, ArealLand_Km2, Ber_Tidbruk_Min, Ber_Dagsverk, Status, Fremdrift_Prosent, Antall_Lenker, Gjenstaaende_Lenker, Geovekst_Prosjekter, Er_Laast |
| `kapasitet_kontorer.csv` | 10 rader - Kartkontor, Kapasitet_Ukesverk (årlig), Min/Max_Tidsbruk_Timer, Antall_Kommuner, Total_Lenker, Gjenstaaende_Lenker |
| `geovekst_prosjekter.csv` | 173 rader - Prosjektnr, KomNr, Kommune, Kartkontor, Prosjektstatus, Laaseperiode_Start/Slutt |
| `nvdb_overfoering.csv` | 3 scenarioer: Basis_85 (85% auto), Middels_90, Samferdsel_96. Parametre for NVDB-trinnet. |
| `tidbruk_kalibrering.csv` | 58 rader - kartblad-målinger: Kartblad, Minutter, Lengde_M, Min_Per_Km, Min_Per_Km2, Region. Empirisk grunnlag for Ber_Tidbruk_Min-formelen |
| `tidbruk_konstanter.csv` | 2 rader - koeffisientene 0,9035 min/km og 0,6510 min/km² brukt i formelen |

## Viktige avklaringer og LÅSTE beslutninger

### Datadefinisjoner

- **1 ukesverk = 37.5 timer** (bekreftet 2026-04-17)
- **Kapasitet_Ukesverk** = årlig disponibel kapasitet for TVS-prosjektet i 2026. Antas tilsvarende for senere år i modellen.
- **Fylkesnr/fylkesnavn** i StatistikkTVS er feil/shufflet → utledes fra kommunenummer (komm // 100)
- **Arbeidsmengde** = antall lenker (ikke km)
- **Produksjonstakt NVDB:** 300 lenker/person/dag manuelt (samferdselsavdelingens punktestimat, kalibrert 2026-04-20). Monte Carlo sampler Uniform(275, 325) som måleusikkerhet.
- **data.csv "Ferdig"** = kartkontoret er ferdig (IKKE overført til NVDB ennå)
- **Ber_Tidbruk_Min-formel:** `Ber_Tidbruk_Min = Km_Kurve × 0,9035 + ArealLand_Km² × 0,6510`. Koeffisientene er hentet fra fanen `Tidbruk` i StatistikkTVS og bygger på 58 kartbladmålinger. Empirisk spredning i MIN/KM: 0,10–3,44, std 0,55 (~60 % av snitt). Formel verifisert numerisk (maks avvik 0,5 min på alle 357 kommuner).

### Kjente datakilde-inkonsistenser (fanget av sanity_check_data.py 2026-04-25)

- **Nærøysund (5060):** Status=Ferdig men Gjenstaaende_Lenker=Antall_Lenker=7867. Heuristikkens `gjenvaerende_timer = 0 if ferdig_kk else timer` overstyrer dette korrekt; ingen modell-effekt.
- **9 Påbegynt-kommuner med Fremdrift_Prosent=0** (Hå, Nittedal, Modum, Porsgrunn, Notodden, Lillesand, Hitra, Ibestad, Lebesby): rapportert som Påbegynt men Gjenstaaende_Lenker=Antall_Lenker. Modellen behandler dem konservativt som full arbeidsmengde — ingen effekt på resultater.
- **LACIVL03 (Aurland 4641, Årdal 4643):** Rådata Bergen-fane sier «juni 2025 - mars 2006», sannsynlig typo for «mars 2026». Modellen leser Start>Slutt og tolker som ingen lås. **Antas korrekt** fordi prosjektet ville være utløpt før STARTDATO (2026-05-01) uansett. Aurland har gyldig LACHVL39-lås. `vask_og_strukturer.py` har nå advarsel som flagger Start>Slutt slik at fremtidige slike feil oppdages.

### Kapasitet-override (manuell justering)

Oslo-kontorets opprinnelige oppgitte verdier ble vurdert som urealistisk lave. Etter avtale 2026-04-17 er Oslo justert i `vask_og_strukturer.py` via `KAPASITET_OVERRIDE`:
- Kapasitet: 20 → **30 ukesverk**
- Min/Max tidsbruk per kommune: 20-60 → **30-90 timer**

### Kartkontor-mapping (fra fylke)

| Fylke | Kartkontor |
|-------|-----------|
| 03, 31, 32, 33 (Oslo, Østfold, Akershus, Buskerud) | Oslo |
| 34 (Innlandet) | Hamar |
| 39, 40 (Vestfold, Telemark) | Skien |
| 42 (Agder) | Kristiansand |
| 11 (Rogaland) | Stavanger |
| 46 (Vestland) | Bergen |
| 15 (Møre og Romsdal) | Molde |
| 50 (Trøndelag) | Trondheim |
| 18 (Nordland) | Bodø |
| 55, 56 (Troms, Finnmark) | Tromsø |

### Låseperioder (standardisering)

Ulike tekstformater i rådata ("Juni-Desember", "7", "August 2026 - mars 2027"). Standardiseres til datoer. For ukjente brukes **mai-desember 2026** (7 mnd).

### LÅST: Kapasitetskonvensjon — 245 effektive arbeidsdager per år (kartkontor)

Kartkontor-kapasitet er **245 effektive arbeidsdager/år** av 260 mandag-fredag-dager. Folk har ferie spredt utover året (sommervikarer demper, men ikke nok). Konsekvens: daglig/månedlig kapasitet skaleres med faktor 245/260 ≈ 0,9423. Heuristikk: `dag_kap = K × 37,5 × (245/260) / 260`. MIP: `mnd_kap = K × 37,5 × (245/260) / 12`. Total per år = `K × 37,5 × (245/260)` ≈ 0,942 × K × 37,5 timer. Endret 2026-04-24 etter avklaring med oppdragsgiver.

**Historikk:**
- Pre-2026-04-22: dag_kap = K × 37,5 / 230, simulering 260 dager → 13 % overbruk (skjult, jf. review_modellering.md funn 2.1)
- 2026-04-22 (260-fiks): dag_kap = K × 37,5 / 260, simulering 260 dager → 0 % overbruk, men brukte feil arbeidsdagstall
- 2026-04-24 (245-fiks): dag_kap = K × 37,5 × (245/260) / 260, simulering 260 dager → reflekterer faktiske 245 produktive dager

**NVDB-konvensjon uendret:** NVDB-throughput konverteres fortsatt med 260/12 = 21,67 dg/mnd i MIP. Samferdselsavdelingen opererer selv med 240 dg/år i sitt eget regnestykke; det dokumenterte 240/260-gapet (samferdsel 7,22 år vs modell 6,72 år for Middels_90) er beholdt som drøftelsespoeng i 5.1.2.

**Effekt av 245-fiksen:** makespan uendret i alle 3 NVDB-scenarioer (NVDB dominerer flaskehalsen). Faktisk MC-utslag på kartkontor-tid +1,4 % (P50 503 → 510 dager). Matematisk minimumsgrense Min_Kartkontor_Mnd +5,9 % (6,8 → 7,2 mnd), men låseperioder absorberer mye av kapasitetskuttet, så reelt simuleringsutslag er mindre. Heuristikk siste-ferdig forskjøvet 3 dager (2027-09-13 → 2027-09-16). MC-percentiler for total varighet praktisk talt uendret pga NVDB-dominans. MIP- og MC-tall er gjenkjørt 2026-04-24.

### LÅST: Hovedmetode er hybrid heuristikk + MIP

Besluttet 2026-04-16:
- **Steg 1:** Regelbasert heuristikk gir baseline (sorter etter størrelse, respekter låseperioder)
- **Steg 2:** MIP-modell i PuLP forbedrer baseline
- **Sammenligning:** brukes som diskusjonspoeng i rapporten
- **ML/regresjon droppet** (62 ferdige kommuner er for lite treningsgrunnlag)

### LÅST: To-stegs modell inkluderer NVDB

Både kartkontor-allokering og NVDB-overføring modelleres. NVDB er sannsynlig flaskehals (150 lenker/dag manuelt ved 85 % auto, kalibrert 2026-04-20).

### LÅST: Monte Carlo-usikkerhetsanalyse

Implementert 2026-04-18 i `monte_carlo.py`, kalibrert 2026-04-20. Tre stokastiske kilder per iterasjon:

1. **MIN/KM per kommune:** bootstrap fra empirisk fordeling (58 kartblader, range 0,10–3,44)
2. **Produksjonstakt_Manuell:** Uniform(275, 325) lenker/person/dag – sentrert på samferdselsavdelingens punktestimat 300
3. **Automasjonsgrad_FME:** Normal(scenariopunkt, 0,03), klippet til [0,5; 0,99]. Std 0,03 reflekterer realistisk måleusikkerhet på FME-automasjon

500 iterasjoner per scenario. Resultater (varighet i år, P5/P50/P95, post-260-fiks 2026-04-23):
- Basis_85: 6,46 / 10,01 / 13,28
- Middels_90: 3,25 / 6,67 / 9,91
- Samferdsel_96: 1,38 / 2,36 / 5,88

**Nøkkelfunn (revidert):** scenarioene overlapper nå realistisk — P95 Samferdsel_96 (5,88 år) er over P5 Middels_90 (3,25 år). Den tidligere "ingen overlapp"-konklusjonen (AUTOMASJON_STD=0,01) var et designvalg, ikke et empirisk funn. Automasjonsgrad er fortsatt dominerende usikkerhetskilde. Kartkontor-varighet stabilt ~510 dager (P5-P95: 495-532) etter 245-fiksen. P95 Basis_85 økte fra 11,98 til 13,28 år ifm. 260-fiksen — halen er mer følsom for kapasitet uten 260/230-overbruket.

### LÅST: NVDB-scenarioanalyse på automasjonsgrad

Kalibrert 2026-04-20 mot samferdselsavdelingens eksplisitte regnestykke (300 lenker/dag, 240 arbeidsdager/år). Tre scenarioer i `nvdb_overfoering.csv`:

| Scenario | Automasjon | Manuell takt | Manuell kap./dag | Total/dag | Estimert |
|----------|-----------|--------------|------------------|-----------|----------|
| Basis_85 | 85 % | 300 | 150 | 1 000 | ~10 år |
| Middels_90 | 90 % | 300 | 150 | 1 500 | ~6,7 år (prosjekt 260 d) / 7,22 år (samf.avd. 240 d) |
| Samferdsel_96 | 96 % | 300 | 150 | 3 750 | ~2,7 år (optimistisk øvre grense) |

Bemanning (0,5 årsverk) og manuell produksjonstakt (300 lenker/dag) holdes konstant. NVDB-startdato: 2026-05-01.

**Merknad om Samferdsel_96:** Samferdselsavdelingen opererer selv med 80–90 % automasjon. Scenarioet er en optimistisk øvre grense bakoverregnet mot et 2-års-mål, ikke et eksplisitt anslag fra avdelingen. Middels_90 er samferdselsavdelingens eksplisitte regnestykke, oversatt til prosjektets 260-dagers kalenderkonvensjon.

### LÅST: Valideringsstrategi

- Ingen train/test-split – alle 357 kommuner brukes til å definere problemet
- Validering skjer via **scenarioanalyse** (NVDB-automasjon, eventuell kapasitetsvariasjon)
- Sanity-sjekk: bruk de 62 ferdige kommunene til å validere at `Ber_Tidbruk_Min`-estimater er realistiske

## Viktige nøkkeltall

- **357** kommuner
- **10** kartkontor, kapasitet 22-52 ukesverk/år (Trondheim størst, Bodø minst)
- **Total årlig kapasitet:** 327 ukesverk = 12 262 t/år
- **2 630 964** lenker totalt
- **2 138 104** lenker gjenstår
- **152** kommuner låst av Geovekst-prosjekter
- **173** kommune-prosjekt-par i geovekst

## MIP-modell (mip_modell.py)

Implementert 2026-04-19. Time-indeksert MILP med månedlig granularitet. Beslutningsvariabler:
- `y_ij ∈ {0,1}`: kommune i tildeles kontor j
- `w_ijt ≥ 0`: timer brukt på (i, j) i måned t
- `z_it ∈ {0,1}`: kommune i er ferdig på kartkontor innen måned t
- `D_t ≥ 0`: lenker overført til NVDB i måned t (aggregert)
- `Q_t ∈ {0,1}`: 1 hvis ikke alt NVDB overført innen måned t

Horisonter (etter kalibrering 2026-04-20, Samferdsel_96 utvidet 2026-04-23 etter 260-fiks): Basis_85 T=144, Middels_90 T=96, Samferdsel_96 T=54. Tidsoppløsning: kalendermåneder (21,67 arbeidsdager/måned som følger av 260 kalenderarbeidsdager/år).

### Tre modi (via `--mode`)

- **makespan**: min sum Q_t alene. CBC stopper ofte prematurt uten å bevise optimalitet.
- **lex**: sekvensiell lex-opt. Runde 1 min makespan, runde 2 min sum_i timer_i × (1 - z_it) gitt makespan-constraint. Robust men langsom (2 solver-runder).
- **vektet** (default): én-pass obj = W1 × makespan + W2 × kartkontor-ferdig + inertia. W1 ≈ 10¹⁰, W2 ≈ 10³. Raskest og mest stabil; CBC løser grundig.

### Resultater (vektet-modus, post-245-fiks 2026-04-24)

| Scenario | Heuristikk | MIP | Diff | Omfordelinger | Status | Solver-tid |
|----------|-----------|-----|------|---------------|--------|------------|
| Basis_85 | 10,08 år | 10,17 år | −0,9 % | 27 / 295 | Not Solved | 2 293 s |
| Middels_90 | 6,72 år | 6,75 år | −0,4 % | 36 / 295 | Optimal | 989 s |
| Samferdsel_96 | 2,69 år | 2,75 år | −2,2 % | 71 / 295 | Optimal | 609 s |

**Hovedfunn**: MIP bekrefter at heuristikkens ansvarskontor-tildeling er nær optimal for makespan. <2,2 % forskjell skyldes månedlig vs. daglig tidsoppløsning. Omfordelingene er ikke nødvendige for makespan — NVDB er konsistent flaskehals og kartkontor-delen er ferdig innen 10-11 måneder (MIP) eller ~16,5 måneder (heuristikk) i alle scenarioer.

**Post-245-fiks:** makespan uendret i alle 3 scenarioer (NVDB dominerer). Min_Kartkontor_Mnd matematisk grense: 6,8 → 7,2 mnd (~6 % økning fra 245/260-faktor). Kartkontor-ferdig-måned i MIP uendret (10/10/11 mnd, median 4 mnd). Omfordelingsmønsteret endret: Basis 97→27, Middels 76→36, Samferdsel 54→71 — dette er ikke et systematisk skift men reflekterer at vektet objektiv har flere nær-optimale assignmenter, og CBC kan finne ulike incumbenter. Basis_85 er nå Not Solved ved 1800s timeout (var Optimal pre-245); løsningen er IP-feasible men ikke bevist optimal — 2 kommuner (3305 Ringerike, 5610 Kárášjohka-Karasjok) endte med fraksjonelle y-verdier (ingen y > 0,5) og er telt som ikke-omfordelt (faller tilbake til ansvarlig kartkontor).

### Solver-valg: CBC (gratis, innebygd i PuLP)

HiGHS (nyere, raskere) ble testet men pulp-integrasjonen var ikke stabil via `highspy`. CBC løser Middels_90 og Samferdsel_96 optimalt innen 10-16 min med MIP_GAP=0,001; Basis_85 ender som Not Solved ved 30-min timeout.

CBC-særegenhet: enkelte kjøringer stopper tidlig med status "Optimal" før B&B er fullført. Vektet-modus med inertia-tie-breaker omgår dette.

**MIP_GAP**: relativ gap-toleranse er strammet fra 0,05 (5 %) til 0,001 (0,1 %) per 2026-04-26 etter sanity_check_mip.py-funn. Strammere gap garanterer at z_it-rapportering matcher faktisk ferdig-måned i alle praktiske tilfeller. Restanomali: Sykkylven (1528) i Samferdsel_96 har Ferdigdato_Kartkontor_Mnd=1 (juni, låst) selv om alt arbeid skjer i mnd 0 (mai) — gjelder kun denne ene kommunen og er en kosmetisk rapporterings-effekt, ikke faktisk skedulering-feil.

### Bolk B: Kapasitets-sensitivitetsanalyse (mip_kapasitet_sensitivitet.py)

6 varianter × 3 NVDB-scenarioer = 18 MIP-kjøringer:
- S0_Baseline: nominell kapasitet
- S1_Trondheim50: Trondheim -50 % (krise)
- S2_Alle_pluss20: alle kontor +20 % (rekruttering)
- S3_Omfordeling: små +50 %, store -20 %
- S4_Alle_minus15: alle kontor -15 % (sparekrav)
- S5_Alle_minus50: alle kontor -50 % (ekstrem, for å vise kartkontor-bundet regime)

**Hovedfunn (post-245-fiks 2026-04-24, post-rerun 2026-04-26 med MIP_GAP=0,001):** makespan er **identisk på tvers av alle 6 kapasitetsvarianter** per NVDB-scenario (Basis_85 10,17 / Middels_90 6,75 / Samferdsel_96 2,75 år). NVDB er dominerende flaskehals i hele det testede kapasitetsområdet. Kartkontor-ferdigmåned holder seg på 10-11 mnd i S0-S4 og 14 mnd i S5_Alle_minus50 (matematisk minimum 14,4 mnd).

**Solver-status:** 9 av 18 kjøringer løser Optimal (S0 Middels/Samferdsel; S1 Middels; S2 alle tre; S3 Middels/Samferdsel; S4 Basis_85). 9/18 er Not Solved ved timeout 30 min — lavere kapasitet og strammere MIP_GAP=0,001 gjør problemet vanskeligere for CBC, men makespan-tallene er robuste (big-M-gated via Q_t). Omfordelings- og kartkontor-ferdigtall for Not Solved-kjøringene er IP-feasible incumbenter, men ikke bevist optimale.

**Phantom-omfordelings-fix (2026-04-26):** lagre_tidsplan og n_reassigned i mip_modell.py og mip_kapasitet_sensitivitet.py er fikset til å falle tilbake til ansvarlig kartkontor for kommuner uten klar y-tildeling (Not Solved-fraksjonelle). Dette korrigerte phantom-omfordelinger på 2-8 i 8 av 18 sensitivitet-varianter. Effekt på rapporterte tall: S0 Basis 29→27, S1 Basis 31→28, S1 Samferdsel 31→28, S4 Middels 33→31, S4 Samferdsel 33→31, S5 Basis 20→17, S5 Middels 20→15, S5 Samferdsel 20→12. Makespan uendret i alle.

**S5_Alle_minus50:** rapporterer Kartkontor_Siste_Mnd=14 mot matematisk minimum 14,4 mnd — plausibel IP-feasible løsning, men status Not Solved. Bør dokumenteres som "nær-optimal ved timeout", ikke som gyldig bevist løsning. Etter rerun med phantom-fix: Kommuner_Omfordelt 17/15/12 i Basis/Middels/Samferdsel (nedjustert fra 20 i alle).

### Bolk D: Monte Carlo på MIP-plan (monte_carlo_mip.py)

Bruker eksisterende `monte_carlo.py`-motor med MIP-assignment fra `tidsplan_mip_vektet_<scenario>.csv` som fast tildeling. 500 iterasjoner × 3 scenarioer med samme 3 stokastiske kilder som heuristikk-MC.

**Funn (2026-04-23, post-260-fiks; tall oppdatert post-245-fiks 2026-04-24):** for Basis_85 gir MIP-basert MC og heuristikk-MC **identiske** percentiler (6,46 / 10,01 / 13,28) — tidligere gap (P95 13,28 MIP vs 11,98 heur) var et artefakt av 260/230-overbruket. For Middels_90 er alle tre percentiler identiske (3,25 / 6,67 / 9,91). For Samferdsel_96 er P5 marginalt bedre i MIP (1,10 vs 1,38) mens P50/P95 er like. Etter fiksen er det derfor ikke lenger grunnlag for "deterministisk optimum ≠ robust optimum"-funnet på makespan-nivå. MIP-planen gir fortsatt markant kortere kartkontor-tid i MC (P50: 452 dager vs 510 for Basis_85), men denne forskjellen er skjult av NVDB-flaskehalsen i total varighet.

### Bolk E: Tidbruk-skaleringssensitivitet (heuristikk_tidbruk_sensitivitet.py + monte_carlo_tidbruk_sensitivitet.py)

Modell-evalueringsjobb #1 (2026-04-23). Skaler `Ber_Tidbruk_Min` med faktor 1,5 og 2,0 for å teste om hovedbudskapet "NVDB er flaskehalsen" overlever at tidbruk-formelen underestimerer (jf. validering_tidbruk_formel.md V2/V3: 8/10 kontor har median formel-estimat under sitt eget bånd; ferdige kommuner ~halvparten så tunge per stk som de gjenstående). 6 heuristikk-kjøringer + 6 MC-kjøringer (500 iter hver, 3000 iter totalt).

**Hovedfunn:** NVDB-makespan **uendret** for Basis_85 og Middels_90 i alle tre kjøringer (heuristikk: 10,08/6,72/2,69 år. MC P50: 10,01/6,67 år for Basis_85 og Middels_90 også ved skala 2,0). Kartkontor-fasen vokser proporsjonalt med skala (MC P50: 16,8 → 21,1 → 28,2 mnd), men forblir mindre enn NVDB-tiden i alle scenarioer med flaskehals > 6 år.

**Eneste merkbare effekt:** Samferdsel_96 (raskest NVDB) får P5 presset opp fra 1,38 → 1,65 → 2,15 år ved skala 2 fordi kartkontor-tiden begynner å bestemme ferdigdatoen i de raskeste iterasjonene. P50 og P95 forblir uendret.

**Konklusjon:** Hovedbudskapet "NVDB-flaskehalsen dominerer" overlever en dobling av tidbruk-formelen for de to mest realistiske scenarioene. MIP er ikke kjørt med skalert tidbruk; uniform skalering bevarer relativ rangering, så omfordelingsstrategien antas kvalitativt uendret.

### Bolk F: AUTOMASJON_STD-sensitivitet (monte_carlo_automasjon_sensitivitet.py)

Modell-evalueringsjobb #2 (2026-04-23). Kjør Monte Carlo med std ∈ {0,01; 0,02; 0,03; 0,05} for alle 3 scenarioer = 12 kjøringer × 500 iter = 6000 iter totalt. Adresserer review-funn 3.1: "0,03-standardavviket er et designvalg som bestemmer om scenariofordelingene overlapper".

**Hovedfunn:** Median (P50) er praktisk talt uendret på tvers av std-verdier (Basis_85: 10,01–10,10; Middels_90: 6,65–6,72; Samferdsel_96: 2,66–2,70). Kun haleformen påvirkes:

| Std | Basis_85 P5-P95 (år) | Middels_90 P5-P95 (år) | Samferdsel_96 P5-P95 (år) |
|-----|------------------------|---------------------------|------------------------------|
| 0,01 | 8,75–11,39 | 5,45–7,87 | 1,51–3,75 |
| 0,02 | 7,60–12,29 | 4,31–8,85 | 1,37–4,81 |
| 0,03 | 6,46–13,28 | 3,20–9,93 | 1,38–5,86 |
| 0,05 | 4,22–15,38 | 1,41–12,03 | 1,37–8,06 |

**Scenario-overlapping (P5-P95-bånd):**
- std = 0,01: ingen overlapp (Middels_90 P95 = 7,87 < Basis_85 P5 = 8,75; Samferdsel_96 P95 = 3,75 < Middels_90 P5 = 5,45)
- std ≥ 0,02: overlapp begynner
- std = 0,03: betydelig overlapp (valgt verdi)
- std = 0,05: overlapp så stor at P95 Samferdsel_96 = 8,06 år, urealistisk

**Konklusjon:** 0,03 ligger som rimelig kompromiss mellom urealistisk skarpt (0,01) og urealistisk vidt (0,05). Rapport 9.4 fikk eget avsnitt med tabell og rettferdiggjøring.

## Pågående arbeid

Se `STATUS.md` for detaljert fremdrift. Nåværende fokus (per 2026-04-24, fase 3 er 90 % ferdig):

1. ✅ Datavask fullført (6 processed CSV-filer inkl. tidbruk-kalibrering)
2. ✅ Metodevalg låst (hybrid heuristikk + MIP + Monte Carlo)
3. ✅ NVDB-scenarioer kalibrert mot samferdselsavdelingens tall (2026-04-20)
4. ✅ 18 figurer produsert (6 deskriptive + 4 resultat + 3 usikkerhet + 5 MIP)
5. ✅ Heuristikk-implementering (`heuristikk.py`) kjørt for alle 3 scenarioer
6. ✅ Monte Carlo-analyse (heur + MIP) – 500 iterasjoner med 3 stokastiske kilder, utvidet usikkerhet
7. ✅ MIP-modell (vektet) – alle 3 scenarioer kjørt etter 245-fiks (Basis_85 Not Solved ved timeout, Middels/Samferdsel Optimal)
8. ✅ Kapasitets-sensitivitet – 6 varianter × 3 NVDB-scenarioer = 18 MIP-kjøringer
9. ✅ Rapport-seksjon 2.0 Litteratur, 4.0 Casebeskrivelse, 5.2 Data, 6.0 Modellering, 7.0 Analyse, 8.0 Resultat, 11.0 Bibliografi
10. ✅ Uavhengig review av modellering + tidbruk-formel (2026-04-22) — to notat i `013 fase 3 - review/`
11. ✅ 260-fiks etter review 2.1 — alle modeller og MC rekjørt, 18 figurer regenerert, arkiv i `arkiv_pre_230_fiks/`
12. ✅ Rapport-seksjon 5.1 Metode + 9.0 Diskusjon utkast ferdig (2026-04-23) — alle ni review-funn innarbeidet
13. ✅ Helhetsgjennomlesing av 5.0+9.0 (2026-04-23) — interne arbeidsreferanser fjernet, numerisk feil i 5.1.4 fikset
14. ✅ **Modell-jobb #1 ferdig (2026-04-23): tidbruk-skaleringssensitivitet** — gjenoppfrisket etter 245-fiks 2026-04-24
15. ✅ **Modell-jobb #2 ferdig (2026-04-23): AUTOMASJON_STD-sensitivitet** — gjenoppfrisket etter 245-fiks 2026-04-24
16. ✅ **245-fiks etter avklaring med oppdragsgiver (2026-04-24)** — Kartkontor 260 → 245 effektive arbeidsdager (faktor 245/260). Alle modeller rekjørt, 53 CSV arkivert i `arkiv_pre_245_fiks/`. NVDB-makespan uendret. Kartkontor-tid +6 %.
17. 🔄 **Rapport-skriving før 29.04:** 1.0 Innledning, 10.0 Konklusjon-skisse, sammendrag/abstract
18. ⏳ Peer review (27-28. apr)
19. ⏳ Fase 4: seksjonene 1 (ferdigstille), 3, 10 (ferdigstille) + kvalitetssikring

### TODO etter peer review-fristen 29.04

- **Døp om CSV-kolonnen `Hjemmekontor` til `Ansvarlig_Kartkontor`** i alle MIP-scripts (`mip_modell.py`, `mip_kapasitet_sensitivitet.py`, `monte_carlo_mip.py`, `analyser_rekkefolge.py`, `figurer_mip.py`). Krever rerun av MIP-modell (~16-65 min) + kapasitets-sensitivitet (~17 t bakgrunn) + monte_carlo_mip. Utsatt fra 2026-04-26 pga. peer review-frist; rapport.md, figur 16 og kommentarer er allerede oppdatert. Aktive CSV-er har fortsatt `Hjemmekontor` som kolonnenavn — internt, ikke synlig i sluttproduktet.

### Viktige milepæler

- **29.04.2026** - Godkjent hovedutkast (11 dager unna per 2026-04-18)
- **01.06.2026** - Innlevert rapport

### Strategiske beslutninger (2026-04-18)

- **MIP-strategi:** start nå med dagens scenarioparametere (alternativ B). Samferdselsavdelingens svar kan rekjøres som sensitivitetsanalyse hvis de kommer.
- **Rapportarbeid:** seksjon-for-seksjon-dialog; Claude skriver utkast, bruker reviderer.
- **Litteratur:** 5 kjerne-referanser lagt inn i 2.0 Litteratur og 11.0 Bibliografi. Full litteraturgjennomgang og 3.0 Teori utsettes til fase 4. Bibliografi må verifiseres mot HiM-bibliotek/Oria (se TODO).

### Oppsummering av økt 2026-04-25/26 (uavhengig review + phantom-fix)

- **Reviewer-rapport av 245-fiksen** identifiserte 7 punkter; alle er rettet (rapport 1.4-konsistens, 1,36→1,38, 8.3 Optimal-status, +6%/30 dager-overestimat, S5 13/13,6→14/14,4, MIP-MC tellingsfeil).
- **Sanity-check-skript** lagt til i `004 data/scripts/`:
  - `sanity_check_data.py` — datavask-konsistens (Status vs Gjenstaaende, Geovekst, fylke-mapping)
  - `sanity_check_mip.py` — MIP-bibetingelser sjekkes mot tidsplan-CSV
- **Funn av latent bug** i `lagre_tidsplan` og `n_reassigned`: kommuner uten klar y-tildeling (fraksjonelle ved Not Solved) ble feilaktig telt som omfordelt. Fikset i mip_modell.py og mip_kapasitet_sensitivitet.py.
- **MIP_GAP strammet** fra 0,05 til 0,001 etter Sykkylven-anomali-funn.
- **Rerun**:
  - mip_kapasitet_sensitivitet.py (~17 t bakgrunn) — phantom-fix korrigerte 8 av 18 sensitivitet-varianter (eksakt 2-8 reduksjon hver, alle Not Solved). Makespan uendret i alle.
  - mip_modell.py for alle 3 scenarioer (~65 min) — Basis_85 Not Solved ved 38 min, Middels Optimal ved 16 min, Samferdsel Optimal ved 10 min. Makespan/omfordelinger uendret.
  - monte_carlo_mip.py — uendret tall (basis-tidsplan endret seg ikke vesentlig).
- **Datavask-typo flagget**: LACIVL03 (Aurland 4641, Årdal 4643) har "juni 2025 - mars 2006" — sannsynligvis "mars 2026". Modellen er korrekt for begge fordi låsen ville være utløpt før STARTDATO uansett. `vask_og_strukturer.py` har nå advarsel for Start>Slutt.
- **Rapport-figur konsistens**: 7 manglende figurer (7-13) lagt til på passende plasser i rapport.md. Alle 18 PNG-er nå referert.
- **Bibliografi**: Graham (1969) "multiprocessing"-typo rettet til "multiprocessor".
- **Rapport-tall korrigert**: 1,36→1,38 Samferdsel P5; 30%→54% Pareto; 0,91→0,9035 MIN/KM-snitt; "1,8-4,4×"→"2,0-4,3×" varians-faktorer; m.m.

### Oppsummering av økt 2026-04-24 (245-fiks)

- Oppdragsgiver avklarte at faktiske produktive arbeidsdager er ca 245/år (ikke 260 som modellen brukte). Sommervikarer kompenserer noe for sommerferie, men ikke fullt ut. NVDB beholder samferdselsavd's egen 240-dagers konvensjon (uendret).
- **Kapasitetsfaktor 245/260 ≈ 0,9423** lagt inn i heuristikk.py og mip_modell.py. Daglig/månedlig kartkontor-kapasitet skaleres ned med ~5,8 %. Faktisk simuleringsutslag på kartkontor-tid er mindre enn nominell kapasitetsreduksjon fordi låseperioder absorberer mye av kuttet.
- **Makespan uendret** i alle 3 NVDB-scenarioer (NVDB dominerer): heuristikk 10,08 / 6,72 / 2,69 år, MIP 10,17 / 6,75 / 2,75 år (identiske med pre-245).
- **MC P5/P50/P95 totalvarighet praktisk talt identiske** med pre-245 (NVDB dominerer): Basis 6,46/10,01/13,28; Middels 3,25/6,67/9,91; Samferdsel 1,38/2,36/5,88 år.
- **Kartkontor-MC P50 økte:** 503 → 510 dager (+1,4 %). Matematisk minimumsgrense Min_Kartkontor_Mnd 6,8 → 7,2 mnd (+5,9 %). Heuristikk siste-ferdig 2027-09-13 → 2027-09-16 (~3 dager senere).
- **MIP solver-kompleksitet økte:** Basis_85 nå Not Solved ved 1800s timeout (var Optimal pre-245 ved 711s). Middels og Samferdsel fortsatt Optimal.
- **MIP-omfordelinger endret:** Basis 97→27, Middels 76→36, Samferdsel 54→71. Ikke et systematisk skift; vektet objektiv har flere nær-optimale incumbenter ved lavere kapasitet. Basis_85 har 2 kommuner med fraksjonelle y-verdier ved Not Solved-timeout (3305 Ringerike, 5610 Kárášjohka-Karasjok); disse telles som ikke-omfordelt (faller tilbake til ansvarlig kartkontor) for konsistens med Monte Carlo-tolkningen.
- 53 CSV arkivert i `arkiv_pre_245_fiks/` for diff-sammenligning.

### Oppsummering av økt 2026-04-23

- Review av modellering (`013 fase 3 - review/review_modellering.md`) og tidbruk-formel (`validering_tidbruk_formel.md`) gjennomgått. Begge dokumenterer forbehold for seksjon 9 Diskusjon.
- Alvorligste funn (review 2.1) var skjult 13 %-overbruk pga 260 simuleringsdager / 230 i kapasitetsnevner. **Fikset:** `ARBEIDSDAGER_PER_AAR=230→260` i heuristikk.py og forenklet faktor i mip_modell.py. (Erstattet av 245-fiks 2026-04-24.)
- Alle modeller rekjørt med nye tall. 18 CSV arkivert i `arkiv_pre_230_fiks/` for diff-sammenligning.
- Figurer 7-19 regenerert. T_MAX Samferdsel_96 utvidet 48→54 for ekstra buffer.

### Oppsummering av økt 2026-04-18

- Rapport korrigert: fylke-til-kontor-tildeling framstår nå som baseline (ikke forenkling); omfordeling er beslutningsvariabel
- Tidbruk-fanen i StatistikkTVS integrert: formelen `Ber_Tidbruk_Min = Km_Kurve × 0,9035 + ArealLand × 0,6510` dokumentert og verifisert (maks avvik 0,5 min)
- Monte Carlo-modul implementert med 3 stokastiske kilder: MIN/KM per kommune (bootstrap fra 58 kartbladmålinger), Produksjonstakt_Manuell (Uniform 300-400), Automasjonsgrad (Normal rundt scenariopunkt, std 0,01)
- Nøkkelfunn: scenarioene overlapper ikke. P95 Samferdsel (3,22 år) < P5 Middels (4,54 år). Automasjonsgrad er dominerende usikkerhetskilde
- 3 usikkerhetsfigurer + 4-ukers glatting på diskrete kommune-kurver
- Rapport: 2.0 Litteratur med fem referanser og 11.0 Bibliografi i APA-format

## Kommunikasjonsstil

- Brukeren foretrekker **norsk** (bokmål)
- Konsise svar, ikke overflødig forklaring
- Bruker AskUserQuestion aktivt når noe er uklart
- Plan-modus brukes for større endringer

## Tekniske detaljer

- **OS:** Windows 11, bruker bash-shell
- **Python:** 3.13 (Microsoft Store-versjon)
- **Python-avhengigheter:** pandas, numpy, openpyxl, python-docx, matplotlib, geopandas
- **Encoding-notat:** Windows cp1252 → UTF-8 må fikses i Python-scripts med `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`

## Referansefiler å lese ved oppstart

For rask kontekst-gjenoppretting:
1. `STATUS.md` - Hvor er vi akkurat nå? (auto-generert fra JSON)
2. `012 fase 2 - plan/prosjektplan.json` - **Single source of truth** for prosjektstatus
3. `004 data/processed_data/master_kommuner.csv` - Hoveddatasett (inkl. ArealLand_Km2)
4. `004 data/processed_data/nvdb_overfoering.csv` - NVDB-scenarioer
5. `004 data/processed_data/tidbruk_konstanter.csv` - Koeffisientene 0,9035 og 0,6510
6. `004 data/processed_data/monte_carlo_summary.csv` - Usikkerhetsresultater P5/P50/P95
7. `004 data/processed_data/oppsummering_scenarioer.csv` - Heuristikk-resultater
8. `004 data/processed_data/oppsummering_mip_vektet.csv` - MIP-resultater per scenario
9. `004 data/processed_data/sammenligning_heuristikk_mip_vektet.csv` - heuristikk vs MIP
10. `004 data/processed_data/oppsummering_sensitivitet.csv` - kapasitets-sensitivitet (6 varianter × 3 scenarioer)
11. `004 data/scripts/vask_og_strukturer.py` - Datavask-logikk (inkluderer Tidbruk-fanen)
12. `004 data/scripts/heuristikk.py` - Simuleringsmotor
13. `004 data/scripts/monte_carlo.py` - Usikkerhetsanalyse (heuristikk)
14. `004 data/scripts/mip_modell.py` - MILP-modell (PuLP/CBC), tre modi (makespan/lex/vektet)
15. `004 data/scripts/mip_kapasitet_sensitivitet.py` - Kapasitets-sensitivitet (Bolk B)
16. `004 data/scripts/monte_carlo_mip.py` - Monte Carlo på MIP-assignment
17. `004 data/scripts/figurer_mip.py` - MIP-figurer (14-19)
18. `005 report/rapport.md` - Aktuell rapport (seksjon 2.0, 4.0, 5.2, 6.0, 7.0, 8.0, 11.0 har innhold; 5.1, 9.0 neste)

## Workflow for statusoppdatering

1. Endre status/fremdrift/kommentarer i `012 fase 2 - plan/prosjektplan.json`
2. Kjør: `python "004 data/scripts/generer_status.py"`
3. STATUS.md regenereres automatisk

**Aldri rediger STATUS.md direkte** - endringer går tapt ved neste regenerering.

## Figurer (i 005 report/figurer/)

### Deskriptive figurer (fig 1-6)

| Nr | Fil | Innhold |
|----|-----|---------|
| 1 | `01_kart_kontorer.png` | Norgeskart med fylker fargelagt etter kontor |
| 2 | `02_kapasitet_vs_arbeid.png` | Søyle: kapasitet vs arbeidsmengde + estimert varighet per kontor |
| 3 | `03_status_per_kontor.png` | Stacked bar: fremdriftsstatus per kontor |
| 4 | `04_lastfordeling.png` | Horisontal søyle per kontor, segmenter = kommuner etter størrelseskategori |
| 5 | `05_geovekst_heatmap.png` | Heatmap: antall låste kommuner per måned og kontor |
| 6 | `06_lenker_histogram.png` | Histogram + Pareto-kurve for arbeidskonsentrasjon |

Regenereres med: `python "004 data/scripts/figurer.py"`

### Resultatfigurer fra heuristikk (fig 7-10)

| Nr | Fil | Innhold |
|----|-----|---------|
| 7 | `07_nvdb_ko.png` | NVDB-kølengde over tid (lenker + kommuner), alle 3 scenarioer |
| 8 | `08_kumulativ_nvdb.png` | Kumulativ NVDB-overføring (lenker + kommuner), alle 3 scenarioer |
| 9 | `09_utnyttelse_heatmap.png` | Kapasitetsutnyttelse per kontor og uke (baseline) |
| 10 | `10_kontor_fremdrift.png` | Kumulativ ferdigstilling per kontor (baseline) |

Regenereres med: `python "004 data/scripts/figurer_resultater.py"`

### Usikkerhetsfigurer fra Monte Carlo (fig 11-13)

| Nr | Fil | Innhold |
|----|-----|---------|
| 11 | `11_fanchart_nvdb.png` | Kumulativ NVDB-overføring med P5-P95 usikkerhetsbånd per scenario |
| 12 | `12_histogram_varighet.png` | Fordeling av totalvarighet per scenario (3 panel) |
| 13 | `13_per_kontor_boxplot.png` | Per-kontor spredning i NVDB-ferdigdato per kommune (Middels_90) |

Regenereres med: `python "004 data/scripts/figurer_usikkerhet.py"`

### MIP-figurer (fig 14-19)

| Nr | Fil | Innhold |
|----|-----|---------|
| 14 | `14_heuristikk_vs_mip.png` | Søyle: total varighet heuristikk vs MIP per scenario |
| 15 | `15_kartkontor_ferdig.png` | Histogram: fordeling av kartkontor-ferdigmåned, heur vs MIP, 3 paneler |
| 16 | `16_omfordeling_matrise.png` | Heatmap: ansvarlig kartkontor → MIP-kontor (Middels_90) |
| 17 | *reservert for fan chart MIP (droppet — MC er identisk med heuristikk-MC)* |
| 18 | `18_kapasitet_sensitivitet.png` | Søyle: makespan per kapasitetsvariant × scenario |
| 19 | `19_omfordeling_varianter.png` | Søyle: antall omfordelinger per variant × scenario |

Regenereres med: `python "004 data/scripts/figurer_mip.py"`
