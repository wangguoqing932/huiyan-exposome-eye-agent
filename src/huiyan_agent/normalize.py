"""normalize — 暴露/眼病名称 → 注册表规范记录的解析与注册表加载。

数据源：data/seed/entities_a.csv（暴露组及常见风险暴露）与
data/seed/entities_b.csv（眼科降眼压及相关专科眼病），由 Phase 1 构建。
多列字段以分号（; 或 ；）分隔；别名大小写不敏感。

公开 API（app/streamlit_app.py 依赖此契约）::
    load_entity_a_registry() -> dict[str, EntityA]   # entity_a_id → 记录
    load_entity_b_registry() -> dict[str, EntityB]   # entity_b_id → 记录
    resolve_entity_a(name)   -> EntityA | None       # 主名/别名 → 记录
    resolve_entity_b(name)   -> EntityB | None
    clear_cache()                                    # 清空注册表缓存
"""
from __future__ import annotations

import csv
from pathlib import Path

from .schemas import EntityA, EntityB

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_A_CACHE: dict[str, dict[str, EntityA]] = {}
_B_CACHE: dict[str, dict[str, EntityB]] = {}


def _split_multi(value: str | None) -> list[str]:
    """分号分隔的多值字段 → 列表（兼容中英文分号，去空白，去空项）。"""
    if not value:
        return []
    parts = value.replace("；", ";").split(";")
    return [p.strip() for p in parts if p.strip()]


def _default_path(kind: str) -> Path:
    name = "entities_a.csv" if kind == "a" else "entities_b.csv"
    return _PROJECT_ROOT / "data" / "seed" / name


def load_entity_a_registry(path: str | Path | None = None) -> dict[str, EntityA]:
    """加载实体 A（暴露）注册表；路径缺省取项目 data/seed/entities_a.csv。"""
    p = Path(path) if path else _default_path("a")
    cache_key = str(p)
    if cache_key in _A_CACHE:
        return _A_CACHE[cache_key]
    registry: dict[str, EntityA] = {}
    if not p.exists():
        raise FileNotFoundError(f"Registry CSV not found: {p}")
    if True:
        with p.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                fid = (row.get("exposure_id") or row.get("entity_a_id") or "").strip()
                if not fid:
                    continue
                registry[fid] = EntityA(
                    entity_a_id=fid,
                    primary_name=(row.get("primary_name") or "").strip(),
                    aliases=_split_multi(row.get("aliases")),
                    category=(row.get("category") or "").strip(),
                    active_mechanisms=_split_multi(row.get("active_mechanisms")),
                    flags=[f.lower() for f in _split_multi(row.get("flags"))],
                    evidence_sources=_split_multi(row.get("evidence_sources")),
                )
    _A_CACHE[cache_key] = registry
    return registry


def load_entity_b_registry(path: str | Path | None = None) -> dict[str, EntityB]:
    """加载实体 B（眼病）注册表；路径缺省取项目 data/seed/entities_b.csv。"""
    p = Path(path) if path else _default_path("b")
    cache_key = str(p)
    if cache_key in _B_CACHE:
        return _B_CACHE[cache_key]
    registry: dict[str, EntityB] = {}
    if not p.exists():
        raise FileNotFoundError(f"Registry CSV not found: {p}")
    if True:
        with p.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                bid = (row.get("entity_b_id") or row.get("disease_id") or "").strip()
                if not bid:
                    continue
                registry[bid] = EntityB(
                    entity_b_id=bid,
                    generic_name=(row.get("generic_name") or "").strip(),
                    aliases=_split_multi(row.get("aliases")),
                    category=(row.get("category") or "").strip(),
                    flags=[f.lower() for f in _split_multi(row.get("flags"))],
                    pathology=_split_multi(row.get("pathology")),
                    grading_source=_split_multi(row.get("grading_source")),
                    judged_in=(row.get("judged_in", "").strip().lower()
                                              in ("1", "true", "yes", "y")),
                    label_source=(row.get("label_source") or "").strip(),
                )
    _B_CACHE[cache_key] = registry
    return registry


def _resolve(name: str, registry: dict, primary_key: str, alias_attr: str):
    """解析顺序：精确 id → 主名（大小写不敏感）→ 别名 → 前缀截断兜底。

    安全纪律（v2.2.1，2026-10-09 审计 B1v2 臂B）：旧版包含式兜底
    （`pn in ql or ql in pn` 双向子串、无最小长度）会把 1 字符残缺输入
    静默解析到错误实体（实例：山楂→"山"→山药→无旗标→LOW 假安心）。
    现仅允许「查询串为官方名前缀且长度 ≥2」的截断输入；其余一律 None
    （上游按范围外拒识 → UNKNOWN）。
    """
    if not name:
        return None
    q = str(name).strip()
    if q in registry:
        return registry[q]
    ql = q.lower()
    for rec in registry.values():
        if getattr(rec, primary_key, "").strip().lower() == ql:
            return rec
    for rec in registry.values():
        aliases = [a.lower() for a in getattr(rec, alias_attr, [])]
        if ql in aliases:
            return rec
    # 兜底（v2.2.1 安全化）：仅两条信息充分的方向——
    #   a) 官方名完整出现于查询串（如"甘草片"含"甘草"）
    #   b) 查询串为官方名 ≥2 字前缀（如"华法"→华法林，截断输入）
    # 封死方向：短查询串含于官方名（如"山"⊂"山药"→错实体沉默低警）
    if len(ql) >= 2:
        for rec in registry.values():
            pn = getattr(rec, primary_key, "").strip().lower()
            if pn and (pn in ql or pn.startswith(ql)):
                return rec
    return None


def resolve_entity_a(name: str, registry: dict[str, EntityA] | None = None) -> EntityA | None:
    """暴露名（主名/别名/部分匹配）→ EntityA 记录；找不到返回 None。"""
    reg = registry if registry is not None else load_entity_a_registry()
    return _resolve(name, reg, "primary_name", "aliases")


def resolve_entity_b(name: str, registry: dict[str, EntityB] | None = None) -> EntityB | None:
    """眼病名（主名/别名/部分匹配）→ EntityB 记录；找不到返回 None。"""
    reg = registry if registry is not None else load_entity_b_registry()
    return _resolve(name, reg, "generic_name", "aliases")


def clear_cache() -> None:
    """清空注册表缓存（注册表文件被更新后调用）。"""
    _A_CACHE.clear()
    _B_CACHE.clear()
