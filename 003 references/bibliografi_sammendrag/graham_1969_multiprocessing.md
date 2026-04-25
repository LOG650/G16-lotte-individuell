# Graham (1969) — Bounds on Multiprocessing Timing Anomalies

## APA 7-referanse

Graham, R. L. (1969). Bounds on multiprocessing timing anomalies. *SIAM Journal on Applied Mathematics, 17*(2), 416–429. https://doi.org/10.1137/0117039

> **Merk:** I rapportens nåværende bibliografi står "multiprocessor" — korrekt tittel er "**multiprocessing**" (verbalsubstantiv, ikke maskinen). Bør rettes før innlevering.

## Verifisert mot

- SIAM Publications Library: https://epubs.siam.org/doi/10.1137/0117039
- ACM Digital Library: https://dl.acm.org/doi/10.1137/0117039
- DOI: 10.1137/0117039

## Type publikasjon

Forskningsartikkel i fagfellevurdert tidsskrift (*SIAM Journal on Applied Mathematics*). Klassisk og hyppig sitert.

## Sammendrag

Artikkelen analyserer hvordan list-scheduling-heuristikker oppfører seg når et sett av oppgaver med presedensbetingelser (DAG) skal kjøres på flere identiske prosessorer. Graham viser den paradoksale observasjonen at å øke antall prosessorer, redusere prosesseringstider eller fjerne presedensbetingelser kan i verste fall *forlenge* makespan — såkalte "timing anomalies".

Hovedresultatet er en eksakt verste-tilfelle-grense: for vilkårlig list-scheduling er makespan ≤ (2 − 1/m) · OPT, der m er antall prosessorer. For den spesielle varianten **Longest Processing Time (LPT)** — der oppgaver sorteres i synkende rekkefølge etter prosesseringstid før de tildeles fortløpende til den prosessoren som blir tidligst ledig — er grensen 4/3 · OPT (uten presedensbetingelser).

## Sentrale begreper og bidrag

- **List scheduling:** dispatching-regel som tildeler oppgaver fortløpende til ledige ressurser etter en prioritert liste
- **Longest Processing Time (LPT):** liste sortert synkende etter prosesseringstid; gir 4/3-garanti
- **Multiprocessor timing anomalies:** kontraintuitiv oppførsel der "mer ressurs" gjør planen verre
- **(2 − 1/m)-grense:** worst-case ratio for vilkårlig list-scheduling

## Relevans for LOG650-prosjektet

Heuristikken i `004 data/scripts/heuristikk.py` bruker en LPT-variant (sortering etter størst gjenstående arbeidsmengde først). Graham-grensen på 4/3 forklarer teoretisk hvorfor heuristikken ligger så nær MIP-løsningen i resultatene (faktisk gap <2,2 % på makespan, jf. tabell i CLAUDE.md). Tidsvinduer fra Geovekst-låsninger gir tilleggsbetingelser som *kan* svekke 4/3-garantien i verste tilfelle, men empirisk holder nær-optimaliteten i alle tre NVDB-scenarioer.

## Hvor kilden brukes i rapporten

- Kapittel 6.0 / 7.1 (omtrent linje 406): omtaler Regel 2 i heuristikken som en LPT-variant og siterer Graham (1969) for 4/3-garantien

## Tilgang

- DOI: https://doi.org/10.1137/0117039
- Fritt tilgjengelig PDF (ofte): https://people.irisa.fr/Sophie.Pinchinat/AA/Graham1969SIAM.pdf
- Oria-søk: tittel "Bounds on Multiprocessing Timing Anomalies", forfatter Graham, R. L.
