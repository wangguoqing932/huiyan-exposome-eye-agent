# TIFF 体积问题（已解决，2026-10-23）

## 原问题

共享渲染器输出无压缩 TIFF，7 张合计约 593 MB，是投稿门户上传的实际障碍
（figure7 90.9 MB、figure8 57.5 MB 为最坏两例）。

## 处置

- `scripts/render_locked_figures.py`（figure3/6/7/8）已使用 `tiff_lzw` 压缩。
- `scripts/generate_paper_figures.py`（figure1/2/4/5）于 2026-10-23 改为
  `pil_kwargs={"compression": "tiff_lzw"}`，同时补齐 SVG + TIFF 导出，
  使四张图与契约 `export.formats: [svg, pdf, tiff, png]` 一致。

## 现状（2026-10-23 实测）

`outputs/figures/*.tiff` 合计 **6.2 MB**，单图最大 1.16 MB（figure2）。

复验命令：`du -ch outputs/figures/*.tiff`。
