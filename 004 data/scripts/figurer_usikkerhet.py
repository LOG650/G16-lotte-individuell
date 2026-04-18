"""
Usikkerhetsfigurer basert på Monte Carlo-kjoeringen.

Produserer:
  11_fanchart_nvdb.png          - Kumulativ NVDB-overfoering med P5-P95-baand per scenario
  12_histogram_varighet.png     - Fordeling av totalvarighet per scenario
  13_per_kontor_boxplot.png     - Fordeling av median kommune-ferdigdato per kontor
"""

import os
import sys
import io
import numpy as np
import pandas as pd
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
    'Basis_85': 'Basis (85 % auto)',
    'Middels_90': 'Middels (90 % auto)',
    'Samferdsel_96': 'Samferdsel (96 % auto)',
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


def uke_til_dato(uke_aar, uke_nr):
    return date.fromisocalendar(int(uke_aar), int(uke_nr), 1)


def fig11_fanchart():
    print('11. Fanchart NVDB...')
    df = pd.read_csv(os.path.join(DATA_DIR, 'monte_carlo_ko_percentiles.csv'))
    df['dato'] = pd.to_datetime(
        df.apply(lambda r: uke_til_dato(r['uke_aar'], r['uke_nr']), axis=1)
    )

    # Kommuner-percentilene er diskrete (heltall 0-357) og blir ujevne
    # i ukentlig oppløsning. Glatter med 4-ukers rullende snitt.
    smooth_cols = ['Kommuner_Overfort_P5', 'Kommuner_Overfort_P50',
                   'Kommuner_Overfort_P95']
    df = df.sort_values(['Scenario', 'dato']).copy()
    for col in smooth_cols:
        df[col] = (df.groupby('Scenario')[col]
                     .transform(lambda s: s.rolling(4, min_periods=1, center=True).mean()))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    for s in SCENARIOER:
        sub = df[df['Scenario'] == s].sort_values('dato')
        if sub.empty:
            continue
        c = SCENARIO_FARGER[s]
        ax1.fill_between(sub['dato'], sub['Lenker_Overfort_P5'],
                         sub['Lenker_Overfort_P95'], color=c, alpha=0.22)
        ax1.plot(sub['dato'], sub['Lenker_Overfort_P50'], color=c,
                 linewidth=2, label=SCENARIO_NAVN[s])
        ax2.fill_between(sub['dato'], sub['Kommuner_Overfort_P5'],
                         sub['Kommuner_Overfort_P95'], color=c, alpha=0.22)
        ax2.plot(sub['dato'], sub['Kommuner_Overfort_P50'], color=c,
                 linewidth=2, label=SCENARIO_NAVN[s])

    ax1.set_ylabel('Kumulativt antall lenker overført')
    ax1.axhline(2630964, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    ax1.legend(loc='lower right')
    ax1.grid(alpha=0.3)
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' '))
    )
    ax1.set_title('Monte Carlo-usikkerhetsbånd for NVDB-overføring '
                  '(500 iterasjoner per scenario, skyggelagt område = P5–P95)')

    ax2.set_ylabel('Kumulativt antall kommuner overført')
    ax2.axhline(357, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    ax2.grid(alpha=0.3)
    ax2.set_xlabel('Dato')
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '11_fanchart_nvdb.png'))
    plt.close()


def fig12_histogram():
    print('12. Histogram varighet...')
    df = pd.read_csv(os.path.join(DATA_DIR, 'monte_carlo_varigheter.csv'))
    df['Varighet_Aar'] = df['Varighet_Dager'] / 365.25

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)

    for ax, s in zip(axes, SCENARIOER):
        sub = df[df['Scenario'] == s]
        c = SCENARIO_FARGER[s]
        ax.hist(sub['Varighet_Aar'], bins=30, color=c, edgecolor='white',
                alpha=0.78)
        p5, p50, p95 = np.percentile(sub['Varighet_Aar'], [5, 50, 95])
        ax.axvline(p5, color='black', linestyle=':', alpha=0.7,
                   label=f'P5: {p5:.2f} år')
        ax.axvline(p50, color='black', linestyle='-', alpha=0.9,
                   linewidth=2, label=f'P50: {p50:.2f} år')
        ax.axvline(p95, color='black', linestyle=':', alpha=0.7,
                   label=f'P95: {p95:.2f} år')
        ax.set_ylabel('Antall iterasjoner')
        ax.set_title(SCENARIO_NAVN[s])
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel('Total varighet (år)')
    axes[0].set_xlim(left=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '12_histogram_varighet.png'))
    plt.close()


def fig13_per_kontor_boxplot():
    print('13. Per-kontor boxplot...')
    per_komm = pd.read_csv(os.path.join(DATA_DIR, 'monte_carlo_per_kommune.csv'),
                           dtype={'KomNr': str})
    master = pd.read_csv(os.path.join(DATA_DIR, 'master_kommuner.csv'),
                         dtype={'KomNr': str})

    scenario = 'Middels_90'
    sub = per_komm[per_komm['Scenario'] == scenario].merge(
        master[['KomNr', 'Kartkontor']], on='KomNr'
    )

    # Per kontor: P50 NVDB-ferdigdato i aar for hver kommune (fordeling over kommuner)
    data = []
    for kontor in KONTOR_REKKEFOLGE:
        ks = sub[sub['Kartkontor'] == kontor]
        data.append(ks['Dager_P50'].values / 365.25)

    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(data, tick_labels=KONTOR_REKKEFOLGE, patch_artist=True,
                    widths=0.6, showfliers=True)
    for patch in bp['boxes']:
        patch.set_facecolor('#64b5cd')
        patch.set_alpha(0.65)
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(1.5)

    # Overlegg individuelle kommuner som scatter for bedre innsyn
    for i, kontor in enumerate(KONTOR_REKKEFOLGE):
        ks = sub[sub['Kartkontor'] == kontor]
        x = np.random.default_rng(42).normal(i + 1, 0.08, size=len(ks))
        ax.scatter(x, ks['Dager_P50'] / 365.25, color='navy', alpha=0.35,
                   s=12, zorder=3)

    ax.set_xlabel('Kartkontor')
    ax.set_ylabel('Median NVDB-ferdigdato per kommune (år fra 2026-05-01)')
    ax.set_title(f'Fordeling av median NVDB-ferdigdato per kommune, gruppert på kartkontor\n'
                 f'({SCENARIO_NAVN[scenario]})',
                 fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '13_per_kontor_boxplot.png'))
    plt.close()


def main():
    print('=== GENERERER USIKKERHETSFIGURER ===')
    fig11_fanchart()
    fig12_histogram()
    fig13_per_kontor_boxplot()
    print(f'\nLagret i: {OUT_DIR}')


if __name__ == '__main__':
    main()
