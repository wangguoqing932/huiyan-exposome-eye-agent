#!/usr/bin/env python
"""生成/校验 Executor 交付的 6 张表（R10 2026-10-15 实装，取代 WO-25 存根）。

职责划分（单一写者原则）：
  本脚本生成（源数据在仓库内，可独立重建）：
    registry_summary.csv        ← data/seed/entities_{a,b}.csv
    rule_list.csv               ← configs/rules.yaml（v1.2 冻结）
    validation_distribution.csv ← outputs/confirmatory/*_confirmatory.csv
                                   + *_metrics_v11.json（R5 survey 方差 headline）
  本脚本只校验（写者为 rebuild_deliverables_R5.py / make_baseline_summary_R5.py，
  不在此重复生成，避免双源漂移）：
    performance_matrix.csv / performance_by_dataset.csv / dataset_summary.csv
    —— 存在性 + 表头（WO-24/26 契约：performance_by_dataset 8 列契约前缀
       dataset_id,dataset_role,method,metric,mean,std,n_cases,n_seeds + CI 列，
       且含 gap_ 行）+ headline 数字与 metrics JSON 一致。

审计注记（2026-10-15）：旧 validation_distribution.csv 的 NHANES 行为 R5 测量
修复前的过期数字（tested=71/29，freq 口径 7/0/7）；本实现按当前主口径重算
（tested=80/20，survey headline 5/0/9），KNHANES/CHARLS 行不受影响。

Run: PYTHONUTF8=1 python scripts/generate_paper_tables.py
"""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "outputs" / "tables"
CONF = ROOT / "outputs" / "confirmatory"

PBD_CONTRACT_PREFIX = ["dataset_id", "dataset_role", "method", "metric",
                       "mean", "std", "n_cases", "n_seeds"]


def gen_registry_summary() -> None:
    a = pd.read_csv(ROOT / "data/seed/entities_a.csv", encoding="utf-8-sig")
    b = pd.read_csv(ROOT / "data/seed/entities_b.csv", encoding="utf-8-sig")

    def n_unique_flags(df: pd.DataFrame) -> int:
        flags = set()
        for v in df["flags"].fillna(""):
            flags.update(f.strip() for f in str(v).split(";") if f.strip())
        return len(flags)

    out = pd.DataFrame([
        {"registry": "entity_a", "count": len(a), "unique_flags": n_unique_flags(a),
         "note": f"{len(a)} exposures, v1.2 rules"},
        {"registry": "entity_b", "count": len(b), "unique_flags": n_unique_flags(b),
         "note": f"{len(b)} eye disease items"},
    ])
    out.to_csv(TAB / "registry_summary.csv", index=False, encoding="utf-8-sig")
    print(f"[gen] registry_summary.csv: A={len(a)}/{n_unique_flags(a)} B={len(b)}/{n_unique_flags(b)}")


def gen_rule_list() -> None:
    data = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))
    rules = data["rules"] if isinstance(data, dict) and "rules" in data else data
    # 表注记不在 yaml 内，来自 analysis_plan v1.2 冻结记录（§0/§0.2：r22 为
    # 看过首轮确证后新增的探索性扩展，survey 方差下两条 NHANES 对不构成复证）
    rule_notes = {
        "r22_bmi_x_retinopathy": "exploratory extension (v1.2 §0)",
    }
    rows = []
    for r in rules:
        a_flags = ",".join(ast.literal_eval(str(r["entity_a_flags"])))
        b_flags = ",".join(ast.literal_eval(str(r["entity_b_flags"])))
        rows.append({
            "rule_id": r["id"], "severity": r["severity"], "risk_type": r["risk_type"],
            "evidence_level": r["evidence_level"], "direction": r["direction"],
            "a_flags": a_flags, "b_flags": b_flags,
            "negative_control": str(r.get("negative_control", "False")) == "True",
            "note": rule_notes.get(r["id"], ""),
        })
    out = pd.DataFrame(rows, columns=["rule_id", "severity", "risk_type", "evidence_level",
                                      "direction", "a_flags", "b_flags", "negative_control", "note"])
    out.to_csv(TAB / "rule_list.csv", index=False, encoding="utf-8-sig")
    print(f"[gen] rule_list.csv: {len(out)} rules")


def gen_validation_distribution() -> None:
    rows = []
    for ds, csv_name, json_name in [
        ("NHANES", "nhanes_confirmatory.csv", "nhanes_metrics_v11.json"),
        ("KNHANES", "knhanes_confirmatory.csv", "knhanes_metrics_v11.json"),
        ("CHARLS", "charls_confirmatory.csv", "charls_metrics_v11.json"),
    ]:
        res = pd.read_csv(CONF / csv_name, encoding="utf-8-sig")
        met = json.loads((CONF / json_name).read_text(encoding="utf-8"))
        counts = res["status"].value_counts()
        rows.append({
            "dataset": ds, "total_pairs": len(res),
            "tested": int(counts.get("tested", 0)),
            "underpowered": int(counts.get("underpowered", 0)),
            "rule_pairs_tested": met["rule_pairs_tested"],
            "replicated": met["replicated"], "contradicted": met["contradicted"],
            "uninformative": met["uninformative"],
        })
    out = pd.DataFrame(rows)
    out.to_csv(TAB / "validation_distribution.csv", index=False, encoding="utf-8-sig")
    print(f"[gen] validation_distribution.csv: {list(out['dataset'])} "
          f"rule 前三态 {[tuple(r) for r in out[['replicated','contradicted','uninformative']].to_records(index=False)]}")


def validate_pipeline_tables() -> list[str]:
    errs: list[str] = []
    # performance_matrix：表头 + 三行 headline 与 metrics JSON 一致
    pm_path = TAB / "performance_matrix.csv"
    if not pm_path.exists():
        errs.append(f"缺 {pm_path.name}（应由 rebuild_deliverables_R5.py 生成）")
    else:
        pm = pd.read_csv(pm_path, encoding="utf-8-sig")
        need = ["dataset", "rule_pairs_tested", "replicated", "contradicted",
                "uninformative", "precision_rule", "coverage", "methodology"]
        missing = [c for c in need if c not in pm.columns]
        if missing:
            errs.append(f"performance_matrix 缺列 {missing}")
        for ds, json_name in [("NHANES", "nhanes_metrics_v11.json"),
                              ("KNHANES", "knhanes_metrics_v11.json"),
                              ("CHARLS", "charls_metrics_v11.json")]:
            met = json.loads((CONF / json_name).read_text(encoding="utf-8"))
            row = pm[pm["dataset"] == ds]
            if row.empty:
                errs.append(f"performance_matrix 缺 {ds} 行")
                continue
            for col, key in [("rule_pairs_tested", "rule_pairs_tested"),
                             ("replicated", "replicated"),
                             ("contradicted", "contradicted"),
                             ("uninformative", "uninformative"),
                             ("coverage", "coverage")]:
                if float(row.iloc[0][col]) != float(met[key]):
                    errs.append(f"performance_matrix {ds}.{col}={row.iloc[0][col]} "
                                f"与 {json_name} {key}={met[key]} 不一致")
    # performance_by_dataset：WO-26 契约表头前缀 + gap 行
    pbd_path = TAB / "performance_by_dataset.csv"
    if not pbd_path.exists():
        errs.append(f"缺 {pbd_path.name}（rebuild_deliverables_R5.py / make_baseline_summary_R5.py 生成）")
    else:
        pbd = pd.read_csv(pbd_path, encoding="utf-8-sig")
        cols = list(pbd.columns)
        if cols[:len(PBD_CONTRACT_PREFIX)] != PBD_CONTRACT_PREFIX:
            errs.append(f"performance_by_dataset 表头契约前缀应为 {PBD_CONTRACT_PREFIX}，实际 {cols}")
        for extra in ["ci_lo", "ci_hi", "ci_note"]:
            if extra not in cols:
                errs.append(f"performance_by_dataset 缺 {extra} 列")
        if "gap" not in "".join(pbd["metric"].astype(str)):
            errs.append("performance_by_dataset 缺 gap_ 行（WO-26 契约）")
    # dataset_summary：存在 + 基本列
    dst_path = TAB / "dataset_summary.csv"
    if not dst_path.exists():
        errs.append(f"缺 {dst_path.name}")
    else:
        dst = pd.read_csv(dst_path, encoding="utf-8-sig")
        if "dataset_id" not in dst.columns or "confirmatory_run" not in dst.columns:
            errs.append("dataset_summary 缺 dataset_id/confirmatory_run 列")
    return errs


def main() -> int:
    TAB.mkdir(parents=True, exist_ok=True)
    gen_registry_summary()
    gen_rule_list()
    gen_validation_distribution()
    errs = validate_pipeline_tables()
    if errs:
        print("[tables] 校验失败：", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("[tables] performance_matrix / performance_by_dataset / dataset_summary 校验通过"
          "（写者：rebuild_deliverables_R5.py + make_baseline_summary_R5.py）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
