# Plan for å lukke issues fra reviewrapporten

**Dato:** 2026-04-20
**Kontekst:** `reviewrapport_modellering.md` identifiserte 17 issues (6 alvorlige, 6 viktige, 6 mindre) + tilleggsfunn fra samferdselsavdelingens data. Denne planen dekker hva som må endres i kode/data, hva som må skrives om i rapporten, og rekkefølgen.
**Tidsramme:** 9 dager til milepæl 29.04. Rapportseksjon 5.1 og 9.0 må også skrives i samme periode.

---

## 0. Strategisk veivalg (må avgjøres først)

**Valgt: Hybrid-tilnærming**
- Endre `Produksjonstakt_Manuell` fra 350 til 300 i alle scenarioer (1 parameter)
- Behold 260 arbeidsdager/år i simulatoren, dokumenter valget og sammenlign med samferdselsavdelingens 240
- Utvid Monte Carlo-parametrene så scenariofordelinger kan overlappe realistisk
- Resultat: varigheter blir ~15 % lengre enn i dag, fortsatt ~8 % kortere enn samferdselsavdelingens tall – men langt mer forsvarlig

**Alternativer vurdert men forkastet:**
- Full kalibrering (endre også 260→240): mer arbeid, structural change, men gir eksakt match med samferdselsavdelingens 7,22 år
- Kun dokumentasjon: svak posisjon mot sensor ("dere ignorerte kundens tall")

---

## Fase 1 — Parameterkalibrering (2-3 timer, blokkerer nedstrøms)

### 1.1 Endre manuell takt i scenariofilen
- **Fil:** `004 data/processed_data/nvdb_overfoering.csv`
- **Endring:** `Produksjonstakt_Manuell` fra 350 → 300 for alle 4 scenarioer
- **Konsekvens for `Manuell_Kapasitet_Per_Dag` og `Total_Throughput_Per_Dag`:**
  - Basis_85: 175 → 150, 1167 → 1000
  - Middels_90: 175 → 150, 1750 → 1500 (duplikat med Samferdsel_90 – dropper Samferdsel_90?)
  - Samferdsel_96: 175 → 150, 4375 → 3750
- **Beslutningspunkt:** Middels_90 og Samferdsel_90 blir identiske etter kalibrering (begge 90 %, 300 l/dag). Slå sammen eller endre Middels_90 til annet (f.eks. 87,5 %)?
  - **Foreslått:** Fjern `Samferdsel_90` og endre Middels_90 til takt=300 som "samferdselsavdelingens eksplisitte regnestykke"; beholder 3-scenariostruktur

### 1.2 Rett kommentar på Samferdsel_96
- **Fil:** `004 data/processed_data/nvdb_overfoering.csv`
- **Gammel kommentar:** "Bakregnet fra samferdselsavdelingens anslag om ca 2 aar"
- **Ny kommentar:** "Optimistisk øvre grense – 96 % automasjon er bakoverregnet for å treffe 2-års-mål. Samferdselsavdelingen opererer selv med 80-90 % automasjon."

### 1.3 Utvid Monte Carlo-parametre
- **Fil:** `004 data/scripts/monte_carlo.py`
- **Endringer:**
  - `MANUELL_TAKT_LOW: 300 → 275` og `MANUELL_TAKT_HIGH: 400 → 325` (sentrert på 300, ±25)
  - `AUTOMASJON_STD: 0.01 → 0.03` (mer realistisk måleusikkerhet)
  - **Valgfritt:** La `scenario_takt` passes fra CSV i stedet for global konstant – lar scenarioer ha ulik takt-sentering. Men siden alle nå har takt=300, er dette unødvendig.

### 1.4 Oppdater CLAUDE.md
- **Fil:** `CLAUDE.md`
- **Seksjoner å oppdatere:**
  - "NVDB-scenarioanalyse på automasjonsgrad"-tabellen – nye throughput-tall
  - "LÅST: Monte Carlo-usikkerhetsanalyse" – nye sampling-parametre
  - "Viktige avklaringer"-seksjonen – produksjonstakt 300 (ikke 300-400)
  - Fjern eller endre "Samferdsel_96 = bakoverregnet fra samferdselsavdelingens anslag"

---

## Fase 2 — Kodeforbedringer (3-4 timer)

### 2.1 Kjør Samferdsel_96 på nytt med synlig solver-output
- **Issue:** 1.2 (Not Solved status)
- **Kommando:** `python "004 data/scripts/mip_modell.py" --scenario Samferdsel_96 --mode vektet --tidsgrense 3600`
- **Pass på:** sett `msg=True` i `solve_modell`-kallet i scriptet, evt. redirect stdout til fil
- **Dokumenter:** CBC's rapporterte MIP-gap, bestBound, solve-tid

### 2.2 Kjør S2_Alle_pluss20 i sensitivitet
- **Issue:** 1.5 (mangler fra output)
- **Kommando:** `python "004 data/scripts/mip_kapasitet_sensitivitet.py" --varianter S2_Alle_pluss20 --tidsgrense 3600`
- **Alternativ:** hvis timeout igjen, fjern varianten fra `lag_varianter()` og dokumenter at S0-S4 dekker praktisk relevant område

### 2.3 Legg til ekstremvariant S5_Alle_minus50
- **Issue:** 1.6 (sensitivitet viser ingen varians i makespan)
- **Fil:** `004 data/scripts/mip_kapasitet_sensitivitet.py`
- **Endring:** legg til `('S5_Alle_minus50', {k: 0.5 for k in alle_kontor})` for å vise kartkontor-bundet regime
- **Formål:** bevise at modellen *kan* produsere endret makespan under tilstrekkelig kapasitetsreduksjon

### 2.4 Legg til lav-inertia MIP-variant
- **Issue:** 2.5 (inertia-termens dominans gir 59 "gratis" omfordelinger)
- **Fil:** `004 data/scripts/mip_modell.py`
- **Endring:** legg til argparse-flag `--w2-scale` (default 1.0), multiplikator på `W2`. Kjør med `--w2-scale 0.001` for å se om makespan holder seg ved færre omfordelinger.
- **Formål:** diskusjonspoeng om organisatorisk kostnad av omfordelinger

### 2.5 Endre FIFO-tie-breaker til størrelse
- **Issue:** 2.6 (alfabetisk sortering ved like Ledig_Fra_Mnd)
- **Fil:** `004 data/scripts/mip_modell.py`, `fifo_nvdb_per_kommune()`
- **Endring:** `sorted(..., key=lambda k: (k['Ledig_Fra_Mnd'], -k['Lenker']))` – største først
- **Valider:** `heuristikk.py` bruker ferdigstillelsesrekkefølge, ikke alfabetisk; sjekk om endringen gir synkron oppførsel

### 2.6 Verifisér monte_carlo_mip vs monte_carlo
- **Issue:** 3.5 (mistanke om identiske resultater)
- **Handling:** kjør `monte_carlo_mip.py` etter fase 1, sammenlign summary med `monte_carlo_summary.csv`
- **Hvis nær-identiske:** fjern `monte_carlo_mip.py` fra rapporten, behold kun som sanity-check-fil i repoet
- **Hvis signifikant forskjellige:** dokumenter forskjellen som robusthetstest av MIP-assignment

### 2.7 Ingen kodeendring, men dokumenter i rapporten
- **Issue 2.4** – myopisk heuristikk (kun STARTDATO-evaluering)
- **Issue 3.2** – konstant NVDB-kapasitet
- **Issue 3.4** – MAX_AAR=12 hardkodet

---

## Fase 3 — Full rekjøring (2-3 timer compute, mye i bakgrunn)

**Rekkefølge (avhengigheter):**

1. `heuristikk.py` – rask (< 1 min), alle 4 (evt. 3) scenarioer
2. `monte_carlo.py` – 500 iter × 4 scenarioer (~10 min)
3. `mip_modell.py --mode vektet` – alle scenarioer (~20-30 min, kan kjøres i bakgrunn parallelt med fase 4)
4. `mip_kapasitet_sensitivitet.py` – 5-6 varianter × 3 scenarioer (~30-60 min)
5. `monte_carlo_mip.py` – valgfritt, avhenger av 2.6
6. Figurer:
   - `figurer.py` (deskriptive 1-6 – ikke påvirket, kan skippes)
   - `figurer_resultater.py` (7-10)
   - `figurer_usikkerhet.py` (11-13)
   - `figurer_mip.py` (14-19)

---

## Fase 4 — Rapportendringer (2-3 timer)

### 4.1 Seksjon 5.1 — Metode (er fortsatt tom, skrives uansett)
- Dokumentér NVDB-formel `Throughput = 0,5 × Takt / (1 − auto)` og dens divergens nær auto=1 (**issue 1.4**)
- Forsvar `AUTOMASJON_STD = 0,03` som realistisk måleusikkerhet (**issue 2.3**)
- Begrunn bootstrap-strategi (uavhengighet mellom kommuner, kartblad- vs kommune-nivå) (**issue 2.1, 2.2**)
- Nevn myopisk heuristikk eksplisitt (**issue 2.4**)
- Kort setning om konstant NVDB-kapasitet (ingen ferier/opplæring) (**issue 3.2**)

### 4.2 Seksjon 5.2 — Data
- Nevn at validering mot 62 ferdige kommuner krever faktisk-tidsbruk-data som ikke er tilgjengelig (**issue 3.1**)
- Oppdater tabellen for NVDB-scenarioer med nye tall

### 4.3 Seksjon 6 — Modellering
- **Kapasitetskonvensjon (issue 1.3):** eksplisitt avsnitt som begrunner 260 arbeidsdager/år, sammenligner med samferdselsavdelingens 240, kvantifiserer forskjellen (~8 %)
- Nevn MIP: månedlig diskretisering er hovedkilden til at MIP er marginalt verre enn heuristikk på makespan

### 4.4 Seksjon 7 — Analyse
- **Ny kalibreringstabell (hovedbidrag fra samferdselsavdelingens data):** prosjektmodell vs samferdselsavdelingens regnestykke side om side
- Reframe sensitivitet: "NVDB er dominerende flaskehals – kartkontor er robust mot rimelige kapasitetsforstyrrelser" (**issue 1.6**)

### 4.5 Seksjon 8 — Resultat
- **Reframe MIP-bidraget (issue 1.1):** MIP bekrefter at heuristikkens hjemmekontor-assignment er nær optimal, ikke "forbedrer" – dette er et positivt funn, ikke en svakhet
- Dokumentér Samferdsel_96 status (Optimal vs Not Solved), MIP-gap fra CBC (**issue 1.2**)

### 4.6 Seksjon 9 — Diskusjon (er fortsatt tom, skrives uansett)
- **Usikkerhet og robusthet:**
  - Bootstrap uten korrelasjon overdriver per-kontor-spredning (**issue 2.1**)
  - Kartblad-nivå MIN/KM tildelt per kommune (**issue 2.2**)
  - Scenarioer overlapper med ny AUTOMASJON_STD=0,03 (**issue 2.3**)
- **Organisatoriske begrensninger:**
  - 59 omfordelinger er "gratis" i modellen – politisk/praktisk kostnad ikke modellert (**issue 2.5**)
- **Modellforenklinger:**
  - Myopisk heuristikk (**issue 2.4**)
  - NVDB-kapasitet konstant gjennom hele horisonten (**issue 3.2**)
- **Kalibrering mot eksternt anslag:**
  - Samferdselsavdelingens 7,22 år vs prosjektmodellens (nye) ~7 år – kvantifiser gap, forklar med 240-vs-260

---

## Fase 5 — CLAUDE.md + STATUS (30 min)

- Endre "Viktige nøkkeltall"-seksjonen med nye NVDB-tall
- Endre "NVDB-scenarioanalyse"-tabellen
- Rett "LÅST: Monte Carlo-usikkerhetsanalyse"-seksjonens parametre og resultater
- Oppdatér `012 fase 2 - plan/prosjektplan.json` med framdrift
- Kjør `python "004 data/scripts/generer_status.py"`

---

## Prioritetsmatrise hvis tid blir knapp

### MUST (stopper rapporten – gjør uansett)
- Fase 1 (alle delsteg)
- 2.1 (Samferdsel_96 gap-rapportering)
- Fase 3 steg 1-4
- Fase 4.1, 4.3, 4.5, 4.6

### SHOULD (svekker argumentasjonen hvis droppet)
- 2.2 (S2_Alle_pluss20)
- 2.3 (S5_Alle_minus50)
- 2.4 (lav-inertia MIP-variant)
- 2.5 (FIFO-tie-breaker)
- Fase 3 steg 5-6 (figurer)
- Fase 4.2, 4.4

### NICE (ingen merverdi hvis tid er knapp)
- 2.6 (monte_carlo_mip verifisering)
- 2.7 (ren dokumentasjon av forenklinger)
- Fase 5 (oppdateres kontinuerlig)

---

## Totalestimat

| Fase | Tid aktiv | Tid compute (bakgrunn) |
|---|---|---|
| 1 | 2-3 t | – |
| 2 | 3-4 t | 1 t (MIP-rekjøringer) |
| 3 | 30 min setup + overvåkning | 1-2 t |
| 4 | 2-3 t | – |
| 5 | 30 min | – |
| **Sum** | **8-11 t aktiv** | **2-3 t compute** |

Fordelt over 2-3 arbeidsdager mellom 20.-24. april gir rom for rapportseksjon 5.1 og 9.0 (som uansett skal skrives), samt peer review 27.-28. april.

---

## Sjekkliste (for gradvis avhaking under arbeidet)

### Fase 1
- [ ] 1.1 Endre takt 350→300 i `nvdb_overfoering.csv`
- [ ] 1.1 Beslut om Samferdsel_90 skal beholdes eller fjernes etter kalibrering
- [ ] 1.2 Rett kommentar på Samferdsel_96
- [ ] 1.3 Utvid MC-parametre i `monte_carlo.py`
- [ ] 1.4 Oppdater CLAUDE.md-seksjoner

### Fase 2
- [ ] 2.1 Rekjør Samferdsel_96 MIP med synlig output, noter gap
- [ ] 2.2 S2_Alle_pluss20 (kjør eller fjern)
- [ ] 2.3 Legg til S5_Alle_minus50
- [ ] 2.4 `--w2-scale` flag i mip_modell.py
- [ ] 2.5 FIFO-tie-breaker til størrelse
- [ ] 2.6 Verifisér monte_carlo_mip

### Fase 3
- [ ] 3.1 Rekjør heuristikk.py
- [ ] 3.2 Rekjør monte_carlo.py
- [ ] 3.3 Rekjør mip_modell.py (alle scenarioer)
- [ ] 3.4 Rekjør mip_kapasitet_sensitivitet.py
- [ ] 3.5 Regenerer figurer 7-19

### Fase 4
- [ ] 4.1 Seksjon 5.1 skrives med review-punkter innarbeidet
- [ ] 4.2 Seksjon 5.2 oppdateres
- [ ] 4.3 Seksjon 6 oppdateres
- [ ] 4.4 Seksjon 7 oppdateres + kalibreringstabell
- [ ] 4.5 Seksjon 8 reframes
- [ ] 4.6 Seksjon 9 skrives med review-punkter innarbeidet

### Fase 5
- [ ] 5.1 CLAUDE.md oppdatert
- [ ] 5.2 prosjektplan.json oppdatert
- [ ] 5.3 STATUS.md regenerert
