# Peer-review-rapport – LOG650

## Forsideopplysninger

| | |
|---|---|
| **Gruppe som vurderer** | Lotte Picard |
| **Gruppe som blir vurdert** | Kjetil Tronstad Lund (enkeltforfatter) |
| **Tittel på rapporten** | *Optimal lagerbeholdning for BiteBurst: En SARIMA-basert tilnærming til prognose og sikkerhetslager* |
| **Dato** | 7. mai 2026 |

Rapporten er generert av Claude, og kvalitetssikret og gjennomgått av meg i etterkant	

Notis: Det er brukt noen ord som f.eks "likelihooden" i kap. 3.4 og 6.1, "random walk" i kap. 6.3, "baselines" i kap 7.1 og 9.6. Kan hende det er riktig å bruke engelsk uttrykk her, men om det finnes bedre norske uttrykk er det kanskje fint å bruke? I kap 7.1 Modellnøyaktighet refereres det til tabell 9 i første avsnitt, men det er flere tabeller (a, b, c osv). Mulig det skulle stått 9a her? Lotte

---

## Helhetsinntrykk

Rapporten er en gjennomarbeidet, godt strukturert og metodisk solid anvendelse av SARIMA-modellering på et avgrenset lagerstyringsproblem. Forfatteren demonstrerer god forståelse for både tidsrekketeori og lagerstyringsteori, og kobler de to gjennom en klar pipeline fra ADF-/ACF-diagnostikk via automatisert modellvalg til prediksjonsintervallbasert sikkerhetslager. Hovedstyrkene er en tydelig problemstilling, eksplisitte avgrensninger og antagelser, sammenligning mot en naiv baseline, residualdiagnostikk (Ljung-Box) og en åpen og selvkritisk diskusjon av MH-utsalgsstedets trendproblem. Hovedutfordringene er knyttet til (1) det relativt korte datagrunnlaget på 101 observasjoner kombinert med kun ett valideringsvindu på syv dager, (2) at den rullerende 7-dagers sumstrukturen i dataene har metodiske implikasjoner som er nevnt, men ikke fullt ut drøftet for tolkningen av prediksjonsintervallene, og (3) at litteraturgjennomgangen kunne identifisert tydeligere hva som skiller dette bidraget fra eksisterende SARIMA-anvendelser i detaljhandelen. Rapporten er gjennomgående velskrevet, og tabeller og figurer støtter argumentasjonen godt.

---

## Områdevis vurdering

### Innledning

**Styrker.** Innledningen (kap. 1) etablerer effektivt motivasjonen ved å kontrastere stockout og overlagring som de to grunnleggende avveiningene i lagerstyring, og knytter dette tydelig til SARIMA og BiteBurst-konteksten. Problemstillingen (s. 101 i rapporten) er presist formulert og operasjonalisert i to delspørsmål som direkte speiles i resultatkapitlet – dette gir god rød tråd. Avgrensninger (kap. 1.2) og antagelser (kap. 1.3) er eksplisitte og gjennomtenkte, og det er positivt at den opprinnelige antagelsen om manglende sesongvariasjon er korrigert med begrunnelse (kap. 1.3, "Ukessyklus").

**Forbedringspunkter.**
- Studiens *betydning og relevans* er argumentert fra et generelt logistikkperspektiv (lønnsomhet, kapitalbinding), men det fremgår ikke like klart hvorfor *akkurat dette* studiet – på simulerte spilldata – er verdt å gjennomføre. Et eget avsnitt som tydelig skiller mellom (a) metodisk bidrag (en reproduserbar pipeline) og (b) substansielt bidrag (innsikt om BiteBurst) ville styrket innledningen. Forslag: utvid s. 93 med én setning som plasserer bidraget i forhold til hva en reell bedrift ville hatt nytte av.
- Forskningsmålet er rent anvendt ("fastsette optimalt lagernivå"). Hvis det også er et metodologisk mål – f.eks. å vurdere om prediksjonsintervallbasert sikkerhetslager er bedre enn tradisjonell *z·σ_L* – kunne dette med fordel vært eksplisitt nevnt i innledningen, ikke kun antydet i kap. 2.3 og 5.1.

### Litteraturgjennomgang og teoretisk forankring

**Styrker.** Kap. 2 og 3 er sammenhengende og dekker det essensielle: ARIMA/SARIMA-fundamentet (Box et al.), pedagogisk gjennomgang (Hyndman & Athanasopoulos) og lagerstyringsteorien (Silver et al., Chopra & Meindl). Kap. 2.3 om integrering av prognose og lagerstyring er en faglig styrke fordi den begrunner det metodiske valget om å bruke prediksjonsintervaller direkte. Teorikapittelet (kap. 3) er stramt og inneholder de nødvendige formlene (ARIMA, SARIMA, AIC, sikkerhetslager) uten å bli oppslagsverkpreget.

**Forbedringspunkter.**
- *Identifikasjon av teoretiske/begrepsmessige hull*: Litteraturgjennomgangen oppsummerer eksisterende kunnskap, men peker ikke ut et klart forskningshull som motiverer studien. Det fremgår at SARIMA er etablert for daglige salgsdata i mat- og dagligvarehandel (s. 146), men da blir det uklart hva *dette* studiet bidrar med utover en ny anvendelse. Et avsnitt på 3–5 setninger som identifiserer hva som *ikke* er godt dekket i litteraturen (f.eks. samspillet mellom rullerende 7-dagerssum-strukturer og SARIMA, eller dokumenterte ulemper ved direkte prediksjonsintervallbasert sikkerhetslager), ville styrket forankringen.
- *Få kilder utover lærebøker*. Litteraturgrunnlaget hviler på fire lærebøker og ett spill. For en peer-reviewet faglig forankring av SARIMA i detaljhandel og hurtigmatbransjen ville et par fagartikler (gjerne empiriske studier på reelle salgsdata) gjort kapitlet mer overbevisende, særlig der det hevdes at "fellesnevneren er at daglige salgsdata […] viser en signifikant ukentlig sesongkomponent" (s. 146).
- *Metoder relevante for målene som ikke er valgt*: Holt-Winters, SARIMAX og ML-metoder nevnes først i kap. 9.6 (Diskusjon). Det ville være mer naturlig å introdusere disse alternativene i litteraturkapittelet og deretter begrunne valget av SARIMA i metodekapittelet, slik kriteriet "begrunnelse for valgte metoder" tilsier.

### Metode

**Styrker.** Metodevalgene (kap. 5.1) er eksplisitt og plausibelt begrunnet i to empiriske analyser (ADF og ACF) før modellvalget gjøres – dette er metodisk forbilledlig. Trenings-/valideringssplit (94/7) er klart beskrevet, MAPE er definert med formel, og sikkerhetslagerformelen (s. 298) er gjennomsiktig. Det er også positivt at parametersøkerommet for `auto_arima` rapporteres eksplisitt (kap. 6.2). Etiske hensyn er korrekt avklart i forsidedelen (data uten personopplysninger, ikke REK-pliktig).

**Forbedringspunkter.**
- *Implikasjoner av rullerende 7-dagerssummer for modelleringen*: Forfatteren erkjenner at strukturen skaper "konstruert artefakt" av høy lag-1-korrelasjon (s. 274, 310), men diskuterer ikke at SARIMA-tilpasning på *overlappende* summer formelt bryter med antagelsen om uavhengige innovasjoner i hvit-støy-leddet. I praksis kan dette føre til (a) underestimering av residualvarians og dermed for smale prediksjonsintervaller, og (b) misvisende AIC-sammenligninger. Forfatteren bør enten (i) drøfte om prediksjonsintervallbredden derfor undervurderer reell usikkerhet, eller (ii) vurdere om analysen burde vært gjort på rekonstruerte daglige tall (differanser mellom påfølgende 7-dagerssummer). Dette er et sentralt metodisk poeng som fortjener egen behandling.
- *Validering*: Med kun *én* tilbakeholdt 7-dagersperiode er MAPE-verdiene punktestimater og ikke statistisk robuste. En rullerende prognoseopprinnelse (rolling-origin / time-series cross-validation) – f.eks. fem til sju påfølgende 7-dagers vinduer – ville gitt et langt mer pålitelig bilde av modellytelsen og ville samtidig ha avdekket trendskiftet i MH som et systematisk fenomen, ikke bare en "siste-uke-effekt". Forslag: kort begrunnelse i kap. 5.1 for hvorfor dette ikke er gjort, eller bruk av minst ett ekstra valideringsvindu som sensitivitetsanalyse.
- *Validitet og reliabilitet* er kun implisitt drøftet (gjennom datarensing, residualdiagnostikk og forbehold om simuleringsdata). Et eksplisitt avsnitt i metoden om intern/ekstern validitet og reliabilitet ville gjort kriteriedekningen tydelig.
- *Tilstrekkelighet av 101 observasjoner*: Begrenset i forhold til SARIMA(p,d,q)(P,D,Q,7) – med noen modeller har relativt mange parametre. Dette er nevnt i diskusjonen, men kunne også vært diskutert som forhåndsbegrensning i metoden, ikke kun som forklaring i etterkant.

### Analyse og resultater

**Styrker.** Analysekapittelet er grundig og strukturert. Tabell 9a–c gir et komplett bilde av modellytelsen med MAPE for SARIMA, MAPE for naiv baseline og Ljung-Box-diagnostikk – dette er en betydelig metodisk styrke som flere peer-reviewede tidsrekkearbeider ville hatt nytte av. Resultatkapittelet (kap. 8) leverer det problemstillingen lover: konkrete lagernivåer per produkt per utsalgssted med tydelig skille mellom punktprognose og sikkerhetslager. Resultatene er internt konsistente: avvikene mellom utsalgssteder (LM høyest, GM lavest) er konsistent forklart, og koblingen mellom høy *σ* (kap. 5.2) og høyt sikkerhetslager (kap. 8) er overbevisende.

**Forbedringspunkter.**
- I Tabell 9a er åtte modeller med MAPE > 8 %. To av dem (GM Pølse 19,9 %, MH Pommes frites 21,6 %) er i kategorien som vanligvis betegnes som *uakseptabel* prognosenøyaktighet i operasjonell sammenheng. Resultatkapittelet kunne hatt en mer eksplisitt vurdering av om disse anbefalingene faktisk *bør brukes* eller om de er upålitelige. Forfatteren foreslår "konservativt påslag" (s. 636), men kvantifiserer ikke dette.
- *Plassering av Tabell 2*: Den ukentlige prognosen per utsalgssted (Tabell 2 i kap. 4 Casebeskrivelse) er hentet fra resultatene i kap. 8. Selv om dette er nyttig for kontekst, gjør det at leseren introduseres for resultater før metoden er forklart. Forslag: enten flytt tabellen til kap. 8 og henvis tilbake derfra, eller signaliser tydelig at dette er en *foregrep*.
- *Figurer*: Det er kun fire figurer i hele rapporten. En figur som viser ACF/PACF for et representativt produkt (motiverer SARIMA-valget visuelt), eller en residualplott for en av modellene med Ljung-Box-grenseverdi, ville styrket den empiriske argumentasjonen i kap. 5.1 og 7.5.
- *Tabell 9c*: Mange p-verdier er svært nær 1 (1,0000). Dette kan signalisere at testen har lav effekt med så små utvalg, eller at residualene faktisk er nær perfekt hvit støy. En kort kommentar om hvordan disse skal tolkes ville hjulpet leseren.

### Diskusjon

**Styrker.** Diskusjonen er den faglig sterkeste delen av rapporten. Forfatteren skiller systematisk mellom modellusikkerhet og iboende etterspørselsvarians (kap. 9.1), gir en god strukturanalyse av MH-trenden (kap. 9.2), og drøfter kritisk validiteten av normalfordelingsantagelsen for sikkerhetslagerberegningen (kap. 9.4). Sammenligningen med naive baseline (kap. 9.6) er en konkret operasjonalisering av "metodefordel" og styrker konklusjonene betydelig.

**Forbedringspunkter.**
- *Uventede funn pekes ut, men forklares delvis*: At "samme produkt presterer svært forskjellig på ulike utsalgssteder" (kap. 9.3) er et uventet og interessant funn, men forklaringen ("ustabil trend ved svake utsalgssteder") forblir kvalitativ. Et forsøk på empirisk underbygging – f.eks. ved å vise variasjonskoeffisienten eller en strukturbruddtest (Chow/CUSUM) for de fire serienes Pommes frites – ville styrket argumentet.
- *Implikasjoner for praksis* er godt dekket for BiteBurst, men er litt tynnere for *teori* og *policy*. F.eks.: Hva sier resultatene om bruken av prediksjonsintervallbasert sikkerhetslager *generelt*? Bekrefter eller utfordrer de litteraturen (Silver et al., 2017)?
- *Begrensninger ved 101-observasjoners datagrunnlag*: Diskusjonen i kap. 9.2 berører dette indirekte gjennom MH-eksempelet, men en mer eksplisitt drøfting av hvor mange observasjoner SARIMA(p,d,q)(P,D,Q,7) "egentlig" trenger for stabil parameterestimering ville løftet den metodiske refleksjonen.
- *Manglende drøfting av implikasjon av rullerende-sum-strukturen*: Det er noe paradoksalt at forfatteren erkjenner at strukturen skaper artefaktisk autokorrelasjon (kap. 5.1, 5.2), men ikke vender tilbake til om dette har påvirket prediksjonsintervallene som hele sikkerhetslageret er bygget på. Dette er en vesentlig nyanse som bør med.

### Konklusjon

**Styrker.** Konklusjonen (kap. 10) er konsis og strukturert direkte rundt de to delspørsmålene fra kap. 1.1, og oppsummerer både modellvalget og lagernivåene med konkrete tall. Refleksjon over begrensninger (MH-trenden) er beholdt, og forslagene til videre arbeid (validering mot reelle data, SARIMAX, kortere rullerende treningsvindu) er forankret i diskusjonens funn.

**Forbedringspunkter.**
- *Bidrag til teori og praksis*: Konklusjonen oppsummerer hva som er funnet, men sier mindre om hva *nytt* studien bidrar med utover BiteBurst-konteksten. En eksplisitt setning om metodisk overføringsverdi (som er nevnt i kap. 9.5) ville rundet av rapporten godt.
- *Begrensninger* er kort omtalt for MH, men de mer grunnleggende begrensningene (simuleringsdata, kort tidsserie, ett valideringsvindu, overlappende sumstruktur) som er drøftet i tidligere kapitler kunne med fordel vært samlet i en kort punktliste i konklusjonen.
- *Forslag til videre forskning*: Forslagene er fornuftige, men kunne vært mer ambisiøse (f.eks. eksperimentell sammenligning av SARIMA mot Holt-Winters og ML-metoder på samme datasett, eller et eget studium av rolling-origin-validering).

### Skriveflyt, formelle aspekter og helhetsvurdering

**Styrker.** Språket er faglig korrekt, presist og lett å følge. Strukturen følger en klassisk vitenskapelig oppbygning, og kryssreferansene mellom kapitler (f.eks. "jf. kapittel 5.1") fungerer godt. Tabellnummerering og figurnummerering er konsistent. Bibliografien er kort, men oppført i tråd med APA 7. Bruken av matematiske formler er korrekt og pedagogisk plassert. Bruken av forkortelser (SARIMA, MAPE, AIC, ADF, GM/HK/LM/MH) er introdusert ved første bruk og brukt konsekvent.

**Forbedringspunkter.**
- *Forsideopplysninger* er ufullstendige: studiepoeng, veileder, antall sider og dato på publiseringsavtalen er tomme felter (s. 5, 33, 35, 41). Disse må fylles inn før innlevering.
- *Tabellformatering*: I de deskriptive tabellene (Tabell 4–7) og lagernivåtabellene (Tabell 10–13) er det inkonsistent kolonnejustering for produktnavn med ulike lengder ("Pommes frites", "Hamburger", "Iskrem"). Mindre kosmetisk, men påvirker lesbarheten i markdown-rendering.
- *Manglende figurliste/tabelliste*: For en rapport av denne størrelsen (12 numererte tabeller, 4 figurer) ville en figurliste og tabelliste etter innholdsfortegnelsen vært nyttig.
- *Visuelt støttemateriale*: Som nevnt under "Analyse og resultater" er rapporten relativt fattig på figurer i forhold til tabeller. Spesielt diagnostiske figurer (ACF/PACF, residualplott) mangler. Figur 4 er nevnt som visuell oppsummering, men det er ikke spesifisert om den er sortert (etter utsalgssted, etter MAPE, etter volum) – informasjon som ville hjulpet tolkningen.
- *Originalitet*: Bidraget er først og fremst metodisk demonstrasjon på en uvanlig datakilde (et dataspill), noe som er en interessant og original vinkling. Originaliteten ville fremstått tydeligere dersom innledningen og litteraturkapittelet eksplisitt rammet inn "simulerte spilldata som testbenk for logistikkmetodikk" som et bevisst valg, ikke kun som en pragmatisk løsning.

---

*Vurderingskriteriene er anvendt i sin helhet; ingen er utelatt som åpenbart irrelevante. Datainnsamlingsbeskrivelsen i kriteriet "Metode" er behandlet på samme måte som de øvrige punktene fordi rapporten faktisk inneholder en datainnsamlingsprosess (manuell avlesning fra spillgrensesnittet).*
