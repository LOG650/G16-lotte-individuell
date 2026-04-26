"""
Datavask og strukturering for TraktorvegSti-prosjektet.
Produserer tre rene datasett fra rådata:
  1. master_kommuner.csv    - en rad per kommune med all relevant info
  2. kapasitet_kontorer.csv - en rad per kartkontor med kapasitet og arbeidsmengde
  3. geovekst_prosjekter.csv - en rad per kommune-prosjekt-kombinasjon
"""

import pandas as pd
import numpy as np
import os
import sys
import io
import warnings
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# --- Stier ---
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
RAW_DIR = os.path.join(BASE_DIR, 'raw_data')
OUT_DIR = os.path.join(BASE_DIR, 'processed_data')
os.makedirs(OUT_DIR, exist_ok=True)

# --- Mappinger ---
FYLKE_NAVN = {
    3: 'Oslo', 11: 'Rogaland', 15: 'Møre og Romsdal', 18: 'Nordland',
    31: 'Østfold', 32: 'Akershus', 33: 'Buskerud', 34: 'Innlandet',
    39: 'Vestfold', 40: 'Telemark', 42: 'Agder', 46: 'Vestland',
    50: 'Trøndelag', 55: 'Troms', 56: 'Finnmark',
}

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

MAANED_NR = {
    'januar': 1, 'februar': 2, 'mars': 3, 'april': 4, 'mai': 5, 'juni': 6,
    'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'okt': 10,
    'november': 11, 'desember': 12,
}

SISTE_DAG = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
             7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def parse_laaseperiode(tekst):
    """Konverterer låseperiode-tekst til (start_dato, slutt_dato)."""
    if pd.isna(tekst) or str(tekst).strip() == '':
        return pd.NaT, pd.NaT

    tekst = str(tekst).strip().lower()

    # Ren tallverdi (antall måneder, f.eks. "7") -> mai-desember 2026
    if re.match(r'^\d+$', tekst):
        return pd.Timestamp('2026-05-01'), pd.Timestamp('2026-12-31')

    # Eksplisitt årstall: "august 2026 - mars 2027"
    m = re.match(r'(\w+)\s+(\d{4})\s*[-–]\s*(\w+)\s+(\d{4})', tekst)
    if m:
        start_mnd = MAANED_NR.get(m.group(1))
        start_aar = int(m.group(2))
        slutt_mnd = MAANED_NR.get(m.group(3))
        slutt_aar = int(m.group(4))
        if start_mnd and slutt_mnd:
            return (pd.Timestamp(start_aar, start_mnd, 1),
                    pd.Timestamp(slutt_aar, slutt_mnd, SISTE_DAG[slutt_mnd]))

    # "juni/juli - november" -> ta første måned
    tekst_renset = re.sub(r'/\w+', '', tekst)

    # "mnd - mnd" eller "mnd-mnd"
    m = re.match(r'(\w+)\s*[-–]\s*(\w+)', tekst_renset)
    if m:
        start_mnd = MAANED_NR.get(m.group(1).strip())
        slutt_mnd = MAANED_NR.get(m.group(2).strip())
        if start_mnd and slutt_mnd:
            start_aar = 2026
            slutt_aar = 2027 if slutt_mnd < start_mnd else 2026
            return (pd.Timestamp(start_aar, start_mnd, 1),
                    pd.Timestamp(slutt_aar, slutt_mnd, SISTE_DAG[slutt_mnd]))

    print(f"  ADVARSEL: Kunne ikke parse låseperiode: '{tekst}'")
    return pd.NaT, pd.NaT


def les_base():
    """Leser StatistikkTraktorvegSti som base. Ignorerer feil fylkesnr/fylkesnavn.
    Bevarer arealLand som brukes til dokumentasjon av Ber_Tidbruk_Min-formelen."""
    print("1. Leser StatistikkTraktorvegSti (base)...")
    df = pd.read_excel(os.path.join(RAW_DIR, '20250903StatistikkTraktorvegSti.xlsx'),
                       sheet_name='Data')
    df = df.dropna(subset=['komm'])
    df['KomNr'] = df['komm'].astype(int).astype(str).str.zfill(4)
    df['Fylkesnr'] = df['komm'].astype(int) // 100
    df['Fylke'] = df['Fylkesnr'].map(FYLKE_NAVN)
    df['Kartkontor'] = df['Fylkesnr'].map(FYLKE_TIL_KONTOR)

    base = df[['KomNr', 'kommunenavn', 'Fylkesnr', 'Fylke', 'Kartkontor',
               'km_kurve', 'arealLand', 'Ber_tidbruk_minutter', 'Dagsverk']].copy()
    base.columns = ['KomNr', 'Kommune', 'Fylkesnr', 'Fylke', 'Kartkontor',
                    'Km_Kurve', 'ArealLand_Km2', 'Ber_Tidbruk_Min', 'Ber_Dagsverk']
    base['Kommune'] = base['Kommune'].str.strip()
    print(f"   {len(base)} kommuner lastet")
    return base


def les_tidbruk_kalibrering():
    """Leser Tidbruk-fanen i StatistikkTraktorvegSti.

    Inneholder 58 kartblader med faktisk malt tidsbruk (MIN) og utledede verdier
    MIN/KM og MIN/KM2. Brukes som empirisk kalibreringsgrunnlag for formelen:
        Ber_Tidbruk_Min = Km_Kurve * 0.9035 + ArealLand_Km2 * 0.6510

    De to konstantene leses ogsaa ut fra fanen (i kolonne 9-10 paa rad 1 og 2).
    """
    print("1b. Leser Tidbruk-kalibrering...")
    path = os.path.join(RAW_DIR, '20250903StatistikkTraktorvegSti.xlsx')

    df = pd.read_excel(path, sheet_name='Tidbruk', header=0)

    # Hent konstantene fra kolonne 9 og 10 (de to siste kolonnene i raad 1-2)
    label_kol = df.columns[-2]
    verdi_kol = df.columns[-1]
    konst_navn_1 = str(label_kol).strip()
    konst_verdi_1 = float(verdi_kol)
    konst_navn_2 = str(df.iloc[0, -2]).strip()
    konst_verdi_2 = float(df.iloc[0, -1])

    konstanter = pd.DataFrame([
        {'Konstant': 'Gjennomsnitt_Min_Per_Km', 'Verdi': round(konst_verdi_1, 6),
         'Enhet': 'min/km',
         'Beskrivelse': ('Empirisk gjennomsnittlig tidsbruk per km TVS-lenke, '
                         'utledet fra 58 kartblader. Kilde: fanen "Tidbruk" i StatistikkTraktorvegSti')},
        {'Konstant': 'Grunnpakke_Min_Per_Km2', 'Verdi': round(konst_verdi_2, 6),
         'Enhet': 'min/km2',
         'Beskrivelse': ('Grunnpakke-tillegg for landareal. '
                         'Brukes sammen med Gjennomsnitt_Min_Per_Km i formelen for Ber_Tidbruk_Min')},
    ])

    # Lag kalibreringsdatasett
    kalibrering = df.iloc[:, :8].copy()
    kalibrering.columns = ['Kartblad', 'Objekttype', 'Minutter', 'Lengde_M',
                           'Lengde_Km', 'Min_Per_Km', 'Min_Per_Km2', 'Region']
    kalibrering = kalibrering.dropna(subset=['Kartblad'])
    print(f"   {len(kalibrering)} kartblader, 2 konstanter ({konst_navn_1}, {konst_navn_2})")
    return kalibrering, konstanter


def les_fremdrift():
    """Leser fremdriftsstatus fra data.csv."""
    print("2. Leser fremdriftsstatus (data.csv)...")
    df = pd.read_csv(os.path.join(RAW_DIR, 'data.csv'), dtype={'KomNr': str})
    df['KomNr'] = pd.to_numeric(df['KomNr'], errors='coerce').fillna(0).astype(int).astype(str).str.zfill(4)
    df['%'] = pd.to_numeric(df['%'], errors='coerce').fillna(0)
    result = df[['KomNr', 'Status', '%']].copy()
    result.columns = ['KomNr', 'Status', 'Fremdrift_Prosent']
    print(f"   {len(result)} rader: {result['Status'].value_counts().to_dict()}")
    return result


def les_arbeidsmengde():
    """Leser antall lenker per kommune."""
    print("3. Leser arbeidsmengde (Antall objekter per kommune.csv)...")
    df = pd.read_csv(os.path.join(RAW_DIR, 'Antall objekter per kommune.csv'))
    df.columns = ['Kommune', 'Antall_Lenker']
    df['Kommune'] = df['Kommune'].str.strip()
    print(f"   {len(df)} kommuner med lenkedata")
    return df


def les_geovekst_datainnsamling():
    """Parser Geovekst-prosjekter fra Datainnsamling-fila."""
    print("4. Leser Geovekst fra Datainnsamling...")
    xl = pd.ExcelFile(os.path.join(RAW_DIR, 'Datainnsamling_TraktorvegSti.xlsx'))
    geovekst_rader = []

    for sheet in xl.sheet_names:
        if sheet == 'Ark1':
            continue
        df = pd.read_excel(xl, sheet_name=sheet)
        if len(df) < 8:
            continue

        # Finn rader med kommunedata (rad 8+, der kolonne 0 har kommunenr)
        for i in range(8, len(df)):
            row = df.iloc[i]
            komm_nr = row.iloc[0]
            if pd.isna(komm_nr):
                continue
            try:
                komm_nr = int(float(komm_nr))
            except (ValueError, TypeError):
                continue

            prosjektnr = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            status = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
            periode = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''

            if prosjektnr and prosjektnr != 'nan':
                geovekst_rader.append({
                    'Prosjektnr': prosjektnr,
                    'KomNr': str(komm_nr).zfill(4),
                    'Kartkontor': sheet,
                    'Prosjektstatus': status.capitalize(),
                    'Laaseperiode_Tekst': periode,
                })

    print(f"   {len(geovekst_rader)} kommune-prosjekt-par fra Datainnsamling")
    return pd.DataFrame(geovekst_rader)


def les_geovekst_csv(filnavn, prosjekt_mapping, kartkontor):
    """Parser en Geovekst CSV-fil (semikolon-separert, ustrukturert format).
    Returnerer liste med (prosjektnr, kommunenavn) tupler."""
    print(f"   Leser {filnavn}...")
    filepath = os.path.join(RAW_DIR, filnavn)
    rader = []
    current_prosjekt = None

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(';')]
            parts = [p for p in parts if p]

            if not parts:
                current_prosjekt = None
                continue

            # Sjekk om linjen starter med prosjektkode (LACI...)
            if parts[0].startswith('LACI'):
                current_prosjekt = parts[0]
                # Sjekk om det er kommunenavn på samme linje
                for p in parts[1:]:
                    if (not p.startswith('FKB') and len(p) > 2
                            and 'flyvning' not in p.lower()
                            and 'omløp' not in p.lower()):
                        rader.append({'Prosjektnr': current_prosjekt, 'Kommune': p})
            elif current_prosjekt:
                for p in parts:
                    if (len(p) > 2 and not p.startswith('FKB')
                            and 'flyvning' not in p.lower()
                            and 'omløp' not in p.lower()):
                        rader.append({'Prosjektnr': current_prosjekt, 'Kommune': p})

    df = pd.DataFrame(rader)
    if not df.empty:
        df['Kartkontor'] = kartkontor
        df['Prosjektstatus'] = 'Planlagt'
        df['Laaseperiode_Tekst'] = 'mai-desember'  # 7 mnd, mai-desember 2026
    print(f"   {len(df)} kommune-prosjekt-par fra {filnavn}")
    return df


KAPASITET_OVERRIDE = {
    'Oslo': {'Kapasitet_Ukesverk': 30, 'Min_Tidsbruk_Timer': 30, 'Max_Tidsbruk_Timer': 90},
}


def les_kapasitet():
    """Leser kapasitetsdata fra Datainnsamling-fila."""
    print("5. Leser kapasitetsdata...")
    xl = pd.ExcelFile(os.path.join(RAW_DIR, 'Datainnsamling_TraktorvegSti.xlsx'))
    kap_rader = []

    for sheet in xl.sheet_names:
        if sheet == 'Ark1':
            continue
        df = pd.read_excel(xl, sheet_name=sheet)
        if len(df) < 5:
            continue

        kapasitet = pd.to_numeric(df.iloc[2, 2], errors='coerce')
        min_tid = pd.to_numeric(df.iloc[3, 2], errors='coerce')
        max_tid = pd.to_numeric(df.iloc[4, 2], errors='coerce')

        if sheet in KAPASITET_OVERRIDE:
            override = KAPASITET_OVERRIDE[sheet]
            kapasitet = override.get('Kapasitet_Ukesverk', kapasitet)
            min_tid = override.get('Min_Tidsbruk_Timer', min_tid)
            max_tid = override.get('Max_Tidsbruk_Timer', max_tid)

        kap_rader.append({
            'Kartkontor': sheet,
            'Kapasitet_Ukesverk': kapasitet,
            'Min_Tidsbruk_Timer': min_tid,
            'Max_Tidsbruk_Timer': max_tid,
        })

    return pd.DataFrame(kap_rader)


def bygg_master():
    """Bygger master_kommuner.csv."""
    # 1. Base
    master = les_base()

    # 2. Fremdrift
    fremdrift = les_fremdrift()
    master = master.merge(fremdrift, on='KomNr', how='left')
    master['Status'] = master['Status'].fillna('Ikke påbegynt')
    master['Fremdrift_Prosent'] = master['Fremdrift_Prosent'].fillna(0)

    # 3. Arbeidsmengde - match på kommunenavn, med fuzzy for samisk/doble navn
    arbeid = les_arbeidsmengde()
    master = master.merge(arbeid, on='Kommune', how='left')

    # Fyll inn manglende via første del av kommunenavn (før " - ")
    mangler = master['Antall_Lenker'].isna()
    if mangler.any():
        arbeid_kort = arbeid.copy()
        arbeid_kort['Kommune_kort'] = arbeid_kort['Kommune'].str.split(' - ').str[0].str.strip()
        master.loc[mangler, 'Kommune_kort'] = master.loc[mangler, 'Kommune'].str.split(' - ').str[0].str.strip()
        for idx in master[mangler].index:
            kort = master.at[idx, 'Kommune_kort']
            match = arbeid_kort[arbeid_kort['Kommune_kort'] == kort]
            if len(match) == 0:
                # Prøv andre delen av navnet
                deler = master.at[idx, 'Kommune'].split(' - ')
                for del_navn in deler:
                    match = arbeid_kort[arbeid_kort['Kommune_kort'] == del_navn.strip()]
                    if len(match) > 0:
                        break
            if len(match) > 0:
                master.at[idx, 'Antall_Lenker'] = match.iloc[0]['Antall_Lenker']
        if 'Kommune_kort' in master.columns:
            master.drop(columns=['Kommune_kort'], inplace=True)

    # 4. Gjenstående lenker
    master['Gjenstaaende_Lenker'] = (
        master['Antall_Lenker'] * (1 - master['Fremdrift_Prosent'] / 100)
    ).round(0)

    # 5. Geovekst - fra Datainnsamling
    geovekst_di = les_geovekst_datainnsamling()

    # 6. Geovekst - suppler fra CSV-er
    print("4b. Supplerer Geovekst fra CSV-er...")
    geovekst_agder = les_geovekst_csv('Agder_prosjekter.csv', {}, 'Kristiansand')
    geovekst_rogaland = les_geovekst_csv('Rogaland_prosjekter.csv', {}, 'Stavanger')

    # Map kommunenavn til kommunenr for CSV-data
    navn_til_nr = dict(zip(master['Kommune'], master['KomNr']))
    for gv_csv in [geovekst_agder, geovekst_rogaland]:
        if gv_csv.empty:
            continue
        gv_csv['KomNr'] = gv_csv['Kommune'].map(navn_til_nr)
        mangler = gv_csv[gv_csv['KomNr'].isna()]['Kommune'].unique()
        if len(mangler) > 0:
            print(f"   ADVARSEL: Fant ikke kommunenr for: {list(mangler)}")

    # Kombiner alle Geovekst-data
    alle_geovekst_dfs = [geovekst_di]
    for gv_csv in [geovekst_agder, geovekst_rogaland]:
        if gv_csv.empty:
            continue
        gv_csv_clean = gv_csv[gv_csv['KomNr'].notna()][
            ['Prosjektnr', 'KomNr', 'Kartkontor', 'Prosjektstatus', 'Laaseperiode_Tekst']
        ].copy()
        # Fjern duplikater mot Datainnsamling (sjekk KomNr + Prosjektnr)
        if not geovekst_di.empty:
            eksisterende = set(zip(geovekst_di['KomNr'], geovekst_di['Prosjektnr']))
            mask = gv_csv_clean.apply(
                lambda r: (r['KomNr'], r['Prosjektnr']) not in eksisterende, axis=1
            )
            gv_csv_clean = gv_csv_clean[mask]
        alle_geovekst_dfs.append(gv_csv_clean)

    alle_geovekst = pd.concat(alle_geovekst_dfs, ignore_index=True)

    # Parse låseperioder
    alle_geovekst[['Laaseperiode_Start', 'Laaseperiode_Slutt']] = alle_geovekst[
        'Laaseperiode_Tekst'
    ].apply(lambda x: pd.Series(parse_laaseperiode(x)))

    # Valider: Start <= Slutt. En periode med Start > Slutt blir tolket som
    # "ingen lås" av heuristikk (er_laast returnerer False) og MIP (tom range),
    # som kan skjule en aktiv lås hvis det skyldes en typo i rådata.
    # Eks: LACIVL03 (4641 Aurland, 4643 Årdal) har "juni 2025 - mars 2006" i
    # rådata, sannsynligvis typo for "mars 2026". Den utløpte tolkningen er
    # plausibel her, men skal flagges eksplisitt for fremtidige tilfeller.
    feil_periode = alle_geovekst[
        alle_geovekst['Laaseperiode_Start'].notna()
        & alle_geovekst['Laaseperiode_Slutt'].notna()
        & (alle_geovekst['Laaseperiode_Start'] > alle_geovekst['Laaseperiode_Slutt'])
    ]
    if not feil_periode.empty:
        print(f"\n  ADVARSEL: {len(feil_periode)} geovekst-rader har "
              f"Laaseperiode_Start > Laaseperiode_Slutt. Disse blir tolket "
              f"som 'ingen lås' av heuristikk og MIP. Sjekk rådata for typo.")
        for _, r in feil_periode.iterrows():
            print(f"    {r['Prosjektnr']} kommune {r['KomNr']}: "
                  f"'{r['Laaseperiode_Tekst']}' -> "
                  f"{r['Laaseperiode_Start'].date()} til {r['Laaseperiode_Slutt'].date()}")

    # Aggreger Geovekst per kommune for master
    if not alle_geovekst.empty:
        gv_agg = alle_geovekst.groupby('KomNr').agg(
            Geovekst_Prosjekter=('Prosjektnr', lambda x: ','.join(sorted(set(x)))),
            Geovekst_Status=('Prosjektstatus', lambda x: ','.join(sorted(set(x)))),
        ).reset_index()
        gv_agg['Er_Laast'] = True
        master = master.merge(gv_agg, on='KomNr', how='left')
    else:
        master['Geovekst_Prosjekter'] = ''
        master['Geovekst_Status'] = ''
        master['Er_Laast'] = False

    master['Er_Laast'] = master['Er_Laast'].fillna(False)
    master['Geovekst_Prosjekter'] = master['Geovekst_Prosjekter'].fillna('')
    master['Geovekst_Status'] = master['Geovekst_Status'].fillna('')

    return master, alle_geovekst


def bygg_kapasitet(master):
    """Bygger kapasitet_kontorer.csv."""
    print("6. Bygger kapasitetstabell...")
    kap = les_kapasitet()

    # Beregn per kontor fra master
    kontor_stats = master.groupby('Kartkontor').agg(
        Antall_Kommuner=('KomNr', 'count'),
        Total_Lenker=('Antall_Lenker', 'sum'),
        Gjenstaaende_Lenker=('Gjenstaaende_Lenker', 'sum'),
    ).reset_index()

    kap = kap.merge(kontor_stats, on='Kartkontor', how='left')
    return kap


def bygg_geovekst(alle_geovekst, master):
    """Bygger geovekst_prosjekter.csv."""
    print("7. Bygger Geovekst-prosjekttabell...")
    nr_til_navn = dict(zip(master['KomNr'], master['Kommune']))
    alle_geovekst['Kommune'] = alle_geovekst['KomNr'].map(nr_til_navn)

    output = alle_geovekst[[
        'Prosjektnr', 'KomNr', 'Kommune', 'Kartkontor',
        'Prosjektstatus', 'Laaseperiode_Start', 'Laaseperiode_Slutt'
    ]].copy()
    return output


def valider(master, kapasitet, geovekst):
    """Validerer output og printer sammendrag."""
    print("\n=== VALIDERING ===")
    print(f"Master: {len(master)} kommuner")
    print(f"Kapasitet: {len(kapasitet)} kontorer")
    print(f"Geovekst: {len(geovekst)} kommune-prosjekt-par")

    # Manglende data
    mangler_kontor = master[master['Kartkontor'].isna()]
    if len(mangler_kontor) > 0:
        print(f"\nADVARSEL: {len(mangler_kontor)} kommuner mangler kartkontor:")
        print(f"  {mangler_kontor[['KomNr', 'Kommune']].to_string(index=False)}")

    mangler_lenker = master[master['Antall_Lenker'].isna()]
    if len(mangler_lenker) > 0:
        print(f"\nADVARSEL: {len(mangler_lenker)} kommuner mangler lenkedata:")
        for _, r in mangler_lenker.iterrows():
            print(f"  {r['KomNr']} {r['Kommune']}")

    # Sammendrag per kontor
    print("\n--- Sammendrag per kartkontor ---")
    print(f"{'Kontor':<15} {'Kommuner':>8} {'Lenker':>10} {'Gjenstående':>12} {'Låst':>6}")
    print("-" * 55)
    for _, row in kapasitet.sort_values('Kartkontor').iterrows():
        kontor = row['Kartkontor']
        laast = master[(master['Kartkontor'] == kontor) & (master['Er_Laast'] == True)]
        print(f"{kontor:<15} {int(row.get('Antall_Kommuner', 0)):>8} "
              f"{int(row.get('Total_Lenker', 0)):>10} "
              f"{int(row.get('Gjenstaaende_Lenker', 0)):>12} "
              f"{len(laast):>6}")

    totalt = master['Antall_Lenker'].sum()
    gjenstaaende = master['Gjenstaaende_Lenker'].sum()
    print("-" * 55)
    print(f"{'TOTALT':<15} {len(master):>8} {int(totalt):>10} {int(gjenstaaende):>12} "
          f"{len(master[master['Er_Laast'] == True]):>6}")

    # Status-fordeling
    print(f"\n--- Status ---")
    print(master['Status'].value_counts().to_string())

    # Spot-sjekk
    print(f"\n--- Spot-sjekk ---")
    for komm in ['0301', '4601', '5001']:
        r = master[master['KomNr'] == komm]
        if len(r) > 0:
            r = r.iloc[0]
            print(f"  {r['Kommune']} ({komm}): kontor={r['Kartkontor']}, "
                  f"lenker={r.get('Antall_Lenker', 'N/A')}, "
                  f"status={r['Status']}, låst={r['Er_Laast']}")


def valider_tidbruk_formel(master, konstanter):
    """Verifiserer at Ber_Tidbruk_Min = Km_Kurve * konst1 + ArealLand_Km2 * konst2."""
    k1 = konstanter.loc[konstanter['Konstant'] == 'Gjennomsnitt_Min_Per_Km', 'Verdi'].iloc[0]
    k2 = konstanter.loc[konstanter['Konstant'] == 'Grunnpakke_Min_Per_Km2', 'Verdi'].iloc[0]
    beregnet = master['Km_Kurve'] * k1 + master['ArealLand_Km2'] * k2
    avvik = (beregnet - master['Ber_Tidbruk_Min']).abs()
    print(f"\n--- Verifisering av Ber_Tidbruk_Min-formel ---")
    print(f"  Formel: Ber_Tidbruk_Min = Km_Kurve * {k1} + ArealLand_Km2 * {k2}")
    print(f"  Maks avvik fra oppgitt verdi: {avvik.max():.2f} min")
    print(f"  Median avvik: {avvik.median():.2f} min")
    if avvik.max() > 5:
        print(f"  ADVARSEL: Stort avvik - formelen er kanskje unoyaktig")


def main():
    print("=" * 60)
    print("DATAVASK OG STRUKTURERING - TraktorvegSti")
    print("=" * 60)

    master, alle_geovekst = bygg_master()
    kapasitet = bygg_kapasitet(master)
    geovekst = bygg_geovekst(alle_geovekst, master)
    tidbruk_kal, tidbruk_konst = les_tidbruk_kalibrering()

    # Lagre
    master_path = os.path.join(OUT_DIR, 'master_kommuner.csv')
    kap_path = os.path.join(OUT_DIR, 'kapasitet_kontorer.csv')
    gv_path = os.path.join(OUT_DIR, 'geovekst_prosjekter.csv')
    tb_kal_path = os.path.join(OUT_DIR, 'tidbruk_kalibrering.csv')
    tb_konst_path = os.path.join(OUT_DIR, 'tidbruk_konstanter.csv')

    master.to_csv(master_path, index=False, encoding='utf-8-sig')
    kapasitet.to_csv(kap_path, index=False, encoding='utf-8-sig')
    geovekst.to_csv(gv_path, index=False, encoding='utf-8-sig')
    tidbruk_kal.to_csv(tb_kal_path, index=False, encoding='utf-8-sig')
    tidbruk_konst.to_csv(tb_konst_path, index=False, encoding='utf-8-sig')

    print(f"\nFiler lagret:")
    print(f"  {master_path}")
    print(f"  {kap_path}")
    print(f"  {gv_path}")
    print(f"  {tb_kal_path}")
    print(f"  {tb_konst_path}")

    valider(master, kapasitet, geovekst)
    valider_tidbruk_formel(master, tidbruk_konst)


if __name__ == '__main__':
    main()
