"""
Monte Carlo usikkerhetsanalyse for tidsbruk per kommune OG NVDB-takt.

Tre stokastiske kilder per iterasjon:
  1. MIN/KM per kommune - bootstraper fra empirisk fordeling (58 kartblader
     i tidbruk_kalibrering.csv). Påvirker kartkontor-varighet og kø-rekkefølge.
  2. Produksjonstakt_Manuell - Uniform(300, 400) lenker/person/dag. Påvirker
     total NVDB-throughput.
  3. Automasjonsgrad_FME - Normal(scenariopunkt, 0,01), klippet til [0,5; 0,99].
     Påvirker total NVDB-throughput via formelen
     Total_Throughput = 0,5 × Manuell_Takt / (1 - Automasjonsgrad).

Sampling-strategi: per-kommune, globalt, med tilbakelegging for MIN/KM.
Grunnpakke-tillegget (0,6510 min/km²) holdes konstant siden det ikke har
tilsvarende empirisk fordeling.

Output i processed_data/:
  monte_carlo_summary.csv        - Varighetspercentiler per scenario
  monte_carlo_varigheter.csv     - Varighet + sampled NVDB-params per iterasjon
  monte_carlo_per_kommune.csv    - Percentiler for NVDB-ferdigdato per kommune
  monte_carlo_ko_percentiles.csv - Ukentlige percentiler for kølengde/overført
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import timedelta

# Importer byggeklossene fra heuristikk.py (setter selv opp stdout-wrapping på Windows)
from heuristikk import (
    last_data,
    bygg_laseintervaller,
    bygg_kommunestate,
    simuler,
    STARTDATO,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

N_ITERATIONS = 500
SEED = 42
# Grunnpakke-tillegg holdes konstant (ingen empirisk fordeling for km²-leddet)
GRUNNPAKKE_MIN_PER_KM2 = 0.651042

# NVDB-takt usikkerhet
MANUELL_TAKT_LOW = 300   # lenker/person/dag (nedre grense iht. kilde 300-400)
MANUELL_TAKT_HIGH = 400
AUTOMASJON_STD = 0.01    # standardavvik rundt scenariopunktet
AUTOMASJON_CLIP_LOW = 0.5
AUTOMASJON_CLIP_HIGH = 0.99
ANTALL_STILLINGER = 2
STILLINGSPROSENT = 0.25  # gir 0.5 samlet årsverk


def last_empirisk_min_per_km():
    df = pd.read_csv(os.path.join(DATA_DIR, 'tidbruk_kalibrering.csv'))
    return df['Min_Per_Km'].values


def beregn_timer_med_sampled_mpk(kommuner, sampled_mpk):
    """Returner liste med gjenvaerende_timer per kommune, basert på sampled MIN/KM.

    gjenvaerende_timer = (Km_Kurve * sampled_mpk + ArealLand_Km2 * 0,6510) / 60
                         * (Gjenstaaende_Lenker / Antall_Lenker)
    """
    timer_liste = []
    for i, (_, r) in enumerate(kommuner.iterrows()):
        antall = float(r['Antall_Lenker']) if pd.notna(r['Antall_Lenker']) else 0.0
        gjenstaar = float(r['Gjenstaaende_Lenker']) if pd.notna(r['Gjenstaaende_Lenker']) else 0.0
        km = float(r['Km_Kurve']) if pd.notna(r['Km_Kurve']) else 0.0
        areal = float(r['ArealLand_Km2']) if pd.notna(r['ArealLand_Km2']) else 0.0
        ber_min = km * sampled_mpk[i] + areal * GRUNNPAKKE_MIN_PER_KM2
        if antall > 0:
            timer_liste.append((ber_min / 60.0) * (gjenstaar / antall))
        else:
            timer_liste.append(0.0)
    return timer_liste


def sample_nvdb_params(rng, scenario_automasjon):
    """Sample Manuell_Takt (Uniform[300, 400]) og Automasjonsgrad (Normal rundt
    scenariopunkt). Returnerer (manuell_takt, automasjon, total_throughput)."""
    manuell_takt = rng.uniform(MANUELL_TAKT_LOW, MANUELL_TAKT_HIGH)
    automasjon = rng.normal(scenario_automasjon, AUTOMASJON_STD)
    automasjon = float(np.clip(automasjon, AUTOMASJON_CLIP_LOW, AUTOMASJON_CLIP_HIGH))
    manuell_kap = ANTALL_STILLINGER * STILLINGSPROSENT * manuell_takt
    total_throughput = manuell_kap / (1 - automasjon)
    return manuell_takt, automasjon, total_throughput


def kjor_iterasjon(rng, kommuner, kontorer, lock_intervals, scenario, empirisk_mpk):
    """Én Monte Carlo-iterasjon. Returnerer resultat-dict."""
    # 1. MIN/KM per kommune
    n = len(kommuner)
    sampled = rng.choice(empirisk_mpk, size=n, replace=True)

    kommunestate = bygg_kommunestate(kommuner, lock_intervals)
    timer = beregn_timer_med_sampled_mpk(kommuner, sampled)
    for k, t in zip(kommunestate, timer):
        if not k['ferdig_kartkontor']:
            k['gjenvaerende_timer'] = t
            k['Timer_Start'] = t

    # 2. og 3. NVDB-takt og automasjon
    manuell_takt, automasjon, total_throughput = sample_nvdb_params(
        rng, scenario['Automasjonsgrad_FME']
    )

    # Bygg et modifisert scenario-objekt uten å mutere originalen
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
    per_kommune_nvdb = [(k['KomNr'], k['ferdigdato_nvdb']) for k in kommunestate]
    return {
        'max_kartkontor': max_kk,
        'max_nvdb': max_nvdb,
        'per_kommune': per_kommune_nvdb,
        'ukentlig_nvdb': ukentlig_nvdb,
        'sampled_manuell_takt': manuell_takt,
        'sampled_automasjon': automasjon,
        'sampled_throughput': total_throughput,
    }


def aggreger_uke_percentiler(alle_ukentlige):
    """Samle ukentlig_nvdb fra N iterasjoner og beregn percentiler per uke.

    alle_ukentlige: liste av lister av dicts (én per iterasjon).
    Returnerer DataFrame med (uke_aar, uke_nr) og percentiler for
    Ko_Lengde_Kommuner, Lenker_I_Ko, Lenker_Overfort_Hittil, Kommuner_Overfort_Hittil.
    """
    rader = []
    for it, uker in enumerate(alle_ukentlige):
        for u in uker:
            rader.append({**u, 'iter': it})
    if not rader:
        return pd.DataFrame()
    df = pd.DataFrame(rader)

    grp = df.groupby(['uke_aar', 'uke_nr'])
    agg = grp.agg(
        Ko_Lengde_P5=('Ko_Lengde_Kommuner', lambda x: np.percentile(x, 5)),
        Ko_Lengde_P50=('Ko_Lengde_Kommuner', lambda x: np.percentile(x, 50)),
        Ko_Lengde_P95=('Ko_Lengde_Kommuner', lambda x: np.percentile(x, 95)),
        Lenker_I_Ko_P5=('Lenker_I_Ko', lambda x: np.percentile(x, 5)),
        Lenker_I_Ko_P50=('Lenker_I_Ko', lambda x: np.percentile(x, 50)),
        Lenker_I_Ko_P95=('Lenker_I_Ko', lambda x: np.percentile(x, 95)),
        Lenker_Overfort_P5=('Lenker_Overfort_Hittil', lambda x: np.percentile(x, 5)),
        Lenker_Overfort_P50=('Lenker_Overfort_Hittil', lambda x: np.percentile(x, 50)),
        Lenker_Overfort_P95=('Lenker_Overfort_Hittil', lambda x: np.percentile(x, 95)),
        Kommuner_Overfort_P5=('Kommuner_Overfort_Hittil', lambda x: np.percentile(x, 5)),
        Kommuner_Overfort_P50=('Kommuner_Overfort_Hittil', lambda x: np.percentile(x, 50)),
        Kommuner_Overfort_P95=('Kommuner_Overfort_Hittil', lambda x: np.percentile(x, 95)),
        N=('iter', 'count'),
    ).reset_index()
    return agg


def main():
    print('=' * 60)
    print('MONTE CARLO USIKKERHETSANALYSE')
    print('=' * 60)

    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)
    empirisk_mpk = last_empirisk_min_per_km()

    print(f'Kommuner: {len(kommuner)}')
    print(f'Empirisk MIN/KM-fordeling: N={len(empirisk_mpk)}, '
          f'mean={empirisk_mpk.mean():.3f}, std={empirisk_mpk.std():.3f}, '
          f'range=[{empirisk_mpk.min():.3f}, {empirisk_mpk.max():.3f}]')

    rng = np.random.default_rng(SEED)

    summary_rader = []
    varighet_rader = []
    per_kommune_rader = []
    uke_rader = []

    for _, scenario in nvdb.iterrows():
        navn = scenario['Scenario']
        print(f'\n=== {navn} ({N_ITERATIONS} iterasjoner) ===')

        varigheter_dager = []
        kk_varigheter = []
        per_komm_dict = {}
        alle_ukentlige = []

        for it in range(N_ITERATIONS):
            if it % 50 == 0 and it > 0:
                print(f'  Iterasjon {it}/{N_ITERATIONS}...')
            res = kjor_iterasjon(
                rng, kommuner, kontorer, lock_intervals, scenario, empirisk_mpk
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
        # Hent sampled throughput for denne scenario
        scen_rader = [r for r in varighet_rader if r['Scenario'] == navn]
        tp_arr = np.array([r['Sampled_Throughput'] for r in scen_rader])
        summary_rader.append({
            'Scenario': navn,
            'N_Iterasjoner': len(varigheter_dager),
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
        print(f'  Varighet (år) P5/P50/P95: '
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
                'KomNr': komnr,
                'N_Iterasjoner': len(gyldige),
                'Dager_P5': int(np.percentile(dager, 5)),
                'Dager_P50': int(np.percentile(dager, 50)),
                'Dager_P95': int(np.percentile(dager, 95)),
            })

        uke_agg = aggreger_uke_percentiler(alle_ukentlige)
        uke_agg.insert(0, 'Scenario', navn)
        uke_rader.append(uke_agg)

    # Lagre alt
    pd.DataFrame(summary_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_summary.csv'), index=False
    )
    pd.DataFrame(varighet_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_varigheter.csv'), index=False
    )
    pd.DataFrame(per_kommune_rader).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_per_kommune.csv'), index=False
    )
    pd.concat(uke_rader, ignore_index=True).to_csv(
        os.path.join(DATA_DIR, 'monte_carlo_ko_percentiles.csv'), index=False
    )

    print('\n=== Sammendrag ===')
    print(pd.DataFrame(summary_rader).to_string(index=False))
    print(f'\nOutput lagret i {DATA_DIR}')


if __name__ == '__main__':
    main()
