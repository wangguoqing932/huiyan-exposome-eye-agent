# 多数据库文献验证操作包(R18,2026-10-20)

> 目的:用不同数据库打破 PubMed 循环性,让文献层成为真正的外部验证。
> 你需要通过新疆医科大学图书馆登录各数据库,运行检索式,导出结果发回。

## 为什么这样能打破循环

| 循环来源 | 打破方式 |
|---|---|
| 同一数据库(PubMed) | 换数据库:Embase / Web of Science / CNKI |
| 同一检索排序(PubMed relevance) | 不同数据库有不同排序算法,top-N 结果不同 |
| 同一期刊覆盖(PubMed≈20,000 刊) | Embase 覆盖更多欧洲/药物期刊;CNKI 覆盖中文期刊 |
| 同一语言(英文) | CNKI = 中文文献,完全不同的研究生态系统 |

---

## 一、Embase(最推荐,与 PubMed 重叠最少)

### 操作步骤
1. 图书馆登录 Embase
2. 逐条复制检索式,设日期过滤 `2020-01-01 至 2026-10-11`(与证据池同期)
3. 按 relevance 排序,取 **top 20**/规则
4. 导出格式:RIS 或 CSV(含标题+摘要)
5. 21 条规则 × 20 篇 ≈ 400 篇(去重后约 300)

### 检索式(Embase 语法,直接复制)

```
r01: 'uric acid'/exp AND 'cataract'/exp
r02: ('diabetes'/exp OR 'hyperglycemia'/exp) AND 'cataract'/exp
r03: ('hemoglobin a1c'/exp OR 'glycosylated hemoglobin'/exp) AND 'diabetic retinopathy'/exp
r04: ('hemoglobin a1c'/exp OR 'glycosylated hemoglobin'/exp) AND 'proliferative retinopathy'/exp
r05: ('dyslipidemia'/exp OR 'hypercholesterolemia'/exp) AND 'macular degeneration'/exp
r06: ('c reactive protein'/exp) AND 'macular degeneration'/exp
r07: 'vitamin d'/exp AND 'retinopathy'/exp
r08: ('antioxidant'/exp OR 'lutein'/exp OR 'zeaxanthin'/exp) AND 'cataract'/exp
r09: ('mediterranean diet'/exp OR 'dietary pattern'/exp) AND 'macular degeneration'/exp
r10: 'smoking'/exp AND 'cataract'/exp
r11: 'smoking'/exp AND 'macular degeneration'/exp
r12: 'alcohol'/exp AND 'cataract'/exp
r13: ('body mass index'/exp OR 'obesity'/exp) AND 'cataract'/exp
r14: 'lead'/exp AND 'cataract'/exp
r16: ('particulate matter'/exp OR 'pm2.5'/exp) AND ('glaucoma'/exp OR 'intraocular pressure'/exp)
r17: ('particulate matter'/exp OR 'pm2.5'/exp) AND 'macular degeneration'/exp
r18: ('ultraviolet'/exp OR 'uv radiation'/exp) AND 'cataract'/exp
r19: ('dietary inflammatory index'/exp OR 'pro-inflammatory diet'/exp) AND 'retinopathy'/exp
r20: 'smoking'/exp AND ('vision impairment'/exp OR 'visual acuity'/exp)
r21: ('particulate matter'/exp OR 'pm2.5'/exp) AND ('vision impairment'/exp OR 'visual loss'/exp)
r22: ('body mass index'/exp OR 'obesity'/exp) AND 'retinopathy'/exp
```

---

## 二、Web of Science

### 操作步骤
同上,但用以下检索式(WoS 语法,`TS` = Title/Abstract)

```
r01: TS=("uric acid" AND cataract*)
r02: TS=((diabet* OR hyperglycemi*) AND cataract*)
r03: TS=("HbA1c" OR "glycosylated hemoglobin") AND TS("diabetic retinopathy")
r04: TS=("HbA1c" OR "glycosylated hemoglobin") AND TS("proliferative retinopathy" OR PDR)
r05: TS=(dyslipidemia OR cholesterol) AND TS("macular degeneration" OR AMD)
r06: TS=("C-reactive protein" OR CRP) AND TS("macular degeneration" OR AMD)
r07: TS("vitamin D") AND TS(retinopathy)
r08: TS=(antioxidant* OR lutein OR zeaxanthin) AND TS(cataract*)
r09: TS("Mediterranean diet" OR "dietary pattern") AND TS("macular degeneration" OR AMD)
r10: TS(smok*) AND TS(cataract*)
r11: TS(smok*) AND TS("macular degeneration" OR AMD)
r12: TS(alcohol) AND TS(cataract*)
r13: TS("body mass index" OR BMI OR obes*) AND TS(cataract*)
r14: TS(lead AND cataract*)
r16: TS("PM2.5" OR "particulate matter") AND TS(glaucoma OR "intraocular pressure")
r17: TS("PM2.5" OR "particulate matter") AND TS("macular degeneration")
r18: TS(ultraviolet OR "UV radiation") AND TS(cataract*)
r19: TS("pro-inflammatory diet" OR "dietary inflammatory") AND TS(retinopathy)
r20: TS(smok*) AND TS("vision impairment" OR "visual acuity")
r21: TS("PM2.5" OR "particulate matter") AND TS("vision impairment" OR "visual loss")
r22: TS("body mass index" OR BMI OR obes*) AND TS(retinopathy)
```

---

## 三、CNKI 中国知网(最不同的数据库,中文文献)

### 操作步骤
1. 图书馆登录 CNKI → 高级检索
2. 选"学术期刊"+ "学位论文"
3. 逐条运行检索式,日期不限(中文文献池与英文池天然不重叠)
4. 按"相关度"排序,取 **top 15**/规则
5. 导出:Refworks 或 EndNote 格式

### 检索式(CNKI 语法,主题=标题+关键词+摘要)

```
r01: 主题:尿酸 AND 主题:白内障
r02: 主题:(糖尿病 OR 高血糖) AND 主题:白内障
r03: 主题:(糖化血红蛋白 OR 糖化血糖) AND 主题:糖尿病视网膜病变
r04: 主题:(糖化血红蛋白 OR 糖化血糖) AND 主题:增殖性视网膜病变
r05: 主题:(血脂异常 OR 胆固醇) AND 主题:(黄斑变性 OR 年龄相关性黄斑变性)
r06: 主题:C反应蛋白 AND 主题:(黄斑变性 OR 年龄相关性黄斑变性)
r07: 主题:维生素D AND 主题:视网膜病变
r08: 主题:(抗氧化 OR 叶黄素 OR 玉米黄质) AND 主题:白内障
r09: 主题:(地中海饮食 OR 膳食模式) AND 主题:黄斑变性
r10: 主题:吸烟 AND 主题:白内障
r11: 主题:吸烟 AND 主题:黄斑变性
r12: 主题:饮酒 AND 主题:白内障
r13: 主题:(体重指数 OR 肥胖 OR BMI) AND 主题:白内障
r14: 主题:铅 AND 主题:白内障
r16: 主题:(颗粒物 OR PM2.5) AND 主题:(青光眼 OR 眼压)
r17: 主题:(颗粒物 OR PM2.5) AND 主题:黄斑变性
r18: 主题:(紫外线 OR 紫外辐射) AND 主题:白内障
r19: 主题:促炎饮食 AND 主题:视网膜病变
r20: 主题:吸烟 AND 主题:(视力损害 OR 视力下降)
r21: 主题:(颗粒物 OR PM2.5) AND 主题:视力损害
r22: 主题:(体重指数 OR 肥胖 OR BMI) AND 主题:视网膜病变
```

---

## 四、导出后怎么交给我

1. 每个数据库导出一个文件(RIS / CSV / EndNote .enw 均可)
2. 文件命名:`embase_results.{ris|csv}`、`wos_results.{ris|csv}`、`cnki_results.{ris|csv}`
3. 放到 `data/processed/` 目录下
4. 告诉我一声,我运行分析脚本:
   - 去重(排除与 PubMed 证据池重叠的 DOI/标题)
   - LLM 逐篇方向判定(与文献层同协议)
   - 计算 precision_lit_per_database
   - 与 PubMed 基线(0.889)比较

---

## 五、预期结果

| 数据库 | 预计新增(去重后) | 独立性来源 | 预期 precision |
|---|---|---|---|
| Embase | ~200-300 篇 | 更多欧洲/药物期刊,Emtree vs MeSH | 可能低于 0.889(更严格) |
| Web of Science | ~150-250 篇 | 不同排序,引文索引 | 接近 0.889(覆盖面类似) |
| CNKI | ~100-200 篇 | **完全不同的语言和生态系统** | 最不确定(可能发现反向证据) |
| **合计** | ~500-700 篇新文献 | | **文献层从"750 篇 PubMed 审计"升级为"750+700=1450 篇多数据库验证"** |

---

## 六、为什么这很重要

现在论文的文献层写的是:
> *"We validated 21 rules against 750 PubMed papers (precision 0.889)."*
> 审稿人:"你的规则来自 PubMed,你用 PubMed 验证,循环。"

做完多数据库后可以写:
> *"We validated 21 rules against 750 papers from PubMed, plus an independent sample from Embase (N=X), Web of Science (N=Y), and CNKI (N=Z). Precision was consistent across databases (PubMed 0.889, Embase X.XX, CNKI X.XX), supporting the robustness of the rule base beyond a single literature index."*
> 审稿人:无话可说。
