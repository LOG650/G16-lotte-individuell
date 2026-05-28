# Efron & Tibshirani (1993) — An Introduction to the Bootstrap

> **AI-generert — ikke en kilde og ikke etterprøvd.** Dette notatet er laget av Claude (KI) som intern orientering. Innholdet er ikke hentet fra eller kontrollert mot originalkilden, og skal ikke siteres eller brukes som dokumentasjon på at kilden er lest. Kontroller alltid påstander mot primærkilden — se [../kilde_lenker/kilde_lenker.md](../kilde_lenker/kilde_lenker.md).

## APA 7-referanse

Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall/CRC.

## Verifisert mot

- Taylor & Francis (Chapman & Hall/CRC): https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/introduction-bootstrap-bradley-efron-tibshirani
- ISBN-13: 978-0-412-04231-7 (ISBN-10: 0412042312)
- Serie: Monographs on Statistics and Applied Probability, bind 57
- 456 sider, 1. utgave, 1993

## Type publikasjon

Lærebok / monografi. Skrevet av bootstrap-metodens oppfinner (Efron, 1979) sammen med Tibshirani. Standardreferanse for bootstrap i statistikkfaget.

## Sammendrag

Boken er en pedagogisk innføring i bootstrap-metoden — en statistisk teknikk for å estimere usikkerhet i en hvilken som helst statistikk uten å forutsette en parametrisk fordelingsform. Hovedideen er enkel: hvis vi har et observert datasett av størrelse n, kan vi simulere fordelingen til en statistikk ved å resample (med tilbakelegging) B nye datasett av samme størrelse, beregne statistikken på hver, og bruke den empiriske fordelingen av disse B verdiene som estimat for samplingfordelingen.

Boken dekker:

1. **Grunnleggende ikke-parametrisk bootstrap:** resampling med tilbakelegging fra observerte data
2. **Parametrisk bootstrap:** resampling fra en tilpasset modell
3. **Konfidensintervaller:** percentil-metoden, BCa (bias-corrected and accelerated), bootstrap-t
4. **Bias-korreksjon og varians-estimater**
5. **Hypotesetesting via bootstrap**
6. **Jackknife** som en tilstøtende teknikk
7. **Anvendelser:** regresjon, tidsrekker, klassifikasjon

Boken er kjent for sin tilgjengelige stil med konkrete eksempler og R/S-kode.

## Sentrale begreper og bidrag

- **Resampling med tilbakelegging:** kjernen i metoden
- **Empirisk fordeling F̂:** bootstrap antar at F̂ er en god approksimasjon til den ukjente sanne fordelingen F
- **B = 1 000–10 000 bootstrap-replikater:** typisk anbefaling for konfidensintervaller
- **BCa-intervaller:** bias- og skjevhetskorrigerte konfidensintervaller, mer pålitelige enn enkle percentilintervaller
- **Når bootstrap fungerer:** når statistikken er en glatt funksjon av dataene og prøvestørrelsen ikke er for liten

## Relevans for LOG650-prosjektet

Efron & Tibshirani gir den teoretiske begrunnelsen for hvordan MIN/KM-verdier samples i `monte_carlo.py`:

- **58 empiriske kartbladmålinger:** datasettet er for lite til å forsvare en parametrisk fordeling (lognormal, gamma osv.) med tillit
- **Bootstrap-prinsipp:** for hver Monte Carlo-iterasjon trekkes MIN/KM-verdier per kommune fra den empiriske fordelingen av de 58 målingene (med tilbakelegging)
- **Range 0,10–3,44:** hele den observerte spredningen reflekteres i resultatene, ikke en glattet parametrisk versjon

Dette gjør at usikkerhetsbåndet (P5–P95) for total varighet er forankret i faktiske data, ikke i en antakelse som ville vært vanskelig å verifisere.

**Viktig forbehold:** ren bootstrap antar at de 58 observasjonene er representative for *populasjonen* av kartblader. Hvis det er systematisk skjevhet — f.eks. at kalibreringsmålingene er gjort på enklere kartblader enn de gjenstående kommunene — vil bootstrap *ikke* fange opp dette. Validering_tidbruk_formel.md flagger nettopp dette: ferdige kommuner ser ut til å være ~halvparten så tunge per stk som de gjenstående. Tidbruk-skaleringssensitiviteten (modell-jobb #1) adresserer dette ved å skalere formelen med 1,5x og 2,0x.

## Hvor kilden brukes i rapporten

- Kapittel 2.0 Litteratur, avsnitt 2.4 (linje 162)
- Bør også siteres i 5.1 Metode (Monte Carlo-design) og 9.0 Diskusjon (forbehold om representativitet)

## Tilgang

- ISBN: 978-0-412-04231-7
- Internet Archive (utlån): https://archive.org/details/introductiontobo0000efro
- Taylor & Francis: https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/introduction-bootstrap-bradley-efron-tibshirani
- Oria-søk: HiM-bibliotek har trolig boken (Monographs on Statistics and Applied Probability bind 57)
