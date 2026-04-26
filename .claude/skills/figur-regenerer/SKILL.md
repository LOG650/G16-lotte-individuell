---
name: figur-regenerer
description: Regenerer figurer i 005 report/figurer/. Bruk når en figur eller dens kildedata er endret og PNG må oppdateres.
disable-model-invocation: true
argument-hint: "[1-19 | alle | mip | usikkerhet | resultater | deskriptive]"
---

Regenerer figurer basert på argumentet brukeren ga.

Tilgjengelige figur-genererings-skript:
- `figurer.py` — figur 1-6 (deskriptive)
- `figurer_resultater.py` — figur 7-10 (heuristikk)
- `figurer_usikkerhet.py` — figur 11-13 (Monte Carlo)
- `figurer_mip.py` — figur 14-19 (MIP, fig 17 droppet)

Logikk:
- Hvis argumentet er et tall mellom 1-19: kjør riktig skript basert på nummer-mapping over.
- Hvis argumentet er "alle" eller tomt: kjør alle 4 skript parallelt.
- Hvis argumentet er navn på et skript (f.eks. "mip" eller "usikkerhet"): match til skriptet.

Etter regenerering:
1. Vis hvilke PNG-er som ble oppdatert.
2. Hvis figur 16 (omfordelingsmatrise) er regenerert: minn brukeren om at akseteksten skal vise "Ansvarlig kartkontor", ikke "Hjemmekontor".
3. Tilby å lese den regenererte figuren med Read-verktøyet for visuell verifisering.
