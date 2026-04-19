"""
Figurer for MIP-modellering (Bolk E).

Produserer figurer 14-19 i 005 report/figurer/.
  14 heuristikk_vs_mip.png      - makespan sammenligning per scenario
  15 kartkontor_ferdig.png      - fordeling av kartkontor-ferdigtid, heur vs MIP
  16 omfordeling_matrise.png    - heatmap hjemmekontor -> MIP-kontor
  17 fanchart_mip.png           - kumulativ NVDB med MC-baand for MIP-plan
  18 kapasitet_sensitivitet.png - makespan per kapasitetsvariant (Bolk B)
  19 omfordeling_varianter.png  - antall omfordelte per variant
"""

import os
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')
FIG_DIR = os.path.join(BASE_DIR, '..', '005 report', 'figurer')
os.makedirs(FIG_DIR, exist_ok=True)

STARTDATO = date(2026, 5, 1)
MIP_MODE = 'vektet'

FARGER = {
    'Basis_85': '#8B0000',
    'Middels_90': '#228B22',
    'Samferdsel_96': '#1E40AF',
    'heuristikk': '#666666',
    'mip': '#D97706',
}


def aar_format(mnd):
    return f'{mnd / 12:.1f}'


# --- Fig 14: Makespan-sammenligning ---
def fig14_makespan_sammenligning():
    df = pd.read_csv(os.path.join(DATA_DIR, f'sammenligning_heuristikk_mip_{MIP_MODE}.csv'))
    if len(df) == 0:
        print('Fig 14: tom sammenligning, hopper over')
        return
    scenarioer = df['Scenario'].tolist()
    heur = df['Varighet_Heuristikk_Aar'].values
    mip = df['Varighet_MIP_Aar'].values

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(scenarioer))
    w = 0.35
    ax.bar(x - w / 2, heur, w, label='Heuristikk', color=FARGER['heuristikk'])
    ax.bar(x + w / 2, mip, w, label='MIP', color=FARGER['mip'])
    for i, (h, m) in enumerate(zip(heur, mip)):
        ax.text(i - w / 2, h + 0.1, f'{h:.2f}', ha='center', fontsize=9)
        ax.text(i + w / 2, m + 0.1, f'{m:.2f}', ha='center', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarioer)
    ax.set_ylabel('Total varighet (aar)')
    ax.set_title('Prosjektvarighet: heuristikk vs. MIP')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fn = os.path.join(FIG_DIR, '14_heuristikk_vs_mip.png')
    fig.tight_layout()
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(f'Fig 14 lagret: {fn}')


# --- Fig 15: Kartkontor-ferdigfordeling ---
def fig15_kartkontor_ferdig():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, scenario in zip(axes, ['Basis_85', 'Middels_90', 'Samferdsel_96']):
        mip_fil = os.path.join(DATA_DIR, f'tidsplan_mip_{MIP_MODE}_{scenario}.csv')
        if not os.path.exists(mip_fil):
            ax.set_title(f'{scenario} (mangler)')
            continue
        mip = pd.read_csv(mip_fil)
        heur_fil = os.path.join(DATA_DIR, f'tidsplan_{scenario}.csv')
        heur = pd.read_csv(heur_fil, parse_dates=['Ferdigdato_Kartkontor'])
        heur['kk_mnd'] = ((heur['Ferdigdato_Kartkontor'].dt.date - STARTDATO)
                          .apply(lambda d: d.days / 30.44))
        mip_vals = mip['Ferdigdato_Kartkontor_Mnd'].dropna()
        bins = np.linspace(0, max(mip_vals.max(), heur['kk_mnd'].max()) + 2, 30)
        ax.hist(heur['kk_mnd'], bins=bins, alpha=0.55,
                label='Heuristikk', color=FARGER['heuristikk'])
        ax.hist(mip_vals, bins=bins, alpha=0.55,
                label='MIP', color=FARGER['mip'])
        ax.set_title(scenario)
        ax.set_xlabel('Kartkontor-ferdigmaaned')
        ax.legend()
        ax.grid(alpha=0.3)
    axes[0].set_ylabel('Antall kommuner')
    fig.suptitle('Fordeling av kartkontor-ferdigtid per scenario')
    fn = os.path.join(FIG_DIR, '15_kartkontor_ferdig.png')
    fig.tight_layout()
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(f'Fig 15 lagret: {fn}')


# --- Fig 16: Omfordelingsmatrise ---
def fig16_omfordeling_matrise(scenario='Middels_90'):
    mip_fil = os.path.join(DATA_DIR, f'tidsplan_mip_{MIP_MODE}_{scenario}.csv')
    if not os.path.exists(mip_fil):
        print(f'Fig 16: mangler {mip_fil}')
        return
    df = pd.read_csv(mip_fil)
    matrise = pd.crosstab(df['Hjemmekontor'], df['Kartkontor_MIP'])
    # Ordne radene og kolonnene i samme rekkefolge
    ordre = ['Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
             'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø']
    ordre = [o for o in ordre if o in matrise.index or o in matrise.columns]
    matrise = matrise.reindex(index=ordre, columns=ordre, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrise.values, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(len(ordre)))
    ax.set_xticklabels(ordre, rotation=45, ha='right')
    ax.set_yticks(range(len(ordre)))
    ax.set_yticklabels(ordre)
    ax.set_xlabel('MIP-kontor')
    ax.set_ylabel('Hjemmekontor')
    ax.set_title(f'Omfordeling hjemmekontor → MIP-kontor ({scenario})')
    for i in range(len(ordre)):
        for j in range(len(ordre)):
            v = matrise.values[i, j]
            if v > 0:
                ax.text(j, i, str(int(v)), ha='center', va='center',
                        color='white' if v > matrise.values.max() / 2 else 'black',
                        fontsize=8)
    plt.colorbar(im, ax=ax, label='Antall kommuner')
    fn = os.path.join(FIG_DIR, '16_omfordeling_matrise.png')
    fig.tight_layout()
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(f'Fig 16 lagret: {fn}')


# --- Fig 18: Kapasitets-sensitivitet (fra Bolk B) ---
def fig18_kapasitet_sensitivitet():
    fil = os.path.join(DATA_DIR, 'oppsummering_sensitivitet.csv')
    if not os.path.exists(fil):
        print('Fig 18: mangler oppsummering_sensitivitet.csv, hopper over')
        return
    df = pd.read_csv(fil)
    scenarioer = df['NVDB_Scenario'].unique()
    varianter = df['Variant'].unique()

    fig, axes = plt.subplots(1, len(scenarioer), figsize=(5 * len(scenarioer), 5))
    if len(scenarioer) == 1:
        axes = [axes]
    for ax, s in zip(axes, scenarioer):
        sub = df[df['NVDB_Scenario'] == s].sort_values('Variant')
        ax.bar(range(len(sub)), sub['Makespan_Aar'],
               color=FARGER.get(s, '#555555'))
        for i, (_, r) in enumerate(sub.iterrows()):
            ax.text(i, r['Makespan_Aar'] + 0.05,
                    f'{r["Makespan_Aar"]:.2f}', ha='center', fontsize=8)
        ax.set_xticks(range(len(sub)))
        ax.set_xticklabels(sub['Variant'], rotation=40, ha='right')
        ax.set_ylabel('Makespan (aar)')
        ax.set_title(s)
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle('Kapasitets-sensitivitet: makespan per variant og NVDB-scenario')
    fn = os.path.join(FIG_DIR, '18_kapasitet_sensitivitet.png')
    fig.tight_layout()
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(f'Fig 18 lagret: {fn}')


# --- Fig 19: Omfordelinger per variant ---
def fig19_omfordeling_varianter():
    fil = os.path.join(DATA_DIR, 'oppsummering_sensitivitet.csv')
    if not os.path.exists(fil):
        print('Fig 19: mangler oppsummering_sensitivitet.csv, hopper over')
        return
    df = pd.read_csv(fil)
    scenarioer = df['NVDB_Scenario'].unique()

    fig, ax = plt.subplots(figsize=(10, 5))
    varianter = sorted(df['Variant'].unique())
    w = 0.8 / len(scenarioer)
    x = np.arange(len(varianter))
    for i, s in enumerate(scenarioer):
        sub = df[df['NVDB_Scenario'] == s].set_index('Variant').reindex(varianter)
        ax.bar(x + (i - (len(scenarioer) - 1) / 2) * w,
               sub['Kommuner_Omfordelt'], w,
               label=s, color=FARGER.get(s, None))
    ax.set_xticks(x)
    ax.set_xticklabels(varianter, rotation=35, ha='right')
    ax.set_ylabel('Antall omfordelte kommuner')
    ax.set_title('Omfordeling mellom kontor under kapasitetsvariasjoner')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fn = os.path.join(FIG_DIR, '19_omfordeling_varianter.png')
    fig.tight_layout()
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(f'Fig 19 lagret: {fn}')


def main():
    fig14_makespan_sammenligning()
    fig15_kartkontor_ferdig()
    fig16_omfordeling_matrise('Middels_90')
    fig18_kapasitet_sensitivitet()
    fig19_omfordeling_varianter()
    print('Ferdig.')


if __name__ == '__main__':
    main()
