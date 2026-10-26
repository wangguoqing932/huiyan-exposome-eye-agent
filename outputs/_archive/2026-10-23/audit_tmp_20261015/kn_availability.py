"""Consolidated availability check of the KNHANES columns we can actually use."""
import sys
from pathlib import Path
import pandas as pd

TMP = Path(sys.argv[1])
for enc in ("utf-8", "gbk", "latin1"):
    try:
        cols = pd.read_csv(TMP / "kn_colnames.csv", encoding=enc)
        break
    except Exception:
        continue
have = {o: set(g["col"]) for o, g in cols.groupby("obj")}
ALLOBJ = sorted(have)

GROUPS = {
    "eye 2008-2012 scheme": ["E_DRP_R", "E_DRP_L", "E_AMD_ELY_R", "E_AMD_LATE_R", "E_VS_DS",
                             "E_Gr_p", "E_Gl_p", "E_Grv", "E_Glv"],
    "eye 2016-2021 scheme": ["E_DM", "E_DM_r", "E_DM_l", "E_DME", "E_AMD", "E_AMD_r", "E_AMD_l",
                             "E_EM", "E_GR", "E_Pr_1", "E_DG", "E_DG1"],
    "self-report eye": ["DH2_lt", "DH3_lt", "DH1_dg", "DH2_dg", "DH3_dg", "DH4_dg", "DH6_dg", "DH7_dg"],
    "smoking": ["BS1_1", "BS3_1", "BS5", "BS5_1", "BS12_1"],
    "alcohol (BD module)": ["BD1", "BD1_11", "BD2", "BD2_1", "BD2_14", "BD2_31", "BD2_32", "BD4"],
    "alcohol (BA module, what repo used)": ["BA2_2_1", "BA2_22", "BA2_12", "BA2_13", "BA2_14"],
    "anthropometry / BP": ["HE_BMI", "HE_wc", "HE_sbp", "HE_dbp", "HE_ht", "HE_wt"],
    "glycemia": ["HE_HbA1c", "HE_glu", "HE_insulin", "HE_DM"],
    "lipids": ["HE_chol", "HE_TG", "HE_HDL_st2", "HE_LDL_drct"],
    "inflammation": ["HE_hsCRP", "HE_WBC"],
    "urate / metals": ["HE_Uacid", "HE_UAScr", "HE_UAScr_AAS", "HE_Pb", "HE_Cd", "HE_Hg"],
    "vitamin D candidates": ["HE_VitD", "HE_25OHD", "HE_25OHD2", "HE_25OHD3", "HE_vitD", "VITD"],
    "diet (24h recall / FFQ)": ["N_CAROT", "N_vitc", "N_vite", "N_FIBER", "N_N3", "N_KCAL",
                                "N_FAT", "N_PROT", "N_NA", "N_CA"],
    "supplements": ["LS_1MO", "LS_1YR", "LS_KIND1", "LS_NAME1", "LS_FQ1"],
    "air pollution (_ap)": ["PM25", "PM10", "O3", "NO2", "SO2", "CO"],
    "indoor air (iaq)": ["IAQ_PM2_5", "IAQ_PM2_5_atmos"],
    "UV / sunshine candidates": ["UV", "UVB", "SUN", "SUNSHINE", "SI", "SSD"],
    "design / SES": ["edu", "incm", "incm5", "psu", "kstrata", "wt_itvex", "wt_itv", "wt_ex", "age", "sex"],
}

rows = []
for gname, vs in GROUPS.items():
    for v in vs:
        objs = [o for o in ALLOBJ if v in have[o]]
        rows.append({"group": gname, "var": v, "n_objects": len(objs),
                     "objects": ",".join(objs)})
out = pd.DataFrame(rows)
with pd.option_context("display.max_colwidth", 120, "display.width", 240):
    for g in out["group"].unique():
        sub = out[out["group"] == g]
        print(f"\n=== {g} ===")
        for r in sub.itertuples():
            mark = "OK " if r.n_objects else "-- "
            print(f"  {mark}{r.var:16s} {r.objects if r.n_objects else 'ABSENT from all probed objects'}")

print("\n=== fuzzy scan for vitamin D / UV / sunshine across ALL objects ===")
allset = {c for s in have.values() for c in s}
for key in ["VIT", "Vit", "vit", "25", "OHD", "UV", "Sun", "SUN", "sun", "SSD"]:
    hit = sorted(c for c in allset if key in c)
    print(f"  {key:5s} -> {hit[:20]}")
