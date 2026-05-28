# Vose (2008) — Risk Analysis: A Quantitative Guide (3. utg.)

> **AI-generert — ikke en kilde og ikke etterprøvd.** Dette notatet er laget av Claude (KI) som intern orientering. Innholdet er ikke hentet fra eller kontrollert mot originalkilden, og skal ikke siteres eller brukes som dokumentasjon på at kilden er lest. Kontroller alltid påstander mot primærkilden — se [../kilde_lenker/kilde_lenker.md](../kilde_lenker/kilde_lenker.md).

## APA 7-referanse

Vose, D. (2008). *Risk analysis: A quantitative guide* (3. utg.). John Wiley & Sons.

## Verifisert mot

- Wiley: https://www.wiley.com/en-us/Risk+Analysis:+A+Quantitative+Guide,+3rd+Edition-p-9780470512845
- ISBN-13: 978-0-470-51284-5
- 752 sider, hardcover, 2008

## Type publikasjon

Lærebok / praktisk håndbok i kvantitativ risikoanalyse. Bredt brukt referanseverk i prosjektledelse, finans, forsikring og helsesektor. Forfatteren har lang fartstid som konsulent og har vært involvert i risikoanalyse-verktøyet ModelRisk.

## Sammendrag

Boken er et oppslagsverk for praktisk Monte Carlo-basert risikoanalyse og kvantitativ usikkerhetsmodellering. Den er strukturert i fire deler:

1. **Grunnleggende metodikk:** problembestemmelse, hva risiko betyr, "rules of thumb" for når kvantitativ analyse er hensiktsmessig
2. **Sannsynlighetsfordelinger:** hvordan velge mellom uniform, normal, trekantet, lognormal, beta, empirisk osv. — basert på datatilgjengelighet og logiske egenskaper ved variabelen
3. **Monte Carlo-mekanikk:** sampling-strategier (enkel sampling, Latin Hypercube), antall iterasjoner som trengs for konvergens, korrelasjon mellom inputs (Iman-Conover, copula), variansreduksjon
4. **Tolkning og presentasjon:** persentiler (P5/P50/P95), tornado-diagrammer, fan charts, sensitivitetsanalyse, hvordan kommunisere usikkerhet til ikke-tekniske beslutningstakere

Boken har et anvendt fokus med rikelig av eksempler fra reelle prosjekter — særlig egnet for studenter og praktikere som skal lage en MC-analyse for første gang.

## Sentrale begreper og bidrag

- **Monte Carlo-simulering:** prinsipp, antall iterasjoner (Vose anbefaler 1 000–10 000 for de fleste anvendelser; 500 er marginalt)
- **Valg av input-fordeling:** beslutningstre basert på hva man vet om variabelen (data, ekspertvurdering, fysiske grenser)
- **Korrelasjonshåndtering:** når og hvordan modellere avhengigheter mellom inputs
- **Persentilrapportering (P5/P50/P95):** standardpresentasjon av output
- **Sensitivitetsanalyse:** tornado-diagrammer for å identifisere dominerende usikkerhetskilder

## Relevans for LOG650-prosjektet

Vose er hovedreferansen for valgene i `monte_carlo.py`:

- **Tre stokastiske kilder:** valgt etter Voses prinsipp om at kun de variablene som faktisk har materiell usikkerhet bør modelleres stokastisk (MIN/KM, produksjonstakt, automasjonsgrad)
- **500 iterasjoner:** lavere enn Voses anbefaling, men begrunnet i at MIP-baserte kjøringer er kostbare. P5/P95 stabilitet sjekket empirisk
- **Empirisk fordeling for MIN/KM:** følger Voses prinsipp om at empiriske data er å foretrekke når antall observasjoner er lite og parametrisk antakelse er svakt begrunnet
- **Persentilbasert rapportering:** alle MC-resultater i rapporten er presentert som P5/P50/P95
- **Identifisering av dominerende usikkerhetskilde:** automasjonsgraden er identifisert som dominerende, jf. Voses tornado-prinsipp

## Hvor kilden brukes i rapporten

- Kapittel 2.0 Litteratur, avsnitt 2.3 (linje 158)
- Bør også siteres i 5.1 Metode (Monte Carlo-design) og 9.0 Diskusjon (begrunnelse for AUTOMASJON_STD-valg)

## Tilgang

- ISBN: 978-0-470-51284-5
- Internet Archive (utlån): https://archive.org/details/riskanalysisquan0000vose
- Oria-søk: HiM-bibliotek har trolig boken. ModelRisk-nettsiden (vosesoftware.com) har gratis ressursmateriale.
