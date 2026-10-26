# Table 1b. Characteristics of the analysed populations (STROBE items 14a and 14b)

Computed from the same cohort frames the analysis uses, so the table cannot drift from the analysis. The unit is the person-wave, which is the analysed unit; SHARE's five imputation replicates are collapsed to replicate 1, so neither denominators nor prevalences are inflated.

Percentages are of person-waves with the variable observed. Missingness is reported separately in the table below.

| Cohort | Person-waves | Age, years, mean (SD) | Female, % | Current smoking, % | Diabetes (self-reported), % | BMI above the cohort cut-point, % | Cataract, % | Moderate vision impairment, % |
|---|---|---|---|---|---|---|---|---|
| SHARE | 338,703 | 67.9 (10.3) | 56.7 | 17.1 | 13.6 | 22.8 | 8.4 | 14.0 |
| HRS | 42,946 | 65.7 (11.8) | 58.5 | 22.5 | 24.5 | not available | 13.5 | 19.1 |
| ELSA | 9,771 | 64.9 (10.6) | 56.4 | 23.8 | not available | not available | 22.2 | 11.8 |
| KLoSA | 40,406 | 65.7 (11.0) | 57.0 | 14.2 | 5.4 | 23.1 | 4.5 | 20.9 |
| LASI | 73,408 | 57.9 (11.7) | 57.6 | not available | 12.1 | not available | 11.2 | 12.1 |
| MHAS | 15,217 | 60.3 (10.8) | 57.2 | not available | not available | not available | not available | 34.8 |
| CLHLS | 72,744 | 92.0 (7.9) | 60.0 | 15.9 | 1.4 | not available | 17.1 | 13.5 |
| CRELES | 5,191 | 76.7 (10.0) | 54.4 | 11.0 | 19.1 | 20.0 | 38.5 | not available |

### Missingness (% of person-waves with the variable missing)

**Read this table with the caveat that follows.** A 100% cell here usually means the variable is not carried in this cohort's analysis frame, not that the survey failed to measure it or that the item went unanswered. The frames were built to hold only what the pre-specified rules need, so a cohort that contributes no BMI rule has no BMI column at all and reports 100%. This column therefore describes **frame coverage**, which is what decides which (rule x cohort) cells are testable -- it is not an item non-response rate.

| Cohort | Age, years, mean (SD) | Female, % | Current smoking, % | Diabetes (self-reported), % | BMI above the cohort cut-point, % | Cataract, % | Moderate vision impairment, % | Missing at least one, % |
|---|---|---|---|---|---|---|---|---|
| SHARE | 0.0 | 0.0 | 58.0 | 0.4 | 0.0 | 0.4 | 18.7 | 58.1 |
| HRS | 51.3 | 51.3 | 33.1 | 0.7 | 100.0 | 62.5 | 0.3 | 100.0 |
| ELSA | 20.5 | 19.8 | 51.8 | 100.0 | 100.0 | 17.2 | 3.4 | 100.0 |
| KLoSA | 0.0 | 0.0 | 0.0 | 24.6 | 2.3 | 0.4 | 0.4 | 26.7 |
| LASI | 0.0 | 0.0 | 100.0 | 0.3 | 100.0 | 0.0 | 0.3 | 100.0 |
| MHAS | 0.2 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 7.6 | 100.0 |
| CLHLS | 7.3 | 0.0 | 75.1 | 76.8 | 100.0 | 76.6 | 81.9 | 100.0 |
| CRELES | 0.0 | 0.0 | 31.2 | 0.5 | 4.4 | 1.7 | 100.0 | 100.0 |

**Footnotes.**
* **Frame coverage versus item non-response.** Where a variable is present, its missingness is genuine non-response, SHARE's smoking is 58.0% missing with the column present, while HRS's BMI is 100% missing because the frame carries no BMI column.
* **Age in CLHLS is a baseline value repeated across waves**, not a follow-up age: 92.74% of its participants have a single unique age across all their waves, so its mean is not comparable to the others and should not be read as an average age during follow-up. The frame defect is documented in `docs/GAP_ANALYSIS_20IF.md`.
* **Diabetes is self-reported** in every cohort, so its prevalence reflects diagnosis rates rather than disease prevalence, the mechanism the paper demonstrates with the NHANES comparison.
* **Cataract and vision impairment are absent from HRS, KLoSA and MHAS** in these frames, which is why the cohort layer tests only six rules: those cohorts cannot contribute a cataract or vision-impairment cell.
* The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² otherwise, fixed by the prevalence gate before the confirmatory analysis.
