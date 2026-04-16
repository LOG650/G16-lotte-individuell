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
- **NVDB-overføring:** 2 stillinger × 25% = 0,5 årsverk. 80-90% automatisk via FME, resten manuelt. 300-400 lenker/person/dag.
- **Status per april 2026:** 62 ferdig kvalitetshevet, 48 påbegynt, 247 ikke startet. **Ingen** er overført til NVDB ennå.

## Mappestruktur

```
G16-lotte-individuell/
├── CLAUDE.md                        ← Denne filen
├── STATUS.md                        ← Levende statusdokument
├── 000 templates/
│   └── Mal prosjekt LOG650 v2.docx  ← Rapportmal (Word)
├── 001 info/
├── 002 meetings/
├── 003 references/
├── 004 data/
│   ├── raw_data/                    ← Rådata
│   ├── processed_data/              ← Vaskede data (output)
│   ├── scripts/
│   │   ├── vask_og_strukturer.py    ← Hovedscript for datavask
│   │   ├── generer_status.py        ← Genererer STATUS.md fra prosjektplan.json
│   │   └── generer_master_data.py   ← Eldre script (beholdt som referanse)
│   └── generer_excel_med_faner.py   ← Genererte datainnsamlingsmal
├── 005 report/
│   └── rapport.md                   ← Rapportmal (Markdown)
├── 011 fase 1 - proposal/
│   └── proposal.md                  ← Godkjent proposal
├── 012 fase 2 - plan/
│   ├── prosjektstyringsplan_utfylt.md  ← Godkjent prosjektplan
│   ├── Gannt.pdf                       ← Gantt-eksport fra MS Project
│   └── prosjektplan.json               ← Strukturert prosjektplan
├── 013 fase 3 - review/
└── 014 fase 4 - report/
```

## Datakilder (rådata)

| Fil | Innhold |
|-----|---------|
| `data.csv` | Fremdriftsstatus per kommune (Ferdig/Påbegynt/Ikke påbegynt). Fra samferdselsavd. PowerBI-rapport |
| `Antall objekter per kommune.csv` | Arbeidsmengde i **antall lenker** (ikke km) per kommune - 355 rader |
| `20250903StatistikkTraktorvegSti.xlsx` | Kommunemapping, km_kurve, beregnet tidsbruk. **MERK:** fylkesnr/fylkesnavn er feil/shufflet og må ignoreres |
| `Datainnsamling_TraktorvegSti.xlsx` | Kapasitet (ukesverk), min/max tidsbruk per kontor, Geovekst-prosjekter per kommune. 10 ark (ett per kontor). Kristiansand-arket er tomt. |
| `Agder_prosjekter.csv` | Geovekst LACIAG61, LACIAG63 - supplerer Datainnsamling |
| `Rogaland_prosjekter.csv` | Geovekst LACIRO61, LACIRO62 - supplerer Datainnsamling |

## Behandlede data (output)

Produsert av `004 data/scripts/vask_og_strukturer.py`:

| Fil | Innhold |
|-----|---------|
| `master_kommuner.csv` | 357 rader - en per kommune med KomNr, Kommune, Fylke, Kartkontor, Status, Fremdrift_Prosent, Antall_Lenker, Km_Kurve, Gjenstaaende_Lenker, Er_Laast, Geovekst_Prosjekter |
| `kapasitet_kontorer.csv` | 10 rader - Kartkontor, Kapasitet_Ukesverk, Min/Max_Tidsbruk_Timer, Antall_Kommuner, Total_Lenker, Gjenstaaende_Lenker |
| `geovekst_prosjekter.csv` | 165 rader - Prosjektnr, KomNr, Kommune, Kartkontor, Prosjektstatus, Laaseperiode_Start, Laaseperiode_Slutt |

## Viktige avklaringer (fra dialog med brukeren)

### Dataspesifikke

- **Fylkesnr/fylkesnavn** i StatistikkTVS er feil/shufflet → ignoreres, utledes fra kommunenummer (komm // 100)
- **Arbeidsmengde** = antall lenker, IKKE km
- **Produksjonstakt:** 300-400 lenker/person/dag
- **data.csv statuser:** "Ferdig" = kartkontoret er ferdig med kvalitetsheving (IKKE overført til NVDB ennå)

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

Ulike tekstformater i rådata ("Juni-Desember", "7", "August 2026 - mars 2027"). Standardiseres til datoer. For ukjente (Skien "7", Agder CSV, Rogaland CSV) brukes **mai-desember 2026** (7 mnd).

## Viktige nøkkeltall

- **357** kommuner (alle må behandles)
- **10** kartkontor med varierende kapasitet (20-52 ukesverk)
- **2 630 964** lenker totalt
- **2 138 104** lenker gjenstår
- **145** kommuner låst av Geovekst-prosjekter
- **NVDB manuell kapasitet:** 2 × 0.25 × 350 = 175 lenker/dag

## Metodiske valg (UNDER DISKUSJON)

Drøftet med brukeren, men ikke endelig bestemt:

### Hovedmetode - alternativer

1. **Optimalisering (IP/MIP)** - PuLP eller OR-Tools, finner optimal løsning
2. **Heuristikk + scenarioanalyse** - regelbaserte strategier, praktisk
3. **Hybrid** - heuristikk som baseline + MIP for forbedring (anbefalt)

### ML som supplement?

- **Relevant:** Enkel regresjon på de 62 ferdige kommunene for å validere Ber_tidbruk_minutter
- **Ikke hovedmetode:** For lite treningsdata, tidsestimat finnes allerede
- **Argument for:** Gir "KI-element" i tråd med kursnavn (LOG650 Logistikk og **KI**)

### Train/test-split?

- **OR-modell:** Nei - alle 357 kommuner brukes til å definere problemet. Validering via scenarioanalyse.
- **Regresjon (hvis valgt):** Ja, men kryssvalidering er bedre med kun 62 ferdige kommuner.

## Pågående arbeid

Se `STATUS.md` for detaljert fremdrift. Nåværende fokus:

1. ✅ Datavask fullført
2. 🔄 Rapportstruktur under skriving (005 report/rapport.md)
3. ⏳ Metodevalg må ferdigstilles
4. ⏳ NVDB-overføringskapasitet må legges inn som datafil (`nvdb_overfoering.csv`)
5. ⏳ Modelleringen må påbegynnes

### Viktige milepæler

- **29.04.2026** - Godkjent hovedutkast (13 dager unna)
- **01.06.2026** - Innlevert rapport

## Kommunikasjonsstil

- Brukeren foretrekker **norsk** (bokmål)
- Konsise svar, ikke overflødig forklaring
- Bruker AskUserQuestion aktivt når noe er uklart
- Plan-modus brukes for større endringer

## Tekniske detaljer

- **OS:** Windows 11, bruker bash-shell
- **Python:** 3.13 (Microsoft Store-versjon)
- **Python-avhengigheter brukt:** pandas, numpy, openpyxl, python-docx
- **Encoding-notat:** Windows cp1252 → UTF-8 må fikses i Python-scripts med `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`

## Referansefiler å lese ved oppstart

For rask kontekst-gjenoppretting:
1. `STATUS.md` - Hvor er vi akkurat nå? (auto-generert fra JSON)
2. `012 fase 2 - plan/prosjektplan.json` - **Single source of truth** for prosjektstatus
3. `011 fase 1 - proposal/proposal.md` - Problemstilling
4. `004 data/processed_data/master_kommuner.csv` - Hoveddatasett
5. `004 data/scripts/vask_og_strukturer.py` - Datavask-logikk

## Workflow for statusoppdatering

1. Endre status/fremdrift/kommentarer i `012 fase 2 - plan/prosjektplan.json`
2. Kjør: `python "004 data/scripts/generer_status.py"`
3. STATUS.md regenereres automatisk

**Aldri rediger STATUS.md direkte** - endringer går tapt ved neste regenerering.
