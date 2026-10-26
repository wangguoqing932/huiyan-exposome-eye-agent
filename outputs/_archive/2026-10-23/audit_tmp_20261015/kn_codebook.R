#!/usr/bin/env Rscript
# Dump official KNHANES labels for every variable of interest, per source object.
# This is the codebook we must use instead of guessing name semantics.
base <- Sys.getenv("KN_DIR", unset = ".")
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())

files <- c("kn_2007_2010.Rdata", "kn_2011_2015.Rdata",
           "kn_2016_2020.Rdata", "kn_2021_2024.Rdata")

rows <- list()
for (f in files) {
  p <- file.path(base, f)
  if (!file.exists(p)) next
  e <- new.env(); load(p, envir = e)
  if (!exists("dictionary", envir = e)) { cat("no dictionary in", f, "\n"); next }
  d <- get("dictionary", envir = e)
  names(d) <- c("id","kr","cn","note","from","year","rdata")
  rows[[length(rows) + 1]] <- d
  rm(e); gc(verbose = FALSE)
}
dict <- do.call(rbind, rows)
dict <- dict[!duplicated(dict[, c("id","from")]), ]

write.csv(dict, file.path(outdir, "kn_dictionary_full.csv"), row.names = FALSE)
cat("dictionary rows:", nrow(dict), "\n\n")

# --- what we need to decode: eye variables of the 2016-2021 scheme
show <- function(ids) {
  for (v in ids) {
    sub <- dict[dict$id == v, ]
    if (nrow(sub) == 0) { cat(sprintf('%-12s : NOT IN DICTIONARY\n', v)); next }
    for (i in seq_len(min(nrow(sub), 6))) {
      cat(sprintf('%-12s | %-22s | %s\n', v, sub$from[i], sub$cn[i]))
    }
  }
}
cat("=== 2016-2021 eye scheme ===\n")
show(c("E_DR","E_DR1","E_AMD","E_AMD_l","E_AMD_r","E_DM","E_DM_l","E_DM_r",
       "E_DME","E_DME_l","E_DME_r","E_EM","E_EM_l","E_EM_r","E_GR","E_DG","E_DG1",
       "E_RT","E_ex","E_CT","E_Q_EX"))

cat("\n=== 2008-2012 eye scheme ===\n")
show(c("E_DRP_R","E_DRP_L","E_DRP_Rorp","E_DRP_Lorp","E_AMD_ELY_R","E_AMD_LATE_R",
       "E_AMD_WET_R","E_AMD_DRY_R","E_VS_DS","E_Gr_p","E_Gl_p","E_Grv","E_Glv",
       "E_Pr_1","E_GR","E_AMR_RT"))

cat("\n=== self-report eye (DH*) ===\n")
show(c("DH1_dg","DH1_lt","DH2_lt","DH2_dg","DH3_lt","DH3_dg","DH4_dg","DH6_dg","DH7_dg"))

cat("\n=== smoking / alcohol ===\n")
show(c("BS1_1","BS3_1","BS5","BS5_1","BA2_12","BA2_13","BA2_14","BA2_22","BA2_2_1"))

cat("\n=== labs / design ===\n")
show(c("HE_Uacid","HE_UAScr","HE_hsCRP","HE_HbA1c","HE_glu","HE_BMI","HE_chol","HE_TG",
       "HE_HDL_st2","HE_LDL_drct","HE_VitD","HE_25OHD","HE_crea",
       "edu","incm","incm5","wt_itvex","wt_itv","wt_ex","psu","kstrata"))

cat("\n=== anything vitamin-D / antioxidant / PM2.5-like ===\n")
hit <- dict[grepl("vit|Vit|25|OHD|carot|retinol|toco|antiox|PM|particulate|air|iaq",
                  dict$id) | grepl("vitamin|carot|particulate|air quality", dict$cn, ignore.case = TRUE), ]
hit <- hit[!duplicated(hit$id), ]
print(head(hit[, c("id","cn","from")], 40), row.names = FALSE)
