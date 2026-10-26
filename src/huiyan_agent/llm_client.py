"""LLM chat client (DeepSeek V4 Flash, OpenAI-compatible).

Provides a thin ``complete(prompt, system)`` interface used by the rule-citation
relevance judge, the Streamlit RAG-chat tab, and LightRAG's entity-extraction /
summary LLM. DeepSeek's API is OpenAI-compatible, so we use the OpenAI client
when available and fall back to raw urllib if the SDK is missing.

Reads from env (.env / os.environ):
  HUANYU_BULK_API_KEY       preferred key (== DEEPSEEK_API_KEY)
  HUANYU_BULK_MODEL         deepseek-v4-flash (default)
  HUANYU_BULK_BASE_URL      https://api.deepseek.com/v1
  HUANYU_BULK_TEMPERATURE   default 0.0
  HUANYU_BULK_MAX_TOKENS    default 1024

If no key is configured, the client enters **stub mode**: every ``complete``
returns a canned template answer and sets ``self.degraded = True`` so callers
(verify_rule_citations relevance layer, Streamlit chat) can gracefully degrade
instead of crashing the build.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# 项目 .env 是密钥/模型的唯一事实来源；override=True 防止外部环境变量
# （如历史遗留的 HKCU DEEPSEEK_API_KEY）静默遮蔽项目配置。
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass


def _ensure_v1(base_url: str) -> str:
    """规范化 base_url：补全 /v1 后缀且不重复（commandcode 网关自带 /v1）。"""
    url = base_url.rstrip("/")
    return url if url.endswith("/v1") else url + "/v1"


@dataclass
class ChatResponse:
    text: str
    degraded: bool = False


@dataclass
class LLMConfig:
    """LLM 客户端配置（app/streamlit_app.py 契约：LLMClient(LLMConfig(provider=...))）。"""

    provider: str = "deepseek"  # deepseek | arbiter | stub
    temperature: float | None = None
    max_tokens: int | None = None


class LLMClient:
    """OpenAI-compatible chat client (DeepSeek V4 Flash by default).

    Parameters
    ----------
    config : LLMConfig | None
        配置对象（streamlit 契约入口）。
    provider, temperature, max_tokens :
        关键字覆盖（与 config 等价；config 与 kwargs 同时给出时 kwargs 优先）。
    provider 通道语义:
        "deepseek" — 主通道: HUANYU_BULK_* → DEEPSEEK_*（Command Code 网关）
        "arbiter"  — 仲裁通道: HUANYU_ARBITER_*（缺失时逐项回退主通道）
        "stub"     — 强制降级模式（离线测试）
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        provider: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        seed: int | None = None,
    ) -> None:
        cfg = config or LLMConfig()
        self.provider = provider or cfg.provider
        self.degraded = False
        # R5 fix 2026-10-14: seed is now passed through to the API request
        # body (previously only recorded in metadata, with no reproducibility
        # semantics). OpenAI-compatible /chat/completions supports `seed`
        # (llama-server and DeepSeek both honor it).
        self.seed = seed

        if self.provider == "stub":
            self.degraded = True
            self.api_key = ""
            self.base_url = ""
            self.model = "stub"
            self.temperature = temperature if temperature is not None else (cfg.temperature or 0.0)
            self.max_tokens = max_tokens or cfg.max_tokens or 1024
            return

        # 本地 llama-server（OpenAI 兼容，无鉴权；基线/测试用）
        if self.provider == "local":
            self.api_key = os.getenv("LOCAL_LLM_API_KEY", "local")
            self.base_url = _ensure_v1(
                os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8082/v1"))
            self.model = os.getenv("LOCAL_LLM_MODEL", "local-qwen")
            self.temperature = float(
                temperature if temperature is not None
                else (cfg.temperature if cfg.temperature is not None else 0.0))
            self.max_tokens = int(
                max_tokens or cfg.max_tokens or os.getenv("HUANYU_BULK_MAX_TOKENS", "1024"))
            return

        # DeepSeek / OpenAI-compatible resolution
        if self.provider == "arbiter":
            self.api_key = (
                os.getenv("HUANYU_ARBITER_API_KEY")
                or os.getenv("HUANYU_BULK_API_KEY")
                or os.getenv("DEEPSEEK_API_KEY")
                or ""
            )
            self.base_url = (
                _ensure_v1(os.getenv("HUANYU_ARBITER_BASE_URL"))
                if os.getenv("HUANYU_ARBITER_BASE_URL")
                else _ensure_v1(os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
            )
            self.model = (
                os.getenv("HUANYU_ARBITER_MODEL")
                or os.getenv("LLM_CHAT_MODEL")
                or "deepseek-v4-flash"
            )
        elif self.provider == "zhipu":  # bigmodel 智谱 GLM(2026-10-16 加,有 key 即可用)
            self.api_key = os.getenv("ZHIPU_API_KEY", "")
            if not self.api_key:
                raise RuntimeError(
                    "[zhipu] .env 缺 ZHIPU_API_KEY(bigmodel.cn)——拿到 key 后填入即可启用,无需改代码")
            # bigmodel v4 端点以 /v4 结尾,_ensure_v1 会错拼 /v1——直接原样使用
            self.base_url = (os.getenv("ZHIPU_BASE_URL", "")
                             or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
            self.model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
        else:  # deepseek 主通道
            self.api_key = (
                os.getenv("HUANYU_BULK_API_KEY")
                or os.getenv("DEEPSEEK_API_KEY")
                or ""
            )
            self.base_url = (
                os.getenv("HUANYU_BULK_BASE_URL")
                or _ensure_v1(os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
            )
            self.model = (
                os.getenv("HUANYU_BULK_MODEL")
                or os.getenv("LLM_CHAT_MODEL")
                or "deepseek-v4-flash"
            )

        self.temperature = float(
            temperature if temperature is not None
            else (cfg.temperature if cfg.temperature is not None else os.getenv("HUANYU_BULK_TEMPERATURE", "0.0"))
        )
        self.max_tokens = int(
            max_tokens or cfg.max_tokens or os.getenv("HUANYU_BULK_MAX_TOKENS", "1024")
        )

        if not self.api_key:
            # no key → degrade to stub so the build can proceed in keyword-only mode
            self.degraded = True
            self.model = "stub"

    # ------------------------------------------------------------------ #
    # metadata helpers
    # ------------------------------------------------------------------ #
    @property
    def label(self) -> str:
        """人类可读标识（报告 metadata.llm_label 用）。"""
        return f"{self.provider}:{self.model}" if self.model != "stub" else "stub"

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def complete(self, prompt: str, system: str | None = None,
                 *, raise_on_error: bool = False) -> ChatResponse:
        """Return a chat completion. ``degraded=True`` if in stub mode.

        ``raise_on_error=True`` 时网络/API 失败直接抛异常（基线运行等
        需要区分"模型判断"与"管道故障"的场景必须开启；默认 False 保持
        建索引等长任务的韧性降级）。
        """
        # R13-D(2026-10-16):自一致确定性层。temp=0 仍有提供方级非确定
        # (AGENT_AUDIT: 1/12 翻转)。n_consistency>1 时多次采样取多数,
        # 并按 (模型,温度,消息哈希) 落盘缓存保证跨运行可复现。
        import os as _os
        _nc = int(_os.environ.get("HUIYAN_ARBITER_CONSISTENCY", "1"))
        if _nc > 1:
            return self._complete_consistent(prompt, system, _nc, raise_on_error)
        # R15 修复(2026-10-20):R13-D 抽函数时漏了此分支,complete() 在
        # _nc=1 时静默返回 None——补回单次委托,并以单测锁定。
        return self._complete_single(prompt, system, raise_on_error)


    def _complete_consistent(self, prompt: str, system: str | None, n: int,
                             raise_on_error: bool) -> ChatResponse:
        """n 次自一致采样:文本完全一致 → 直接返回;否则取多数文本。

        缓存:data/processed/arbiter_consistency_cache.json,key 为
        (model, temperature, sha256(messages));命中则零调用返回。
        """
        import hashlib, json as _json
        from collections import Counter
        from pathlib import Path as _P
        messages = ([{"role": "system", "content": system}] if system else []) +                    [{"role": "user", "content": prompt}]
        key = hashlib.sha256(
            (f"{self.model}|{self.temperature}|" +
             _json.dumps(messages, ensure_ascii=False, sort_keys=True)
             ).encode("utf-8")).hexdigest()[:24]
        cache_path = _P(__file__).resolve().parents[2] / "data" / "processed" /             "arbiter_consistency_cache.json"
        cache = {}
        if cache_path.exists():
            try:
                cache = _json.loads(cache_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 — 缓存损坏则重建
                cache = {}
        if key in cache:
            r0 = ChatResponse(text=cache[key]["text"], degraded=False)
            r0.consistency_meta = {"cached": True, **(cache[key].get("meta") or {})}
            return r0
        texts = []
        last = None
        for _ in range(n):
            r = self._complete_single(prompt, system, raise_on_error)
            texts.append(r.text)
            last = r
        (majority, _), = Counter(texts).most_common(1)
        cache[key] = {"text": majority, "meta": {"n": n, "distinct": len(set(texts)),
                                                 "texts": texts}}
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(_json.dumps(cache, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        rr = ChatResponse(text=majority, degraded=last.degraded)
        rr.consistency_meta = {"n": n, "distinct": len(set(texts))}
        return rr

    def _complete_single(self, prompt: str, system: str | None,
                         raise_on_error: bool) -> ChatResponse:
        """原 complete 主体(单次)。"""
        if self.degraded:
            if raise_on_error:
                raise RuntimeError("LLM client in stub/degraded mode at init")
            return ChatResponse(
                text=f"[stub] no LLM key configured; prompt was {len(prompt)} chars.",
                degraded=True,
            )
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            text = self._chat(messages)
            return ChatResponse(text=text, degraded=False)
        except Exception as e:
            if raise_on_error:
                raise
            # network / API failure → degrade rather than crash the build
            return ChatResponse(text=f"[llm error] {e}", degraded=True)

    # ------------------------------------------------------------------ #
    # transport
    # ------------------------------------------------------------------ #
    def _chat(self, messages: list[dict[str, str]]) -> str:
        """Try the OpenAI SDK first, fall back to raw urllib."""
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            kwargs = {}
            if self.provider == "zhipu":
                # bigmodel v4 的思考开关是 thinking.type,reasoning_effort 不被识别
                # (实测默认 9s/次含 1.4k 字推理,关思考 3.8s;与本地 qwen 的
                # thinking-disabled 口径一致,论文标注同源)
                kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
            elif self.provider != "local":
                # Command Code 网关的 deepseek-v4.1-flash 对结构化提示词默认启动
                # 深度推理，max_tokens 被 reasoning 耗尽后 content 为空（Phase 4
                # 实测 reasoning 64K 字符 content 0）。管线场景不需要推理。
                kwargs["extra_body"] = {"reasoning_effort": "off"}
            else:
                # 本地 qwen3.8：关思维链（实测 84s→0.3s），基线跑批必需；
                # 论文报告时注明 thinking disabled (fast mode)。
                kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **({"seed": self.seed} if self.seed is not None else {}),
                **kwargs,
            )
            return resp.choices[0].message.content or ""
        except ImportError:
            pass
        # raw urllib fallback (no openai SDK installed)
        return self._chat_urllib(messages)

    def _chat_urllib(self, messages: list[dict[str, str]]) -> str:
        body_d = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.seed is not None:
            body_d["seed"] = self.seed
        if self.provider != "local":
            body_d["reasoning_effort"] = "off"
        else:
            body_d["chat_template_kwargs"] = {"enable_thinking": False}
        body = json.dumps(body_d).encode("utf-8")
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url, data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices") or []
        if not choices:
            return ""
        msg = choices[0].get("message", {})
        # DeepSeek V4 puts reasoning in `reasoning_content`; final answer in `content`
        return msg.get("content") or ""


def from_env_dual():
    """Convenience factory referenced by setup_environment.py docstring.

    Returns a single bulk (DeepSeek) client configured from env.
    """
    return LLMClient(provider="deepseek")


class DualLLMClient:
    """主通道 + 仲裁通道双客户端（safety_agent 分层仲裁用）。

    app/streamlit_app.py 契约入口：``DualLLMClient.from_env()``。
    - primary: 主通道（bulk），报告生成/常规调用
    - arbiter: 仲裁通道；未配置时回退到 primary（同一对象别名）
    """

    def __init__(self, primary: LLMClient, arbiter: LLMClient | None = None) -> None:
        self.primary = primary
        self.arbiter = arbiter if arbiter is not None else primary

    @classmethod
    def from_env(cls) -> DualLLMClient:
        """从 .env / 环境变量构建双通道；主通道缺 key 时整体进入 stub 语义。"""
        primary = LLMClient(provider="deepseek")
        arbiter = LLMClient(provider="arbiter") if primary.api_key else LLMClient(provider="stub")
        return cls(primary=primary, arbiter=arbiter)

    # ------------------------------------------------------------------ #
    # streamlit / safety_agent 依赖的鸭子类型接口（与 LLMClient 一致）
    # ------------------------------------------------------------------ #
    @property
    def degraded(self) -> bool:
        return self.primary.degraded

    @property
    def label(self) -> str:
        return self.primary.label

    def complete(self, prompt: str, system: str | None = None) -> ChatResponse:
        return self.primary.complete(prompt, system)

    def complete_arbiter(self, prompt: str, system: str | None = None) -> ChatResponse:
        """走仲裁通道（分层仲裁第二跳用）。"""
        return self.arbiter.complete(prompt, system)
