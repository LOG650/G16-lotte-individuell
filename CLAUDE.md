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
│   │   └── monte_carlo_*.csv              (summary, varigheter, per_kommune, ko_percentiles)
│   ├── scripts/
│   │   ├── vask_og_strukturer.py    ← Hovedscript for datavask
│   │   ├── heuristikk.py            ← Regelbasert baseline-simulering
│   │   ├── monte_carlo.py           ← Usikkerhetsanalyse (500 iter × 3 scenarioer)
│   │   ├── figurer.py               ← Genererer deskriptive figurer (1-6)
│   │   ├── figurer_resultater.py    ← Resultatfigurer fra heuristikk (7-10)
│   │   ├── generer_status.py        ← Genererer STATUS.md fra prosjektplan.json
│   │   └── generer_master_data.py   ← Eldre script (referanse)
│   └── generer_excel_med_faner.py   ← Datainnsamlingsmal
├── 005 report/
│   ├── rapport.md                   ← Rapport (seksjon 4 og 5.2 utkast ferdig)
│   └── figurer/                     ← PNG-figurer (1-10)
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
- **Produksjonstakt NVDB:** 300-400 lenker/person/dag manuelt
- **data.csv "Ferdig"** = kartkontoret er ferdig (IKKE overført til NVDB ennå)
- **Ber_Tidbruk_Min-formel:** `Ber_Tidbruk_Min = Km_Kurve × 0,9035 + ArealLand_Km² × 0,6510`. Koeffisientene er hentet fra fanen `Tidbruk` i StatistikkTVS og bygger på 58 kartbladmålinger. Empirisk spredning i MIN/KM: 0,10–3,44, std 0,55 (~60 % av snitt). Formel verifisert numerisk (maks avvik 0,5 min på alle 357 kommuner).

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

### LÅST: Hovedmetode er hybrid heuristikk + MIP

Besluttet 2026-04-16:
- **Steg 1:** Regelbasert heuristikk gir baseline (sorter etter størrelse, respekter låseperioder)
- **Steg 2:** MIP-modell i PuLP forbedrer baseline
- **Sammenligning:** brukes som diskusjonspoeng i rapporten
- **ML/regresjon droppet** (62 ferdige kommuner er for lite treningsgrunnlag)

### LÅST: To-stegs modell inkluderer NVDB

Både kartkontor-allokering og NVDB-overføring modelleres. NVDB er sannsynlig flaskehals (175 lenker/dag manuelt ved 85% auto).

### LÅST: Monte Carlo-usikkerhetsanalyse

Implementert 2026-04-18 i `monte_carlo.py`. Tre stokastiske kilder per iterasjon:

1. **MIN/KM per kommune:** bootstrap fra empirisk fordeling (58 kartblader, range 0,10–3,44)
2. **Produksjonstakt_Manuell:** Uniform(300, 400) lenker/person/dag
3. **Automasjonsgrad_FME:** Normal(scenariopunkt, 0,01), klippet til [0,5; 0,99]

500 iterasjoner per scenario. Resultater (varighet i år, P5/P50/P95):
- Basis_85: 7,27 / 8,64 / 10,17
- Middels_90: 4,54 / 5,73 / 7,10
- Samferdsel_96: 1,41 / 2,20 / 3,22

**Nøkkelfunn:** scenarioene overlapper IKKE – P95 av Samferdsel (3,22) er under P5 av Middels (4,54). Automasjonsgraden er den dominerende usikkerhetskilden, ikke tidsbruk per kommune. Kartkontor-varighet er stabilt ~488 dager (P5-P95: 475-504).

### LÅST: NVDB-scenarioanalyse på automasjonsgrad

Samferdselsavdelingens uformelle anslag (~2 år) avviker fra CLAUDE.md-baseline (~7 år). Forskjellen tolkes som automasjonsgrad. Tre scenarioer i `nvdb_overfoering.csv`:

| Scenario | Automasjon | Manuell | Total/dag | Estimert |
|----------|-----------|---------|-----------|----------|
| Basis_85 | 85% | 175 | 1 167 | ~7 år |
| Middels_90 | 90% | 175 | 1 750 | ~4.7 år |
| Samferdsel_96 | 96% | 175 | 4 375 | ~2 år |

Bemanning (0.5 årsverk) og manuell produksjonstakt (350 lenker/dag) holdes konstant. NVDB-startdato: 2026-05-01.

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

## Neste steg: heuristikk.py

Ikke skrevet ennå. Skal ligge i `004 data/scripts/heuristikk.py`.

### Algoritme (pseudokode)

```
INPUT:
  kommuner       — master_kommuner.csv
  kontorer       — kapasitet_kontorer.csv
  geovekst       — geovekst_prosjekter.csv
  nvdb_scenario  — én rad fra nvdb_overfoering.csv

KONSTANTER:
  TIMER_PER_UKESVERK = 37.5
  ARBEIDSDAGER_PER_AAR = 230
  STARTDATO = 2026-05-01

STEG 1: Beregn gjenvaerende_timer per kommune
  For hver kommune:
    Hvis Status == 'Ferdig': ferdigdato_kartkontor = STARTDATO, skip
    Ellers: gjenvaerende_timer = (Ber_Tidbruk_Min / 60) * (Gjenstaaende_Lenker / Antall_Lenker)

STEG 2: Bygg prioriteringskø per kontor
  For hvert kontor:
    sorter kommuner etter:
      1. Låst på STARTDATO → sist
      2. Ikke-låste: størst først
      3. Låste: tidligste opplåsing først

STEG 3: Simuler dag for dag (arbeidsdager, hopp over helg)
  gjeldende_dato = STARTDATO
  nvdb_ko = []

  Mens ikke alle kommuner er ferdige NVDB:
    For hvert kontor parallelt:
      aktiv = første kommune i køen som ikke er låst på gjeldende_dato
      timer_i_dag = kontor.Kapasitet_Ukesverk * 37.5 / ARBEIDSDAGER_PER_AAR  # årlig kapasitet fordelt på arbeidsdager
      aktiv.gjenvaerende_timer -= timer_i_dag
      Hvis aktiv.gjenvaerende_timer <= 0:
        aktiv.ferdigdato_kartkontor = gjeldende_dato
        nvdb_ko.append(aktiv)
        fjern fra kontor.ko

    Hvis gjeldende_dato >= nvdb_scenario.Startdato og nvdb_ko ikke tom:
      kapasitet = nvdb_scenario.Total_Throughput_Per_Dag
      Mens kapasitet > 0 og nvdb_ko ikke tom:
        ta fra kommune i front av køen, trekk fra lenker
        hvis ferdig: kommune.ferdigdato_nvdb = gjeldende_dato

    gjeldende_dato += 1 arbeidsdag

OUTPUT:
  tidsplan.csv                — per kommune: KomNr, start/slutt kartkontor og NVDB
  kapasitetsbruk_per_uke.csv  — per uke per kontor: timer brukt, utnyttelse
  flaskehals_nvdb.csv         — per uke: kø-lengde, ferdige kommuner totalt
```

### Bevisste forenklinger for v1 (baseline-heuristikk)

- Ingen planlegging av ferier/pauser
- Ingen individuell effektivitet per person
- Ingen oppstartskostnad ved kommuneskifte
- **Baseline:** kommuner tildeles sitt "hjemme-kontor" basert på fylke (status quo). Dette er KUN baseline – omfordeling mellom kontor er en kjernebeslutning i prosjektet (jf. proposal) og skal undersøkes i MIP og evt. en utvidet heuristikk-variant.

### Skal kjøres for alle 3 NVDB-scenarioer for sensitivitetsanalyse

## Pågående arbeid

Se `STATUS.md` for detaljert fremdrift. Nåværende fokus:

1. ✅ Datavask fullført (4 processed CSV-filer)
2. ✅ Metodevalg låst (hybrid heuristikk + MIP)
3. ✅ NVDB-scenarioer definert
4. ✅ 6 deskriptive figurer produsert
5. ✅ Rapport-seksjon 4 (Casebeskrivelse) og 5.2 (Data) utkast skrevet
6. 🔄 Heuristikk-implementering (neste)
7. ⏳ MIP-modell
8. ⏳ Resultater og diskusjon
9. ⏳ Rapport-seksjoner 1, 2, 3, 6, 7, 8, 9, 10

### Viktige milepæler

- **29.04.2026** - Godkjent hovedutkast (12 dager unna per 2026-04-17)
- **01.06.2026** - Innlevert rapport

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
3. `004 data/processed_data/master_kommuner.csv` - Hoveddatasett
4. `004 data/processed_data/nvdb_overfoering.csv` - NVDB-scenarioer
5. `004 data/scripts/vask_og_strukturer.py` - Datavask-logikk
6. `005 report/rapport.md` - Aktuell rapport (seksjon 4 og 5.2 har innhold)

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
