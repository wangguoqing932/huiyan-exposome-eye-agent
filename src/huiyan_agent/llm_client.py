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
    ) -> None:
        cfg = config or LLMConfig()
        self.provider = provider or cfg.provider
        self.degraded = False

        if self.provider == "stub":
            self.degraded = True
            self.api_key = ""
            self.base_url = ""
            self.model = "stub"
            self.temperature = temperature if temperature is not None else (cfg.temperature or 0.0)
            self.max_tokens = max_tokens or cfg.max_tokens or 1024
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
    def complete(self, prompt: str, system: str | None = None) -> ChatResponse:
        """Return a chat completion. ``degraded=True`` if in stub mode."""
        if self.degraded:
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
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                # Command Code 网关的 deepseek-v4.1-flash 对结构化提示词默认启动
                # 深度推理，max_tokens 被 reasoning 耗尽后 content 为空（Phase 4
                # 实测 reasoning 64K 字符 content 0）。管线场景不需要推理。
                extra_body={"reasoning_effort": "off"},
            )
            return resp.choices[0].message.content or ""
        except ImportError:
            pass
        # raw urllib fallback (no openai SDK installed)
        return self._chat_urllib(messages)

    def _chat_urllib(self, messages: list[dict[str, str]]) -> str:
        body = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "reasoning_effort": "off",
        }).encode("utf-8")
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
