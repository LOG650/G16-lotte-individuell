# Kvalitetsheving av FKB-TraktorvegSti før implementering i NVDB

Prosjektarbeid i **LOG650 Logistikk og KI** ved Høgskolen i Molde. Et planleggingsgrunnlag for hvordan Statens kartverk bør fordele og sekvensere kvalitetshevingen av datasettet FKB-TraktorvegSti før overføring til Nasjonal vegdatabank (NVDB).

| | |
| --- | --- |
| **Forfatter** | Lotte Picard (individuelt prosjekt) |
| **Fag** | LOG650 Logistikk og KI, Høgskolen i Molde |
| **Oppdragsgiver** | Statens kartverk, Region og samfunnskontakt |
| **Periode** | 12.01.2026 – 01.06.2026 |

## Problemstilling

357 kommuner skal kvalitetsheves ved 10 fylkeskartkontor med ulik kapasitet og deretter overføres til NVDB via en FME-automatisert prosess med begrenset manuell bemanning. 152 kommuner er i perioder låst av Geovekst-kartleggingsprosjekter. Oppgaven er et ressursallokerings- og produksjonsplanleggingsproblem: Hvordan bør de gjenstående kommunene fordeles og sekvenseres for kortest mulig total prosjektvarighet?

Analysen kombinerer tre metoder: en regelbasert **heuristikk** (tolkbar referanse), en **MIP-modell** i PuLP/CBC (matematisk optimering) og **Monte Carlo-simulering** (usikkerhet). Tre NVDB-scenarioer undersøkes, differensiert på FME-automasjonsgrad (85 %, 90 %, 96 %).

**Hovedfunn:** NVDB-overføringen er flaskehalsen, ikke kartkontor-fasen. Total varighet er 6,7–10 år ved realistisk automasjon og 2,7 år i optimistisk scenario, mens kartkontorene fullfører sitt arbeid innen 10–17 måneder uavhengig av scenario. Omfordeling av kommuner mellom kontor er ikke nødvendig for å redusere totalvarigheten.

## Mappestruktur

```
003 references/      Kilder og referanser
004 data/
  raw_data/          Rådata fra Kartverket + fylkeskart (GeoJSON)
  processed_data/    Vaskede data og resultatfiler (CSV)
  scripts/           All analysekode (Python)
005 report/
  rapport.md         Hovedrapporten
  figurer/           Figurer (PNG)
  _assets/           Bygge-oppsett for PDF (pandoc/LaTeX)
011–014              Faseleveranser (proposal, plan, review, rapport)
```

## Rapporten

Rapporten ligger i [`005 report/rapport.md`](005%20report/rapport.md). **Vedlegg B** i rapporten gir en fullstendig oversikt over hvilke script som produserer hvilke resultatfiler og figurer.

PDF bygges fra Markdown med pandoc + xelatex (kjør fra `005 report/`):

```
pandoc rapport.md -o rapport_LATEX.pdf --pdf-engine=xelatex \
  -f markdown-implicit_figures --lua-filter="_assets/figurer_float.lua" \
  -V lang=nb-NO -V geometry:margin=2.5cm -V fontsize=11pt -V linestretch=1.4 \
  -V mainfont="Georgia" -V monofont="Consolas" -H "_assets/latex_header.tex"
```

## Reproduser analysen

Krever **Python 3.13** med `pandas`, `numpy`, `openpyxl`, `matplotlib`, `geopandas` og `pulp` (CBC-solveren er innebygd i PuLP).

Scriptene i [`004 data/scripts/`](004%20data/scripts/) kjøres i denne rekkefølgen:

1. `vask_og_strukturer.py` — datavask og strukturering → CSV-ene i `processed_data/`
2. `heuristikk.py` — regelbasert baseline-skedulering
3. `monte_carlo.py` — usikkerhetsanalyse (500 iterasjoner × 3 scenarioer)
4. `mip_modell.py` — MIP-optimering (PuLP/CBC)
5. `mip_kapasitet_sensitivitet.py` — kapasitets-sensitivitet (18 kjøringer)
6. `monte_carlo_mip.py` — Monte Carlo på MIP-tildelingen
7. `heuristikk_tidbruk_sensitivitet.py`, `monte_carlo_tidbruk_sensitivitet.py`, `monte_carlo_automasjon_sensitivitet.py` — robusthetsanalyser
8. `figurer.py`, `figurer_resultater.py`, `figurer_usikkerhet.py`, `figurer_mip.py` — figurproduksjon
9. `sanity_check_data.py`, `sanity_check_mip.py` — kvalitetssikring

MIP-kjøringene kan ta fra minutter til flere timer avhengig av scenario og maskin.

## Data og opphavsrett

Rådataene kommer fra Statens kartverk (samferdselsavdelingens PowerBI-rapport, statistikk- og datainnsamlingsark) samt fylkesgrenser fra Geonorge (CC BY 4.0). Opphavsrettsbeskyttede kildekopier og generert PDF-output er holdt utenfor versjonskontroll (se `.gitignore`).
