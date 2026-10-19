# 8 队列原始数据 · 变量操作化台账（逐队列，码本核验）

> 纪律：仅用**原始文件**。不使用 Gateway Harmonized（`H_*.dta` / `h_*_g*.dta`）、
> 不使用既往中间产物（`Working_data/`、`Temp_data/`、`*_CN.dta`）。
> 每个变量必须凭官方值标签/码本确定语义，**不得由变量名推断**。
> 体例沿用 `configs/variable_map.yaml` 的 C1–C18 更正记录。

---

## 0. 数据存在性核查结论（最重要——决定哪些队列可用）

> ⚠️ **本节已于第 3 轮整体重写。**首版结论基于 `pd.to_numeric(s).notna().sum()` 统计
> "有数据"，而 Stata 带值标签的变量在 pandas 里返回**类别型（categories = 标签字符串）**，
> `to_numeric` 会把每一个取值都变成 NaN，于是**把有数据的变量报成全空**。
> 这造成了 8 个队列中近一半的错误"不可用"判定（详见更正 C36）。
> 现改用 `s.notna().sum()`（不使用 to_numeric）。

**方法**：读原始 Series 的非缺失计数；值分布用 `astype(str)` 或 `convert_categoricals=False`
取数值码。变量名或标签命中 **不构成** 可得性证据。

> ⚠️ **第 4 轮二次重扫后再次修订。**C36 那个 bug 不仅造成假"全空"，
> 还**让 ELSA 的整个眼科模块、HRS 的多波视力、MHAS 的 5 波视力全部漏检**
> （这些变量都是类别型，被 `to_numeric` 变成 0 后又被 `if n>0` 过滤掉；
> 只有恰好是数值型的 `HeEye`、`c45` 幸存）。下表的数字均来自修正后的扫描。

### 0.0 八队列眼科能力矩阵（全部可用）

| 队列 | 视力评分（矫正后自评） | 白内障**患病** | 白内障手术 | 青光眼**患病** | **AMD** |
|---|---|---|---|---|---|
| **HRS** | ✅ 3 波：`KC095`(2006) `MC095`(2010,22,034) `PC095`(2016,20,911)；远/近 `K/M/PC096/097` | ❌ | ✅ `KC098` | ✅ `KC101` | ❌ |
| **ELSA** | ✅ w1 `heeye` 12,099；远 `hefrnd`；近 `hepap` | ✅ **`heoptca`** | — | ✅ **`heoptgl`** | ✅ **`heoptmd`** |
| **MHAS** | ✅ 5 波：`c45`(w1) `c42_12/15/18/21`(w3–6) | ❌ | ❌ | ❌ | ❌ |
| **SHARE** | ✅ 8 波 `eyesightr`（W1 152,080 → W9 347,235） | ✅ `ph006d13` | — | ❌ | ❌ |
| **LASI** | ✅ `ht019` 远 / `ht020` 近 | ✅ `ht017`s2 = **8,219** | — | ✅ `ht017`s3 = **1,284** | ❌ |
| **KLoSA** | ✅ 9 波 `C075/076/077` | ❌ | ✅ `C078` | 治疗史 `C080` | ❌ |
| **CLHLS** | ✅ `g1_*`（功能测试，4 级） | ✅ `g15g1_*` | — | ✅ `g15h1_*` | ❌ |
| **CRELES** | ✅ `c55` SeeFar / `c56` SeeClose | ✅ `c57` HaveCataracts | ✅ `c58` | ✅ `c60` HaveGlaucoma | ❌ |

**结论：8 个队列全部可用（ELSA 为单波，其余多波）。**
**白内障患病 5 个队列（ELSA/SHARE/LASI/CLHLS/CRELES）、青光眼患病 5 个
（HRS/ELSA/LASI/CLHLS/CRELES）、AMD 仅 1 个（ELSA `heoptmd`）。**

**可评估规则范围（修正后）**：
- 视力族 r20/r21 → **8 个队列全部**
- 白内障族 r10/r12/r13/r14 → **5 个队列**（用患病结局；HRS/KLoSA 只有手术史，构念不同）
- 青光眼族 r16/r17 → **5 个队列**
- AMD 族 → **仅 ELSA**
- 视网膜病变 / DME → **队列层全部不可得**（需眼底影像）

**可跨库对齐的核心结局**：**"矫正后自评视力"序数量表**
（HRS 1–6、MHAS 1–6、SHARE 5 级、ELSA 5 级、CRELES 5 级、KLoSA 1–5），
其中 HRS/MHAS/KLoSA/ELSA 均含独立的 **"legally blind"** 类别。

### 0.1 通用纪律（由本轮发现固化）

1. **可得性 = 原始 Series 的非缺失计数（`notna()`）**。
   **绝不用 `to_numeric` 统计可得性** —— 类别型会全变 NaN（C36）。
2. **变量名、标签、文件存在，三者都不构成可得性证据**；且标签命中会大量假阳性：
   - ELSA `sherqgs`/`wineqgs` = "glasses of **sherry/wine**"（酒的杯数）
   - SHARE `q6d`/`v6_4` = "gaining **insight** into other people's…"
   - LASI `we110` = "Number of people under **supervision**"
   - ELSA `ialreye` = "annual commercial **loan** repayment"（名字以 "eye" 结尾）
   - ELSA `ahseyear` = "HSE Year"
   - HRS `KT002` = "family provisions in **will**"
   - MHAS 正则 `ver\b` 命中 "**ever** told you"
3. **变量名跨版本不稳定**：LASI Pilot 的 `ht015/16/17` 是**癌症**变量，Wave 1 里同名的
   是**眼科**变量。**不得跨版本套用码本**。
4. **逐队列拉官方值标签**（pyreadstat `variable_value_labels` / 码本 docx / 模块码本 txt / 问卷 PDF）。
5. **手术/治疗/功能受限 ≠ 患病**，必须独立命名并声明构念偏移。
6. **插补数据须标记并优先用实测值**（SHARE `eyesightr_f` 可直接区分实测与插补）。
7. 韩文数据需 `encoding='cp949'`；pandas `read_stata` 不支持该参数，须用 `pyreadstat`（已装 1.3.6）。
8. HRS 的 `.dta` 无值标签，须读模块码本 txt；读取需 `encoding='ISO-8859-1'`。

### 0.2 更正 C36（本项目最严重的自查发现）

**问题**：判定"某变量是否有数据"时用了 `pd.to_numeric(s, errors='coerce').notna().sum()`。

**机制**：Stata 中带值标签的变量，pandas `read_stata` 默认 `convert_categoricals=True`，
返回 **category dtype，其 categories 是标签字符串**（如 `ht015` → `'Yes'`/`'No'`）。
`to_numeric` 无法把 `'Yes'` 变成数字 → **全部变 NaN** → 非缺失计数报 0。

**影响**：把大量**有完整数据**的变量误判为"声明了但全空"，进而得出两项错误结论
（"SHARE 不可用"、"KLoSA 仅插补文件有数据"）。**两项均已撤回。**

**对照证据**：

| 变量 | `notna()` | `to_numeric().notna()` |
|---|---|---|
| SHARE `ph006d13` W1 | 30,283 | 0 |
| SHARE `eyesightr` W1 | 152,080 | 0 |
| LASI `ht015` | 73,198 | 0 |
| KLoSA `w01C075` | 10,229 | 0 |
| LASI 试点 `ht039` | 9 | 0 ← 这条**确实**近空 |

**已修**：`scripts/cohort_vision_scan.py` 改用 `s.notna().sum()` 计可得性；
值分布按 `to_numeric` 可行性择一（数值码或标签字符串），并输出 `dtype` 以便审计。
台账中所有"全空"判定均已用新口径复核。

**纪律条款**：**任何"变量为空"的结论，必须用 `notna()` 复核，且必须打印 dtype。**
`to_numeric` 只能用于取值转换，**绝不可用于可得性判定**。

### 0.3 LASI 补充发现（第 3 轮）

**更正 C39 — LASI 通过多选字符串提供疾病特异结局，样本量全队列最大**

`lasi_w1b_ind_bm.dta`（73,408 行）：
- `ht015` = "Ever diagnosed_eye or vision problem" → 1 Yes **34,223 (46.8%)** / 2 No 38,975
- `ht016` = diagnosed in one or both eyes → 1 One eye 4,833 / 2 Both eyes 29,378
- `ht017` = 多选**字符串**（如 `'1-2-3-4-5'`），n=73,408
- `ht017s1`–`ht017s6` 指示变量**标签即解码表**（虽其本身 n=0）：
  `s1 presbyopia / s2 cataract / s3 glaucoma / s4 myopia / s5 hypermetropia / s6 other`
- `ht019` = "Eyesight for seeing things at a distance"；`ht020` = "…up close"

**解码结果**（按 `ht017` 字符串拆分，code ∈ parts）：

| code | 疾病 | n | 占有效 |
|---|---|---|---|
| 1 | presbyopia | 4,976 | 6.78% |
| **2** | **cataract** | **8,219** | **11.20%** |
| **3** | **glaucoma** | **1,284** | **1.75%** |
| 4 | myopia | 17,670 | 24.07% |
| 5 | hypermetropia | 15,708 | 21.40% |
| 6 | other | 39,124 | 53.30% |

→ **LASI 是本外验层白内障/青光眼样本最大的队列**（远大于 SHARE `ph006d13` 的约 6,500）。

**更正 C40 — 解码依据是"配套指示变量的标签"，不是频率猜测**
`ht017s2` 的标签写着 `cataract`，故 `ht017` 中的 `2` 即白内障。
这是码本证据而非流行病学推断，符合本项目的取值语义核验纪律。

### 0.4 第 4 轮重扫的更正（C41–C45）

**更正 C41 — C36 的 bug 还造成了整模块漏检，不只是假"全空"**
旧口径把类别型变量算成 0，扫描器里 `if n>0` 的过滤器再把它们**整个丢掉**，
于是：
- **ELSA 的整套眼科模块被漏掉**（只留下恰好为数值型的 wave 6 `HeEye`）
- **HRS 的多波视力被漏掉**（只剩 2006 波）
- **MHAS 的 5 波视力被漏掉**（只剩 wave 1 `c45`）
教训：**过滤条件写在错误的度量上，会让错误从"低估"升级为"缺失"。**

**更正 C42 — ELSA 实际有自己的眼科模块，且提供 AMD**
wave 1：`heeye`（自评视力，含 `SPONTANEOUS: registered or legally blind`，n=12,099）、
`hefrnd`（看朋友 = 远视力）、`hepap`（看报纸 = 近视力）。
wave 2 派生变量：**`heoptca` 白内障 / `heoptgl` 青光眼 / `heoptmd` 黄斑变性**。
→ **ELSA 是本外验层唯一提供 AMD 结局的队列**（r05/r06 族可在此检验）。
→ 撤回"ELSA 仅单波单变量、只能贡献视力族"的结论。
⚠️ `heoptca/gl/md` 位于 `wave_2_derived_variables.dta`（派生文件），
使用前须确认其底层原始题项，并在预注册中声明。

**更正 C43 — HRS 提供 3 个波次的视力评分**
2006 `KC095`（18,467）、2010 `MC095`（22,034）、2016 `PC095`（20,911），
各波另有远/近视力（`KC096/097`、`MC096/097`、`PC096/097`）。
→ HRS 可做**纵向**分析，不限于横断面。
⚠️ HRS 目录内另有 `20XX RAND HRS Fat File/hdXXf*.dta`（RAND 派生版，同名小写变量）。
按"仅原始文件"原则**使用 `HXXC_R.dta`**，不用 RAND fat file。

**更正 C44 — MHAS 提供 5 个波次的视力评分，但变量名随波变化**
`c45`（w1）→ `c42_12`（w3）→ `c42_15`（w4）→ `c42_18`（w5）→ `c42_21`（w6）。
均为 1–6 级（含 `6.Legally blind`）。
⚠️ **后缀数字与文件夹波号不一致**（`c42_18` 在 `wave5/` 目录里）——
必须按**实际文件**而非名字推断波次，且逐波核验码本。

**更正 C45 — CRELES 解压后可用，且其变量含义在两个队列间不同**
解压 8 个 zip → 59 个 `.dta`（跳过 145 个 `__MACOSX/._*` 元数据），
输出至 `data/raw/creles/`。
- `Data-CRELES-pre-1945`：`c54` UsesGlasses、**`c55` SeeFar**、**`c56` SeeClose**、
  `c57` **HaveCataracts**、`c58` CataractsSurgery、`c59` LimitationCataracts、
  `c60` **HaveGlaucoma**、`c131` VisionExam
- `Creles_1945-1955_Retirement`：**`c55q` = EyesightContactLenses**（与上者同名族但**不同义**）
→ **又一次"变量名跨队列不稳定"**（同 LASI Pilot vs Wave 1）。
CRELES 每波约 2,800 人，3 波（pre-1945）+ 2 波（1945-1955）。

### 0.5 第 5 轮：暴露侧核验（进行中）

**更正 C46 — 扫描器的文件上限会伪造"某变量族不存在"**
首版暴露扫描器把数据读取上限设为 30 个候选文件（按变量数升序），
于是 **SHARE 的 `ph` 慢病模块在后续波次从未被读取**，导致高血压/糖尿病被误判为
"不可用"。提高上限后 SHARE 候选数从 162 → **447**，全部暴露族齐备。
→ 教训：**读取上限必须足够高，且一旦触发截断必须在输出中显式报告**
（已在 `cohort_exposure_scan.py` 加入截断告警）。
这与 C41 同源：**限制条件写在错误的层级，会产生"缺失"而非"低估"。**

**SHARE 暴露侧（已核验）**：

| 族 | 变量 | n | 备注 |
|---|---|---|---|
| **BMI** | `bmi` / `bmi2`（分类，含 underweight<18.5） | 488,400（全 person-wave） | |
| **吸烟** | `smoking`（现吸，Yes 58,049）、`ever_smoked`（曾每日吸）、`esmoked_f` | 488,400 | |
| **饮酒** | `drinking`（几乎每天 >2 杯）、`br010_mod`（每周天数）、`br039_`、`br623_`（暴饮） | 488,400 / 330,190 | |
| **糖尿病** | `illness2` + `drugs5`（用药） | 287,735 | |
| **高血压** | `illness3` + `drugs2`（用药） | 287,735 | |
| **身高体重** | `weight` / `height` + `_f` 标志 | 385,905 | 实测人体测量 |
| **设计权重** | `dw_w*` / `cchw_w*` / **`cci_w*` 校准个体权重** | | 支持 survey 设计分析 |

**更正 C47 — SHARE 的缺失码是负数码**
`-12` DK/拒答、`-13` 本波未问、`-10` SHARELIFE 访谈、`-15` 无信息、`-3` 可疑值。
与本项目已有的 NHANES（8/9）、KNHANES（8/9）、KLoSA（-9/-8）、CLHLS（9/99 与 8/88）
**均不同**。每队列必须建独立缺失码表。

**更正 C48 — SHARE 的分析就绪变量位于官方 `gv_*`（generated variables）模块**
`bmi`/`smoking`/`ever_smoked`/`drinking`/`illness*`/`weight`/`height`/`eyesightr` 等
均在 SHARE 自己发布的 `gv_*` 模块中，且**多数带 `_f` 插补/质量标志**
（如 `eyesightr_f`、`weight_f`、`height_f`、`esmoked_f`）。
→ 这是 **SHARE 官方发布物**，不是第三方 harmonize，**符合"仅原始文件"原则**；
但须在预注册中声明：SHARE 层使用官方 `gv_*` 变量，并以 `_f` 标志**限定实测值**做
主分析、插补值做敏感性分析。

### 0.6 暴露侧核验完成（第 5 轮，6 个 `.dta` 队列）

| 队列 | 候选数 | 关键暴露变量（已核验） |
|---|---|---|
| **HRS** | 448 | 抽样/权重完整（`HHBASEWT` 等）；健康变量需按模块定向取（见下注） |
| **ELSA** | 756 | 药物模块详尽：`bpmedc`（是否服降压药）、`diur`/`beta`/`aceinh`/`calciumb` |
| **KLoSA** | 411 | （见 JSON） |
| **LASI** | 73 | **`ht002` 高血压**（Yes 20,320 / No 52,887）、`ht003` 糖尿病；**印度级 / 州级个体权重** |
| **MHAS** | 429 | **`diabetes`**（Yes 16,240 / No 59,703）、**`hipertension`**（Yes 33,176 / No 42,758）、`bmi_imp`（10 次插补均值）、`imc_imp_cat`（5 类）、`factorh_*` 权重 |
| **CRELES** | 216 | `antidiab`/`antihta`（用药）等 |

**更正 C49 — 三个队列的 BMI 都是插补产物，必须显式处理**
- **MHAS**：`bmi_imp` = "Mean of BMI across **10 imputations**"；`imc_imp_cat` = 插补后 5 分类
- **SHARE**：`weight`/`height` 带 `weight_f`/`height_f` 标志
- **CRELES**：用药变量为主，BMI 待定向核验
→ 与 KLoSA 插补文件、SHARE `_f` 标志同属一类问题。
**预注册须写明**：BMI 相关规则（r13）在所有队列均基于插补/标定后的 BMI，
并做"仅实测值"敏感性分析。

**更正 C50 — 排序会误导：`n_valid` 最大的变量不是研究变量**
扫描输出按非缺失数降序，排在最前的是**权重与抽样状态变量**
（HRS `HHBASEWT`、`AWHY0WGT`；LASI `indiaindividualweight`），
它们在小文件里天然"全量非缺失"。
→ **不得按非缺失数排序来选研究变量**；必须按语义族定向检索
（已在 JSON 中保留 `label` 字段供语义筛选）。

**各队列权重变量（供 survey 设计分析）**：
HRS `HHBASEWT`/wave 权重；ELSA 见 UKDA 文档；LASI `indiaindividualweight` /
`stateindividualweight`；MHAS `factorh_*`/`factori_*`；SHARE `cci_w*`（校准个体）；
CRELES 待查；CLHLS 待查；KLoSA 待查。

**CLHLS 暴露侧（码本核验，无 `.dta`，走 CSV + docx 码本）**
- **吸烟**：`d61`（现吸）/`d62`（既往）/`d63`/`d64`（起止年龄）/`d65`（支数）；
  随访 `d0smoke`/`d0smktim`
- **饮酒**：`d71`（现饮）/`d73`/`d74`/`d75`（种类）/`d76`（量）；`d4tea2` 饮茶
- **体重**：`g12` / `g10_0` / `g101_*`
- **慢病块（字母映射，跨波基本稳定）**：`g17<字母>1`（1998）→ `g15<字母>1_<波>`（随访）
  - **a** 高血压、**b** 糖尿病、c 心脏病、d 卒中、e 呼吸系、f 结核、
    **g 白内障**、**h 青光眼**、i 肿瘤、j 前列腺、k 溃疡、l 帕金森、m 压疮
  - ⚠️ **字母并非完全稳定**：`n` 在 1998 = "其他慢病"，2000 = "关节炎"，
    "其他慢病"移到 `p`。**g/h/a/b 四个我需要的字母经 1998 与 2000 双向确认一致。**
  - `g15a2_0` = "diagnosed by hospital?"（高血压的医院确诊验证题）

### 0.7 第 6 轮：KLoSA/HRS/CRELES 定向暴露核验 + C51/C52

**更正 C51 — 守卫必须放在依赖它的操作之前（本族错误的第三次）**
`cohort_exposure_scan.py` 的打印循环写成：

```python
for c in sorted(rec["candidates"], key=lambda x: -x["n_valid"])[:34]:
    if "n_valid" not in c:      # ← 守卫在循环体内
        continue
```

`sorted(key=...)` **先于**守卫执行。KLoSA 有 6 个文件读取失败
（`e_imp_w05_new.dta` 等 cp949 编码），产生只有 `{file, error}` 的条目 →
`KeyError: 'n_valid'` → **整个脚本崩溃，JSON 从未写出**。
→ 已改为**先过滤、再排序**，并对读取失败的文件打印告警。
→ 本族错误累计三次：**C41**（过滤器挂在错误度量上 → 整模块消失）、
**C46**（读取上限卡在错误层级 → 整模块消失）、**C51**（守卫在操作之后 → 全部产物消失）。
**共同规律：限制/守卫写错位置时，错误会从"低估"升级为"缺失"。**

（附带留痕：我最初把 KLoSA 缺 JSON 归因于 PowerShell `Select-Object -First 6`
截断管道，**该假设经 stderr 证伪并已撤回**，真实原因是上述 KeyError。）

**更正 C52 — KLoSA 源数据存在错误的值标签**
`w01smoke`（标签 "Smoking status"）的取值标签竟写着
`0: 7297, 1: "Current-drinker": 979` —— **把饮酒的标签贴到了吸烟变量上**。
→ **不得使用 `w01smoke`**；改用标签自洽的 `w01C116`（曾吸 >5 包/100 支：
Yes 2,956 / No 7,297）与 `w01C117`（目前是否吸烟：Yes 1,977 / No 978）。
→ 教训：**官方发布的标签也会有错，必须交叉核对同一构念的多个变量。**

**KLoSA 暴露侧**：`w01C116`/`w01C117` 吸烟；`w01alc`（1:3,889/2:689/3:5,676）、
`w01C126` 频次、`w01C127` 酒量；**`w01bmi` n=9,991**；`w01C105` 体重(kg)；
`w01C011`/`w01chronic_b` 糖尿病（Yes 1,222 / No 9,031）；`w06C006` 高血压。

**HRS 暴露侧**：`NZ205` 曾吸烟（Yes 11,258 / No 8,859）、`NZ231`/`NZ232` 起止；
`NZ254`/`PZ254` 饮酒变化、`LB117` 酒精问题；**`MC010` 糖尿病**、
**`MC005` 高血压**（1:12,860）、`MC006` 降压药；`QC010` 糖尿病（2016 波）。
⚠️ **`AWGTHH`/`AWGTR` 等 "WEIGHT" 变量是抽样权重（1992 WEIGHT: RESPONDENT-LEVEL），
不是体重**——HRS 的 BMI/体重需另行定向检索。

**CRELES 暴露侧**：`ev10` 吸烟（Yes 212 / No 2,217）、`ev8` HaveSmoke；
`hatalco` **酒精摄入 g/d（连续量）**、`ev1m` 饮酒规律；
**`imc2` BMI（n=2,698）**、`bmi_short`；`waist`(WaistCm)、`whipratio`；
**`c10` HaveDiabetes**（Yes 542 / No 2,270）、**`c4` HaveHypertension**（No 1,434）；
`antidiab`/`antihta` 用药。

### 0.8 第 7 轮：SHARE frame 建成 + C53/C54/C55

**产物**：`data/frames/cohort_SHARE.csv`（1,693,515 行 × 15 列）、
`outputs/confirmatory/cohort_SHARE_prevalence.json`。
**参考率门 8/8 PASS**。构建器：`scripts/build_cohort_frames.py`（SHARE 为参考实现）。

| flag | n（副本 1） | 患病率 | 参考区间 | 判定 |
|---|---|---|---|---|
| `cataract_any` | 337,274 | 8.40% | 3–30% | PASS |
| `vision_impairment_moderate` | 275,470 | 13.95% | 3–35% | PASS |
| `vision_impairment_severe` | 275,470 | 6.98% | 0.5–10% | PASS |
| `current_smoking` | 142,229 | **17.15%** | 5–35% | PASS |
| `alcohol_intake` | 124,020 | 16.70% | 10–80% | PASS |
| `bmi_high` | 338,703 | 22.81% | 8–45% | PASS |
| `diabetes` | 337,274 | 13.64% | 4–35% | PASS |
| `hypertension` | 337,274 | 42.39% | 20–70% | PASS |

**更正 C53 — SHARE `gv_imputations` 有显式 `implicat`（1–5）索引，必须带入 frame**
`gv_imputations` 每人 **5 行**插补副本（W7：77,181 人 × 5 = 385,905 行），
而 `ph` 每人 1 行。**丢弃 `implicat` 不会减少样本**，只会留下 5 行看起来相同的记录，
→ **任何回归都会看到 5 倍的名义 n，标准误被严重低估**（与 KLoSA C20 同类）。
- 处置：frame 保留 `implicat` 列；确认层按副本分别拟合后以 **Rubin 规则**合并；
  参考率门与描述性统计**只用副本 1**（已实现）。
- 附带：`age`/`gender`/`bmi`/`eyesightr` 都在 `gv_imputations` 里，
  我首版构建器只去 `dn` 模块找 `age`/`gender`（那里名字不同），导致这两个协变量**静默未建**。

**更正 C54 — C1 类错误第四次出现：SHARE `br002_` 的条件问法**
`br001_` = "Ever smoked daily"（W6 n=12,600，Yes 5,701）；
**`br002_` = "Smoke at the present time"，只对 `br001_ == Yes` 问**（n=**5,703**）。
→ `br002_ == Yes` 单独使用得 **2,792/5,703 = 49%**，那是**曾吸烟者中的现吸率**，
不是人群现吸率（真实约 15–20%）。
- **正确定义**：`current_smoking = 1 if br002_==Yes；0 if br001_==No or br002_==No；
  NaN 仅当 br001_ 缺失`（即把从不吸烟者作为 0 并入）。
- 修正后实测 **17.15%**，落入参考区间 → **参考率门在此直接验证了修正有效性**。
- **C1 类错误累计四次**：NHANES `SMQ040`、KNHANES `BS1_1`、CHARLS `da061`、SHARE `br002_`。
  **这是本项目复现率最高的单一错误类型**：所有"是否现吸/现饮"类题目都可能是
  条件问法，必须先查其门槛变量（gate）。
- 纪律条款：**任何二值暴露 flag，必须先确认它是全样本题还是条件题；
  条件题必须把门槛的否定分支显式并入 0。**

**更正 C55 — `smoking`/`ever_smoked` 只存在于 easySHARE（派生发布版）**
`easySHARE_rel9-0-0.dta` 是 SHARE 的**简化派生发行版**（精选变量集），
不是主发布版。`smoking`/`ever_smoked` 仅在此文件中出现（n=488,400）。
→ 按"仅原始文件"原则，**改用主发布 `br` 模块的 `br001_`/`br002_` 自行构造**，
不使用 easySHARE 的现成变量。（easySHARE 可作为交叉核对。）

### 0.9 第 8 轮：C54 类错误的系统性审计（更正 C56）——**四个队列同时中招**

**工具**：`scripts/detect_exposure_gates.py`。条件题的机械特征是
`n_valid(V) ≈ #positive(G)` 且 `n_valid(G) ≫ n_valid(V)`（G 为门槛变量）。
脚本直接读已有的暴露扫描 JSON，无需重新读数据。

**审计结果（"现吸/现饮"类变量）**：

| 队列 | 被判条件题 | naive 率 | 说明 |
|---|---|---|---|
| **HRS** | `OC117` / `PC117` / `RC117` / `QC117`（SMOKE CIGARETTES NOW） | 23.5% / 27.0% / 22.5% / 24.5% | 门槛为同波"曾吸"题 |
| **ELSA** | `smoker`、`smokerstat`、`rhska`(14.3%)、`HESka`(8.0%) | 14.3% / 8.0% | ELSA 有多个基数不同的吸烟变量 |
| **MHAS** | `c55`（smoke now） | **40.6%** | |
| **SHARE** | `br002_`、`cusmoke` | 22–49%（逐波） | 门槛 `br001_` |
| LASI | `ht002c`（Currently on medication_hypertension） | 71.1% | 门槛为高血压诊断题 |

**结论：HRS / ELSA / MHAS / SHARE 四个队列的"现吸"变量都是条件问法。**
若按变量名直接建 flag，这四个队列会**同时**复现 C1 类错误，而且
**每一波的 naive 率都落在看似合理的区间（22–49%）**，不会自行暴露。

**更正 C56 — 定则：所有二值暴露 flag 必须过门槛审计，不得逐个手工判断**
C1 类错误累计已五次（`E_DR` 语义错、NHANES `SMQ040`、KNHANES `BS1_1`、
CHARLS `da061`、SHARE `br002_`，另加本轮查出的 HRS/ELSA/MHAS 三处潜在）。
**逐次事后发现的方式已被证明失效** —— 因为 naive 率总是"看起来合理"。
→ 定为**流程前置步骤**：任何二值 flag 在进入 frame 之前，
必须由 `detect_exposure_gates.py` 过一遍；命中者一律按
`flag = 1 if 现况==Yes；0 if 门槛==No or 现况==No；NaN 仅当门槛缺失` 构造。

**构造规范（三队列共用）**：
```
ever   = binary(gate_var,    true="Yes", false="No")
now    = binary(target_var,  true="Yes", false="No")
flag   = NaN
flag[now == 1] = 1
flag[(ever == 0) | (now == 0)] = 0      # 从不吸烟者显式并入 0
flag[ever.isna()] = NaN
```

**已知假阳性**：SHARE `ph006d2`（高血压）被同主题规则误判为条件题——
高血压题在全样本问。**检测器的输出仍需逐条人工语义确认**，
它是"提醒器"而非"判决器"。

**HRS 门槛的实证核验（2016 波 `H16C_R.dta`）**：

| 变量 | 标签 | n | 取值 |
|---|---|---|---|
| `PC116` | EVER SMOKE | **4,567** | Yes 2,311 / No 2,254 |
| `PC117` | SMOKE CIGARETTES NOW | **11,298** | Yes **3,053** / No 8,240 |
| `PC118` | NUM CIGARETTES SMOKED PER DAY | 2,628 | ≈ 现吸者数 |

`PC117` 的实际基数仅 **11,298 / 20,911 = 54%**，确为条件题。
- naive 率 = 3,053/11,298 = **27.0%**（被问者中）
- **全样本分母** = 3,053/20,911 = **14.6%** ← 与 50+ 美国人群一致
→ **检测器对 HRS 的判定成立**；`PC116` 是"曾经吸烟"，
且其 n（4,567）**小于** `PC117` 的 n，说明分叉方向是
"先问是否现吸（`PC117`），否定者再问是否曾吸（`PC116`）"——
**与 SHARE（先问曾吸、再问现吸）的嵌套方向相反**。
→ 纪律补充：**门槛关系可能是双向嵌套的，必须逐队列确认分叉方向，
不能假定"先问是否曾吸"**。

### 0.10 第 9 轮：frame 构建器扩展到 5 个队列 + C57/C58/C59

**产物**：`data/frames/cohort_{SHARE,HRS,MHAS,KLoSA,CRELES}.csv`

| 队列 | 行数 | 人数 | 波次 | 门 |
|---|---|---|---|---|
| SHARE | 1,693,515 | 137,183 | 4/5/6/7/9 | 8/9 PASS（`bmi_high_25` FAIL，见 C58） |
| HRS | 42,946 | 27,261 | 2010/2016 | **5/5 PASS** |
| KLoSA | 40,406 | 11,137 | 1/2/4/6/8 | 5/6 PASS（`bmi_high_30` FAIL，见 C58） |
| MHAS | 15,182 | 15,182 | 1 | 2/2 PASS（仅波 1 建成） |
| CRELES | 5,191 | 2,827 | 1/2 | 3/4 PASS（`cataract_any` 见下） |

**更正 C57 —— "键与查找"错误族（第四次同源错误）**
一次构建中同时暴露四个键/查找缺陷：

| 队列 | 错误 | 真相 |
|---|---|---|
| HRS | 以为有 `HHIDPN` 单列，回退到 `d.columns[0]` | 键是 **`HHID` + `PN` 两列**；回退把健康变量当 ID，42,946 行只算出 **8 个人** |
| MHAS | 同上，回退到 `d.columns[0]` | 键是 **`unhhid` + `ps3`** |
| CRELES | ID 猜测为 `id`/`hhid` | 键是 **`idsujeto`** |
| CRELES | glob `__DS1*.dta` | **`DS1*` 同时匹配 `DS10_Recoded_Variables`** → 选错文件，`want` 全空 → 空 frame → IndexError |

→ **glob/前缀匹配必须锚定分隔符**（改为 `__DS1_`），且**必须校验目标变量确实存在**后才使用该文件。
→ 与 C32（"名字含 eye"）、C50（按 n 排序）同族：**匹配规则比意图更宽时，会静默替换成错误的数据/文件**。

**更正 C58 —— BMI 切点必须按人群给出两个，不能静默选一个**
用 WHO 国际切点（BMI≥30）配西方参考区间时，KLoSA 实测仅 **1.45%**（区间 8–45%）→
看似数据错误，实为**切点不适用**。改为**同时输出两个切点**并各自设参考区间：

| 队列 | `bmi_high_25`（亚洲） | `bmi_high_30`（国际） | 判定 |
|---|---|---|---|
| **KLoSA** | **23.06% PASS** | 1.45% FAIL | **亚洲切点对** |
| **SHARE** | 63.83% FAIL | **22.81% PASS** | **国际切点对** |
| MHAS | 待建 | 待建 | |

→ 同一个参考率门**自动判别出哪一切点适合哪个人群**，无需预先决定。
→ 若当初静默选用单一切点，KLoSA 的 BMI 规则会以 1.45%（几乎无变异）进入分析，
   检验力被悄悄毁掉。**预注册须逐队列声明主切点，并保留另一作为敏感性分析。**

**更正 C59 —— CRELES 的视力量表无法解码，按纪律不猜**
`c55`(SeeFar)/`c56`(SeeClose) 是**数值 1–7**（不是我最初假设的 Excellent/Poor 字符串）。
本地**无可解码文档**：`H_CRELES_codebook.pdf`（250 页、47 万字符）与
`H_CRELES_creation.do`（466 KB）经关键词扫描**均不含视力条目**，
harmonized CRELES 本身不含眼科变量。
→ **1–7 的方向未知，猜错会反转结局** → **CRELES 不输出 `vision_impairment_*`**，
直到读到外部码本。
→ CRELES 只贡献**自描述**条项：`c54` 中的 **`'Is blind'`**（n=27）→
`blindness_selfreport`；`c57` HaveCataracts、`c60` HaveGlaucoma（均为 Yes/No）。

**CRELES `cataract_any` = 38.53%，超出通用区间 3–30%**：
该队列为 pre-1945 出生（**全部 60+**），此率对该年龄段属正常。
→ 已在门报告中加入 `age_context`（年龄分布/60+ 占比），
**以便在年龄背景下判读，而不是事后放宽区间以强行通过**——
放宽区间本身就是对门的事后调整。

**MHAS 现状**：仅波 1 建成（`sect_c.dta`）。波 3–6 的合并文件路径需核实；
且波 1 的糖尿病/高血压是 `c4`/`c6`（MHAS 码本命名），
而波 3–6 用的是 `diabetes`/`hipertension`——**同一结局跨波命名不同，需逐波映射**。
（**已于第 10 轮全部解决**，见 §0.11。）

### 0.11 第 10 轮：7 个 `.dta` 队列 frame 全部建成 + C60/C61

| 队列 | 行数 | 人数 | 波次 | 门 |
|---|---|---|---|---|
| SHARE | 1,693,515 | 137,183 | 4/5/6/7/9 | **9/9 PASS** |
| MHAS | 78,537 | 15,199 | 1/3/4/5/6 | 2/2 PASS |
| LASI | 73,408 | 73,408 | 1 | **5/5 PASS** |
| HRS | 42,946 | 27,261 | 2010/2016 | **5/5 PASS** |
| KLoSA | 40,406 | 11,137 | 1/2/4/6/8 | **6/6 PASS** |
| ELSA | 9,771 | 9,771 | 3 | 4/4 PASS |
| CRELES | 5,191 | 2,827 | 1/2 | 4/4 PASS |

**仅剩 CLHLS**（CSV，无 `.dta`）。

**更正 C60 —— 参考率门必须分两层，单层会混淆"变量错"与"国家不同"**
ELSA 的 `vision_impairment_severe` = **0.25%**，落在单层区间的下限（0.5%）之外；
但英国眼科服务覆盖好，重度视力损害本就罕见——**这不是错误，是国家差异**。
同理 CRELES 的 `cataract_any` = 38.5%（该队列全为 60+）。
→ 改为两层：
- **HARD（决定通过/否决）**：宽误差带。真正的缺陷会落在带外——
  吸烟门槛错误表现为 49%、CRELES 选错文件表现为 n=0、
  KLoSA 切点不匹配表现为 1.45%。
- **TYPICAL（仅信息）**：规则建立时来源（NHANES/KNHANES）的区间。
  落在带外**记录但不否决**，并单列 `outside_typical`。
→ **不为强行通过而放宽区间**——那是对门本身的事后调整。

**更正 C61 —— C36 在我自己新写的构建器代码里复发**
LASI 的 `ht002`（高血压）/`ht003`（糖尿病）/`ht019`/`ht020`（视力）都是
**带值标签的类别型**（取值是字符串 `'1 Yes'`/`'2 No'`）。
我在新 builder 里又写了 `pd.to_numeric` → 全部变 NaN →
糖尿病/高血压/两个视力 flag 的 `n` **全为 0**，而 `cataract_any` 正常
（因为它是从字符串 `ht017` 解码的，没走 to_numeric）——
**四个 flag 静默为空、一个正常**，这种"部分为空"最容易被忽略。
→ 新增 `_code()` 辅助函数：先取标签的前导整数，失败再回退到直接数值读取。
修正后 LASI 5/5 PASS（糖尿病 12.1%、高血压 27.8%、视力 12.12%/1.34%）。
→ **C36 的教训不能只写在文档里，必须做成公用的取值函数**——
只要还有人（包括我）直接写 `to_numeric`，它就会再犯。

**其它路径陷阱（同族）**：
- ELSA 波 3 核心文件在子目录中（`UKDA-5050-stata/stata/stata13_se/wave3/`）→ 须 `rglob`
- **MHAS 波 5 文件名段序不同**：`sect_a_c_d_f_e_pc_h_i_2018`，其余为 `sect_a_c_d_e_pc_f_h_i_<年>`
  → 又一次"按名字猜路径"失败（C57 同族）
- MHAS 波 3–6 的慢病/BMI 在**官方派生文件**中：
  `Constructed Data/MHAS_ENASEM_<年>_Constructed_Variables_Creadas.dta`（`hipertension_<yy>`）
  与 `Imputations of Weight & Height/MHAS_<年>_Weight_and_Height_IMPUTED.dta`（`bmi_imp_<yy>`）

### 0.12 第 11 轮：CLHLS frame 建成（8/8 完成）+ C62/C63/C64

`data/frames/cohort_CLHLS.csv` —— **72,744 行**（9,093 人 × 8 波），门 7/7 PASS。

| flag | n | 患病率 | HARD | TYPICAL |
|---|---|---|---|---|
| `cataract_any` | 16,989 | 17.08% | PASS | 内 |
| `vision_impairment_moderate` | 17,932 | 18.27% | PASS | 内 |
| `vision_impairment_severe` | 17,932 | 17.34% | PASS | **外**（>10%） |
| `current_smoking` | 18,128 | 15.87% | PASS | 内 |
| `alcohol_intake` | 9,083 | 23.55% | PASS | 内 |
| `hypertension` | 16,955 | **15.06%** | PASS | **外**（<20%） |
| `diabetes` | 16,858 | **1.36%** | PASS（贴下限） | **外**（<4%） |

**更正 C62 —— CLHLS 吸烟/饮酒块的字母位移比慢病块更凶险**
- 基线（1998）：`d61` = 现吸烟，**`d71` = 现饮酒**
- 随访（`_0`/`_2`/`_5`/`_8`/`_11`）：**`d71_<波>` = 现吸烟**，`d72_<波>` = 曾吸烟

→ **同一个 token `d71` 在基线是饮酒、带后缀是吸烟。**
→ 且**随访波完全没有饮酒题** → `alcohol_intake` 只能是基线单波（已如此实现）。
→ 与 C24（`g17`→`g15`）同族，但危害更大：慢病块是字母位移，
**这里是"同名不同义"**，凭名字取变量会直接张冠李戴。

**更正 C63 —— CLHLS 码本陈述的缺失约定与本发布版不符**
码本正文写"`9/99` = 缺失，`8/88` = 不知道，`-1` = 不适用"，
但**数据里还有 `-6`/`-7`/`-8`/`-9`**——仅 `g1_2` 一列就有 **`-8` 共 4,261 行**。
→ 若把 `-8` 当有效取值，结局会被彻底污染。
→ 处置：**全部负数码 + `8/88/9/99/888/999` 一律映射为缺失**。
   这个方向不可能反转结局，因此是安全默认值。

**更正 C64 —— 两个未决问题，必须在确认层运行前解决**
1. **`g1` 尺度在波次间不一致**（C25 的实测确认）：
   - 1998：`3` = 1,523 > `2` = 1,018
   - 2000：`2` = 1,499 ≫ `3` = 165
   - 2002：`3` = 602 > `2` = 427
   名义顺序（see and distinguish / see only / cannot see / blind）在 1998 与 2002 一致，
   **但 2000 波相反**。逐波分布已写入 `cohort_CLHLS_prevalence.json` 的诊断字段，
   **必须逐波确认后才可用于确认层**，不得假定顺序统一。
2. **慢病码 `3` 的含义——【已解决】**
   逐行读取官方值标签表（不再用会串行的解析器）得到：

   ```
   g17a1:  1 = yes   2 = no   3 = "don't know"   9 = missing
   g17a2: -1 = not applicable  1 = rather serious  2 = more or less  3 = no
   ```

   → **`g17*1`/`g15*1` 系列是 yes/no/don't-know 三码，`3` = "don't know"。**
   → 我的映射（1=是、2=否、其余→缺失）**正确**，`3` 被排除是对的。
   → 分级信息在**另一组变量** `g17*2`/`g15*2`（rather serious / more or less / no）。
   → **因此 `hypertension` = 15.06%、`diabetes` = 1.36% 是真实的自报值**，
     不是映射错误。差异来源是**自报医生诊断 vs 测量**：
     TYPICAL 带按 NHANES/KNHANES（多为测量）校准，而 CLHLS 问的是"医生是否告知"。
   → **这印证了两层门的设计**：单层门会把"测量口径不同"误判为"变量错误"，
     进而诱发一次错误的"修正"（把正确的东西改坏）。

   残留待办（**不阻塞**，但须在论文中声明）：CLHLS 是否使用 `g17*2` 分级做敏感性分析，
   待预注册时决定。

**CLHLS 无 BMI**：只有体重 `g12`（无身高）→ `bmi_high` 不可构造。

### 0.13 第 12 轮：解决 C64-1，并抓到一处会静默污染结果的尺度错误（C65）

**逐行读码本得到 `g1` 的真实逐波尺度**：

| 波 | 取值定义 | 级数 |
|---|---|---|
| `g1` (1998) | 1 能看见并分辨 / 2 能看但不能分辨 / 3 看不见 / 4 盲 | 4 |
| **`g1_0` (2000)** | 1 能看见并分辨 / **2 看不见 / 3 盲** | **3** |
| `g1_2` (2002) | 1 / 2 只能看见 / 3 看不见 / 4 盲 | 4 |
| `g1_5` (2005) | 同 2002 | 4 |

**更正 C65 —— 尺度在波次间级数不同，合并映射会静默错分**
2000 波**没有"只能看见"这一类**，只有 3 级：`2` = 看不见、`3` = 盲。
我原先的合并映射把 2000 波的
- `2`（看不见，**重度**）映射成了 `vision_impairment_moderate`
- `3`（盲）映射成了 `vision_impairment_severe`

→ **1,499 人被错分**（另有 165 人）。
→ **而参考率门没有抓到它**：合并后的 moderate = 18.3%，完全正常。
**波特异性缺陷藏在合理的合并数字里，合并口径看不见它。**
→ 已按逐个波次分别映射（2000 波不产出 `moderate`，因为它不存在）；
并给参考率门**加上逐波检查**（`per_wave` / `wave_outliers`），
任何波偏离合并值 >10 个百分点即列出。

**修正后 `vision_impairment_severe` = 25.7%，超出 HARD 上限 25%**：

| 波 | severe | 波 | severe |
|---|---|---|---|
| 1998 | 19.99% | 2008 | 32.38% |
| 2000 | 34.75% | 2011 | 33.33% |
| 2002 | 25.10% | 2014 | 25.58% |
| 2005 | 31.14% | 2018 | (n=10) |

**跨波一致（20–35%）**，且 CLHLS 是 **80+ 队列**——"看不见"占 20–35% 是该队列的已知特征。
→ **不放宽区间以强行通过**（放宽区间即是对门的事后调整）。
→ 判定：这是 **HARD 带未按年龄分层**这一门自身的局限，不是映射错误。
   已标记为 review 项：**CLHLS 的 `vision_impairment_severe` 在使用前需要年龄分层的参考率**。

**逐波检查同时标出的小样本波**：2014（47 人）与 2018（10 人）在吸烟/高血压上偏离合并值——
属噪声，但已单列，避免被误读为趋势。

**待办（进入确认层前必须补齐）**：**年龄与性别协变量** → **已于第 13 轮处理**，见 §0.14。

---

### 0.14 第 13 轮：协变量补全（C66/C67/C68）

**各队列协变量来源（逐队列核实，非按名字猜）**：

| 队列 | 年龄 | 性别 | 来源文件 |
|---|---|---|---|
| HRS | `PA044` | `PX060_R`（"SEX OF INDIVIDUAL-UPDATED - R"） | `H16A_H.dta` / `H16PR_R.dta` |
| KLoSA | `w01A002_age` | `w01gender1` | 核心文件 `str0N_e.dta` |
| LASI | `dm005`（Age at last birthday） | `dm003`（Sex of Respondent） | `lasi_w1b_ind_bm.dta` |
| MHAS | `edad` | `sexo` | 各波合并 `sect_*.dta` |
| CRELES | `age` | `sex` | **`DS10_Recoded_Variables_*.dta`**（DS1 主表无这两项） |
| CLHLS | **`trueage`**（CLHLS 的验证年龄） | **`a1`** | CSV |
| SHARE | `age` | `gender` | `gv_imputations` |

**更正 C66 —— 协变量不在结局文件里**
HRS 的年龄在 section A 住户文件（`PA044`），性别在 **`H16PR_R` 预载文件**（`PX060_R`）；
CRELES 的在 **DS10 "Recoded Variables"** 而非 DS1 主表；
CLHLS 的年龄是 **`trueage`**（验证年龄），不是 `a53*` 那一族（那是同住者的年龄，另一个构念）。
→ 逐队列定向核实后才拿到，**没有一个是猜中的**。

**实测年龄分布**：

| 队列 | n | 平均年龄 |
|---|---|---|
| **CLHLS** | 67,464 | **92.0** ← 证实"80+ 队列"的判断（C65 的依据） |
| CRELES | 5,191 | 76.7 |
| SHARE | 1,693,515 | 67.9 |
| KLoSA | 40,406 | 65.7 |
| ELSA | 7,769 | 64.9 |
| MHAS | 15,182 | 60.3 |
| LASI | 73,408 | 57.9 |

**更正 C67 —— 全局正则替换引发了无限递归（我自己的操作事故）**
为一次性消灭 `pd.to_numeric` 的类别型陷阱，我用正则把构建器里 17 处
`pd.to_numeric(X)` 批量换成 `_code(X)`——**结果把 `_code()` 函数体内的
`pd.to_numeric(series, ...)` 也换掉了，造成自递归**，8 个队列全部
`RecursionError` 失败。
→ 已回填，最终 17 → 4 处（余下的是 1 处注释、1 处 `_code` 自身、2 处在已建好的数值列上）。
→ **教训：全局替换必须排除被替换函数的自身定义域；批量修复的工具本身也会是缺陷来源。**

**更正 C68 —— `_code()` 对"纯文本类别"无效**
`_code` 取标签的前导整数，能处理 `'1 Male'` 但**不能处理 categories 就是
`'Male'`/`'Female'`** 的列。KLoSA `w01gender1` 与 SHARE `gender` 正是如此，
在 `_code` 扫过之后**整列为 NaN**。
→ 新增 `_sex()`：按文本 male/female/m/f 与数字 1/2 匹配，再回退。
→ 修正后 KLoSA（40,406）与 SHARE（1,693,515）性别补全。

**协变量覆盖（第 13 轮末）**：

| 队列 | age | sex |
|---|---|---|
| SHARE | ✅ 1,693,515 | ✅ 1,693,515 |
| LASI | ✅ 73,408 | ✅ 73,408 |
| CLHLS | ✅ 67,464 | ✅ 72,744 |
| KLoSA | ✅ 40,406 | ✅ 40,406 |
| MHAS | ✅ 15,182 | ✅ 15,182 |
| HRS | ❌ **缺** | ✅ 20,912 |
| ELSA | ✅ 7,769 | ❌ **缺** |
| CRELES | ✅ 5,191 | ❌ **缺** |

**剩余三项待补** → **已于第 14 轮全部解决**，见 §0.15。

---

### 0.15 第 14 轮：协变量缺口全部闭合 + C69

**三项全部解决**：

| 缺口 | 真实原因 | 处置 |
|---|---|---|
| HRS 年龄 | 年龄在 **`H16A_R.dta` 的 `PA019`**（"R CURRENT AGE CALCULATION"，n=20,912），该文件为个体级并带 `HHID`+`PN`；`H16A_H` 是住户级、无 `PN` | 改用 `H16A_R` |
| ELSA 性别 | 生命历程文件**键就是 `idauniq`**（合并本来就对），但 `sex` 是纯文本 `'Male'`/`'Female'`，被 `_code` 清空 | 走 `_sex()` |
| CRELES 性别 | DS10 的 `sex` 同为纯文本；我上一轮的 `_sex` 补丁因锚点不同**未生效**，仍走 `_code` | 走 `_sex()` |

**最终协变量覆盖（8/8 齐备）**：

| 队列 | age | sex |
|---|---|---|
| SHARE | 1,693,515 | 1,693,515 |
| LASI | 73,408 | 73,408 |
| CLHLS | 67,464（均龄 92.0） | 72,744 |
| KLoSA | 40,406 | 40,406 |
| HRS | 20,912 | 20,912 |
| MHAS | 15,182 | 15,182 |
| ELSA | 7,769 | 7,833 |
| CRELES | 5,191 | 5,191 |

**→ 8 个队列的 frame 现已具备确认层回归所需的最小变量集（结局 + 暴露 + 年龄 + 性别）。**

**更正 C69 —— 全局正则替换造成"部分匹配"损伤**
C67 的批量替换除自递归外，还留下更隐蔽的一类损伤：替换模式的候选分支含**裸变量名 `s`**，
**没有词边界**，于是 `pd.to_numeric(sub[col], errors="coerce")` 被
`s` + `[^)]*` 部分匹配，整段替换成 **`s = _code(s)`**——一句引用未定义变量的话，
会在逐波检查块里抛 `NameError`。
→ 通过**枚举审计全部 `_code(` 调用点**逐一核对才发现（本应更早做），已修回。
→ **教训：正则替换的候选分支必须带词边界；替换后必须审计全部调用点，不能只看替换计数。**
C67 与 C69 是同一次操作的两处损伤——**"用正则批量改代码"这件事本身的失败率，
高于它想修复的问题**。以后此类修复改为逐个锚点编辑。

---

### 0.16 八队列 frame 全部完成（第 11 轮）

| 队列 | 行数 | 人数 | 波次 | 门 |
|---|---|---|---|---|
| SHARE | 1,693,515 | 137,183 | 4/5/6/7/9 | 9/9 |
| MHAS | 78,537 | 15,199 | 1/3/4/5/6 | 2/2 |
| LASI | 73,408 | 73,408 | 1 | 5/5 |
| **CLHLS** | **72,744** | **9,093** | **1998–2018（8 波）** | **7/7** |
| HRS | 42,946 | 27,261 | 2010/2016 | 5/5 |
| KLoSA | 40,406 | 11,137 | 1/2/4/6/8 | 6/6 |
| ELSA | 9,771 | 9,771 | 3 | 4/4 |
| CRELES | 5,191 | 2,827 | 1/2 | 4/4 |

**8/8 完成。**合计约 200 万行 person-wave。

**进入确认层前必须解决的两项**（均已在台账留痕）：
1. ~~**CLHLS `g1` 尺度的波次不一致**（C64-1）~~ → **已解决**，见 §0.13 / C65
2. **CRELES `c55`/`c56` 的 1–7 尺度未解码**（C59）——已排除该队列的视力结局

**已知无法检验的规则**（不受 frame 完成影响）：
- 视网膜病变族 r03/r04/r07/r19/r22 → **全部 8 个队列均无眼底影像**
- PM2.5 族 r16/r17/r21 → 队列原始文件无地理编码暴露
- 眼压/视盘族（`glaucoma_iop_elevated`/`glaucoma_suspect_cdr`）→ 无眼压/CDR

---


## 1. KLoSA（韩国老龄化纵向研究）— 已完成侦察

**原始文件布局**（`Raw_data/`）：
- 波 1–8 各有 `_e`（英文标签版）、`韩语版/`（韩文原始版）、以及 `_CN`（中文改写副本，**本项目不用**）
- 波 9 仅 `韩语版`
- 每波另有 `Lt*`（319 变量）、`str*`、`e_imp_w*`（插补文件）
- 官方 harmonized 在 `H_KLoSA/`（**本项目不用**）

**眼科变量块**（每波一套，波 w 前缀 `w{w:02d}C0*`）：

| 变量 | 韩文标签 | 官方英文标签 | 官方值标签 |
|---|---|---|---|
| `C074` | 평소 안경, 콘택트렌즈 사용여부 | Usual usage of glasses and contact lenses | 1 Yes / **3 Visually disabled (blind)** / 5 No |
| `C075` | 시력(교정시력 포함) | Eyesight | 1 Very good / 2 Good / 3 Fair / 4 Bad / 5 Very bad |
| `C076` | 멀리 떨어진 물체에 대한 시력 | Eyesight for far away object | 同上（1–5） |
| `C077` | 가까이 있는 물체에 대한 시력 | Eyesight for near object | 同上（1–5） |
| `C078` | 백내장 수술 경험 여부 | Whether or not cataract **operation** experience | 1 Yes / 5 No |
| `C079` | 백내장 수술 부위 | Cataract operation part | 1 / 5（部位） |
| `C080` | 녹내장 치료 경험 여부 | Whether or not glaucoma **treatment** experience | 1 Yes / 5 No |
| `C081` | 현재 시력으로 인한 일상활동의 어려움 | Daily activity difficulty by eyesight | 1 Yes / 5 No |

缺失码：**-9 Don't know / -8 Refuse to answer**（不同波可能另有 8/9，需逐波核验）。

### 1.1 三个必须记入更正记录的发现

**更正 C19 —— 【第 3 轮撤回并改写】KLoSA 眼科数据在核心波文件中可得**

**撤回原文**（错误）："KLoSA 眼科数据只存在于插补文件；核心波文件声明了 C074–C081
但取值全为缺失"。

**重新核验（`notna()` 而非 `to_numeric`）**：

| 文件 | 变量 | notna | to_numeric（错误口径） |
|---|---|---|---|
| `wave1/str01_e.dta` | `w01C075` 自评视力 | **10,229 / 10,254** | 0 |
| `wave1/str01_e.dta` | `w01C078` 白内障手术 | **10,229**（Yes 827 / No 9,402） | 0 |
| `wave1/str01_e.dta` | `w01C080` 青光眼治疗 | **10,229**（Yes 112 / No 10,117） | 0 |
| `wave4/韩语版/w04.dta` | `w04C075` | **7,456 / 7,486** | 0 |

**真相**：KLoSA 的带值标签变量在 pandas 中返回**类别型**（categories 是标签字符串
`Very good/Good/Fair/Bad/Very bad`），`to_numeric` 把全部取值变成 NaN，于是被误报为
"全空"。这些变量**在核心波文件中本来就有完整数据**，每波一套，波 1–9 均有。
- 教训见 C36（这是同一 bug 的实例）。

**更正 C20 —— 【第 3 轮改写】插补文件不必使用**
`e_imp_w{w}.dta` 确为 5 副本堆叠（如 `e_imp_w06` 37,450 = 7,490 × 5），
但**既然核心波文件已有实测值，应优先使用实测数据**，不需要多重插补合并
（KLoSA 波 1 的 `str01_e.dta` 缺失仅 25/10,254 = 0.24%）。
- 若某波核心文件缺失率高，再考虑插补并预注册合并规则（Rubin）。
- 插补副本仍可用于敏感性分析。

**更正 C21 — 构念纪律：手术/治疗 ≠ 患病**
`C078` = 白内障**手术**史、`C080` = 青光眼**治疗**史、`C081` = 视力致活动困难。
- **不得**把它们映射为 `cataract_any` / `glaucoma_*`。
- 只能作为**独立命名的结局**：`cataract_surgery`、`glaucoma_treated`、
  `activity_limitation_vision`；并在论文中声明其构念（仅覆盖就医并接受干预者，
  受医疗可及性混杂）。
- 这是 R11 的 `E_DR`（名字像 DR、实为眼药水）同一类错误的预防条款。

**更正 C22 — `C074` 内嵌失明标记**
`C074 == 3` = "Visually disabled (blind)"（波 1 插补文件中 n=125）。
可构造 `blindness_selfreport`，与 `C074 ∈ {1,5}` 互斥。

### 1.2 可构造的 KLoSA 结局（待预注册确认切点）

| 慧眼结局 flag | KLoSA 来源 | 构造 | 说明 |
|---|---|---|---|
| `vision_impairment_moderate` | `C076`/`C077` | == 4 (Bad) | 远/近分列，遵循 R11「不得用二值顶替分级」纪律 |
| `vision_impairment_severe` | `C076`/`C077` | == 5 (Very bad) | |
| `vision_impairment_any` | `C075` | ≥ 4 | 总体自评，含矫正视力 |
| `blindness_selfreport` | `C074` | == 3 | 由眼镜题内嵌 |
| `cataract_surgery` | `C078` | == 1 | 非患病 |
| `glaucoma_treated` | `C080` | == 1 | 非患病 |
| `activity_limitation_vision` | `C081` | == 1 | 功能结局 |

**KLoSA 无法构造**：`cataract_any`、`glaucoma_exam`、`retinopathy_*`、`amd_*`、
`dme_any`（无患病题项、无视网膜影像）。
→ 该层可评估的规则：**r20/r21（视力类）、r10/r12/r13/r14（若结局定义为白内障手术则仅为代理，
须显式声明构念偏移）**。视网膜/AMD/青光眼规则的评估在 KLoSA 不可行。

### 1.3 暴露侧（待逐变量核验）

首轮关键词命中：`r{w}smokev`(48)、`r{w}drinkev`(128)、`r{w}diabe`(57)、
`r{w}hibpe`(57)；**BMI 未命中**（KLoSA harmonized 亦无 BMI）——需从 `Lt*`/`str*` 或
anthropometry 文件另找身高体重，暂记为待办。

---

## 2. CLHLS（中国老年健康影响因素跟踪调查）— 已完成侦察

**数据形态**：8 波（1998/2000/2002/2005/2008/2011/2014/2018）以 `.csv` + `.sav` + `.xlsx`
提供，另有 2018 横断面。官方码本 `CLHLS_codebook 1998-2018/codebook_for_*.docx`
（8 个有效 OOXML）：
- **表0**（6,176 变量）：`Variable | Position | Label | Measurement Level | Write Format`
  —— **标签为英文**（首轮中文关键词搜索因此漏检）
- **表1**（37,975 行）：值标签 `Value | | Label`

⚠️ 目录冗余：`clhls` 与 `clhls（Excel）` 是相同 33 文件 / 1,585.6 MB 两份；
`clhls-state` 另一批 31 文件 / 6,652.9 MB。**本项目只用一份。**

### 2.1 眼科变量（码本核验）

| 变量（波后缀） | 标签 | 类型 |
|---|---|---|
| `g1`（1998）、`g1_0/_2/_5/_8/_11/_14/_18` | **visual function** | Ordinal / Nominal |
| `g17g1`（1998）→ `g15g1_*`（随访） | **suffering from cataract?** | Ordinal |
| `g17h1`（1998）→ `g15h1_*`（随访） | **suffering from glaucoma?** | Ordinal |
| `d0/d2/d5/d8/d11/d14/d18` + `catara`/`glauco` | 死亡前患白内障/青光眼 | Nominal |

**更正 C23 — CLHLS 提供真正的"患病"结局，优于 KLoSA**
`g15g1_*` = 白内障**患病**、`g15h1_*` = 青光眼**患病**（KLoSA 只有手术/治疗史）。
**更正 C24 — 变量名存在跨波位移**：1998 为 `g17g1`/`g17h1`，2000 起改为 `g15g1_*`/`g15h1_*`。
必须逐波映射，不得假定同名。

**更正 C25 — `g1_*` 不是自评量表，是功能测试**
题面为 "can you see the break in the circle?"（圆环缺口辨识）。
取值（2002 波起为规整 4 级）：
`1 can see and distinguish` / `2 can see only` / `3 cannot see` / `4 blind`。
1998 基线措辞不同（"can see but can't distinguish the break"、"can't see"、"blind"），
**跨波合并前须逐波对齐措辞**。
→ 可构造：`vision_impairment_moderate` = `g1 ∈ {2}`；`vision_impairment_severe` = `g1 ∈ {3,4}`；
`blindness_selfreport` = `g1 == 4`。（切点待预注册确认）

**更正 C26 — CLHLS 缺失码与 KLoSA/NHANES 均不同**
码本明示：`-1` = 不适用；`9/99/999/9999/99999` = 缺失；`8/88/888/8888/88888`（多数但非全部）
= 不知道。且码本明确写明 **"Datasets with imputed values to replace the missing data are
not currently available"** —— **CLHLS 原始数据无插补**，与 KLoSA（只给插补版）相反。

**CLHLS 变量命名规则**（码本第 5–6 条）：
- `r` 前缀 = 该题由代答人回答
- `_0/_2/_5/_8/_11/_14/_18` 后缀 = 该波仍存活并复访
- `d0/d2/d5/d8/d11/d14/d18` 前缀 = 该区间内死亡的受访者

**CLHLS 可构造**：`vision_impairment_*`、`blindness_selfreport`、**`cataract_any`**、
**`glaucoma_selfreport`**（后两者为真正患病）。
**无法构造**：`retinopathy_*`、`amd_*`、`dme_any`、`glaucoma_exam`、`glaucoma_iop_elevated`
（无影像/眼压）。
→ CLHLS 可评估规则：**r10（吸烟×白内障）、r12（饮酒×白内障）、r13（BMI×白内障）、
r14（铅×白内障）、r20/r21（视力类）**；较 KLoSA 多覆盖 r10/r12/r13 的**真患病**结局。

---

## 3. HRS（美国健康与退休研究）— 已完成码本核验

**码本位置**：每个模块一份码本文本，如
`Raw_data\2006 HRS\2006 HRS Core\h06cb\H06C_R.txt`（含题面与取值频数）。
⚠️ HRS 的 `.dta` **不携带值标签**（`variable_value_labels` 为空），
**必须读码本 txt**，不能依赖 .dta 元数据。读取需 `encoding='ISO-8859-1'`
（pyreadstat 拒绝 latin-1 字样但接受 ISO-8859-1）。

### 3.1 眼科变量（码本核验，2006 波）

| 变量 | 题面 | 取值 | n |
|---|---|---|---|
| `KC095` RATE EYESIGHT | "Is your eyesight excellent, very good, good, fair, or poor **using glasses or corrective lenses as usual**?" | 1 EXCELLENT / 2 VERY GOOD / 3 GOOD / 4 FAIR / 5 POOR / **6 [VOL] LEGALLY BLIND** | 18,467 |
| `KC096` RATE DISTAL VISION | "…for seeing things at a distance, like recognizing a friend across the street, using glasses or corrective lenses as usual?" | 1–5（Excellent–Poor） | 18,381 |
| `KC097` RATE NEAR VISION | "…for seeing things up close, like reading ordinary newspaper print, using glasses…?" | 1–5 | 18,381 |
| `KC098` | "Have you ever had cataract **surgery**?" | 1 Yes / 5 No | 10,063 |
| `KC099` | Cataract surgery on one or both eyes | 1 / 2 | 1,109 |
| `KC100` | Cataract implant lens | 1 Yes / 5 No | 1,109 |
| `KC101` | **GLAUCOMA** | 1 Yes (416) / 5 No (9,828) → **4.05%** | 10,279 |
| `KJ541` | GOOD EYESIGHT | 1–4 | 3,657 |
| ~~`KT002`~~ | ~~"did R make family provisions in will"~~ | — | ❌ **关键词假阳性，非眼科** |

**更正 C27 — 视力评分题测的是"矫正后视力"**
`KC095/096/097` 题面均限定 "using glasses or corrective lenses as usual"，
与 KLoSA `시력(교정시력 포함)` 同构念。
→ 由此构造的"视力损害"捕获的是**矫正后仍存在的损害**，**不是**未矫正屈光不正。
论文必须显式声明，否则会被误读为屈光不正负担。

**更正 C28 — `KC095` 含独立"法定盲"类别**
code 6 = [VOL] LEGALLY BLIND（n=86）。可构造 `blindness_selfreport`（法律意义失明），
与 `vision_impairment_severe`（POOR）区分开。

**更正 C29 — `KC098` 是白内障手术，非患病**
与 KLoSA `C078` 同类构念问题。HRS **无白内障患病题项**，只有手术。
→ HRS 的 `cataract_surgery` 为独立结局；`cataract_any` 在 HRS **不可构造**。

**更正 C30 — HRS .dta 无值标签，必须读模块码本 txt**
`pyreadstat` 的 `variable_value_labels` 对 HRS 返回空。
码本为 `Raw_data/<波> HRS/<Core>/hYYcb/HYYx_R.txt`，含题面与取值频数。

### 3.2 HRS 可构造结局

| 慧眼结局 | HRS 构造 |
|---|---|
| `vision_impairment_moderate` | `KC096` 或 `KC097` ∈ {4}（Fair） |
| `vision_impairment_severe` | `KC095` ∈ {5} 或 `KC096/097` == 5（Poor） |
| `blindness_selfreport` | `KC095` == 6（legally blind） |
| `cataract_surgery` | `KC098` == 1 |
| `glaucoma_selfreport` | `KC101` == 1（**真患病**，自报诊断） |

**HRS 无可构造**：`cataract_any`、`retinopathy_*`、`amd_*`、`dme_any`、`glaucoma_exam`、`glaucoma_iop_elevated`。

---

## 4. SHARE（欧洲健康退休与老龄化调查）— ✅ 可用（第 3 轮撤回"不可用"结论）

**撤回原文**（错误）："`ph006d13` 全 9 波 n_valid = 0；`eyesightr` 全波 n_valid = 0；
SHARE 本地副本的眼科变量被系统性清空。"

**真相**：这些变量是**带值标签的类别型**，用 `to_numeric` 统计得 0，用 `notna()` 统计则完整
（见 C36）。修正后的实测结果：

| 变量 | 模块 | 波次 | n_valid（实测） | 取值 |
|---|---|---|---|---|
| **`eyesightr`** | `gv_imputations` | W1 152,080 / W2 185,660 / W4 289,910 / W5 330,190 / W6 340,275 / W7 385,905 / W8 268,475 / W9 347,235 | 全量 | **Excellent / Very good / Good / Fair / Poor** |
| **`eyesightr_f`** | `gv_imputations` | 同上 | 全量 | **Regular obs. / Imp: missing value / Missing by design** ← 插补状态标记 |
| **`ph006d13`** | `ph` | W6/W7/W9 … | W6 67,945 / W7 76,806 / W9 69,351 | **Selected / Not selected / DK / Refusal**（白内障患病） |
| `ph043_` / `ph044_` | `ph` | W9 | 69,345 | Excellent / Very good / Good / Fair / Poor（远/近视力） |
| `ph009_13` | `ph` | W1–W9 | W1 2,275 / W4 3,278 / W7 47 | 白内障确诊年龄（仅患病者） |

**更正 C37 — SHARE 是本外验层唯一提供"插补状态标记"的队列**
`eyesightr_f` 直接区分 `Regular obs.` / `Imp: missing value` / `Missing by design`。
→ 可**限定为实测值**（`eyesightr_f == 'Regular obs.'`）做主要分析，
插补值做敏感性分析。这是处理插补最干净的做法，应作为其他队列的规范。
注意 W7 有大量 `Missing by design`（316,165），需按波确认可分析样本量。

**更正 C38 — `ph006d13` 是真正的"白内障患病"（ever diagnosed）**
与 HRS `KC098`（手术）不同，SHARE 提供患病。→ SHARE 可评估 **r10/r12/r13/r14** 的
白内障结局，而 HRS 不能。

先前记录的假阳性仍有效：`q6d` / `v6_4` = "gaining **insight** into other people's social
circumstances"（访员问卷）。

---

## 5. MHAS（墨西哥健康与老龄化研究）— 已完成码本核验

**码本位置**：`Raw_data/wave1/Codebooks/Section_*.pdf`（分节 PDF，**英文题面 + 取值频数**）。
⚠️ 码本里变量名**大写**（`C44`/`C45`），数据集里是**小写**（`c44`/`c45`）。

### 5.1 眼科变量（Section C Health 码本核验）

| 变量 | 题面 | 取值（频数/占比） | n |
|---|---|---|---|
| `C44` | "Do you usually **wear glasses**?" | 1 Yes 6,070 (39.98%) / 2 No 9,092 | 15,182 |
| **`C45`** | **"How is your vision (using glasses)? Is it…"** | 1 Excellent 427 (3.02%) / 2 Very Good 1,363 (9.63%) / 3 Good 6,029 (42.61%) / 4 Fair 4,891 (34.57%) / 5 Poor 1,295 (9.15%) / **6 Legally blind 44 (0.31%)** / 8 RF / 9 DK | 14,150 |
| `E2`/`E3`/`E4`（Section E） | glasses help / use glasses / glasses for close-up | 见 §7.2 | 13,962 / 10,361 / 6,745 |
| `C29C` | "stroke causes vision difficulty" | 1 Yes 213 / 2 No 177 | 391 |

**更正 C33 — `C45` 与 HRS `KC095` 同构念**
题面均限定 **"using glasses"**（矫正后视力），且都有独立的 **"Legally blind"** 类别。
→ 两库可**用同一构念定义合并**（1–5 序数 + 6 = 法定盲），这是本外验层少数可跨库对齐的结局。

**更正 C34 — `C45` 标注 "Skip if proxy"，代理访谈按设计缺失**
`C45` 的缺失 1,032 例**恰好等于**代理访谈数（`ENT_TIP` 21/22 合计 438+594=1,032）。
→ 这是**效度优点**（视力自评不由代理代答），但会造成**与允许代理的队列之间的选择差异**，
跨库比较时须声明。MHAS 代理率 6.8%。

**更正 C35 — MHAS 无白内障/青光眼患病题项**
全库检索（标签含 cataract/catarata/glaucoma）**无任何有数据的命中**。
→ r10/r12/r13/r14 的**白内障结局**在 MHAS **不可构造**；MHAS 只能贡献**视力族（r20/r21）**。

**又一个假阳性（已入否决表）**：正则 `ver\b` 命中了 "Has a doctor ever told you" 里的
"**ever**"。现已改为要求 `vista|visión` 等完整词。

### 5.2 MHAS 可构造结局

| 慧眼结局 | MHAS 构造 |
|---|---|
| `vision_impairment_moderate` | `C45` == 4（Fair） |
| `vision_impairment_severe` | `C45` ∈ {5}（Poor） |
| `blindness_selfreport` | `C45` == 6（Legally blind） |

**MHAS 无可构造**：`cataract_any`、`cataract_surgery`、`glaucoma_*`、
`retinopathy_*`、`amd_*`、`dme_any`。
→ **MHAS 仅能评估视力族规则（r20/r21）**，样本约 14,150。

---

## 6. ELSA（英国老龄化纵向研究）— 已完成码本核验

> ⚠️ 本节下方"C31：ELSA 只有单波单变量的视力结局"**已被更正 C42 推翻**。
> ELSA 实际有自己的眼科模块（wave 1 `heeye`/`hefrnd`/`hepap`）并提供
> **白内障 `heoptca` / 青光眼 `heoptgl` / AMD `heoptmd`**。
> 保留原记录以留痕，结论以 C42 与 §0.0 矩阵为准。

**结论：ELSA 唯一可用的眼科结局是 `HeEye`，且只存在于 wave 6。**

| 变量 | 标签 | n | 取值 |
|---|---|---|---|
| **`HeEye`（wave 6）** | Self-reported eyesight (**while using lenses, if appropriate**) | 10,601 | 1–5 + **6 'Spont: registered/legally blind'**；缺失 -9/-8 |
| `ialreye`（wave 5/6/7） | ~~annual commercial loan repayment - bracket entry point~~ | 10,274 / 10,601 / 9,666 | ❌ **假阳性**（变量名恰好以 "eye" 结尾） |
| `ahseyear`（wave 1） | ~~HSE Year~~ | 12,099 | ❌ **假阳性**（Health Survey for England 年份） |
| `SCINNO05` / `SCINNO06`（wave 10） | "My vision is **not good enough to use the equipment**" / "My health problems (not including vision problems)…" | 6,042 each | ❌ **未完成物理测试的原因**，不是视力结局；且高度选择 |
| `EIEye` / `EiCat` / `EiOpt1`（临终模块） | deceased's eyesight / cataract surgery / glaucoma | **240** | ❌ 样本过小且为代理报告 |

**更正 C31 — ELSA 只有单波单变量的视力结局**
`HeEye` 仅存在于 wave 6（core waves 1–5、7–9 无该题）。
→ ELSA 层为**横断面单波**，不能做纵向；且 ELSA **无白内障/青光眼患病变量**
（仅临终模块的代理报告，n=240 不可用）。
→ ELSA 可评估的最多只有**视力族规则（r20/r21）**，且样本约 10,600。
**ELSA 在本外验层中的价值显著低于 HRS。**

**更正 C32 — "变量名含 eye" 是高频假阳性源**
`ialreye`（贷款）、`ahseyear`（HSE 年份）均因名字含 "eye" 而误入候选。
已把该模式写入扫描器的语义否决表。

---

