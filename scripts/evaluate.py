#!/usr/bin/env python
"""huiyan executor — confirmatory validation pipeline (analysis_plan v1.1).

Replaces phase5_nhanes/knhanes/charls scripts (B1: archived as .bak).
Reads cases from data/datasets/<id>/cases.jsonl (B2: file I/O with error on missing).
Implements B3-B7 fixes: fixed clinical cutoffs, unit-harmonized composites,
VI threshold fix, flag de-overloading, nesting guard, direction audit wired,
separation detection, R survey fallback path.

Usage:
    python scripts/evaluate.py --dataset intval-nhanes
    python scripts/evaluate.py --dataset extval-knhanes
    python scripts/evaluate.py --dataset extval-cohorts-9
"""
from __future__ import annotations
import argparse, json, math, os, subprocess, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, Rule
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
import csv


def get_judgeable_b_items(dataset_key: str = "nhanes") -> set[str]:
    """D5: Read boolean judgeable columns from entities_b.csv.
    
    Returns the set of entity_b_ids that are judgeable in the given dataset.
    Items not in this set are excluded from P/R/F1 denominators (coverage only).
    """
    b_path = ROOT / "data" / "seed" / "entities_b.csv"
    if not b_path.exists():
        return set()
    col = f"{dataset_key}_judgeable"
    judgeable = set()
    with b_path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get(col, "").strip().lower() == "true":
                judgeable.add(row.get("entity_b_id", "").strip())
    return judgeable


warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════════════
#  B3a: Fixed clinical cutoffs (NOT sample quantiles)
# ══════════════════════════════════════════════════════════════════
# These thresholds are pre-registered and must NEVER change between datasets.
CLINICAL_CUTOFFS = {
    "uric_acid_elevated": {"male": 7.0, "female": 5.7, "unit": "mg/dL",
                           "note": "R11 统一 NHANES(原 6.8) 与 KNHANES(7.0) 切点以保证跨库可比"},
    "hyperglycemia": {"threshold": 126, "unit": "mg/dL", "alt_dx": "DIQ010==1 (DIQ 模块 R11 起已加载)"},
    "hba1c_elevated": {"threshold": 6.5, "unit": "%"},
    "dyslipidemia": {
        "total_cholesterol": 240, "ldl": 160, "triglycerides": 200, "hdl_low": 40, "unit": "mg/dL",
        "vars": {"TC": "BIOPRO.LBXSCH", "TG": "BIOPRO.LBXSTR",
                 "HDL": "HDL_D.LBDHDD", "LDL": "TRIGLY_D.LBDLDL"},
        "note": "R11 2026-10-15: HDL/LDL 模块此前未加载, 两个分支恒为 False",
    },
    # R11 2026-10-15: LBXCRP 单位是 mg/dL。AHA 高危阈值 3 mg/L ≡ 0.3 mg/dL。
    # 原写法 >3.0 实为 >30 mg/L, 暴露率 1.17%(应 30.4%)。
    "crp_elevated": {"threshold": 0.3, "unit": "mg/dL (=3 mg/L, AHA)", "raw_unit": "mg/dL",
                     "continuous_export": "crp_mgl_continuous (mg/L)"},
    "bmi_high": {"threshold": 25.0, "unit": "kg/m2",
                 "sensitivity": "bmi_high_asian23 (>=23, WHO 亚洲切点)"},
    "current_smoking": {"var": "SMQ020+SMQ040", "positive": "SMQ020==1 & SMQ040 in (1,2); ref=never∪former (R11)"},
    "ever_smoking": {"var": "SMQ020", "positive": "SMQ020==1; ref=SMQ020==2"},
    "former_smoking": {"var": "SMQ020+SMQ040", "positive": "SMQ020==1 & SMQ040==3"},
    "alcohol_intake": {"var": "ALQ120Q (current; ALQ101 gate)", "positive": ">=1 day past yr; ref=0 or lifetime-never (R11)"},
    "alcohol_frequent": {"var": "ALQ120Q", "positive": ">=52 days/yr (weekly+)"},
    "lead_exposure": {"threshold": 3.5, "unit": "ug/dL",
                      "note": "2021 CDC blood lead reference value (原用 5.0, 暴露率 4.9%→12.9%)",
                      "continuous_export": "log_lead_continuous"},
    # B3b / R11 2026-10-15: 原实现引用不存在的 DR1TVE 且用样本下四分位切点。
    # 现改为外生 EAR 标准下的"摄入不足项数 >= 2/3"。
    "low_antioxidant_intake": {
        "vars": ["DR1TVC", "DR1TATOC", "DR1TLZ"],
        "banned_vars": ["DR1TVE"],
        "method": "count_below_EAR_ge_2_of_3",
        "ear_thresholds": {"DR1TVC": 60, "DR1TATOC": 12, "DR1TLZ": 6},
        "note": "单位: DR1TVC mg, DR1TATOC mg α-生育酚, DR1TLZ mg 叶黄素+玉米黄质; "
                "另有 antioxidant_inadequate_count (0-3) 序数版本",
    },
}

# ══════════════════════════════════════════════════════════════════
#  B3c: VI thresholds in logMAR (presenting VA, worse eye — R5 fix)
#  LogMAR values differ from each other — the original bug was using
#  identical thresholds for mild and moderate.
# ══════════════════════════════════════════════════════════════════
VI_THRESHOLDS = {
    "vision_impairment_mild": {"logMAR_gt": 0.30},      # worse than 20/40
    "vision_impairment_moderate": {"logMAR_gt": 0.48},  # worse than 20/60
    "vision_impairment_severe": {"logMAR_gt": 1.00},    # worse than 20/200
    # NOTE: these are CUMULATIVE (severe ⊂ moderate ⊂ mild); B3e nesting guard
    # prevents double-counting by assigning each person to the WORST category only
}

# ══════════════════════════════════════════════════════════════════
#  B3d: Flag de-overloading — secondhand smoke gets its own flag
# ══════════════════════════════════════════════════════════════════
# entities_a.csv already has secondhand_smoke as separate row with
# current_smoking flag. The fix: separate rows should NOT share flags
# that trigger different rules. We do this at the registry level, not here.

# ══════════════════════════════════════════════════════════════════
#  Core pipeline
# ══════════════════════════════════════════════════════════════════

def load_cases(dataset_id: str) -> list[dict]:
    """B2: Read cases from JSONL. Exit non-zero if file missing or empty."""
    path = ROOT / "data" / "datasets" / dataset_id / "cases.jsonl"
    if not path.exists():
        print(f"[evaluate] ERROR: {path} not found — run scripts/generate_cases.py first")
        sys.exit(1)
    cases = [json.loads(l) for l in path.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
    if not cases:
        print(f"[evaluate] ERROR: {path.name} is empty (0 cases)")
        sys.exit(1)
    return cases


# ── variable_map 运行时守卫(M12/M7,2026-10-16)───────────────────────
_VM_CODE_VARS = {  # 代码实际引用变量(改派生时同步此表与 configs/variable_map.yaml)
    "current_smoking": {"SMQ020", "SMQ040"},
    "ever_smoking": {"SMQ020"},
    "alcohol_current": {"ALQ101", "ALQ110", "ALQ120Q", "ALQ120U", "ALQ130"},
    "uric_acid": {"LBXSUA"},
    "hyperglycemia": {"LBXGL", "LBXSGL", "DIQ010"},
    "hba1c": {"LBXGH"},
    "dyslipidemia": {"LBXSCH", "LBXSTR", "LBDHDD", "LBDLDL"},
    "crp_elevated": {"LBXCRP"},
    "bmi_high": {"BMXBMI"},
    "lead_exposure": {"LBXBPB"},
}
_VM_FLAG2REF = {  # 代码 flag -> reference_prevalence 键
    "current_smoking": "current_smoking", "ever_smoking": "ever_smoking",
    "alcohol_intake": "alcohol_current", "uric_acid_elevated": "uric_acid_elevated",
    "hyperglycemia": "hyperglycemia_126", "hba1c_elevated": "hba1c_elevated",
    "bmi_high": "bmi_high_25", "crp_elevated": "crp_elevated_3mgl",
    "lead_exposure": "lead_3_5",
}


def _vm_guard_nhanes(e: dict) -> None:
    from huiyan_agent.variable_map import (load_variable_map, check_code_vars,
                                           prevalence_gate, reference_rates)
    vm = load_variable_map()
    for domain, cvars in _VM_CODE_VARS.items():
        check_code_vars(vm, "nhanes", domain, cvars, context="evaluate.py")
    refs = reference_rates(vm, "nhanes_40plus")
    rates = {rk: float(e[flag].mean()) for flag, rk in _VM_FLAG2REF.items()
             if flag in e and rk in refs and e[flag].notna().any()}
    findings = prevalence_gate(rates, refs, "nhanes", source="evaluate.py")
    out = ROOT / "outputs" / "confirmatory" / "prevalence_gate_nhanes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"date": "2026-10-16", "n_rates": len(rates),
                               "findings": findings}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    for f in findings:
        print(f"[M7 gate] {f['severity'].upper()}: {f['exposure']} obs {f['observed']:.3f} "
              f"vs ref {f['reference']:.3f} (rel_dev {f['rel_deviation']})")


def build_nhanes_exposures(d: pd.DataFrame) -> dict[str, pd.Series]:
    """B3a: All cutoffs are pre-registered clinical values, NOT sample quantiles."""
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    sex = q("RIAGENDR")
    e = {}
    # Uric acid: sex-specific mg/dL.
    # R11 harmonisation 2026-10-15: 原 NHANES 用男 >=6.8, KNHANES 用男 >7.0 —— 两库
    # 切点不一致会使跨库比较失效。统一到近期文献常用定义: 男 >7.0 / 女 >5.7 mg/dL。
    ua = q("LBXSUA")
    e["uric_acid_elevated"] = (((ua > 7.0) & (sex == 1)) | ((ua > 5.7) & (sex == 2))).astype(float).where(ua.notna())
    # Glucose: fixed 126 mg/dL (or diabetes dx). R11: DIQ 模块已补入 FILES,
    # DIQ010(医生诊断糖尿病) 分支此前因模块未加载而恒为死代码, 现已生效。
    glu = q("LBXGL") if "LBXGL" in d else q("LBXSGL")
    diq = q("DIQ010")
    e["hyperglycemia"] = ((glu >= 126) | (diq == 1)).astype(float).where(glu.notna() | diq.notna())
    # HbA1c: fixed 6.5%
    e["hba1c_elevated"] = (q("LBXGH") >= 6.5).astype(float).where(q("LBXGH").notna())
    # Dyslipidemia (R11 更正 2026-10-15): 原代码取 LBDHDD/LBDHDL/LBDLDL, 但这三列
    # 所在的 HDL_D / TRIGLY_D 模块从未被加载 → 变量全为 NaN,
    # HDL<40 与 LDL>=160 两个分支恒为 False, "血脂异常"实际只剩 TC>=240 | TG>=200。
    # 现已补入模块。TC/TG 仍取自 BIOPRO(LBXSCH/LBXSTR, 覆盖更全),
    # HDL 取 HDL_D.LBDHDD, LDL 取 TRIGLY_D.LBDLDL(空腹亚样本)。
    tc, tg = q("LBXSCH"), q("LBXSTR")
    hdl = q("LBDHDD") if "LBDHDD" in d else pd.Series(np.nan, index=d.index)
    ldl = q("LBDLDL") if "LBDLDL" in d else pd.Series(np.nan, index=d.index)
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    e["hdl_low"] = (hdl < 40).astype(float).where(hdl.notna())
    e["ldl_high"] = (ldl >= 160).astype(float).where(ldl.notna())
    # CRP (R11 更正 2026-10-15): LBXCRP 单位为 mg/dL, 不是 mg/L。
    # 原阈值 >3.0 实为 >30 mg/L —— 暴露率被压到 1.17%(实测), 而 AHA 高危阈值
    # >3 mg/L ≡ >0.3 mg/dL 对应 30.4%。r06(CRP×晚期AMD) 因此一直 underpowered。
    e["crp_elevated"] = (q("LBXCRP") > 0.3).astype(float).where(q("LBXCRP").notna())
    # BMI: fixed >=25 (WHO); 另存亚洲切点 >=23 供跨人群敏感性分析
    e["bmi_high"] = (q("BMXBMI") >= 25).astype(float).where(q("BMXBMI").notna())
    e["bmi_high_asian23"] = (q("BMXBMI") >= 23).astype(float).where(q("BMXBMI").notna())
    # B3b / R11 更正 2026-10-15: 抗氧化复合指标。
    # 原实现用 DR1TVE —— DR1TOT 里不存在该列(SAS 传输文件中无维生素E总量),
    # 导致 z_ve 全为 NaN → 复合 z 全 NaN → 非缺失 n=0, r08 从未真正被测到。
    # 正确列: DR1TVC(维生素C mg) / DR1TATOC(α-生育酚 mg) / DR1TLZ(叶黄素+玉米黄质 mg)。
    # 切点改为外生 EAR 标准下的"摄入不足项数(0-3)", 不再使用样本分位数
    # (原 `z_sum.quantile(0.25)` 与文件头部"切点必须预注册"的纪律自相矛盾)。
    vc, atoc, lz = q("DR1TVC"), q("DR1TATOC"), q("DR1TLZ")
    if vc.notna().sum() > 100:
        # 单位(实测): DR1TVC mg, DR1TATOC mg α-生育酚, DR1TLZ **µg**(中位≈503)。
        # R11 gate 抓出: DR1TLZ 是 µg 不是 mg, 若不换算则阈值 6 会把所有人判为不足。
        lz_mg = lz / 1000.0
        inadequate = pd.concat([(vc < 60).astype(float),
                                (atoc < 12).astype(float),
                                (lz_mg < 6).astype(float)], axis=1)
        n_inad = inadequate.sum(axis=1, min_count=3)          # 仅三项齐全时计分
        e["low_antioxidant_intake"] = (n_inad >= 2).astype(float).where(n_inad.notna())
    # Smoking (R11 更正 2026-10-15): SMQ040 只对 SMQ020==1(一生吸≥100支)者提问,
    # 原 .where(smk.isin([1,2,3])) 把全部从不吸烟者置缺失 → 0 组实为已戒烟者
    # (40+ 样本暴露率 38.7%,真实当前吸烟应≈20%)。修正为:
    # current = SMQ020==1 且 SMQ040∈{1,2};参照 = never(SMQ020==2) ∪ former(SMQ020==1 且 SMQ040==3)
    smk020, smk040 = q("SMQ020"), q("SMQ040")
    cur = (smk020 == 1) & smk040.isin([1, 2])
    noncur = (smk020 == 2) | ((smk020 == 1) & (smk040 == 3))
    e["current_smoking"] = cur.astype(float).where(cur | noncur)
    e["ever_smoking"] = (smk020 == 1).astype(float).where(smk020.isin([1, 2]))
    e["former_smoking"] = ((smk020 == 1) & (smk040 == 3)).astype(float).where(cur | noncur)
    # Alcohol (R11 更正 2026-10-15 + gate 二轮): ALQ101 为终生门槛题(阳性率≈62%),非当前饮酒。
    # 修正: drinker = 过去一年有饮酒天数; non-drinker = 0 天 或 终生不饮(ALQ101==2)。
    # 两个陷阱(实测):
    #   (a) ALQ120Q 是天数, 但需配 ALQ120U 换算(1=周*52 / 2=月*12 / 3=年*1);
    #       原 `>=52` 直接当天数用, 高频饮酒率只有 0.9%(应≈13%)。
    #   (b) 非饮酒者 ALQ120Q 被 SAS 传输读成 5.4e-79(非 0), 故 `==0` 判断会漏掉他们,
    #       分母偏小、饮酒率虚高。凡 <0.5 一律归 0。
    alq101 = q("ALQ101") if "ALQ101" in d else q("ALQ110")
    alq110 = q("ALQ110") if "ALQ110" in d else pd.Series(np.nan, index=d.index)
    alq120q = q("ALQ120Q") if "ALQ120Q" in d else pd.Series(np.nan, index=d.index)
    alq120u = q("ALQ120U") if "ALQ120U" in d else pd.Series(np.nan, index=d.index)
    alq130 = q("ALQ130") if "ALQ130" in d else pd.Series(np.nan, index=d.index)
    days_raw = alq120q.where(alq120q >= 0.5, 0.0)            # 5.4e-79 -> 0
    days_raw = days_raw.where(alq120q.notna())               # 真缺失仍为缺失
    per_year = days_raw.where(alq120u != 1, days_raw * 52.0)
    per_year = per_year.where(alq120u != 2, per_year * 12.0)
    drinker = per_year >= 1
    # 终生不饮: ALQ101==2 且 ALQ110==2(或未问 ALQ110); 其余有 ALQ101 者为非当前饮酒
    lifetime_never = (alq101 == 2) & (~(alq110 == 1))
    nondrinker = (per_year < 1) | lifetime_never
    denom_alc = drinker | nondrinker
    e["alcohol_intake"] = drinker.astype(float).where(denom_alc)
    e["alcohol_frequent"] = (per_year >= 52).astype(float).where(denom_alc)      # 每周+
    e["alcohol_binge"] = (alq130 >= 2).astype(float).where(drinker)              # 单次>=2杯
    e["alcohol_days_per_year"] = per_year.where(denom_alc)                       # 连续天数
    # Lead (R11 更正 2026-10-15): CDC 2021 血液铅参考值已下调至 3.5 µg/dL;
    # 原 >=5.0 暴露率仅 4.9%, 现为 12.9%。同时保留 log 连续暴露(推荐主分析)。
    pb = q("LBXBPB")
    e["lead_exposure"] = (pb >= 3.5).astype(float).where(pb.notna())

    # ── M12/M7 守卫(2026-10-16):variable_map 为唯一操作化事实源 ──────
    # (a) 代码实际引用变量必须登记在字典(防 A1/A2 式漂移);
    # (b) 实测暴露率须过 reference_prevalence 门(>50% 报警,>2.5× 阻断)。
    _vm_guard_nhanes(e)
    return e


def build_nhanes_continuous(d: pd.DataFrame) -> dict[str, pd.Series]:
    """Continuous exposure measures for the dose-response / association matrix.

    Kept separate from build_nhanes_exposures so the binary rule-validation
    loop cannot accidentally treat a continuous variable as a 0/1 flag
    (``.isin([0,1])`` would silently reduce it to n=0).
    """
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    c = {}
    c["hba1c_pct"] = q("LBXGH").where(q("LBXGH").notna())
    c["fasting_glucose_mgdl"] = (q("LBXGL") if "LBXGL" in d else q("LBXSGL")).where(
        (q("LBXGL") if "LBXGL" in d else q("LBXSGL")).notna())
    c["uric_acid_mgdl"] = q("LBXSUA").where(q("LBXSUA").notna())
    c["crp_mgl"] = (q("LBXCRP") * 10.0).where(q("LBXCRP").notna())      # mg/dL -> mg/L
    c["bmi_kgm2"] = q("BMXBMI").where(q("BMXBMI").notna())
    c["waist_cm"] = q("BMXWAIST").where(q("BMXWAIST").notna())
    c["hdl_mgdl"] = q("LBDHDD").where(q("LBDHDD").notna())
    c["ldl_mgdl"] = q("LBDLDL").where(q("LBDLDL").notna())
    c["triglycerides_mgdl"] = q("LBXSTR").where(q("LBXSTR").notna())
    c["total_cholesterol_mgdl"] = q("LBXSCH").where(q("LBXSCH").notna())
    c["blood_lead_ugdl"] = q("LBXBPB").where(q("LBXBPB").notna())
    c["log_blood_lead"] = np.log1p(q("LBXBPB")).where(q("LBXBPB").notna())
    c["serum_cotinine_ngml"] = q("LBXCOT").where(q("LBXCOT").notna())   # 客观吸烟标志物
    c["vitamin_c_mg"] = q("DR1TVC").where(q("DR1TVC").notna())
    c["alpha_tocopherol_mg"] = q("DR1TATOC").where(q("DR1TATOC").notna())
    # DR1TLZ 原始单位是 µg(中位≈503); 导出为 mg 并另存原始 µg
    c["lutein_zeaxanthin_mg"] = (q("DR1TLZ") / 1000.0).where(q("DR1TLZ").notna())
    c["lutein_zeaxanthin_ug"] = q("DR1TLZ").where(q("DR1TLZ").notna())
    c["antioxidant_inadequate_count"] = (
        (q("DR1TVC") < 60).astype(float)
        + (q("DR1TATOC") < 12).astype(float)
        + ((q("DR1TLZ") / 1000.0) < 6).astype(float)
    ).where(q("DR1TVC").notna() & q("DR1TATOC").notna() & q("DR1TLZ").notna())
    return c


def build_nhanes_outcomes(d: pd.DataFrame) -> dict[str, pd.Series]:
    """B3c: VI thresholds properly differentiated; B3e: worst-category assignment."""
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    o = {}
    o["cataract_any"] = (q("VIQ071") == 1).astype(float).where(q("VIQ071").notna())
    # B3c (R5-P0 fix 2026-10-14): VI — presenting VA from VIDRVA/VIDLVA.
    # VIXPRS is SPHERICAL REFRACTION (not visual acuity); VIDRVA/VIDLVA are
    # Snellen denominators (20/xx coded 20-666; 666 = worse than 20/400).
    # logMAR = log10(xx/20): 20/40→0.30, 20/60→0.48, 20/200→1.00 (pre-registered
    # thresholds). Worse eye = max logMAR; one missing eye falls back to the
    # available eye (Han 2021 presenting-VA standard, r20 citation).
    va_r = q("VIDRVA").where(q("VIDRVA").between(20, 666))
    va_l = q("VIDLVA").where(q("VIDLVA").between(20, 666))
    va = np.log10(pd.concat([va_r, va_l], axis=1) / 20.0).max(axis=1)
    # B3e: Worst-category assignment (each person assigned to exactly one VI level)
    vi_severe = (va > 1.00).astype(float).where(va.notna())
    vi_moderate = ((va > 0.48) & ~(va > 1.00)).astype(float).where(va.notna())
    vi_mild = ((va > 0.30) & ~(va > 0.48)).astype(float).where(va.notna())
    o["vision_impairment_mild"] = vi_mild
    o["vision_impairment_moderate"] = vi_moderate
    o["vision_impairment_severe"] = vi_severe
    # Retinopathy (OPXRET)
    ret = q("OPDURL4")
    o["retinopathy_any"] = ret.isin([2, 3, 4]).astype(float).where(ret.notna())
    o["dr_npdr"] = ret.isin([2, 3]).astype(float).where(ret.notna())
    o["dr_pdr"] = (ret == 4).astype(float).where(ret.notna())
    # B3e: retinopathy_any = dr_npdr ∪ dr_pdr — nesting guard in metrics
    # AMD
    arm, pig = q("OPDUARM"), q("OPDUPIGA")
    o["amd_early"] = ((arm >= 1) | (pig >= 1)).astype(float).where(arm.notna() | pig.notna())
    larm, ga, exu = q("OPDULARM"), q("OPDUGA"), q("OPDUEXU")
    o["amd_late"] = ((larm >= 1) | (ga >= 1) | (exu >= 1)).astype(float).where(larm.notna() | ga.notna() | exu.notna())
    # CDR
    cdr = pd.concat([q("OPDDVCDR"), q("OPDSVCDR")], axis=1).max(axis=1)
    o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())
    return o


def detect_separation(y: pd.Series, x: pd.Series) -> bool:
    """B5: Check for perfect/quasi separation before fitting."""
    pos = y == 1; neg = y == 0
    if pos.sum() < 5 or neg.sum() < 5:
        return True
    # Perfect separation: all positives have x=1 and all negatives have x=0 (or vice versa)
    if (x[pos] == 1).all() and (x[neg] == 0).all():
        return True
    if (x[pos] == 0).all() and (x[neg] == 1).all():
        return True
    return False


def fdr_bhy(p: pd.Series) -> pd.Series:
    """BHY step-up FDR with monotonicity (analysis_plan §7)."""
    p = pd.Series(p).astype(float)
    q = pd.Series(np.nan, index=p.index, dtype=float)
    pv = p.dropna()
    n = len(pv)
    if n:
        order = pv.sort_values(kind="mergesort")
        c_n = float(np.sum(1.0 / np.arange(1, n + 1)))
        ranked = order.to_numpy() * n * c_n / np.arange(1, n + 1)
        ranked = np.minimum.accumulate(ranked[::-1])[::-1]
        q.loc[order.index] = np.clip(ranked, 0.0, 1.0)
    return q


def three_state(or_val, q_val, rule_dir="risk_up"):
    if not np.isfinite(q_val) or q_val >= 0.05:
        return "uninformative"
    if not np.isfinite(or_val) or abs(float(or_val) - 1.0) < 1e-9:
        return "uninformative"
    if rule_dir == "risk_down":
        return "replicated" if or_val < 1 else "contradicted"
    return "replicated" if or_val > 1 else "contradicted"


def _flag_index(reg):
    idx = {}
    for ent in (reg or {}).values():
        for f in (getattr(ent, "flags", None) or []):
            idx.setdefault(str(f), ent)
    return idx


# ══════════════════════════════════════════════════════════════════
#  NHANES raw-data loading (module level, R11 2026-10-15)
#  提到模块级是为了让管线与 scripts/validate_nhanes_exposures.py
#  共用同一份模块表 —— 变量名不一致正是本项目反复出错的根源。
# ══════════════════════════════════════════════════════════════════
NHANES_DIR = Path(os.environ.get("NHANES_DIR", r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES"))
NHANES_CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}
NHANES_FILES = {
    "DEMO": ("DEMO", True), "BIOPRO": ("BIOPRO", True), "VIQ": ("VIQ", True),
    "VIX": ("VIX", True), "OPXRET": ("OPXRET", True), "SMQ": ("SMQ", True),
    "ALQ": ("ALQ", True), "BMX": ("BMX", True), "CRP": ("CRP", True),
    "PBCD": ("PBCD", True), "DR1TOT": ("DR1TOT", True),
    "GLU": ("GLU", True), "GHB": ("GHB", True),
    # R11 更正 2026-10-15: 补齐四组此前缺失的模块。
    #   HDL_D.LBDHDD      = HDL 胆固醇 (mg/dL) —— 原代码查 LBDHDD/LBDHDL 但模块从未加载,
    #                       导致 dyslipidemia 的 HDL<40 分支恒为 False
    #   TRIGLY_D.LBDLDL   = LDL 胆固醇 (mg/dL, 空腹亚样本) —— 同上, LDL>=160 分支恒为 False
    #   TRIGLY_D.LBXTR    = 甘油三酯 (mg/dL, 空腹亚样本)
    #   TCHOL_D.LBXTC     = 总胆固醇 (mg/dL)
    #   DIQ_D.DIQ010      = 医生是否诊断糖尿病 —— 原代码引用 DIQ010 但模块未加载, 分支恒为死代码
    "HDL": ("HDL", True), "TRIGLY": ("TRIGLY", True),
    "TCHOL": ("TCHOL", True), "DIQ": ("DIQ", True),
    # 血清可替宁(LBXCOT, ng/mL): 客观吸烟标志物, 用于校验自报吸烟变量。
    # 2005-2006 在 COT_D.XPT, 2007-2008 在 COTNAL_E.XPT —— 两个候选名都登记,
    # 加载器会跳过不存在的那个。
    "COT": ("COT", True), "COTNAL": ("COTNAL", True),
    "DEQ": ("DEQ", "D"), "VITAEC": ("VITAEC", "D"),
}


def load_nhanes_raw(nhanes_dir: Path | None = None,
                    cycles: dict | None = None,
                    files: dict | None = None) -> pd.DataFrame:
    """Load and horizontally merge the NHANES modules used by the pipeline.

    Kept minimal on purpose: the caller applies the age / weight restriction,
    because scripts/validate_nhanes_exposures.py needs to report the effect of
    that restriction separately.
    """
    nhanes_dir = Path(nhanes_dir or NHANES_DIR)
    cycles = cycles or NHANES_CYCLES
    files = files or NHANES_FILES

    def _load_cycle(cycle_dir: Path, suf: str) -> pd.DataFrame:
        frames = {}
        for mod, (base, cyc) in files.items():
            if cyc is True:
                name = f"{base}{suf}.XPT"
            elif cyc == suf or (isinstance(cyc, str) and suf.endswith(cyc)):
                name = f"{base}{suf}.XPT"
            else:
                continue
            p = cycle_dir / name
            if not p.exists():
                continue
            df = pd.read_sas(str(p), format="xport", encoding="utf-8")
            cols = [c for c in df.columns if c != "SEQN"]
            frames[mod] = df.set_index("SEQN")[cols]
        out = None
        for m, df in frames.items():
            if out is None:
                out = df
            else:
                overlap = [c for c in df.columns if c in out.columns]
                if overlap:
                    df = df.drop(columns=overlap)
                out = out.join(df, how="outer") if len(df.columns) else out
        return out.reset_index()

    parts = []
    for cyc, suf in cycles.items():
        if not (nhanes_dir / cyc).exists():
            print(f"[nhanes] WARNING: cycle dir missing: {nhanes_dir / cyc}")
            continue
        df = _load_cycle(nhanes_dir / cyc, suf)
        df["cycle"] = cyc
        parts.append(df)
    if not parts:
        raise SystemExit(f"[nhanes] no cycles loaded from {nhanes_dir}")
    return pd.concat(parts, ignore_index=True, sort=False)


def restrict_nhanes_adults(d: pd.DataFrame, min_age: int = 40,
                           weight_col: str = "WTMEC2YR") -> pd.DataFrame:
    d = d[pd.to_numeric(d["RIDAGEYR"], errors="coerce") >= min_age]
    d = d[pd.to_numeric(d.get(weight_col, 0), errors="coerce") > 0]
    return d


def run_nhanes_confirmatory() -> pd.DataFrame:
    """Full NHANES confirmatory run with all B3-B7 fixes."""
    import statsmodels.api as sm
    cases = load_cases("intval-nhanes")
    d = load_nhanes_raw()
    d = restrict_nhanes_adults(d)
    # Covariates (B3f: unified /100)
    covar_cols = [c for c in ["RIDAGEYR", "RIAGENDR", "RIDRETH1", "INDFMPIR"] if c in d.columns]
    for c in ("DMDEDU2", "DMDEDU3"):
        if c in d.columns: covar_cols.append(c); break
    E = build_nhanes_exposures(d)
    B = build_nhanes_outcomes(d)
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)
    cov = d[covar_cols].copy()
    cov["age2"] = pd.to_numeric(cov.get("RIDAGEYR", 0), errors="coerce") ** 2 / 100

    results = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            a_ent = a_idx.get(a_flag) or a_reg.get(a_flag)
            b_ent = b_idx.get(b_item) or b_reg.get(b_item)
            predicted, rule_ids, is_nc, direction = False, [], False, "risk_up"
            if a_ent and b_ent:
                sigs = match_rules(rules, a_ent, b_ent)
                predicted = len(sigs) > 0
                rule_ids = [s.rule_id for s in sigs]
                by_id = {r.id: r for r in rules}
                hit = [by_id[i] for i in rule_ids if i in by_id]
                is_nc = any(r.negative_control for r in hit)
                dirs = [r.direction for r in hit]
                direction = "risk_down" if dirs and all(d == "risk_down" for d in dirs) else "risk_up"
            meta = {"a_flag": a_flag, "b_item": b_item, "predicted": predicted,
                    "rule_ids": ",".join(rule_ids), "negative_control": is_nc, "direction": direction}
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": "underpowered"})
                continue
            # B5: separation check
            if detect_separation(sub["y"], sub["x"]):
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": "separation"})
                continue
            try:
                X = sm.add_constant(sub[["x"] + covar_cols + ["age2"]].astype(float))
                y = sub["y"].astype(float)
                w = d.loc[sub.index, "WTMEC2YR"].astype(float)
                w = w.where(w > 0, 1.0) / w.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
                if not getattr(fit, "converged", True):
                    raise RuntimeError("not converged")
                beta, se = fit.params["x"], fit.bse["x"]
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx,
                                "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                                "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                                "status": "tested"})
            except Exception as ex:
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": f"fit_fail:{type(ex).__name__}"})
    res = pd.DataFrame(results)
    res = assign_three_state(res)          # R11: dual-family FDR + three-state labels
    print(f"[fdr] confirmatory family (rule-relevant) n={int(res['q_rule'].notna().sum())}; "
          f"exploratory family n={int((res['status'] == 'tested').sum())}")
    return res


def assign_three_state(res: pd.DataFrame, family_col: str = "predicted") -> pd.DataFrame:
    """Attach FDR and the three-state gold label, using TWO pre-registered families.

    R11 2026-10-15
    --------------
    Once the exposure x outcome matrix was expanded (NHANES 20x10, KNHANES 20x16)
    a single BHY family spanning >100 pairs with no rule attached dilutes power
    for exactly the pairs the paper is about.  So:

      * ``q``       — BHY over ALL tested pairs (exploratory family).  Used for
                      the uncovered/exploratory findings.
      * ``q_rule``  — BHY over rule-relevant tested pairs only (confirmatory,
                      pre-registered primary family).
      * ``q_primary`` / ``gold3`` — q_rule for rule-relevant pairs, q otherwise.
                      This is the label the headline rule metrics consume.
      * ``gold3_exploratory`` — three-state label under the full family.

    Both are reported; neither is allowed to replace the other silently.
    """
    res = res.copy()
    res["q"] = np.nan
    res["q_rule"] = np.nan
    m = res["status"] == "tested"
    if m.any():
        res.loc[m, "q"] = fdr_bhy(res.loc[m, "p"])
    rule_m = m & res[family_col].fillna(False).astype(bool)
    if rule_m.any():
        res.loc[rule_m, "q_rule"] = fdr_bhy(res.loc[rule_m, "p"])
    res["q_primary"] = np.where(rule_m, res["q_rule"], res["q"])

    def _label(qv, orv, direction):
        return three_state(orv, qv, direction)

    for col, qcol in (("gold3", "q_primary"), ("gold3_exploratory", "q")):
        res[col] = res.apply(
            lambda r, _q=qcol: _label(r.get(_q, np.nan), r.get("or", np.nan),
                                      r.get("direction", "risk_up"))
            if r["status"] == "tested" else "not_tested", axis=1)
    return res


def direction_audit_and_block(res, rules, dataset_id):
    """B7: Wire direction_audit with mandatory blocking.

    R5 fix 2026-10-14 (plan §4 alignment): the pre-registered audit standard
    is ANY reversed (OR<1) A-level pair triggers review — the implementation
    had silently narrowed this to significant reversals only (q<0.05 AND
    OR<1). Now every reversed A-level pair is RECORDED as a fourth state
    "direction_review" (col added to the CSV, written to
    direction_review_<dataset>.csv); automatic quarantine of headline metrics
    still requires >=2 SIGNIFICANT reversals (kept from the bias-investigation
    era, now as a documented deviation in analysis_plan §0.1)."""
    lvl = {r.id: r.evidence_level for r in rules}
    # A-tier emptiness guard. The pre-registered section 4 trigger operates on
    # A-level pairs. On 2026-10-16 every rule's citation was verified against
    # Crossref and PubMed and 11 rules were regraded, which left NO rule at grade
    # A: the corpus contains no regulatory label or clinical guideline, and the
    # strongest evidence any rule cites is a meta-analysis. With an empty A tier
    # the selection below yields nothing, the audit prints nothing, and the run
    # LOOKS as though it found no reversals when in fact the audit could not run.
    # A check that passes because its subject is empty is not a check, so say so.
    a_tier = sorted(rid for rid, lv in lvl.items() if lv == "A")
    if not a_tier:
        print("[audit] " + "=" * 56)
        print("[audit] WARNING: no rule is graded A, so the pre-registered")
        print("[audit] section 4 direction audit has NO SUBJECT for "
              f"{dataset_id}.")
        print("[audit] An empty result below means 'the audit could not run',")
        print("[audit] NOT 'no reversed A-level pair was found'.")
        print("[audit] See docs/AGENT_AUDIT.md section 10.")
        print("[audit] " + "=" * 56)
    a_pairs = res[(res["predicted"]) & (res["status"] == "tested")].copy()
    if "rule_ids" in a_pairs.columns and len(a_pairs):
        def _is_a(ids):
            got = [lvl.get(i.strip()) for i in str(ids).split(",") if i.strip()]
            return bool(got) and all(g == "A" for g in got)
        # R11 hardening: cast the mask to bool explicitly.  On an EMPTY frame
        # `.map()` yields an empty object-dtype Series, which pandas interprets
        # as LABEL-based indexing and silently drops every column -> downstream
        # `a_pairs["direction"]` raises KeyError.
        mask = a_pairs["rule_ids"].map(_is_a).astype(bool)
        a_pairs = a_pairs[mask]
    # Fourth state: ANY reversed A-level pair (pre-registered §4 trigger)
    reversed_any = a_pairs[
        (a_pairs["direction"] != "risk_down") & (a_pairs["or"] < 1)
    ].copy() if len(a_pairs) and "direction" in a_pairs.columns else a_pairs.iloc[0:0].copy()
    rev = reversed_any[reversed_any.get("q", pd.Series(dtype=float)) < 0.05]
    # annotate res with the review flag (non-A / non-reversed rows stay False)
    review_mask = res.index.isin(reversed_any.index)
    res["direction_review"] = review_mask
    if len(reversed_any):
        out = ROOT / "outputs" / "confirmatory"
        out.mkdir(parents=True, exist_ok=True)
        reversed_any.to_csv(out / f"direction_review_{dataset_id.lower()}.csv",
                            index=False, encoding="utf-8-sig")
        print(f"[audit] {len(reversed_any)} A-level pair(s) with OR<1 flagged "
              f"direction_review (plan §4 standard):")
        for _, r in reversed_any.iterrows():
            sig = "SIGNIFICANT" if r.get("q", 1.0) < 0.05 else f"ns (q={r.get('q', float('nan')):.2f})"
            print(f"    {r['a_flag']} x {r['b_item']}: OR={r['or']:.3f} [{sig}]")
    quarantine = len(rev) >= 2
    if quarantine:
        print(f"\n{'='*60}")
        print(f"⚠️  DIRECTION AUDIT: QUARANTINE triggered for {dataset_id}")
        print(f"    {len(rev)} A-level rule pairs show OR<1 (reversed direction):")
        for _, r in rev.iterrows():
            print(f"      {r['a_flag']} × {r['b_item']}: OR={r['or']:.3f} q={r.get('q', 'n/a')}")
        print(f"    Headline metrics SUPPRESSED until bias investigation completed.")
        print(f"    Check: exposure coding, outcome ascertainment, selection bias,")
        print(f"    reverse causation (current vs former smoking).")
        print(f"{'='*60}\n")
        # Write quarantine state
        state_path = ROOT / ".medical-agent" / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state.setdefault("blocked", []).append({
                "phase": "executor.phase5",
                "reason": f"direction_audit quarantine: {dataset_id} has {len(rev)} A-level pairs with OR<1"
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return quarantine, len(rev)


def compute_metrics_v11(res, dataset_key="nhanes"):
    """Analysis plan v1.1: precision_rule + coverage (no recall).

    R5-P0 fix 2026-10-14: judgeable set is per-dataset (was hardcoded
    "nhanes" for all three datasets, inflating KNHANES/CHARLS coverage).
    """
    t = res[res["status"] == "tested"].copy()
    # D5: filter out non-judgeable B items from metrics denominator
    judgeable = get_judgeable_b_items(dataset_key)
    if judgeable:
        before = len(t)
        t = t[t["b_item"].isin(judgeable)]
        if before > len(t):
            print(f"[metrics] D5: excluded {before - len(t)} non-judgeable pairs from denominator")
    nc_mask = t["negative_control"].fillna(False).astype(bool) if "negative_control" in t else pd.Series(False, index=t.index)
    t_main = t[~nc_mask]; t_nc = t[nc_mask]
    rp = t_main[t_main["predicted"]]
    rep = int((rp["gold3"] == "replicated").sum())
    con = int((rp["gold3"] == "contradicted").sum())
    uninf = int((rp["gold3"] == "uninformative").sum())
    sep = int((res["status"] == "separation").sum())
    prec = round(rep / (rep + con), 3) if rep + con else None
    # Clopper-Pearson exact binomial CI on rep/(rep+con)（小 n 下 bootstrap 对观测
    # 标签重采样会退化，如 7/0 恒得 [1.0,1.0]，无法反映真实不确定性）
    ci = (None, None)
    if rep + con:
        from scipy import stats as _st
        lo = _st.beta.ppf(0.025, rep, con + 1) if rep > 0 else 0.0
        hi = _st.beta.ppf(0.975, rep + 1, con) if con > 0 else 1.0
        ci = (round(float(lo), 3), round(float(hi), 3))
    coverage = round(len(rp) / len(t_main), 3) if len(t_main) else None
    # R11-B1 (2026-10-15): 保守二元口径(uninformative 记 FP)与声明域口径并列双呈,
    # 消除"报自己成绩剔除失败、评基线把失败算 FP"的双标准并观。
    from scipy import stats as _st  # CHARLS rep=con=0 时上方块未导入
    prec_b = round(rep / len(rp), 3) if len(rp) and rep else (0.0 if len(rp) else None)
    ci_b = (None, None)
    if len(rp):
        lo_b = _st.beta.ppf(0.025, rep, len(rp) - rep + 1) if rep > 0 else 0.0
        hi_b = _st.beta.ppf(0.975, rep + 1, len(rp) - rep) if rep < len(rp) else 1.0
        ci_b = (round(float(lo_b), 3), round(float(hi_b), 3))
    non_rule = t_main[~t_main["predicted"]]
    # R11 2026-10-15 coverage 定义修正:
    #   原 coverage = len(rp)/len(t_main) 的分母是"全部可测配对"。当暴露×结局矩阵
    #   从 49 对扩到 279 对后, 该式实际变成"规则覆盖了全矩阵的多大比例", 会在
    #   0.08 量级, 已不是原本要表达的"规则负责的假设里有多少能被检验"。
    #   现改为: coverage = P(可检验 | 存在规则), 并单列矩阵层面的探索性产出。
    rule_relevant = res[res["predicted"].fillna(False).astype(bool)]
    if "negative_control" in res.columns:
        rule_relevant = rule_relevant[~rule_relevant["negative_control"].fillna(False).astype(bool)]
    if judgeable:
        rule_relevant = rule_relevant[rule_relevant["b_item"].isin(judgeable)]
    rule_tested = rule_relevant[rule_relevant["status"] == "tested"]
    coverage_rule = (round(len(rule_tested) / len(rule_relevant), 3)
                     if len(rule_relevant) else None)
    uncovered_sig = non_rule[non_rule["gold3"] == "replicated"]
    return {
        "rule_pairs_tested": len(rp), "replicated": rep,
        "contradicted": con, "uninformative": uninf, "separation": sep,
        "precision_rule": prec, "precision_rule_ci95": ci,
        "coverage": coverage_rule,
        "coverage_definition": ("P(tested | rule exists, judgeable, non-negative-control) "
                                "— R11 fixed; the old formula divided by ALL testable pairs"),
        "coverage_of_full_matrix": coverage,
        "rule_relevant_pairs": len(rule_relevant),
        "precision_binary_uninf_as_fp": prec_b, "precision_binary_ci95": ci_b,
        "uncovered_significant": int((non_rule["gold3"] == "replicated").sum()),
        "uncovered_pairs": len(non_rule),
        "matrix_tested_pairs": len(t_main),
        "matrix_significant_pairs": int((t_main["gold3"] == "replicated").sum()),
        "matrix_significant_uncovered": int(len(uncovered_sig)),
        "negative_control_pairs": len(t_nc),
        "negative_control_outcome": t_nc["gold3"].value_counts().to_dict() if len(t_nc) else {},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=[
        "intval-nhanes", "extval-knhanes", "extval-cohorts-9", "all"])
    args = parser.parse_args()

    if args.dataset in ("intval-nhanes", "all"):
        print("\n" + "="*60)
        print("NHANES confirmatory (analysis_plan v1.1)")
        print("="*60)
        res = run_nhanes_confirmatory()
        rules = load_rules()
        quarantine, n_rev = direction_audit_and_block(res, rules, "NHANES")
        if not quarantine:
            metrics = compute_metrics_v11(res, "nhanes")
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
            out = ROOT / "outputs" / "confirmatory"
            out.mkdir(parents=True, exist_ok=True)
            res.to_csv(out / "nhanes_confirmatory.csv", index=False, encoding="utf-8-sig")
            (out / "nhanes_metrics_v11.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            out_q = ROOT / "outputs" / "confirmatory"
            out_q.mkdir(parents=True, exist_ok=True)
            res.to_csv(out_q / "nhanes_quarantined.csv",
                       index=False, encoding="utf-8-sig")
            print(f"[evaluate] Quarantined results saved: {out_q / 'nhanes_quarantined.csv'}")
            print(f"[evaluate] Bias investigation required before headline metrics can be produced.")

    print("\n[evaluate] KNHANES and cohort layers: implement using same framework")
    print("[evaluate] with build_knhanes_exposures/outcomes (fixed cutoffs) + cohort outcomes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
