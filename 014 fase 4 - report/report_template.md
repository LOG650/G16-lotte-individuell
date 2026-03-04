# Tittel (norsk og/eller engelsk)

**Forfatter(e):**      
**Totalt antall sider inkludert forsiden:**      
**Molde, Innleveringsdato:**      

---

## Obligatorisk egenerklæring/gruppeerklæring

Den enkelte student er selv ansvarlig for å sette seg inn i hva som er lovlige hjelpemidler, retningslinjer for bruk av disse og regler om kildebruk. Erklæringen skal bevisstgjøre studentene på deres ansvar og hvilke konsekvenser fusk kan medføre. Manglende erklæring fritar ikke studentene fra sitt ansvar.

Du/dere fyller ut erklæringen ved å klikke i ruten til høyre for den enkelte del 1-6:

1. Jeg/vi erklærer herved at min/vår besvarelse er mitt/vårt eget arbeid, og at jeg/vi ikke har brukt andre kilder eller har mottatt annen hjelp enn det som er nevnt i besvarelsen. [ ]
2. Jeg/vi erklærer videre at denne besvarelsen:
   - ikke har vært brukt til annen eksamen ved annen avdeling/universitet/høgskole innenlands eller utenlands. [ ]
   - ikke refererer til andres arbeid uten at det er oppgitt. [ ]
   - ikke refererer til eget tidligere arbeid uten at det er oppgitt. [ ]
   - har alle referansene oppgitt i litteraturlisten. [ ]
   - ikke er en kopi, duplikat eller avskrift av andres arbeid eller besvarelse. [ ]
3. Jeg/vi er kjent med at brudd på ovennevnte er å betrakte som fusk og kan medføre annullering av eksamen og utestengelse fra universiteter og høgskoler i Norge, jf. Universitets- og høgskoleloven §§4-7 og 4-8 og Forskrift om eksamen §§14 og 15. [ ]
4. Jeg/vi er kjent med at alle innlevere oppgaver kan bli plagiatkontrollert i URKUND. [ ]
5. Jeg/vi er kjent med at høgskolen vil behandle alle saker hvor det forligger mistanke om fusk etter høgskolens retningslinjer. [ ]
6. Jeg/vi har satt oss inn i regler og retningslinjer i bruk av kilder og referanser på biblioteket sine nettsider. [ ]

---

## Personvern

**Personopplysningsloven**
Har oppgaven vært vurdert av NSD? [ ] ja [ ] nei
- Hvis ja, referansenummer:      
- Hvis nei, erklærer jeg/vi at oppgaven ikke omfattes av Personopplysningsloven.

**Helseforskningsloven**
Har oppgaven vært til behandling hos REK? [ ] ja [ ] nei
- Hvis ja, referansenummer:      

---

## Publiseringsavtale

**Studiepoeng:**      
**Veileder:**      

**Fullmakt til elektronisk publisering av oppgaven**
Jeg/vi gir herved Høgskolen i Molde en vederlagsfri rett til å gjøre oppgaven tilgjengelig for elektronisk publisering: [ ] ja [ ] nei

**Er oppgaven båndlagt (konfidensiell)?** [ ] ja [ ] nei
- Hvis ja, kan oppgaven publiseres når båndleggingsperioden er over? [ ] ja [ ] nei

**Dato:**      
**Antall ord:**      

---

## Sammendrag / Abstract

(Skriv sammendrag her)

---

## Innhold

1. [Innledning](#10-innledning)
2. [Litteratur](#20-litteratur)
3. [Teori](#30-teori)
4. [Casebeskrivelse](#40-casebeskrivelse)
5. [Metode og data](#50-metode-og-data)
6. [Modellering](#60-modellering)
7. [Analyse](#70-analyse)
8. [Resultat](#80-resultat)
9. [Diskusjon](#90-diskusjon)
10. [Konklusjon](#100-konklusjon)
11. [Bibliografi](#110-bibliografi)
12. [Vedlegg](#120-vedlegg)

---

# 1.0 Innledning
Dette prosjektet tar for seg kvalitetsheving og implementering av datasettet FKB-TraktorvegSti i Nasjonal vegdatabank (NVDB). Kartverket, i samarbeid med Geovekst-partnere, forvalter geografisk informasjon som er kritisk for norsk infrastruktur. Et komplett og nøyaktig vegnettverk, som inkluderer traktorveger og stier, er avgjørende for planlegging og navigasjon for både gående, syklende og kjørende. 

I dag utføres dette arbeidet kommunevis ved ti ulike fylkeskartkontorer med varierende kapasitet. Utfordringen ligger i å koordinere dette arbeidet effektivt, spesielt når deler av datasettet er "låst" på grunn av pågående kartleggingsprosjekter (Geovekst-prosjekter). Tidligere har prosessen vært preget av manuelle vurderinger lokalt, men det er behov for en mer helhetlig tilnærming for å optimalisere ressursbruken på nasjonalt nivå. 

I denne rapporten undersøkes det hvordan man kan organisere og fordele dette arbeidet for å minimere total prosjektvarighet og sikre jevn arbeidsbelastning på tvers av kontorene.

## 1.1 Problemstilling
Hvordan kan Kartverket optimalisere tildelingen og rekkefølgen av kommuner i kvalitetshevingsprosjektet for TraktorvegSti, slik at total prosjektvarighet minimeres under hensyn til kontorenes kapasitet og begrensninger fra eksterne kartleggingsprosjekter?

## 1.2 Delproblemer (valgfri)
For å besvare hovedproblemstillingen belyses følgende:
1. Hvordan påvirker de "låste" periodene i Geovekst-prosjektene den optimale produksjonsplanen?
2. På hvilken måte kan ulik kapasitet ved de ti fylkeskartkontorene utnyttes for å balansere arbeidsbelastningen?

## 1.3 Avgrensinger
Oppgaven avgrenses til den delen av produksjonen som utføres av fylkeskartkontorene (kvalitetsheving og klarmelding). Selve innleggingsjobben i NVDB, som utføres av en annen avdeling, faller utenfor oppgavens rammer. Det tas videre ikke hensyn til individuelle forskjeller i effektivitet hos saksbehandlere, men opereres med gjennomsnittlig estimert tidsbruk per kommune.

## 1.4 Antagelser
Det antas at estimatene for tidsbruk per kommune er representative basert på historiske data. Det legges også til grunn at kapasiteten ved hvert kartkontor er konstant gjennom prosjektperioden, med mindre annet er spesifisert. Låseperioder for planlagte Geovekst-prosjekter forutsettes å være kjente og faste i modelleringstidspunktet.

# 2.0 Litteratur
I dette kapittelet presenteres faglitteratur og forskning fra de siste fem årene som danner det faglige grunnlaget for oppgaven. Litteraturgjennomgangen er strukturert rundt tre hovedtemaer: forvaltning av nasjonale vegdata, datakvalitet i geografiske informasjonssystemer (GIS), og optimalisering av produksjonsplanlegging.

### 2.1 Forvaltning av nasjonale vegdata og NVDB
Forvaltningen av vegdata i Norge utføres i et samspill mellom Statens vegvesen og Kartverket, der Nasjonal vegdatabank (NVDB) utgjør fundamentet for vegsystemet. Statens vegvesen (2025) understreker i sine kvalitetsrapporter at nøyaktige vegdata er avgjørende for samfunnets planleggingsbehov. Her deles kvalitet inn i elementer som fullstendighet, stedfesting og nøyaktighet i egenskapsdata. Implementeringen av detaljerte nettverksmodeller som NVDB Vegnett Pluss stiller økte krav til presisjon i datasett som TraktorvegSti for å kunne danne et sømløst samferdselsnettverk.

### 2.2 Datakvalitet i GIS
Internasjonale standarder som ISO 19157-1 (International Organization for Standardization, 2023) legger rammene for hvordan geografisk datakvalitet skal måles og dokumenteres. Kartverkets datakvalitetsstrategi for 2026–2030 (Kartverket, 2025) peker på at økt datakvalitet er en forutsetning for effektiv digitalisering og ressursbruk i offentlig sektor. Videre viser forskning (Oluyisola et al., 2022) en direkte sammenheng mellom datakvalitet og suksess i produksjonsplanlegging. Det argumenteres for at beslutningsprosesser i moderne produksjonslinjer er sårbare for mangelfulle data, noe som er direkte overførbart til kvalitetshevingsarbeidet ved fylkeskartkontorene.

### 2.3 Optimalisering av produksjonsplanlegging med begrensninger
Teori innen operasjonsanalyse beskriver metoder for å allokere begrensede ressurser for å minimere total prosjekttid ("makespan"). Litteraturen skiller mellom teknikker som ressursutjevning og ressursglatting for å håndtere kapasitetsbegrensninger. I GIS-spesifikk produksjon må slike modeller håndtere både romlige og tidsmessige avhengigheter. En sentral utfordring er håndtering av "låste" ressurser, tilsvarende Geovekst-prosjektene som legger begrensninger på hvilke kommuner som kan behandles til enhver tid. Bruk av matematiske modeller og heuristikker trekkes frem som effektive verktøy for å finne optimale løsninger i slike komplekse nettverk.

# 3.0 Teori
Dette kapittelet redegjør for de teoretiske rammene som danner grunnlaget for analysen av ressursallokering og produksjonsplanlegging i Kartverket. Det fokuseres på prinsipper innen operasjonsanalyse, spesifikt Resource-Constrained Project Scheduling Problem (RCPSP), samt teorier knyttet til kapasitetsstyring og geografisk nettverkstopologi.

### 3.1 Operasjonsanalyse og RCPSP
Operasjonsanalyse (OR) benytter matematiske modeller for å finne de beste løsningene på komplekse beslutningsproblemer under gitte begrensninger. For dette prosjektet er rammeverket *Resource-Constrained Project Scheduling Problem* (RCPSP) sentralt. RCPSP adresserer utfordringen med å planlegge en serie oppgaver (kommuner) slik at de utføres i en rekkefølge som minimerer prosjektets varighet, samtidig som man respekterer begrensninger i ressurser og tid (Brucker et al., 1999). 

Innenfor dette feltet skilles det mellom eksakte løsningsmetoder og heuristikker. Mens eksakte metoder søker den matematisk optimale planen, benyttes ofte heuristikker for å håndtere store og komplekse datasett der beregningstiden ellers ville blitt uforholdsmessig lang (Hartmann & Kolisch, 2006).

### 3.2 Kapasitetsstyring og køteori
Kapasitetsstyring omhandler balanseringen mellom tilgjengelige ressurser og etterspørselen etter produksjon. I Kartverkets kontekst, hvor ti ulike kontorer har ulik bemanning, er teorier om *ressursutjevning* (resource leveling) relevante for å sikre en jevn arbeidsbelastning (Slack et al., 2022). 

Køteoretiske perspektiver anvendes for å forstå sammenhengen mellom ressursutnyttelse og ventetid. Slack et al. (2022) påpeker at når utnyttelsesgraden av en ressurs nærmer seg 100 %, vil ventetiden øke eksponentielt dersom det forekommer variasjon i oppgavene. Dette er kritisk for å forstå tidsbruken i produksjonsløypa når ulike kommuner krever ulik grad av manuell redigering.

### 3.3 Geografisk nettverkstopologi og dataintegritet
Teori om geografisk nettverkstopologi beskriver hvordan geografiske objekter er logisk knyttet til hverandre gjennom noder og lenker (Worboys & Duckham, 2004). For at TraktorvegSti skal kunne integreres i et nasjonalt vegnettverk, kreves det topologisk konsistens. Laurini og Thompson (1992) definerer dette som integritetskrav som sikrer at nettverket er logisk sammenhengende og fritt for feil som hindrer ruteanalyser.

Ved å se de tekniske kravene til topologisk integritet i sammenheng med logistisk planlegging, kan man identifisere hvordan datakvalitet direkte påvirker premissene for optimal ressursallokering i produksjonslinjen.

# 4.0 Casebeskrivelse
Utbrodering av problemet for bedriften/bransjen. Ta kun med relevant informasjon.

# 5.0 Metode og data
## 5.1 Metode
Beskriv prosessen så nøyaktig at den kan gjentas (paradigme, design, utvalg, analysemetoder).
## 5.2 Data
Hvordan data er samlet inn (tidsperiode, intervjuer, spørreskjema, ERP-system).

# 6.0 Modellering
(Beskrivelse av modell)

# 7.0 Analyse
Kvalitativ, kvantitativ eller dokumentanalyse.

# 8.0 Resultat
Objektiv presentasjon av funn ved bruk av tabeller og figurer med forklarende tekst.

# 9.0 Diskusjon
Kommenter resultatene. Er de som forventet? Samsvarer de med litteraturen? Betydning for næringslivet og begrensninger.

# 10.0 Konklusjon
Oppsummering av hovedfunn i forhold til problemstilling og forslag til videre forskning.

# 11.0 Bibliografi
Brucker, P., Drexl, A., Möhring, R., Neumann, K., & Pesch, E. (1999). Resource-constrained project scheduling: Notation, classification, models, and methods. *European Journal of Operational Research*, *112*(1), 3–41. https://doi.org/10.1016/S0377-2217(98)00204-5

Hartmann, S., & Kolisch, R. (2006). Heuristic algorithms for solving the resource-constrained project scheduling problem: Classification and computational analysis. In J. Weglarz (Ed.), *Project scheduling: Recent models, algorithms and applications* (pp. 147–178). Springer. https://doi.org/10.1007/0-306-48125-7_7

International Organization for Standardization. (2023). *Geographic information — Data quality — Part 1: General requirements* (ISO Standard No. 19157-1:2023). https://www.iso.org/standard/78910.html

Kartverket. (2025). *Datakvalitetsstrategien 2026–2030: Datakvalitetsstrategi for eiendomsregisteret*. https://www.kartverket.no/eiendom/matrikkel/datakvalitet-i-matrikkelen/datakvalitetsstrategi

Laurini, R., & Thompson, D. (1992). *Fundamentals of spatial information systems*. Academic Press.

Oluyisola, O. E., Bhalla, S., Sgarbossa, F., & Strandhagen, J. O. (2022). Designing and developing smart production planning and control systems in the industry 4.0 era: a methodology and case study. *Journal of Intelligent Manufacturing*, *33*(1), 311–332. https://doi.org/10.1007/s10845-021-01808-w

Slack, N., Brandon-Jones, A., & Burgess, N. (2022). *Operations management* (10th ed.). Pearson.

Statens vegvesen. (2025). *Datakvalitet i NVDB: Kvalitetsrapporter*. Nasjonal vegdatabank. https://www.vegvesen.no/fag/teknologi/nasjonal-vegdatabank/datakvalitet-i-nvdb/kvalitetsrapporter/

Worboys, M. F., & Duckham, M. (2004). *GIS: A computing perspective* (2nd ed.). CRC Press.

# 12.0 Vedlegg
(Relevante vedlegg)