"""
MIP-modell for TVS-kvalitetsheving og NVDB-overforing.

Minimerer makespan (antall maaneder for alle kommuner er overfort til NVDB)
med full frihet til omfordeling mellom kartkontor. Reformulert makespan
via binaer Q_t-variabel for aa redusere problemstorrelse.

Beslutningsvariabler:
  y_{i,j} in {0,1}  - kommune i tildeles kontor j
  w_{i,j,t} >= 0    - timer brukt paa (i, j) i maaned t
  z_{i,t} in {0,1}  - kommune i er ferdig paa kartkontor innen maaned t
  D_t >= 0           - lenker overfort til NVDB i maaned t (aggregert)
  Q_t in {0,1}       - 1 hvis ikke alle NVDB-lenker er overfort innen maaned t

Maalfunksjon: min sum_t Q_t

Output i processed_data/:
  tidsplan_mip_<scenario>.csv
  oppsummering_mip.csv
  sammenligning_heuristikk_mip.csv
"""

import os
import sys
import io
import time
import argparse
import pandas as pd
import pulp
from datetime import date, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

# --- Konstanter -----------------------------------------------------------
TIMER_PER_UKESVERK = 37.5
# Kalenderkonvensjon er 260 mandag-fredag-dager/aar, men kontorene har
# bare ~245 effektive arbeidsdager/aar pga ferie spredt utover (sommer-
# vikarer demper sommeren, men ikke nok). Kartkontor-kapasitet skaleres
# derfor med faktoren 245/260 slik at total levert arbeid per aar blir
# K * 37,5 * (245/260). Heuristikken og MIP bruker samme konvensjon.
# NVDB-throughput beholder 260-konvensjonen i denne modellen; samferds-
# elsavd's egen 240-dagers regnestykke gir et dokumentert 240/260-gap
# som er drøftet i 5.1.2 i rapporten. Endret fra 260 til 245 2026-04-24
# etter avklaring med oppdragsgiver. Forrige fix (230 -> 260, 2026-04-22)
# loste 13 %-overbruk men brukte feil aarstall; riktig verdi er 245.
ARBEIDSDAGER_PER_KALENDERAAR = 260   # mandag-fredag per aar (simuleringskalender, NVDB-throughput)
EFFEKTIVE_ARBEIDSDAGER_PER_AAR = 245  # produktive dager pga ferieuttak (kartkontor)
KAPASITET_FAKTOR = EFFEKTIVE_ARBEIDSDAGER_PER_AAR / ARBEIDSDAGER_PER_KALENDERAAR  # 0.9423
ARBEIDSDAGER_PER_MND = ARBEIDSDAGER_PER_KALENDERAAR / 12  # ≈ 21.67 (NVDB-konvertering)
STARTDATO = date(2026, 5, 1)
SOLVER_TIDSGRENSE_SEK = 1800  # 30 min per scenario
MIP_GAP = 0.05  # akseptkriterie 5 %

# Horisonter per scenario (maaneder), ca 15 % buffer over heuristikk
T_MAX = {
    # Etter kalibrering 2026-04-20: manuell takt 300 (var 350), gir ~15 % laengre
    # varighet enn tidligere. Horisontene er justert med ~15 % buffer.
    'Basis_85': 144,      # forventet heuristikk ~10 aar (120 mnd)
    'Middels_90': 96,     # forventet heuristikk ~6.7 aar (80 mnd)
    'Samferdsel_96': 54,  # forventet heuristikk ~2.7 aar (33 mnd) - utvidet fra 48 2026-04-22 for ekstra buffer etter 260-fiks
}


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


def dato_til_maaned(d):
    """Antall maaneder fra STARTDATO til d (floor). Negativ hvis for STARTDATO."""
    return (d.year - STARTDATO.year) * 12 + (d.month - STARTDATO.month)


def maaned_til_dato(t):
    """Konverter maaned-indeks til dato (midt i maaneden)."""
    aar = STARTDATO.year + (STARTDATO.month - 1 + t) // 12
    mnd = (STARTDATO.month - 1 + t) % 12 + 1
    return date(aar, mnd, 15)


# --- Preprosessering ------------------------------------------------------
def bygg_lasematrise(kommuner_df, geovekst_df, T):
    """Returner dict: KomNr -> set av maaneder der kommunen er laast.

    En maaned er laast hvis laaseperioden overlapper maaneden med minst én dag.
    """
    lock = {kn: set() for kn in kommuner_df['KomNr']}
    for _, r in geovekst_df.iterrows():
        kn = r['KomNr']
        if kn not in lock:
            continue
        start = r['Laaseperiode_Start'].date()
        slutt = r['Laaseperiode_Slutt'].date()
        t_start = max(0, dato_til_maaned(start))
        t_slutt = min(T - 1, dato_til_maaned(slutt))
        for t in range(t_start, t_slutt + 1):
            lock[kn].add(t)
    return lock


def bygg_kommunedata(kommuner_df):
    """Splitt kommuner i aktive (trenger kartkontor-arbeid) og ferdige
    (rett i NVDB-koe)."""
    aktive = []
    ferdige = []
    for _, r in kommuner_df.iterrows():
        antall = float(r['Antall_Lenker']) if pd.notna(r['Antall_Lenker']) else 0.0
        gjenstaar = float(r['Gjenstaaende_Lenker']) if pd.notna(r['Gjenstaaende_Lenker']) else 0.0
        ber_min = float(r['Ber_Tidbruk_Min']) if pd.notna(r['Ber_Tidbruk_Min']) else 0.0
        timer = (ber_min / 60.0) * (gjenstaar / antall) if antall > 0 else 0.0
        rec = {
            'KomNr': r['KomNr'],
            'Kommune': r['Kommune'],
            'Hjemmekontor': r['Kartkontor'],
            'Timer': timer,
            'Lenker': antall,
        }
        if r['Status'] == 'Ferdig':
            ferdige.append(rec)
        else:
            aktive.append(rec)
    return aktive, ferdige


def beregn_kapasitet_per_maaned(kontorer_df):
    """Timer per maaned per kontor - matcher heuristikkens effektive kap.

    Heuristikk: daglig_kap = K * 37.5 * (245/260) / 260, kjoeres 260 dg/aar
              => total per aar = K * 37.5 * (245/260)
              => maanedskap = K * 37.5 * (245/260) / 12
    """
    faktor = TIMER_PER_UKESVERK * KAPASITET_FAKTOR / 12
    return {
        r['Kartkontor']: r['Kapasitet_Ukesverk'] * faktor
        for _, r in kontorer_df.iterrows()
    }


# --- Modellbygging --------------------------------------------------------
def bygg_modell(scenario, kommuner_df, kontorer_df, geovekst_df):
    T = T_MAX[scenario['Scenario']]
    aktive, ferdige = bygg_kommunedata(kommuner_df)
    lock = bygg_lasematrise(kommuner_df, geovekst_df, T)
    kap = beregn_kapasitet_per_maaned(kontorer_df)

    # NVDB-kapasitet per maaned (lenker)
    mu = scenario['Total_Throughput_Per_Dag'] * ARBEIDSDAGER_PER_MND

    # NVDB-startmaaned
    t0_nvdb = max(0, dato_til_maaned(scenario['Startdato'].date()))

    # Totale NVDB-lenker (alle kommuner bidrar, ogsaa pre-ferdige)
    total_lenker = sum(a['Lenker'] for a in aktive) + sum(f['Lenker'] for f in ferdige)
    L_preklar = sum(f['Lenker'] for f in ferdige)

    I = [a['KomNr'] for a in aktive]
    J = list(kap.keys())
    Tid = list(range(T))

    timer_i = {a['KomNr']: a['Timer'] for a in aktive}
    lenker_i = {a['KomNr']: a['Lenker'] for a in aktive}

    prob = pulp.LpProblem(f'mip_{scenario["Scenario"]}', pulp.LpMinimize)

    # --- Beslutningsvariabler ---
    y = pulp.LpVariable.dicts('y', [(i, j) for i in I for j in J], cat='Binary')
    w = pulp.LpVariable.dicts(
        'w',
        [(i, j, t) for i in I for j in J for t in Tid],
        lowBound=0, cat='Continuous',
    )
    z = pulp.LpVariable.dicts('z', [(i, t) for i in I for t in Tid], cat='Binary')
    D = pulp.LpVariable.dicts('D', Tid, lowBound=0, cat='Continuous')
    Q = pulp.LpVariable.dicts('Q', Tid, cat='Binary')

    # --- Maalfunksjon: min sum Q_t (ren makespan) ---
    # Sekundaerer maalfunksjoner legges til via solve_lex_opt()
    prob += pulp.lpSum(Q[t] for t in Tid), 'Makespan'

    # C1: Hver kommune til ett kontor
    for i in I:
        prob += pulp.lpSum(y[(i, j)] for j in J) == 1, f'C1_assign_{i}'

    # C2: Totale timer per kommune leveres
    for i in I:
        prob += (
            pulp.lpSum(w[(i, j, t)] for j in J for t in Tid) == timer_i[i],
            f'C2_timer_{i}',
        )

    # C3: Kontor-kapasitet per maaned
    for j in J:
        for t in Tid:
            prob += (
                pulp.lpSum(w[(i, j, t)] for i in I) <= kap[j],
                f'C3_kap_{j}_{t}',
            )

    # C4': Arbeid kun paa tildelt kontor (aggregert over tid - strammere LP enn
    # per-maaned-versjonen men mye faerre rader: I*J i stedet for I*J*T)
    for i in I:
        for j in J:
            prob += (
                pulp.lpSum(w[(i, j, t)] for t in Tid) <= timer_i[i] * y[(i, j)],
                f'C4_ytildeling_{i}_{j}',
            )

    # C5: Ingen arbeid i laaste maaneder (aggregert over kontor)
    for i in I:
        for t in lock.get(i, set()):
            prob += (
                pulp.lpSum(w[(i, j, t)] for j in J) == 0,
                f'C5_lock_{i}_{t}',
            )

    # C6: z_it indikerer kartkontor-fullforing
    #     z_it * timer_i <= sum_{s<=t} sum_j w_{i,j,s}
    for i in I:
        for t in Tid:
            prob += (
                timer_i[i] * z[(i, t)]
                <= pulp.lpSum(w[(i, j, s)] for j in J for s in range(t + 1)),
                f'C6_zferdig_{i}_{t}',
            )

    # C7: Monotoni for z
    for i in I:
        for t in range(1, T):
            prob += z[(i, t)] >= z[(i, t - 1)], f'C7_zmono_{i}_{t}'

    # C8: NVDB-kapasitet per maaned (ingen drenering for t < t0_nvdb)
    for t in Tid:
        if t < t0_nvdb:
            prob += D[t] == 0, f'C8a_nvdbstart_{t}'
        else:
            prob += D[t] <= mu, f'C8b_nvdbkap_{t}'

    # C9: Kumulativ NVDB-drenering <= tilgjengelig (L_preklar + ferdige fra kartkontor)
    for t in Tid:
        prob += (
            pulp.lpSum(D[s] for s in range(t + 1))
            <= L_preklar + pulp.lpSum(lenker_i[i] * z[(i, t)] for i in I),
            f'C9_nvdbtilgjengelig_{t}',
        )

    # C10: All NVDB maa overfores innen horisonten
    prob += (
        pulp.lpSum(D[t] for t in Tid) == total_lenker,
        'C10_nvdbtotal',
    )

    # C11: Q_t = 1 hvis ikke alt overfort innen maaned t
    for t in Tid:
        prob += (
            total_lenker - pulp.lpSum(D[s] for s in range(t + 1))
            <= total_lenker * Q[t],
            f'C11_Qlin_{t}',
        )

    # C12: Monotoni for Q (Q_t <= Q_{t-1}, dvs. naar ferdig, forblir ferdig)
    for t in range(1, T):
        prob += Q[t] <= Q[t - 1], f'C12_Qmono_{t}'

    data = {
        'scenario_navn': scenario['Scenario'],
        'aktive': aktive,
        'ferdige': ferdige,
        'lock': lock,
        'I': I, 'J': J, 'T': T, 'Tid': Tid,
        'y': y, 'w': w, 'z': z, 'D': D, 'Q': Q,
        'timer_i': timer_i, 'lenker_i': lenker_i,
        'kap': kap, 'mu': mu,
        't0_nvdb': t0_nvdb, 'total_lenker': total_lenker, 'L_preklar': L_preklar,
    }
    return prob, data


# --- Losning og ekstrahering ---------------------------------------------
def solve_modell(prob, tidsgrense=SOLVER_TIDSGRENSE_SEK, gap=MIP_GAP, msg=True):
    """Loser MIP-modell med CBC. HiGHS er ikke tilgjengelig via PuLP uten
    egen installasjon, saa CBC er default."""
    solver = pulp.PULP_CBC_CMD(
        msg=msg,
        timeLimit=tidsgrense,
        gapRel=gap,
        presolve=True,
        strong=5,
    )
    start = time.time()
    status = prob.solve(solver)
    elapsed = time.time() - start
    return status, elapsed


def solve_lex_opt(prob, data, tidsgrense=SOLVER_TIDSGRENSE_SEK, gap=MIP_GAP, msg=True):
    """Sekvensiell lex-opt (brukt naar tid og presisjon er viktig):
       Runde 1: min makespan (sum Q_t)
       Runde 2: min sum_i timer_i * sum_t (1 - z_it), gitt makespan <= opt_round1
    """
    Q = data['Q']
    z = data['z']
    I = data['I']
    Tid = data['Tid']
    timer_i = data['timer_i']

    print('    Runde 1: min makespan')
    r1_status, r1_elapsed = solve_modell(prob, tidsgrense=tidsgrense, gap=gap, msg=msg)
    # Q-sum fra R1 brukes som bindende skranke i R2. Det er ikke det samme som
    # endelig makespan (se FIFO-rekonstruksjon i ekstraher_loesning), og kan
    # avvike hvis CBC stoppet med Not Solved.
    makespan_opt = int(round(sum((pulp.value(Q[t]) or 0) for t in Tid)))
    print(f'    Runde 1 ferdig ({r1_elapsed:.1f}s, status {pulp.LpStatus[r1_status]}), '
          f'Q-sum = {makespan_opt} mnd (brukes som skranke i R2)')

    print('    Runde 2: min kartkontor-ferdigtid gitt makespan optimum')
    prob += pulp.lpSum(Q[t] for t in Tid) <= makespan_opt, 'LexOpt_Makespan_Bundet'
    kartkontor_term = pulp.lpSum(
        timer_i[i] * (1 - z[(i, t)]) for i in I for t in Tid
    )
    prob.setObjective(kartkontor_term)
    r2_status, r2_elapsed = solve_modell(prob, tidsgrense=tidsgrense, gap=gap, msg=msg)
    print(f'    Runde 2 ferdig ({r2_elapsed:.1f}s, status {pulp.LpStatus[r2_status]})')

    return {
        'status_1': r1_status,
        'status_2': r2_status,
        'tid_1': r1_elapsed,
        'tid_2': r2_elapsed,
        'makespan_opt': makespan_opt,
    }


def solve_vektet(prob, data, tidsgrense=SOLVER_TIDSGRENSE_SEK, gap=MIP_GAP, msg=True,
                 w2_scale=1.0):
    """En-pass vektet objektiv med tre niveauer:
       obj = W1 * makespan + W2 * kartkontor-ferdigtid + inertia

    Prioritering:
      1. makespan (W1 dominerer)
      2. kartkontor-ferdigtid tidlig (W2 dominerer inertia)
      3. inertia: behold hjemmekontor ved like objektiv

    w2_scale multipliserer W2. Verdi < 1 svekker kartkontor-ferdigtid-prioritet
    og gir mer vekt til inertia. Brukes til aa undersoke om faerre omfordelinger
    kan oppnaas uten aa oke makespan.
    """
    Q = data['Q']
    z = data['z']
    y = data['y']
    I = data['I']
    J = data['J']
    Tid = data['Tid']
    timer_i = data['timer_i']
    T = data['T']
    aktive = data['aktive']
    hjem = {a['KomNr']: a['Hjemmekontor'] for a in aktive}

    total_timer = sum(timer_i.values())
    max_kartkontor = total_timer * T
    max_inertia = len(I)

    # Vektvalg: W1 > W2 * max_kartkontor + max_inertia; W2 > max_inertia
    W2 = max(10 * max_inertia, 1000) * w2_scale
    W1 = max(10 * (max(W2, 1) * max_kartkontor + max_inertia), 1e9)

    makespan_term = pulp.lpSum(Q[t] for t in Tid)
    kartkontor_term = pulp.lpSum(
        timer_i[i] * (1 - z[(i, t)]) for i in I for t in Tid
    )
    inertia_term = pulp.lpSum(
        (1 - y[(i, hjem[i])]) for i in I if hjem[i] in J
    )
    prob.setObjective(W1 * makespan_term + W2 * kartkontor_term + inertia_term)

    print(f'    Vektet objektiv (W1={W1:.0e}, W2={W2:.0e})')
    status, elapsed = solve_modell(prob, tidsgrense=tidsgrense, gap=gap, msg=msg)
    # Merk: endelig makespan hentes fra ekstraher_loesning (FIFO-rekonstruksjon
    # over z_it). Vi printer ikke en intermediær Q-sum her, fordi den kan avvike
    # fra FIFO-verdien i Not-Solved-tilfeller og skape forvirring mellom stdout
    # og CSV-output.
    print(f'    Ferdig ({elapsed:.1f}s, status {pulp.LpStatus[status]})')

    return {
        'status_1': status,
        'status_2': None,
        'tid_1': elapsed,
        'tid_2': 0,
    }


def fifo_nvdb_per_kommune(data):
    """Post-hoc: fordel NVDB-drenering per kommune via FIFO basert paa z_it.

    Gir per-kommune NVDB-ferdigmaaned som er konsistent med D_t-loesningen.
    Ferdige kommuner er i koeen fra t=0.
    """
    I = data['I']
    T = data['T']
    t0_nvdb = data['t0_nvdb']
    mu = data['mu']
    z = data['z']
    lenker_i = data['lenker_i']

    # Bygg kommune-liste i rekkefolge de blir tilgjengelig
    # Ferdige kommuner forst (kan dreneres fra t0_nvdb)
    kommuner_koe = []
    for f in data['ferdige']:
        kommuner_koe.append({
            'KomNr': f['KomNr'],
            'Lenker': f['Lenker'],
            'Ledig_Fra_Mnd': t0_nvdb,
            'Ferdig_Kartkontor_Mnd': 0,  # pre-ferdig
            'Gjenstaaende_Lenker': f['Lenker'],
        })

    # Aktive kommuner: tilgjengelig fra forste maaned z_it = 1
    for i in I:
        ferdig_mnd = None
        for t in range(T):
            v = pulp.value(z[(i, t)])
            if v is not None and v > 0.5:
                ferdig_mnd = t
                break
        if ferdig_mnd is None:
            # Ikke ferdig innen horisonten (vil normalt ikke skje)
            ferdig_mnd = T
        kommuner_koe.append({
            'KomNr': i,
            'Lenker': lenker_i[i],
            'Ledig_Fra_Mnd': max(ferdig_mnd, t0_nvdb),
            'Ferdig_Kartkontor_Mnd': ferdig_mnd,
            'Gjenstaaende_Lenker': lenker_i[i],
        })

    # Sorter FIFO: primaert etter Ledig_Fra_Mnd. Ved like maaneder tas stoerste
    # kommune foerst (negativ Lenker = storst foerst) slik at gjenstaaende
    # kapasitet fylles effektivt. KomNr som siste tie-breaker for determinisme.
    kommuner_koe.sort(key=lambda k: (k['Ledig_Fra_Mnd'], -k['Lenker'], k['KomNr']))

    # Drener mu per maaned
    ferdig_nvdb_mnd = {}
    for t in range(T):
        if t < t0_nvdb:
            continue
        kap = mu
        for k in kommuner_koe:
            if kap <= 1e-9:
                break
            if k['Gjenstaaende_Lenker'] <= 1e-9:
                continue
            if k['Ledig_Fra_Mnd'] > t:
                continue
            bruk = min(kap, k['Gjenstaaende_Lenker'])
            k['Gjenstaaende_Lenker'] -= bruk
            kap -= bruk
            if k['Gjenstaaende_Lenker'] <= 1e-9:
                ferdig_nvdb_mnd[k['KomNr']] = t
    return ferdig_nvdb_mnd


def ekstraher_loesning(prob, data):
    """Hent y_ij, z_it, D_t og bygg komplett tidsplan (kartkontor + NVDB).

    Pipeline sjekker om rapportert kartkontor-ferdigmnd er konsistent med en
    matematisk nedre grense (total_timer / total_kapasitet). Hvis solveren
    stoppet med Not Solved og returnerer LP-relax-verdier, kan z[(i,t)] ha
    fraksjoner som passerer 0.5-terskelen for enkelte kommuner og gi
    kunstig lave ferdigmaaneder. Upaalitelig-flagg settes naar dette skjer.
    """
    y, z, D, Q = data['y'], data['z'], data['D'], data['Q']
    I, J, T = data['I'], data['J'], data['T']

    # Assignment
    assignment = {}
    for i in I:
        for j in J:
            v = pulp.value(y[(i, j)])
            if v is not None and v > 0.5:
                assignment[i] = j
                break

    # Kartkontor-ferdigmaaned (forste t med z=1)
    ferdig_kk = {}
    for i in I:
        ferdig_kk[i] = None
        for t in range(T):
            v = pulp.value(z[(i, t)])
            if v is not None and v > 0.5:
                ferdig_kk[i] = t
                break

    # NVDB-drenering per maaned
    D_t = {t: (pulp.value(D[t]) or 0.0) for t in range(T)}

    # Per-kommune NVDB-ferdig via FIFO
    ferdig_nvdb = fifo_nvdb_per_kommune(data)

    # Makespan = siste NVDB-ferdigmaaned + 1 (0-indeksert til antall-maaneder)
    # Dette er robust for solver-status; Q-variabler kan ha None-verdier etter
    # lex-opt runde 2 hvis CBC forlot uten aa bevise optimalitet.
    ferdig_datoer = [v for v in ferdig_nvdb.values() if v is not None]
    if ferdig_datoer:
        makespan_mnd = max(ferdig_datoer) + 1
    else:
        makespan_mnd = T

    # Sanity: minimum kartkontor-maaneder ved full parallell utnyttelse.
    # Hvis rapportert max er under dette, har solveren returnert LP-relax
    # (z-fraksjoner), ikke en IP-feasible incumbent.
    status_str = pulp.LpStatus[prob.status]
    total_timer = sum(data['timer_i'].values())
    total_kap_mnd = sum(data['kap'].values())
    min_kk_mnd = total_timer / total_kap_mnd if total_kap_mnd > 0 else 0
    kk_maks = max(
        (v for v in ferdig_kk.values() if v is not None),
        default=None,
    )
    upaalitelig = False
    if status_str != 'Optimal' and kk_maks is not None:
        if kk_maks + 1 < min_kk_mnd * 0.9:
            upaalitelig = True
            print(
                f'  !! ADVARSEL: solver-status={status_str}, rapportert '
                f'kartkontor-maks={kk_maks+1} mnd < matematisk minimum '
                f'{min_kk_mnd:.1f} mnd. Tallene kommer fra LP-relaksjonen '
                f'og er ikke IP-feasible. Rapporter ikke som gyldig loesning.'
            )

    return {
        'scenario': data['scenario_navn'],
        'assignment': assignment,
        'ferdig_kk': ferdig_kk,
        'ferdig_nvdb': ferdig_nvdb,
        'D_t': D_t,
        'makespan_mnd': int(makespan_mnd),
        'objective': pulp.value(prob.objective),
        'status': status_str,
        'upaalitelig': upaalitelig,
        'min_kartkontor_mnd': round(min_kk_mnd, 1),
    }


def lagre_tidsplan(data, losning, mode='lex'):
    """Skriv tidsplan_mip_<mode>_<scenario>.csv med per-kommune ferdigdatoer."""
    rader = []
    # Aktive kommuner (med MIP-assignment)
    for a in data['aktive']:
        kn = a['KomNr']
        kk_mnd = losning['ferdig_kk'].get(kn)
        nv_mnd = losning['ferdig_nvdb'].get(kn)
        rader.append({
            'KomNr': kn,
            'Kommune': a['Kommune'],
            'Hjemmekontor': a['Hjemmekontor'],
            'Kartkontor_MIP': losning['assignment'].get(kn, ''),
            'Omfordelt': losning['assignment'].get(kn) != a['Hjemmekontor'],
            'Timer': round(a['Timer'], 2),
            'Lenker': a['Lenker'],
            'Ferdigdato_Kartkontor_Mnd': kk_mnd,
            'Ferdigdato_Kartkontor': maaned_til_dato(kk_mnd) if kk_mnd is not None else None,
            'Ferdigdato_NVDB_Mnd': nv_mnd,
            'Ferdigdato_NVDB': maaned_til_dato(nv_mnd) if nv_mnd is not None else None,
        })
    # Pre-ferdige kommuner (gar rett i NVDB)
    for f in data['ferdige']:
        kn = f['KomNr']
        nv_mnd = losning['ferdig_nvdb'].get(kn)
        rader.append({
            'KomNr': kn,
            'Kommune': f['Kommune'],
            'Hjemmekontor': f['Hjemmekontor'],
            'Kartkontor_MIP': f['Hjemmekontor'],  # uendret - var allerede ferdig
            'Omfordelt': False,
            'Timer': 0.0,
            'Lenker': f['Lenker'],
            'Ferdigdato_Kartkontor_Mnd': 0,
            'Ferdigdato_Kartkontor': STARTDATO,
            'Ferdigdato_NVDB_Mnd': nv_mnd,
            'Ferdigdato_NVDB': maaned_til_dato(nv_mnd) if nv_mnd is not None else None,
        })
    df = pd.DataFrame(rader)
    df.to_csv(
        os.path.join(DATA_DIR, f'tidsplan_mip_{mode}_{data["scenario_navn"]}.csv'),
        index=False,
    )
    return df


# --- Main -----------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default=None,
                        help='Kjor bare ett scenario (f.eks. Samferdsel_96)')
    parser.add_argument('--tidsgrense', type=int, default=SOLVER_TIDSGRENSE_SEK,
                        help=f'Solver-tidsgrense i sekunder (default {SOLVER_TIDSGRENSE_SEK})')
    parser.add_argument('--mode', choices=['makespan', 'lex', 'vektet'], default='vektet',
                        help='makespan: bare min makespan. lex: sekvensiell lex-opt '
                             '(2 solver-runder). vektet: en-pass kombinert objektiv '
                             '(BIG*makespan + kartkontor). Default vektet (raskere).')
    parser.add_argument('--w2-scale', type=float, default=1.0,
                        help='Multiplikator paa W2 (kartkontor-ferdigtid-vekt) i vektet-modus. '
                             'Verdi < 1 gir mer vekt til inertia og faerre omfordelinger. Default 1.0.')
    parser.add_argument('--msg', action='store_true',
                        help='Vis CBC solver-output (gap, bestBound, osv.)')
    args = parser.parse_args()

    kommuner, kontorer, geovekst, nvdb = last_data()
    if args.scenario:
        nvdb = nvdb[nvdb['Scenario'] == args.scenario].reset_index(drop=True)
        if len(nvdb) == 0:
            print(f'FEIL: scenario "{args.scenario}" finnes ikke')
            sys.exit(1)

    print('=' * 60)
    print('MIP-MODELL FOR TVS-ALLOKERING')
    print('=' * 60)
    print(f'Kommuner: {len(kommuner)} ({(kommuner["Status"] == "Ferdig").sum()} pre-ferdige)')
    print(f'Kontor: {len(kontorer)}')
    print(f'Geovekst-prosjekter: {len(geovekst)}')
    print(f'Scenarioer: {len(nvdb)}')

    oppsummering = []
    sammenligning = []

    # Last heuristikk-oppsummering for sammenligning
    heur_df = pd.read_csv(os.path.join(DATA_DIR, 'oppsummering_scenarioer.csv'))
    heur_map = {r['Scenario']: r for _, r in heur_df.iterrows()}

    for _, scenario in nvdb.iterrows():
        navn = scenario['Scenario']
        T = T_MAX[navn]
        print(f'\n{"=" * 60}')
        print(f'Scenario: {navn} (horisont T = {T} maaneder)')
        print('=' * 60)

        prob, data = bygg_modell(scenario, kommuner, kontorer, geovekst)

        n_I = len(data['I'])
        n_J = len(data['J'])
        n_var = prob.numVariables()
        n_con = prob.numConstraints()
        print(f'  Aktive kommuner: {n_I}')
        print(f'  Kontor: {n_J}')
        print(f'  Tidssteg: {data["T"]}')
        print(f'  NVDB-kapasitet: {data["mu"]:.0f} lenker/mnd')
        print(f'  Totale lenker (NVDB): {data["total_lenker"]:.0f}')
        print(f'  Variabler: {n_var}')
        print(f'  Bibindelser: {n_con}')

        if args.mode == 'lex':
            lex = solve_lex_opt(prob, data, tidsgrense=args.tidsgrense, msg=args.msg)
            total_elapsed = lex['tid_1'] + lex['tid_2']
            print(f'  Solver-tid total: {total_elapsed:.1f}s '
                  f'(R1 {lex["tid_1"]:.1f}s, R2 {lex["tid_2"]:.1f}s)')
            status_str = f'{pulp.LpStatus[lex["status_1"]]} / {pulp.LpStatus[lex["status_2"]]}'
        elif args.mode == 'vektet':
            res = solve_vektet(prob, data, tidsgrense=args.tidsgrense, msg=args.msg,
                               w2_scale=args.w2_scale)
            total_elapsed = res['tid_1']
            print(f'  Solver-tid: {total_elapsed:.1f}s')
            status_str = pulp.LpStatus[res['status_1']]
        else:
            status, total_elapsed = solve_modell(prob, tidsgrense=args.tidsgrense, msg=args.msg)
            print(f'  Solver-tid: {total_elapsed:.1f}s')
            status_str = pulp.LpStatus[status]

        losning = ekstraher_loesning(prob, data)
        print(f'  Status: {status_str}')
        print(f'  Makespan (mnd): {losning["makespan_mnd"]}')
        print(f'  Makespan (aar): {losning["makespan_mnd"] / 12:.2f}')
        n_reassigned = sum(
            1 for a in data['aktive']
            if losning['assignment'].get(a['KomNr']) != a['Hjemmekontor']
        )
        kk_maks_mnd = max(
            (v for v in losning['ferdig_kk'].values() if v is not None),
            default=None,
        )
        kk_median_mnd = (
            pd.Series([v for v in losning['ferdig_kk'].values() if v is not None]).median()
            if losning['ferdig_kk'] else None
        )
        print(f'  Kommuner omfordelt: {n_reassigned}/{n_I}')
        print(f'  Kartkontor-ferdig: max={kk_maks_mnd} mnd, median={kk_median_mnd} mnd')

        lagre_tidsplan(data, losning, mode=args.mode)

        oppsummering.append({
            'Scenario': navn,
            'Mode': args.mode,
            'Status': status_str,
            'Upaalitelig': losning.get('upaalitelig', False),
            'Min_Kartkontor_Mnd': losning.get('min_kartkontor_mnd'),
            'Makespan_Mnd': losning['makespan_mnd'],
            'Makespan_Aar': round(losning['makespan_mnd'] / 12, 2),
            'Kartkontor_Maks_Mnd': kk_maks_mnd,
            'Kartkontor_Median_Mnd': kk_median_mnd,
            'Kommuner_Omfordelt': n_reassigned,
            'Aktive_Kommuner': n_I,
            'Solver_Tid_Sek': round(total_elapsed, 1),
            'Variabler': n_var,
            'Bibindelser': n_con,
        })

        # Sammenligning med heuristikk
        heur = heur_map[navn]
        heur_aar = heur['Varighet_Aar']
        mip_aar = round(losning['makespan_mnd'] / 12, 2)
        forbedring_pst = round(100 * (heur_aar - mip_aar) / heur_aar, 1) if heur_aar else 0.0
        sammenligning.append({
            'Scenario': navn,
            'Varighet_Heuristikk_Aar': heur_aar,
            'Varighet_MIP_Aar': mip_aar,
            'Forbedring_Aar': round(heur_aar - mip_aar, 2),
            'Forbedring_Pst': forbedring_pst,
            'Kommuner_Omfordelt': n_reassigned,
        })

    suffiks = '' if args.w2_scale == 1.0 else f'_w2-{args.w2_scale}'
    pd.DataFrame(oppsummering).to_csv(
        os.path.join(DATA_DIR, f'oppsummering_mip_{args.mode}{suffiks}.csv'), index=False
    )
    pd.DataFrame(sammenligning).to_csv(
        os.path.join(DATA_DIR, f'sammenligning_heuristikk_mip_{args.mode}{suffiks}.csv'), index=False
    )

    print(f'\n{"=" * 60}')
    print('Sammendrag')
    print('=' * 60)
    print(pd.DataFrame(sammenligning).to_string(index=False))
    print(f'\nOutput lagret i {DATA_DIR}')


if __name__ == '__main__':
    main()
