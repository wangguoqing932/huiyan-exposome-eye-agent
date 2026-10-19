"""Record the README correction and the submission-directory cleanup."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十五、README 断言了系统不具备的性质

### 发现

`README.md` 第 4 步的管线注释写着：

```
# 4. 融合系统与文献层（LLM 仲裁 temp=0，确定性）
```

**"确定性"这一句被 §十四 的测量推翻**：温度确已 0.0，而同一输入仍有
约 1/12 的运行被改级（`smoking × amd_late`，medium↔high）。

**README 是任何人（使用者、审稿人、后续会话）接触这个 agent 的第一份文档，
而它断言了一个系统不具备的性质。**

### 同时发现的其它失真

| 位置 | 原述 | 实测 |
|---|---|---|
| Project Status | "论文写作未开始：`outputs/paper/`、`outputs/submission/` **为空**" | 稿件 116,856 B；提交包 12 件 + 8 表 + 24 图 |
| Project Status | 状态停在 "2026-10-15，R10 维护轮后" | writer **7_9** |
| Quick Navigation | "交付表 **6** 张、论文图 **4** 张" | 表 **8** 张、图 **6** 张 |
| 重建管道第 5 步 | "渲染 **4** 图" | 6 图 |

**"outputs 为空"这条尤其危险**：一个后续会话（或作者本人）读到它，
会以为稿件尚未开始，从而**重做已有的工作或覆盖它**。

### 已修

- 第 4 步注释改为"规则层确定；仲裁层温度已 0 但**非确定**，见 §十四"
- Project Status 改为 writer 7_9，并**新增一段写明三层的可靠性现状**：
  规则层确定 · 证据/KG 层就位 · **仲裁层非确定且 `confidence` 无法自我标记**
- Quick Navigation 的数字按其实际值订正，并补入 `docs/AGENT_AUDIT.md` 一行
- 第 5 步删除硬编码的图数

### 我改完后自查，抓到自己写错一个数

改完立即逐项核验新写的每个数字，**`submission 顶层 9 件` 报 FAIL，实测 11 件**
（后又因补入 `highlights.md` 成 12 件）。已订正。

**这条自查不是形式**：同一轮里我刚写下"9 件"，若不复核就会把一个新错误
写进这份文档——**即用一次未经验证的陈述去替换另一条未经验证的陈述**。

### 顺带清理（作者要求"别污染项目"）

| 项 | 处置 |
|---|---|
| `submission/manuscript.md` 是 118,498 B 的旧 **CRLF** 版，而 `paper/manuscript.md` 已规范化为 116,856 B | **已同步**；现两者逐字节相同，无 CRLF 残留 |
| `submission/_journal_pages/` 空目录（抓取全失败留下的） | **已删** |
| `highlights.md` 在 `paper/` 而其余提交件在 `submission/`，包不自洽 | **已复制进 submission/** |

### 最终核验（11 项全通过）

```
OK  规则 21 条            OK  submission/tables 8      OK  outputs/figures 6
OK  稿件 116,856 B        OK  submission/figures 24    OK  AGENT_AUDIT 14 节
OK  submission 顶层 12 件  OK  outputs/tables 8         OK  两处稿件逐字节一致
OK  _journal_pages 已删   OK  无 CRLF 残留
```
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "README 断言了系统不具备的性质" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
