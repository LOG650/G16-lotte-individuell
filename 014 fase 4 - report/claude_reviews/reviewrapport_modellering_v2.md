# Reviewrapport v2 – modellering LOG650 (oppfølgingsreview etter kalibrering)

**Dato:** 2026-04-21
**Omfang:** `heuristikk.py`, `monte_carlo.py`, `mip_modell.py`, `mip_kapasitet_sensitivitet.py`, `monte_carlo_mip.py` + oppdaterte output-CSV-filer og solver-logger etter rekjøringen 2026-04-20.
**Kontekst:** Forrige review (`reviewrapport_modellering.md`, 2026-04-20) identifiserte 17 issues + tilleggsfunn fra samferdselsavdelingens data. `fikse_issues_plan.md` ble lagt, det meste er kjørt, og denne reviewen vurderer *restrisikoen* før seksjon 9 skrives.

---

## 0. Hva er ferdig adressert siden forrige review

| Issue | Status | Evidens |
|---|---|---|
| 1.2 Samferdsel_96 "Not Solved" | ✅ Løst | `oppsummering_mip_vektet.csv`: Optimal i 158 s |
| 1.5 S2_Alle_pluss20 manglet | ✅ Løst | I `oppsummering_sensitivitet.csv`, alle 3 NVDB-scenarioer Optimal |
| 1.6 Ingen varians i makespan | ✅ Adressert med S5_Alle_minus50 | Egen variant lagt til, se nytt funn 1.1 under |
| 2.3 AUTOMASJON_STD=0.01 designvalg | ✅ Løst | `monte_carlo.py` bruker nå 0.03; P95 Samf_96 (5.88 år) > P5 Mid_90 (3.25 år) – overlappen er reell |
| 2.5 Lav-inertia variant | ✅ Delvis | `--w2-scale`-flagg lagt til; ikke tydelig om alternative kjøringer er produsert (søk etter `_w2-`-suffiks i CSVene: ingen treff) |
| 2.6 FIFO tie-breaker alfabetisk | ✅ Løst | Sortering er nå `(Ledig_Fra_Mnd, -Lenker, KomNr)` – størst først |
| Samferdsel-kalibrering (takt 350→300) | ✅ Løst | `nvdb_overfoering.csv` og `monte_carlo.py` oppdatert konsistent |

De *gjenstående* issuene fra forrige review er primært rapportformuleringer (reframing av MIP-bidraget, diskusjon av 230-vs-260, bootstrap-antagelser osv.) og blir adressert i seksjon 5.1 / 9. De er ikke gjentatt her.

---

## 1. Nye funn etter rekjøringen

### 1.1 ⚠️ **Solver-output er inkonsistent med CSV-output i "Not Solved"-tilfeller**

Dette er det alvorligste nye funnet. I `sens_log.txt` ser jeg:

```
  --- Samferdsel_96 (T=48) ---
    Ferdig (30362.3s, status Not Solved), makespan = 16 mnd    ← solve_vektet print
    Tid: 30362s | status: Not Solved
    Makespan: 33 mnd (2.75 aar)                                ← ekstraher_loesning
```

Og for S5_Alle_minus50 Basis_85:

```
    Ferdig (2723.8s, status Not Solved), makespan = 60 mnd     ← solve_vektet print
    Makespan: 122 mnd (10.17 aar)                              ← ekstraher_loesning
```

**Rotårsaken:** `solve_vektet` og `solve_lex_opt` beregner makespan som `sum(pulp.value(Q[t]) or 0)`, mens `ekstraher_loesning`→`fifo_nvdb_per_kommune` rekonstruerer makespan fra `z_it`-verdier (når kommuner blir ferdig på kartkontor) og deretter FIFO-dreneringen av NVDB-køen. Når CBC stopper med *Not Solved*, kan `pulp.value(Q[t])` være fractional (LP-relaksasjon) eller fra en infeasibel deloppgave, mens `z_it` gir et konsistent rekonstruert skjema.

**Konsekvens:**
- CSV-verdien (122 / 81 / 33 mnd for S5-variantene) er den *konsistente* makespan
- Stdout-verdien (60 / 40 / 16 mnd for S5) er *misvisende* og vil føre sensor vill hvis stdout blir sitert
- De to verdiene kan avvike med opptil 2–3× i Not-Solved-tilfeller

**Anbefaling:**
1. Fiks `solve_vektet` til å rapportere `makespan_opt` fra den samme rekonstruksjonen som CSVen bruker, IKKE fra `sum(Q_t)` direkte. Eller tydelig annoter at stdout-verdien er "CBC's siste LP-anslag, kan avvike fra endelig rekonstruksjon".
2. I rapporten: siter kun CSV-verdiene (oppsummering_mip_vektet.csv, oppsummering_sensitivitet.csv). Ikke sitér stdout.

### 1.2 ⚠️ **S1_Trondheim50 + Samferdsel_96 kjørte i 8,4 timer uten å respektere tidsgrense**

`oppsummering_sensitivitet.csv` linje 7:
```
S1_Trondheim50,Samferdsel_96,301.0,Not Solved,33,2.75,10,33,295,30362.3
```

Tidsgrensen i koden er `SOLVER_TIDSGRENSE_SEK = 1800`. Dette tilfellet brukte 30 362 s = **17× grensen**. Alle andre S1-kjøringer brukte 327–519 s. Dette mønsteret (én utligger på 8+ timer) fortjener enten:

- Forklaring: ble kjørt med `--tidsgrense 36000` eller lignende for å *prøve* å finne optimum, uten hell
- Eller bekymring: CBC's `timeLimit` ble ikke respektert (har skjedd før med CBC i presolve-fasen)

**Anbefaling:**
1. Hvis bevisst: legg inn en kort kommentar i rapporten eller i `sens_log.txt` om at dette ble kjørt med utvidet grense og fortsatt ikke løste optimalt.
2. Hvis ikke bevisst: legg til hard cap med `pulp.PULP_CBC_CMD(..., options=['sec', str(tidsgrense)])` som en ekstra sikring, eller verifiser at CBC-versjonen respekterer `timeLimit`.
3. Uansett: rapporten bør nevne at Samferdsel_96 under S1 er *feasible, ikke Optimal*, og at makespan 33 mnd er en øvre grense (ikke bevist).

### 1.3 📊 **MIP-MC har *verre* P95-varighet enn Heuristikk-MC for Basis_85**

Sammenligning `monte_carlo_summary.csv` vs `monte_carlo_mip_summary.csv`:

| Scenario | Plan | P5 | P50 | **P95** | Kartkontor P95 |
|---|---|---|---|---|---|
| Basis_85 | Heuristikk | 2358 d | 3657 d | **4375 d** (11,98 år) | 504 d |
| Basis_85 | MIP | 2358 d | 3657 d | **4851 d** (13,28 år) | 444 d |
| Middels_90 | Heuristikk | 1188 d | 2435 d | 3620 d | 502 d |
| Middels_90 | MIP | 1188 d | 2435 d | 3620 d | 433 d |
| Samferdsel_96 | Heuristikk | 481 d | 862 d | 2149 d | 504 d |
| Samferdsel_96 | MIP | 367 d | 862 d | 2149 d | 444 d |

**Observasjoner:**
- **Kartkontor-P95 er bedre for MIP i alle 3 scenarioer** (444 vs 504, 433 vs 502, 444 vs 504). MIP's balanseringsoppgave fungerer i gjennomsnitt.
- **Varighet-P50 er identisk** (MIP-omfordeling har null effekt på median-varighet – NVDB er flaskehals).
- **Varighet-P95 er *verre* for MIP i Basis_85** (+476 dager, +11 %). I Middels_90 og Samferdsel_96 er de like i P95.

**Tolkning:** MIP's omfordeling konsentrerer noen store kommuner på utvalgte kontor for å minimere makespan. I ekstreme Monte Carlo-trekninger (høye MIN/KM-verdier) kan disse kontorene bli flaskehalser, og de ferdigstiller kartkontoret sent → kommune havner sent i NVDB-køen → siste kommune sin NVDB-ferdigdato forsinkes. Heuristikken har mer spredt last (hjemmekontor) og er derfor mer robust i halen.

**Konsekvens for issue 3.5 fra forrige review:** `monte_carlo_mip.py` er IKKE identisk med `monte_carlo.py`. Det gir ny og relevant info – spesielt: MIP er ikke bare marginalt verre enn heuristikken i baseline (issue 1.1), den er også mer skjør i halen.

**Anbefaling:**
1. Denne forskjellen bør fram i rapportens seksjon 9 (diskusjon). Det er et sterkt funn: *optimering for forventet tilfelle kan gi svakere robusthet*.
2. Overvei å legge til en kort stresstest: kjør MC med en høyere W2 eller lavere inertia for å se om tail-risk kan reduseres uten makespan-økning.

### 1.4 🐞 **`monte_carlo_mip.py` har hardkodet `MIP_MODE = 'vektet'`**

Linje 35: `MIP_MODE = 'vektet'  # hvilken MIP-loesning vi tar assignment fra`.

Hvis noen rekjører MIP i `lex`-modus eller `makespan`-modus, vil MC-MIP fortsatt plukke opp den gamle vektet-CSVen hvis den ligger igjen. Dette er en stillesittende konsistens-bombe.

**Anbefaling:** Gjør det til et `argparse`-argument, eller bruk en sjekk for nyeste `tidsplan_mip_*_<scenario>.csv`-fil.

### 1.5 🐞 **Feil kommentar om stdout-wrapping i `monte_carlo_mip.py`**

Linje 23:
```python
# heuristikk.py og monte_carlo.py wrapper sys.stdout selv - ikke dobbeltwrap her
```

Men `monte_carlo.py` wrapper IKKE sys.stdout – det er kun `heuristikk.py` og `mip_modell.py` som gjør det. Import av `heuristikk` wrapping'er da også `monte_carlo`'s utskrift via sidevirkning. Kommentaren er derfor feil.

**Konsekvens:** Ingen funksjonell feil (wrap-en skjer én gang via heuristikk-import), men kommentaren kan forlede videre kodeendringer.

**Anbefaling:** Kommentar-korreksjon:
```python
# heuristikk.py wrapper sys.stdout paa Windows; monte_carlo.py arver det via import.
```

### 1.6 🐞 **`solve_vektet` returnerer `makespan_opt` som aldri brukes**

Linje 384:
```python
makespan_opt = int(round(sum((pulp.value(Q[t]) or 0) for t in Tid)))
...
return {
    ...
    'makespan_opt': makespan_opt,
}
```

Verdien returneres, men `main()` bruker aldri den – den henter makespan fra `ekstraher_loesning` i stedet. Dette er dead code og kilden til forvirringen i funn 1.1. Enten:
- Fjern returfeltet, eller
- Bruk det til sanity-check mot `losning['makespan_mnd']` og advar hvis de avviker >1 mnd (gir tidlig varsling om CBC-solution-kvalitet)

Anbefalt: sanity-check.

### 1.7 🐞 **FIFO-rekonstruksjonen ignorerer solverens `D_t`-verdier**

`fifo_nvdb_per_kommune` bruker kun `z_it` og drenerer med maks kapasitet `mu` hver måned. Dette er nesten alltid riktig (solverens optimum drenerer også maks), men betyr at:

1. Enhver MIP-løsning med "lur" suboptimal drenering (f.eks. en pause i NVDB av andre grunner) vil bli overskrevet av FIFO
2. I "Not Solved"-tilfeller der `z_it` er fractional, gir `threshold > 0.5` en egen rekonstruksjon som ikke matcher solverens egen Q-basert makespan (funn 1.1)

**Anbefaling:** Dokumentér eksplisitt i en kodekommentar at `D_t` forkastes og at FIFO er *den autoritative* NVDB-tidsplanen post-solve. Da blir funn 1.1 forklart som designvalg, ikke bug. Alternativt: hvis solveren er Optimal, valider at FIFO-makespan matcher `sum(Q_t)` – ellers feilflagg.

---

## 2. Resterende strukturelle issues som fortsatt bør håndteres

### 2.1 Single-source-of-truth for NVDB-formelen (issue 3.3 fra forrige review)

Fortsatt hardkodet på to steder:
- `nvdb_overfoering.csv` (kolonne `Total_Throughput_Per_Dag`)
- `monte_carlo.py` (funksjonen `sample_nvdb_params`)

Hvis formelen endres (f.eks. innføring av FME-kapasitetstak), må begge steder oppdateres. Lav risk, men dokumenteres i seksjon 5.1.

### 2.2 `aggreger_uke_percentiler` filtrerer kolonner *etter* forward-fill

`monte_carlo.py` linje 176–185 forward-filler per metrikk/iterasjon, deretter beregner percentiler. Det ser riktig ut, men kantcaset "iterasjonen har NO data for metrikk m" (f.eks. tom `ukentlig_nvdb`) resulterer i en rad med kun NaN. Koden håndterer dette ok (`gyldig = kol[~np.isnan(kol)]`) men antall gyldige iterasjoner per uke er ikke alltid 500 – det kan variere. `N`-kolonnen rapporterer riktig, men hvis bruker lagrer P-kolonnen uten `N`, kan det være misvisende i figur-tittel.

**Anbefaling:** Behold som er, men nevne i figurtekst at percentiler er betinget på iterasjoner som hadde data for den uken (typisk 500 for tidlige uker, synkende for sene uker).

### 2.3 Grunnpakken (0,6510 min/km²) i MC holdes konstant

Fortsatt uadresseret (issue 2.1). Km²-leddet bidrar med ~36 % av Ber_Tidbruk_Min i snitt. Null varians på dette gjør at total kommune-tidsvariasjon undervurderes.

**Anbefaling:** Behold som er – det er forsvarlig fordi vi ikke har empirisk fordeling for km²-leddet. Dokumentert i seksjon 5.1.

### 2.4 `MAX_AAR = 15` cutoff i `heuristikk.py`

Nå 15 år (var 12 i forrige review). Basis_85 MC P95 er 11,98 år, så margin er 3 år. OK for dagens scenarioer. Men hvis sensor spør "hva skjer ved 75 % automasjon?" er cutoff raskt i spill.

**Anbefaling:** Bytt ut `MAX_AAR` med en beregnet grense: `max_aar = min(30, 1.5 * scenario_estimert_aar)`, eller bare 30.

### 2.5 `maaned_til_dato` returnerer alltid dag 15

`mip_modell.py` linje 89: `return date(aar, mnd, 15)`. Ferdigdatoene i `tidsplan_mip_*.csv` har derfor alle formatet YYYY-MM-15. Dette er kosmetisk, men hvis en sensor tar dato-kolonnen og gjør datoaritmetikk, kan det gi ±15 dager feil per sammenligning. Bør nevnes.

**Anbefaling:** Enten dokumenter i CSV-header (kommentar-kolonne) eller skift til månedens første dag (1.) som er mindre kognitivt støyende.

---

## 3. Styrker ved rekjøringen

- **Samferdselsavdelingens kalibrering ryddig gjennomført.** Produksjonstakt 300 og ny kommentar-linje på Samferdsel_96 er kvantifiserte endringer med tydelig audit trail.
- **AUTOMASJON_STD=0,03** er godt begrunnet i kildekommentar (linje 53–56 i `monte_carlo.py`), og den tidligere "overlapp-frie" narrativet er erstattet med et mer forsvarlig empirisk funn.
- **S5_Alle_minus50** er et smart valg for å vise at modellen *kan* bli kartkontor-bundet under ekstrem reduksjon – det strammer opp argumentasjonen i sensitivitetsdelen.
- **FIFO-tie-breaker endret til størrelse** er et minimalt men presist grep mot en subtil svakhet.
- **Full MIP-kjøring på alle 3 NVDB-scenarioer med Optimal-status** – betydelig kvalitativt steg opp fra forrige review.

---

## 4. Prioritert oppfølging før 29.04

Sortert etter kost/nytte, min→max innsats:

1. **Fiks dead code + inkonsistens i `solve_vektet`** (funn 1.1, 1.6) – 15 min: fjern `makespan_opt` fra returdict ELLER legg til sanity-check. Fiksjer også stdout-forvirring.
2. **Kodekommentarfiks i `monte_carlo_mip.py`** (funn 1.5) – 2 min.
3. **Dokumentér 30 362 s-kjøringen** (funn 1.2) – 10 min: én linje i rapporten eller i sens_log.txt.
4. **Skriv funn 1.3 (MIP-MC P95) inn i seksjon 9** – 20 min. Dette er det mest interessante nye funnet og forsterker rammene "MIP er nær-optimal, ikke forbedring" + "robusthet er tail-kritisk".
5. **Gjør `MIP_MODE` i `monte_carlo_mip.py` konfigurerbart** (funn 1.4) – 10 min hvis det blir kjørt på nytt; ellers skippes trygt.
6. **`MAX_AAR`-dynamisk cutoff** (funn 2.4) – 10 min, kun nødvendig hvis nye scenarioer legges til.

**Total minste aktive arbeid: ~1 time**, og de tre første bør gjøres som minste-cut-off før rapporten peer-reviews 27.-28. april.

---

## 5. Oppsummering i ett avsnitt

Kalibrerings-rekjøringen 2026-04-20 adresserte alle de alvorlige issuene fra forrige review (Samferdsel_96 status, scenario-overlapp, kapasitetsvariasjon, takt 350→300). To nye issues har dukket opp: (i) `solve_vektet` og `ekstraher_loesning` bruker ulike metoder for å beregne makespan og gir inkonsistente stdout/CSV-tall i "Not Solved"-tilfeller – dette er en kommunikasjonsrisk mot sensor; (ii) MIP-MC gir *verre* P95-varighet enn Heuristikk-MC i Basis_85, et interessant robusthetsfunn som bør fram i seksjon 9. I tillegg ble S1_Trondheim50+Samferdsel_96 kjørt i 8,4 timer uten å respektere tidsgrense – trolig bevisst forlengelse, men bør forklares. Alt annet er kosmetikk eller tidligere dokumenterte forenklinger. **Modellen er nå i god nok stand for innlevering**; det gjenstår ~1 time aktiv kode-/rapport-rydding.
