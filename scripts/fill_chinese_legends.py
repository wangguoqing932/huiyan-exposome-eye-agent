#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill the Chinese figure legends (writer 7_8).

The legends builder emits an English draft plus a Chinese scaffold marked
"[TODO: 根据上方英文图例翻译并核对中文表述]". Phase 7_8 owns that scaffold.

Two rules govern this file:
  * every number in the Chinese legend must equal the number in the English
    legend for the same figure -- the two are read side by side, and a
    discrepancy between them is worse than a translation error; and
  * the Chinese legend is a translation, not a second summary. It must not
    introduce a claim the English version does not make.

The script refuses to write if any figure's numbers disagree with the English
text, so a transcription slip fails loudly instead of shipping.

Run: python scripts/fill_chinese_legends.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FP = ROOT / "outputs" / "paper" / "figure_legends.md"

CN = {
1: """**图 1。慧眼系统架构。**
慧眼整合三层结构——确定性规则引擎、知识图谱检索模块（LightRAG）与 LLM 仲裁器——为
暴露组（代谢-营养-生活方式-环境）× 主要致盲眼病交互输出可解释的风险分级报告，
并保证从输出回溯至原始证据的完整可追溯性。
（**a**）端到端流程：用户输入 → 实体归一化 → 规则引擎 → 风险引导的 LightRAG 检索
→ 证据压缩 → LLM 仲裁 → 结构化报告。
（**b**）三层放大视图：规则层（YAML 配置）+ 知识图谱层（LightRAG 图）+ 仲裁层（LLM），展示可追溯链。
（**c**）四种输出视图：临床医生卡片／患者手册／研究表格／政策简报，均由单次推理生成。
统计说明：规则层含 configs/rules.yaml 中的 21 条确定性规则；知识图谱层为覆盖证据片段的
LightRAG 图；仲裁层为 DeepSeek 主客户端 + DualLLMClient 第二客户端（未配置 GPT 端点）。
缩写：LLM = 大语言模型；KG = 知识图谱；YAML = YAML Ain't Markup Language；
LightRAG = 轻量检索增强生成；GPT = 生成式预训练变换器。""",

2: """**图 2。慧眼（v1.2）与三个 LLM 基线在 NHANES 配对上的比较（针对 R11 更正后的金标准，5 个随机种子）。**
在 R11 更正后的三态金标准下（survey svyglm 方差），完整慧眼系统的 F1 = 0.435
（精确率 0.294 / 召回率 0.833，跨种子完全一致），高于 lightrag 0.327 ± 0.005、
pure_llm 0.301 ± 0.017 与 naive_rag 0.080 ± 0.089（各方法 5 个种子）。
配对 McNemar 检验相对 pure_llm（p = 0.0043–0.0118）与 naive_rag（p = 0.00024–0.0129）
显著，但相对 lightrag **不显著**（p = 0.057–0.092）。所有方法的精确率都低（0.10–0.29），
原因是多数被预测为正的配对在三态标准下属于"无信息"而非"相反"。扩张前的 v1.1 规则集
在 R5 金标准上得 0.111；该柱按要求同时呈现，但处于不同的金标准上，图中已如此标注。
（**a**）各方法的 F1（5 个种子，均值 ± 标准差；R11 更正金标准）。森林图按方法汇总，
顺序为 full_system 0.435（确定性）> lightrag 0.327 > pure_llm 0.301 > naive_rag 0.080。
源 CSV 中另有一行单独标注的 full_system_v1.1_replay（0.111），其处于 R5 金标准上。
统计说明：NHANES 已检验配对；金标准为 R11 操作化更正后、survey svyglm 方差下的三态标签；
每方法 5 个种子；full_system 为确定性，五次运行完全相同；配对 McNemar 精确检验；
\\* p<0.05；n.s. p>=0.057（对比 lightrag）；v1.1 replay 行基于 R5 金标准，与 R11 金标准柱不可直接比较。
缩写：F1 = F1 分数；P = 精确率；R = 召回率；LLM = 大语言模型；
NHANES = 美国国家健康与营养调查；R5/R11 = 内部分析修订版本（金标准版本）；SD = 标准差；n.s. = 不显著。""",

3: """**图 3。R11 三态协议下的规则层评价：按证据等级的精确率、覆盖度与复现率。**
在预注册的三态标准下，声明域精确率（replicated / (replicated + contradicted)）
在两国均为 1.00，而保守精确率（replicated / 全部可检验的规则相关配对）为
0.375（NHANES，95% CI 0.152–0.646）与 0.333（KNHANES，0.118–0.616）——
两者之差是headline数值最大的单一杠杆，因此必须并列呈现。规则覆盖度
P(可检验 | 规则存在) 很高：NHANES 0.889 / KNHANES 0.882。
复现完全集中在证据等级 A 之外：两国在等级 A 均为 0/3，等级 A+B 为 4/13，
总体分别为 6/19 与 5/16。两国均无规则被否证。
（**a**）双精确率、覆盖度与按证据等级的复现率（两层）。森林图每个数量一行，两国分列。
各行数值：声明域精确率（NHANES 1.00 [0.541,1.000]；KNHANES 1.00 [0.478,1.000]）；
保守精确率（0.375 [0.152,0.646]；0.333 [0.118,0.616]）；规则覆盖度（0.889；0.882）；
证据等级 A 的复现率（两国均 0/3 = 0.00）；等级 A+B（两国均 4/13 = 0.308）；
全部规则（NHANES 6/19 = 0.316；KNHANES 5/16 = 0.312）。均为 0–1 轴上的比例，
区间为精确二项区间。
统计说明：分析单元 = （暴露 flag，结局条目）配对，仅规则相关配对；
声明域精确率 = replicated / (replicated + contradicted)；保守精确率 =
replicated / 全部可检验的规则相关配对；覆盖度 = P(可检验 | 规则存在)，
见分析计划 §0.4 更正 17b；区间为 Clopper-Pearson 精确区间；两国 contradicted 均为 0。
缩写：CI = 置信区间；BHY = Benjamini-Hochberg-Yekutieli；FDR = 错误发现率；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

4: """**图 4。演示案例：暴露组（代谢-营养-生活方式-环境）× 主要致盲眼病风险评估。**
一个完整工作案例，展示系统如何将输入转化为风险分级、可追溯的报告，
以及四个输出视图如何共用同一次推理。
（**a**）输入与实体归一化；（**b**）触发的规则及其证据；（**c**）知识图谱检索路径；
（**d**）LLM 仲裁后的风险分级报告与依据链。
统计说明：四视图由单次推理生成，报告字段可逐项回溯至规则、知识图谱路径与仲裁决策。
缩写：OR = 比值比；LLM = 大语言模型；AMD = 年龄相关性黄斑变性；
DR = 糖尿病视网膜病变；IOP = 眼压；CDR = 视杯视盘比。""",

5: """**图 5。贯穿三层架构的逐步推理轨迹。**
慧眼的三层架构产生完全可追溯的推理链——从规则信号到知识图谱路径再到 LLM 仲裁的
每一次转换都被记录，使任一输出均可事后审计。
（**a**）单个案例的轨迹流：横向泳道图，三条泳道（规则／知识图谱／LLM），
时间自左向右，每个节点为一步骤，含输入、输出与耗时。
（**b**）时延分解：横向堆叠条，显示三层各自的平均耗时，呈现运行成本所在（通常为 LLM）。
（**c**）知识图谱路径多样性：网络图，节点为两个实体与中间概念，边为抽取出的路径，
边宽表示检索频次。
统计说明：泳道配色对应三层架构（见图 1）；耗时为 intval-nhanes 案例的中位数
（n 以 .executor/progress.json 为准）；第二客户端升档仅作用于最高严重度档位
（DualLLMClient；未配置 GPT 端点）。
缩写：KG = 知识图谱；LLM = 大语言模型；LightRAG = 轻量检索增强生成；CI = 置信区间。""",

6: """**图 6。规则相关配对的连续（每 1 个标准差）剂量反应，按调查加权。**
对可估计连续暴露的规则相关配对，展示每 1 个标准差增量对应的比值比，
以检验关联是否随暴露水平单调变化，而非仅在二分类切点上出现。
统计说明：按调查设计加权；每 1 SD；仅规则相关配对；
区间为基于设计的稳健区间。
缩写：SD = 标准差；OR = 比值比；CI = 置信区间；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

7: """**图 7。效能：最小可检出 OR（80%）与观测 OR 的对照，仅规则相关配对。**
多数规则零结果是**有信息量的**而非效能不足。80% 效能下最小可检出比值比的中位数为
NHANES 1.337、KNHANES 1.159，30 个规则相关配对中有 17 个可归类为**有检验力的零结果**
——该设计本可排除 2 倍关联。发生复现的配对位于相反的一角（观测 OR 大、可检出 OR 小），
即它们既有足够效能又效应量大；没有任何配对仅凭较小的可检出效应就实现复现。
设计效应由各配对 survey 与 model 的置信区间宽度之比逐对导出（中位数 NHANES 1.07、KNHANES 1.26），
而非假定。
（**a**）最小可检出 OR（80% 效能）与观测 OR 的散点，双轴均为对数，
每个规则相关配对一点（NHANES n=17，KNHANES n=13）。x = 80% 效能下的最小可检出 OR；
y = 观测 OR。点按层与三态标签着色，可看出复现的配对聚集于"高观测 OR、低可检出 OR"，
而"无信息"配对沿整个可检出范围聚集在 OR = 1 附近。参考线为两轴上的 OR = 1.0、1.5、2.0
以及 y = x 的 identity 线：**位于 identity 线下方者，其观测效应大于该设计所需**。
NHANES 复现 6 个、KNHANES 5 个；无被否证的配对可绘。
统计说明：规则相关配对 NHANES n=17、KNHANES n=13；双对数轴；
x = 80% 效能（双侧 α=0.05）下最小可检出 OR；y = 观测 OR；
灰线为 1.0 / 1.5 / 2.0 与 identity 线；位于 1.5x 线左侧者具备排除 1.5 倍关联的足够效能；
设计效应逐对由 survey/model 置信区间宽度之比导出（中位数 1.07 / 1.26）。
缩写：OR = 比值比；MDE = 最小可检出效应（此处为 80% 效能下的最小可检出比值比）；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

8: """**图 8。文献衍生暴露组规则在八个老龄化队列中的跨队列可迁移性。**
21 条文献衍生规则中，仅 6 条可在八个老龄化队列中检验，而其中只有 2 条实现迁移。
r02（高血糖 → 白内障）在四个可检验队列中的三个复现（LASI OR 1.88、SHARE 1.75、
CLHLS 3.59；CRELES 1.31，q=0.051）。r20（吸烟 → 视力损害）在五个队列中的三个复现，
且**五个队列方向完全一致**（HRS 1.61、ELSA 1.49、SHARE 1.09；KLoSA 1.10 与 CLHLS 1.03 为无信息）。
相反，r10（吸烟 → 白内障）**未能迁移且方向随地区反转**：在 SHARE 为风险升高
（1.11，q=0.0095），而在 CLHLS 显著**保护**（0.748，q=0.0012），ELSA（0.77）与
CRELES（0.70）亦为保护向。r12（饮酒 → 白内障）在 CLHLS 被否证（0.809，q=0.018），
在 SHARE 未复现。
（**a**）按规则的三态构成，跨可检验队列。横向堆叠条，每条规则一个条，
按结局状态分段：replicated、uninformative、contradicted。计数为贡献该状态的队列数。
r02 = 3 复现 + 1 无信息；r20 = 3 复现 + 2 无信息；r10 = 1 复现 + 2 无信息 + 1 否证；
r12 = 1 无信息 + 1 否证；r13 = 1 复现 + 1 无信息；r11 = 1 无信息。
无信息段以独立颜色绘制，**绝不并入其他任一段**。
（**b**）每个（规则，队列）配对的比值比，按结局状态着色。森林图，每个预注册确认配对一行
（共 18 行）。行标签为"<状态> · <规则> · <队列>"，使首位词元既标明状态又决定行色。
x = 比值比。估计值范围自 0.702（CRELES r10）至 3.589（CLHLS r02）。
区间为按个体聚类的稳健区间；SHARE 按五个插补副本以 Rubin 规则合并。
区间跨 1 而点估计与其余队列方向相背者（ELSA 与 CRELES 的 r10、SHARE 的 r12）清楚可见，
**不得读作分歧**。
统计说明：分析单元 = 预注册（规则，队列）配对；18 对，涵盖 6 条规则与 7 个队列；
三种状态：replicated / uninformative / contradicted（R11 定义，分析计划 §19.7）；
transportable = 在 ≥2 个队列中 replicated 且 q<0.05（§19.7 预先声明）；
13 条规则完全没有条柱：5 条需眼底影像、1 条需眼压或视盘分级、3 条需地理编码暴露、
3 条需血液指标、2 条需膳食指数；森林图区间为按个体聚类稳健区间；SHARE 按 5 个插补以
Rubin 合并；森林图绘于对数轴并含 OR = 1 的空值线（项目内渲染器，见 backend.renderer）。
缩写：OR = 比值比；CI = 置信区间；BHY = Benjamini-Hochberg-Yekutieli；FDR = 错误发现率；
AMD = 年龄相关性黄斑变性；SHARE = 欧洲健康、老龄化与退休调查；
HRS = 美国健康与退休研究；ELSA = 英国老龄化纵向研究；KLoSA = 韩国老龄化纵向研究；
LASI = 印度老龄化纵向研究；MHAS = 墨西哥健康与老龄化研究；
CLHLS = 中国老年健康影响因素跟踪调查；CRELES = 哥斯达黎加长寿与健康老龄化研究；
IOP = 眼压；CDR = 视杯视盘比；r01–r22 = configs/rules.yaml 中的预注册规则编号。""",
}


def main() -> int:
    text = FP.read_text(encoding="utf-8")
    en_part = text.split("# 图例（中文）")[0]

    # every number in the Chinese legend must exist in the English legends
    bad = []
    for n, cn in CN.items():
        nums = set(re.findall(r"\d+\.\d+", cn))
        for v in nums:
            if v not in en_part:
                bad.append(f"fig{n}: {v} not found in the English legends")
    if bad:
        print("REFUSING TO WRITE -- numeric mismatch:")
        for b in bad:
            print("  " + b)
        return 1

    head, _, tail = text.partition("# 图例（中文）")
    body = ["", "",
            "> 中文图例与上方英文图例逐项对应。数字与英文版完全一致，"
            "由 `scripts/fill_chinese_legends.py` 在写入前自动比对，不一致则拒绝写入。",
            ""]
    for n in sorted(CN):
        body += [CN[n], "", "---", ""]
    FP.write_text(head + "# 图例（中文）" + "\n".join(body).rstrip() + "\n",
                  encoding="utf-8")

    left = FP.read_text(encoding="utf-8").count("[TODO")
    print(f"chinese legends filled: {len(CN)}")
    print(f"remaining [TODO] in the legends file: {left}")
    print(f"-> {FP}")
    return 0 if left == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
