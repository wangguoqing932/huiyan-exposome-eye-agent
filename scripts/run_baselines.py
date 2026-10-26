#!/usr/bin/env python
"""Run 4 baselines for A2 handoff deliverable.

Baselines:
  1. pure_llm      — LLM answers without retrieval
  2. naive_rag     — EvidenceStore keyword retrieval + LLM
  3. lightrag      — LightRAG KG retrieval + LLM (requires index)
  4. full_system   — Rule engine + evidence + LLM arbiter (deterministic)

Seeds: [11, 22, 33, 44, 55] (pre-registered); temperature=0.7 makes
seed-level variation meaningful. full_system is rule-driven and
seed-invariant.

Fail-loud discipline (2026-10-12 audit):
  - LLM 调用失败必须计数并落盘 error 字段，禁止静默变成 NO；
  - 每个基线开跑前先做 canary 调用（连通性 + 合理性），失败即中止该基线；
  - failures>0 的 run 标记 valid=False，不并入均值；全部失败则非零退出。

Output: outputs/baseline_predictions.jsonl (append; provider/model 落盘可溯)

Usage:
  PYTHONUTF8=1 python scripts/run_baselines.py --baseline pure_llm --provider local
  PYTHONUTF8=1 python scripts/run_baselines.py --all --provider local --seed 11
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PYTHONUTF8", "1")
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from huiyan_agent.risk_rules import load_rules, match_rules, assess
from huiyan_agent.normalize import (load_entity_a_registry, load_entity_b_registry)

SEEDS = [11, 22, 33, 44, 55]
BASELINES = ["pure_llm", "naive_rag", "lightrag", "full_system"]
TEMPERATURE = 0.7
CANARY_PAIR = ("hyperglycemia", "retinopathy_any")
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(text: str) -> str:
    """本地 qwen 等带思维链模型：剥掉 <think> 块再解析。"""
    return _THINK_RE.sub("", text or "").strip()


def make_llm(provider: str, seed: int | None = None):
    from huiyan_agent.llm_client import LLMClient
    # R5 fix: seed now travels into the API request body (reproducibility)
    return LLMClient(provider=provider, temperature=TEMPERATURE, seed=seed)


def human_names() -> tuple[dict, dict]:
    """R5 fix: map internal flag ids to registry human-readable names so LLM
    baselines see the same natural-language terms as full_system users
    (previously baselines were fed ids like dr_npdr / glaucoma_suspect_cdr)."""
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_names = {}
    for ent in a_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            a_names.setdefault(str(f), ent.primary_name or str(f))
        a_names.setdefault(ent.entity_a_id, ent.primary_name or ent.entity_a_id)
    b_names = {k: (v.generic_name or k) for k, v in b_reg.items()}
    return a_names, b_names


def canary(llm) -> None:
    """跑批前单点连通性 + 合理性检查：失败即抛异常中止。"""
    resp = llm.complete(
        prompt="Is hyperglycemia a risk factor for diabetic retinopathy? Answer YES or NO on the first line only.",
        system="You are a medical knowledge classifier. Be concise.",
        raise_on_error=True,
    )
    first = strip_think(resp.text).split("\n")[0].strip().upper()
    if not first.startswith(("YES", "NO")):
        raise RuntimeError(f"canary unparsable response: {first[:120]!r}")
    if not first.startswith("YES"):
        print(f"[canary] WARNING: model answered {first[:20]!r} for hyperglycemia×retinopathy "
              f"(expected YES) — proceeding but flag as quality concern")
    else:
        print(f"[canary] OK ({llm.label})")


def load_test_pairs(dataset: str = "nhanes") -> list[dict]:
    """R15(2026-10-20): per-dataset 化(skill v3.0 要求四基线跑在每个验证数据集)。
    nhanes=canonical(80 对历史口径兼容);knhanes/charls 从各自 confirmatory 取 tested。"""
    name = {"nhanes": "nhanes", "knhanes": "knhanes", "charls": "charls"}[dataset]
    csv_path = ROOT / f"outputs/confirmatory/{name}_confirmatory.csv"
    if not csv_path.exists():
        print(f"[baselines] ERROR: {name} confirmatory not found — run evaluate first")
        sys.exit(1)
    import pandas as pd
    df = pd.read_csv(csv_path)
    tested = df[df["status"] == "tested"]
    pairs = []
    for _, row in tested.iterrows():
        pairs.append({
            "a_flag": row["a_flag"], "b_item": row["b_item"],
            "predicted_rule": bool(row["predicted"]),
            "gold3": row.get("gold3", ""),
        })
    print(f"[baselines] {len(pairs)} test pairs from {name} confirmatory (dataset={dataset})")
    return pairs


def run_full_system(pairs, seed):
    """Baseline 4: Full system — rule engine drives prediction (deterministic).

    R5 fix: provider recorded as rule_engine:deterministic (previously
    'deepseek:legacy' — this path makes zero LLM calls)."""
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    from huiyan_agent.risk_rules import match_rules_canonical
    from huiyan_agent.variable_map import load_variable_map, outcome_alias
    _B_ALIAS = outcome_alias(load_variable_map())
    a_idx, b_idx = {}, {}
    for ent in a_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            a_idx.setdefault(str(f), ent)
    for ent in b_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            b_idx.setdefault(str(f), ent)
    results = []
    for p in pairs:
        a_ent = a_idx.get(p["a_flag"]) or a_reg.get(p["a_flag"])
        b_ent = b_idx.get(p["b_item"]) or b_reg.get(p["b_item"])
        rec_common = {
            "baseline": "full_system", "seed": seed,
            "a_flag": p["a_flag"], "b_item": p["b_item"], "gold3": p["gold3"],
            "provider": "rule_engine:deterministic",
        }
        # R16 结局变体规范化回退(与 evaluate_knhanes 同一别名表,variable_map.outcome_alias)
        _canon = _B_ALIAS.get(p["b_item"])
        canon_ent = (b_idx.get(_canon) or b_reg.get(_canon)) if _canon else None
        if a_ent and (b_ent or canon_ent):
            signals, _aliased = match_rules_canonical(rules, a_ent, b_ent, canon_ent)
            assessment = assess(signals)
            prediction = len(signals) > 0
            results.append({
                **rec_common,
                "prediction": prediction,
                "risk_level": assessment.risk_level.value,
                "confidence": assessment.confidence,
            })
        else:
            results.append({
                **rec_common,
                "prediction": False,
                "risk_level": "unknown", "confidence": 0.0,
            })
    return results, 0


def _llm_predict(llm, prompt, system, meta, results, failures):
    """单次 LLM 预测：失败计数+落盘 error，绝不静默。

    R5 (2026-10-14): 解析规则透明化——
    - 首行以 YES/NO 开头 → 正常解析；
    - 首行不可解析但回答是明确的"证据未提及/无信息"（no-evidence 陈述）
      → 映射为 NO（absent evidence ⇒ not a supported risk factor），
      并标记 parsed="no_evidence_inference"（透明可审计，不算失败）；
    - 其余（空响应/乱码/真正歧义）仍计为失败。
    """
    rec = dict(meta)
    # R15(2026-10-20):长跑批的瞬时错误重试(429/网络抖动最多 3 次退避),
    # 重试穷尽才计入 failures——避免一次抖动作废整个 301 对 run
    resp = None
    for _attempt in range(3):
        try:
            resp = llm.complete(prompt=prompt, system=system, raise_on_error=True)
            break
        except Exception as _e:
            if _attempt == 2:
                resp = None
                _last_err = _e
            else:
                import time as _t
                # 429(速率限制)用长退避,其余短退避(bigmodel 1302 实测需要 >10s)
                _wait = 15 * (_attempt + 1) if "429" in str(_e) or "1302" in str(_e) else 2 * (_attempt + 1)
                _t.sleep(_wait)
    if resp is None:
        failures[0] += 1
        rec["prediction"] = False
        rec["risk_level"] = "unknown"; rec["confidence"] = 0.0
        rec["error"] = f"api_retry_exhausted: {str(_last_err)[:90]}"
        results.append(rec)
        return
    try:
        pass
        first = strip_think(resp.text).split("\n")[0].strip().upper()
        if first.startswith(("YES", "NO")):
            rec["prediction"] = first.startswith("YES")
            rec["parsed"] = "yes_no"
        else:
            blob = strip_think(resp.text).upper()
            if _NO_EVIDENCE_RE.search(blob):
                rec["prediction"] = False
                rec["parsed"] = "no_evidence_inference"
            else:
                failures[0] += 1
                rec["prediction"] = False
                rec["error"] = f"unparsable: {first[:80]!r}"
    except Exception as e:
        failures[0] += 1
        rec["prediction"] = False
        rec["error"] = f"{type(e).__name__}: {str(e)[:150]}"
    results.append(rec)


# 明确的"证据缺失"陈述（大小写不敏感；匹配第一条即判 NO）
_NO_EVIDENCE_RE = re.compile(
    r"(DOES NOT MENTION|NOT MENTION|NO MENTION|NO INFORMATION|"
    r"DOES NOT PROVIDE|NOT PROVIDE|NO EVIDENCE|DOES NOT DISCUSS|"
    r"NO DIRECT|NOT SPECIFICALLY|INSUFFICIENT INFORMATION|"
    r"CANNOT DETERMINE|DOES NOT ESTABLISH|NO RELATIONSHIP MENTIONED|"
    # R15(2026-10-20): glm-5.3-flash 的道歉式拒答(实测 hba1c×amd_early 一例),
    # 本质是"无足够信息"——按透明协议归 NO 并标 parsed,不算失败
    r"DO NOT HAVE THE SPECIFIC|APOLOGIZE.*(?:INFO|EVIDENCE)|"
    r"UNABLE TO PROVIDE|DON'T HAVE (?:ENOUGH |ANY )?(?:INFORMATION|EVIDENCE))", re.IGNORECASE)


def run_pure_llm(pairs, seed, provider):
    """Baseline 1: Pure LLM knowledge — no retrieval, no rules."""
    llm = make_llm(provider, seed)
    canary(llm)
    a_names, b_names = human_names()
    results, failures = [], [0]
    for p in pairs:
        a_disp = a_names.get(p["a_flag"], p["a_flag"])
        b_disp = b_names.get(p["b_item"], p["b_item"])
        prompt = (
            f"Is {a_disp} a known risk factor for {b_disp}? "
            f"Respond with exactly YES or NO on the first line. "
            f"If the evidence does not mention the relationship, answer NO."
        )
        meta = {"baseline": "pure_llm", "seed": seed,
                "a_flag": p["a_flag"], "b_item": p["b_item"], "gold3": p["gold3"],
                "provider": llm.label, "api_seed": llm.seed}
        _llm_predict(llm, prompt, "You are a medical knowledge classifier. Be concise.",
                     meta, results, failures)
    return results, failures[0]


def run_naive_rag(pairs, seed, provider):
    """Baseline 2: Naive RAG — plain term-frequency retrieval + LLM.

    R5 fix: uses the purpose-built NaiveRAG retriever (no evidence-level
    weighting, no entity-id boost) instead of the system's EvidenceStore,
    which was tuned for the full system (A-level weight 5.0x) and made the
    baseline non-comparable."""
    from huiyan_agent.naive_rag import NaiveRAG
    store = NaiveRAG()
    llm = make_llm(provider, seed)
    canary(llm)
    a_names, b_names = human_names()
    results, failures = [], [0]
    for p in pairs:
        a_disp = a_names.get(p["a_flag"], p["a_flag"])
        b_disp = b_names.get(p["b_item"], p["b_item"])
        query = f"{a_disp} {b_disp}"
        evidence = store.retrieve(query, top_k=3)
        ev_text = " | ".join(ev.text[:200] for ev in evidence) if evidence else "No evidence found."
        prompt = (f"Evidence: {ev_text[:500]}\n\nIs {a_disp} a risk factor for {b_disp}? "
                  f"Respond with exactly YES or NO on the first line. "
                  f"If the evidence does not mention the relationship, answer NO.")
        meta = {"baseline": "naive_rag", "seed": seed,
                "a_flag": p["a_flag"], "b_item": p["b_item"], "gold3": p["gold3"],
                "n_evidence": len(evidence), "provider": llm.label, "api_seed": llm.seed}
        _llm_predict(llm, prompt, "Answer based only on provided evidence.",
                     meta, results, failures)
    return results, failures[0]


def run_lightrag(pairs, seed, provider):
    """Baseline 3: LightRAG KG retrieval + LLM."""
    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    llm = make_llm(provider, seed)
    canary(llm)
    # 传入同一 provider，避免 adapter 内部默认 deepseek（429 时 KG 综合降级）
    adapter = LightRAGAdapter(chat_client=llm)
    a_names, b_names = human_names()
    results, failures = [], [0]
    for p in pairs:
        a_disp = a_names.get(p["a_flag"], p["a_flag"])
        b_disp = b_names.get(p["b_item"], p["b_item"])
        query = f"What is the relationship between {a_disp} and {b_disp}?"
        # R17(2026-10-20):基线公平修复——lightrag 的定义性能力是 KG 图遍历,
        # 此前硬编码 naive(纯向量)使基线残血(limitations §5 曾如实记录)。
        # hybrid=local+global 图检索;adapter 自带空结果→naive 的韧性降级。
        # R17 终局:hybrid 为 lightrag 基线定格配置——mix+rerank 实测更差
        # (0.164 vs 0.182,5 seeds),已试并如实入册;满血能力开放≠盲目用最大档。
        kg_result = adapter.query(query, mode="hybrid") or ""
        prompt = (f"KG evidence: {kg_result[:500]}\n\nIs {a_disp} a risk factor for {b_disp}? "
                  f"Respond with exactly YES or NO on the first line. "
                  f"If the KG evidence does not mention the relationship, answer NO.")
        meta = {"baseline": "lightrag", "seed": seed,
                "a_flag": p["a_flag"], "b_item": p["b_item"], "gold3": p["gold3"],
                "kg_chars": len(kg_result), "provider": llm.label, "api_seed": llm.seed}
        _llm_predict(llm, prompt, "Answer based on KG evidence.",
                     meta, results, failures)
    return results, failures[0]


def metrics(results):
    tp = sum(1 for r in results if r["prediction"] and r["gold3"] == "replicated")
    fp = sum(1 for r in results if r["prediction"] and r["gold3"] != "replicated")
    fn = sum(1 for r in results if not r["prediction"] and r["gold3"] == "replicated")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else None
    return {"TP": tp, "FP": fp, "FN": fn, "precision": prec, "recall": rec, "F1": f1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--baseline", choices=BASELINES)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dataset", default="nhanes",
                        choices=["nhanes", "knhanes", "charls"],
                        help="per-dataset baselines (skill v3.0); knhanes/charls 写入独立 jsonl")
    parser.add_argument("--provider", default="deepseek",
                        choices=["deepseek", "local", "zhipu"],
                        help="LLM provider（deepseek=commandcode 网关；local=127.0.0.1:8082 llama-server）")
    args = parser.parse_args()

    pairs = load_test_pairs(args.dataset)
    if not pairs:
        return 1

    all_results = []
    output_path = (ROOT / "outputs/baseline_predictions.jsonl" if args.dataset == "nhanes"
                   else ROOT / f"outputs/baseline_predictions_{args.dataset}.jsonl")
    baselines_to_run = [args.baseline] if args.baseline else BASELINES
    seeds_to_run = [args.seed] if args.seed else SEEDS

    any_total_failure = False
    for baseline in baselines_to_run:
        for seed in seeds_to_run:
            print(f"\n[baselines] {baseline} seed={seed} provider={args.provider}...")
            t0 = time.time()
            try:
                if baseline == "full_system":
                    results, n_fail = run_full_system(pairs, seed)
                elif baseline == "pure_llm":
                    results, n_fail = run_pure_llm(pairs, seed, args.provider)
                elif baseline == "naive_rag":
                    results, n_fail = run_naive_rag(pairs, seed, args.provider)
                elif baseline == "lightrag":
                    results, n_fail = run_lightrag(pairs, seed, args.provider)
                else:
                    continue
            except Exception as e:
                print(f"  ABORTED: {type(e).__name__}: {str(e)[:200]}")
                any_total_failure = True
                continue
            elapsed = time.time() - t0
            m = metrics(results)
            valid = n_fail == 0
            if not valid:
                any_total_failure = True
                n_err_samples = sum(1 for r in results if r.get("error"))
                print(f"  {len(results)} pairs in {elapsed:.1f}s | "
                      f"FAILURES={n_fail}/{len(results)} (invalid run, excluded from means)")
                for r in results:
                    if r.get("error"):
                        print(f"    e.g. {r['a_flag']}x{r['b_item']}: {r['error'][:100]}")
                        break
            else:
                print(f"  {len(results)} pairs in {elapsed:.1f}s | "
                      f"P={m['precision']} R={m['recall']} F1={m['F1']} | 0 failures")
            for r in results:
                r["valid"] = valid
            all_results.extend(results)

    with output_path.open("a", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n[baselines] {len(all_results)} predictions → {output_path}")

    # Summary（只统计 valid run）
    by_bl = defaultdict(list)
    for r in all_results:
        if r.get("valid", True):
            by_bl[r["baseline"]].append(r)
    print("\n=== Summary (valid runs only) ===")
    for bl, rs in sorted(by_bl.items()):
        by_seed = defaultdict(list)
        for r in rs:
            by_seed[r["seed"]].append(r)
        ms = [metrics(srs) for srs in by_seed.values()]
        p = sum(m["precision"] or 0 for m in ms) / max(1, len(ms))
        r_ = sum(m["recall"] or 0 for m in ms) / max(1, len(ms))
        f = sum(m["F1"] or 0 for m in ms) / max(1, len(ms))
        print(f"  {bl:15s} | P={p:.3f} R={r_:.3f} F1={f:.3f} | {len(ms)} seeds | temp={TEMPERATURE}")
    return 1 if any_total_failure else 0


if __name__ == "__main__":
    sys.exit(main())
