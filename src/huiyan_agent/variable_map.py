#!/usr/bin/env python
"""configs/variable_map.yaml 的运行时加载器(MUSTFIX M12/M7,2026-10-16)。

此前 variable_map.yaml 只是"对齐过的文档"——没有任何脚本程序化消费它,
A1/A2 类"代码与字典漂移"无守卫。本模块使字典成为可执行事实源:

  load_variable_map()   解析 + schema 校验(缺字段 fail-loud)
  vars_for(ds, domain)  某数据集某暴露/结局的变量清单(一致性守卫用)
  reference_rates(ds)   参考患病率(M7 运行时门用)
  check_code_vars(...)  代码实际使用的变量 ⊆ 字典登记变量,漂移即抛错

纪律(与字典 meta 段一致):切点必须外生;偏离参考率 >50% 报警、>2.5× 阻断。
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "configs" / "variable_map.yaml"

DATASETS = ("nhanes", "knhanes", "charls", "charls2015", "cohorts")
WARN_REL_DEV = 0.50   # 相对偏离>50%:报警入册
FAIL_REL_DEV = 1.50   # 相对偏离>150%(即 >2.5×):阻断(HUIYAN_VM_FAIL_OVERRIDE=1 可豁免并记录)


def load_variable_map(path: str | Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_PATH
    if not p.exists():
        raise FileNotFoundError(f"variable_map 不存在: {p}(M12:操作化唯一事实源缺失)")
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    for sec in ("exposures", "outcomes", "reference_prevalence"):
        if not isinstance(d.get(sec), dict) or not d[sec]:
            raise ValueError(f"variable_map.{sec} 缺失或为空")
    for domain, spec in {**d["exposures"], **d["outcomes"]}.items():
        if not isinstance(spec, dict) or not spec.get("concept"):
            raise ValueError(f"variable_map: {domain} 缺 concept")
        for ds, entry in spec.items():
            if ds in DATASETS:
                if not isinstance(entry, dict):
                    raise ValueError(f"variable_map: {domain}.{ds} 条目须为 dict")
                if entry.get("status") == "unmeasurable":
                    continue  # 显式声明的不可测(须带 note)
                if not (_collect_names(entry) or entry.get("vars")):
                    raise ValueError(f"variable_map: {domain}.{ds} 无任何变量登记"
                                     f"(显式不可测请写 status: unmeasurable + note)")
    return d


def _collect_names(node) -> set[str]:
    """深度收集任意嵌套结构里的变量名。

    兼容两族命名: NHANES 全大写(SMQ040/LBXSUA)与 KNHANES 混合大小写
    (HE_Uacid/HE_glu/E_Gr_p)——凡含下划线分段或全大写的标识符均视为变量。
    """
    found: set[str] = set()
    pat = re.compile(r"\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*\b|\b[A-Z][A-Z0-9]{2,}\b")
    if isinstance(node, str):
        found.update(pat.findall(node))
    elif isinstance(node, dict):
        for v in node.values():
            found |= _collect_names(v)
    elif isinstance(node, (list, tuple, set)):
        for v in node:
            found |= _collect_names(v)
    return found


def vars_for(vm: dict, dataset: str, domain: str) -> set[str]:
    """某数据集某领域登记的变量名集合(嵌套结构与 derive 字符串深度扫描)。"""
    spec = (vm.get("exposures") or {}).get(domain) or (vm.get("outcomes") or {}).get(domain)
    if not spec or dataset not in spec:
        return set()
    return _collect_names(spec[dataset] or {})


def check_code_vars(vm: dict, dataset: str, domain: str, code_vars: set[str],
                    context: str = "") -> None:
    """守卫:代码实际使用的变量必须登记在字典中,否则抛错(防 A1/A2 式漂移)。"""
    registered = vars_for(vm, dataset, domain)
    unregistered = {v for v in code_vars if v not in registered and not v.startswith("RID") and not v.startswith("WT")}
    if unregistered:
        raise ValueError(
            f"[M12 守卫] {context or domain}: 代码使用变量 {sorted(unregistered)} "
            f"未登记于 variable_map.{dataset} 的 {domain} 条目——先更新字典再改代码")


def reference_rates(vm: dict, dataset: str) -> dict:
    vals = ((vm.get("reference_prevalence") or {}).get("values") or {})
    return dict(vals.get(dataset) or {})


def prevalence_gate(rates: dict, refs: dict, dataset: str, source: str = "") -> list[dict]:
    """M7 运行时门:实际暴露率 vs 参考率。>50% 偏离报警;>2.5× 阻断(可 env 豁免)。"""
    import os
    findings: list[dict] = []
    for name, ref in (refs or {}).items():
        rate = rates.get(name)
        if rate is None or ref in (None, 0):
            continue
        rel = abs(rate - ref) / ref
        finding = {"dataset": dataset, "exposure": name, "observed": round(float(rate), 4),
                   "reference": ref, "rel_deviation": round(float(rel), 3),
                   "severity": "warn" if rel > WARN_REL_DEV else "ok"}
        if rel > FAIL_REL_DEV:
            finding["severity"] = "fail"
            findings.append(finding)
            if os.environ.get("HUIYAN_VM_FAIL_OVERRIDE") == "1":
                finding["overridden"] = True
            else:
                raise ValueError(
                    f"[M7 门] {dataset} 暴露 {name} 实测率 {rate:.3f} 偏离参考 {ref:.3f} "
                    f"超 2.5×(rel={rel:.2f})——操作化可疑,阻断({source})。"
                    f"确属真实且已核码本者,设 HUIYAN_VM_FAIL_OVERRIDE=1 豁免并留痕。")
        elif rel > WARN_REL_DEV:
            findings.append(finding)
    return findings
