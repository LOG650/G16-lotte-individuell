"""
Tidbruk-sensitivitetsanalyse, heuristikk-versjon (modell-evalueringsjobb #1).

Kjoerer heuristikken for et sett med skaleringsfaktorer paa Ber_Tidbruk_Min
per NVDB-scenario, for aa teste om hovedbudskapet "NVDB er flaskehalsen"
overlever at tidbruk-formelen underestimerer (jf. validering_tidbruk_formel.md).

Skaleringsfaktorene 1,5 og 2,0 dekker det "doblede" tallet anslaatt i
review-anbefalingen (8/10 kontor har median formel-estimat under sitt eget
oppgitte baand; ferdige kommuner er ~halvparten saa tunge per stykk som de
gjenstaaende).

Output i processed_data/:
  tidsplan_<nvdb_scenario>_skala<X>.csv
  oppsummering_tidbruk_sensitivitet_heur.csv
"""

import os
import argparse
import pandas as pd

# heuristikk.py wrapper sys.stdout selv ved import
from heuristikk import (
    last_data,
    bygg_laseintervaller,
    bygg_kommunestate,
    simuler,
    STARTDATO,
    MAX_AAR,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

SKALAER_DEFAULT = [1.5, 2.0]


def skaler_kommuner(kommuner_df, skala):
    """Returner ny df med Ber_Tidbruk_Min skalert. Endrer ikke originalen."""
    df = kommuner_df.copy()
    df['Ber_Tidbruk_Min'] = df['Ber_Tidbruk_Min'].astype(float) * skala
    df['Ber_Dagsverk'] = df['Ber_Dagsverk'].astype(float) * skala
    return df


def lagre_tidsplan(kommunestate, scenario_navn, skala):
    rader = []
    for k in kommunestate:
        rader.append({
            'KomNr': k['KomNr'],
            'Kommune': k['Kommune'],
            'Kartkontor': k['Kartkontor'],
            'Antall_Lenker': k['Antall_Lenker'],
            'Gjenstaaende_Lenker_Start': k['Gjenstaaende_Lenker_Start'],
            'Timer_Start': round(k['Timer_Start'], 2),
            'Ferdigdato_Kartkontor': k['ferdigdato_kartkontor'],
            'Ferdigdato_NVDB': k['ferdigdato_nvdb'],
        })
    skala_str = f'{skala:.1f}'.replace('.', '_')
    filnavn = f'tidsplan_{scenario_navn}_skala{skala_str}.csv'
    pd.DataFrame(rader).to_csv(os.path.join(DATA_DIR, filnavn), index=False)
    return filnavn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skalaer', nargs='+', type=float, default=SKALAER_DEFAULT,
                        help='Skaleringsfaktorer paa Ber_Tidbruk_Min (default 1.5 2.0)')
    parser.add_argument('--scenarioer', nargs='+', default=None,
                        help='NVDB-scenarioer (default alle 3)')
    args = parser.parse_args()

    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)

    if args.scenarioer:
        nvdb = nvdb[nvdb['Scenario'].isin(args.scenarioer)].reset_index(drop=True)

    print(f'Tidbruk-sensitivitet (heuristikk): '
          f'{len(args.skalaer)} skalaer x {len(nvdb)} scenarioer = '
          f'{len(args.skalaer) * len(nvdb)} kjoeringer')

    oppsummering = []

    for skala in args.skalaer:
        kommuner_skalert = skaler_kommuner(kommuner, skala)
        total_timer_start = (
            kommuner_skalert['Ber_Tidbruk_Min'].astype(float).sum() / 60.0
        )
        print(f'\n{"=" * 60}')
        print(f'Skala: {skala:.2f}x  (sum Ber_Tidbruk = {total_timer_start:.0f} timer)')
        print('=' * 60)

        for _, scenario in nvdb.iterrows():
            navn = scenario['Scenario']
            print(f'\n  --- {navn} ---')

            kommunestate = bygg_kommunestate(kommuner_skalert, lock_intervals)
            simuler(kommunestate, kontorer, lock_intervals, scenario)

            filnavn = lagre_tidsplan(kommunestate, navn, skala)

            ferdig_kk = [k['ferdigdato_kartkontor'] for k in kommunestate
                         if k['ferdigdato_kartkontor']]
            ferdig_nvdb = [k['ferdigdato_nvdb'] for k in kommunestate
                           if k['ferdigdato_nvdb']]
            uferdig = sum(1 for k in kommunestate if k['ferdigdato_nvdb'] is None)

            slutt_kk = max(ferdig_kk) if ferdig_kk else None
            slutt_nvdb = max(ferdig_nvdb) if ferdig_nvdb else None

            if slutt_nvdb:
                dager_nvdb = (slutt_nvdb - STARTDATO).days
                aar_nvdb = round(dager_nvdb / 365.25, 2)
            else:
                dager_nvdb = None
                aar_nvdb = None

            if slutt_kk:
                dager_kk = (slutt_kk - STARTDATO).days
                mnd_kk = round(dager_kk / 30.44, 1)
            else:
                dager_kk = None
                mnd_kk = None

            print(f'    Siste kartkontor ferdig: {slutt_kk} ({mnd_kk} mnd)')
            print(f'    Siste NVDB ferdig:       {slutt_nvdb} ({aar_nvdb} aar)')
            if uferdig:
                print(f'    ADVARSEL: {uferdig} kommuner ikke fullfoert innen cutoff ({MAX_AAR} aar)')

            oppsummering.append({
                'Skala': skala,
                'NVDB_Scenario': navn,
                'Ferdig_Kartkontor_Sist': slutt_kk,
                'Kartkontor_Dager': dager_kk,
                'Kartkontor_Mnd': mnd_kk,
                'Ferdig_NVDB_Sist': slutt_nvdb,
                'Varighet_Dager': dager_nvdb,
                'Varighet_Aar': aar_nvdb,
                'Uferdig_NVDB_Kommuner': uferdig,
                'Tidsplan_Fil': filnavn,
            })

    df_opp = pd.DataFrame(oppsummering)
    out_path = os.path.join(DATA_DIR, 'oppsummering_tidbruk_sensitivitet_heur.csv')
    df_opp.to_csv(out_path, index=False)

    print(f'\n{"=" * 60}')
    print('Oppsummering')
    print('=' * 60)
    print(df_opp.to_string(index=False))
    print(f'\nLagret: {out_path}')


if __name__ == '__main__':
    main()
