"""
Tidbruk-sensitivitetsanalyse, Monte Carlo-versjon (modell-evalueringsjobb #1).

Kjoerer monte_carlo.py med skaleringsfaktor paa beregnet tidbruk per kommune,
for samme skalaer (1,5 og 2,0) og NVDB-scenarioer som
heuristikk_tidbruk_sensitivitet.py. 500 iterasjoner per (skala, scenario).

Skaleringen anvendes paa det stokastiske MIN/KM-leddet OG det deterministiske
areal-leddet — matematisk ekvivalent med aa gange `Ber_Tidbruk_Min` med skala
i heuristikkens kommune-df. Dette holder skaleringen konsistent paa tvers av
heuristikk- og MC-sensitiviteten.

Output i processed_data/:
  monte_carlo_tidbruk_summary.csv
  monte_carlo_tidbruk_varigheter.csv
"""

import os
import argparse
import numpy as np
import pandas as pd

# heuristikk.py wrapper sys.stdout selv ved import (transitiv via monte_carlo)
import monte_carlo
from monte_carlo import (
    last_empirisk_min_per_km,
    sample_nvdb_params,
    aggreger_uke_percentiler,
    N_ITERATIONS,
    SEED,
    GRUNNPAKKE_MIN_PER_KM2,
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

SKALAER_DEFAULT = [1.5, 2.0]


def beregn_timer_skalert(kommuner, sampled_mpk, skala):
    """Som monte_carlo.beregn_timer_med_sampled_mpk, men ganger resultatet med skala.

    ber_min = (Km_Kurve * sampled_mpk + ArealLand_Km2 * 0,6510) * skala
    timer   = (ber_min / 60) * (Gjenstaaende_Lenker / Antall_Lenker)
    """
    timer_liste = []
    for i, (_, r) in enumerate(kommuner.iterrows()):
        antall = float(r['Antall_Lenker']) if pd.notna(r['Antall_Lenker']) else 0.0
        gjenstaar = float(r['Gjenstaaende_Lenker']) if pd.notna(r['Gjenstaaende_Lenker']) else 0.0
        km = float(r['Km_Kurve']) if pd.notna(r['Km_Kurve']) else 0.0
        areal = float(r['ArealLand_Km2']) if pd.notna(r['ArealLand_Km2']) else 0.0
        ber_min = (km * sampled_mpk[i] + areal * GRUNNPAKKE_MIN_PER_KM2) * skala
        if antall > 0:
            timer_liste.append((ber_min / 60.0) * (gjenstaar / antall))
        else:
            timer_liste.append(0.0)
    return timer_liste


def kjor_iterasjon_skalert(rng, kommuner, kontorer, lock_intervals, scenario,
                           empirisk_mpk, skala):
    """En MC-iterasjon med tidbruk-skala. Speiler monte_carlo.kjor_iterasjon
    bortsett fra at timer-beregningen ganges med skala."""
    n = len(kommuner)
    sampled = rng.choice(empirisk_mpk, size=n, replace=True)

    kommunestate = bygg_kommunestate(kommuner, lock_intervals)
    timer = beregn_timer_skalert(kommuner, sampled, skala)
    for k, t in zip(kommunestate, timer):
        if not k['ferdig_kartkontor']:
            k['gjenvaerende_timer'] = t
            k['Timer_Start'] = t

    manuell_takt, automasjon, total_throughput = sample_nvdb_params(
        rng, scenario['Automasjonsgrad_FME']
    )
    modifisert_scenario = scenario.copy()
    modifisert_scenario['Total_Throughput_Per_Dag'] = total_throughput

    _, ukentlig_nvdb = simuler(
        kommunestate, kontorer, lock_intervals, modifisert_scenario
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
        'ukentlig_nvdb': ukentlig_nvdb,
        'sampled_manuell_takt': manuell_takt,
        'sampled_automasjon': automasjon,
        'sampled_throughput': total_throughput,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skalaer', nargs='+', type=float, default=SKALAER_DEFAULT,
                        help='Skaleringsfaktorer paa Ber_Tidbruk_Min (default 1.5 2.0)')
    parser.add_argument('--scenarioer', nargs='+', default=None,
                        help='NVDB-scenarioer (default alle 3)')
    parser.add_argument('--n', type=int, default=N_ITERATIONS,
                        help=f'Iterasjoner per (skala, scenario) (default {N_ITERATIONS})')
    args = parser.parse_args()

    print('=' * 60)
    print('TIDBRUK-SENSITIVITET - MONTE CARLO')
    print('=' * 60)

    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)
    empirisk_mpk = last_empirisk_min_per_km()

    if args.scenarioer:
        nvdb = nvdb[nvdb['Scenario'].isin(args.scenarioer)].reset_index(drop=True)

    print(f'Kommuner: {len(kommuner)}')
    print(f'Empirisk MIN/KM: N={len(empirisk_mpk)}, mean={empirisk_mpk.mean():.3f}')
    print(f'Skalaer: {args.skalaer}')
    print(f'NVDB-scenarioer: {list(nvdb["Scenario"])}')
    print(f'Iterasjoner: {args.n} per (skala, scenario) = '
          f'{len(args.skalaer) * len(nvdb) * args.n} totalt')

    summary_rader = []
    varighet_rader = []

    for skala in args.skalaer:
        print(f'\n{"=" * 60}')
        print(f'Skala: {skala:.2f}x')
        print('=' * 60)

        for _, scenario in nvdb.iterrows():
            navn = scenario['Scenario']
            print(f'\n=== {navn} (skala {skala:.2f}x, {args.n} iterasjoner) ===')

            # Reset RNG per (skala, scenario) for replikasjon
            rng = np.random.default_rng(SEED)

            varigheter_dager = []
            kk_varigheter = []
            alle_ukentlige = []

            for it in range(args.n):
                if it % 100 == 0 and it > 0:
                    print(f'  Iterasjon {it}/{args.n}...')
                res = kjor_iterasjon_skalert(
                    rng, kommuner, kontorer, lock_intervals, scenario,
                    empirisk_mpk, skala,
                )
                if res['max_nvdb']:
                    varigheter_dager.append((res['max_nvdb'] - STARTDATO).days)
                if res['max_kartkontor']:
                    kk_varigheter.append((res['max_kartkontor'] - STARTDATO).days)
                alle_ukentlige.append(res['ukentlig_nvdb'])
                varighet_rader.append({
                    'Skala': skala,
                    'Scenario': navn,
                    'iter': it,
                    'Varighet_Dager': (res['max_nvdb'] - STARTDATO).days if res['max_nvdb'] else None,
                    'Kartkontor_Dager': (res['max_kartkontor'] - STARTDATO).days if res['max_kartkontor'] else None,
                    'Sampled_Manuell_Takt': round(res['sampled_manuell_takt'], 1),
                    'Sampled_Automasjon': round(res['sampled_automasjon'], 4),
                    'Sampled_Throughput': round(res['sampled_throughput'], 1),
                })

            v_arr = np.array(varigheter_dager)
            kk_arr = np.array(kk_varigheter)
            summary_rader.append({
                'Skala': skala,
                'Scenario': navn,
                'N_Iterasjoner': len(varigheter_dager),
                'Kartkontor_Dager_P5': int(np.percentile(kk_arr, 5)),
                'Kartkontor_Dager_P50': int(np.percentile(kk_arr, 50)),
                'Kartkontor_Dager_P95': int(np.percentile(kk_arr, 95)),
                'Kartkontor_Mnd_P5': round(np.percentile(kk_arr, 5) / 30.44, 1),
                'Kartkontor_Mnd_P50': round(np.percentile(kk_arr, 50) / 30.44, 1),
                'Kartkontor_Mnd_P95': round(np.percentile(kk_arr, 95) / 30.44, 1),
                'Varighet_Dager_P5': int(np.percentile(v_arr, 5)),
                'Varighet_Dager_P50': int(np.percentile(v_arr, 50)),
                'Varighet_Dager_P95': int(np.percentile(v_arr, 95)),
                'Varighet_Aar_P5': round(np.percentile(v_arr, 5) / 365.25, 2),
                'Varighet_Aar_P50': round(np.percentile(v_arr, 50) / 365.25, 2),
                'Varighet_Aar_P95': round(np.percentile(v_arr, 95) / 365.25, 2),
            })
            print(f'  Kartkontor (mnd) P5/P50/P95: '
                  f'{summary_rader[-1]["Kartkontor_Mnd_P5"]} / '
                  f'{summary_rader[-1]["Kartkontor_Mnd_P50"]} / '
                  f'{summary_rader[-1]["Kartkontor_Mnd_P95"]}')
            print(f'  Varighet (aar) P5/P50/P95: '
                  f'{summary_rader[-1]["Varighet_Aar_P5"]} / '
                  f'{summary_rader[-1]["Varighet_Aar_P50"]} / '
                  f'{summary_rader[-1]["Varighet_Aar_P95"]}')

    pd.DataFrame(summary_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_tidbruk_summary.csv'), index=False
    )
    pd.DataFrame(varighet_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_tidbruk_varigheter.csv'), index=False
    )

    print(f'\n{"=" * 60}')
    print('Sammendrag')
    print('=' * 60)
    print(pd.DataFrame(summary_rader).to_string(index=False))
    print(f'\nLagret: monte_carlo_tidbruk_summary.csv + monte_carlo_tidbruk_varigheter.csv')


if __name__ == '__main__':
    main()
