# TIFF 体积问题（已知项，非本轮引入）

## 现状

`outputs/figures/*.tiff` 合计 **593.4 MB**（7 张）；新图 figure8 为 **0.98 MB**。

| 图 | TIFF 体积 | 渲染器 |
|---|---|---|
| figure1_architecture | ~81 MB | 共享渲染器（无压缩） |
| figure2_performance | ~大 | 共享渲染器（无压缩） |
| figure3_rule_evaluation | ~大 | 共享渲染器（无压缩） |
| figure4_demo_case | ~大 | 共享渲染器（无压缩） |
| figure5_reasoning_trace | ~大 | 共享渲染器（无压缩） |
| figure6_dose_response | ~大 | 共享渲染器（无压缩） |
| figure7_power_mde | ~大 | 共享渲染器（无压缩） |
| **figure8_cohort_transportability** | **0.98 MB** | **项目内渲染器（LZW）** |

## 原因

`~/.dsh/skills/medical-agent-writer/scripts/build_figures.py` 用 matplotlib 默认参数
写 TIFF，即 **无压缩**。180 mm × 600 dpi 的图约 80 MB/张。

## 影响

593 MB 的 TIFF 是**投稿门户的实际障碍**（多数期刊单文件上限 10–50 MB），
且与图像质量无关——LZW 是**无损**压缩。

## 两条修法

### (a) 在共享渲染器里修（治本，影响所有项目）

`build_figures.py` 的 `_save`/导出处，为 TIFF 传
`pil_kwargs={"compression": "tiff_lzw"}` 给 `fig.savefig`。
**默认行为改变，但输出无损**——建议连同上一轮记录的 forest `log_x`/`ref` 钩子一起提。

### (b) 就地重压（治标，仅本项目）

**当前沙箱下不可行**，两种尝试都失败：

| 尝试 | 结果 |
|---|---|
| `PIL.Image.save(同路径, compression='tiff_lzw')` | `OSError: [Errno 22] Invalid argument`（PIL 以 `w+b` 打开该路径失败） |
| 写 `*.tiff.tmp` 再 `os.replace` | `PermissionError: [WinError 5] 拒绝访问`（沙箱禁止创建 `.tmp`） |

**但同一路径用 `open(p, 'r+b')` 与 `p.write_bytes(...)` 均可写**——说明是
PIL 的打开模式与沙箱 ACL 的组合问题，不是路径或权限本身。

因此 (b) 需要在**沙箱外**执行，命令如下（已验证 figure8 走同一 LZW 路径后为 0.98 MB）：

```python
import pathlib, os
from PIL import Image
d = pathlib.Path("outputs/figures")
for p in sorted(d.glob("*.tiff")):
    b = p.stat().st_size
    with Image.open(p) as im:
        arr = im.copy()
    if arr.mode == "RGBA":                     # 这些图是白底不透明
        bg = Image.new("RGB", arr.size, (255, 255, 255))
        bg.paste(arr, mask=arr.split()[-1]); arr = bg
    elif arr.mode not in ("RGB", "L"):
        arr = arr.convert("RGB")
    arr.save(p, format="TIFF", compression="tiff_lzw")
    print(p.name, f"{b/1e6:.1f} -> {p.stat().st_size/1e6:.2f} MB")
```

预期：593 MB → 约 10–12 MB（figure8 实测减 98%）。

## 处置决定

**本轮不阻塞 writer 管线**：图片体积不影响科学正确性，也不影响图例、正文与
投稿包的撰写。已在 7_1 QC 报告与本文档留痕，作为**投稿前必须解决**的清单项，
优先走修法 (a)。
