"""Search the KNHANES official dictionary (Chinese labels) for the exposure
domains the project needs but never operationalized.
"""
import sys
from pathlib import Path
import pandas as pd

TMP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")


def read_any(p: Path) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "gbk", "cp936", "latin1"):
        try:
            d = pd.read_csv(p, encoding=enc)
            if d.shape[1] > 1:
                return d
        except Exception:
            continue
    raise RuntimeError(f"cannot read {p}")


dictp = TMP / "kn_dictionary_full.csv"
d = read_any(dictp)
base_names = ["id", "kr", "cn", "note", "from", "year", "rdata"]
d.columns = base_names + [f"extra{i}" for i in range(d.shape[1] - len(base_names))]
print("dictionary rows:", len(d), "cols:", list(d.columns))

cols = read_any(TMP / "kn_colnames.csv")
have = {o: set(g["col"]) for o, g in cols.groupby("obj")}
print("objects with colnames:", list(have))


def search(title, patterns, maxn=30):
    print(f"\n=== {title} ===")
    pat = "|".join(patterns)
    hit = d[d["cn"].astype(str).str.contains(pat, regex=True, na=False)].copy()
    if hit.empty:
        print("  (no match)")
        return
    hit = hit.drop_duplicates(subset=["id", "from"])
    # annotate availability in the objects we actually have
    def where(r):
        return ",".join(o for o, s in have.items() if r["id"] in s)
    hit["in_our_objects"] = hit.apply(where, axis=1)
    hit = hit.sort_values(["id", "from"])
    show = hit[["id", "cn", "from", "in_our_objects"]].head(maxn)
    with pd.option_context("display.max_colwidth", 46, "display.width", 200):
        print(show.to_string(index=False))


search("ALCOHOL (drinking)", [r"饮酒", r"喝酒", r"酗酒", r"酒精", r"酒量", r"喝酒频率"])
search("VITAMIN D / 25(OH)D", [r"维生素\s*D", r"25-?羟", r"维生素D"])
search("ANTIOXIDANT / CAROTENOID", [r"维生素C", r"维生素E", r"胡萝卜素", r"叶黄素", r"玉米黄质", r"抗氧化", r"视黄醇"])
search("AIR POLLUTION / PM", [r"颗粒物", r"PM2", r"PM10", r"空气污染", r"大气", r"细颗粒", r"可吸入"])
search("UV / SUNLIGHT", [r"紫外线", r"日照", r"阳光", r"户外活动"])
search("DIETARY INDEX inputs (膳食/饮食)", [r"膳食", r"饮食", r"营养"], maxn=40)
search("MEDICATION / supplement", [r"维生素补充", r"营养补充剂", r"保健品"])

print("\n=== any BD* (alcohol module) columns available? ===")
allcols = sorted({c for s in have.values() for c in s})
for pref in ["BD", "BA1", "LS_", "N_", "Nf_", "HS_", "LQ", "MF", "AC_"]:
    sel = [c for c in allcols if c.startswith(pref)]
    print(f"  {pref:6s} -> {sel[:24]}{' ...' if len(sel) > 24 else ''}")
