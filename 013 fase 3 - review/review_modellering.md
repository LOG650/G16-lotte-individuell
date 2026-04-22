# Review av modellering - LOG650 TVS-prosjekt

**Dato:** 2026-04-22
**Forfatter:** Uavhengig review (Claude-subagent)
**Omfang:** `heuristikk.py`, `mip_modell.py`, `monte_carlo.py`, `mip_kapasitet_sensitivitet.py`, `monte_carlo_mip.py`, `vask_og_strukturer.py` og tilhorende resultatfiler.
**Type:** Kritisk gjennomgang av modellens gyldighet, interne inkonsistenser og antakelser. Ikke kodestil.

---

## 1. Sammendrag

Modellpipelinen er teknisk korrekt og gir interne konsistente tall: heuristikk og MIP (vektet) loser begge optimerings- og simuleringsproblemet slik de er definert, og ekstraheringen av resultater er forsvarlig. **Det mest alvorlige funnet er en skjult overbruk av kapasitet paa ~13 %** (260/230-faktoren i heuristikken som MIP bevisst matcher), noe som systematisk presser alle varighetsestimater ned. I tillegg bygger alle timer-estimater paa en tidbruk-formel som ikke er identifiserbar fra kalibreringsdataene (allerede dokumentert i eksisterende valideringsnotat). Monte Carlo-implementasjonen er riktig bygget for de tre stokastiske kildene, men har flere dokumenterte **designvalg som bor rapporteres eksplisitt** - spesielt uavhengighetsantakelsen mellom MIN/KM og NVDB-takt, og 0,03-standardavviket paa automasjonsgrad.

---

## 2. Alvorlige funn

### 2.1 Skjult 13 % kapasitets-overbruk (260/230-faktoren)

**Fil:** `heuristikk.py:33-36, 154` og `mip_modell.py:40-46, 141-146`

Heuristikken bruker:
```python
dag_kap = Kapasitet_Ukesverk * 37.5 / 230
```
men simulerer med **260 arbeidsdager/ar** (mandag-fredag × 52 uker). Effektiv arlig kapasitet blir:

```
K * 37.5 * (260/230) = K * 42.39 timer/ar    (ikke K * 37.5 = K * 37.5 timer/ar)
```

Det er en bevisst **overbruk paa 13 % (260/230 = 1,130)** av den kapasiteten dataeierne oppga. MIP-modellen dokumenterer dette eksplisitt og velger aa matche heuristikken for sammenlignbarhet (`ARBEIDSDAGER_PER_KALENDERAAR=260` dividert paa `ARBEIDSDAGER_I_DATAFILEN=230`), men **begge modellene rapporterer dermed kortere varigheter enn det Kapasitet_Ukesverk faktisk tillater**.

Effekten er stor: ved nominell kapasitet (37,5 * K / 12 timer/mnd) er matematisk nedre grense 6,8 mnd for alle aktive kommuner samlet; med 260/230-overbruket 6,0 mnd. Paa Hamar (tightest hjemmekontor) er forskjellen 11,87 mnd vs 13,41 mnd.

**Anbefaling:** Dokumenter dette i rapportseksjon 5.1 (metode) og 9.0 (diskusjon) som et eksplisitt designvalg. Enten:
- (a) juster ARBEIDSDAGER_PER_AAR til 260 og fjern overbruket, eller
- (b) behold 230 som nominell referanse og forklar at "Kapasitet_Ukesverk tolkes som 'disponible ukesverk per ar ved 230 effektive arbeidsdager' - med 260 kalenderdager jobber kontorene effektivt 13 % mer enn oppgitt".

Alternativ (b) er mest trofast mot datakilden (`Kapasitet_Ukesverk` er oppgitt fra kontorene selv), men maa nevnes som forbehold ettersom det paavirker alle tall i rapporten.

### 2.2 Tidbruk-formelen er ikke identifiserbar (henvisning til V1)

**Fil:** `vask_og_strukturer.py:126, 490-501` og `validering_tidbruk_formel.md`

Formelen `Ber_Tidbruk_Min = Km_Kurve * 0,9035 + ArealLand_Km2 * 0,6510` er ikke OLS-regresjon paa kalibreringsdataene (alle 58 kartblader har identisk areal = 7,68 km²). Dette er **beskrevet grundig i det eksisterende valideringsnotatet** - jeg dupliserer ikke det her, men understreker at alle modelleringsresultater arver denne usikkerheten:

- Heuristikk/MIP-varigheter skalerer lineaert med formelen
- Monte Carlo bootstraper MIN/KM fra empirisk fordeling, men **holder areal-leddet (0,6510 * Areal) konstant** (`monte_carlo.py:46, 81`). Hvis areal-leddet er galt kalibrert, vil MC gi kunstig smal varighetsfordeling for kommuner som domineres av areal-leddet (typisk Molde/Vestland med store landkommuner og fa km TVS).

**Minimumsanbefaling:** Forbehold eksplisitt i seksjon 9.0. Vurder et sensitivitetsscenario der formelen skaleres med en kontor-spesifikk multiplikator mot kontorenes egne min/max-band (f.eks. scale_Molde slik at median treffer 40 timer, ikke 12).

### 2.3 S5_Alle_minus50 er ikke flagget korrekt i CSV

**Fil:** `mip_modell.py:519-537`

Upaalitelig-flagget settes kun naar `status_str != 'Optimal'` **OG** `kk_maks + 1 < min_kk_mnd * 0.9`. Men den rapporterte `Kartkontor_Siste_Mnd=11` i oppsummering_sensitivitet.csv tilsvarer 12 mnd, mens `Min_Kartkontor_Mnd=20`. Saa 12 < 20*0,9 = 18 er OPPFYLT og flagget settes til True - greit. Men i CSV rapporteres fortsatt `Makespan_Mnd=122/81/33` for de tre scenarioene som om de var gyldige. 

**Risiko:** Lesere av `oppsummering_sensitivitet.csv` som sorterer paa Makespan_Aar vil se at S5 har samme makespan som baseline, og kan feilaktig konkludere at "50 % kutt i kapasitet paavirker ikke makespan". Upaalitelig-kolonnen haandterer dette, men bare hvis man leser den aktivt. 

**Anbefaling:** I rapporten: ikke vis S5-tallet i samme tabell som S0-S4, men beskriv det i ren tekst som "ikke losbar innen solver-budsjett". Alternativt: erstatt tallene med `NaN` i oppsummeringsraden naar `Upaalitelig=True`.

---

## 3. Moderate funn

### 3.1 Monte Carlo: uavhengighet mellom MIN/KM og NVDB-takt

**Fil:** `monte_carlo.py:100-123`

De tre stokastiske kildene (MIN/KM, Manuell_Takt, Automasjonsgrad) samples uavhengig. I virkeligheten er det plausibelt at:
- **MIN/KM og manuell NVDB-takt er korrelert** (begge reflekterer "saksbehandlingshastighet" - personer som er raskt paa kartkontoret er trolig ogsaa raskt paa NVDB). Antakelsen om uavhengighet **undervurderer halene** (extrem-scenarioer der alle produktivitetsmal sklir i samme retning).
- **Automasjonsgrad er et policyvalg**, ikke en maaleusikkerhet — det er ingen empirisk fordeling for den. 0,03-standardavvik er et designvalg som bestemmer om scenariofordelingene overlapper (0,01 → ingen overlapp, 0,03 → overlapp).

Begge punkter **er** dokumentert i CLAUDE.md og kommentarer, men rapporten bor vaere eksplisitt:

> "Automasjonsgrad modelleres som Normal(scenariopunkt, 0,03) som en kalibrert proxy for epistemisk usikkerhet, ikke som maaleresultat fra en kjent fordeling."

### 3.2 MIP: "Kartkontor_Maks_Mnd=10" er 0-indeksert men tolkes ofte som antall maaneder

**Fil:** `mip_modell.py:494-500, 685-688`

Koden setter `ferdig_kk[i] = t` der `t` er 0-indeksert. I CSV og print heter kolonnen "Kartkontor_Siste_Mnd=10", men det tilsvarer **11 kalendermaaneder fra start** (april 2027). Heuristikken rapporterer "2027-09-03" for kartkontor-ferdig, som er 16 mnd fra 2026-05-01. 

MIP-tallet 11 mnd vs heuristikk 16 mnd **er** legitimt (MIP omfordeler fra Hamar vekk, heuristikk holder paa hjemmekontor), men **sammenligning maa gjoeres paa felles konvensjon**. CSV-kolonnen `Kartkontor_Maks_Mnd` bor enten navngis `Kartkontor_Maks_MndIdx` (0-indeks) eller konverteres til antall maaneder.

### 3.3 MIP-Monte Carlo-halen er bredere enn heuristikk-MC — ikke bug, men underkommunisert

**Fil:** `monte_carlo_mip.py` og `monte_carlo_mip_summary.csv`

Tallene i CSV:
- Basis_85: MIP P95 = 13,28 ar, heuristikk P95 = 11,98 ar (forskjell **1,3 ar**)
- Middels_90: identiske
- Samferdsel_96: MIP P5 = 1,0 ar, heuristikk = 1,32 ar

Jeg verifiserte per-iterasjon-distribusjonene (Basis_85):
- Heuristikk Varighet_Dager: mean 3594, std 647, max 4380
- MIP Varighet_Dager: mean 3658, std 744, **max 5464**

Kvartilene (Q1/Q3) er **identiske** — det er kun halen som skiller. Forklaringen "deterministisk optimum ≠ robust optimum" stemmer: MIP pakker kapasiteten tett, saa naar MIN/KM-bootstrap gir en "uheldig" iterasjon (mange hoye rater paa akkurat de kommunene MIP flyttet til Hamar), eksploderer varigheten. Hjemmekontor-tildelingen har mer slakk.

Dette er **et godt diskusjonspoeng**, ikke en bug. Men det forsvinner lett i tabellen hvis man bare sammenligner P5/P50/P95. **Anbefaling:** figur som viser CDF eller boxplot av Varighet_Dager for heuristikk-MC og MIP-MC side om side — halen er det interessante.

### 3.4 Heuristikkens sorteringslogikk er forsvarlig, men ikke bevisst optimal

**Fil:** `heuristikk.py:121-127`

Sorteringen er:
1. Ikke-last kommuner forst, sortert etter stoerste gjenvaerende timer (LPT — Longest Processing Time)
2. Laste kommuner til slutt, sortert etter tidligste opplaasning

LPT er en klassisk heuristikk for parallell scheduling og gir i verste fall 4/3-tilnaerming for makespan (Graham 1969) — **bor nevnes i seksjon 3 Teori eller 5.1 Metode** som teoretisk forankring. Uten denne referansen virker valget tilfeldig.

LPT er ikke garantert optimal naar jobber ogsaa har deadline-begrensninger (laaseperioder), men i praksis fungerer det fordi laste kommuner uansett havner "bakerst" i koen.

### 3.5 Heuristikken mangler reprioritering etter opplaasning

**Fil:** `heuristikk.py:129-131`

Koen sorteres **en gang** (ved start) og gaas gjennom lineaert. Naar en laast kommune blir opplaast midt i simuleringen, vurderes den ikke paa nytt mot andre gjenvaerende kommuner i koen — den staar bare lenger bak i den initielle sorteringen.

Dette **kan** gi suboptimal makespan hvis en stor kommune blir frigjort sent men fortsatt er den "tyngste" som gjenstaar. I praksis paavirker det lite fordi de fleste laaseperioder ender i desember 2026, mens simuleringen fortsetter i flere aar. Men bor nevnes som begrensning.

### 3.6 Ingen stokastikk paa laaseperioder eller kapasitet i MC

**Fil:** `monte_carlo.py` (hele filen)

MC varierer kun MIN/KM, Manuell_Takt og Automasjonsgrad. Følgende holdes **konstant** i alle 500 iterasjoner per scenario:
- Geovekst-laaseperioder (standardisert til mai-des 2026 ved ukjente)
- Kapasitet per kontor
- Fremdriftsstatus (62 ferdig, 48 paabegynt)
- Arealledd (0,6510 * Areal)

Dette er **et designvalg**, ikke en bug, men usikkerheten i estimatene er saa liten som den er **delvis fordi usikkerhetskildene er begrenset**. P95/P5 reflekterer kun stokastikk i 3 av mange mulige stokastiske dimensjoner. Bor rapporteres som begrensning i seksjon 9.

### 3.7 MIP: vektet objektiv har store tallverdier

**Fil:** `mip_modell.py:372-384`

```python
W2 = max(10 * max_inertia, 1000) * w2_scale     # ~2950 for 295 kommuner
W1 = max(10 * (W2 * max_kartkontor + max_inertia), 1e9)   # ~10^10
```

Med `total_timer ~ 6924` og `T=144`, blir `max_kartkontor = 997 056`, saa `W1 ≈ 10 * (2950 * 997 056 + 295) ≈ 2,94 * 10^10`. CBC haandterer dette greit i praksis (status Optimal for alle tre scenarioer etter kalibrering), men **numerisk stabilitet er en legitim bekymring**. Typiske tommelfingerregler anbefaler vektforhold under 10^6–10^7 for kommersielle solvere.

**Observasjon:** Lex-opt med to solver-runder (`solve_lex_opt`) er mer numerisk robust men tregere. Vektet-modus valgt for rapport-tabellen. Bor nevnes som implementasjonsvalg.

---

## 4. Mindre observasjoner

### 4.1 MAX_AAR cutoff

`heuristikk.py:38` setter `MAX_AAR=30`. Ingen av scenarioene kommer i naerheten, men hvis man kjorer S5_Alle_minus50 + Basis_85 i heuristikken (ikke i dagens pipeline), kunne man nadd cutoff. Greit for naa, men vaer oppmerksom.

### 4.2 Monte Carlo: sampled MIN/KM brukes per kommune IID

`monte_carlo.py:104`: `rng.choice(empirisk_mpk, size=n, replace=True)` — **iid bootstrap per kommune, ikke per region**. De 58 kartbladene har en Region-kolonne (se tidbruk_kalibrering.csv), men denne ignoreres. Hvis det er regionale forskjeller i produktivitet (snoerik i Nord-Norge → lavere takt enn Sorvest), vil iid-bootstrap undervurdere varians for regionale grupper. 

**Observasjon:** for 500 iterasjoner * 357 kommuner per iterasjon smoothes effekten ut — gjennomsnittstendenser er riktige. Men for per-kommune percentiler (`monte_carlo_per_kommune.csv`) kan tallene vaere feilkalibrerte for noen regionale kommuner. Lavt risiko.

### 4.3 fifo_nvdb_per_kommune tie-breaker

`mip_modell.py:448` — tie-breaker sorterer etter `(Ledig_Fra_Mnd, -Lenker, KomNr)`. Stoerste kommune foerst ved like maaneder. Dette **post-prosesserer** D_t-løsningen til en per-kommune-plan konsistent med aggregert drenering. Det er ikke en del av MIPens objektiv, men en rimelig FIFO-rekonstruksjon.

Merknad: hvis MIPen hadde modellert NVDB per kommune (med indekser i,t og kapasitetsbeskrankninger per kommune + D_it ≤ M * z_it-kobling), kunne man faatt en per-kommune plan direkte. Med dagens aggregerte D_t-variabel er FIFO et rimelig valg. Bor nevnes i seksjon 6 Modellering som "post-processing".

### 4.4 NVDB-regnestykke er konsistent

Verifisert:
- Basis_85: 150 / (1-0,85) = 1000 ✓
- Middels_90: 150 / (1-0,90) = 1500 ✓
- Samferdsel_96: 150 / (1-0,96) = 3750 ✓

Og forholdet 10,17 / 6,75 = 1,506 ≈ 1500/1000 = 1,5 (Middels_90 vs Basis_85). For Samferdsel_96: 10,17 / 2,75 = 3,70 ≈ 3750/1000 = 3,75 — avvik skyldes pre-ferdig-kommuner og kartkontor-flaskehals. Konsistent.

### 4.5 ArbeidsdagerPerMND = 260/12 = 21,67

`mip_modell.py:46` gir 21,67 arbeidsdager/mnd. Empirisk varierer dette fra 19 (februar 2026: 20 dager) til 23 (august 2026: 21 dager) mnd-for-mnd. Gjennomsnittsverdien paaloegger ingen modellfeil, men hvis en laaseperiode paa f.eks. juli 2026 ville blokkert ~21 reelle dager, tildeler MIP 21,67 ikke-tilgjengelige dager. Minimalt.

### 4.6 Heuristikk bygger NVDB-koe i rekkefoelge kommunene blir ferdig paa kartkontor

`heuristikk.py:222` — `nvdb_ko.append(k)` naar kommunen blir ferdig. Dette er implisitt FCFS: store kommuner som tar tid paa kartkontor havner sent i NVDB-koen, og deres overforing blir flyttet til slutten. **Bor dokumenteres** som antakelse. Samferdselsavdelingen kunne teoretisk prioritere store kommuner foerst (skjedulering i NVDB er utenfor prosjektets scope, antatt FCFS).

### 4.7 NVDB-"drenering" i MIP: C9-beskrankningen

`mip_modell.py:248-254`:
```python
sum(D[s] for s <= t) <= L_preklar + sum(lenker_i[i] * z[(i, t)] for i in I)
```

Merknad: begrensningen bruker `z[(i, t)]` (ikke `z[(i, s)]`) paa hoeyre side. Siden z er monoton (C7), betyr dette at hoyre side = kumulativ mengde tilgjengelig per maaned t. Korrekt formulert.

---

## 5. Anbefalinger for rapporten (seksjon 9 Diskusjon)

### 5.1 Kjerneforbehold som bor loftes frem

1. **Kapasitets-overbruket 260/230:** Diskuter eksplisitt at heuristikk og MIP begge simulerer 13 % mer effektiv kapasitet enn nominell Kapasitet_Ukesverk. Enten juster modellen, eller dokumenter og motivater valget.
2. **Tidbruk-formelen:** Legg valideringsnotatets V1 og V2 som forbehold. Ber_Tidbruk_Min underestimerer mot 8/10 kontorers eget min/max-band. Scale-opp med faktor 2 er en plausibel sensitivitet.
3. **S5 er upaalitelig:** Dokumenter at makespan-tallene for S5_Alle_minus50 i `oppsummering_sensitivitet.csv` er LP-relaxation-verdier fra en Not Solved solver — vis dem som illustrasjon paa regimeskifte, ikke som gyldige resultater.

### 5.2 Modellspesifikke forbehold

4. **Uavhengighet mellom stokastiske kilder:** Rapporter eksplisitt at MIN/KM, Manuell_Takt og Automasjonsgrad samples uavhengig — den reelle fordelingen kan ha korrelasjon som gir bredere haler.
5. **0,03-std paa automasjonsgrad:** Ikke skjul at dette er et designvalg, ikke en empirisk fordeling. Sensitivitet mot STD=0,01, 0,02, 0,05 kunne vaere nyttig.
6. **Aggregert NVDB:** NVDB modelleres som D_t (totale lenker per mnd), ikke per kommune. FIFO-rekonstruksjon er en forenkling; i praksis kan samferdselsavdelingen prioritere annerledes.
7. **Deterministisk optimum ≠ robust optimum:** MIP-tildeling har bredere halen enn hjemmekontor-tildeling i MC. Legitim innsikt — ikke begrav i tabell, vis eksplisitt.

### 5.3 Modellstyrker som bor nevnes balansert

- Heuristikken og MIPen er **konsistente** (MIP forbedrer heuristikken med <2,2 % paa makespan — bekrefter at hjemmekontor-tildelingen er naer optimal).
- MIP verifiserer at **NVDB er flaskehalsen** i alle kapasitetsregimer inntil S4/S5 (kartkontor-delen ferdig innen ~11 mnd i MIP).
- Monte Carlo-motoren haandterer forward-filling korrekt og unngaar bias i halen.
- Lex-opt-mode gir alternativ verifisering av vektet-modus.

### 5.4 Ting som ikke er bekreftet og bor kanskje sjekkes

- **Heuristikkens re-sortering av kø** etter laaseperiode-slutt er ikke implementert. Effekten er sannsynligvis liten, men kunne kjores som sanity-check.
- **Kolonnen `Kartkontor_Maks_Mnd`** i MIP-output er 0-indeksert; kan forvirre lesere som tolker det som antall maaneder.
- **Solver-tid 2724 s for S5+Basis_85** tyder paa at modellen er **paa grensen av CBCs evne**. Kommersielle solvere (Gurobi/CPLEX) ville trolig loest S5 uten problem, men det er utenfor dagens budsjett.

---

## 6. Oppsummering per spesifikk sporsmaal fra oppdragsgiver

### 6.1 Heuristikken
- Sorteringslogikken er fornuftig (LPT + laste-til-bakerst + tidligste-opplaasning-forst). **Bor refereres som LPT-heuristikk** i rapporten.
- Kapasitetsbegrensning er implementert **per dag** (budsjett per kontor = K * 37,5 / 230), ikke per uke/aar. Korrekt tolkning av dag-for-dag.
- Laaseperioder korrekt implementert — kommuner i en laaseperiode hoppes over inntil de er fri. Intervallvis sjekk per dag (`er_laast`).
- **Ja**, Kapasitet_Ukesverk brukes som aarlig kapasitet som implisitt "resettes" hvert ar (arbeidstimer forsvinner per dag, ikke akkumuleres). Men: overbruket 260/230 gir 13 % hoyere effektiv kapasitet enn oppgitt — se 2.1.

### 6.2 MIP-modellen
- Tid-diskretiseringen (21,67 arbeidsdager/mnd) **er konsistent med heuristikken ved design** (begge bruker 260/230-konvensjonen). Arv av 2.1.
- `Q_t` er korrekt formulert for makespan (lineaer big-M paa gjenstaaende lenker, monoton).
- Vektet malfunksjon med W1=10^10 og W2=10^3 fungerer empirisk, men er paa grensen av numerisk stabilitet. Lex-opt som alternativ er robustere.
- S5 feiler fordi horisonten T fra baseline (144/81/33 mnd) er for kort for halvert kapasitet — minimum kartkontor-tid skalerer til 20 mnd, og solver stopper paa LP-relaxation. Upaalitelig-flagget er korrekt sett, men CSV rapporterer fortsatt Makespan_Aar-tallene (se 2.3).

### 6.3 Monte Carlo
- Tre kilder er samples uavhengig — uavhengighetsantakelsen er **rimelig men diskutabel** (se 3.1).
- iid bootstrap av MIN/KM per kommune **ignorerer Region-info**. Lavt risiko for globale tall, hoyere risiko for per-kommune-tall (se 4.2).
- AUTOMASJON_STD=0,03 er **et designvalg**, ikke empirisk begrunnet (se 3.1). Gir realistisk overlapp mellom scenarioer, men bor ikke presenteres som "maaleusikkerhet".
- MIP-MC gir hoyere P95 enn heuristikk-MC fordi MIP-tildelingen er tettere pakket. **Ikke en bug, legitim innsikt** (se 3.3).

### 6.4 Tidbruk-formelen
- Allerede dokumentert i valideringsnotatet V1-V3. Primaer bekymring: formelen kan underestimere med faktor ~2 mot kontorenes egne min/max-band (Molde 0 % innenfor).
- ArealLand-leddet er **ikke identifiserbart** fra 58 kartblader med identisk areal. Reell koeffisient kan vaere vesentlig forskjellig fra 0,6510.
- MC bootstraper kun MIN/KM — areal-leddet er deterministisk. Gir kunstig naerhet for areal-dominerte kommuner.

### 6.5 Konsistens mellom scenarioene
- Verifisert: 1000 / 1500 / 3750 lenker/dag matcher 85 % / 90 % / 96 % automasjon med 150 lenker/dag manuelt.
- Forholdene 10,17 / 6,75 / 2,75 ar stemmer innenfor pre-ferdig-kommuner og kartkontor-begrensning. Konsistent.

### 6.6 Metodologiske svakheter som bor nevnes
- Maanedlig (MIP) vs daglig (heuristikk) tidsopploesning - forklarer <2,2 % avvik
- Ingen stokastikk paa laaseperioder (kan glippe)
- Ingen stokastikk paa kapasitet (personell-tilgang varierer aar for aar)
- NVDB aggregert, ikke per kommune (FIFO-post-processing)
- LPT-heuristikk uten re-sortering
- Kapasitetsoverbruk 260/230 (skjult 13 %)
- Tidbruk-formelen er ikke validert i kalibreringsdatasettet

---

## Avsluttende bemerkning

Modellen er **teknisk solid og velimplementert**. De fleste funnene over er **forbehold som bor dokumenteres**, ikke feil som maa rettes — med unntak av (2.3) S5-haandtering i CSV, som er mer et rapporteringsvalg enn en kodefeil. Den faktiske kvantitative usikkerheten er sannsynligvis vesentlig stoerre enn P5-P95-intervallene antyder, primaert pga tidbruk-formelens skalering (faktor ~2 mulig underestimering) og uavhengighetsantakelsen i MC.

Anbefalt rekkefoelge for seksjon 9:
1. Tidbruk-formelens identifiserbarhet (arv fra valideringsnotat)
2. Kapasitetsoverbruket 260/230
3. Deterministisk vs robust optimum (MIP-MC)
4. Stokastiske kilders uavhengighet
5. Aggregert NVDB-modellering
