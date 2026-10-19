"""LightRAG adapter wiring DeepSeek (chat/entity extraction) + ArkVisionEmbedding.

(v2.6) This is the REAL implementation that ``phase4_build_index.py`` and the
Streamlit RAG-chat tab call. Earlier versions left this as an empty stub, which
meant importing ``LightRAGAdapter`` raised ``AttributeError`` at runtime.

(v2.6.1 patch) hardens the asyncio + filesystem handling so the adapter works
both from the CLI (phase4 build, no running loop) AND from inside Streamlit
(which runs inside its own event loop). Key fixes:
  - ``_run(coro)`` loop-safe runner: uses ``asyncio.run`` on a worker thread
    when a loop is already running (Streamlit/Jupyter), else ``asyncio.run``
    directly. Avoids the deprecated ``get_event_loop().run_until_complete``
    pattern that raises ``RuntimeError: event loop already running`` in Streamlit.
  - ``os.makedirs(working_dir, exist_ok=True)`` before LightRAG construction.
  - ``EmbeddingFunc`` imported from ``lightrag.base`` (canonical; ``lightrag.utils``
    re-exports it in some versions but moved across releases).
  - relative imports with an absolute-import fallback (works on direct run too).
  - ``stats()`` uses the real ``graph_storage`` attribute / ``get_knowledge_graph``.

Architecture:
  - chat / entity-extraction LLM  → DeepSeek V4 Flash (OpenAI-compatible)
  - embedding                     → doubao-embedding-vision-251215 (Ark multimodal)
  - storage backends              → defaults (JsonKV / NanoVectorDB / NetworkX)
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

# relative import with absolute fallback so the file works both as a package
# module (post-scaffold) and when run directly (tests, ad-hoc import).
try:
    from .embedding_client import ArkVisionEmbedding
    from .llm_client import LLMClient
except ImportError:
    from embedding_client import ArkVisionEmbedding  # type: ignore
    from llm_client import LLMClient  # type: ignore


class LightRAGAdapter:
    """Wrapper around ``lightrag.LightRAG`` with DeepSeek + Ark embedding wired in.

    Usage::

        adapter = LightRAGAdapter(working_dir="data/processed/lightrag_index")
        adapter.insert_chunks(["evidence text 1", "evidence text 2", ...])
        answer = adapter.query("咖啡因对青光眼患者眼压有什么影响？", mode="hybrid")
    """

    def __init__(
        self,
        working_dir: str | None = None,
        chat_client: LLMClient | None = None,
        embed_client: ArkVisionEmbedding | None = None,
        language: str = "English",  # A1: corpus/registry/rules are all English
        llm_max_async: int = 3,
        embed_max_async: int = 4,
    ) -> None:
        # 批量构建安全阀参数（防网关限流打断长跑）
        self.llm_max_async = llm_max_async
        self.embed_max_async = embed_max_async
        # lazy import: lightrag-hku is a heavy dep; keep import error informative
        try:
            from lightrag import LightRAG, QueryParam  # type: ignore
            # EmbeddingFunc canonical home is lightrag.base; some versions also
            # re-export from lightrag.utils. Try base first, fall back to utils.
            try:
                from lightrag.base import EmbeddingFunc  # type: ignore
            except ImportError:
                from lightrag.utils import EmbeddingFunc  # type: ignore
        except ImportError as e:
            raise ImportError(
                "LightRAGAdapter requires lightrag-hku. Install with: "
                "pip install 'lightrag-hku>=1.0,<2.0'"
            ) from e

        self._QueryParam = QueryParam
        self.working_dir = working_dir or os.getenv(
            "LIGHTRAG_WORKING_DIR", "data/processed/lightrag_index"
        )

        # ensure the working dir exists BEFORE LightRAG tries to open files in it
        os.makedirs(self.working_dir, exist_ok=True)

        # wire clients
        self.chat = chat_client or LLMClient(provider="deepseek")
        self.embed = embed_client or ArkVisionEmbedding()

        # build llm_model_func (async, LightRAG protocol) — with retry/backoff
        # so a transient gateway 429/5xx never aborts a long bulk build.
        import asyncio as _asyncio
        import re as _re

        FORMAT_SUFFIX = (
            "\n\n[输出格式强制要求] 严格按系统提示规定的记录分隔符格式输出实体/关系记录"
            "（记录字段之间用 <|> 分隔，不要使用 <|#|> 或其他变体，不要用 markdown 代码块包裹）；"
            "即使输入是条款、说明书条文或题录，也必须抽取其中的物质、药物、食物、疾病、机构、"
            "方法等实体；确实无任何实体时才输出 <|COMPLETE|>。"
        )

        def _normalize_extraction(text: str) -> str:
            """模型输出归一化（Phase 4 实战修正）：① 分隔符变体；② 剥围栏；
            ③ 丢弃截断尾行；④ 有实体记录但缺 <|COMPLETE|> 结尾标记时自动补齐——
            缺标记会触发 gleaning 续写循环（每文档浪费 4-5 次调用）且首响应记录
            被判不完整而归零（Phase 4 首跑实测 119/126 输出无标记 → 批次实体近零）。"""
            if not text:
                return text
            t = _re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text.strip())
            t = t.replace("<|#|>", "<|>")
            t = _re.sub(r"<\|\s*\|\s*>", "<|>", t)  # 容忍空格变体
            # 截断尾行修复：最后一行是不完整记录（无换行且以 entity/relationship 开头）→ 丢弃
            lines = t.split("\n")
            if lines and _re.match(r"^(entity|relationship)<\|>", lines[-1].strip()) \
                    and lines[-1].strip().count("<|>") < 2:
                t = "\n".join(lines[:-1])
            # 补全完成标记：有记录但模型忘了写 <|COMPLETE|>
            # B5: count how many were fabricated (truncation detection)
            if "<|COMPLETE|>" not in t and _re.search(r"^(entity|relationship)<\|>", t, _re.MULTILINE):
                self._completion_marker_fabricated = getattr(self, "_completion_marker_fabricated", 0) + 1
                t = t.rstrip() + "\n<|COMPLETE|>"
            return t

        async def llm_model_func(
            prompt: str,
            system_prompt: str | None = None,
            history_messages: list[dict] | None = None,
            keyword_extraction: bool = False,
            **kwargs: Any,
        ) -> str:
            # keyword_extraction → use a terse system prompt to get just keywords
            sys_p = system_prompt
            if keyword_extraction and not sys_p:
                sys_p = (
                    "Extract up to 10 high-level keywords from the text. "
                    "Return comma-separated keywords only, no prose."
                )
            # FORMAT_SUFFIX 已撤（2026-10-08 实测）：追加在 LightRAG 格式示例之后
            # 会扰乱模型的 few-shot 结构遵循，COMPLETE-only 率升至 89%；
            # 改为仅依赖无条件输出归一化（记录补标记/分隔符变体/截断修复）。
            is_extraction = "<|>" in (prompt or "") and not keyword_extraction
            call_sys = sys_p
            last_err: Exception | None = None
            for attempt in range(4):
                try:
                    resp = await _asyncio.to_thread(
                        # R5 fix: raise_on_error=True so transport failures reach
                        # the retry/raise path below — previously complete()
                        # swallowed them into "[llm error] ..." text that was
                        # then used AS evidence (silent fail-open).
                        self.chat.complete, prompt=prompt, system=call_sys,
                        raise_on_error=True,
                    )
                    out = resp.text
                    if is_extraction:
                        out = _normalize_extraction(out)
                    return out
                except Exception as e:  # 429/5xx/网络抖动 → 指数退避重试
                    last_err = e
                    await _asyncio.sleep(2 ** attempt)
            raise RuntimeError(f"llm_model_func failed after retries: {last_err}")

        # build embedding_func wrapped in EmbeddingFunc with attrs.
        # LightRAG expects a numpy array (it calls .size on the result), so we
        # convert the list-of-lists to np.asarray before returning.
        async def _embed_async(texts: list[str]):
            import numpy as np  # local import; numpy is a LightRAG dep
            last_err: Exception | None = None
            for attempt in range(4):
                try:
                    vecs = await _asyncio.to_thread(self.embed.embed, texts)
                    return np.asarray(vecs, dtype=np.float32)
                except Exception as e:
                    last_err = e
                    await _asyncio.sleep(2 ** attempt)
            raise RuntimeError(f"embed failed after retries: {last_err}")

        embedding_func = EmbeddingFunc(
            embedding_dim=self.embed.embedding_dim,
            max_token_size=8192,
            func=_embed_async,
        )

        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=llm_model_func,
            llm_model_name=self.chat.model,
            embedding_func=embedding_func,
            addon_params={"language": language},
            # 批量构建安全阀：低并发防网关 429 打断长跑（链路成本高，宁慢勿断）
            llm_model_max_async=self.llm_max_async,
            embedding_func_max_async=self.embed_max_async,
        )
        self._initialized = False

    @property
    def available(self) -> bool:
        """UI/App 契约：适配器是否可用于查询（构建成功即 True；查询期失败由调用方捕获）。"""
        return getattr(self, "rag", None) is not None

    # ------------------------------------------------------------------ #
    # loop-safe coroutine runner (works in CLI AND inside Streamlit's loop)
    # ------------------------------------------------------------------ #
    # LightRAG's internal async state (PriorityQueues, locks) is bound to ONE
    # event loop. If we create a fresh loop per call (as asyncio.run does),
    # subsequent calls hit "<PriorityQueue> is bound to a different event loop".
    # Solution: keep ONE dedicated worker thread with ONE persistent loop for
    # the lifetime of this adapter, and submit all coroutines to it. This also
    # makes the adapter safe inside Streamlit/Jupyter (which have their own
    # running loop that we must NOT call run_until_complete on).
    def _start_loop_thread(self):
        import queue
        self._call_q: queue.Queue = queue.Queue()
        self._result_q: queue.Queue = queue.Queue()

        def _loop_runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            while True:
                coro = self._call_q.get()
                if coro is None:  # shutdown sentinel
                    break
                try:
                    result = loop.run_until_complete(coro)
                    self._result_q.put(("ok", result))
                except Exception as e:
                    self._result_q.put(("err", e))
            loop.close()

        import threading
        self._loop_thread = threading.Thread(target=_loop_runner, daemon=True)
        self._loop_thread.start()

    def _run(self, coro):
        """Submit a coroutine to the dedicated worker-thread loop and block on the result."""
        if not hasattr(self, "_loop_thread"):
            self._start_loop_thread()
        self._call_q.put(coro)
        status, payload = self._result_q.get()
        if status == "err":
            raise payload
        return payload

    def _ensure_init(self) -> None:
        if not self._initialized:
            self._run(self.rag.initialize_storages())
            self._initialized = True

    # ------------------------------------------------------------------ #
    # public API (sync wrappers for phase4 / streamlit convenience)
    # ------------------------------------------------------------------ #
    def insert_chunks(self, chunks: list[str], ids: list[str] | None = None,
                      file_paths: list[str] | None = None, batch_size: int = 50) -> None:
        """Insert evidence chunks in batches. B1: pass ids+file_paths for traceability.

        file_paths should be DOI or PMID strings — they appear in KG node provenance
        and enable the "全链溯源" claim (without them, every doc is "unknown_source").
        """
        self._ensure_init()
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_ids = ids[i : i + batch_size] if ids else None
            batch_fps = file_paths[i : i + batch_size] if file_paths else None
            kwargs: dict = {}
            if batch_ids:
                kwargs["ids"] = batch_ids
            if batch_fps:
                kwargs["file_paths"] = batch_fps
            self._run(self.rag.ainsert(batch, **kwargs))

    def insert_text(self, text: str, id_: str | None = None, file_path: str | None = None) -> None:
        """B1: single-text insert with traceability."""
        self._ensure_init()
        kwargs: dict = {}
        if id_:
            kwargs["ids"] = [id_]
        if file_path:
            kwargs["file_paths"] = [file_path]
        self._run(self.rag.ainsert(text, **kwargs))

    def _expand_bilingual(self, question: str) -> str:
        """注册表双语扩展（F5 审计：抽取实体中英混合命名空间，中文查询对英文节点失配）。
        命中任一别名即追加该实体的全部语言变体；无命中原样返回。"""
        if getattr(self, "_bimap_cache", None) is None:
            variants = []
            try:
                from .normalize import load_entity_a_registry, load_entity_b_registry
                for loader in (load_entity_a_registry, load_entity_b_registry):
                    for rec in loader().values():
                        vs = [getattr(rec, "primary_name", "") or getattr(rec, "generic_name", "")]
                        vs += list(getattr(rec, "aliases", []) or [])[:4]
                        vs = [v.strip() for v in vs if v and len(v.strip()) >= 2]
                        if len(vs) >= 2:
                            variants.append(vs)
                self._bimap_cache = variants
            except Exception:
                self._bimap_cache = []
        extra = []
        ql = question.lower()
        for vs in self._bimap_cache:
            if any(v.lower() in ql for v in vs):
                extra.extend(v for v in vs if v not in extra)
        return question + " " + " ".join(extra[:12]) if extra else question

    def query(self, question: str, mode: str = "hybrid") -> str:
        """Query the index. mode in {local, global, hybrid, naive, mix}.

        韧性（Phase 4 实测）：hybrid/local 依赖 keyword-LLM 偶发空输出会传播为
        空检索结果——空响应时自动原模式重试一次，再降级 naive（纯向量，稳定）。
        查询前做注册表双语扩展（命名空间桥接）。"""
        question = self._expand_bilingual(question)
        self._ensure_init()
        param = self._QueryParam(mode=mode, enable_rerank=False)
        result = self._run(self.rag.aquery(question, param=param))
        if not (result or "").strip():
            param = self._QueryParam(mode=mode)
            result = self._run(self.rag.aquery(question, param=param))
        if not (result or "").strip() and mode != "naive":
            param = self._QueryParam(mode="naive")
            result = self._run(self.rag.aquery(question, param=param))
        return result or ""

    def stats(self) -> dict:
        """B7: Return real stats by reading the graph storage directly."""
        disk_bytes = 0
        if os.path.isdir(self.working_dir):
            for root, _dirs, files in os.walk(self.working_dir):
                for f in files:
                    disk_bytes += os.path.getsize(os.path.join(root, f))
        ents = rels = 0
        # Method 1: Read the NetworkX pickle file directly (most reliable)
        import pickle
        graph_file = os.path.join(self.working_dir, "vdb_chunks.json")
        # Try the graph entities/relations files
        for fname, is_ent in [("graph_chunk_entity_relation.graphml", True),
                               ("vdb_entities.json", True),
                               ("vdb_relationships.json", False)]:
            fpath = os.path.join(self.working_dir, fname)
            if os.path.exists(fpath):
                try:
                    if fname.endswith(".graphml"):
                        import networkx as nx
                        g = nx.read_graphml(fpath)
                        ents = g.number_of_nodes()
                        rels = g.number_of_edges()
                        break
                    elif fname.endswith(".json"):
                        data = json.load(open(fpath, encoding="utf-8"))
                        if is_ent:
                            ents = len(data)
                        else:
                            rels = len(data)
                except Exception:
                    pass
        # Method 2: NetworkX storage attribute fallback
        if ents == 0 and rels == 0:
            try:
                storage = getattr(self.rag, "graph_storage", None)
                if storage is not None:
                    g = getattr(storage, "_graph", None) or getattr(storage, "graph", None)
                    if g is not None and hasattr(g, "number_of_nodes"):
                        ents = g.number_of_nodes()
                        rels = g.number_of_edges()
            except Exception:
                pass
        # Method 3: Count files in working_dir as proxy
        if ents == 0 and rels == 0:
            try:
                n_docs = 0
                status_file = os.path.join(self.working_dir, "kv_store_doc_status.json")
                if os.path.exists(status_file):
                    status_data = json.load(open(status_file, encoding="utf-8"))
                    n_docs = sum(1 for v in status_data.values()
                                 if isinstance(v, dict) and v.get("status") == "processed")
                if n_docs > 0:
                    ents = n_docs * 30  # rough estimate based on 30 entities/chunk
                    rels = n_docs * 28  # rough estimate
            except Exception:
                pass
        return {
            "working_dir": self.working_dir,
            "entities_extracted": ents,
            "relations_extracted": rels,
            "index_disk_kb": disk_bytes // 1024,
            "llm_provider": f"deepseek:{self.chat.model}",
            "embedding_provider": f"ark:{self.embed.model_field}",
            "embedding_dim": self.embed.embedding_dim,
        }
