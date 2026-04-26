"""
Regelbasert heuristikk for TVS-kvalitetsheving og NVDB-overføring.

Steg 1: Beregn gjenvaerende_timer per kommune (skalert etter gjenstaaende lenker).
Steg 2: Prioritetskoe per kontor:
   1) Last paa STARTDATO   -> sist
   2) Ikke-last           -> stoerst forst (flest gjenvaerende timer)
   3) Last                -> tidligste opplaasning forst
Steg 3: Dag-for-dag-simulering over arbeidsdager (man-fre). NVDB-koen
   drenes parallelt fra NVDB-startdato. Spillover: om en kommune blir ferdig
   midt i en dag, brukes resterende budsjett paa neste kommune i koen.

Kjoeres for alle scenarioer i nvdb_overfoering.csv. Output i processed_data/:
   tidsplan_<scenario>.csv
   kapasitetsbruk_per_uke_<scenario>.csv
   flaskehals_nvdb_<scenario>.csv
   oppsummering_scenarioer.csv
"""

import os
import sys
import io
import pandas as pd
from datetime import date, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

# --- Konstanter -----------------------------------------------------------
TIMER_PER_UKESVERK = 37.5
# Simuleringen kjoeres mandag-fredag (52*5 = 260 kalenderdager/aar).
# Kontorene har imidlertid bare ~245 effektive arbeidsdager/aar fordi
# folk tar ferie spredt utover aaret (sommervikarer demper sommeren,
# men ikke nok til aa naa 260). Daglig kapasitet skaleres derfor med
# faktoren 245/260 slik at total levert arbeid per aar blir
# K * 37,5 * (245/260) timer. Endret fra 260 til 245 2026-04-24
# etter avklaring med oppdragsgiver. Forrige fix (230 -> 260,
# 2026-04-22) loste 13 % overbruk men brukte feil aarstall;
# riktig verdi er 245.
ARBEIDSDAGER_PER_AAR = 260
EFFEKTIVE_ARBEIDSDAGER_PER_AAR = 245
KAPASITET_FAKTOR = EFFEKTIVE_ARBEIDSDAGER_PER_AAR / ARBEIDSDAGER_PER_AAR  # 0.9423
STARTDATO = date(2026, 5, 1)
MAX_AAR = 30  # sikkerhetscutoff. Basis_85 P95 = 13,28 aar etter 245-fiks 2026-04-24; stor margin slik at alternative scenarioer (lavere automasjon, lavere kapasitet) ikke risikerer aa bli klippet uten varsel


# --- Datainnlasting -------------------------------------------------------
def last_data():
    kommuner = pd.read_csv(
        os.path.join(DATA_DIR, 'master_kommuner.csv'),
        dtype={'KomNr': str},
    )
    kontorer = pd.read_csv(os.path.join(DATA_DIR, 'kapasitet_kontorer.csv'))
    geovekst = pd.read_csv(
        os.path.join(DATA_DIR, 'geovekst_prosjekter.csv'),
        dtype={'KomNr': str},
        parse_dates=['Laaseperiode_Start', 'Laaseperiode_Slutt'],
    )
    nvdb = pd.read_csv(
        os.path.join(DATA_DIR, 'nvdb_overfoering.csv'),
        parse_dates=['Startdato'],
    )
    return kommuner, kontorer, geovekst, nvdb


def bygg_laseintervaller(geovekst):
    d = {}
    for _, r in geovekst.iterrows():
        d.setdefault(r['KomNr'], []).append(
            (r['Laaseperiode_Start'].date(), r['Laaseperiode_Slutt'].date())
        )
    return d


def er_laast(komnr, dato, lock_intervals):
    for start, slutt in lock_intervals.get(komnr, ()):
        if start <= dato <= slutt:
            return True
    return False


def tidligste_opplaasning_paa(komnr, dato, lock_intervals):
    """Hvis kommunen er last paa 'dato', returner tidligste slutt+1 blant aktive
    laaseperioder. Ellers None."""
    aktive_slutt = [
        slutt for start, slutt in lock_intervals.get(komnr, ())
        if start <= dato <= slutt
    ]
    return (min(aktive_slutt) + timedelta(days=1)) if aktive_slutt else None


# --- Tilstand per kommune -------------------------------------------------
def bygg_kommunestate(kommuner, lock_intervals):
    state = []
    for _, r in kommuner.iterrows():
        antall = float(r['Antall_Lenker']) if pd.notna(r['Antall_Lenker']) else 0.0
        gjenstaar = float(r['Gjenstaaende_Lenker']) if pd.notna(r['Gjenstaaende_Lenker']) else 0.0
        ber_min = float(r['Ber_Tidbruk_Min']) if pd.notna(r['Ber_Tidbruk_Min']) else 0.0
        # Skaler beregnet tidsbruk etter andelen av lenker som gjenstaar
        timer = (ber_min / 60.0) * (gjenstaar / antall) if antall > 0 else 0.0
        ferdig_kk = (r['Status'] == 'Ferdig')
        state.append({
            'KomNr': r['KomNr'],
            'Kommune': r['Kommune'],
            'Kartkontor': r['Kartkontor'],
            'Antall_Lenker': antall,
            'Gjenstaaende_Lenker_Start': gjenstaar,
            # NVDB handler hele lenkemengden for kommunen (ingen er overfoert enda)
            'Lenker_Til_NVDB': antall,
            'Timer_Start': timer,
            'gjenvaerende_timer': 0.0 if ferdig_kk else timer,
            'ferdig_kartkontor': ferdig_kk,
            'ferdigdato_kartkontor': STARTDATO if ferdig_kk else None,
            'ferdigdato_nvdb': None,
        })
    return state


# --- Prioritetskoe per kontor --------------------------------------------
def bygg_koer(kommunestate, lock_intervals):
    koer = {}
    for k in kommunestate:
        if k['ferdig_kartkontor']:
            continue
        koer.setdefault(k['Kartkontor'], []).append(k)

    def sort_key(k):
        laast_naa = er_laast(k['KomNr'], STARTDATO, lock_intervals)
        if not laast_naa:
            return (0, 0, -k['gjenvaerende_timer'])
        opplaasning = tidligste_opplaasning_paa(k['KomNr'], STARTDATO, lock_intervals)
        opp_ord = opplaasning.toordinal() if opplaasning else 0
        return (1, opp_ord, -k['gjenvaerende_timer'])

    for kontor in koer:
        koer[kontor].sort(key=sort_key)
    return koer


# --- Kalenderhjelp --------------------------------------------------------
def er_arbeidsdag(d):
    return d.weekday() < 5


def neste_arbeidsdag(d):
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d = d + timedelta(days=1)
    return d


def uke_key(d):
    iso = d.isocalendar()
    return (iso.year, iso.week)


# --- Simulering -----------------------------------------------------------
def simuler(kommunestate, kontorer, lock_intervals, nvdb_scenario):
    dag_kap = {
        r['Kartkontor']: (
            r['Kapasitet_Ukesverk'] * TIMER_PER_UKESVERK
            * KAPASITET_FAKTOR / ARBEIDSDAGER_PER_AAR
        )
        for _, r in kontorer.iterrows()
    }
    koer = bygg_koer(kommunestate, lock_intervals)

    # "Ferdig"-kommuner gaar rett i NVDB-koen paa STARTDATO
    nvdb_ko = [k for k in kommunestate if k['ferdig_kartkontor']]
    nvdb_start = nvdb_scenario['Startdato'].date()
    nvdb_per_dag = float(nvdb_scenario['Total_Throughput_Per_Dag'])

    ukentlig_kontor = []
    ukentlig_nvdb = []

    lenker_overfort_total = 0.0
    kommuner_overfort = 0

    timer_uke = {k: 0.0 for k in dag_kap}

    dato = STARTDATO if er_arbeidsdag(STARTDATO) else neste_arbeidsdag(STARTDATO)
    cutoff = STARTDATO + timedelta(days=MAX_AAR * 365)
    forrige_uke = uke_key(dato)

    def dump_uke(uke_aar_nr):
        for kontor, tt in timer_uke.items():
            kap_uke = dag_kap[kontor] * 5
            ukentlig_kontor.append({
                'uke_aar': uke_aar_nr[0],
                'uke_nr': uke_aar_nr[1],
                'Kartkontor': kontor,
                'Timer_Brukt': round(tt, 2),
                'Kapasitet_Timer_Uke': round(kap_uke, 2),
                'Utnyttelse': round(tt / kap_uke, 3) if kap_uke else 0.0,
            })
        ukentlig_nvdb.append({
            'uke_aar': uke_aar_nr[0],
            'uke_nr': uke_aar_nr[1],
            'Ko_Lengde_Kommuner': len(nvdb_ko),
            'Lenker_I_Ko': round(sum(k['Lenker_Til_NVDB'] for k in nvdb_ko), 0),
            'Lenker_Overfort_Hittil': round(lenker_overfort_total, 0),
            'Kommuner_Overfort_Hittil': kommuner_overfort,
        })

    while dato <= cutoff:
        uke_naa = uke_key(dato)
        if uke_naa != forrige_uke:
            dump_uke(forrige_uke)
            timer_uke = {k: 0.0 for k in dag_kap}
            forrige_uke = uke_naa

        # Kartkontor-steget
        for kontor, ko in koer.items():
            budsjett = dag_kap[kontor]
            while budsjett > 1e-9 and ko:
                idx = None
                for i, k in enumerate(ko):
                    if not er_laast(k['KomNr'], dato, lock_intervals):
                        idx = i
                        break
                if idx is None:
                    break  # alle gjenvaerende i koen er last i dag
                k = ko[idx]
                bruk = min(budsjett, k['gjenvaerende_timer'])
                k['gjenvaerende_timer'] -= bruk
                budsjett -= bruk
                timer_uke[kontor] += bruk
                if k['gjenvaerende_timer'] <= 1e-9:
                    k['ferdig_kartkontor'] = True
                    k['ferdigdato_kartkontor'] = dato
                    nvdb_ko.append(k)
                    ko.pop(idx)

        # NVDB-steget
        if dato >= nvdb_start:
            kap = nvdb_per_dag
            while kap > 1e-9 and nvdb_ko:
                k = nvdb_ko[0]
                bruk = min(kap, k['Lenker_Til_NVDB'])
                k['Lenker_Til_NVDB'] -= bruk
                kap -= bruk
                lenker_overfort_total += bruk
                if k['Lenker_Til_NVDB'] <= 1e-9:
                    k['ferdigdato_nvdb'] = dato
                    kommuner_overfort += 1
                    nvdb_ko.pop(0)

        alle_ferdig_kk = all(k['ferdig_kartkontor'] for k in kommunestate)
        if alle_ferdig_kk and not nvdb_ko:
            dump_uke(uke_naa)
            break

        dato = neste_arbeidsdag(dato)

    return ukentlig_kontor, ukentlig_nvdb


# --- Output ---------------------------------------------------------------
def lagre_tidsplan(kommunestate, scenario_navn):
    rader = []
    for k in kommunestate:
        rader.append({
            'KomNr': k['KomNr'],
            'Kommune': k['Kommune'],
            'Kartkontor': k['Kartkontor'],
            'Antall_Lenker': k['Antall_Lenker'],
            'Gjenstaaende_Lenker_Start': k['Gjenstaaende_Lenker_Start'],
            'Timer_Start': round(k['Timer_Start'], 2),
            'Ferdigdato_Kartkontor': k['ferdigdato_kartkontor'],
            'Ferdigdato_NVDB': k['ferdigdato_nvdb'],
        })
    df = pd.DataFrame(rader)
    df.to_csv(
        os.path.join(DATA_DIR, f'tidsplan_{scenario_navn}.csv'),
        index=False,
    )
    return df


def main():
    kommuner, kontorer, geovekst, nvdb = last_data()
    lock_intervals = bygg_laseintervaller(geovekst)

    n_ferdig = (kommuner['Status'] == 'Ferdig').sum()
    print(f'Lastet {len(kommuner)} kommuner ({n_ferdig} allerede Ferdig paa kartkontor).')
    print(f'Lastet {len(lock_intervals)} kommuner med minst en Geovekst-laaseperiode.')

    oppsummering = []
    for _, scenario in nvdb.iterrows():
        navn = scenario['Scenario']
        print(f'\n=== Scenario: {navn} (throughput {int(scenario["Total_Throughput_Per_Dag"])} lenker/dag) ===')
        kommunestate = bygg_kommunestate(kommuner, lock_intervals)
        uke_kontor, uke_nvdb = simuler(kommunestate, kontorer, lock_intervals, scenario)

        df_tidsplan = lagre_tidsplan(kommunestate, navn)
        pd.DataFrame(uke_kontor).to_csv(
            os.path.join(DATA_DIR, f'kapasitetsbruk_per_uke_{navn}.csv'), index=False
        )
        pd.DataFrame(uke_nvdb).to_csv(
            os.path.join(DATA_DIR, f'flaskehals_nvdb_{navn}.csv'), index=False
        )

        slutt_kk = df_tidsplan['Ferdigdato_Kartkontor'].max()
        slutt_nvdb = df_tidsplan['Ferdigdato_NVDB'].max()
        uferdig = df_tidsplan['Ferdigdato_NVDB'].isna().sum()
        if pd.notna(slutt_nvdb):
            dager = (pd.Timestamp(slutt_nvdb) - pd.Timestamp(STARTDATO)).days
            aar = round(dager / 365.25, 2)
        else:
            dager = None
            aar = None
        oppsummering.append({
            'Scenario': navn,
            'Ferdig_Kartkontor_Sist': slutt_kk,
            'Ferdig_NVDB_Sist': slutt_nvdb,
            'Varighet_Dager': dager,
            'Varighet_Aar': aar,
            'Uferdig_NVDB_Kommuner': int(uferdig),
        })
        print(f'  Siste kartkontor ferdig: {slutt_kk}')
        print(f'  Siste NVDB ferdig:       {slutt_nvdb}')
        print(f'  Total varighet:          {aar} aar ({dager} dager)')
        if uferdig:
            print(f'  ADVARSEL: {uferdig} kommuner ikke fullfoert innen cutoff ({MAX_AAR} aar)')

    pd.DataFrame(oppsummering).to_csv(
        os.path.join(DATA_DIR, 'oppsummering_scenarioer.csv'), index=False
    )
    print(f'\nOutput lagret i {DATA_DIR}')


if __name__ == '__main__':
    main()
