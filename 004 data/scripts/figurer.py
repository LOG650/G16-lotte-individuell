"""
Genererer deskriptive figurer for rapporten fra processed_data.
Lagrer alle figurer som PNG i 005 report/figurer/.
"""

import os
import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import geopandas as gpd
from matplotlib.patches import Rectangle

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_DIR = os.path.join(BASE_DIR, '004 data', 'processed_data')
RAW_DIR = os.path.join(BASE_DIR, '004 data', 'raw_data')
OUT_DIR = os.path.join(BASE_DIR, '005 report', 'figurer')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['figure.dpi'] = 110
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

KONTOR_COORDS = {
    'Oslo': (59.91, 10.75),
    'Hamar': (60.80, 11.08),
    'Skien': (59.21, 9.61),
    'Kristiansand': (58.15, 8.00),
    'Stavanger': (58.97, 5.73),
    'Bergen': (60.39, 5.32),
    'Molde': (62.74, 7.16),
    'Trondheim': (63.43, 10.39),
    'Bodø': (67.28, 14.41),
    'Tromsø': (69.65, 18.96),
}

KONTOR_REKKEFOLGE = ['Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
                     'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø']

FYLKE_TIL_KONTOR = {
    3: 'Oslo', 31: 'Oslo', 32: 'Oslo', 33: 'Oslo',
    34: 'Hamar',
    39: 'Skien', 40: 'Skien',
    42: 'Kristiansand',
    11: 'Stavanger',
    46: 'Bergen',
    15: 'Molde',
    50: 'Trondheim',
    18: 'Bodø',
    55: 'Tromsø', 56: 'Tromsø',
}

KONTOR_FARGER = {
    'Oslo': '#4c72b0',
    'Hamar': '#55a868',
    'Skien': '#c44e52',
    'Kristiansand': '#8172b2',
    'Stavanger': '#ccb974',
    'Bergen': '#64b5cd',
    'Molde': '#e3855c',
    'Trondheim': '#937860',
    'Bodø': '#da8bc3',
    'Tromsø': '#8c8c8c',
}


def last_data():
    kommuner = pd.read_csv(os.path.join(DATA_DIR, 'master_kommuner.csv'))
    kontorer = pd.read_csv(os.path.join(DATA_DIR, 'kapasitet_kontorer.csv'))
    geovekst = pd.read_csv(os.path.join(DATA_DIR, 'geovekst_prosjekter.csv'))
    return kommuner, kontorer, geovekst


def fig1_kart(kommuner):
    print('1. Kart med kartkontor og antall kommuner...')
    antall = kommuner.groupby('Kartkontor').size().to_dict()

    fylker = gpd.read_file(os.path.join(RAW_DIR, 'kartverket_fylker.geojson'))
    fylker['fylkesnummer'] = fylker['fylkesnummer'].astype(int)
    fylker['Kartkontor'] = fylker['fylkesnummer'].map(FYLKE_TIL_KONTOR)

    fig, ax = plt.subplots(figsize=(9, 11))
    for kontor in KONTOR_REKKEFOLGE:
        sub = fylker[fylker['Kartkontor'] == kontor]
        if sub.empty:
            continue
        sub.plot(ax=ax, color=KONTOR_FARGER[kontor], edgecolor='white',
                 linewidth=0.6, alpha=0.72)

    for kontor, (lat, lon) in KONTOR_COORDS.items():
        n = antall.get(kontor, 0)
        ax.scatter(lon, lat, s=80, c='black', edgecolors='white',
                   linewidth=1.2, zorder=4)
        ax.annotate(f'{kontor} ({n})',
                    xy=(lon, lat), xytext=(8, 8),
                    textcoords='offset points',
                    fontsize=9.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.9),
                    zorder=5)

    ax.set_xlim(3.5, 32)
    ax.set_ylim(57.5, 71.5)
    ax.set_aspect(1.8)
    ax.set_title('Fylkeskartkontor og fylker de har ansvar for\n'
                 '(tall i parentes: antall kommuner under kontoret)',
                 fontsize=12, pad=14)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '01_kart_kontorer.png'))
    plt.close()


def fig2_kapasitet_vs_arbeid(kontorer):
    print('2. Kapasitet vs arbeidsmengde per kontor...')
    df = kontorer.set_index('Kartkontor').reindex(KONTOR_REKKEFOLGE)

    # Beregn estimert timebehov = antall kommuner × snitt(min,max)
    df['Snitt_Timer_Per_Kommune'] = (df['Min_Tidsbruk_Timer']
                                      + df['Max_Tidsbruk_Timer']) / 2
    df['Estimert_Arbeid_Timer'] = df['Antall_Kommuner'] * df['Snitt_Timer_Per_Kommune']
    df['Kapasitet_Timer_Aar'] = df['Kapasitet_Ukesverk'] * 37.5
    df['Estimert_Aar'] = df['Estimert_Arbeid_Timer'] / df['Kapasitet_Timer_Aar']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    x = np.arange(len(df))
    width = 0.38
    ax1.bar(x - width/2, df['Kapasitet_Timer_Aar'], width,
            label='Kapasitet (timer/år)', color='seagreen')
    ax1.bar(x + width/2, df['Estimert_Arbeid_Timer'], width,
            label='Estimert arbeidsmengde (timer)', color='indianred')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df.index, rotation=35, ha='right')
    ax1.set_ylabel('Timer')
    ax1.set_title('Årlig kapasitet vs. estimert total arbeidsmengde')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    colors = ['firebrick' if v > 2 else 'orange' if v > 1 else 'seagreen'
              for v in df['Estimert_Aar']]
    ax2.barh(df.index, df['Estimert_Aar'], color=colors)
    ax2.set_xlabel('Estimert varighet (år ved full kapasitetsutnyttelse)')
    ax2.set_title('Estimert varighet per kontor (uten Geovekst-låsing)')
    ax2.axvline(x=1, color='gray', linestyle='--', alpha=0.6, label='1 år')
    ax2.axvline(x=2, color='red', linestyle='--', alpha=0.6, label='2 år')
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '02_kapasitet_vs_arbeid.png'))
    plt.close()


def fig3_status_per_kontor(kommuner):
    print('3. Status per kontor (stacked bar)...')
    pivot = (kommuner.groupby(['Kartkontor', 'Status']).size()
             .unstack(fill_value=0)
             .reindex(KONTOR_REKKEFOLGE))
    for col in ['Ferdig', 'Påbegynt', 'Ikke påbegynt']:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[['Ferdig', 'Påbegynt', 'Ikke påbegynt']]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = ['seagreen', 'goldenrod', 'lightgray']
    pivot.plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.7)
    ax.set_ylabel('Antall kommuner')
    ax.set_xlabel('Kartkontor')
    ax.set_title('Fremdriftsstatus per kartkontor (april 2026)')
    ax.legend(title='Status')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '03_status_per_kontor.png'))
    plt.close()


def fig5_lastfordeling(kommuner):
    print('5. Lastfordeling: hver kommune som segment per kontor...')
    df = kommuner.copy()
    df = df[df['Gjenstaaende_Lenker'] > 0]

    bins = [0, 1000, 5000, 15000, float('inf')]
    labels = ['< 1 000', '1 000–5 000', '5 000–15 000', '≥ 15 000']
    colors = ['#cfe3ee', '#7fb7c9', '#3c7990', '#14314f']
    df['Kategori'] = pd.cut(df['Gjenstaaende_Lenker'], bins=bins,
                             labels=labels, right=False)

    fig, ax = plt.subplots(figsize=(13, 6))

    for i, kontor in enumerate(KONTOR_REKKEFOLGE):
        sub = df[df['Kartkontor'] == kontor].sort_values(
            'Gjenstaaende_Lenker', ascending=False)
        left = 0
        for _, rad in sub.iterrows():
            kat = str(rad['Kategori'])
            color = colors[labels.index(kat)]
            ax.barh(i, rad['Gjenstaaende_Lenker'], left=left, height=0.72,
                    color=color, edgecolor='white', linewidth=0.3)
            left += rad['Gjenstaaende_Lenker']

    legend_elements = [plt.Rectangle((0, 0), 1, 1, color=c, label=l,
                                      edgecolor='white')
                       for c, l in zip(colors, labels)]
    ax.legend(handles=legend_elements, title='Lenker per kommune',
              loc='lower right', framealpha=0.95)

    ax.set_yticks(range(len(KONTOR_REKKEFOLGE)))
    ax.set_yticklabels(KONTOR_REKKEFOLGE)
    ax.invert_yaxis()
    ax.set_xlabel('Gjenstående lenker (kommuner sortert størst til minst)')
    ax.set_title('Lastfordeling per kontor\n'
                 'Hver horisontal søyle er ett kontors samlede '
                 'gjenstående arbeid. Hvert segment er én kommune.',
                 fontsize=11)
    ax.grid(axis='x', alpha=0.3)
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '05_lastfordeling.png'))
    plt.close()


def fig4_geovekst_heatmap(geovekst):
    print('4. Geovekst-låsing per måned og kontor (heat map)...')
    df = geovekst.copy()
    df['Laaseperiode_Start'] = pd.to_datetime(df['Laaseperiode_Start'])
    df['Laaseperiode_Slutt'] = pd.to_datetime(df['Laaseperiode_Slutt'])
    df = df.dropna(subset=['Laaseperiode_Start', 'Laaseperiode_Slutt'])

    # Dedupliser: én kommune kan være i flere prosjekter, tell unike KomNr
    df = df.drop_duplicates(subset=['KomNr', 'Laaseperiode_Start',
                                     'Laaseperiode_Slutt'])

    start_min = df['Laaseperiode_Start'].min().replace(day=1)
    slutt_max = df['Laaseperiode_Slutt'].max()
    maaneder = pd.date_range(start_min, slutt_max, freq='MS')

    matrise = np.zeros((len(KONTOR_REKKEFOLGE), len(maaneder)), dtype=int)
    for i, kontor in enumerate(KONTOR_REKKEFOLGE):
        sub = df[df['Kartkontor'] == kontor]
        for j, maaned in enumerate(maaneder):
            mnd_slutt = maaned + pd.offsets.MonthEnd(0)
            # Unike kommuner som er låst i denne måneden
            aktive = sub[(sub['Laaseperiode_Start'] <= mnd_slutt)
                         & (sub['Laaseperiode_Slutt'] >= maaned)]
            matrise[i, j] = aktive['KomNr'].nunique()

    fig, ax = plt.subplots(figsize=(13, 5.5))
    im = ax.imshow(matrise, aspect='auto', cmap='YlOrRd', vmin=0)

    ax.set_yticks(range(len(KONTOR_REKKEFOLGE)))
    ax.set_yticklabels(KONTOR_REKKEFOLGE)
    ax.set_xticks(range(len(maaneder)))
    ax.set_xticklabels([m.strftime('%b %Y') for m in maaneder],
                        rotation=45, ha='right', fontsize=9)

    terskel = matrise.max() * 0.55 if matrise.max() > 0 else 1
    for i in range(matrise.shape[0]):
        for j in range(matrise.shape[1]):
            if matrise[i, j] > 0:
                farge = 'white' if matrise[i, j] > terskel else 'black'
                ax.text(j, i, str(matrise[i, j]), ha='center', va='center',
                        color=farge, fontsize=8)

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label('Antall låste kommuner')

    ax.set_title('Antall kommuner låst av Geovekst-prosjekter, '
                 'per måned og kartkontor',
                 fontsize=12, pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '04_geovekst_heatmap.png'))
    plt.close()


def fig6_lenker_histogram(kommuner):
    print('6. Histogram + topp-10 kommuner...')
    data = kommuner['Antall_Lenker'].dropna()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.hist(data, bins=40, color='steelblue', edgecolor='navy', alpha=0.85)
    ax1.set_xlabel('Antall lenker per kommune')
    ax1.set_ylabel('Antall kommuner')
    ax1.set_title('Fordeling av arbeidsmengde')
    ax1.grid(axis='y', alpha=0.3)
    median_val = int(data.median())
    snitt_val = int(data.mean())
    ax1.axvline(median_val, color='red', linestyle='--',
                label=f'Median: {median_val:,}'.replace(',', ' '))
    ax1.axvline(snitt_val, color='orange', linestyle='--',
                label=f'Snitt: {snitt_val:,}'.replace(',', ' '))
    ax1.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
    ax1.legend()

    sortert = np.sort(data.values)[::-1]
    n = len(sortert)
    andel_kommuner = np.arange(1, n + 1) / n * 100
    kumulativ_lenker = np.cumsum(sortert) / sortert.sum() * 100

    ax2.plot(andel_kommuner, kumulativ_lenker, color='#14314f', linewidth=2.2,
             label='Faktisk fordeling')
    ax2.plot([0, 100], [0, 100], 'k--', alpha=0.45, linewidth=1,
             label='Jevn fordeling')
    ax2.fill_between(andel_kommuner, andel_kommuner, kumulativ_lenker,
                      alpha=0.18, color='#14314f')

    idx_80 = int(np.argmax(kumulativ_lenker >= 80))
    andel_for_80 = andel_kommuner[idx_80]
    ax2.axhline(80, color='red', linestyle=':', alpha=0.55, linewidth=1)
    ax2.axvline(andel_for_80, color='red', linestyle=':', alpha=0.55,
                 linewidth=1)
    ax2.scatter([andel_for_80], [80], color='red', s=60, zorder=5)
    ax2.annotate(f'{andel_for_80:.0f} % av kommunene\ngir 80 % av arbeidet',
                  xy=(andel_for_80, 80),
                  xytext=(andel_for_80 + 15, 55),
                  fontsize=10,
                  arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                  bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                             edgecolor='red', alpha=0.9))

    ax2.set_xlabel('Andel kommuner (sortert størst til minst, %)')
    ax2.set_ylabel('Kumulativ andel av alle lenker (%)')
    ax2.set_title('Arbeidskonsentrasjon (Pareto-kurve)')
    ax2.grid(alpha=0.3)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 101)
    ax2.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, '06_lenker_histogram.png'))
    plt.close()


def print_noekkeltall(kommuner, kontorer, geovekst):
    print('\n=== NØKKELTALL FOR RAPPORT ===')
    print(f'Totalt antall kommuner: {len(kommuner)}')
    print(f'Antall kartkontor: {len(kontorer)}')
    print(f'Totalt antall lenker: {int(kommuner["Antall_Lenker"].sum()):,}')
    print(f'Gjenstående lenker: {int(kommuner["Gjenstaaende_Lenker"].sum()):,}')

    status = kommuner['Status'].value_counts()
    for s, n in status.items():
        print(f'  {s}: {n}')

    laast = kommuner['Er_Laast'].sum()
    print(f'Kommuner låst av Geovekst: {int(laast)}')
    print(f'Antall geovekst-prosjekt-par: {len(geovekst)}')

    kapasitet_sum = kontorer['Kapasitet_Ukesverk'].sum()
    print(f'Total årlig kapasitet: {kapasitet_sum} ukesverk = '
          f'{kapasitet_sum * 37.5:.0f} timer/år')


def main():
    print('=== GENERERER FIGURER ===\n')
    kommuner, kontorer, geovekst = last_data()

    fig1_kart(kommuner)
    fig2_kapasitet_vs_arbeid(kontorer)
    fig3_status_per_kontor(kommuner)
    fig4_geovekst_heatmap(geovekst)
    fig5_lastfordeling(kommuner)
    fig6_lenker_histogram(kommuner)

    print_noekkeltall(kommuner, kontorer, geovekst)
    print(f'\nFigurer lagret i: {OUT_DIR}')


if __name__ == '__main__':
    main()
