#!/usr/bin/env python
"""Refine outputs/paper/figure_legends.md (writer 7_2).

Two mechanical defects in the generated draft, plus the abbreviation fields:

1. `(**a**) . Text` -- the builder emits a space-dot-space after every panel
   label when the panel has no separate title, which reads as a stray period.
2. `Abbreviations: [TODO: expand all abbreviations used in this figure].`
   appears under all eight figures. A placeholder shipped in a submission is a
   desk-reject item, so each is replaced with the abbreviations that figure
   actually uses. They are listed from the contract text and the source CSVs,
   not invented.

The Chinese scaffold is left as TODO on purpose: phase 7_8 (bilingual polish)
owns that translation, and pre-translating here would mean translating text that
7_4-7_7 may still change.

Run: python scripts/refine_figure_legends.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FP = ROOT / "outputs" / "paper" / "figure_legends.md"

# Abbreviations actually used by each figure, taken from its contract and its
# source_data CSV.
ABBR = {
    1: "LLM = large language model; KG = knowledge graph; YAML = YAML Ain't "
       "Markup Language; LightRAG = lightweight retrieval-augmented generation; "
       "GPT = generative pre-trained transformer.",
    2: "F1 = F1 score; P = precision; R = recall; LLM = large language model; "
       "NHANES = National Health and Nutrition Examination Survey; "
       "R5/R11 = internal analysis revisions (gold-label versions); "
       "SD = standard deviation; n.s. = not significant.",
    3: "CI = confidence interval; BHY = Benjamini-Hochberg-Yekutieli; "
       "FDR = false discovery rate; NHANES = National Health and Nutrition "
       "Examination Survey; KNHANES = Korea National Health and Nutrition "
       "Examination Survey.",
    4: "OR = odds ratio; LLM = large language model; "
       "AMD = age-related macular degeneration; DR = diabetic retinopathy; "
       "IOP = intraocular pressure; CDR = cup-to-disc ratio.",
    5: "KG = knowledge graph; LLM = large language model; "
       "LightRAG = lightweight retrieval-augmented generation; "
       "CI = confidence interval.",
    6: "SD = standard deviation; OR = odds ratio; CI = confidence interval; "
       "NHANES = National Health and Nutrition Examination Survey; "
       "KNHANES = Korea National Health and Nutrition Examination Survey.",
    7: "OR = odds ratio; MDE = minimum detectable effect (here, the minimum "
       "detectable odds ratio at 80% power); NHANES = National Health and "
       "Nutrition Examination Survey; KNHANES = Korea National Health and "
       "Nutrition Examination Survey.",
    8: "OR = odds ratio; CI = confidence interval; BHY = "
       "Benjamini-Hochberg-Yekutieli; FDR = false discovery rate; "
       "AMD = age-related macular degeneration; SHARE = Survey of Health, "
       "Ageing and Retirement in Europe; HRS = Health and Retirement Study; "
       "ELSA = English Longitudinal Study of Ageing; KLoSA = Korean "
       "Longitudinal Study of Ageing; LASI = Longitudinal Ageing Study in "
       "India; MHAS = Mexican Health and Aging Study; CLHLS = Chinese "
       "Longitudinal Healthy Longevity Survey; CRELES = Costa Rican Study on "
       "Longevity and Healthy Ageing; IOP = intraocular pressure; "
       "CDR = cup-to-disc ratio; r01-r22 = pre-registered rule identifiers in "
       "configs/rules.yaml.",
}


def main() -> int:
    text = FP.read_text(encoding="utf-8")

    # 1. stray " . " after a panel label
    before = text.count(") . ")
    text = text.replace(") . ", ") ")

    # 2. abbreviations, figure by figure
    parts = re.split(r"(?m)^\*\*Figure (\d+)\.", text)
    if len(parts) < 3:
        print("could not split the legends by figure")
        return 1
    out = [parts[0]]
    filled = 0
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        body = parts[i + 1]
        if num in ABBR:
            new, n = re.subn(
                r"Abbreviations: \[TODO: expand all abbreviations used in this "
                r"figure\]\.",
                "Abbreviations: " + ABBR[num], body)
            filled += n
            body = new
        out.append(f"**Figure {num}.")
        out.append(body)
    text = "".join(out)
    FP.write_text(text, encoding="utf-8")

    print(f"stray ' . ' artefacts removed: {before}")
    print(f"abbreviation placeholders filled: {filled}")
    remaining = text.count("[TODO: expand all abbreviations")
    print(f"remaining abbreviation TODOs: {remaining}")
    print(f"-> {FP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
