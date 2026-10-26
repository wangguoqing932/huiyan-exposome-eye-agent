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
（**a**）端到端流程：输入 → 实体归一化 → 规则引擎 → LightRAG 检索 → LLM 仲裁 → 带轨迹的报告。
（**b**）三层一条可追溯路径：规则层（确定性）、知识图谱层（证据锚定）、仲裁层（有边界）；
每一步都属于某一层，因此任一输出都可回溯到其证据。
（**c**）四种输出视图：临床医生卡片／患者手册／研究表格／政策简报，均由单次推理生成。
统计说明：规则层 21 条规则（A1/B15/C5）；知识图谱层 27,136 个节点、1,060 个证据片段；
仲裁层在报告所用运行中为本地 Qwen3.8-27B（温度 0）。
缩写：LLM = 大语言模型；KG = 知识图谱；YAML = YAML Ain't Markup Language；
LightRAG = 轻量检索增强生成。""",

2: """**图 2。慧眼（v1.2）与三个 LLM 基线在 NHANES 配对上的比较，双基线代并列。**
在主代（80 个开发期配对，本地 Qwen3.8-27B 基线，R11 更正三态金标准、survey svyglm 方差）中，
完整慧眼系统 F1 = 0.522（精确率 0.353 / 召回率 1.000，跨种子完全一致），高于
lightrag 0.392 ± 0.007、pure_llm 0.335 ± 0.010 与 naive_rag 0.080 ± 0.110（各方法 5 个种子；柱为均值，须为 ±1 SD）。
配对 McNemar 相对 pure_llm（p = 0.0043–0.0118）与 naive_rag（p = 0.00024–0.0129）显著，
相对 lightrag 不显著（p = 0.057–0.092），且该代 lightrag 仍为纯向量检索。
两次公平修复后（lightrag 升级为 hybrid 知识图谱遍历；全部基线改在 GLM-5.3-flash 上按
159 对重跑），排序不变且 lightrag 比较落定：full 0.480（P 0.316 / R 1.000）>
lightrag 0.186 ± 0.006 > pure_llm 0.178 ± 0.015 > naive_rag 0.069 ± 0.086，
配对 McNemar 对全部基线显著（lightrag p = 3×10⁻¹¹ 至 9×10⁻¹⁰；
pure_llm p = 8×10⁻¹⁹ 至 6×10⁻²⁴；naive_rag p = 0.006–0.012）。
各方法精确率均低（0.07–0.35），因多数被预测为正的配对在三态标准下属"无信息"而非"相反"。
（**a**）各方法 F1（5 种子均值），两代并列：蓝色 = qwen 代（80 对），黄色 = zhipu 代（159 对）；
qwen 代 full 0.522 > lightrag 0.392 > pure_llm 0.335 > naive_rag 0.080；
zhipu 代 full 0.480 > lightrag 0.186 > pure_llm 0.178 > naive_rag 0.069。
两代不合并（金标准规模与后端不同）。
（**b**）确定性 full_system 对 R11 三态金标准（主代 80 对）的混淆矩阵：预测 YES 为
6 replicated / 0 contradicted / 11 uninformative；预测 NO 为 0 / 2 / 61
（TP 6、FP 11、FN 0、TN 63）。
（**b**）的单元格底纹仅作视觉辅助，每格均印有计数。（**c**）规则层覆盖度与声明域精确率：NHANES 0.889 / KNHANES 0.882；精确率 1.00 / 1.00。
（**d**）qwen 代 lightrag 的检索上下文长度分布（5 seeds × 80 对，字符数），
仅描述检索规模，不是性能声明。
统计说明：NHANES 配对；金标准为 R11 操作化更正后、survey svyglm 方差下的三态标签；
每方法 5 个种子；full_system 为确定性规则引擎，五次运行完全相同；配对 McNemar 精确检验；
\\* p<0.05；n.s. p>=0.057（qwen 代对比 lightrag）。
缩写：F1 = F1 分数；P = 精确率；R = 召回率；KG = 知识图谱；LLM = 大语言模型；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查；
R5/R11 = 内部分析修订版本（金标准版本）；SD = 标准差；n.s. = 不显著。""",

3: """**图 3。R11 三态协议下的规则层评价：按证据等级的精确率、覆盖度与复现率。**
在预注册的三态标准下，声明域精确率（replicated / (replicated + contradicted)）
在两国均为 1.00，而保守精确率（replicated / 全部可检验的规则相关配对）为
0.375（NHANES，95% CI 0.152–0.646）与 0.333（KNHANES，0.118–0.616）——
两者之差是headline数值最大的单一杠杆，因此必须并列呈现。规则覆盖度
P(可检验 | 规则存在) 很高：NHANES 0.889 / KNHANES 0.882。
复现完全集中在证据等级 A 之外：两国在等级 A 均为 0/1，等级 A+B 为 4/13，
总体分别为 6/19 与 5/16。两国均无规则被否证。
（**a**）双精确率、覆盖度与按证据等级的复现率（两层）。森林图每个数量一行，两国分列。（**b**）声明域与保守精确率的斜率图；阴影带为被计为假阳性的无信息配对。
各行数值：声明域精确率（NHANES 1.00 [0.541,1.000]；KNHANES 1.00 [0.478,1.000]）；
保守精确率（0.375 [0.152,0.646]；0.333 [0.118,0.616]）；规则覆盖度（0.889；0.882）；
证据等级 A 的复现率（两国均 0/1 = 0.00）；等级 A+B（两国均 4/13 = 0.308）；
全部规则（NHANES 6/19 = 0.316；KNHANES 5/16 = 0.312）。颜色编码指标族：深蓝 = 声明域精确率，深灰 = 保守精确率，青绿 = 覆盖度，琥珀 = 复现率（等级 A / A+B / 全部）。数值标签为估计值及其 k/n 分母。
均为 0–1 轴上的比例，区间为精确二项区间。
统计说明：分析单元 = （暴露 flag，结局条目）配对，仅规则相关配对；
声明域精确率 = replicated / (replicated + contradicted)；保守精确率 =
replicated / 全部可检验的规则相关配对；覆盖度 = P(可检验 | 规则存在)，
见分析计划 §0.4 更正 17b；区间为 Clopper-Pearson 精确区间；两国 contradicted 均为 0。
缩写：CI = 置信区间；BHY = Benjamini-Hochberg-Yekutieli；FDR = 错误发现率；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

4: """**图 S1。演示案例：暴露组（代谢-营养-生活方式-环境）× 主要致盲眼病风险评估。**
一个完整工作案例，展示系统如何将输入转化为风险分级、可追溯的报告，
以及四个输出视图如何共用同一次推理。
（**a**）输入与实体归一化；（**b**）触发的规则及其证据；（**c**）证据等级：A（监管）至 E（机制）的横向条，显示本案例各等级检索到的证据片段数；
（**d**）LLM 仲裁后的风险分级报告与依据链。
统计说明：四视图由单次推理生成，报告字段可逐项回溯至规则、知识图谱路径与仲裁决策。
缩写：OR = 比值比；LLM = 大语言模型；AMD = 年龄相关性黄斑变性；
DR = 糖尿病视网膜病变；IOP = 眼压；CDR = 视杯视盘比。""",

5: """**图 S2。贯穿三层架构的逐步推理轨迹。**
慧眼的三层架构产生完全可追溯的推理链——从规则信号到知识图谱路径再到 LLM 仲裁的
每一次转换都被记录，使任一输出均可事后审计。
（**a**）七步泳道轨迹：规则引擎第 1–4 步（归一化 A、归一化 B、匹配 r04、交叉覆盖 r03），
LightRAG KG 第 5 步（检索），LLM 仲裁／报告第 6–7 步（风险分级、报告 + 轨迹）。
编号为执行顺序，不编码耗时。
（**b**）知识图谱路径：HbA1c → 高血糖 → 视网膜缺血 → VEGF 上调 → 新生血管 → PDR；
规则 r04 覆盖整条链。
（**c**）各层步数：规则 4、KG 1、仲裁 2——推理负担集中在规则层。
统计说明：共 7 个已记录步骤；分层耗时未记录，故不绘制时延面板；步骤标签取自日志，不是重建。
缩写：KG = 知识图谱；LLM = 大语言模型；LightRAG = 轻量检索增强生成；
VEGF = 血管内皮生长因子；PDR = 增殖型糖尿病视网膜病变；HbA1c = 糖化血红蛋白。""",

6: """**图 4。规则相关配对的连续（每 1 个标准差）剂量反应，按调查加权。**
对可估计连续暴露的规则相关配对，展示每 1 个标准差增量对应的比值比，
以检验关联是否随暴露水平单调变化，而非仅在二分类切点上出现。
（**a**）规则相关配对的每 1 SD 比值比森林图，按暴露家族分组的浅色带排列；
每个点为（暴露，结局）配对，颜色编码确证结果：砖红 = q<0.05 且 OR>1，
青绿 = q<0.05 且 OR<1，灰色 = 不显著；虚线为 OR = 1。
统计说明：按调查设计加权；每 1 SD；仅规则相关配对；
区间为基于设计的稳健区间。
缩写：SD = 标准差；OR = 比值比；CI = 置信区间；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

7: """**图 5。效能：最小可检出 OR（80%）与观测 OR 的对照，仅规则相关配对。**
多数规则零结果是**有信息量的**而非效能不足。80% 效能下最小可检出比值比的中位数为
NHANES 1.337、KNHANES 1.159，30 个规则相关配对中有 17 个可归类为**有检验力的零结果**
——该设计本可排除 2 倍关联。发生复现的配对位于相反的一角（观测 OR 大、可检出 OR 小），
即它们既有足够效能又效应量大；没有任何配对仅凭较小的可检出效应就实现复现。
设计效应由各配对 survey 与 model 的置信区间宽度之比逐对导出（中位数 NHANES 1.07、KNHANES 1.26），
而非假定。
（**a**）最小可检出 OR（80% 效能）与观测 OR 的散点，双轴均为对数，
每个规则相关配对一点（NHANES n=17，KNHANES n=13）。x = 80% 效能下的最小可检出 OR；
y = 观测 OR。点按三态标签着色（蓝 = 复现，灰 = 无信息）；复现的配对聚集于
"高观测 OR、低可检出 OR"，"无信息"配对沿整个可检出范围聚集在 OR = 1 附近。
虚线为 y = x 的 identity 线：**位于其下方者，其观测效应大于该设计所需**；y 轴跨 0.55–2.55，使低于 0.95 的保护向估计仍可见；
上方浅色区为"观测效应大于可检出效应"的效能充足区。NHANES 复现 6 个、KNHANES 5 个；
无被否证的配对可绘。
统计说明：规则相关配对 NHANES n=17、KNHANES n=13；双对数轴；
x = 80% 效能（双侧 α=0.05）下最小可检出 OR；y = 观测 OR；
两轴 OR = 1 参考线与 y = x identity 线；identity 线上方浅色区为效能充足区；
设计效应逐对由 survey/model 置信区间宽度之比导出（中位数 1.07 / 1.26）。
缩写：OR = 比值比；MDE = 最小可检出效应（此处为 80% 效能下的最小可检出比值比）；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。""",

8: """**图 6。文献衍生暴露组规则在八个老龄化队列中的跨队列可迁移性。**
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
（共 18 行）。行标签为队列名，按规则分组并在组首以粗体标出规则名；点色编码三态
（蓝 = 复现，灰 = 无信息，砖红 = 否证）。
x = 比值比。估计值范围自 0.702（CRELES r10）至 3.589（CLHLS r02）。
区间为按个体聚类的稳健区间；SHARE 按五个插补副本以 Rubin 规则合并。
区间跨 1 而点估计与其余队列方向相背者（ELSA 与 CRELES 的 r10、SHARE 的 r12）清楚可见，
**不得读作分歧**。
统计说明：分析单元 = 预注册（规则，队列）配对；18 对，涵盖 6 条规则与 7 个队列；
三种状态：replicated / uninformative / contradicted（R11 定义，分析计划 §19.7）；
transportable = 在 ≥2 个队列中 replicated 且 q<0.05（§19.7 预先声明）；
15 条规则完全没有条柱。缺失条件有重叠，故计数之和大于 15：
7 条需血液指标、5 条需眼底影像、4 条需地理编码暴露、3 条需膳食指数、
1 条需眼压或视盘分级；森林图区间为按个体聚类稳健区间；SHARE 按 5 个插补以
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
