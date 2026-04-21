"""
Monte Carlo usikkerhetsanalyse med MIP-assignment som fast tildeling.

Leser tidsplan_mip_vektet_<scenario>.csv (MIP's optimale tildeling per kommune),
overstyrer hjemmekontor-tildelingen i master_kommuner slik at heuristikkens
simulator bruker MIP-tildelingen, og kjorer deretter eksisterende Monte Carlo-
motor med samme 500 iterasjoner og 3 stokastiske kilder.

Resultatene kan sammenlignes direkte med monte_carlo_*.csv (heuristikk-basert).

Output i processed_data/:
  monte_carlo_mip_summary.csv
  monte_carlo_mip_varigheter.csv
  monte_carlo_mip_per_kommune.csv
  monte_carlo_mip_ko_percentiles.csv
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd

# heuristikk.py wrapper sys.stdout paa Windows; monte_carlo.py arver det via import.
# Vi trenger derfor ikke wrappe her saa lenge heuristikk importeres foerst.
from heuristikk import (
    last_data, bygg_laseintervaller, bygg_kommunestate, simuler, STARTDATO,
)
from monte_carlo import (
    last_empirisk_min_per_km, kjor_iterasjon, aggreger_uke_percentiler,
    N_ITERATIONS, SEED,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

DEFAULT_MIP_MODE = 'vektet'  # default, overstyres av --mode


def overstyr_tildeling(kommuner, mip_df):
    """Erstatt Kartkontor-kolonnen i kommuner med MIP-tildelingen."""
    mip_map = dict(zip(mip_df['KomNr'], mip_df['Kartkontor_MIP']))
    k = kommuner.copy()
    k['Kartkontor'] = k['KomNr'].map(mip_map).fillna(k['Kartkontor'])
    return k


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['makespan', 'lex', 'vektet'],
                        default=DEFAULT_MIP_MODE,
                        help=f'Hvilken MIP-loesning MC skal bruke som assignment '
                             f'(default {DEFAULT_MIP_MODE}). Leser '
                             f'tidsplan_mip_<mode>_<scenario>.csv.')
    args = parser.parse_args()
    mip_mode = args.mode

    print('=' * 60)
    print(f'MONTE CARLO PAA MIP-PLAN (mode={mip_mode})')
    print('=' * 60)

    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)
    empirisk_mpk = last_empirisk_min_per_km()

    print(f'Kommuner: {len(kommuner)}')
    print(f'N iterasjoner: {N_ITERATIONS}')

    rng = np.random.default_rng(SEED)

    summary_rader = []
    varighet_rader = []
    per_kommune_rader = []
    uke_rader = []

    for _, scenario in nvdb.iterrows():
        navn = scenario['Scenario']
        mip_fil = os.path.join(DATA_DIR, f'tidsplan_mip_{mip_mode}_{navn}.csv')
        if not os.path.exists(mip_fil):
            print(f'\n!! Mangler {mip_fil}, hopper over scenario')
            continue
        mip_df = pd.read_csv(mip_fil, dtype={'KomNr': str})
        kommuner_mip = overstyr_tildeling(kommuner, mip_df)

        # Valider at tildelingen er konsistent
        n_omfordelt = (kommuner['Kartkontor'] != kommuner_mip['Kartkontor']).sum()
        print(f'\n=== {navn} ({N_ITERATIONS} iter, {n_omfordelt} omfordelte kommuner) ===')

        varigheter_dager = []
        kk_varigheter = []
        per_komm_dict = {}
        alle_ukentlige = []

        for it in range(N_ITERATIONS):
            if it % 50 == 0 and it > 0:
                print(f'  iterasjon {it}/{N_ITERATIONS}...')
            res = kjor_iterasjon(
                rng, kommuner_mip, kontorer, lock_intervals, scenario, empirisk_mpk
            )
            if res['max_nvdb']:
                varigheter_dager.append((res['max_nvdb'] - STARTDATO).days)
            if res['max_kartkontor']:
                kk_varigheter.append((res['max_kartkontor'] - STARTDATO).days)
            for komnr, dato in res['per_kommune']:
                per_komm_dict.setdefault(komnr, []).append(dato)
            alle_ukentlige.append(res['ukentlig_nvdb'])
            varighet_rader.append({
                'Scenario': navn, 'iter': it,
                'Varighet_Dager': (res['max_nvdb'] - STARTDATO).days if res['max_nvdb'] else None,
                'Kartkontor_Dager': (res['max_kartkontor'] - STARTDATO).days if res['max_kartkontor'] else None,
                'Sampled_Manuell_Takt': round(res['sampled_manuell_takt'], 1),
                'Sampled_Automasjon': round(res['sampled_automasjon'], 4),
                'Sampled_Throughput': round(res['sampled_throughput'], 1),
            })

        v_arr = np.array(varigheter_dager)
        kk_arr = np.array(kk_varigheter)
        tp_arr = np.array([
            r['Sampled_Throughput'] for r in varighet_rader if r['Scenario'] == navn
        ])
        summary_rader.append({
            'Scenario': navn,
            'Plan_Type': 'MIP_' + mip_mode,
            'N_Iterasjoner': len(varigheter_dager),
            'N_Omfordelte': int(n_omfordelt),
            'Kartkontor_Dager_P5': int(np.percentile(kk_arr, 5)),
            'Kartkontor_Dager_P50': int(np.percentile(kk_arr, 50)),
            'Kartkontor_Dager_P95': int(np.percentile(kk_arr, 95)),
            'Varighet_Dager_P5': int(np.percentile(v_arr, 5)),
            'Varighet_Dager_P50': int(np.percentile(v_arr, 50)),
            'Varighet_Dager_P95': int(np.percentile(v_arr, 95)),
            'Varighet_Aar_P5': round(np.percentile(v_arr, 5) / 365.25, 2),
            'Varighet_Aar_P50': round(np.percentile(v_arr, 50) / 365.25, 2),
            'Varighet_Aar_P95': round(np.percentile(v_arr, 95) / 365.25, 2),
            'Throughput_P5': int(np.percentile(tp_arr, 5)),
            'Throughput_P50': int(np.percentile(tp_arr, 50)),
            'Throughput_P95': int(np.percentile(tp_arr, 95)),
        })
        print(f'  Varighet (aar) P5/P50/P95: '
              f'{summary_rader[-1]["Varighet_Aar_P5"]} / '
              f'{summary_rader[-1]["Varighet_Aar_P50"]} / '
              f'{summary_rader[-1]["Varighet_Aar_P95"]}')

        for komnr, datoer in per_komm_dict.items():
            gyldige = [d for d in datoer if d is not None]
            if not gyldige:
                continue
            dager = [(d - STARTDATO).days for d in gyldige]
            per_kommune_rader.append({
                'Scenario': navn,
                'Plan_Type': 'MIP_' + mip_mode,
                'KomNr': komnr,
                'N_Iterasjoner': len(gyldige),
                'Dager_P5': int(np.percentile(dager, 5)),
                'Dager_P50': int(np.percentile(dager, 50)),
                'Dager_P95': int(np.percentile(dager, 95)),
            })

        uke_agg = aggreger_uke_percentiler(alle_ukentlige)
        uke_agg.insert(0, 'Scenario', navn)
        uke_agg.insert(1, 'Plan_Type', 'MIP_' + mip_mode)
        uke_rader.append(uke_agg)

    pd.DataFrame(summary_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_mip_summary.csv'), index=False
    )
    pd.DataFrame(varighet_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_mip_varigheter.csv'), index=False
    )
    pd.DataFrame(per_kommune_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_mip_per_kommune.csv'), index=False
    )
    if uke_rader:
        pd.concat(uke_rader, ignore_index=True).to_csv(
            os.path.join(DATA_DIR, 'monte_carlo_mip_ko_percentiles.csv'), index=False
        )

    print('\n=== Sammendrag ===')
    print(pd.DataFrame(summary_rader).to_string(index=False))
    print(f'\nOutput lagret i {DATA_DIR}')


if __name__ == '__main__':
    main()
