# Prosjektstatus

**Prosjekt:** Kvalitetsheving av FKB-TraktorvegSti før implementering i NVDB  
**Fag:** LOG650 Logistikk og KI | **Institusjon:** Høgskolen i Molde  
**Prosjektleder:** Lotte Picard | **Kunde:** Statens Kartverk, Region og Samfunnskontakt  
**Periode:** 2026-01-12 → 2026-06-01  
**Sist oppdatert:** 2026-04-23

> Denne fila er auto-generert fra `012 fase 2 - plan/prosjektplan.json`. Kjør `python "004 data/scripts/generer_status.py"` for å oppdatere.

---

## Overordnet status

- **Nåværende fase:** Fase 3 – Gjennomføring
- **Neste milepæl:** Godkjent hovedutkast – 2026-04-29 (6 dager)
- **Dager igjen til innlevering:** 39
- **Kritisk linje:** Planleggingsleveranse → Datainnsamling → Analyse/modelldel → Diskusjon → Peer review → Sluttføring av rapport

### Faseoversikt

| Fase | Periode | Status | Fremdrift |
|------|---------|--------|-----------|
| 1. Initiering | 12.01 – 09.02.26 | ✅ Ferdig | 100% |
| 2. Planlegging | 02.03 – 20.03.26 | ✅ Ferdig | 100% |
| 3. Gjennomføring | 16.03 – 27.04.26 | 🔄 Pågående | 90% |
| 4. Avslutning | 27.04 – 31.05.26 | ⏳ Ikke startet | 0% |

---

## Milepæler

| Milepæl | Dato | Status |
|---------|------|--------|
| Godkjent proposal | 2026-02-16 | ✅ Ferdig |
| Godkjent prosjektplan og Gantt | 2026-03-16 | ✅ Ferdig |
| **Godkjent hovedutkast** | **2026-04-29** | ⏳ Neste |
| Innlevert rapport | 2026-06-01 | ⏳ Ikke startet |

---

## Oppgaver – Fase 3 (Gjennomføring)

| ID | Oppgave | Periode | Status | % | Kommentar |
|----|---------|---------|--------|---|-----------|
| 15 | Introduksjon og problemstilling | 16.03 – 18.03 | 🔄 Pågående | 50% |  |
| 16 | Teori og litteratursøk | 19.03 – 25.03 | 🔄 Pågående | 30% |  |
| 17 | Casebeskrivelse og datainnsamling | 26.03 – 03.04 | ✅ Ferdig | 100% | Datagrunnlaget komplett: master_kommuner.csv, kapasitet_kontorer.csv, geovekst_prosjekter.csv og nvdb_overfoering.csv produsert |
| 18 | Data/metode og modellering | 06.04 – 14.04 | ✅ Ferdig | 100% | Heuristikk, Monte Carlo og MIP-modell komplett. MIP i PuLP/CBC med vektet målfunksjon (makespan + kartkontor-ferdig + inertia). Alle 3 NVDB-scenarioer løst optimalt. Kapasitet-sensitivitet for 6 varianter (S0-S5) × 3 scenarioer = 18 MIP-kjøringer. Post-260-fiks (2026-04-23): 6/18 Optimal, 12/18 Not Solved pga økt solverkompleksitet ved lavere kapasitet. Makespan fortsatt identisk på tvers av alle varianter (NVDB dominerer). Monte Carlo på MIP-plan gir nå identiske percentiler med heuristikk-MC for Basis_85 (6,46/10,01/13,28); tidligere observert gap var artefakt av 260/230-overbruket. Rapport-seksjon 6.0 Modellering skrevet. |
| 19 | Analyse og resultater | 15.04 – 21.04 | 🔄 Pågående | 95% | Rapport-seksjon 6.0 Modellering, 7.0 Analyse og 8.0 Resultat utkastet ferdig. 5 MIP-figurer (14-16, 18-19) produsert. Kalibrering mot samferdselsavdelingens tall (2026-04-20/21). Post-260-fiks (2026-04-23): alle modeller og MC rekjørt etter review-funn 2.1; makespan uendret (Basis_85 10,17 / Middels_90 6,75 / Samferdsel_96 2,75 år), omfordelinger økt (97/76/54 fra 36/38/39), MC P95 Basis_85 11,98→13,28 år. Sensitivitet: makespan identisk på tvers av 6 varianter, kartkontor 10-13 mnd i alle (inkl S5 -50% som tidligere ga 11 mnd = LP-relax). Gjenstår: rapportseksjon 5.1 Metode + 9.0 Diskusjon. |
| 20 | Diskusjon | 22.04 – 24.04 | ⏳ Ikke startet | 0% |  |
| 21 | Peer review | 27.04 – 28.04 | ⏳ Ikke startet | 0% |  |

## Oppgaver – Fase 4 (Avslutning)

| ID | Oppgave | Periode | Status | % | Kommentar |
|----|---------|---------|--------|---|-----------|
| 25 | Konklusjon | 27.04 – 05.05 | ⏳ Ikke startet | 0% |  |
| 26 | Ferdigstille introduksjon | 06.05 – 14.05 | ⏳ Ikke startet | 0% |  |
| 27 | Kvalitetssikring og korrektur | 15.05 – 28.05 | ⏳ Ikke startet | 0% |  |
| 28 | Muntlig presentasjon | 29.05 – 29.05 | ⏳ Ikke startet | 0% |  |

## Ferdige faser (sammendrag)

- **Fase 1 – Initiering** (2026-01-12 → 2026-02-09): 1 oppgaver, milepæl `Godkjent proposal` nådd 2026-01-19
- **Fase 2 – Planlegging** (2026-03-02 → 2026-03-20): 6 oppgaver, milepæl `Godkjent prosjektplan og Gantt` nådd 2026-03-20

---

## Leveranser

| Leveranse | Fase | Status |
|-----------|------|--------|
| `011 fase 1 - proposal/proposal.md` | 1 | ✅ Ferdig |
| `012 fase 2 - plan/prosjektstyringsplan_utfylt.md` | 2 | ✅ Ferdig |
| `012 fase 2 - plan/Gannt.pdf` | 2 | ✅ Ferdig |
| `012 fase 2 - plan/prosjektplan.json` | 2 | ✅ Ferdig |
| `004 data/processed_data/master_kommuner.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/kapasitet_kontorer.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/geovekst_prosjekter.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/nvdb_overfoering.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/tidbruk_kalibrering.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/tidbruk_konstanter.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/tidsplan_<scenario>.csv (3 filer)` | 3 | ✅ Ferdig |
| `004 data/processed_data/oppsummering_scenarioer.csv` | 3 | ✅ Ferdig |
| `004 data/processed_data/monte_carlo_*.csv (4 filer)` | 3 | ✅ Ferdig |
| `004 data/scripts/vask_og_strukturer.py` | 3 | ✅ Ferdig |
| `004 data/scripts/heuristikk.py` | 3 | ✅ Ferdig |
| `004 data/scripts/monte_carlo.py` | 3 | ✅ Ferdig |
| `004 data/scripts/figurer.py` | 3 | ✅ Ferdig |
| `004 data/scripts/figurer_resultater.py` | 3 | ✅ Ferdig |
| `004 data/scripts/figurer_usikkerhet.py` | 3 | ✅ Ferdig |
| `005 report/figurer/ (13 PNG-figurer)` | 3 | ✅ Ferdig |
| `005 report/rapport.md` | 3 | 🔄 Pågående |
| `MIP-modell (PuLP)` | 3 | ❓ Avventer samferdselsavdelingens svar |

---

## Risikostatus

| ID | Risiko | S | K | Status |
|----|--------|---|---|--------|
| R1 | Forsinket datainnsamling eller manglende tilgang til relevante data | M | H | 🟡 Aktiv |
| R2 | Dårlig datakvalitet i TraktorvegSti eller historiske kapasitetsdata | H | M | 🟡 Aktiv |
| R3 | Endringer i Geovekst-prosjekter gjør planforutsetninger utdaterte | M | M | 🟡 Aktiv |
| R4 | Tidsmangel i sluttfasen av prosjektet | H | H | 🟡 Aktiv |
| R5 | Modelleringen gir ikke tydelige resultater | M | M | 🟡 Aktiv |

---

## Nøkkeltall fra data

- **357** kommuner totalt
- **10** kartkontorer
- **2 630 964** lenker totalt
- **2 138 104** gjenstående lenker
- **152** kommuner låst av Geovekst-prosjekter
- Status: 62 ferdig kvalitetshevet, 48 påbegynt, 247 ikke startet

### Kapasitet per kartkontor

| Kontor | Kommuner | Lenker | Gjenstående | Låst | Ukesverk |
|--------|----------|--------|-------------|------|----------|
| Bergen | 43 | 342 927 | 320 208 | 27 | 40 |
| Bodø | 41 | 157 997 | 154 992 | 15 | 22 |
| Hamar | 46 | 409 715 | 275 331 | 31 | 25 |
| Kristiansand | 25 | 246 636 | 218 155 | 11 | 30 |
| Molde | 27 | 126 294 | 75 602 | 26 | 25 |
| Oslo | 52 | 453 204 | 341 271 | 2 | 30 |
| Skien | 23 | 195 777 | 186 570 | 15 | 40 |
| Stavanger | 23 | 128 923 | 110 121 | 10 | 28 |
| Tromsø | 39 | 254 187 | 207 865 | 11 | 35 |
| Trondheim | 38 | 315 304 | 247 989 | 4 | 52 |

---

## Datakilder

- `data.csv` – Fremdriftsstatus per kommune (Ferdig/Påbegynt/Ikke påbegynt) - dekker hele løypa inkl. NVDB-overføring
  - *Merknad:* Per april 2026: 62 ferdig kvalitetshevet, 48 påbegynt, 247 ikke startet. Ingen ferdig overført til NVDB ennå.
- `Antall objekter per kommune.csv` – Arbeidsmengde i antall lenker (ikke km) per kommune - 355 kommuner
- `20250903StatistikkTraktorvegSti.xlsx` – Kommunemapping, km_kurve, beregnet tidsbruk, dagsverk - 359 kommuner
  - *Merknad:* Fylkesnr/fylkesnavn er feil/shufflet og må ignoreres. Kommunenr+kommunenavn er korrekt.
- `Datainnsamling_TraktorvegSti.xlsx` – Kapasitet (ukesverk), min/max tidsbruk per kommune, og Geovekst-prosjekter med låseperioder
- `Agder_prosjekter.csv` – Geovekst-prosjekter LACIAG61 og LACIAG63 - supplerer Datainnsamling der Kristiansand-arket var tomt
- `Rogaland_prosjekter.csv` – Geovekst-prosjekter LACIRO61 og LACIRO62 - supplerer Datainnsamling

---

## Endringslogg

| Dato | Endring |
|------|---------|
| 2026-04-23 | STATUS.md regenerert fra prosjektplan.json |
