"""
AUTOMASJON_STD-sensitivitetsanalyse, Monte Carlo (modell-evalueringsjobb #2).

Kjoerer monte_carlo.py med varierende standardavvik paa Automasjonsgrad_FME-
sampling, for aa kvantifisere hvor foelsomt scenario-overlappet er for
designvalget std=0,03 (jf. review-funn 3.1 i `013 fase 3 - review/
review_modellering.md`).

Standardavviket er ikke en empirisk fordeling — det er et designvalg som
bestemmer om scenariofordelingene overlapper hverandre. Ved std=0,01 vil
scenarioene ligge tilnaermet adskilt; ved std=0,05 vil de overlappe mye.
0,03 er valgt som rimelig kompromiss; denne analysen verifiserer den
vurderingen.

Output i processed_data/:
  monte_carlo_automasjon_summary.csv
  monte_carlo_automasjon_varigheter.csv
"""

import os
import argparse
import numpy as np
import pandas as pd

# heuristikk.py wrapper sys.stdout selv ved import (transitiv via monte_carlo)
from monte_carlo import (
    last_empirisk_min_per_km,
    beregn_timer_med_sampled_mpk,
    N_ITERATIONS,
    SEED,
    MANUELL_TAKT_LOW,
    MANUELL_TAKT_HIGH,
    AUTOMASJON_CLIP_LOW,
    AUTOMASJON_CLIP_HIGH,
    ANTALL_STILLINGER,
    STILLINGSPROSENT,
)
from heuristikk import (
    last_data,
    bygg_laseintervaller,
    bygg_kommunestate,
    simuler,
    STARTDATO,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

STD_DEFAULT = [0.01, 0.02, 0.03, 0.05]


def sample_nvdb_med_std(rng, scenario_automasjon, std):
    """Som monte_carlo.sample_nvdb_params, men std er parameter."""
    manuell_takt = rng.uniform(MANUELL_TAKT_LOW, MANUELL_TAKT_HIGH)
    automasjon = rng.normal(scenario_automasjon, std)
    automasjon = float(np.clip(automasjon, AUTOMASJON_CLIP_LOW, AUTOMASJON_CLIP_HIGH))
    manuell_kap = ANTALL_STILLINGER * STILLINGSPROSENT * manuell_takt
    total_throughput = manuell_kap / (1 - automasjon)
    return manuell_takt, automasjon, total_throughput


def kjor_iterasjon_med_std(rng, kommuner, kontorer, lock_intervals, scenario,
                            empirisk_mpk, std):
    """En MC-iterasjon der AUTOMASJON_STD er parameter. Speiler
    monte_carlo.kjor_iterasjon ellers."""
    n = len(kommuner)
    sampled = rng.choice(empirisk_mpk, size=n, replace=True)

    kommunestate = bygg_kommunestate(kommuner, lock_intervals)
    timer = beregn_timer_med_sampled_mpk(kommuner, sampled)
    for k, t in zip(kommunestate, timer):
        if not k['ferdig_kartkontor']:
            k['gjenvaerende_timer'] = t
            k['Timer_Start'] = t

    manuell_takt, automasjon, total_throughput = sample_nvdb_med_std(
        rng, scenario['Automasjonsgrad_FME'], std,
    )
    modifisert_scenario = scenario.copy()
    modifisert_scenario['Total_Throughput_Per_Dag'] = total_throughput

    _, ukentlig_nvdb = simuler(
        kommunestate, kontorer, lock_intervals, modifisert_scenario,
    )

    max_kk = max(
        (k['ferdigdato_kartkontor'] for k in kommunestate if k['ferdigdato_kartkontor']),
        default=None,
    )
    max_nvdb = max(
        (k['ferdigdato_nvdb'] for k in kommunestate if k['ferdigdato_nvdb']),
        default=None,
    )
    return {
        'max_kartkontor': max_kk,
        'max_nvdb': max_nvdb,
        'sampled_manuell_takt': manuell_takt,
        'sampled_automasjon': automasjon,
        'sampled_throughput': total_throughput,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--std', nargs='+', type=float, default=STD_DEFAULT,
                        help='AUTOMASJON_STD-verdier (default 0.01 0.02 0.03 0.05)')
    parser.add_argument('--scenarioer', nargs='+', default=None,
                        help='NVDB-scenarioer (default alle 3)')
    parser.add_argument('--n', type=int, default=N_ITERATIONS,
                        help=f'Iterasjoner per (std, scenario) (default {N_ITERATIONS})')
    args = parser.parse_args()

    print('=' * 60)
    print('AUTOMASJON_STD-SENSITIVITET - MONTE CARLO')
    print('=' * 60)

    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)
    empirisk_mpk = last_empirisk_min_per_km()

    if args.scenarioer:
        nvdb = nvdb[nvdb['Scenario'].isin(args.scenarioer)].reset_index(drop=True)

    print(f'Kommuner: {len(kommuner)}')
    print(f'AUTOMASJON_STD-verdier: {args.std}')
    print(f'NVDB-scenarioer: {list(nvdb["Scenario"])}')
    print(f'Iterasjoner: {args.n} per (std, scenario) = '
          f'{len(args.std) * len(nvdb) * args.n} totalt')

    summary_rader = []
    varighet_rader = []

    for std in args.std:
        print(f'\n{"=" * 60}')
        print(f'AUTOMASJON_STD: {std}')
        print('=' * 60)

        for _, scenario in nvdb.iterrows():
            navn = scenario['Scenario']
            print(f'\n=== {navn} (std={std}, {args.n} iterasjoner) ===')

            # Reset RNG per (std, scenario) for replikasjon
            rng = np.random.default_rng(SEED)

            varigheter_dager = []
            automasjoner = []

            for it in range(args.n):
                if it % 100 == 0 and it > 0:
                    print(f'  Iterasjon {it}/{args.n}...')
                res = kjor_iterasjon_med_std(
                    rng, kommuner, kontorer, lock_intervals, scenario,
                    empirisk_mpk, std,
                )
                if res['max_nvdb']:
                    varigheter_dager.append((res['max_nvdb'] - STARTDATO).days)
                automasjoner.append(res['sampled_automasjon'])
                varighet_rader.append({
                    'Std': std,
                    'Scenario': navn,
                    'iter': it,
                    'Varighet_Dager': (res['max_nvdb'] - STARTDATO).days if res['max_nvdb'] else None,
                    'Sampled_Automasjon': round(res['sampled_automasjon'], 4),
                    'Sampled_Throughput': round(res['sampled_throughput'], 1),
                })

            v_arr = np.array(varigheter_dager)
            a_arr = np.array(automasjoner)
            summary_rader.append({
                'Std': std,
                'Scenario': navn,
                'N_Iterasjoner': len(varigheter_dager),
                'Varighet_Aar_P5': round(np.percentile(v_arr, 5) / 365.25, 2),
                'Varighet_Aar_P50': round(np.percentile(v_arr, 50) / 365.25, 2),
                'Varighet_Aar_P95': round(np.percentile(v_arr, 95) / 365.25, 2),
                'Automasjon_P5': round(np.percentile(a_arr, 5), 4),
                'Automasjon_P50': round(np.percentile(a_arr, 50), 4),
                'Automasjon_P95': round(np.percentile(a_arr, 95), 4),
            })
            print(f'  Automasjon P5/P50/P95: '
                  f'{summary_rader[-1]["Automasjon_P5"]} / '
                  f'{summary_rader[-1]["Automasjon_P50"]} / '
                  f'{summary_rader[-1]["Automasjon_P95"]}')
            print(f'  Varighet (aar) P5/P50/P95: '
                  f'{summary_rader[-1]["Varighet_Aar_P5"]} / '
                  f'{summary_rader[-1]["Varighet_Aar_P50"]} / '
                  f'{summary_rader[-1]["Varighet_Aar_P95"]}')

    pd.DataFrame(summary_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_automasjon_summary.csv'), index=False,
    )
    pd.DataFrame(varighet_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_automasjon_varigheter.csv'), index=False,
    )

    print(f'\n{"=" * 60}')
    print('Sammendrag')
    print('=' * 60)
    df = pd.DataFrame(summary_rader)
    print(df.to_string(index=False))

    # Overlapp-sjekk: P95 av lavere-automasjon scenario vs P5 av hoeyere
    print(f'\n{"=" * 60}')
    print('Scenario-overlapp per std-verdi')
    print('=' * 60)
    print('Overlapp = P5 av raskere scenario er mindre enn P95 av tregere scenario')
    for std in args.std:
        sub = df[df['Std'] == std].set_index('Scenario')
        if not all(s in sub.index for s in ['Basis_85', 'Middels_90', 'Samferdsel_96']):
            continue
        b_p95 = sub.loc['Basis_85', 'Varighet_Aar_P95']
        m_p5 = sub.loc['Middels_90', 'Varighet_Aar_P5']
        m_p95 = sub.loc['Middels_90', 'Varighet_Aar_P95']
        s_p5 = sub.loc['Samferdsel_96', 'Varighet_Aar_P5']
        bm = 'JA' if m_p5 < b_p95 else 'NEI'
        ms = 'JA' if s_p5 < m_p95 else 'NEI'
        print(f'  std={std}: Basis_85 vs Middels_90 = {bm} '
              f'(M_P5={m_p5:.2f} vs B_P95={b_p95:.2f}); '
              f'Middels_90 vs Samferdsel_96 = {ms} '
              f'(S_P5={s_p5:.2f} vs M_P95={m_p95:.2f})')

    print(f'\nLagret: monte_carlo_automasjon_summary.csv + monte_carlo_automasjon_varigheter.csv')


if __name__ == '__main__':
    main()
