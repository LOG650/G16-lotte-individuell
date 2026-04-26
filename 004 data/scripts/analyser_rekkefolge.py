"""Analyser rekkefolgemonstre i tidsplaner pa tvers av modeller og scenarioer.

Spor: hvor robust er kommune-rekkefolgen?
- Heuristikk vs MIP
- Pa tvers av 3 NVDB-scenarioer
- Per kontor: hvilke kommuner gar alltid forst/sist?
- Effekt av storrelse, lasing, ansvarlig-kartkontor-tilhorighet?
"""

import sys
import io
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "processed_data"

SCENARIOER = ["Basis_85", "Middels_90", "Samferdsel_96"]

def les_heuristikk(scenario):
    df = pd.read_csv(PROC / f"tidsplan_{scenario}.csv", dtype={"KomNr": str})
    df["Ferdigdato_Kartkontor"] = pd.to_datetime(df["Ferdigdato_Kartkontor"])
    df = df.sort_values("Ferdigdato_Kartkontor").reset_index(drop=True)
    df["Rang_Heur"] = df.index + 1
    return df[["KomNr", "Kommune", "Kartkontor", "Antall_Lenker",
               "Gjenstaaende_Lenker_Start", "Ferdigdato_Kartkontor", "Rang_Heur"]]

def les_mip(scenario):
    df = pd.read_csv(PROC / f"tidsplan_mip_vektet_{scenario}.csv", dtype={"KomNr": str})
    df["Ferdigdato_Kartkontor"] = pd.to_datetime(df["Ferdigdato_Kartkontor"])
    # Innen samme manedsbucket: bryt ties pa lenker (storre forst, samme regel som heur)
    df = df.sort_values(["Ferdigdato_Kartkontor_Mnd", "Lenker"],
                        ascending=[True, False]).reset_index(drop=True)
    df["Rang_MIP"] = df.index + 1
    return df[["KomNr", "Kommune", "Hjemmekontor", "Kartkontor_MIP", "Omfordelt",
               "Lenker", "Ferdigdato_Kartkontor_Mnd",
               "Ferdigdato_Kartkontor", "Rang_MIP"]]

# Master for laast-info
master = pd.read_csv(PROC / "master_kommuner.csv", dtype={"KomNr": str})
laast = master[["KomNr", "Er_Laast", "Geovekst_Prosjekter", "Status"]]

print("=" * 78)
print("REKKEFOLGEANALYSE: kommuner pa tvers av scenarioer og modeller")
print("=" * 78)

# --- HEURISTIKK pa tvers av scenarioer ---
print("\n[1] HEURISTIKK: rang-stabilitet pa tvers av 3 scenarioer")
print("-" * 78)
heur = {s: les_heuristikk(s) for s in SCENARIOER}
heur_alle = heur["Basis_85"][["KomNr", "Kommune", "Kartkontor", "Rang_Heur"]].rename(
    columns={"Rang_Heur": "Rang_Basis"})
for s in ["Middels_90", "Samferdsel_96"]:
    heur_alle = heur_alle.merge(
        heur[s][["KomNr", "Rang_Heur"]].rename(columns={"Rang_Heur": f"Rang_{s}"}),
        on="KomNr"
    )
# Spearman-korrelasjoner (Pearson pa rangtall)
def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())

for s in ["Middels_90", "Samferdsel_96"]:
    rho = spearman(heur_alle["Rang_Basis"], heur_alle[f"Rang_{s}"])
    print(f"  Spearman rho (Basis_85 vs {s}): {rho:.4f}")

# Median rangforskyvning
heur_alle["Rang_Median"] = heur_alle[["Rang_Basis", "Rang_Middels_90",
                                       "Rang_Samferdsel_96"]].median(axis=1)
heur_alle["Rang_Spredning"] = heur_alle[["Rang_Basis", "Rang_Middels_90",
                                          "Rang_Samferdsel_96"]].max(axis=1) - \
                              heur_alle[["Rang_Basis", "Rang_Middels_90",
                                          "Rang_Samferdsel_96"]].min(axis=1)
print(f"\n  Rang-spredning over scenarioer (max-min):")
print(f"    Median: {heur_alle['Rang_Spredning'].median():.0f}")
print(f"    Gjennomsnitt: {heur_alle['Rang_Spredning'].mean():.1f}")
print(f"    P95: {heur_alle['Rang_Spredning'].quantile(0.95):.0f}")
print(f"    Maks: {heur_alle['Rang_Spredning'].max():.0f}")

# --- MIP pa tvers av scenarioer ---
print("\n[2] MIP: rang-stabilitet pa tvers av 3 scenarioer")
print("-" * 78)
mipd = {s: les_mip(s) for s in SCENARIOER}
mip_alle = mipd["Basis_85"][["KomNr", "Kommune", "Kartkontor_MIP", "Rang_MIP"]].rename(
    columns={"Rang_MIP": "MIP_Basis"})
for s in ["Middels_90", "Samferdsel_96"]:
    mip_alle = mip_alle.merge(
        mipd[s][["KomNr", "Rang_MIP"]].rename(columns={"Rang_MIP": f"MIP_{s}"}),
        on="KomNr"
    )
for s in ["Middels_90", "Samferdsel_96"]:
    rho = spearman(mip_alle["MIP_Basis"], mip_alle[f"MIP_{s}"])
    print(f"  Spearman rho (Basis_85 vs {s}): {rho:.4f}")

# --- HEURISTIKK vs MIP per scenario ---
print("\n[3] HEURISTIKK vs MIP per scenario")
print("-" * 78)
for s in SCENARIOER:
    sammen = heur[s][["KomNr", "Rang_Heur"]].merge(
        mipd[s][["KomNr", "Rang_MIP"]], on="KomNr")
    rho = spearman(sammen["Rang_Heur"], sammen["Rang_MIP"])
    print(f"  {s}: Spearman rho = {rho:.4f}")

# --- Hva forklarer rang? Storrelse vs lasing ---
print("\n[4] HVA STYRER REKKEFOLGEN? Korrelasjon med kommune-attributter")
print("-" * 78)
heur_basis = heur["Basis_85"].merge(laast, on="KomNr")
print("\n  Heuristikk Basis_85:")
rho_lenker = spearman(heur_basis["Rang_Heur"], heur_basis["Gjenstaaende_Lenker_Start"])
print(f"    rho(rang, gjenstaende lenker)       : {rho_lenker:.4f}")
print(f"    (negativ = stor kommune ferdig sent — fordi store tar mer tid)")
# For laaste vs ulaaste: gjennomsnittlig rang
laast_rang = heur_basis.groupby("Er_Laast")["Rang_Heur"].agg(["mean", "median", "count"])
print(f"\n    Snitt-rang etter lasing:")
print(laast_rang.to_string())

mip_basis = mipd["Basis_85"].merge(laast, on="KomNr")
print("\n  MIP Basis_85:")
rho_lenker_mip = spearman(mip_basis["Rang_MIP"], mip_basis["Lenker"])
print(f"    rho(rang, lenker)                   : {rho_lenker_mip:.4f}")
laast_rang_mip = mip_basis.groupby("Er_Laast")["Rang_MIP"].agg(["mean", "median", "count"])
print(f"\n    Snitt-rang etter lasing:")
print(laast_rang_mip.to_string())

# --- "Always early" / "always late" kommuner ---
print("\n[5] KOMMUNER MED ROBUST PLASSERING (heur + MIP, alle scenarioer)")
print("-" * 78)
# Slot inn rangkvartil per modell-scenario
N = len(heur["Basis_85"])
def kvartil(rang):
    arr = np.asarray(rang)
    q = (arr - 1) // (N // 4)
    return np.clip(q, 0, 3)  # 0=tidligst, 3=senest

robust = heur_alle[["KomNr", "Kommune", "Kartkontor"]].copy()
for s in SCENARIOER:
    robust[f"Q_heur_{s}"] = kvartil(heur[s].set_index("KomNr").loc[robust["KomNr"],
                                    "Rang_Heur"].values)
    robust[f"Q_mip_{s}"] = kvartil(mipd[s].set_index("KomNr").loc[robust["KomNr"],
                                    "Rang_MIP"].values)
q_cols = [c for c in robust.columns if c.startswith("Q_")]
robust["Alltid_Q1"] = (robust[q_cols] == 0).all(axis=1)
robust["Alltid_Q4"] = (robust[q_cols] == 3).all(axis=1)
robust["Alltid_Q1Q2"] = (robust[q_cols] <= 1).all(axis=1)
robust["Alltid_Q3Q4"] = (robust[q_cols] >= 2).all(axis=1)

print(f"\n  Kommuner alltid i Q1 (forste kvartil) — alle 6 modell-scenarioer:")
n_q1 = robust["Alltid_Q1"].sum()
n_q4 = robust["Alltid_Q4"].sum()
n_q12 = robust["Alltid_Q1Q2"].sum()
n_q34 = robust["Alltid_Q3Q4"].sum()
print(f"    Alltid Q1     : {n_q1} kommuner ({100*n_q1/N:.1f}%)")
print(f"    Alltid Q4     : {n_q4} kommuner ({100*n_q4/N:.1f}%)")
print(f"    Alltid Q1+Q2  : {n_q12} kommuner ({100*n_q12/N:.1f}%) — robust 'tidlig'")
print(f"    Alltid Q3+Q4  : {n_q34} kommuner ({100*n_q34/N:.1f}%) — robust 'sen'")

# Hva kjennetegner robust-tidlige vs robust-sene?
robust_meta = robust.merge(master[["KomNr", "Antall_Lenker", "Gjenstaaende_Lenker",
                                     "Er_Laast", "Status"]], on="KomNr")
print(f"\n  Karakteristikk av robust-TIDLIGE (alltid Q1+Q2, n={n_q12}):")
tidlig = robust_meta[robust_meta["Alltid_Q1Q2"]]
print(f"    Median gjenstaende lenker: {tidlig['Gjenstaaende_Lenker'].median():.0f}")
print(f"    Andel laast              : {100*tidlig['Er_Laast'].mean():.1f}%")
print(f"    Status-fordeling         : {tidlig['Status'].value_counts().to_dict()}")

print(f"\n  Karakteristikk av robust-SENE (alltid Q3+Q4, n={n_q34}):")
sen = robust_meta[robust_meta["Alltid_Q3Q4"]]
print(f"    Median gjenstaende lenker: {sen['Gjenstaaende_Lenker'].median():.0f}")
print(f"    Andel laast              : {100*sen['Er_Laast'].mean():.1f}%")
print(f"    Status-fordeling         : {sen['Status'].value_counts().to_dict()}")

print(f"\n  Total andel laast i datasett: {100*master['Er_Laast'].mean():.1f}%")
print(f"  Median gjenstaende lenker totalt: {master['Gjenstaaende_Lenker'].median():.0f}")

# --- Per kontor: variasjon i nar kontoret er ferdig ---
print("\n[6] PER KONTOR: nar kontoret er ferdig med sin siste kommune")
print("-" * 78)
print(f"\n  Heuristikk Basis_85 — siste ferdigdato per kontor:")
for kontor, grp in heur["Basis_85"].groupby("Kartkontor"):
    siste = grp["Ferdigdato_Kartkontor"].max()
    forst = grp["Ferdigdato_Kartkontor"].min()
    n = len(grp)
    print(f"    {kontor:14s}: {forst.date()} -> {siste.date()}  (n={n})")

# Er rekkefolgen blant store kommuner mer eller mindre stabil enn smaa?
print("\n[7] RANG-SPREDNING ETTER STORRELSE (heuristikk over 3 scenarioer)")
print("-" * 78)
heur_basis_full = heur_alle.merge(master[["KomNr", "Gjenstaaende_Lenker"]], on="KomNr")
heur_basis_full["Stor_Quantil"] = pd.qcut(heur_basis_full["Gjenstaaende_Lenker"],
                                            q=4, labels=["Q1_smaa", "Q2", "Q3", "Q4_store"])
spr = heur_basis_full.groupby("Stor_Quantil", observed=True)["Rang_Spredning"].agg(
    ["mean", "median", "max"])
print(spr.to_string())

# --- Per-kontor "biggest first"-test ---
print("\n[8] PER KONTOR: holder 'biggest first' INNEN kontor? (heuristikk Basis_85)")
print("-" * 78)
heur_basis_kontor = heur["Basis_85"].merge(laast, on="KomNr")
print(f"\n  Spearman rho(rang_innen_kontor, gjenstaende lenker) per kontor:")
print(f"  (negativ verdi = stor forst, positiv = liten forst)")
for kontor, grp in heur_basis_kontor.groupby("Kartkontor"):
    grp_sort = grp.sort_values("Ferdigdato_Kartkontor").reset_index(drop=True)
    grp_sort["Rang_Innen"] = grp_sort.index + 1
    rho = spearman(grp_sort["Rang_Innen"], grp_sort["Gjenstaaende_Lenker_Start"])
    rho_l = spearman(grp_sort["Rang_Innen"], grp_sort["Er_Laast"].astype(int))
    print(f"    {kontor:14s}: rho(lenker)={rho:+.3f}, rho(laast)={rho_l:+.3f}, n={len(grp)}")

# Andel av sene kommuner som er laast — per kontor
print("\n  Per kontor: andel laaste i siste tredjedel av koen")
for kontor, grp in heur_basis_kontor.groupby("Kartkontor"):
    grp_sort = grp.sort_values("Ferdigdato_Kartkontor")
    n = len(grp_sort)
    siste_3 = grp_sort.tail(n // 3)
    andel = siste_3["Er_Laast"].mean()
    total_andel = grp_sort["Er_Laast"].mean()
    print(f"    {kontor:14s}: siste tredjedel laast = {andel:.0%}, totalt {total_andel:.0%}")

# Lagre robust-rangering til CSV for videre bruk
ut = robust_meta[["KomNr", "Kommune", "Kartkontor", "Antall_Lenker",
                   "Gjenstaaende_Lenker", "Er_Laast", "Status",
                   "Alltid_Q1Q2", "Alltid_Q3Q4"]].copy()
ut["Rang_Median_Heur"] = heur_alle["Rang_Median"].values

# Klassifiser i fire kategorier som er reelt informative for rapporten
def klassifiser(rad):
    if rad["Status"] == "Ferdig":
        return "trivielt_tidlig_allerede_ferdig"
    if rad["Alltid_Q1Q2"]:
        return "ekte_robust_tidlig"
    if rad["Alltid_Q3Q4"]:
        return "robust_sen"
    return "fleksibel_mellomgruppe"

ut["Rekkefolge_Klasse"] = ut.apply(klassifiser, axis=1)
ut.to_csv(PROC / "rekkefolge_robust.csv", index=False, encoding="utf-8")

# Oppsummering av klassene
print(f"\n[9] FIRE REKKEFOLGEKLASSER (lagret som Rekkefolge_Klasse i CSV):")
print("-" * 78)
oppsum = ut.groupby("Rekkefolge_Klasse").agg(
    Antall=("KomNr", "count"),
    Median_Gjenst_Lenker=("Gjenstaaende_Lenker", "median"),
    Snitt_Gjenst_Lenker=("Gjenstaaende_Lenker", "mean"),
    Andel_Laast=("Er_Laast", "mean"),
)
oppsum["Andel_Laast"] = (oppsum["Andel_Laast"] * 100).round(0).astype(int).astype(str) + "%"
oppsum["Median_Gjenst_Lenker"] = oppsum["Median_Gjenst_Lenker"].astype(int)
oppsum["Snitt_Gjenst_Lenker"] = oppsum["Snitt_Gjenst_Lenker"].astype(int)
print(oppsum.to_string())

print(f"\n[OK] Lagret rekkefolge_robust.csv ({len(ut)} rader, {ut['Rekkefolge_Klasse'].nunique()} klasser)")
