---
name: sanity
description: Kjør sanity_check_data.py og sanity_check_mip.py og rapporter funn
---

Kjør integritetsjekkene på dataene og MIP-modellen:

1. Kjør `python "004 data/scripts/sanity_check_data.py"` — sjekker datavask-konsistens (Status vs Gjenstaaende, Geovekst, fylke-mapping).
2. Kjør `python "004 data/scripts/sanity_check_mip.py"` — sjekker MIP-bibetingelser mot tidsplan-CSV.
3. Rapporter funn som kort liste:
   - Forventede inkonsistenser (allerede dokumentert i CLAUDE.md): markér som kjente.
   - Nye/uventede funn: flagg tydelig.
4. Hvis nye funn dukker opp, foreslå hvordan de bør håndteres (rotårsaks-fiks vs. patch).

Kjør begge skriptene parallelt hvis mulig.
