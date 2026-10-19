#!/usr/bin/env Rscript
# R5 P0-4 (2026-10-14): survey-design sensitivity for confirmatory pairs.
# analysis_plan §6 pre-registered svyglm (strata/PSU) as the variance standard.
# Re-fits every exported pair with proper survey variance and writes
# outputs/confirmatory/survey_sensitivity_R5.csv for comparison with the
# Python freq_weights GLM main analysis.
suppressPackageStartupMessages(library(survey))

# R11 2026-10-15: paths parameterised so the same script serves the binary
# (rule-validation) layer and the continuous (per-1-SD dose-response) layer.
indir <- Sys.getenv("SVY_INDIR", unset = "data/processed/survey_pairs_R5")
outfile <- Sys.getenv("SVY_OUTFILE", unset = "outputs/confirmatory/survey_sensitivity_R5.csv")

files <- list.files(indir, pattern = "\\.csv$", full.names = TRUE)
options(survey.lonely.psu = "adjust")

rows <- list()
for (f in files) {
  d <- read.csv(f, stringsAsFactors = FALSE)
  pair <- d$pair[1]
  ds <- d$dataset[1]
  covs <- setdiff(names(d), c("y", "x", "wt", "strata", "psu", "dataset", "pair", "cycle"))
  res <- tryCatch({
    des <- svydesign(ids = ~psu, strata = ~strata, weights = ~wt, data = d, nest = TRUE)
    fml <- as.formula(paste("y ~ x +", paste(covs, collapse = " + ")))
    fit <- svyglm(fml, design = des, family = quasibinomial())
    s <- summary(fit)$coefficients
    est <- s["x", "Estimate"]; se <- s["x", "Std. Error"]; pval <- s["x", "Pr(>|t|)"]
    ci <- exp(est + c(-1, 1) * 1.96 * se)
    data.frame(dataset = ds, pair = pair, n = nrow(d),
               or = exp(est), ci_lo = ci[1], ci_hi = ci[2], p = pval,
               stringsAsFactors = FALSE)
  }, error = function(e) {
    data.frame(dataset = ds, pair = pair, n = nrow(d),
               or = NA, ci_lo = NA, ci_hi = NA,
               p = NA, stringsAsFactors = FALSE)
  })
  rows[[length(rows) + 1]] <- res
}

out <- do.call(rbind, rows)
write.csv(out, outfile, row.names = FALSE)
cat(sprintf("survey sensitivity: %d pairs written to %s\n", nrow(out), outfile))
cat(sprintf("  fits failed: %d\n", sum(is.na(out$p))))
rep_pairs <- out[!is.na(out$p) & out$p < 0.05, ]
cat(sprintf("  pairs with survey p<0.05: %d\n", nrow(rep_pairs)))
