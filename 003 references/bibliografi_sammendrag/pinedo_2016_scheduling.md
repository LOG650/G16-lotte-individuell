# Pinedo (2016) — Scheduling: Theory, Algorithms, and Systems (5. utg.)

> **AI-generert — ikke en kilde og ikke etterprøvd.** Dette notatet er laget av Claude (KI) som intern orientering. Innholdet er ikke hentet fra eller kontrollert mot originalkilden, og skal ikke siteres eller brukes som dokumentasjon på at kilden er lest. Kontroller alltid påstander mot primærkilden — se [../kilde_lenker/kilde_lenker.md](../kilde_lenker/kilde_lenker.md).

## APA 7-referanse

Pinedo, M. L. (2016). *Scheduling: Theory, algorithms, and systems* (5. utg.). Springer. https://doi.org/10.1007/978-3-319-26580-3

## Verifisert mot

- Springer Nature Link: https://link.springer.com/book/10.1007/978-3-319-26580-3
- ISBN-13 (print): 978-3-319-26578-0
- ISBN-13 (eBook): 978-3-319-26580-3
- DOI: 10.1007/978-3-319-26580-3

## Type publikasjon

Lærebok / standardverk. Brukt på master- og PhD-nivå internasjonalt. 5. utgave (siste utgave per 2026) utgitt 2016 av Springer.

## Sammendrag

Boken er et bredt anlagt standardverk i scheduling-feltet, organisert i tre deler:

1. **Deterministiske scheduling-modeller:** klassiske formuleringer på enkelmaskin, parallelle maskiner, flow shops, job shops og open shops. Bruker Graham et al.s α | β | γ-notasjon for å klassifisere problemer (maskinmiljø | jobbkarakteristikker | målfunksjon). Dekker både eksakte algoritmer (branch-and-bound, dynamisk programmering, polynomiske spesialtilfeller) og heuristikker (dispatching rules, lokale søk).

2. **Stokastiske scheduling-modeller:** problemer der prosesseringstider, ankomster eller maskintilgjengelighet er stokastiske. Inkluderer Markov-baserte modeller og policy-iterasjon.

3. **Scheduling i praksis:** anvendelser i produksjon, helse, transport, IT/datanettverk. Diskuterer arkitekturen til reelle scheduling-systemer og kobling mot ERP/MRP.

Boken har ledsagende materiale (industri-presentasjoner, demonstrasjonsalgoritmer) tilgjengelig via Pinedos nettside.

## Sentrale begreper og bidrag

- **α | β | γ-notasjon:** standard klassifikasjon i scheduling-litteraturen
- **Parallelle maskiner med ulike hastigheter:** *uniform machines* (Q_m) og *unrelated machines* (R_m) — direkte parallell til de 10 kartkontorene som har ulik kapasitet
- **Release-datoer og deadlines:** matematisk grunnlag for tidsvinduer
- **List-scheduling og dispatching rules:** SPT, LPT, EDD, WSPT mv.
- **Lagrange-relaksasjon og column generation:** eksakte teknikker for store problemer

## Relevans for LOG650-prosjektet

Pinedo gir det teoretiske rammeverket for å beskrive TraktorvegSti-problemet i α | β | γ-notasjon: den nærmeste klassiske analogien er *uniform machines med release-datoer og deadlines* — i Graham-notasjon noe i retning av Q_m | r_j, d_j | C_max, men med tilleggsbetingelser (NVDB-flaskehals nedstrøms) som gjør problemet til en RCPSP-variant. Boken er kilden å gå til hvis modelleringskapittelet skal styrkes med en formell problemklassifikasjon.

Boken er også et godt oppslagsverk for valg av baseline-heuristikker — kapittel 5 dekker LPT-regelen som ligger til grunn for `heuristikk.py`.

## Hvor kilden brukes i rapporten

- Kapittel 2.0 Litteratur, avsnitt 2.1 (linje 148)
- Kan utvides i kapittel 3.0 Teori med formell α | β | γ-klassifikasjon
- Kan også siteres i 5.1 Metode for begrunnelse av LPT-heuristikken

## Tilgang

- ISBN: 978-3-319-26578-0 (print) / 978-3-319-26580-3 (eBook)
- DOI: https://doi.org/10.1007/978-3-319-26580-3
- HiM-bibliotek: trolig fysisk på campus eller via SpringerLink-abonnement. Sjekk Oria.
