---
name: commit-rapport
description: Stage rapport.md og figurer, foreslå commit-melding i prosjektstilen
disable-model-invocation: true
argument-hint: "[valgfri beskrivelse av endringen]"
---

Lag en commit for endringer i rapporten:

1. Kjør `git status` og `git diff` for å se hva som er endret.
2. Identifiser hva commiten gjelder (ny seksjon, korrigering, polering, terminologi-endring osv.).
3. Foreslå commit-melding i prosjektets stil:
   - Kort prefix på første linje (eks: "konsistens-fiks:", "1.0 Innledning:", "polering:", "terminologi:")
   - ASCII (oe/aa/ae) i commit-meldingen — følg mønsteret fra `git log --oneline -10`
   - Punktliste med spesifikke endringer
   - Avslutt med "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
4. Stage kun relevante filer:
   - `005 report/rapport.md` for tekstendringer
   - `005 report/figurer/*.png` hvis figurer er regenerert
   - Aldri stage `.claude/settings.local.json` (per-bruker-config)
5. Bekreft commit-melding med brukeren før kjøring.
6. Etter commit: vis `git log --oneline -3` for å verifisere.
