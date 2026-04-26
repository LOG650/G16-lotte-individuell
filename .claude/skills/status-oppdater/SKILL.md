---
name: status-oppdater
description: Oppdater prosjektplan.json og regenerer STATUS.md
disable-model-invocation: true
argument-hint: "[valgfri beskrivelse av endringen]"
---

Brukeren vil oppdatere prosjektstatus. Følg denne prosedyren:

1. Spør hvilke endringer som skal gjøres i `012 fase 2 - plan/prosjektplan.json` (oppgave-IDer, fremdrift, status, kommentarer).
2. Gjør endringene i prosjektplan.json.
3. Kjør `python "004 data/scripts/generer_status.py"` for å regenerere STATUS.md.
4. Vis diff på begge filene.
5. Foreslå commit-melding i prosjektets stil (kort prefix + punktliste).

VIKTIG: Aldri rediger STATUS.md direkte — den auto-genereres fra prosjektplan.json.
