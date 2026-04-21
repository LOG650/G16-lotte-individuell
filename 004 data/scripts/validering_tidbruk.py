"""
Uavhengig validering av tidbruk-formelen:
    Ber_Tidbruk_Min = Km_Kurve * 0.9035 + ArealLand_Km2 * 0.6510

Tre valideringer:
  V1: Re-deriver koeffisientene fra 58 kartbladmaalinger
  V2: Formel vs kontorenes oppgitte min/max-band
  V3: Fordeling Ferdig vs gjenstaaende
"""

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r"C:\IT_studier\LOG650_Logistikk_og_KI\Prosjekt\G16-lotte-individuell")
PROC = ROOT / "004 data" / "processed_data"

# ---------------------------------------------------------------
# V1: Re-deriver koeffisientene
# ---------------------------------------------------------------
print("=" * 70)
print("V1: Re-deriver koeffisientene fra 58 kartbladmaalinger")
print("=" * 70)

kal = pd.read_csv(PROC / "tidbruk_kalibrering.csv")
print(f"Kolonner i tidbruk_kalibrering.csv: {list(kal.columns)}")
print(f"Antall rader: {len(kal)}")
print(f"\nFoerste 3 rader:")
print(kal.head(3).to_string())

# Sjekker om arealkolonne finnes
har_areal = any("areal" in c.lower() or "km2" in c.lower() for c in kal.columns)
print(f"\nHar arealkolonne: {har_areal}")
print(f"Min_Per_Km2-kolonnen finnes, men er den et areal eller en rate?")
# Ut fra dataene: Min_Per_Km2 = Minutter / kartblad-areal. Kartblad har fast areal.
# Det er IKKE en uavhengig prediktor pr. kartblad.
print(f"\nUnike verdier i Min_Per_Km2 (foerste 10): {sorted(kal['Min_Per_Km2'].unique())[:10]}")
print(f"Beregnet kartblad-areal (Minutter/Min_Per_Km2):")
arealer = kal['Minutter'] / kal['Min_Per_Km2']
print(f"  unike (avrundet til 4 desimaler): {sorted(arealer.round(4).unique())}")

# Min_Per_Km2 = Minutter / Areal -> Areal = Minutter / Min_Per_Km2
# Hvis areal er konstant per kartblad, kan vi sjekke det
kal['Beregnet_Areal_Km2'] = kal['Minutter'] / kal['Min_Per_Km2']
print(f"\nAreal-statistikk: min={kal['Beregnet_Areal_Km2'].min():.4f}, "
      f"max={kal['Beregnet_Areal_Km2'].max():.4f}, "
      f"std={kal['Beregnet_Areal_Km2'].std():.4f}")

# OLS uten konstantledd: Minutter ~ Lengde_Km + Areal
print("\n--- OLS uten konstantledd (Minutter ~ Lengde_Km + Areal_Km2) ---")
y = kal['Minutter'].values.astype(float)
X = np.column_stack([
    kal['Lengde_Km'].values.astype(float),
    kal['Beregnet_Areal_Km2'].values.astype(float),
])

# Egen OLS
beta, residuals_ss, rank, sv = np.linalg.lstsq(X, y, rcond=None)
y_hat = X @ beta
resid = y - y_hat
ss_res = (resid ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
ss_tot_uncentered = (y ** 2).sum()
r2_centered = 1 - ss_res / ss_tot
r2_uncentered = 1 - ss_res / ss_tot_uncentered
n, k = X.shape
sigma2 = ss_res / (n - k)
cov_beta = sigma2 * np.linalg.inv(X.T @ X)
se_beta = np.sqrt(np.diag(cov_beta))

print(f"  beta_Lengde_Km   = {beta[0]:.4f}  (SE = {se_beta[0]:.4f})")
print(f"  beta_Areal_Km2   = {beta[1]:.4f}  (SE = {se_beta[1]:.4f})")
print(f"  R^2 (sentrert)   = {r2_centered:.4f}")
print(f"  R^2 (usentrert)  = {r2_uncentered:.4f}")
print(f"  Residual std     = {np.sqrt(sigma2):.3f} min")
print(f"  n = {n}, k = {k}")

# Sjekk paastaatt 0.9035 / 0.6510
print(f"\nPaastaatt: 0.9035 / 0.6510")
print(f"Paastaatt 0.9035 = mean(Min_Per_Km) = {kal['Min_Per_Km'].mean():.4f}")
print(f"Paastaatt 0.6510 = mean(Min_Per_Km2) = {kal['Min_Per_Km2'].mean():.4f}")
# -> 0.9035 og 0.6510 er IKKE OLS-koeffisienter, men gjennomsnitt av to RATER

# Outliers
print("\n--- Outliers (standardiserte residualer > 2.5) ---")
std_resid = resid / np.sqrt(sigma2)
out = kal.assign(resid=resid, std_resid=std_resid).query("abs(std_resid) > 2.5")
if len(out):
    print(out[['Kartblad', 'Minutter', 'Lengde_Km', 'Min_Per_Km', 'std_resid']].to_string())
else:
    print("  ingen.")

# Spredning i Min_Per_Km
print(f"\nMin_Per_Km empirisk: mean={kal['Min_Per_Km'].mean():.3f}, "
      f"median={kal['Min_Per_Km'].median():.3f}, "
      f"std={kal['Min_Per_Km'].std():.3f}, "
      f"min={kal['Min_Per_Km'].min():.3f}, "
      f"max={kal['Min_Per_Km'].max():.3f}")

# ---------------------------------------------------------------
# V2: Formel vs kontorenes oppgitte min/max-band
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("V2: Formel vs kontorenes oppgitte min/max-band (timer per kommune)")
print("=" * 70)

mast = pd.read_csv(PROC / "master_kommuner.csv")
kap = pd.read_csv(PROC / "kapasitet_kontorer.csv")

mast['Ber_Tidbruk_Timer'] = mast['Ber_Tidbruk_Min'] / 60.0

rows = []
for _, k in kap.iterrows():
    kontor = k['Kartkontor']
    lo = k['Min_Tidsbruk_Timer']
    hi = k['Max_Tidsbruk_Timer']
    sub = mast[mast['Kartkontor'] == kontor]
    n = len(sub)
    innenfor = ((sub['Ber_Tidbruk_Timer'] >= lo) & (sub['Ber_Tidbruk_Timer'] <= hi)).sum()
    under = (sub['Ber_Tidbruk_Timer'] < lo).sum()
    over = (sub['Ber_Tidbruk_Timer'] > hi).sum()
    rows.append({
        'Kontor': kontor,
        'Band_lo': lo, 'Band_hi': hi,
        'n_komm': n,
        'innenfor': innenfor,
        'under': under,
        'over': over,
        'andel_innenfor_%': round(100 * innenfor / n, 1),
        'median_timer': round(sub['Ber_Tidbruk_Timer'].median(), 1),
        'min_timer': round(sub['Ber_Tidbruk_Timer'].min(), 1),
        'max_timer': round(sub['Ber_Tidbruk_Timer'].max(), 1),
    })
v2 = pd.DataFrame(rows)
print(v2.to_string(index=False))
flagget = v2[v2['andel_innenfor_%'] < 50]
print(f"\nKontorer der >50 % er UTENFOR baandet: {list(flagget['Kontor'])}")

# ---------------------------------------------------------------
# V3: Fordeling Ferdig vs resten
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("V3: Fordeling av Ber_Tidbruk_Min, Ferdig vs resten")
print("=" * 70)

ferdig = mast[mast['Status'] == 'Ferdig']['Ber_Tidbruk_Min'].dropna()
resten = mast[mast['Status'] != 'Ferdig']['Ber_Tidbruk_Min'].dropna()

print(f"n_Ferdig = {len(ferdig)}, n_Resten = {len(resten)}")
print(f"Verdier av Status: {mast['Status'].value_counts().to_dict()}")

def stats(s, navn):
    q = s.quantile([0.25, 0.5, 0.75])
    print(f"  {navn}: median={s.median():.0f}, Q1={q[0.25]:.0f}, Q3={q[0.75]:.0f}, "
          f"mean={s.mean():.0f}, min={s.min():.0f}, max={s.max():.0f}, n={len(s)}")

stats(ferdig, "Ferdig")
stats(resten, "Resten")

# KS-test og Mann-Whitney
try:
    from scipy import stats as sps
    ks = sps.ks_2samp(ferdig, resten)
    mw = sps.mannwhitneyu(ferdig, resten, alternative='two-sided')
    print(f"\nKolmogorov-Smirnov: D = {ks.statistic:.4f}, p = {ks.pvalue:.4f}")
    print(f"Mann-Whitney U:     U = {mw.statistic:.1f}, p = {mw.pvalue:.4f}")
except ImportError:
    print("  scipy ikke tilgjengelig")

# Forholdstall
print(f"\nMedian Ferdig / Median Resten = {ferdig.median() / resten.median():.3f}")
print(f"Mean   Ferdig / Mean   Resten = {ferdig.mean() / resten.mean():.3f}")
