# Reviewrapport – modellering LOG650 (kritisk gjennomgang)

**Dato:** 2026-04-20
**Omfang:** `heuristikk.py`, `monte_carlo.py`, `mip_modell.py`, `mip_kapasitet_sensitivitet.py`, `monte_carlo_mip.py` + utvalgte output-CSV-filer.
**Formål:** Identifisere svakheter, antagelser som bør gjøres eksplisitte, og risikopunkter i modellene før skriving av rapportseksjon 9 (diskusjon).

Issuene er sortert etter alvorlighet. Hver har en **anbefaling** til hva som bør gjøres før innlevering.

---

## 1. Alvorlige funn (må adresseres)

### 1.1 MIP gir systematisk *verre* makespan enn heuristikken

| Scenario | Heuristikk | MIP (vektet) | Differanse |
|---|---|---|---|
| Basis_85 | 8,64 år | 8,75 år | **+0,11 år (−1,3 %)** |
| Middels_90 | 5,76 år | 5,83 år | **+0,07 år (−1,2 %)** |
| Samferdsel_96 | 2,31 år | 2,33 år | **+0,02 år (−0,9 %)** |

Dette er et validitetsproblem, ikke bare et dokumentasjonspoeng. En "optimeringsmodell" som gir dårligere verdi enn heuristikken på selve målfunksjonen svekker narrativet "MIP forbedrer baseline".

Forklaringen i CLAUDE.md – månedlig vs. daglig tidsoppløsning – er trolig riktig, men bør verifiseres eksplisitt: dersom MIP-løsningen mappes tilbake til daglig simulering, er den da minst like god som heuristikken? Hvis ja, er forskjellen ren diskretiseringsfeil. Hvis nei, er det en reell modell-feil.

**Anbefaling:**
- Implementer en liten verifisering: ta MIP-assignment, kjør gjennom `heuristikk.py`s daglige simulator (slik `monte_carlo_mip.py` allerede gjør med gjennomsnittsparametre), og rapporter makespan. Er den ≤ heuristikkens, er saken klar.
- Reframe MIP-bidraget i rapporten: **MIP er en bekreftelse på at heuristikken er nær optimal**, ikke en forbedring. Det er i seg selv et sterkt funn og bør løftes fram som hovedbidraget fra MIP-delen.

### 1.2 `Samferdsel_96` har status `Not Solved` – krever forklaring

`oppsummering_mip_vektet.csv` viser status `Not Solved` for Samferdsel_96 med 1203 s solver-tid (grense 1800 s). Makespan 28 mnd er rapportert uansett.

CBC kan returnere status `Not Solved` selv med en gyldig heltalls-løsning; da er resultatet en *feasible* løsning, ikke beviselig optimal. Rapporten må klargjøre:
- Er 28 mnd en øvre grense (beviselig nedre grense er noe mindre)?
- Hva er MIP-gapet CBC rapporterer?

**Anbefaling:**
- Kjør Samferdsel_96 på nytt med `msg=True` og noter `gapRel`/bestBound-verdi fra CBC-loggen.
- I rapporten: oppgi eksplisitt at løsningen er `feasible` med gap X %, ikke "optimal".

### 1.3 Kapasitetskonvensjonen `37,5 / 230` gir systematisk overbruk

Heuristikken setter:

```
daglig_kap = Kapasitet_Ukesverk × 37,5 / 230
```

og kjører simuleringen mandag–fredag, dvs. ~260 arbeidsdager/år. Effektiv årlig kapasitet blir dermed `ukesverk × 37,5 × 260/230 ≈ ukesverk × 42,4` – altså ~13 % høyere enn de oppgitte `ukesverk × 37,5`. MIP matcher dette bevisst (kommentert i koden), så heuristikk–MIP-sammenligningen er rettferdig, men *absolutt* varighet er systematisk underestimert med ~13 %.

Dette er en **modellparameter som må forsvares** i rapporten – det er lett for en sensor å se dette.

**Anbefaling:**
- Velg én konvensjon og forsvar den:
  - Opprinnelig intensjon: 230 arbeidsdager/år (ferier, sykefravær, annet arbeid). Da må simuleringen også bruke 230 dager, ikke 260. Enkleste fiks: skipp én arbeidsdag per 11. dag, eller multipliser ukentlig_kontor-kapasitet med 230/260.
  - Alternativ: bruk 260 dager konsistent og reduser oppgitt kapasitet med en tilgjengelighetsfaktor.
- Diskuter valget i seksjon 6 (modellering). Anerkjenn at totalvarigheten hadde blitt ~1 år lengre i Basis_85 med 230 dager, men at *relative* resultater mellom scenarioene er robuste.

### 1.4 NVDB-throughput-formelen er følsom nær `automasjon = 1`

Formelen `Total_Throughput = Manuell_Kap / (1 − Automasjon)` er en implisitt antagelse om at FME har ubegrenset kapasitet og at manuell etterbehandling er den eneste flaskehalsen. Konsekvenser:

- Ved 85 %: 175 / 0,15 = 1167 lenker/dag
- Ved 90 %: 175 / 0,10 = 1750 lenker/dag (+50 %)
- Ved 96 %: 175 / 0,04 = 4375 lenker/dag (+150 % fra 90 %)
- Ved 99 %: 175 / 0,01 = 17 500 lenker/dag (+300 % fra 96 %)

Formelen divergerer ved automasjon → 1. Dermed blir konklusjonen "automasjonsgrad er dominerende usikkerhetskilde" *analytisk nødvendig*, ikke empirisk funnet. Monte Carlo-studien samples rundt scenariopunktene med kun 0,01 std, så divergensen er lokalt dempet, men følsomheten øker raskt.

**Anbefaling:**
- Diskuter formelens struktur eksplisitt i seksjon 5.1 (metode). Avklar: Antas FME virkelig grenseløst? I virkeligheten har FME også grenser (maskinressurs, vedlikehold, sanity-sjekk etter kjøring).
- Overvei en alternativ modell: `Throughput = min(FME_kap, Manuell_Kap / (1 − auto))`, med en oppgitt eller estimert øvre grense for FME.
- Kontroller CLAUDE.md-avklaringen: produksjonstakten 300–400 lenker/person/dag refererer til manuell QA eller kombinert? Dette påvirker tolkningen av formelen.

### 1.5 `S2_Alle_pluss20` mangler fra `oppsummering_sensitivitet.csv`

Definert i `mip_kapasitet_sensitivitet.py` (linje 44–47), men er ikke i output. Sannsynlig solver-timeout eller manuelt slettet. Enten kjør den på nytt, eller fjern varianten fra rapporten og forklar hvorfor.

**Anbefaling:** Kjør S2 på nytt med lengre tidsgrense (`--tidsgrense 3600`) eller fjern den fra beskrivelsen i CLAUDE.md/rapporten.

### 1.6 Kapasitets-sensitivitet viser ingen varians i makespan

Alle fire varianter som *er* rapportert gir **identisk** makespan per NVDB-scenario (105 / 70 / 28 mnd). Kun antall omfordelinger varierer.

Det er konsistent med at NVDB er flaskehalsen – men da sier sensitivitetsstudien egentlig bare "kartkontor-kapasitet har ingenting å si for totalvarighet". Det er et funn i seg selv, men bruken av en kostbar 4×3 MIP-kjøring for å dokumentere det er ineffektiv, og risikerer å se ut som "modellen er ikke sensitiv".

**Anbefaling:**
- I seksjon 7/8 (analyse/resultat): løft fram dette som et *konklusjonspunkt*, ikke en svakhet ("Kartkontor-fasen er robust mot rimelige kapasitetsforstyrrelser – flaskehalsen er NVDB, ikke kartkontorene"). Støtt med kartkontor-makespan (`Kartkontor_Siste_Mnd = 10`), som *også* er konstant.
- Legg til én ekstrem variant for å vise at modellen *kan* bli bundet av kartkontor – f.eks. `S5_Alle_minus50`. Hvis kartkontor-makespan plutselig stiger til f.eks. 20+ mnd og begynner å dominere over NVDB, blir poenget skarpere.

---

## 2. Viktige funn (bør adresseres)

### 2.1 Bootstrap av MIN/KM er uten korrelasjon – overdriver heterogenitet

I `monte_carlo.py` trekkes 357 MIN/KM-verdier uavhengig fra 58 kartblader. I virkeligheten er MIN/KM *geografisk korrelert* (topografi, terreng, veitype). Uavhengige trekninger gir:
- Antakelig realistisk total-varighet (loven om store tall jevner ut)
- Men underestimert spredning på kontor-nivå (variansen blir for liten fordi nabokommuner får uavhengige verdier)

Grunnpakken (0,6510 min/km²) holdes konstant. Dette er inkonsistent – hvis MIN/KM har så stor spredning (range 0,10–3,44), burde man forvente at grunnpakken også har usikkerhet.

**Anbefaling:**
- Behold dagens modell, men diskuter dette i rapportens usikkerhetsdrøfting. Skriv f.eks.: "Bootstrap-strategien antar uavhengighet mellom kommuner; reell geografisk korrelasjon ville gitt bredere per-kontor-fordelinger men lignende total."
- Evt. sensitivitet: kjør én variant med regional klynging (bruk `Region`-kolonnen i `tidbruk_kalibrering.csv`).

### 2.2 Per-kommune MIN/KM-tilordning fra kartblad-nivå er diskutabel

58 kartblader er *ikke* 58 kommuner. Et kartblad dekker geografiske områder, og en kommune kan overlappe flere kartblader. Når Monte Carlo tildeler én MIN/KM per kommune, tildeler man egentlig én kartblad-representativ verdi.

Dette forstørrer variasjonen for store kommuner (som dekker flere kartblad-typer) og undervurderer utjevning innad i store kommuner.

**Anbefaling:** Legg til en kort drøftingssetning om at MIN/KM-variansen er "kartblad-nivå-varians", og at per-kommune-varians i virkeligheten er lavere på grunn av intern utjevning. Dette strammer inn tolkningen av P5/P95-intervallene.

### 2.3 Monte Carlo-scenarioene overlapper ikke – av *designvalg*, ikke empirisk funn

P95 av Samferdsel_96 (3,22 år) < P5 av Middels_90 (4,54 år). CLAUDE.md kaller dette et "nøkkelfunn", men det er en direkte konsekvens av at automasjon samples med std=0,01 rundt scenariopunkter som er 5–6 prosentpoeng fra hverandre.

Sagt annerledes: hvis `AUTOMASJON_STD` hadde vært 0,03 i stedet for 0,01, ville fordelingene overlappet markant. Valget 0,01 er ikke begrunnet i rådata.

**Anbefaling:**
- Grunngi `AUTOMASJON_STD = 0,01` i rapporten (hvorfor akkurat denne verdien?), eller endre den til noe mer defensibelt (f.eks. basert på en antatt måleusikkerhet på ±3 prosentpoeng på FME-automasjonsgrad).
- Reformuler "nøkkelfunn" til: "Under antagelsen om liten usikkerhet innen hvert scenario (std=0,01), overlapper fordelingene ikke. Dermed fanger *scenarioer* (ikke usikkerhetsintervaller) den viktigste variasjonen."

### 2.4 Heuristikkens prioritetsregel evaluerer kun på STARTDATO

`bygg_koer()` setter sorteringsnøkkel basert på låsestatus *på 2026-05-01*. En kommune som låses opp 2026-09-01 plasseres før en som låses opp 2026-06-01 hvis førstnevnte har flere `gjenvaerende_timer`. Videre: rekkefølgen revurderes ikke når låsninger utløper – kommuner tas i fast rekkefølge etter at køen er bygget, uavhengig av om senere opplåsninger kunne gitt bedre flyt.

Dette er en klassisk myopisk heuristikk og er dokumentert, men det er en antagelse som bør nevnes.

**Anbefaling:**
- I seksjon 6 (modellering): nevn eksplisitt at prioritetsrekkefølgen fastsettes *én gang ved start* og at dynamisk omprioritering (gjen-sortering etter opplåsning) er utelatt som forenkling.
- MIP-modellen gjør *ikke* denne forenklingen – den ser over hele horisonten. Dette er et argument for at MIP *burde* slå heuristikken, og kontrasten med funn 1.1 (MIP er marginalt verre) underbygger hypotesen om at forskjellen er diskretiseringsfeil, ikke modell-feil.

### 2.5 Inertia-termens dominans i vektet MIP

I `solve_vektet` er vektene satt til `W1 = max(10·(W2·max_kk + max_inertia), 1e9)` og `W2 = max(10·max_inertia, 1000)`. Det sikrer leksikografisk prioritering, men det betyr også at *hele* løsningen styres av lexordering – makespan → kartkontor-ferdigtid → inertia.

Resultatet: 59 omfordelinger i Basis_85 og Middels_90, 31 i Samferdsel_96. Disse omfordelingene endrer *ikke* makespan (se 1.1), men forbedrer kartkontor-ferdigtid (median 3 mnd, maks 10 mnd). De er altså drevet av prioritering 2, ikke 1.

**Spørsmål det bør kunne besvares i rapporten:**
- Hvorfor 59 omfordelinger? Dette er 20 % av aktive kommuner. Er det *nødvendig* for kartkontor-ferdigtid, eller kunne W2 vært satt lavere for å gi en mindre aggressiv løsning?
- Hva er den politiske/organisatoriske kostnaden av 59 omfordelinger? Modellen gir det "gratis".

**Anbefaling:** Rapporter en ekstra variant der inertia-vekten er mye høyere (f.eks. `W2 = 1`), og sammenlign makespan/kartkontor-ferdigtid/omfordelingsantall. Hvis makespan holder seg ved få omfordelinger, er det et praktisk funn.

### 2.6 FIFO-prioritering i NVDB-køen alfabetisk ved like `Ledig_Fra_Mnd`

`fifo_nvdb_per_kommune` sorterer etter `(Ledig_Fra_Mnd, KomNr)`. Når flere kommuner blir ferdig samme måned, tas de alfabetisk etter kommunenummer. Det er vilkårlig, og kan gi uheldige rekkefølger (små kommuner med lave nummer tas først fremfor store).

Heuristikken bruker en annen regel (rekkefølgen de ble ferdig i kartkontor-steget, med intra-dags spillover). Dette skaper en mulig asymmetri i hvordan MIP og heuristikk fordeler NVDB-kapasiteten.

**Anbefaling:** Enten dokumenter at forskjellen er neglisjerbar (sjekk med en sensitivitetstest), eller bruk samme tie-breaker i begge (f.eks. størrelse først, så KomNr).

---

## 3. Mindre funn (dokumentér eller ignorer)

### 3.1 Ingen validering av `Ber_Tidbruk_Min`-formelen mot 62 ferdige kommuner

CLAUDE.md beskriver at de 62 ferdige kommunene "skal brukes til sanity-check". Fant ingen kode som gjør dette. Datapunkt: hvis faktisk tidsbruk på de 62 ferdige er tilgjengelig, hadde det vært en sterk validering av hele tidsbruksmodellen.

Hvis data ikke finnes, skriv det i rapporten: "Validering mot ferdig-kommuner krevde faktisk-tidsbruk-registrering som ikke er tilgjengelig i Kartverkets systemer."

### 3.2 NVDB-kapasitet konstant hele horisonten

Ingen modellering av ferier, opplæring, opprampning, eller reduksjon når "restkø" har spesialtilfeller. Rimelig forenkling, men nevn den.

### 3.3 `nvdb_overfoering.csv` og Monte Carlo bruker *samme* formel

`Total_Throughput = 0,5 × Manuell × 1/(1 − auto)` er hardkodet både i `nvdb_overfoering.csv` (via forhåndsutregnede verdier 1167/1750/4375) og i `monte_carlo.py` (via `sample_nvdb_params`). En endring av formelen må gjøres på to steder. Lav risk, men dokumenter at formelen er en "single source of truth" i kode.

### 3.4 Heuristikkens cutoff på 12 år (`MAX_AAR = 12`)

Hardkodet i `heuristikk.py`. Basis_85 gir 8,64 år, Monte Carlo P95 10,17 år. Det er komfortabel margin, men hvis scenarioer endres (f.eks. lavere automasjon enn 85 %), kan cutoff klippe. Bruk heller dynamisk grense basert på scenarioet, eller advar tydelig hvis cutoff aktiveres.

### 3.5 `monte_carlo_mip.py` returnerer *identiske* resultater som `monte_carlo.py` for makespan

Siden MIP-assignment ikke endrer *når* kommuner blir ferdig på kartkontor (kartkontor-makespan stabilt ~488 dager i begge), og NVDB er eneste flaskehals, er `monte_carlo_mip`s resultater antakelig numerisk nesten identiske med `monte_carlo`s. Hvis det er tilfelle, er merverdien minimal.

**Anbefaling:** Bekreft ved å kjøre begge og sammenligne summary. Hvis identiske, drop `monte_carlo_mip` fra rapporten eller bruk det kun som en ekstra sanity-check.

### 3.6 Inkonsistent norsk/bokmål i stdout-meldinger

Blandede meldinger ("maaneder", "aar", "loesning"). Kosmetisk, påvirker ikke vitenskapelig validitet.

---

## 4. Styrker ved modelleringen

For balansens skyld – ting som er gjort godt:

- **Klar separasjon** mellom simulering (heuristikk), optimering (MIP) og usikkerhet (Monte Carlo). God arkitektur.
- **MIP-modellen er lesbar og korrekt formulert.** Q-reformulering av makespan er en standard teknikk, og monotoni-begrensningene (C7, C12) er riktig.
- **Tre solve-moduser** (makespan/lex/vektet) med klar dokumentasjon av avveiningene.
- **Monte Carlo med 3 stokastiske kilder** og bootstrap på rekte empirisk fordeling viser metodisk bevissthet.
- **Scenario-struktur** (Basis/Middels/Samferdsel) er godt gjennomtenkt, og Samferdsel_96 sin bakoverregning fra samferdselsavdelingens anslag er en fin metodisk grep.
- **Forward-fill i aggregering av ukentlige percentiler** (`aggreger_uke_percentiler`) er et detaljert, korrekt grep som mange glemmer.

---

## 5. Prioritert oppfølging før 29.04

Rangert etter hva som vil bedre rapportens robusthet med minst mulig innsats:

1. **Kjør Samferdsel_96 MIP på nytt med synlig solver-output** for å dokumentere gap (≤1 t arbeid). Fiksjer 1.2.
2. **Skriv inn kapasitet/260-vs-230-diskusjonen** i seksjon 6 (≤30 min). Fiksjer 1.3.
3. **Reframe MIP-bidraget** fra "forbedring" til "bekreftelse på heuristikkens nær-optimalitet" i seksjon 8/9 (≤1 t). Fiksjer 1.1.
4. **Forklar `AUTOMASJON_STD = 0,01`-valget** og NVDB-formelens divergens i seksjon 5.1 (≤30 min). Fiksjer 1.4 og 2.3.
5. **Kjør eller fjern S2_Alle_pluss20** (1–2 t avhengig av solver-tid). Fiksjer 1.5.
6. **Diskusjon av bootstrap-antagelser** i seksjon 9 (≤30 min). Fiksjer 2.1, 2.2.
7. **Sjekk om `monte_carlo_mip` gir ny informasjon** (≤30 min). Fiksjer 3.5.

Estimert total: **4–6 timer arbeid** for å lukke de alvorlige og viktige issuene uten ny kode.

---

## Oppsummering i ett avsnitt

Modelleringsrammeverket er metodisk solid og godt implementert. De største risikoene i rapporten er: (i) å selge MIP som "forbedring" når den marginalt er verre enn heuristikken på makespan, (ii) ikke forsvare 230-dagers-konvensjonen, (iii) ikke diskutere at Monte Carlo-konklusjonen "ingen overlapp mellom scenarioer" er designvalg snarere enn empirisk funn, og (iv) ikke forklare `Not Solved`-status for Samferdsel_96. Alle fire kan håndteres med 4–6 timers reformulering og én solver-rekjøring, uten ny modellering.
