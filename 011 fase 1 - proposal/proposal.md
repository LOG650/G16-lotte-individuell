# Proposal LOG650

**Gruppemedlemmer:**
Lotte Picard

**Område:**
Operasjonell planlegging, ressursallokering og produksjonsplanlegging

**Bedrift (valgbart):**
Statens Kartverk, Region og Samfunnskontakt

Litt bakgrunnsinfo:

Fra Kartverket.no:
Geovekst er et samarbeid om etablering, forvaltning og bruk av geografisk informasjon. Her deltar Kartverket, Statens vegvesen, NVE, Bane NOR, Energi Norge, Telenor, kommunene, fylkeskommunene og Landbruksdepartementet med sine underliggende etater.
Datasettene i FKB består av blant annet høyde, vann, markslag (AR5), arealbruk, bygninger, bygningsmessige anlegg, ledninger, veg, jernbane og flyplass.
FKB-data er ikke-sensitive og åpne data. FKB-dataene er finansiert gjennom Geovekst-samarbeidet, eller kommunene alene for kommuner som står utenfor Geovekst. FKB-dataene er fritt tilgjengelige for Norge digitalt parter og kan lastes ned gjennom nedlastingsløsningen på Geonorge. Private aktører må kjøpe tilgang til dataene gjennom en forhandler.

Fra nvdb.no:
Nasjonal vegdatabank (NVDB) er en nasjonal tjeneste og database fra Statens vegvesen. Den utgjør grunnmuren i det norske vegsystemet. NVDB inneholder offisiell informasjon om vegen og brukes til flere formål.

Fra SOSI-standardisert produktspesifikasjon for FKB-TraktorvegSti 5.1:
FKB-TraktorvegSti er et landsdekkende, soneinndelt FKB-datasett som inneholder traktorveger, stier og stitrapp med senterlinjegeometri. Det er de mest detaljerte dataene Norge har over slike små veger og stier. Dataene lagres på vektorformat (kurver).
FKB-TraktorvegSti må sees i sammenheng med datasettet Vegnett som inneholder øvrig vegnett og som forvaltes i Nasjonal vegdatabank (NVDB). Sammen med vegnettet fra NVDB skal FKB-TraktorvegSti kunne danne et komplett samferdselsnettverk for kjørende, syklende og gående.
Datagrunnlaget i FKB-TraktorvegSti vil ha svært varierende grad av nettverkstopologi. Man må regne med å gjøre en jobb med sammenknytning av FKB-TraktorvegSti og Vegnett før dette kan betraktes som ett nettverk og benyttes i nettverksanalyser.

**Problemstilling:**
Fylkeskartkontorene i Kartverket skal gjennomføre et kvalitetshevingsprosjekt av datasettet TraktorvegSti, der datasettet etter kvalitetsheving skal implementeres i NVDB (Norsk Vegdatabank).

Kvalitetshevingens mål er at traktorveger og stier skal inngå sammen med veger i et nasjonalt vegnettverk for kjørende, gående og syklende.

Kvalitetshevingsarbeidet gjøres likt over hele landet, basert på en fast produksjonsløype, og innebærer en god del manuell redigering i datasettet. Arbeidet utføres i dag kommunevist på fylkeskartkontorene.

Utfordringer som kan påvirke tidsbruken er mengde data som ikke har topologisk sammenheng eller har dårlig stedfestingsnøyaktighet. I tillegg må data som ikke er gjenfinnbare i terrenget etter kontroll mot flybilder, eller som er i konflikt med andre objekter som bygninger og veger fjernes.

Datasettet er lagret i sonearkiv, og hvert fylkeskartkontor har ansvar for oppdatering innenfor de kommunene som hører til fylket/fylkene de ulike kontorene representerer. Det er ulik kapasitet på de forskjellige kartkontorene, og det må i tillegg tas hensyn til pågående- og planlagte kartleggingsprosjekter, der flere offentlige aktører går sammen om å finansiere og produsere geografiske data.

Et kartleggingsprosjekt foregår ved at dataene sendes til eksterne firma, som tar bilder fra fly, og deretter konstruerer vektordata på grunnlag av det de ser i disse flybildene. Ved pågående kartleggingsprosjekt er dataene i et avgrenset område «låst», dvs man skal helst unngå større arbeid der mens prosjektet pågår. Kan være et tidsrom på et halvt år eller mer. Kartleggingsprosjekter foregår stort sett regionvis, med få eller mange kommuner involvert i samme prosjekt.

Når kartkontorene er ferdig med arbeidet sitt klarmeldes dataene kommunevis til en annen avdeling i Kartverket, som deretter foretar innleggingen i NVDB. Avgrensningen av prosjektet er den delen av produksjonene som tilhører fylkeskartkontorene, dvs kvalitetshevingsjobben og klarmelding av kommuner til videre innlegging.

Det er en forutsetning at det skal jobbes kommunevis med dataene, da hele produksjonsløypa er lagt opp etter det.

**Data:**

Arbeidsmengde:

- Antall TraktorvegSti-veglenker pr kommune.
- Estimert tidsbruk pr kommune basert på historikk.
- Antall kommuner.

Kapasitet:

- Antall kontorer. Kartverket har 10 fylkeskartkontor.
- Kapasitet lokalt på hvert kartkontor. Varierer fra kontor til kontor.
- Tilgjengelige timer pr uke/mnd/sesong.
- Overføringskapasitet til NVDB (evt. simulerte data). Denne oppgaven utføres ikke av fylkeskartkontorene.

Geovekstprosjekter:

- Oversikt over aktive prosjekter i kommuner.
- Oversikt over planlagte prosjekter.
- Estimert låseperiode for aktive og planlagte prosjekter.

**Beslutningsvariabler:**

- Tildeling av kommuner til hvert kartkontor.
- Rekkefølge på hvilke kommuner som behandles når.
- Ressursallokering basert på kontorenes kapasitet.
- Justeringer i produksjonsrekkefølge pga Geovekst-prosjekter.

**Målfunksjon:**
Målet er å finne en organisering og fordeling av kommuner som:

- Minimerer total prosjektvarighet for hele landet.
- Utnytter kapasiteten ved kartkontorene best mulig.
- I minst mulig grad utfører kvalitetsheving i perioder der kommuner er "låst" pga kartleggingsprosjekter.
- Sikrer jevn arbeidsbelastning.

**Avgrensninger:**

- Ulike personer har ulik effektivitet - dette kan vi ikke ta hensyn til i prosjektet.
- Kartleggingsprosjekter kan endre seg fortløpende, her kan tidsskjema endre seg.
- All produksjon må ferdigstilles kommunevis.
