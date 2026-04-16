"""
Genererer STATUS.md fra prosjektplan.json og processed data.
Kjør dette scriptet hver gang prosjektplanen oppdateres for å holde STATUS.md i synk.
"""

import json
import os
import sys
import io
from datetime import datetime, date
import pandas as pd

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Stier
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
JSON_PATH = os.path.join(BASE_DIR, '012 fase 2 - plan', 'prosjektplan.json')
STATUS_PATH = os.path.join(BASE_DIR, 'STATUS.md')
DATA_DIR = os.path.join(BASE_DIR, '004 data', 'processed_data')

STATUS_IKON = {
    'Ferdig': '✅',
    'Pågående': '🔄',
    'Ikke startet': '⏳',
}

RISIKO_FARGE = {
    'Aktiv': '🟡',
    'Redusert': '🟢',
    'Realisert': '🔴',
    'Lukket': '⚪',
}


def les_json():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def les_master_data():
    """Les nøkkeltall fra processed data hvis tilgjengelig."""
    master_path = os.path.join(DATA_DIR, 'master_kommuner.csv')
    kap_path = os.path.join(DATA_DIR, 'kapasitet_kontorer.csv')

    if not (os.path.exists(master_path) and os.path.exists(kap_path)):
        return None, None

    master = pd.read_csv(master_path)
    kap = pd.read_csv(kap_path)
    return master, kap


def beregn_dager_til(dato_str, fra_dato):
    """Beregn antall dager fra en dato til en annen."""
    maaldato = datetime.strptime(dato_str, '%Y-%m-%d').date()
    return (maaldato - fra_dato).days


def format_dato(iso_dato):
    """Konverter ISO-dato til dd.mm-format."""
    d = datetime.strptime(iso_dato, '%Y-%m-%d')
    return d.strftime('%d.%m')


def fase_emoji(status):
    return STATUS_IKON.get(status, '❓')


def generer(plan, master, kap):
    i_dag = date.today()
    p = plan['prosjekt']

    # Finn nåværende fase og neste milepæl
    naavaerende_fase = next((f for f in plan['faser'] if f['status'] == 'Pågående'), None)
    neste_milepael = next((m for m in plan['milepaeler'] if m['status'] != 'Ferdig'), None)

    md = []
    md.append(f"# Prosjektstatus")
    md.append("")
    md.append(f"**Prosjekt:** {p['tittel']}  ")
    md.append(f"**Fag:** {p['fag']} | **Institusjon:** {p['institusjon']}  ")
    md.append(f"**Prosjektleder:** {p['prosjektleder']} | **Kunde:** {p['kunde']}  ")
    md.append(f"**Periode:** {p['startdato']} → {p['sluttdato']}  ")
    md.append(f"**Sist oppdatert:** {i_dag.isoformat()}")
    md.append("")
    md.append("> Denne fila er auto-generert fra `012 fase 2 - plan/prosjektplan.json`. Kjør `python \"004 data/scripts/generer_status.py\"` for å oppdatere.")
    md.append("")
    md.append("---")
    md.append("")

    # Overordnet status
    md.append("## Overordnet status")
    md.append("")
    if naavaerende_fase:
        md.append(f"- **Nåværende fase:** Fase {naavaerende_fase['id']} – {naavaerende_fase['navn']}")
    if neste_milepael:
        dager = beregn_dager_til(neste_milepael['dato'], i_dag)
        md.append(f"- **Neste milepæl:** {neste_milepael['navn']} – {neste_milepael['dato']} ({dager} dager)")
    sluttdato_dager = beregn_dager_til(p['sluttdato'], i_dag)
    md.append(f"- **Dager igjen til innlevering:** {sluttdato_dager}")
    md.append(f"- **Kritisk linje:** {' → '.join(plan.get('kritisk_linje', []))}")
    md.append("")

    # Faseoversikt
    md.append("### Faseoversikt")
    md.append("")
    md.append("| Fase | Periode | Status | Fremdrift |")
    md.append("|------|---------|--------|-----------|")
    for f in plan['faser']:
        ikon = fase_emoji(f['status'])
        periode = f"{format_dato(f['startdato'])} – {format_dato(f['sluttdato'])}.{f['startdato'][2:4]}"
        md.append(f"| {f['id']}. {f['navn']} | {periode} | {ikon} {f['status']} | {f.get('fremdrift_prosent', 0)}% |")
    md.append("")

    md.append("---")
    md.append("")

    # Milepæler
    md.append("## Milepæler")
    md.append("")
    md.append("| Milepæl | Dato | Status |")
    md.append("|---------|------|--------|")
    for m in plan['milepaeler']:
        ikon = fase_emoji(m['status'])
        navn = f"**{m['navn']}**" if m == neste_milepael else m['navn']
        dato = f"**{m['dato']}**" if m == neste_milepael else m['dato']
        status_tekst = '⏳ Neste' if m == neste_milepael else f"{ikon} {m['status']}"
        md.append(f"| {navn} | {dato} | {status_tekst} |")
    md.append("")

    md.append("---")
    md.append("")

    # Oppgaver per fase
    for f in plan['faser']:
        if f['status'] == 'Ferdig':
            continue  # Hopp over ferdige faser i den detaljerte listen
        md.append(f"## Oppgaver – Fase {f['id']} ({f['navn']})")
        md.append("")
        md.append("| ID | Oppgave | Periode | Status | % | Kommentar |")
        md.append("|----|---------|---------|--------|---|-----------|")
        for o in f['oppgaver']:
            ikon = fase_emoji(o['status'])
            periode = f"{format_dato(o['startdato'])} – {format_dato(o['sluttdato'])}"
            kommentar = o.get('kommentar', '')
            md.append(f"| {o['id']} | {o['navn']} | {periode} | {ikon} {o['status']} | {o.get('fremdrift_prosent', 0)}% | {kommentar} |")
        md.append("")

    # Ferdige faser - vis kun summert
    ferdige = [f for f in plan['faser'] if f['status'] == 'Ferdig']
    if ferdige:
        md.append("## Ferdige faser (sammendrag)")
        md.append("")
        for f in ferdige:
            md.append(f"- **Fase {f['id']} – {f['navn']}** ({f['startdato']} → {f['sluttdato']}): {len(f['oppgaver'])} oppgaver, milepæl `{f['milepael']['navn']}` nådd {f['milepael']['dato']}")
        md.append("")

    md.append("---")
    md.append("")

    # Leveranser
    md.append("## Leveranser")
    md.append("")
    md.append("| Leveranse | Fase | Status |")
    md.append("|-----------|------|--------|")
    for lev in plan.get('leveranser', []):
        ikon = fase_emoji(lev['status'])
        md.append(f"| `{lev['fil']}` | {lev['fase']} | {ikon} {lev['status']} |")
    md.append("")

    md.append("---")
    md.append("")

    # Risikostatus
    md.append("## Risikostatus")
    md.append("")
    md.append("| ID | Risiko | S | K | Status |")
    md.append("|----|--------|---|---|--------|")
    for r in plan['risikoer']:
        farge = RISIKO_FARGE.get(r['status'], '⚪')
        s = r['sannsynlighet'][0]  # H/M/L
        k = r['konsekvens'][0]
        md.append(f"| {r['id']} | {r['navn']} | {s} | {k} | {farge} {r['status']} |")
    md.append("")

    md.append("---")
    md.append("")

    # Nøkkeltall fra data
    if master is not None and kap is not None:
        md.append("## Nøkkeltall fra data")
        md.append("")
        total_lenker = int(master['Antall_Lenker'].sum())
        gjenstaaende = int(master['Gjenstaaende_Lenker'].sum())
        antall_laast = int(master['Er_Laast'].sum())
        status_dist = master['Status'].value_counts().to_dict()

        md.append(f"- **{len(master)}** kommuner totalt")
        md.append(f"- **{len(kap)}** kartkontorer")
        md.append(f"- **{total_lenker:,}** lenker totalt".replace(',', ' '))
        md.append(f"- **{gjenstaaende:,}** gjenstående lenker".replace(',', ' '))
        md.append(f"- **{antall_laast}** kommuner låst av Geovekst-prosjekter")
        md.append(f"- Status: {status_dist.get('Ferdig', 0)} ferdig kvalitetshevet, {status_dist.get('Påbegynt', 0)} påbegynt, {status_dist.get('Ikke påbegynt', 0)} ikke startet")
        md.append("")

        md.append("### Kapasitet per kartkontor")
        md.append("")
        md.append("| Kontor | Kommuner | Lenker | Gjenstående | Låst | Ukesverk |")
        md.append("|--------|----------|--------|-------------|------|----------|")
        for _, row in kap.sort_values('Kartkontor').iterrows():
            kontor = row['Kartkontor']
            laast_kontor = int(master[(master['Kartkontor'] == kontor) & (master['Er_Laast'] == True)].shape[0])
            md.append(
                f"| {kontor} | {int(row['Antall_Kommuner'])} | "
                f"{int(row['Total_Lenker']):,} | {int(row['Gjenstaaende_Lenker']):,} | "
                f"{laast_kontor} | {int(row['Kapasitet_Ukesverk'])} |".replace(',', ' ')
            )
        md.append("")
        md.append("---")
        md.append("")

    # Datakilder
    md.append("## Datakilder")
    md.append("")
    for d in plan.get('datakilder', []):
        md.append(f"- `{d['fil']}` – {d['innhold']}")
        if 'merknad' in d:
            md.append(f"  - *Merknad:* {d['merknad']}")
    md.append("")

    md.append("---")
    md.append("")

    md.append("## Endringslogg")
    md.append("")
    md.append("| Dato | Endring |")
    md.append("|------|---------|")
    md.append(f"| {i_dag.isoformat()} | STATUS.md regenerert fra prosjektplan.json |")
    md.append("")

    return '\n'.join(md)


def main():
    print("Leser prosjektplan.json...")
    plan = les_json()
    print("Leser processed data...")
    master, kap = les_master_data()
    print("Genererer STATUS.md...")
    md = generer(plan, master, kap)

    with open(STATUS_PATH, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"FERDIG! Skrev {STATUS_PATH}")


if __name__ == '__main__':
    main()
