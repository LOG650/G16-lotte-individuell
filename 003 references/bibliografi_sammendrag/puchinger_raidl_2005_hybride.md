# Puchinger & Raidl (2005) — Combining Metaheuristics and Exact Algorithms

> **AI-generert — ikke en kilde og ikke etterprøvd.** Dette notatet er laget av Claude (KI) som intern orientering. Innholdet er ikke hentet fra eller kontrollert mot originalkilden, og skal ikke siteres eller brukes som dokumentasjon på at kilden er lest. Kontroller alltid påstander mot primærkilden — se [../kilde_lenker/kilde_lenker.md](../kilde_lenker/kilde_lenker.md).

## APA 7-referanse

Puchinger, J., & Raidl, G. R. (2005). Combining metaheuristics and exact algorithms in combinatorial optimization: A survey and classification. I J. Mira & J. R. Álvarez (Red.), *Artificial intelligence and knowledge engineering applications: A bioinspired approach* (s. 41–53). Springer. (Lecture Notes in Computer Science, bind 3562)

## Verifisert mot

- SpringerLink: https://link.springer.com/chapter/10.1007/11499305_5
- Open-access preprint (TU Wien): https://www.ac.tuwien.ac.at/files/pub/puchinger-05.pdf
- DOI: 10.1007/11499305_5

## Type publikasjon

Bokkapittel / fagfellevurdert konferanseartikkel i Springer Lecture Notes in Computer Science (LNCS), bind 3562. Publisert i sammenheng med IWINAC 2005 (International Work-Conference on the Interplay Between Natural and Artificial Computation). Sidetall 41–53.

## Sammendrag

Artikkelen gir en taksonomi over hvordan metaheuristikker (genetiske algoritmer, tabu-søk, simulated annealing osv.) kan kombineres med eksakte algoritmer (branch-and-bound, MILP, dynamisk programmering) i kombinatorisk optimering. Forfatterne deler hybride tilnærminger inn i to hovedkategorier:

1. **Kollaborativ kombinasjon:** de to metodene kjører som separate moduler — enten sekvensielt (heuristikk produserer en startløsning som varmstarter en eksakt metode) eller parallelt (de to bytter informasjon underveis)
2. **Integrativ kombinasjon:** den ene metoden er innebygd som en komponent i den andre, f.eks. en LP-relaksering brukt inne i en lokal søk-prosedyre, eller large-neighborhood search der nabolagsutforskningen løses med en MIP

Forfatterne argumenterer for at hybrider ofte gir bedre løsninger enn rene metoder, fordi heuristikker og eksakte metoder har komplementære styrker: heuristikker er raske men gir ingen optimalitetsgaranti, mens eksakte metoder er trege men beviser optimalitet eller dual-grenser.

## Sentrale begreper og bidrag

- **Kollaborativ vs. integrativ hybrid**
- **Sekvensiell varmstart:** heuristikk → eksakt metode
- **Matheuristics:** samlebetegnelse for hybrider basert på matematisk programmering

## Relevans for LOG650-prosjektet

Legitimerer den valgte to-stegs-arkitekturen (heuristikk → MIP) som en kollaborativ sekvensiell hybrid. Selv om implementasjonen i prosjektet ikke bruker heuristikk-løsningen som varmstart for CBC (heuristikken og MIPen er kjørt uavhengig og brukes til *sammenligning*), er hovedideen — å bruke begge metoder for å belyse problemet fra to vinkler — direkte i tråd med Puchinger & Raidls rammeverk. Artikkelen gir også vokabularet (kollaborativ, sekvensiell) som metodekapittelet kan bruke.

**Forbedringsmulighet:** Hvis tid tillater, kunne heuristikk-løsningen brukes som faktisk varmstart for MIP via PuLPs `solve(initialValues=...)` — det ville gjort hybriden integrativ og potensielt redusert solver-tiden for Basis_85 (Not Solved ved 1 800 s).

## Hvor kilden brukes i rapporten

- Kapittel 2.0 Litteratur, avsnitt 2.2 (linje 154)
- Kan også siteres i kapittel 5.1 Metode for å begrunne hybridvalget

## Tilgang

- DOI: https://doi.org/10.1007/11499305_5
- Open-access PDF: https://www.ac.tuwien.ac.at/files/pub/puchinger-05.pdf
- Oria-søk: HiM har trolig SpringerLink-tilgang for LNCS
