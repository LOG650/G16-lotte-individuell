---
name: sjekk-konsistens
description: Konsistens-sjekk A av rapport.md mot CSV-er, figurer og bibliografi
---

Kjør konsistens-sjekk A på 005 report/rapport.md:

1. **Tall-konsistens**: verifiser hovedtall mot CSV-er i `004 data/processed_data/`:
   - Heuristikk-resultater: `oppsummering_scenarioer.csv` (10,08 / 6,72 / 2,69 år)
   - MIP-resultater: `oppsummering_mip_vektet.csv` (10,17 / 6,75 / 2,75 år; status; omfordelinger)
   - Monte Carlo: `monte_carlo_summary.csv` (P5/P50/P95 totalvarighet og kartkontor-dager)
   - MIP MC: `monte_carlo_mip_summary.csv`
   - Sensitivitet: `oppsummering_sensitivitet.csv` (S0-S5 × 3 scenarioer)
   - Tidbruk-skala: `monte_carlo_tidbruk_summary.csv`
   - Automasjon-std: `monte_carlo_automasjon_summary.csv`
   - Master: `master_kommuner.csv` (357 kommuner, 62 ferdig, 48 påbegynt, 247 ikke startet)
   - Kapasitet: `kapasitet_kontorer.csv` (327 ukesverk, fordeling 22-52)

2. **Figur-referanser**: alle 18 figurer (1-19, fig 17 droppet) skal være referert minst én gang. Sjekk at figurnumrene i tekst matcher filnavn.

3. **Bibliografi**: alle 6 bibliografi-entries skal ha minst én inline-sitering. Alle inline-siteringer skal ha bibliografi-entry.

4. **Datoer/milepæler**: STARTDATO 2026-05-01, peer review 27-29.04.2026, innlevering 01.06.2026, ferdig kartkontor heuristikk 2027-09-16.

5. **Interne arbeidskoder**: søk etter V1/V2/V3, sanity_check, Bolk[A-F], jobb #, review-funn, arkiv_pre — disse skal IKKE være i sluttproduktet.

Rapporter funn som nummerert avviksliste med:
- Linjenummer
- Hva som står
- Hva CSV/data sier
- Foreslått fix

Skill mellom kritiske avvik (matematiske feil) og presisering (uklarheter).
