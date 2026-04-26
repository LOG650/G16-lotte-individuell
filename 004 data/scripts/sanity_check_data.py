"""
Sanity-check av processed_data for inkonsistenser.

Sjekker:
  1. Duplikate KomNr i master
  2. Manglende verdier i kritiske kolonner
  3. Status vs Gjenstaaende_Lenker konsistens
     - Ferdig =>  Gjenstaaende = 0?
     - Ikke paabegynt => Gjenstaaende = Antall_Lenker?
  4. Fylke -> Kartkontor mapping konsistens
  5. Antall_Kommuner i kapasitet_kontorer matcher faktisk count i master
  6. Geovekst-laaste kommuner finnes i master
  7. master.Er_Laast matcher om kommunen har en geovekst-rad
  8. Antall_Lenker > 0 for alle med Status != "Ikke paabegynt"
  9. Lasperiode_Start <= Laaseperiode_Slutt
 10. Total_Lenker og Gjenstaaende_Lenker i kapasitet_kontorer matcher master-aggregat
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(BASE, 'processed_data')

FYLKE_TIL_KONTOR = {
    '03': 'Oslo', '31': 'Oslo', '32': 'Oslo', '33': 'Oslo',
    '34': 'Hamar',
    '39': 'Skien', '40': 'Skien',
    '42': 'Kristiansand',
    '11': 'Stavanger',
    '46': 'Bergen',
    '15': 'Molde',
    '50': 'Trondheim',
    '18': 'Bodø',
    '55': 'Tromsø', '56': 'Tromsø',
}


def main():
    issues = []

    master = pd.read_csv(os.path.join(DATA, 'master_kommuner.csv'),
                         dtype={'KomNr': str})
    kontorer = pd.read_csv(os.path.join(DATA, 'kapasitet_kontorer.csv'))
    geovekst = pd.read_csv(os.path.join(DATA, 'geovekst_prosjekter.csv'),
                           dtype={'KomNr': str},
                           parse_dates=['Laaseperiode_Start', 'Laaseperiode_Slutt'])

    print('=' * 60)
    print(f'master: {len(master)} rader, kontorer: {len(kontorer)}, geovekst: {len(geovekst)}')
    print('=' * 60)

    # 1. Duplikate KomNr
    dups = master[master['KomNr'].duplicated()]
    print(f'\n1. Duplikate KomNr i master: {len(dups)}')
    if len(dups) > 0:
        issues.append(f'1: {len(dups)} duplikate KomNr')
        print(dups[['KomNr','Kommune']])

    # 2. Manglende verdier i kritiske kolonner
    kritiske = ['KomNr', 'Kommune', 'Kartkontor', 'Status']
    print(f'\n2. Manglende verdier i kritiske kolonner:')
    for k in kritiske:
        n = master[k].isna().sum()
        flagg = '!! ' if n > 0 else '   '
        print(f'  {flagg}{k}: {n} NaN')
        if n > 0:
            issues.append(f'2: {k} har {n} NaN')

    # Sjekk Antall_Lenker / Gjenstaaende_Lenker / Ber_Tidbruk_Min
    for k in ['Antall_Lenker', 'Gjenstaaende_Lenker', 'Ber_Tidbruk_Min', 'Km_Kurve', 'ArealLand_Km2']:
        n = master[k].isna().sum()
        flagg = '!! ' if n > 0 else '   '
        print(f'  {flagg}{k}: {n} NaN')

    # 3. Status vs Gjenstaaende_Lenker
    print(f'\n3. Status vs Gjenstaaende_Lenker:')
    ferdig = master[master['Status'] == 'Ferdig']
    feil = ferdig[ferdig['Gjenstaaende_Lenker'] > 0]
    print(f'  Ferdig med Gjenstaaende > 0: {len(feil)} av {len(ferdig)}')
    if len(feil) > 0:
        issues.append(f'3a: {len(feil)} Ferdig-kommuner med Gjenstaaende > 0')
        print(feil[['KomNr','Kommune','Antall_Lenker','Gjenstaaende_Lenker']].head())

    ikkpb = master[master['Status'] == 'Ikke påbegynt']
    feil2 = ikkpb[ikkpb['Gjenstaaende_Lenker'] != ikkpb['Antall_Lenker']]
    feil2 = feil2[feil2['Antall_Lenker'].notna()]
    print(f'  Ikke paabegynt med Gjenstaaende != Antall: {len(feil2)} av {len(ikkpb)}')
    if len(feil2) > 0:
        issues.append(f'3b: {len(feil2)} Ikke paabegynt med mismatched lenker')
        print(feil2[['KomNr','Kommune','Antall_Lenker','Gjenstaaende_Lenker']].head())

    paab = master[master['Status'] == 'Påbegynt']
    feil3 = paab[(paab['Gjenstaaende_Lenker'] >= paab['Antall_Lenker']) | (paab['Gjenstaaende_Lenker'] <= 0)]
    feil3 = feil3[feil3['Antall_Lenker'].notna()]
    print(f'  Paabegynt med urimelige Gjenstaaende: {len(feil3)} av {len(paab)}')
    if len(feil3) > 0:
        issues.append(f'3c: {len(feil3)} Paabegynt med urimelige verdier')

    # 4. Fylke -> Kartkontor mapping konsistens
    print(f'\n4. Fylke -> Kartkontor mapping:')
    master['Fylkenr_Utledet'] = master['KomNr'].astype(str).str[:2]
    feil4 = []
    for _, r in master.iterrows():
        forventet = FYLKE_TIL_KONTOR.get(r['Fylkenr_Utledet'])
        if forventet is None:
            feil4.append((r['KomNr'], r['Kommune'], 'UKJENT FYLKE'))
        elif r['Kartkontor'] != forventet:
            feil4.append((r['KomNr'], r['Kommune'], f'{r["Kartkontor"]} != {forventet}'))
    print(f'  Avvik: {len(feil4)}')
    if len(feil4) > 0:
        issues.append(f'4: {len(feil4)} fylke-kontor avvik')
        for f in feil4[:5]:
            print(f'    {f}')

    # 5. Antall_Kommuner i kapasitet_kontorer matcher master
    print(f'\n5. kapasitet_kontorer.Antall_Kommuner vs faktisk:')
    faktisk = master.groupby('Kartkontor').size().to_dict()
    avvik5 = 0
    for _, r in kontorer.iterrows():
        n_oppgitt = r['Antall_Kommuner']
        n_faktisk = faktisk.get(r['Kartkontor'], 0)
        flagg = '!! ' if n_oppgitt != n_faktisk else '   '
        print(f'  {flagg}{r["Kartkontor"]:14s}: oppgitt {n_oppgitt}, faktisk {n_faktisk}')
        if n_oppgitt != n_faktisk:
            avvik5 += 1
    if avvik5 > 0:
        issues.append(f'5: {avvik5} kontor med mismatch i Antall_Kommuner')

    # 6. Geovekst-kommuner finnes i master
    print(f'\n6. Geovekst-kommuner i master:')
    gv_komnr = set(geovekst['KomNr'])
    master_komnr = set(master['KomNr'])
    mangler = gv_komnr - master_komnr
    print(f'  Geovekst-rader for kommuner ikke i master: {len(mangler)}')
    if len(mangler) > 0:
        issues.append(f'6: {len(mangler)} geovekst kommuner mangler i master')
        print(f'    Eks: {list(mangler)[:5]}')

    # 7. master.Er_Laast vs geovekst
    print(f'\n7. master.Er_Laast vs geovekst:')
    if 'Er_Laast' in master.columns:
        master_last = set(master[master['Er_Laast']]['KomNr'])
        gv_kommuner = gv_komnr & master_komnr
        feil7a = master_last - gv_kommuner
        feil7b = gv_kommuner - master_last
        print(f'  Er_Laast=True men ingen geovekst-rad: {len(feil7a)}')
        print(f'  Geovekst-rad men Er_Laast=False: {len(feil7b)}')
        if len(feil7a) > 0:
            issues.append(f'7a: {len(feil7a)} Er_Laast=True uten geovekst')
        if len(feil7b) > 0:
            issues.append(f'7b: {len(feil7b)} geovekst uten Er_Laast=True')

    # 8. Antall_Lenker > 0 for kommuner som ikke er Ferdig
    print(f'\n8. Antall_Lenker > 0 for ikke-Ferdig kommuner:')
    aktive = master[master['Status'] != 'Ferdig']
    null_lenker = aktive[(aktive['Antall_Lenker'] == 0) | aktive['Antall_Lenker'].isna()]
    print(f'  Aktive med Antall_Lenker = 0 eller NaN: {len(null_lenker)} av {len(aktive)}')
    if len(null_lenker) > 0:
        issues.append(f'8: {len(null_lenker)} aktive uten Antall_Lenker')
        print(null_lenker[['KomNr','Kommune','Status','Antall_Lenker']].head())

    # 9. Laaseperiode_Start <= Slutt
    print(f'\n9. Laaseperiode-validering:')
    feil9 = geovekst[geovekst['Laaseperiode_Start'] > geovekst['Laaseperiode_Slutt']]
    print(f'  Start > Slutt: {len(feil9)}')
    if len(feil9) > 0:
        issues.append(f'9: {len(feil9)} laaseperiode start > slutt')
        print(feil9[['KomNr','Kommune','Laaseperiode_Start','Laaseperiode_Slutt']].head())

    # 10. Aggregat-konsistens
    print(f'\n10. kapasitet_kontorer aggregat vs master:')
    avvik10 = 0
    for _, r in kontorer.iterrows():
        sub = master[master['Kartkontor'] == r['Kartkontor']]
        ttotal = sub['Antall_Lenker'].sum()
        tgj = sub['Gjenstaaende_Lenker'].sum()
        avvik_total = abs(ttotal - r['Total_Lenker'])
        avvik_gj = abs(tgj - r['Gjenstaaende_Lenker'])
        flagg = '!! ' if (avvik_total > 1 or avvik_gj > 1) else '   '
        if flagg == '!! ':
            avvik10 += 1
        print(f'  {flagg}{r["Kartkontor"]:14s}: Total {r["Total_Lenker"]:.0f} vs {ttotal:.0f}, '
              f'Gj {r["Gjenstaaende_Lenker"]:.0f} vs {tgj:.0f}')
    if avvik10 > 0:
        issues.append(f'10: {avvik10} kontor med aggregat-mismatch')

    print('\n' + '=' * 60)
    print('SAMMENDRAG')
    print('=' * 60)
    print(f'Totalt {len(issues)} issues:')
    for i in issues:
        print(f'  - {i}')


if __name__ == '__main__':
    main()
