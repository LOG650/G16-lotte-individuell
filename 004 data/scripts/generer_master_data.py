import pandas as pd
import os
import warnings

# Skjul advarsler om åpen fil
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# 1. Stier
raw_dir = '004 data/raw_data'
proc_dir = '004 data/processed_data'

def build_master_dataset():
    print("--- Starter generering av master-datasett ---")

    # A. Kobling (Nummer <-> Navn)
    print("Leser statistikk-fil for kommune-mapping...")
    df_map_raw = pd.read_excel(os.path.join(raw_dir, '20250903StatistikkTraktorvegSti.xlsx'), sheet_name='Data')
    df_base = df_map_raw[['komm', 'kommunenavn']].copy()
    # Sikre at komm er rent heltall før tekstkonvertering
    df_base['komm'] = pd.to_numeric(df_base['komm'], errors='coerce').fillna(0).astype(int).astype(str).str.zfill(4)
    df_base['kommunenavn'] = df_base['kommunenavn'].str.strip()

    # B. Arbeidsmengde (Antall objekter per kommune.csv)
    print("Leser arbeidsmengde (Antall objekter)...")
    df_objects = pd.read_csv(os.path.join(raw_dir, 'Antall objekter per kommune.csv'))
    df_objects['Kommmune navn'] = df_objects['Kommmune navn'].str.strip()

    # C. Fremdriftsdata (data.csv)
    print("Leser fremdriftsdata (data.csv)...")
    df_status = pd.read_csv(os.path.join(raw_dir, 'data.csv'), dtype={'KomNr': str})
    # Sikre at KomNr er renset (håndterer "301" -> "0301")
    df_status['KomNr'] = pd.to_numeric(df_status['KomNr'], errors='coerce').fillna(0).astype(int).astype(str).str.zfill(4)
    df_status['%'] = pd.to_numeric(df_status['%'], errors='coerce').fillna(0)
    
    # D. Kartkontor (fra Datainnsamling-fila)
    print("Mapper kommuner til kartkontor...")
    xl_kontor = pd.ExcelFile(os.path.join(raw_dir, 'Datainnsamling_TraktorvegSti (1).xlsx'))
    kontor_mapping = []

    for sheet in xl_kontor.sheet_names:
        if sheet in ['Ark1', 'pivot', 'Oslo']: # Oslo-arket har litt annen struktur, håndterer det spesielt hvis trengs
             pass
        
        df_sheet = pd.read_excel(xl_kontor, sheet_name=sheet)
        if not df_sheet.empty:
            rader = df_sheet.iloc[:, 0].dropna().astype(str).tolist()
            for rad in rader:
                navn = rad.replace('DATAINNSAMLING:', '').strip()
                if navn and len(navn) > 2 and "Totalt" not in navn:
                    kontor_mapping.append({'Kommune': navn, 'Kartkontor': sheet})

    df_kontorer = pd.DataFrame(kontor_mapping).drop_duplicates(subset=['Kommune'])

    # E. Slå sammen alt (Merge)
    print("Slår sammen kilder...")
    # 1. Koble nr/navn med status
    master = pd.merge(df_base, df_status[['KomNr', '%', 'Status']], left_on='komm', right_on='KomNr', how='left')
    # 2. Legg til objekter basert på navn
    master = pd.merge(master, df_objects, left_on='kommunenavn', right_on='Kommmune navn', how='left')
    # 3. Legg til kartkontor basert på navn
    master = pd.merge(master, df_kontorer, left_on='kommunenavn', right_on='Kommune', how='left')

    # F. Beregninger
    master['Gjenværende_Arbeid'] = master['sum objekter'] * (1 - (master['%'] / 100))
    
    # Rydd kolonner
    master = master[['komm', 'kommunenavn', 'Kartkontor', 'Status', '%', 'sum objekter', 'Gjenværende_Arbeid']]
    master.columns = ['KomNr', 'Kommune', 'Kartkontor', 'Status', 'Fremdrift_Prosent', 'Total_Arbeidsmengde', 'Gjenværende_Arbeid']

    # F. Lagre
    output_path = os.path.join(proc_dir, 'master_analyse.csv')
    master.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\nFERDIG! Master-fil er opprettet: {output_path}")
    print(f"Totalt antall kommuner i fila: {len(master)}")

if __name__ == "__main__":
    build_master_dataset()
