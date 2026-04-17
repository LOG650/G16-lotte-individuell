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

Kartverket har 10 fylkeskartkontor som hver har ansvar for sine fylker. Ansvarsfordelingen mellom kontor og kommuner er geografisk bestemt og kan ikke endres i denne analysen.

![Figur 1: Fylkeskartkontor og antall kommuner per kontor](figurer/01_kart_kontorer.png)

Kontorene har svært ulik arbeidsbelastning og kapasitet (se figur 2). Oslo har 52 kommuner under sitt ansvar, mens Stavanger og Skien har 23 hver. Årlig kapasitet (uttrykt i ukesverk disponibelt for TVS-prosjektet i 2026) varierer fra 22 ukesverk (Bodø) til 52 ukesverk (Trondheim).

![Figur 2: Årlig kapasitet vs. estimert arbeidsmengde, og estimert varighet per kontor](figurer/02_kapasitet_vs_arbeid.png)

## 4.4 Fremdrift per april 2026

Av 357 kommuner er 62 ferdig kvalitetshevet, 48 påbegynt og 247 ikke startet. Ingen kommuner er ennå overført til NVDB. Fremdriften er ulikt fordelt mellom kontorene (figur 3).

![Figur 3: Fremdriftsstatus per kartkontor (april 2026)](figurer/03_status_per_kontor.png)

## 4.5 Geovekst-låsing

Parallelt med TVS-prosjektet pågår ordinære Geovekst-kartleggingsprosjekter i flere kommuner. Under kartleggingsperiodene er kommunene låst for TVS-kvalitetsheving fordi dataene er under endring. I april 2026 er 152 kommuner berørt av slike låsninger, og låseperiodene strekker seg fra mars 2026 til mars 2027 (figur 5). Planleggingen må hensynta at låste kommuner ikke kan behandles før låseperioden er over.

![Figur 5: Antall kommuner låst av Geovekst per måned og kontor](figurer/05_geovekst_heatmap.png)

## 4.6 Hvorfor dette er et planleggingsproblem

Problemet kombinerer klassiske elementer fra ressursallokering og produksjonsplanlegging:

- **Heterogene ressurser:** Kontorene har ulik kapasitet og ulike tidsestimater per kommune.
- **Heterogene jobber:** Kommunene varierer sterkt i størrelse (fra under 100 til over 35 000 lenker, se figur 6).
- **Tidsvinduer:** Geovekst-låsninger gjør deler av arbeidet utilgjengelig i perioder.
- **Nedstrøms flaskehals:** NVDB-overføringen har lav manuell kapasitet og blir trolig flaskehalsen i kjeden.
- **Målkonflikter:** Minimere total varighet, utnytte kapasitet, og unngå arbeid i låseperioder – disse kan trekke i ulike retninger.

![Figur 6: Fordeling av antall lenker per kommune og Pareto-kurve for arbeidskonsentrasjon](figurer/06_lenker_histogram.png)

Pareto-kurven (figur 6, høyre) viser at arbeidet er sterkt konsentrert på få kommuner: en liten andel av kommunene står for det meste av lenkene. Dette har betydning for prioritering i heuristikken – å starte med de største kommunene kan gi rask reduksjon i gjenstående arbeid.

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

Datarensingen er implementert i `004 data/scripts/vask_og_strukturer.py` og produserer fire behandlede datasett.

### 5.2.3 Behandlede datasett

| Fil | Rader | Innhold |
|-----|-------|---------|
| `master_kommuner.csv` | 357 | Én rad per kommune: kommunenr, kartkontor, status, antall lenker, gjenstående lenker, beregnet tidsbruk, Geovekst-status |
| `kapasitet_kontorer.csv` | 10 | Én rad per kartkontor: årlig kapasitet (ukesverk), min/maks tidsbruk per kommune, aggregerte nøkkeltall |
| `geovekst_prosjekter.csv` | 173 | Én rad per kommune-prosjekt-par: prosjektkode, kommune, kartkontor, status, låseperiode (start/slutt) |
| `nvdb_overfoering.csv` | 3 | Tre scenarioer for NVDB-overføring med varierende automasjonsgrad (85 %, 90 %, 96 %) |

### 5.2.4 Nøkkeltall og deskriptiv statistikk

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

Arbeidsbelastningen varierer sterkt mellom kontorene, og også innad i hvert enkelt kontor (figur 4). Enkelte kontor (som Oslo, Hamar og Bergen) har et fåtall svært store kommuner som dominerer arbeidsmengden, mens andre (som Molde og Bodø) har en jevnere fordeling av små og mellomstore kommuner.

![Figur 4: Lastfordeling per kontor, hver kommune som segment](figurer/04_lastfordeling.png)

### 5.2.5 Antagelser og begrensninger

- Kapasitet oppgitt i ukesverk for 2026 antas å gjelde også for etterfølgende år i modellen.
- Individuell effektivitet per saksbehandler er ikke modellert; kapasiteten behandles som en aggregert ressurs per kontor.
- Samferdselsavdelingens estimat om ca. 2 års varighet for NVDB-innlegging avviker fra opprinnelig oppgitte tall (300–400 lenker/dag, 80–90 % automasjon). Avviket håndteres via sensitivitetsanalyse på automasjonsgrad.
- Tildeling av kommuner til kartkontor er geografisk fastlåst og kan ikke omfordeles.

---

# 6.0 Modellering



---

# 7.0 Analyse



---

# 8.0 Resultat



---

# 9.0 Diskusjon



---

# 10.0 Konklusjon



---

# 11.0 Bibliografi



---

# 12.0 Vedlegg


