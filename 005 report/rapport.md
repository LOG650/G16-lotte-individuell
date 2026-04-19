# Kvalitetsheving av FKB-TraktorvegSti før implementering i NVDB

**Forfatter:** Lotte Picard

**Studiepoeng:**

**Veileder:**

**Antall sider:**

**Antall ord:**

Molde, innleveringsdato

---

## Obligatorisk egenerklæring

Den enkelte student er selv ansvarlig for å sette seg inn i hva som er lovlige hjelpemidler, retningslinjer for bruk av disse og regler om kildebruk. Erklæringen skal bevisstgjøre studentene på deres ansvar og hvilke konsekvenser fusk kan medføre. Manglende erklæring fritar ikke studentene fra sitt ansvar.

### Personvern

Har oppgaven vært vurdert av NSD? Nei

Jeg erklærer at oppgaven ikke omfattes av Personopplysningsloven.

### Helseforskningsloven

Har oppgaven vært til behandling hos REK? Nei

### Publiseringsavtale

Forfatter(ne) har opphavsrett til oppgaven. Det betyr blant annet enerett til å gjøre verket tilgjengelig for allmennheten (Åndsverkloven. §2). Alle oppgaver som fyller kriteriene vil bli registrert og publisert i Brage HiM med forfatter(ne)s godkjennelse.

Jeg gir herved Høgskolen i Molde en vederlagsfri rett til å gjøre oppgaven tilgjengelig for elektronisk publisering: ja/nei

Er oppgaven båndlagt (konfidensiell)? ja/nei

---

## Sammendrag



---

## Abstract



---

## Innhold

- [1.0 Innledning](#10-innledning)
  - [1.1 Problemstilling](#11-problemstilling)
  - [1.2 Delproblemer](#12-delproblemer)
  - [1.3 Avgrensinger](#13-avgrensinger)
  - [1.4 Antagelser](#14-antagelser)
- [2.0 Litteratur](#20-litteratur)
- [3.0 Teori](#30-teori)
- [4.0 Casebeskrivelse](#40-casebeskrivelse)
- [5.0 Metode og data](#50-metode-og-data)
  - [5.1 Metode](#51-metode)
  - [5.2 Data](#52-data)
- [6.0 Modellering](#60-modellering)
- [7.0 Analyse](#70-analyse)
- [8.0 Resultat](#80-resultat)
- [9.0 Diskusjon](#90-diskusjon)
- [10.0 Konklusjon](#100-konklusjon)
- [11.0 Bibliografi](#110-bibliografi)
- [12.0 Vedlegg](#120-vedlegg)

---

# 1.0 Innledning



## 1.1 Problemstilling



## 1.2 Delproblemer



## 1.3 Avgrensinger



## 1.4 Antagelser



---

# 2.0 Litteratur

Problemstillingen i denne oppgaven kombinerer flere etablerte fagområder: ressursallokering og scheduling med tidsvinduer, hybride løsningsmetoder som kombinerer heuristikk og eksakt optimering, samt usikkerhetsanalyse basert på Monte Carlo-simulering og bootstrap. Dette kapittelet presenterer sentrale referanser som danner det metodiske grunnlaget for analysen.

## 2.1 Scheduling og ressursallokering med tidsvinduer

Pinedo (2016) er et standardverk innen scheduling-teori og dekker både klassiske formuleringer – parallelle maskiner, release- og due-datoer – og utvidelser som tidsvinduer og ressursbegrensninger. Verket gir det teoretiske rammeverket for å formulere TraktorvegSti-problemet som et ressursallokerings- og sekvenseringsproblem der de 10 kartkontorene tilsvarer parallelle ressurser med varierende kapasitet.

Hartmann og Briskorn (2010) gir en oversiktsartikkel over det ressursbegrensede prosjektplanleggingsproblemet (Resource-Constrained Project Scheduling Problem, RCPSP) og dets utvidelser. Artikkelen etablerer en klassifikasjon som er direkte overførbar til Kartverkets problemstilling: kommuner som aktiviteter, kartkontor som ressurser, Geovekst-låsninger som tidsvinduer, og NVDB-overføringen som en nedstrøms kapasitetsbegrensning.

## 2.2 Hybride løsningsmetoder

Puchinger og Raidl (2005) presenterer en taksonomi over kombinasjoner av metaheuristikker og eksakte algoritmer i kombinatorisk optimering. Forfatterne beskriver ulike måter heuristiske og eksakte metoder kan utfylle hverandre, for eksempel ved at en heuristikk genererer en baseline-løsning som videre forbedres av en eksakt metode. Denne tilnærmingen ligger til grunn for metodevalget i oppgaven, der en regelbasert heuristikk gir en baseline som sammenlignes med en MIP-modell med full omfordelingsfrihet.

## 2.3 Monte Carlo-simulering og usikkerhetsanalyse

Vose (2008) er et bredt brukt standardverk for kvantitativ risikoanalyse og dekker Monte Carlo-metoden anvendt i planleggingskontekst. Boken omhandler valg av sannsynlighetsfordelinger, sampling-strategier, hensiktsmessig antall iterasjoner, samt tolkning av persentiler og konfidensintervall – alle aspekter som er relevante for usikkerhetsanalysen i denne oppgaven.

## 2.4 Bootstrap og empirisk resampling

Efron og Tibshirani (1993) presenterer bootstrap-metoden som en statistisk teknikk for å estimere usikkerhet basert på empiriske fordelinger. Verket begrunner resampling med tilbakelegging som en gyldig metode når underliggende sannsynlighetsfordeling er ukjent. I denne oppgaven anvendes prinsippet ved å trekke verdier for tidsbruk per kilometer TVS-lenke fra en empirisk fordeling basert på 58 historiske kartbladmålinger, heller enn å forutsette en parametrisk fordelingsform.

---

# 3.0 Teori



---

# 4.0 Casebeskrivelse

## 4.1 FKB-TraktorvegSti og kvalitetsheving

FKB-TraktorvegSti (TVS) er et nasjonalt datasett som inneholder traktorveger og stier i hele Norge. Datasettet forvaltes av Statens Kartverk og er en del av Felles Kartdatabase (FKB). Etter kvalitetsheving skal datasettet implementeres i NVDB (Nasjonal vegdatabank), slik at traktorveger og stier inngår sammen med øvrige veger i et nasjonalt vegnettverk for kjørende, gående og syklende.

Kvalitetshevingen innebærer manuell redigering av hver enkelt kommune: kontroll av topologi, stedfesting, fjerning av ikke-gjenfinnbare objekter og tilpasning av attributter slik at dataene møter NVDB-kravene. Arbeidet utføres av fylkeskartkontorene.

## 4.2 Produksjonskjeden

Produksjonen har to sekvensielle steg:

```
Kartkontor (kvalitetsheving) ──► Samferdselsavdelingen (NVDB-overføring via FME)
```

**Steg 1 – Kvalitetsheving:** Utføres ved 10 fylkeskartkontor. Hver kommune behandles som en udelelig enhet og må ferdigstilles før den kan sendes videre. Kapasiteten varierer mellom kontorene (se figur 1 og 2).

**Steg 2 – NVDB-overføring:** Utføres av to personer i 25 % stillingsandel hver (0,5 årsverk) i samferdselsavdelingen. 80–90 % av objektene legges inn automatisk via FME-rutiner, mens resterende 10–20 % må håndteres manuelt. Manuell produksjonstakt er 300–400 lenker per person per dag.

## 4.3 De 10 fylkeskartkontorene

Kartverket har 10 fylkeskartkontor som hver i dag har ansvar for sine fylker, og hver kommune kvalitetsheves av sitt "hjemme-kontor". Denne geografiske tildelingen er prosjektets utgangspunkt, men ikke en fastlåst begrensning: ett av hovedspørsmålene i analysen er om total varighet kan reduseres ved å omfordele kommuner mellom kontor, slik at kontor med god kapasitet avlaster kontor med høy arbeidsbelastning.

![Figur 1: Fylkeskartkontor og antall kommuner per kontor](figurer/01_kart_kontorer.png)

*Figur 1 Fylkeskartkontorenes ansvarsområder og antall kommuner per kontor*

Kontorene har svært ulik arbeidsbelastning og kapasitet. Oslo har 52 kommuner under sitt ansvar, mens Stavanger og Skien har 23 hver. Årlig kapasitet (uttrykt i ukesverk disponibelt for TVS-prosjektet i 2026) varierer fra 22 ukesverk (Bodø) til 52 ukesverk (Trondheim). Figur 2 (venstre) sammenligner årlig kapasitet i timer med estimert total arbeidsmengde per kontor, mens høyre panel viser estimert varighet i år ved full kapasitetsutnyttelse uten Geovekst-låsning. Mismatchen mellom kapasitet og arbeid er en hovedmotivasjon for å vurdere omfordeling av kommuner mellom kontor.

![Figur 2: Årlig kapasitet vs. estimert arbeidsmengde, og estimert varighet per kontor](figurer/02_kapasitet_vs_arbeid.png)

*Figur 2 Årlig kapasitet vs. estimert arbeidsmengde og estimert varighet per kartkontor*

## 4.4 Fremdrift per april 2026

Av 357 kommuner er 62 ferdig kvalitetshevet, 48 påbegynt og 247 ikke startet. Ingen kommuner er ennå overført til NVDB. Fremdriften er ulikt fordelt mellom kontorene: figur 3 viser antall kommuner per status for hvert kartkontor.

![Figur 3: Fremdriftsstatus per kartkontor (april 2026)](figurer/03_status_per_kontor.png)

*Figur 3 Fremdriftsstatus per kartkontor per april 2026*

## 4.5 Geovekst-låsing

Parallelt med TVS-prosjektet pågår ordinære Geovekst-kartleggingsprosjekter i flere kommuner. Under kartleggingsperiodene er kommunene låst for TVS-kvalitetsheving fordi dataene er under endring. I april 2026 er 152 kommuner berørt av slike låsninger, og låseperiodene strekker seg fra mars 2026 til mars 2027. Heatmap-cellen i figur 5 angir antall unike kommuner under hvert kontor som er i aktiv låseperiode den aktuelle måneden. De fleste låsningene er konsentrert om sommer og høst 2026, med enkelte prosjekter som fortsetter inn i 2027. Planleggingen må hensynta at låste kommuner ikke kan behandles før låseperioden er over.

![Figur 5: Antall kommuner låst av Geovekst per måned og kontor](figurer/05_geovekst_heatmap.png)

*Figur 5 Antall kommuner låst av Geovekst-prosjekter per måned og kartkontor*

## 4.6 Hvorfor dette er et planleggingsproblem

Problemet kombinerer klassiske elementer fra ressursallokering og produksjonsplanlegging:

- **Heterogene ressurser:** Kontorene har ulik kapasitet og ulike tidsestimater per kommune.
- **Heterogene jobber:** Kommunene varierer sterkt i størrelse (fra under 100 til over 35 000 lenker, se figur 6).
- **Tidsvinduer:** Geovekst-låsninger gjør deler av arbeidet utilgjengelig i perioder.
- **Nedstrøms flaskehals:** NVDB-overføringen har lav manuell kapasitet og blir trolig flaskehalsen i kjeden.
- **Målkonflikter:** Minimere total varighet, utnytte kapasitet, og unngå arbeid i låseperioder – disse kan trekke i ulike retninger.

Figur 6 (venstre) viser et histogram over antall lenker per kommune, med markert median og gjennomsnitt. Median er betydelig lavere enn snittet, noe som bekrefter en høyreskjev fordeling. Pareto-kurven (høyre) viser at arbeidet er sterkt konsentrert på få kommuner: omtrent 30 % av kommunene står for 80 % av de samlede lenkene. Dette har betydning for prioritering i heuristikken – å starte med de største kommunene kan gi rask reduksjon i gjenstående arbeid.

![Figur 6: Fordeling av antall lenker per kommune og Pareto-kurve for arbeidskonsentrasjon](figurer/06_lenker_histogram.png)

*Figur 6 Fordeling av arbeidsmengde per kommune og Pareto-kurve for arbeidskonsentrasjon*

---

# 5.0 Metode og data

## 5.1 Metode



## 5.2 Data

### 5.2.1 Datakilder

Rådataene er hentet fra fire hovedkilder:

| Fil | Kilde | Innhold |
|-----|-------|---------|
| `data.csv` | Samferdselsavdelingens PowerBI-rapport | Fremdriftsstatus per kommune (Ferdig / Påbegynt / Ikke påbegynt) |
| `Antall objekter per kommune.csv` | Kartverket | Arbeidsmengde i antall lenker per kommune (355 kommuner) |
| `20250903StatistikkTraktorvegSti.xlsx` | Kartverket grunndata | Kommunemapping, kilometer kurve, beregnet tidsbruk og dagsverk (359 kommuner) |
| `Datainnsamling_TraktorvegSti.xlsx` | 10 fylkeskartkontor | Kapasitet (ukesverk), min/maks tidsbruk per kommune, og Geovekst-prosjekter med låseperioder |

Datainnsamlingen fra kartkontorene ble samlet inn våren 2026 via et felles Excel-skjema med ett ark per kontor. Kristiansand-arket var tomt; disse dataene ble hentet fra separate CSV-filer (`Agder_prosjekter.csv`, `Rogaland_prosjekter.csv`) som supplement.

### 5.2.2 Datarensing

Rådataene hadde flere kvalitetsproblemer som måtte håndteres:

- **Feil fylkesinformasjon:** Feltet `fylkesnr` i `20250903StatistikkTraktorvegSti.xlsx` var forskjøvet og inkonsistent. Fylkestilhørighet utledes derfor fra de to første sifrene i kommunenummeret.
- **Ulike formater på låseperioder:** Tekstverdiene varierte fra datorange (f.eks. "august 2026 – mars 2027") til antall måneder ("7"). Alle standardiseres til start- og sluttdato, og ukjente formater tildeles perioden mai–desember 2026 som konservativt estimat.
- **Arbeidsmengde i ulike enheter:** Arbeidsmengde angis som antall lenker (ikke kilometer), ettersom produksjonstakten oppgis i lenker per person per dag.
- **Manuelle justeringer av kapasitetsdata:** Oslo-kontorets opprinnelige oppgitte kapasitet (20 ukesverk, 20–60 timer per kommune) ble vurdert som urealistisk lav sammenlignet med kontorets størrelse og øvrige kontorers nivå. Etter dialog ble verdiene justert til 30 ukesverk og 30–90 timer per kommune.

Datarensingen er implementert i `004 data/scripts/vask_og_strukturer.py` og produserer seks behandlede datasett.

### 5.2.3 Formel for beregnet tidsbruk per kommune

Den beregnede tidsbruken per kommune (`Ber_Tidbruk_Min` i rådatasettet) er ikke en empirisk måling, men en avledet størrelse beregnet ved følgende lineære formel:

$$
\text{Ber\_Tidbruk\_Min} = \text{Km\_Kurve} \times 0{,}9035 + \text{ArealLand\_Km}^2 \times 0{,}6510
$$

Koeffisientene kommer fra fanen `Tidbruk` i `20250903StatistikkTraktorvegSti.xlsx` og dokumenterer hvordan Kartverket estimerer ressursbehov for kvalitetsheving av TVS-data:

- **0,9035 min/km lenke:** empirisk gjennomsnitt av målt tidsbruk per kilometer TVS-lenke, utledet fra registreringer av faktisk tidsbruk på 58 kartblader.
- **0,6510 min/km² landareal:** standardtillegg for kommunens landareal ("grunnpakke"), som fanger opp arbeid som ikke skalerer direkte med lenkelengde (nettverkskontroll, topologisk kontroll, arkivarbeid m.m.).

Formelen er verifisert numerisk ved at det rekalkulerte Ber_Tidbruk_Min avviker med median 0,2 minutter og maksimalt 0,5 minutter fra oppgitt verdi for alle 357 kommuner. De 58 kartbladmålingene viser samtidig betydelig spredning i MIN/KM: fra 0,10 til 3,44 med standardavvik 0,55 – omtrent 60 % av gjennomsnittet. Dette betyr at `Ber_Tidbruk_Min` er et punktestimat basert på en gjennomsnittssats, og reell tidsbruk per kommune kan avvike betydelig. Denne empiriske variasjonen danner grunnlag for usikkerhetsvurdering i modellen.

### 5.2.4 Behandlede datasett

| Fil | Rader | Innhold |
|-----|-------|---------|
| `master_kommuner.csv` | 357 | Én rad per kommune: kommunenr, kartkontor, status, antall lenker, gjenstående lenker, beregnet tidsbruk, Geovekst-status |
| `kapasitet_kontorer.csv` | 10 | Én rad per kartkontor: årlig kapasitet (ukesverk), min/maks tidsbruk per kommune, aggregerte nøkkeltall |
| `geovekst_prosjekter.csv` | 173 | Én rad per kommune-prosjekt-par: prosjektkode, kommune, kartkontor, status, låseperiode (start/slutt) |
| `nvdb_overfoering.csv` | 3 | Tre scenarioer for NVDB-overføring med varierende automasjonsgrad (85 %, 90 %, 96 %) |
| `tidbruk_kalibrering.csv` | 58 | Én rad per kartblad med faktisk målt tidsbruk (MIN, LENGTH, MIN/KM, MIN/KM²) |
| `tidbruk_konstanter.csv` | 2 | Koeffisientene 0,9035 min/km og 0,6510 min/km² som brukes i formelen for Ber_Tidbruk_Min |

### 5.2.5 Nøkkeltall og deskriptiv statistikk

| Størrelse | Verdi |
|-----------|-------|
| Antall kommuner | 357 |
| Antall kartkontor | 10 |
| Totalt antall lenker | 2 630 964 |
| Gjenstående lenker (april 2026) | 2 138 104 |
| Total årlig kapasitet kartkontor | 327 ukesverk (12 262 timer) |
| Kommuner låst av Geovekst | 152 |
| Geovekst kommune-prosjekt-par | 173 |

Fordelingen av antall lenker per kommune er sterkt høyreskjev (figur 6): medianen er langt lavere enn gjennomsnittet, og noen få store kommuner (f.eks. Oslo, Bergen, Trondheim) inneholder en uforholdsmessig stor andel av totalen. Dette har betydning for modelleringen, ettersom små og store kommuner bør behandles ulikt i prioriteringen.

Arbeidsbelastningen varierer sterkt mellom kontorene, og også innad i hvert enkelt kontor. I figur 4 representerer hver horisontal søyle ett kontors samlede gjenstående arbeid, og hvert segment er én kommune sortert fra størst til minst. Enkelte kontor (som Oslo, Hamar og Bergen) har et fåtall svært store kommuner som dominerer arbeidsmengden, mens andre (som Molde og Bodø) har en jevnere fordeling av små og mellomstore kommuner.

![Figur 4: Lastfordeling per kontor, hver kommune som segment](figurer/04_lastfordeling.png)

*Figur 4 Lastfordeling per kartkontor, hvert segment er én kommune*

### 5.2.6 Antagelser og begrensninger

- Kapasitet oppgitt i ukesverk for 2026 antas å gjelde også for etterfølgende år i modellen.
- Individuell effektivitet per saksbehandler er ikke modellert; kapasiteten behandles som en aggregert ressurs per kontor.
- Samferdselsavdelingens estimat om ca. 2 års varighet for NVDB-innlegging avviker fra opprinnelig oppgitte tall (300–400 lenker/dag, 80–90 % automasjon). Avviket håndteres via sensitivitetsanalyse på automasjonsgrad.
- Kommune-til-kontor-tildelingen er en beslutningsvariabel i optimeringsmodellen. Kolonnen `Kartkontor` i `master_kommuner.csv` angir dagens geografiske tildeling og brukes som baseline som den optimerte omfordelingen sammenlignes mot.

---

# 6.0 Modellering

## 6.1 Heuristikk

Den regelbaserte heuristikken tjener som baseline og som validert simuleringsmotor for Monte Carlo-analyse og MIP-evaluering. Den simulerer dag-for-dag (mandag-fredag, ca. 260 arbeidsdager per år) over STARTDATO 1. mai 2026.

**Steg 1: Initiell tilstand.** For hver kommune *i* beregnes gjenværende timebehov som

$$t_i = \frac{\tau_i}{60} \cdot \frac{\ell^{\text{rest}}_i}{\ell_i}$$

der $\tau_i$ er beregnet tidsbruk i minutter (fra formel 5.2.3), $\ell^{\text{rest}}_i$ er gjenstående lenker og $\ell_i$ er totale lenker. Kommuner med status "Ferdig" (62 stk.) plasseres direkte i NVDB-kø fra STARTDATO.

**Steg 2: Prioriteringskø per kontor.** Kommuner tildeles hjemmekontor basert på fylkestilhørighet (baseline — omfordeling utforskes i MIP). Innenfor hvert kontor sorteres kommuner etter:

1. Låst på STARTDATO → plasseres sist
2. Ikke-låste → størst først (flest gjenværende timer)
3. Låste → tidligste opplåsingsdato først

**Steg 3: Dag-for-dag-simulering.** For hver arbeidsdag:

- Hvert kontor arbeider på første ikke-låste kommune i køen med daglig kapasitet $\kappa_j = K_j \cdot 37{,}5 / 230$ timer (der $K_j$ er oppgitt kapasitet i ukesverk). Når en kommune når 0 gjenværende timer, flyttes den til NVDB-køen.
- Hvis dagen er etter NVDB-startdato, drenerer NVDB-køen med scenariets kapasitet (1 167 / 1 750 / 4 375 lenker/dag for hhv. Basis_85 / Middels_90 / Samferdsel_96).

**Bevisste forenklinger.** Heuristikken modellerer ikke ferier/pauser, individuell effektivitet eller oppstartskostnad ved kommuneskifte. Hjemmekontor-tildelingen er status quo (baseline) — omfordeling er en kjernebeslutning som undersøkes i MIP.

## 6.2 MIP-formulering

Den matematiske optimeringsmodellen er formulert som et blandet heltallsproblem (MILP) med tidsindeksering på månedsnivå. Modellen minimerer totalvarighet fra STARTDATO til siste kommune er overført til NVDB.

### 6.2.1 Sett og parametre

- $I$ = aktive kommuner (ikke pre-ferdige), $|I| = 295$
- $J$ = kartkontor, $|J| = 10$
- $T$ = tidshorisont i måneder (120 for Basis_85, 80 for Middels_90, 32 for Samferdsel_96)
- $\tau_i$ = timebehov på kartkontor for kommune *i*
- $\ell_i$ = antall lenker som skal overføres til NVDB
- $\kappa_j$ = månedlig kartkontor-kapasitet for kontor *j* (matcher heuristikkens effektive kapasitet via $K_j \cdot 37{,}5 \cdot 260/(230 \cdot 12)$)
- $L_{it} \in \{0,1\}$ = 1 hvis kommune *i* kan behandles i måned *t* (0 hvis Geovekst-låst)
- $\mu$ = månedlig NVDB-kapasitet (lenker)
- $L^{pre}$ = lenker fra 62 pre-ferdige kommuner (tilgjengelig i NVDB-kø fra $t=0$)

### 6.2.2 Beslutningsvariabler

- $y_{ij} \in \{0,1\}$: kommune *i* tildeles kontor *j*
- $w_{ijt} \geq 0$: timer brukt på $(i, j)$ i måned *t*
- $z_{it} \in \{0,1\}$: kommune *i* er ferdig på kartkontor innen måned *t*
- $D_t \geq 0$: lenker overført til NVDB i måned *t*
- $Q_t \in \{0,1\}$: 1 hvis ikke all NVDB-overføring er ferdig innen måned *t*

### 6.2.3 Bibindelser

Hver aktive kommune tildeles nøyaktig ett kontor:

$$\sum_{j \in J} y_{ij} = 1, \quad \forall i \in I \tag{1}$$

Totale timer leveres:

$$\sum_{j \in J} \sum_{t \in T} w_{ijt} = \tau_i, \quad \forall i \in I \tag{2}$$

Månedlig kontor-kapasitet:

$$\sum_{i \in I} w_{ijt} \leq \kappa_j, \quad \forall j \in J, t \in T \tag{3}$$

Arbeid skjer kun på tildelt kontor (aggregert over tid):

$$\sum_{t \in T} w_{ijt} \leq \tau_i \cdot y_{ij}, \quad \forall i \in I, j \in J \tag{4}$$

Ingen arbeid under låseperioder:

$$\sum_{j \in J} w_{ijt} = 0, \quad \forall i, t \text{ med } L_{it} = 0 \tag{5}$$

Kommune ferdig-indikator:

$$\tau_i \cdot z_{it} \leq \sum_{j \in J} \sum_{s \leq t} w_{ijs}, \quad \forall i, t \tag{6}$$

Monotoni av ferdig-status:

$$z_{it} \geq z_{i,t-1}, \quad \forall i, t > 0 \tag{7}$$

NVDB-kapasitet per måned (null før NVDB-startdato):

$$D_t \leq \mu, \quad \forall t \geq t_0^{NVDB}; \quad D_t = 0, \quad \forall t < t_0^{NVDB} \tag{8}$$

NVDB kan ikke overføre mer enn tilgjengelig (pre-ferdige + ferdige fra kartkontor):

$$\sum_{s \leq t} D_s \leq L^{pre} + \sum_{i \in I} \ell_i \cdot z_{it}, \quad \forall t \tag{9}$$

All NVDB-overføring fullført innen horisonten:

$$\sum_{t \in T} D_t = L^{pre} + \sum_{i \in I} \ell_i \tag{10}$$

Makespan-indikator (lineariseringsteknikk):

$$L^{tot} - \sum_{s \leq t} D_s \leq L^{tot} \cdot Q_t, \quad \forall t \tag{11}$$

der $L^{tot} = L^{pre} + \sum_i \ell_i$. Sammen med $Q_t \leq Q_{t-1}$ sikrer (11) at $Q_t = 1$ så lenge NVDB ikke er ferdig.

### 6.2.4 Målfunksjon og lex-opt

Vi ønsker primært å minimere makespan $M = \sum_t Q_t$ (antall måneder før NVDB er ferdig). Men makespan-minimering alene ga en degenerert "just-in-time"-løsning der kartkontor-arbeid ble spredt over hele NVDB-perioden — matematisk optimal, men upraktisk.

For å finne en **realistisk** optimal plan brukes en leksikografisk målfunksjon som én-pass vektet sum:

$$\min \; W_1 \cdot M + W_2 \cdot \sum_{i \in I} \sum_{t \in T} \tau_i (1 - z_{it}) + \sum_{i \in I} (1 - y_{i, \text{hjem}(i)})$$

der:
- Første ledd (primær): makespan
- Andre ledd (sekundær): sum av $\tau_i \times$ (antall måneder ikke ferdig) — straffer sen kartkontor-ferdigstilling
- Tredje ledd (tertiær inertia): straffer omfordeling fra hjemmekontor — tie-breaker mot degenererte løsninger

Vektene $W_1 \approx 10^{10}$, $W_2 \approx 10^3$ sikrer at primær > sekundær > tertiær. Denne strukturen gir én solver-runde og unngår numeriske feil fra separate lex-opt-runder.

## 6.3 Sensitivitetsanalyse

To former for sensitivitet utforskes:

**NVDB-parametere (Monte Carlo).** 500 iterasjoner per scenario med tre stokastiske kilder: MIN/KM per kommune (bootstrap fra 58 empiriske kartbladmålinger), manuell takt (Uniform 300-400 lenker/dag/person) og automasjonsgrad (Normal rundt scenariopunktet, std 0,01). Monte Carlo kjøres på både heuristikkens og MIP-s plan for direkte sammenligning.

**Kapasitetsvariasjoner.** Fem varianter på kontor-kapasitet løses i MIP for hvert NVDB-scenario: S0_Baseline (nominell), S1_Trondheim50 (Trondheim -50 %), S2_Alle_pluss20 (alle +20 %), S3_Omfordeling (små kontor +50 %, store -20 %), S4_Alle_minus15 (alle -15 %). Dette kartlegger MIP-ens robusthet og identifiserer scenarioer der omfordeling blir nødvendig.

## 6.4 Implementeringsdetaljer

Heuristikken (`heuristikk.py`) og Monte Carlo-motoren (`monte_carlo.py`) er implementert i Python 3.13 med pandas og numpy. MIP-modellen (`mip_modell.py`) bruker PuLP 3.3 med CBC som solver (versjon 2.10.3, gratis og innebygd i PuLP). Horisonter og solver-tidsgrenser er satt slik at alle scenarioer løses optimalt eller nær-optimalt innen 15 minutter på vanlig utviklingsmaskin.

---

# 7.0 Analyse

## 7.1 MIP vs. heuristikk — makespan

Tabell 7.1 sammenligner total prosjektvarighet for heuristikken og MIP-modellen over de tre NVDB-scenarioene. MIP-modellen bruker vektet målfunksjon (lex-opt med inertia-tie-breaker), og er løst optimalt (CBC) eller nær-optimalt for alle scenarioer.

*Tabell 7.1 Makespan per metode og NVDB-scenario*

| Scenario | Heuristikk (år) | MIP (år) | Differanse |
|----------|:---:|:---:|:---:|
| Basis_85 | 8,64 | 8,75 | +0,11 |
| Middels_90 | 5,76 | 5,83 | +0,07 |
| Samferdsel_96 | 2,31 | 2,33 | +0,02 |

Alle differansene er under 2 % og skyldes MIP-modellens månedlige tidsoppløsning (hver måned avrundes opp ved kollisjon med NVDB-drenering). I praksis gir de to metodene *identisk makespan*. Figur 14 visualiserer resultatene.

![Figur 14: Total varighet heuristikk vs MIP per NVDB-scenario](figurer/14_heuristikk_vs_mip.png)

*Figur 14 Total varighet heuristikk vs MIP per NVDB-scenario*

## 7.2 Kartkontor-ferdigstilling

Heuristikken og MIP gir samme totalvarighet, men forskjellig profil for når kartkontor-arbeidet er ferdig. Figur 15 viser fordelingen: heuristikken ferdigstiller alle kommuner på kartkontoret innen ca. 16 måneder (medianverdi 4–5 måneder), mens MIP-planen — med lex-opt som sekundær målfunksjon — komprimerer kartkontor-arbeidet ytterligere til innen 10 måneder (median 3 måneder). Begge er realistiske fra et ressursforvaltningssynspunkt: NVDB-delen alene tar 2,3–8,7 år avhengig av automasjonsgrad, så kartkontorene rekker uansett å levere alt materiale lenge før NVDB er ferdig.

![Figur 15: Fordeling av kartkontor-ferdigmåned heuristikk vs MIP per NVDB-scenario](figurer/15_kartkontor_ferdig.png)

*Figur 15 Fordeling av kartkontor-ferdigmåned heuristikk vs MIP per NVDB-scenario*

## 7.3 Omfordeling mellom kontor

MIP-modellen har full frihet til å reassigne kommuner mellom kartkontor, men inertia-tie-breakeren favoriserer hjemmekontor-tildeling i tilfeller hvor flere løsninger gir samme makespan. Resultatet (figur 16) viser at 31–59 kommuner flyttes, men disse er hovedsakelig tie-breakere: ingen kommuner *må* omfordeles for å oppnå optimal makespan. Omfordelingene er symmetrisk spredt (diagonale tall dominerer i matrisen), noe som bekrefter at status quo-tildelingen er nær-optimal.

![Figur 16: Omfordeling hjemmekontor til MIP-kontor for Middels_90](figurer/16_omfordeling_matrise.png)

*Figur 16 Omfordeling hjemmekontor til MIP-kontor for Middels_90*

## 7.4 Kapasitets-sensitivitet

Figur 18 og 19 viser resultatet av sensitivitetsanalysen der kapasitet ved ett eller flere kontor endres. Fire varianter ble undersøkt: baseline (S0), Trondheim -50 % (S1), små kontor +50 % og store -20 % (S3), og alle -15 % (S4).

**Hovedfunn**: makespan er *uendret* i alle varianter for alle NVDB-scenarioer. Selv ved halvert Trondheim-kapasitet (S1) eller strukturell omfordeling av ressurser (S3) forblir total prosjektvarighet 8,75 / 5,83 / 2,33 år. Dette skyldes at kartkontorene uansett ferdigstiller arbeidet sitt lenge før NVDB rekker å drenere køen.

![Figur 18: Makespan per kapasitetsvariant og NVDB-scenario](figurer/18_kapasitet_sensitivitet.png)

*Figur 18 Makespan per kapasitetsvariant og NVDB-scenario*

Antallet omfordelte kommuner varierer mellom variantene (figur 19), noe som reflekterer MIP-modellens tilpasning av lokalt arbeid når kapasiteten endres. Dette gir et verdifullt beredskapsverktøy: dersom et kontor får redusert kapasitet, viser MIP hvilke kommuner som bør omfordeles til andre kontor for å holde de respektive køene i balanse — selv om makespan ikke endres.

![Figur 19: Antall omfordelte kommuner per kapasitetsvariant og NVDB-scenario](figurer/19_omfordeling_varianter.png)

*Figur 19 Antall omfordelte kommuner per kapasitetsvariant og NVDB-scenario*

## 7.5 Usikkerhetsanalyse

Monte Carlo-simuleringen (500 iterasjoner per scenario × tre stokastiske kilder) på MIP-s plan gir nesten identiske usikkerhetsbånd som heuristikk-baserte Monte Carlo (tabell 7.2). Dette bekrefter nok en gang at MIP-ens omfordelinger ikke påvirker den samlede risikoprofilen nevneverdig.

*Tabell 7.2 Usikkerhetsbånd MIP-plan (P5 / P50 / P95, år)*

| Scenario | MIP-plan | Heuristikk-plan |
|----------|:---:|:---:|
| Basis_85 | 7,27 / 8,64 / 10,17 | 7,27 / 8,64 / 10,17 |
| Middels_90 | 4,54 / 5,73 / 7,10 | 4,54 / 5,73 / 7,10 |
| Samferdsel_96 | 1,39 / 2,20 / 3,22 | 1,41 / 2,20 / 3,22 |

Den dominerende usikkerhetskilden er automasjonsgraden i FME-overføringen (jf. figur 11-13). Scenariobåndene overlapper ikke — P95 av Samferdsel_96 (3,22 år) ligger lavere enn P5 av Middels_90 (4,54 år). Dette understreker at *automasjonsgrad er den viktigste strategiske faktoren* for totalvarigheten, ikke kartkontor-allokering.

---

# 8.0 Resultat

## 8.1 Hovedresultater

Den hybride løsningsmetoden (regelbasert heuristikk + MIP-verifikasjon + Monte Carlo) gir følgende hovedresultater:

1. **Total prosjektvarighet (deterministisk estimat):**
   - Basis_85 (85 % FME-automasjon): **8,64 år**
   - Middels_90 (90 % automasjon): **5,76 år**
   - Samferdsel_96 (96 % automasjon): **2,31 år**

2. **Usikkerhetsbånd (P5–P95 fra 500 Monte Carlo-iterasjoner):**
   - Basis_85: 7,27 – 10,17 år
   - Middels_90: 4,54 – 7,10 år
   - Samferdsel_96: 1,39 – 3,22 år

3. **Omfordeling mellom kartkontor:** gir *ingen* forbedring i total makespan i noen av de tre NVDB-scenarioene. MIP-modellen bekrefter at heuristikkens hjemmekontor-tildeling er nær-optimal (innenfor 2 % av MIP-ens løsning, forskjellen skyldes tidsoppløsning, ikke assignment).

4. **Kartkontor-ferdigstilling:** alt kartkontor-arbeid fullføres innen 10–16 måneder i alle scenarioer. Kartkontorene er ikke flaskehalsen.

5. **NVDB-overføring er flaskehalsen:** makespan bestemmes nesten utelukkende av NVDB-kapasiteten. Ved 85 % automasjon krever den 9+ år alene, ved 96 % under 3 år.

## 8.2 Scenario-sammenligning

Figur 14 viser makespan for heuristikk og MIP side om side. De tre NVDB-scenarioene gir ikke-overlappende P5–P95-intervaller (P95 av Samferdsel_96 = 3,22 år < P5 av Middels_90 = 4,54 år), som betyr at valg av automasjonsgrad er en *dominant* strategisk beslutning sammenlignet med resourceallokering.

## 8.3 Robusthet mot kapasitetsforstyrrelser

Figur 18 viser at selv dramatiske kapasitetsendringer (f.eks. Trondheim -50 %, eller strukturell omfordeling) ikke endrer makespan. Dette er en robusthetsindikasjon: dagens plan kan absorbere uforutsette kapasitetsreduksjoner uten at prosjektet forsinkes, fordi kartkontorene uansett har luft til NVDB-flaskehalsen.

Fra et beredskapssynspunkt gir dette Kartverket trygghet i planleggingen. Dersom et kontor får redusert kapasitet under produksjonen, viser figur 19 hvilke omfordelinger MIP-modellen anbefaler for å balansere belastningen (selv om total varighet ikke endres).

---

# 9.0 Diskusjon



---

# 10.0 Konklusjon



---

# 11.0 Bibliografi

Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall/CRC.

Hartmann, S., & Briskorn, D. (2010). A survey of variants and extensions of the resource-constrained project scheduling problem. *European Journal of Operational Research, 207*(1), 1–14. https://doi.org/10.1016/j.ejor.2009.11.005

Pinedo, M. L. (2016). *Scheduling: Theory, algorithms, and systems* (5. utg.). Springer.

Puchinger, J., & Raidl, G. R. (2005). Combining metaheuristics and exact algorithms in combinatorial optimization: A survey and classification. I J. Mira & J. R. Álvarez (Red.), *Artificial intelligence and knowledge engineering applications: A bioinspired approach* (s. 41–53). Springer. (Lecture Notes in Computer Science, bind 3562)

Vose, D. (2008). *Risk analysis: A quantitative guide* (3. utg.). John Wiley & Sons.

---

# 12.0 Vedlegg


