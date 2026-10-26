#!/usr/bin/env Rscript
# Inventory every KNHANES wave object in the local Rdata collection:
# which objects exist, their dims, and whether key variables are present.
# Writes a machine-readable inventory to .audit_tmp/knhanes_inventory.csv
suppressPackageStartupMessages(library(tools))

base <- "E:/BaiduNetdiskDownload/所有数据库/11. KNHANES 韩国国民健康与营养调查/Rdata"
files <- c(
  "KNHANES 1998-2005.Rdata",
  "KNHANES 2007-2010.Rdata",
  "KNHANES 2011-2015.Rdata",
  "KNHANES 2016-2020.Rdata",
  "KNHANES 2021-2024.Rdata"
)

# variables we care about (exposure / outcome / design / covariate)
want <- c(
  # design + covariates
  "ID","id","year","sex","age","psu","kstrata","kstrata0","kstrata1","wt_itvex","wt_itv","wt_ex",
  "edu","incm","ho_incm","incm5","occp","region","marri","age_g",
  # smoking / alcohol / lifestyle
  "BS1_1","BS3_1","BS5","BS5_1","BA2_2_1","BA2_22","BA2_12","BA2_13","BA2_14",
  # anthropometry + labs
  "HE_BMI","HE_wc","HE_HbA1c","HE_glu","HE_chol","HE_TG","HE_HDL_st2","HE_LDL_drct",
  "HE_hsCRP","HE_Uacid","HE_UAScr","HE_UAScr_AAS","HE_crea","HE_VitD","HE_25OHD",
  "HE_VC","HE_VE","HE_carot","HE_ast","HE_alt","HE_insulin","HE_HOMA",
  # self-reported eye disease
  "DH2_lt","DH3_lt","DH1_dg","DH1_pr",
  # eye exam
  "E_DRP_R","E_DRP_L","E_AMD_ELY_R","E_AMD_LATE_R","E_AMD_ELY_L","E_AMD_LATE_L",
  "E_VS_DS","E_VS_MYO","E_VS_HYPER","E_Gr_p","E_Gl_p","E_Grv","E_Glv","E_Pr_1","E_GR",
  "E_AMD_WET_R","E_AMD_DRY_R","E_DRP_Rorp","E_DRP_Lorp"
)

rows <- list()
for (f in files) {
  p <- file.path(base, f)
  if (!file.exists(p)) { cat("MISSING:", p, "\n"); next }
  e <- new.env()
  ok <- tryCatch({ load(p, envir = e); TRUE }, error = function(x) { cat("LOAD FAIL:", f, conditionMessage(x), "\n"); FALSE })
  if (!ok) next
  objs <- ls(e)
  cat(sprintf("== %s : %d objects\n", f, length(objs)))
  for (o in objs) {
    x <- get(o, envir = e)
    if (!is.data.frame(x)) next
    cn <- colnames(x)
    hits <- intersect(want, cn)
    rows[[length(rows) + 1]] <- data.frame(
      rdata = f, obj = o, nrow = nrow(x), ncol = ncol(x),
      n_want = length(hits),
      want_found = paste(hits, collapse = "|"),
      stringsAsFactors = FALSE
    )
  }
  rm(e); gc(verbose = FALSE)
}

inv <- do.call(rbind, rows)
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
write.csv(inv, file.path(outdir, "knhanes_inventory.csv"), row.names = FALSE)
cat("\nInventory rows:", nrow(inv), "\n")
print(inv[, c("rdata", "obj", "nrow", "ncol", "n_want")], row.names = FALSE)
