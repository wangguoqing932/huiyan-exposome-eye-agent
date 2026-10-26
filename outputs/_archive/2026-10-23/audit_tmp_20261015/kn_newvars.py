"""Labels for the newly discovered KNHANES variables + _ap / _24rc availability."""
import sys
from pathlib import Path
import pandas as pd

TMP = Path(sys.argv[1])


def read_any(p):
    for enc in ("utf-8", "utf-8-sig", "gbk", "cp936", "latin1"):
        try:
            d = pd.read_csv(p, encoding=enc)
            if d.shape[1] > 1:
                return d
        except Exception:
            continue
    raise RuntimeError(p)


d = read_any(TMP / "kn_dictionary_full.csv")
names = ["id", "kr", "cn", "note", "from", "year", "rdata"]
d.columns = names + [f"x{i}" for i in range(d.shape[1] - len(names))]

WANT = ["HE_vitD", "HE_VitA", "HE_VitE", "N_VITD", "N_VITC", "N_VITE", "N_CAROT",
        "FQ_VITC", "LS_VIT", "TLS_VITC", "LS_1YR", "LS_1MO", "LS_KIND1", "LS_NAME1",
        "BD1", "BD1_11", "BD2", "BD2_1", "BD2_14", "BD2_31", "BD2_32", "BD4",
        "BS1_1", "BS3_1", "BS5", "BS12_1",
        "E_DM", "E_DM_r", "E_DM_l", "E_DME", "E_AMD", "E_AMD_r", "E_AMD_l",
        "E_EM", "E_GR", "E_Pr_1", "E_DG", "E_DG1", "E_Q_SUN",
        "DH2_dg", "DH3_dg", "DH4_dg", "DH6_dg", "DH7_dg",
        "HE_Pb", "HE_Cd", "HE_Hg", "HE_WBC", "HE_Uacid", "HE_hsCRP",
        "edu", "incm", "incm5", "psu", "kstrata", "wt_itvex"]
for v in WANT:
    sub = d[d["id"] == v].drop_duplicates(subset=["from"])
    if sub.empty:
        print(f"{v:14s} : NOT IN DICTIONARY")
        continue
    ids = list(sub["id"]); srcs = list(sub["from"]); cns = list(sub["cn"])
    for i in range(min(4, len(ids))):
        cn = str(cns[i]).replace("\\U+", "U+")
        print(f"{v:14s} | {str(srcs[i]):16s} | {cn}")

# now availability in the extra objects
import os
p2 = TMP / "kn_colnames_extra.csv"
if p2.exists():
    c2 = read_any(p2)
    have2 = {o: set(g["col"]) for o, g in c2.groupby("obj")}
    print("\n=== _ap / _24rc / _ffq availability ===")
    for o, s in sorted(have2.items()):
        keys = [k for k in ["PM25", "PM10", "O3", "NO2", "SO2", "CO", "IAQ_PM2_5",
                            "N_VITC", "N_VITD", "N_VITE", "N_CAROT", "FQ_VITC",
                            "LS_VIT", "TLS_VITC", "HE_VitA", "HE_VitE"] if k in s]
        print(f"  {o:14s} ncol={len(s):4d}  keys={keys}")

print("\n=== dictionary rows whose label mentions PM2.5 / 颗粒物, with source object ===")
hit = d[d["cn"].astype(str).str.contains("颗粒物", na=False)].drop_duplicates(subset=["id", "from"])
print(hit[["id", "from"]].head(30).to_string(index=False))
