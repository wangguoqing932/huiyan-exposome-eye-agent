#!/usr/bin/env Rscript
# Inventory KNHANES wave objects from ASCII-path copies, and report which
# target variables are present in which per-year object.
base <- Sys.getenv("KN_DIR", unset = ".")
files <- c("kn_1998_2005.Rdata", "kn_2007_2010.Rdata", "kn_2011_2015.Rdata",
           "kn_2016_2020.Rdata", "kn_2021_2024.Rdata")

want <- c(
  "ID","id","year","sex","age","psu","kstrata","kstrata0","kstrata1",
  "wt_itvex","wt_itv","wt_ex","wt_hs","edu","incm","ho_incm","incm5","occp","region",
  "BS1_1","BS3_1","BA2_12","BA2_13","BA2_14","BA2_22","BA2_2_1",
  "HE_BMI","HE_wc","HE_HbA1c","HE_glu","HE_chol","HE_TG","HE_HDL_st2","HE_LDL_drct",
  "HE_hsCRP","HE_Uacid","HE_UAScr","HE_UAScr_AAS","HE_crea","HE_VitD","HE_25OHD",
  "HE_VC","HE_VE","HE_carot","HE_insulin",
  "DH2_lt","DH3_lt","DH1_dg",
  "E_DRP_R","E_DRP_L","E_AMD_ELY_R","E_AMD_LATE_R","E_AMD_ELY_L","E_AMD_LATE_L",
  "E_VS_DS","E_VS_MYO","E_VS_HYPER","E_Gr_p","E_Gl_p","E_Grv","E_Glv","E_Pr_1","E_GR"
)

rows <- list()
for (f in files) {
  p <- file.path(base, f)
  if (!file.exists(p)) { cat("MISSING:", p, "\n"); next }
  e <- new.env()
  ok <- tryCatch({ load(p, envir = e); TRUE },
                 error = function(x) { cat("LOAD FAIL:", f, conditionMessage(x), "\n"); FALSE })
  if (!ok) next
  objs <- ls(e)
  dfs <- Filter(function(o) is.data.frame(get(o, envir = e)), objs)
  cat(sprintf("== %-22s objects=%d  data.frames=%d\n", f, length(objs), length(dfs)))
  cat("   objects:", paste(objs, collapse = ", "), "\n")
  for (o in dfs) {
    x <- get(o, envir = e)
    cn <- colnames(x)
    hits <- intersect(want, cn)
    rows[[length(rows) + 1]] <- data.frame(
      rdata = f, obj = o, nrow = nrow(x), ncol = ncol(x), n_want = length(hits),
      has_eye = any(grepl("^E_(DRP|AMD|VS|Gr|Gl)", cn)),
      has_BS3 = "BS3_1" %in% cn, has_edu = "edu" %in% cn, has_incm = "incm" %in% cn,
      want_found = paste(hits, collapse = "|"), stringsAsFactors = FALSE)
  }
  rm(e); gc(verbose = FALSE)
}
inv <- do.call(rbind, rows)
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
write.csv(inv, file.path(outdir, "knhanes_inventory.csv"), row.names = FALSE)
cat("\n--- data.frame objects with n_want>=30 ---\n")
print(inv[inv$n_want >= 30, c("rdata","obj","nrow","ncol","n_want","has_eye","has_BS3","has_edu","has_incm")],
      row.names = FALSE)
