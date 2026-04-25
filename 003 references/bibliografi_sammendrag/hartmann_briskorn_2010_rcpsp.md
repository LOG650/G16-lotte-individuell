# Hartmann & Briskorn (2010) — A Survey of Variants and Extensions of the RCPSP

## APA 7-referanse

Hartmann, S., & Briskorn, D. (2010). A survey of variants and extensions of the resource-constrained project scheduling problem. *European Journal of Operational Research, 207*(1), 1–14. https://doi.org/10.1016/j.ejor.2009.11.005

## Verifisert mot

- ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S0377221709008558
- HSBA arbeidsversjon (open access): https://www.hsba.de/fileadmin/user_upload/bereiche/_dokumente/6-forschung/profs-publikationen/Hartmann_2010_A_Survey_of_Variants_and_Extensions_of_the_Resource-Constraints_Project_Scheduling_Problem.pdf
- DOI: 10.1016/j.ejor.2009.11.005

## Type publikasjon

Oversiktsartikkel (survey) i fagfellevurdert tidsskrift (*European Journal of Operational Research*). En av de mest siterte introduksjonene til RCPSP-litteraturen — over 900 siteringer pr. 2026.

## Sammendrag

Forfatterne gir en systematisk gjennomgang av Resource-Constrained Project Scheduling Problem (RCPSP) og dets utvidelser. Standard-RCPSP består av aktiviteter som skal planlegges under presedens- og ressursbetingelser, slik at makespan minimeres. Forfatterne påpeker at standardmodellen er for restriktiv for de fleste praktiske anvendelser, og artikkelen klassifiserer derfor utvidelser langs tre hoveddimensjoner:

1. **Aktivitetskonseptet:** preemptiv vs. ikke-preemptiv, multimodus, setup-tider, alternative aktivitetsformer
2. **Presedensrelasjoner:** generaliserte/min-max-tidslagrelasjoner, finish-to-start, start-to-start mv.
3. **Ressursbetingelser:** fornybare, ikke-fornybare, dobbeltbegrensede, kapasitetsvarierende ressurser, tidsvinduer

I tillegg dekkes alternative målfunksjoner (NPV, ressursutjevning, tardiness) og multiprosjekt-scheduling. Artikkelen er sentral for å plassere et konkret problem i en større kontekst og finne relevant løsningslitteratur.

## Sentrale begreper og bidrag

- **RCPSP:** standard-formulering med aktiviteter, presedens, fornybare ressurser, makespan-minimering
- **Klassifikasjonsskjema:** tredimensjonal taksonomi (aktiviteter / presedens / ressurser)
- **Tidsvinduer (time windows / time-lag):** generalisering av presedens som tillater min-max-avstand mellom aktiviteter — eksakt det som trengs for Geovekst-låsninger
- **Multimodus-RCPSP (MRCPSP):** flere alternative måter å utføre samme aktivitet på, med ulik ressursbruk

## Relevans for LOG650-prosjektet

Artikkelen er en av to grunnpilarer (sammen med Pinedo) for å begrunne at TraktorvegSti-problemet er en RCPSP-variant. Klassifikasjonen gir et anerkjent rammeverk for å beskrive modellen i metodekapittelet:

- **Aktiviteter** = de 357 kommunene
- **Ressurser** = de 10 kartkontorene (fornybare, kapasitetsvarierende mellom kontor)
- **Tidsvinduer** = Geovekst-låseperioder (kommune kan ikke startes i låst periode)
- **Nedstrøms kapasitetsbegrensning** = NVDB-overføring (0,5 årsverk delt på alle kommuner)
- **Målfunksjon** = makespan

Det finnes en oppdatert utgave fra 2022 (samme tidsskrift, EJOR 297(1)) som er relevant hvis bibliografien skal styrkes ytterligere.

## Hvor kilden brukes i rapporten

- Kapittel 2.0 Litteratur, avsnitt 2.1 (linje 150)
- Kan utvides i kapittel 3.0 Teori for å begrunne RCPSP-formaliseringen mer eksplisitt

## Tilgang

- DOI: https://doi.org/10.1016/j.ejor.2009.11.005
- Open-access arbeidsversjon: HSBA-lenken over (samme innhold som publisert versjon)
- Oria-søk: artikkeltittel via HiM-bibliotek; HiM har EJOR-abonnement via Elsevier
