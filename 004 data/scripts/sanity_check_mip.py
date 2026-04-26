"""
Sanity-check av MIP-loesninger mot bibetingelser.

Sjekker det som er verifiserbart fra tidsplanene aleine (uten aa rekjore MIP):
  C1: hver aktive kommune har en kartkontor-tildeling
  C2 (sanity): total timer per kontor <= kontor sin total horisont-kapasitet
  C5 (laas): Ferdigdato_Kartkontor_Mnd ikke i en laast maaned
  Pre-ferdig: Ferdigdato_Kartkontor_Mnd = 0 for ferdige kommuner
  C7: NVDB-rekkefolge: Ferdigdato_NVDB >= Ferdigdato_Kartkontor
  C8a: NVDB-startdato: Ferdigdato_NVDB >= t0_nvdb
  C8b: NVDB-kapasitet ikke overskredet i noen maaned (kumulativ sjekk)
  C10: alle 357 kommuner har Ferdigdato_NVDB_Mnd
  Makespan: max(Ferdigdato_NVDB_Mnd)+1 stemmer med rapportert
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
from datetime import date

BASE = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(BASE, 'processed_data')

TIMER_PER_UKESVERK = 37.5
KAPASITET_FAKTOR = 245 / 260
ARBEIDSDAGER_PER_MND = 260 / 12

STARTDATO = date(2026, 5, 1)


def dato_til_mnd(d):
    return (d.year - STARTDATO.year) * 12 + (d.month - STARTDATO.month)


def main():
    kommuner = pd.read_csv(os.path.join(DATA, 'master_kommuner.csv'),
                           dtype={'KomNr': str})
    kontorer = pd.read_csv(os.path.join(DATA, 'kapasitet_kontorer.csv'))
    geovekst = pd.read_csv(os.path.join(DATA, 'geovekst_prosjekter.csv'),
                           dtype={'KomNr': str},
                           parse_dates=['Laaseperiode_Start', 'Laaseperiode_Slutt'])
    nvdb = pd.read_csv(os.path.join(DATA, 'nvdb_overfoering.csv'),
                       parse_dates=['Startdato'])
    oppsum = pd.read_csv(os.path.join(DATA, 'oppsummering_mip_vektet.csv'))

    kap_mnd = {
        r['Kartkontor']: r['Kapasitet_Ukesverk'] * TIMER_PER_UKESVERK
                          * KAPASITET_FAKTOR / 12
        for _, r in kontorer.iterrows()
    }

    lock_periods = {}
    for _, r in geovekst.iterrows():
        kn = r['KomNr']
        s = r['Laaseperiode_Start'].date()
        e = r['Laaseperiode_Slutt'].date()
        t_s = max(0, dato_til_mnd(s))
        t_e = dato_til_mnd(e)
        lock_periods.setdefault(kn, set()).update(range(t_s, t_e + 1))

    T_MAX = {'Basis_85': 144, 'Middels_90': 96, 'Samferdsel_96': 54}

    alle_issues = {}
    for scen_navn in ['Basis_85', 'Middels_90', 'Samferdsel_96']:
        issues = []
        fil = os.path.join(DATA, f'tidsplan_mip_vektet_{scen_navn}.csv')
        df = pd.read_csv(fil, dtype={'KomNr': str})
        nvdb_row = nvdb[nvdb['Scenario'] == scen_navn].iloc[0]
        t0_nvdb = max(0, dato_til_mnd(nvdb_row['Startdato'].date()))
        mu = nvdb_row['Total_Throughput_Per_Dag'] * ARBEIDSDAGER_PER_MND
        T = T_MAX[scen_navn]

        master_timer = kommuner.set_index('KomNr')[
            ['Antall_Lenker', 'Gjenstaaende_Lenker', 'Ber_Tidbruk_Min', 'Status']
        ].copy()
        df_full = df.set_index('KomNr').join(master_timer, rsuffix='_master')

        print('\n' + '=' * 60)
        print(f'{scen_navn} (T={T}, t0_nvdb={t0_nvdb} mnd, mu={mu:.0f} lenker/mnd)')
        print('=' * 60)

        # C1: hver aktiv kommune har Kartkontor_MIP
        aktive = df_full[df_full['Status'] != 'Ferdig']
        n_aktive_uten = aktive['Kartkontor_MIP'].isna().sum()
        print(f'C1 (tildeling):  {len(aktive)} aktive | {n_aktive_uten} uten kontor')
        if n_aktive_uten > 0:
            issues.append(f'C1: {n_aktive_uten} aktive uten Kartkontor_MIP')

        # Pre-ferdige
        ferdige = df_full[df_full['Status'] == 'Ferdig']
        pre_kk_ikke_0 = (ferdige['Ferdigdato_Kartkontor_Mnd'] != 0).sum()
        print(f'Pre-ferdig:      {len(ferdige)} ferdige | {pre_kk_ikke_0} med Ferdigdato_Kartkontor != 0')
        if pre_kk_ikke_0 > 0:
            issues.append(f'Pre-ferdig: {pre_kk_ikke_0} med feil Ferdigdato_Kartkontor')

        # C2-sanity
        timer_per_kontor = aktive.groupby('Kartkontor_MIP')['Timer'].sum()
        print(f'C2-sanity (timer per kontor vs T*kap_mnd):')
        for kontor, t in timer_per_kontor.items():
            max_kap = T * kap_mnd[kontor]
            utnyttelse = t / max_kap * 100
            flagg = '!! ' if t > max_kap else '   '
            print(f'  {flagg}{kontor:14s}: {t:7.0f}t / {max_kap:8.0f}t = {utnyttelse:5.1f}%')
            if t > max_kap:
                issues.append(f'C2: {kontor} overskrider horisont-kap')

        # C5
        n_ferdig_i_last = 0
        for komnr, r in aktive.iterrows():
            kk_mnd = r['Ferdigdato_Kartkontor_Mnd']
            if pd.notna(kk_mnd) and komnr in lock_periods:
                if int(kk_mnd) in lock_periods[komnr]:
                    n_ferdig_i_last += 1
        print(f'C5 (laas):       {n_ferdig_i_last} kommuner ferdig i laast maaned')
        if n_ferdig_i_last > 0:
            issues.append(f'C5: {n_ferdig_i_last} ferdig i laast maaned')

        # C7
        amb = aktive.dropna(subset=['Ferdigdato_Kartkontor_Mnd', 'Ferdigdato_NVDB_Mnd'])
        bryter_rk = (amb['Ferdigdato_NVDB_Mnd'] < amb['Ferdigdato_Kartkontor_Mnd']).sum()
        print(f'C7 (NVDB>=KK):   {bryter_rk} brudd')
        if bryter_rk > 0:
            issues.append(f'C7: {bryter_rk} NVDB-rekkefolge')

        # C8a
        bryter_start = (df_full['Ferdigdato_NVDB_Mnd'] < t0_nvdb).sum()
        print(f'C8a (>=t0_nvdb): {bryter_start} brudd')
        if bryter_start > 0:
            issues.append(f'C8a: {bryter_start} foer t0_nvdb')

        # C8b kumulativ
        df_full['Lenker_int'] = df_full['Lenker'].fillna(0)
        nvdb_per_mnd = df_full.groupby('Ferdigdato_NVDB_Mnd')['Lenker_int'].sum().sort_index()
        kumulativ = 0
        bryter_kap = 0
        max_overshoot = 0
        for t, lenker in nvdb_per_mnd.items():
            kumulativ += lenker
            max_kumulativ = mu * (t - t0_nvdb + 1)
            if kumulativ > max_kumulativ + 1:
                bryter_kap += 1
                overshoot = kumulativ - max_kumulativ
                if overshoot > max_overshoot:
                    max_overshoot = overshoot
        print(f'C8b (NVDB-kap):  {bryter_kap} maaneder med brudd (max overshoot {max_overshoot:.0f} lenker)')
        if bryter_kap > 0:
            issues.append(f'C8b: {bryter_kap} mnd NVDB overskredet')

        # C10
        n_uten_nvdb = df_full['Ferdigdato_NVDB_Mnd'].isna().sum()
        print(f'C10 (NVDB-ferdig): {len(df_full)} totalt | {n_uten_nvdb} uten NVDB-ferdig')
        if n_uten_nvdb > 0:
            issues.append(f'C10: {n_uten_nvdb} uten NVDB')

        # Makespan
        rapportert = oppsum[oppsum['Scenario'] == scen_navn]['Makespan_Mnd'].iloc[0]
        fra_csv = int(df_full['Ferdigdato_NVDB_Mnd'].max()) + 1
        match = 'OK' if rapportert == fra_csv else '!! MISMATCH'
        print(f'Makespan:        rapportert={rapportert} mnd, CSV max+1={fra_csv} mnd {match}')
        if rapportert != fra_csv:
            issues.append(f'Makespan: {rapportert} != {fra_csv}')

        alle_issues[scen_navn] = issues

    print('\n' + '=' * 60)
    print('SAMMENDRAG')
    print('=' * 60)
    total = 0
    for scen, issues in alle_issues.items():
        n = len(issues)
        total += n
        print(f'{scen}: {n} issues')
        for i in issues:
            print(f'  - {i}')
    print(f'\nTotalt {total} issues paa tvers av 3 scenarioer.')


if __name__ == '__main__':
    main()
