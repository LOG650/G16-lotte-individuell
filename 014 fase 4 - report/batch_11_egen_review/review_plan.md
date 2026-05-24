# Plan: Uavhengig multi-agent review av rapport (post-batch-10)

## Context

Batch 10 er ferdig (commit 94c8c61) og fase 4-rapport-arbeidet er substansielt fullført. Med ~1 uke til innlevering 2026-06-01 ønsker brukeren en uavhengig review for å fange ting batch-systemet (A1-A5, B1-B3, C1, C3-C6, 9, 10) kan ha normalisert eller missert. Tidligere oppdaget batch 10 selv fem en-dash-inkonsistenser som batch 9 hadde missed, så det er god grunn til å tro at andre subtilere ting fortsatt ligger der.

Mål: identifisere alvorlige funn som *kan* fikses før innlevering uten å destabilisere rapporten. Ikke uttømmende lekehunds-liste; fokus på det som faktisk påvirker karakter eller leserforståelse.

## Recommended approach

Fire uavhengige `Explore`-subagenter kjøres **parallelt** i én melding. Hver har skarpt mandat og rapporterer maks ~500 ord, sortert etter alvorlighet (kritisk / viktig / kosmetisk). Etter at alle er ferdige konsoliderer jeg funnene og presenterer for brukeren:

- en deduplisert prioritetsliste,
- forslag til hva som bør fikses (få, fokuserte endringer),
- hva som bør avvises eller utsettes til etter innlevering.

Brukeren beslutter hvilke funn som faktisk skal handles på. Selve fiksene gjøres i en oppfølgings-økt (potensielt som «batch 11»).

### Agent 1: Faglig kvalitet og argumentasjon

**Mandat:** Kritisk gjennomgang av om konklusjoner og resonnement holder. Spesielt 7.x (Analyse og resultater), 8.x (Diskusjon), 9.0 (Konklusjon). Identifiser ubegrunnede påstander, sirkulær argumentasjon, manglende koblinger mellom problemstilling og funn, eller funn som ikke faktisk er støttet av analysen.

**Output:** 8-15 funn med severity (kritisk/viktig/kosmetisk), fil:linje-referanse, kort forklaring.

### Agent 2: Matematiske utregninger og formler

**Mandat:** Verifiser at formler i rapporten matcher implementasjonen i scripts:
- MIP-formulering (6.2) mot `004 data/scripts/mip_modell.py`
- NVDB-formel `Throughput = 0,5 × Takt / (1 − auto)` mot `nvdb_overfoering.csv`
- Kapasitetsformel `K × 37,5 × (245/260) / 260` mot `heuristikk.py`
- Tidbruk-formel `0,9035 × Km_Kurve + 0,6510 × ArealLand_Km²` mot `vask_og_strukturer.py`
- Månedlig vs daglig konvensjon-konsistens

**Output:** liste over avvik (formel-tekst vs kode), evt. derivasjonsfeil. Hvis alt stemmer: kort bekreftelsesrapport (1-2 avsnitt).

### Agent 3: Sensor-perspektiv / red-team

**Mandat:** Les hele rapporten som ekstern sensor. List de 5-10 mest sannsynlige spørsmålene/kritikkpunktene en sensor ville reist. Spesielt: er hovedbudskapet («NVDB er flaskehalsen») godt nok beskyttet mot vanlige innvendinger? Er antagelser eksplisitte? Hvor er argumentasjonen tynnest?

**Output:** sortert liste av sensor-spørsmål med tekst-referanse og forslag til hvordan rapporten kan adressere det proaktivt.

### Agent 4: Språk og lesbarhet (ny pass)

**Mandat:** Identifiser steder hvor språket er tungt, uklart, eller har gjentagelser batch 9 ikke fanget. Spesielt etter B1-merge (kap 7+8) og batch C1 (akademisk bidrag i 8.7) der nye seksjoner har kommet til. Ikke pirk på stilistiske valg — fokus på lesbarhet.

**Output:** maks 10 språk-funn med fil:linje, eksisterende formulering, forslag til omformulering.

## Critical files

- `005 report/rapport.md` — hovedfilen alle agenter leser
- `004 data/scripts/mip_modell.py`, `heuristikk.py`, `vask_og_strukturer.py` — kun Agent 2
- `004 data/processed_data/nvdb_overfoering.csv`, `tidbruk_konstanter.csv`, `oppsummering_mip_vektet.csv` — kun Agent 2
- `CLAUDE.md` — alle agenter får dette for kontekst om LÅSTE beslutninger, kalibrering, m.m.

## Eksisterende verktøy som gjenbrukes

- `Agent` med `subagent_type: Explore` — read-only, ingen risiko for utilsiktede endringer
- `Skill: verifiser-tall` — kan brukes av meg etter agent-rapportene for å dypsjekke spesifikke tall-funn

## Workflow etter agentene har levert

1. Jeg leser alle 4 rapporter
2. Dedupliserer overlappende funn (sensor-perspektiv og faglig kvalitet vil delvis overlappe)
3. Sorterer kombinert liste etter severity og «kost å fikse»
4. Presenterer brukeren en konsolidert liste: hva bør fikses (få, høyverdige), hva bør avvises, hva bør utsettes
5. Brukeren beslutter scope for evt. oppfølgings-batch

## Verifisering

- Etter at alle 4 agenter er ferdige: hver rapport leses og scores for relevans (er funnet ekte eller en falsk positiv?)
- Funn som peker til konkrete fil:linje er trygge å vurdere; brede påstander krever ekstra sjekk
- Vi committer ingen endringer som resultat av reviewen i denne sesjonen — alt går gjennom brukerens godkjenning per funn

## Estimert tid

- Agent-kjøring (parallelt): 10-20 min wall clock
- Konsolidering og presentasjon: 10-15 min
- **Sum: ~30 min før beslutning om oppfølgings-batch**

Oppfølgings-batch (hvis bestemt) estimeres separat basert på antall + scope av godkjente fikser.
