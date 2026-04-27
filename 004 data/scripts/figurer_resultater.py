"""
Resultatfigurer fra heuristikk-kjoeringen.

Produserer:
  07_nvdb_ko.png              - NVDB-kolengde over tid (lenker + kommuner), 3 scenarioer
  08_kumulativ_nvdb.png       - Kumulativ NVDB-overfoering (lenker + kommuner), 3 scenarioer
  09_utnyttelse_heatmap.png   - Kapasitetsutnyttelse per kontor og uke (baseline)
  10_kontor_fremdrift.png     - Kumulativ ferdigstilling per kontor (baseline)
"""

import os
import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_DIR = os.path.join(BASE_DIR, '004 data', 'processed_data')
OUT_DIR = os.path.join(BASE_DIR, '005 report', 'figurer')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['figure.dpi'] = 110
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

SCENARIOER = ['Basis_85', 'Middels_90', 'Samferdsel_96']
SCENARIO_NAVN = {
    'Basis_85': '85 % automasjon',
    'Middels_90': '90 % automasjon',
    'Samferdsel_96': '96 % automasjon',
}
SCENARIO_FARGER = {
    'Basis_85': '#c44e52',
    'Middels_90': '#dd8452',
    'Samferdsel_96': '#55a868',
}

KONTOR_REKKEFOLGE = [
    'Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
    'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø',
]
KONTOR_FARGER = {
    'Oslo': '#4c72b0', 'Hamar': '#55a868', 'Skien': '#c44e52',
    'Kristiansand': '#8172b2', 'Stavanger': '#ccb974',
    'Bergen': '#64b5cd', 'Molde': '#e3855c', 'Trondheim': '#937860',
    'Bodø': '#da8bc3', 'Tromsø': '#8c8c8c',
}


def uke_til_dato(uke_aar, uke_nr):
    return date.fromisocalendar(int(uke_aar), int(uke_nr), 1)


def last_flaskehals():
    dfs = {}
    for s in SCENARIOER:
        df = pd.read_csv(os.path.join(DATA_DIR, f'flaskehals_nvdb_{s}.csv'))
        df['dato'] = pd.to_datetime(
            df.apply(lambda r: uke_til_dato(r['uke_aar'], r['uke_nr']), axis=1)
        )
        dfs[s] = df
    return dfs


def last_tidsplan():
    dfs = {}
    for s in SCENARIOER:
        df = pd.read_csv(
            os.path.join(DATA_DIR, f'tidsplan_{s}.csv'),
            parse_dates=['Ferdigdato_Kartkontor', 'Ferdigdato_NVDB'],
        )
        dfs[s] = df
    return dfs


def last_kapasitet():
    dfs = {}
    for s in SCENARIOER:
        df = pd.read_csv(os.path.join(DATA_DIR, f'kapasitetsbruk_per_uke_{s}.csv'))
        df['dato'] = pd.to_datetime(
            df.apply(lambda r: uke_til_dato(r['uke_aar'], r['uke_nr']), axis=1)
        )
        dfs[s] = df
    return dfs


def fig7_nvdb_ko(flaskehals):
    print('7. NVDB-ko over tid...')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for s in SCENARIOER:
        df = flaskehals[s]
        ax1.plot(df['dato'], df['Lenker_I_Ko'], label=SCENARIO_NAVN[s],
                 color=SCENARIO_FARGER[s], linewidth=2)
        ax2.plot(df['dato'], df['Ko_Lengde_Kommuner'], label=SCENARIO_NAVN[s],
                 color=SCENARIO_FARGER[s], linewidth=2)

    ax1.set_ylabel('Lenker i NVDB-kø')
    ax1.set_title('NVDB-køens utvikling over tid – flaskehalsvisualisering')
    ax1.grid(alpha=0.3)
    ax1.legend(loc='upper right')
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' '))
    )

    ax2.set_ylabel('Antall kommuner i kø')
    ax2.set_xlabel('Dato')
    ax2.grid(alpha=0.3)
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.setp(ax2.get_xticklabels(), rotation=0)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '07_nvdb_ko.png'))
    plt.close()


def fig8_kumulativ_nvdb(flaskehals):
    print('8. Kumulativ NVDB-overfoering...')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    for s in SCENARIOER:
        df = flaskehals[s]
        ax1.plot(df['dato'], df['Lenker_Overfort_Hittil'], label=SCENARIO_NAVN[s],
                 color=SCENARIO_FARGER[s], linewidth=2)
        ax2.plot(df['dato'], df['Kommuner_Overfort_Hittil'], label=SCENARIO_NAVN[s],
                 color=SCENARIO_FARGER[s], linewidth=2)

    ax1.set_ylabel('Kumulativt antall lenker overført til NVDB')
    ax1.set_xlabel('Dato')
    ax1.set_title('Kumulativ lenkeoverføring')
    ax1.grid(alpha=0.3)
    ax1.legend(loc='lower right')
    ax1.axhline(2630964, color='gray', linestyle='--', alpha=0.5,
                label='Totalt 2 630 964 lenker')
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' '))
    )
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax2.set_ylabel('Kumulativt antall kommuner overført')
    ax2.set_xlabel('Dato')
    ax2.set_title('Kumulativ kommuneoverføring')
    ax2.grid(alpha=0.3)
    ax2.axhline(357, color='gray', linestyle='--', alpha=0.5,
                label='Totalt 357 kommuner')
    ax2.legend(loc='lower right')
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '08_kumulativ_nvdb.png'))
    plt.close()


def fig9_utnyttelse(kapasitet):
    print('9. Utnyttelse heatmap...')
    # Kartkontor-fasen er uavhengig av NVDB-scenario, bruk Basis_85
    df = kapasitet['Basis_85'].copy()

    # Behold kun uker med aktivitet paa minst ett kontor
    aktive = df.groupby('dato')['Timer_Brukt'].sum()
    aktive_dates = aktive[aktive > 0].index
    df = df[df['dato'].isin(aktive_dates)]

    pivot = df.pivot_table(index='Kartkontor', columns='dato',
                           values='Utnyttelse', fill_value=0)
    pivot = pivot.reindex(KONTOR_REKKEFOLGE)

    fig, ax = plt.subplots(figsize=(14, 5.5))
    im = ax.imshow(pivot.values, aspect='auto', cmap='YlGnBu', vmin=0, vmax=1)

    ax.set_yticks(range(len(KONTOR_REKKEFOLGE)))
    ax.set_yticklabels(KONTOR_REKKEFOLGE)

    dates = pivot.columns
    step = max(1, len(dates) // 18)
    tick_idx = list(range(0, len(dates), step))
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(
        [pd.to_datetime(dates[i]).strftime('%b %Y') for i in tick_idx],
        rotation=45, ha='right', fontsize=9,
    )

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label('Kapasitetsutnyttelse')

    ax.set_title('Kapasitetsutnyttelse per kartkontor og uke (baseline-heuristikk)\n'
                 'Lav utnyttelse = ingen arbeidbare kommuner (Geovekst-låsning eller tom kø)',
                 fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '09_utnyttelse_heatmap.png'))
    plt.close()


def fig10_kontor_fremdrift(tidsplan):
    print('10. Kontor-fremdrift...')
    df = tidsplan['Basis_85'].copy()

    fig, ax = plt.subplots(figsize=(12, 6))
    for kontor in KONTOR_REKKEFOLGE:
        sub = df[df['Kartkontor'] == kontor].sort_values('Ferdigdato_Kartkontor')
        if sub.empty:
            continue
        dates = sub['Ferdigdato_Kartkontor'].values
        cum = np.arange(1, len(sub) + 1)
        ax.step(dates, cum, where='post', label=kontor,
                color=KONTOR_FARGER[kontor], linewidth=2)

    ax.set_xlabel('Dato')
    ax.set_ylabel('Kumulativt antall kommuner ferdig kvalitetshevet')
    ax.set_title('Kartkontor-fremdrift: kumulativ ferdigstilling per kontor (baseline)\n'
                 'Startsprang 2026-05-01 = de 62 kommunene som allerede er ferdige',
                 fontsize=11)
    ax.legend(loc='center right', ncol=2, fontsize=9)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '10_kontor_fremdrift.png'))
    plt.close()


def main():
    print('=== GENERERER RESULTATFIGURER ===')
    flaskehals = last_flaskehals()
    tidsplan = last_tidsplan()
    kapasitet = last_kapasitet()

    fig7_nvdb_ko(flaskehals)
    fig8_kumulativ_nvdb(flaskehals)
    fig9_utnyttelse(kapasitet)
    fig10_kontor_fremdrift(tidsplan)

    print(f'\nLagret i: {OUT_DIR}')


if __name__ == '__main__':
    main()
