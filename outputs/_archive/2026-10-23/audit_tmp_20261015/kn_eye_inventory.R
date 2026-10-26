#!/usr/bin/env Rscript
# What eye / outcome / exposure columns actually exist in each KNHANES year object?
base <- Sys.getenv("KN_DIR", unset = ".")
files <- c("kn_2007_2010.Rdata", "kn_2011_2015.Rdata",
           "kn_2016_2020.Rdata", "kn_2021_2024.Rdata")

eye_pat <- "^(E_|DH[0-9]|OPD|VID|VIQ|LE_|HE_)"
key_expo <- c("HE_Uacid","HE_UAScr","HE_hsCRP","HE_HbA1c","HE_glu","HE_BMI","HE_chol",
              "HE_TG","HE_HDL_st2","HE_LDL_drct","HE_crea","HE_VitD","HE_25OHD",
              "BS1_1","BS3_1","BA2_22","BA2_12","BA2_13","BA2_14",
              "wt_itvex","edu","incm","psu","kstrata")

out <- list()
for (f in files) {
  p <- file.path(base, f)
  if (!file.exists(p)) next
  e <- new.env(); load(p, envir = e)
  dfs <- Filter(function(o) is.data.frame(get(o, envir = e)), ls(e))
  for (o in dfs) {
    if (!grepl("^hn[0-9]{2}_", o)) next
    x <- get(o, envir = e); cn <- colnames(x)
    eye <- grep(eye_pat, cn, value = TRUE)
    ex  <- intersect(key_expo, cn)
    if (length(eye) == 0 && length(ex) == 0) next
    out[[length(out) + 1]] <- data.frame(
      obj = o, nrow = nrow(x), ncol = ncol(x),
      n_eye = length(eye), n_expo = length(ex),
      eye_vars = paste(head(sort(eye), 30), collapse = "|"),
      expo_vars = paste(sort(ex), collapse = "|"),
      stringsAsFactors = FALSE)
  }
  rm(e); gc(verbose = FALSE)
}
res <- do.call(rbind, out)
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
write.csv(res, file.path(outdir, "kn_eye_inventory.csv"), row.names = FALSE)

cat("=== objects with eye variables ===\n")
for (i in seq_len(nrow(res))) {
  cat(sprintf("\n-- %s  rows=%d cols=%d  n_eye=%d  n_expo=%d\n",
              res$obj[i], res$nrow[i], res$ncol[i], res$n_eye[i], res$n_expo[i]))
  if (res$n_eye[i] > 0) cat("   EYE :", res$eye_vars[i], "\n")
  cat("   EXPO:", res$expo_vars[i], "\n")
}
