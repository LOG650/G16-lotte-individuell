"""
Kapasitets-sensitivitetsanalyse (Bolk B).

Kjoerer MIP (lex-opt) for et sett med kapasitetsvariasjoner per NVDB-scenario,
og lagrer sammenlignende resultater. Viser NAAR og HVOR omfordeling mellom
kartkontor aktiveres som respons paa kapasitetsforstyrrelser.

Variasjoner:
  S0_Baseline    - nominell kapasitet
  S1_Trondheim50 - Trondheim -50 %% (krise, f.eks. sykefravaer)
  S2_Alle_pluss20 - alle kontor +20 %% (rekruttering/utvidelse)
  S3_Omfordeling - smaa kontor +50 %%, store -20 %% (politisk omfordeling)
  S4_Alle_minus15 - alle kontor -15 %% (sparekrav)
  S5_Alle_minus50 - alle kontor -50 %% (ekstrem, for aa vise kartkontor-bundet regime)

Output i processed_data/:
  mip_sensitivitet_<sensitivitet>_<nvdb_scenario>.csv  (tidsplan per case)
  oppsummering_sensitivitet.csv                         (samlet resultat)
"""

import os
import sys
import argparse
import pandas as pd
import pulp

# mip_modell.py wrapper sys.stdout selv
from mip_modell import (
    last_data, bygg_modell, solve_lex_opt, solve_modell, solve_vektet,
    ekstraher_loesning, maaned_til_dato,
    T_MAX, SOLVER_TIDSGRENSE_SEK, STARTDATO, DATA_DIR,
)


# --- Sensitivitetsvarianter ----------------------------------------------
def lag_varianter():
    """Returner liste av (navn, kapasitet_endring_dict). kapasitet_endring er
    multiplikator per kontor; manglende noekkel betyr 1.0."""
    stor_kontor = ['Oslo', 'Bergen', 'Trondheim']
    smaa_kontor = ['Bodø', 'Molde', 'Skien', 'Stavanger']

    varianter = [
        ('S0_Baseline', {}),
        ('S1_Trondheim50', {'Trondheim': 0.5}),
        ('S2_Alle_pluss20', {k: 1.2 for k in [
            'Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
            'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø',
        ]}),
        ('S3_Omfordeling', {**{k: 1.5 for k in smaa_kontor},
                            **{k: 0.8 for k in stor_kontor}}),
        ('S4_Alle_minus15', {k: 0.85 for k in [
            'Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
            'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø',
        ]}),
        ('S5_Alle_minus50', {k: 0.5 for k in [
            'Oslo', 'Hamar', 'Skien', 'Kristiansand', 'Stavanger',
            'Bergen', 'Molde', 'Trondheim', 'Bodø', 'Tromsø',
        ]}),
    ]
    return varianter


def juster_kapasitet(kontorer_df, endring):
    """Anvend multiplikator paa Kapasitet_Ukesverk per kontor. Returner ny df."""
    df = kontorer_df.copy()
    df['Kapasitet_Ukesverk'] = df['Kapasitet_Ukesverk'].astype(float)
    for kontor, mult in endring.items():
        mask = df['Kartkontor'] == kontor
        if not mask.any():
            print(f'  ADVARSEL: kontor "{kontor}" finnes ikke, hopper over')
            continue
        df.loc[mask, 'Kapasitet_Ukesverk'] = (
            df.loc[mask, 'Kapasitet_Ukesverk'] * mult
        )
    return df


def lagre_tidsplan(data, losning, filnavn):
    rader = []
    for a in data['aktive']:
        kn = a['KomNr']
        rader.append({
            'KomNr': kn,
            'Kommune': a['Kommune'],
            'Hjemmekontor': a['Hjemmekontor'],
            'Kartkontor_MIP': losning['assignment'].get(kn, ''),
            'Omfordelt': losning['assignment'].get(kn) != a['Hjemmekontor'],
            'Timer': round(a['Timer'], 2),
            'Lenker': a['Lenker'],
            'Ferdigdato_Kartkontor_Mnd': losning['ferdig_kk'].get(kn),
            'Ferdigdato_NVDB_Mnd': losning['ferdig_nvdb'].get(kn),
        })
    pd.DataFrame(rader).to_csv(os.path.join(DATA_DIR, filnavn), index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenarioer', nargs='+', default=None,
                        help='NVDB-scenarioer (default alle 3)')
    parser.add_argument('--varianter', nargs='+', default=None,
                        help='Sensitivitets-varianter (default alle)')
    parser.add_argument('--tidsgrense', type=int, default=SOLVER_TIDSGRENSE_SEK)
    parser.add_argument('--mode', choices=['makespan', 'lex', 'vektet'], default='vektet')
    args = parser.parse_args()

    kommuner, kontorer, geovekst, nvdb = last_data()
    varianter = lag_varianter()

    if args.scenarioer:
        nvdb = nvdb[nvdb['Scenario'].isin(args.scenarioer)].reset_index(drop=True)
    if args.varianter:
        varianter = [v for v in varianter if v[0] in args.varianter]

    print(f'Kjorer {len(varianter)} varianter x {len(nvdb)} NVDB-scenarioer = '
          f'{len(varianter) * len(nvdb)} MIP-losninger')

    oppsummering = []

    for var_navn, endring in varianter:
        kontorer_var = juster_kapasitet(kontorer, endring)
        total_aarlig = kontorer_var['Kapasitet_Ukesverk'].sum() * 37.5
        print(f'\n{"=" * 60}')
        print(f'Variant: {var_navn}')
        print(f'  Total aarlig kap: {total_aarlig:.0f} timer '
              f'({kontorer_var["Kapasitet_Ukesverk"].sum():.0f} ukesverk)')
        if endring:
            print(f'  Endringer: {endring}')
        print('=' * 60)

        for _, scenario in nvdb.iterrows():
            nvdb_navn = scenario['Scenario']
            T = T_MAX[nvdb_navn]
            print(f'\n  --- {nvdb_navn} (T={T}) ---')

            prob, data = bygg_modell(scenario, kommuner, kontorer_var, geovekst)

            if args.mode == 'lex':
                lex = solve_lex_opt(prob, data, tidsgrense=args.tidsgrense, msg=False)
                tid = lex['tid_1'] + lex['tid_2']
                status_str = f'{pulp.LpStatus[lex["status_1"]]}/{pulp.LpStatus[lex["status_2"]]}'
            elif args.mode == 'vektet':
                res = solve_vektet(prob, data, tidsgrense=args.tidsgrense, msg=False)
                tid = res['tid_1']
                status_str = pulp.LpStatus[res['status_1']]
            else:
                st, tid = solve_modell(prob, tidsgrense=args.tidsgrense, msg=False)
                status_str = pulp.LpStatus[st]

            los = ekstraher_loesning(prob, data)
            n_reassigned = sum(
                1 for a in data['aktive']
                if los['assignment'].get(a['KomNr']) != a['Hjemmekontor']
            )
            kk_max = max(
                (v for v in los['ferdig_kk'].values() if v is not None),
                default=None,
            )

            filnavn = f'mip_sensitivitet_{var_navn}_{nvdb_navn}.csv'
            lagre_tidsplan(data, los, filnavn)

            print(f'    Tid: {tid:.0f}s | status: {status_str}')
            print(f'    Makespan: {los["makespan_mnd"]} mnd ({los["makespan_mnd"]/12:.2f} aar)')
            print(f'    Omfordelt: {n_reassigned}/{len(data["I"])}')
            print(f'    Kartkontor siste mnd: {kk_max}')

            oppsummering.append({
                'Variant': var_navn,
                'NVDB_Scenario': nvdb_navn,
                'Total_Ukesverk': kontorer_var['Kapasitet_Ukesverk'].sum(),
                'Status': status_str,
                'Makespan_Mnd': los['makespan_mnd'],
                'Makespan_Aar': round(los['makespan_mnd'] / 12, 2),
                'Kartkontor_Siste_Mnd': kk_max,
                'Kommuner_Omfordelt': n_reassigned,
                'Aktive_Kommuner': len(data['I']),
                'Solver_Tid_Sek': round(tid, 1),
            })

    df_opp = pd.DataFrame(oppsummering)
    df_opp.to_csv(os.path.join(DATA_DIR, 'oppsummering_sensitivitet.csv'), index=False)
    print(f'\n{"=" * 60}')
    print('Oppsummering')
    print('=' * 60)
    print(df_opp.to_string(index=False))
    print(f'\nLagret: oppsummering_sensitivitet.csv + {len(oppsummering)} tidsplaner')


if __name__ == '__main__':
    main()
