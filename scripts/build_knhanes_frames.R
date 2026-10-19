#!/usr/bin/env Rscript
# ============================================================================
# build_knhanes_frames.R — 码本驱动的 KNHANES frame 重建
#
# 背景：原 data/raw/knhanes_frames/*.csv 没有对应的生成脚本，且
#   ① 丢了 BS3_1（当前吸烟）、edu、incm
#   ② 只用了 2008-2012 的眼科命名（E_DRP_*/E_AMD_ELY_*），
#      2016-2021 的新命名（E_DM/E_AMD/E_GR/E_DME）完全没合并
#   ③ 没加载 _ap（大气污染）模块
#   ④ 用了 BA2_2_1（酒后骑自行车）当饮酒
#   本脚本按 configs/variable_map.yaml 逐条重建。
#
# 用法（PowerShell）：
#   $env:KN_DIR  = "E:\...\Rdata"          # 中文路径经环境变量传入可行
#   $env:KN_OUT  = "<repo>\data\raw\knhanes_frames_v2"
#   Rscript --vanilla scripts/build_knhanes_frames.R
# ============================================================================

base <- Sys.getenv("KN_DIR", unset = "")
outdir <- Sys.getenv("KN_OUT", unset = "")
if (base == "" || outdir == "") stop("must set KN_DIR and KN_OUT")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

RDATA <- list(
  `2007-2010` = "KNHANES 2007-2010.Rdata",
  `2011-2015` = "KNHANES 2011-2015.Rdata",
  `2016-2020` = "KNHANES 2016-2020.Rdata",
  `2021-2024` = "KNHANES 2021-2024.Rdata"
)

# year -> c(rdata key, all object, eye object (or NA), ap object (or NA))
PLAN <- list(
  list(y = 2008, rd = "2007-2010", all = "hn08_all", eye = "hn08_eye", ap = "hn08_ap"),
  list(y = 2009, rd = "2007-2010", all = "hn09_all", eye = "hn09_eye", ap = "hn09_ap"),
  list(y = 2010, rd = "2007-2010", all = "hn10_all", eye = "hn10_eye", ap = "hn10_ap"),
  list(y = 2011, rd = "2011-2015", all = "hn11_all", eye = "hn11_eye", ap = "hn11_ap"),
  list(y = 2012, rd = "2011-2015", all = "hn12_all", eye = "hn12_eye", ap = "hn12_ap"),
  list(y = 2017, rd = "2016-2020", all = "hn17_all", eye = NA,          ap = "hn17_ap"),
  list(y = 2018, rd = "2016-2020", all = "hn18_all", eye = NA,          ap = "hn18_ap"),
  list(y = 2019, rd = "2016-2020", all = "hn19_all", eye = NA,          ap = "hn19_ap"),
  list(y = 2020, rd = "2016-2020", all = "hn20_all", eye = NA,          ap = "hn20_ap"),
  list(y = 2021, rd = "2021-2024", all = "hn21_all", eye = NA,          ap = "hn21_ap")
)

# ---- 需要抽取的列（全部为码本已核实的名字；不在对象中的会被跳过并记录） ----
COLS_DESIGN <- c("id", "ID", "year", "sex", "age", "psu", "kstrata",
                 "wt_itvex", "wt_itv", "wt_ex", "edu", "incm", "incm5", "region")

COLS_SMOKE  <- c("BS1_1", "BS3_1", "BS5", "BS5_1", "BS12_1")
COLS_ALCOHOL<- c("BD1", "BD1_11", "BD2", "BD2_1", "BD2_14", "BD2_31", "BD2_32", "BD4")
COLS_ALC_BAD<- c("BA2_2_1", "BA2_22", "BA2_12", "BA2_13", "BA2_14")   # 保留仅供审计
COLS_ANTHRO <- c("HE_BMI", "HE_wc", "HE_ht", "HE_wt", "HE_sbp", "HE_dbp")
COLS_GLY    <- c("HE_HbA1c", "HE_glu", "HE_insulin", "HE_DM")
COLS_LIPID  <- c("HE_chol", "HE_TG", "HE_HDL_st2", "HE_LDL_drct")
COLS_INFLAM <- c("HE_hsCRP", "HE_WBC")
COLS_METAL  <- c("HE_Pb", "HE_Cd", "HE_Hg", "HE_Uacid", "HE_crea")
COLS_VIT    <- c("HE_vitD", "HE_VitA", "HE_VitE", "N_VITC", "N_VITE", "N_VITD", "N_CAROT",
                 "LS_VIT", "LS_1YR", "LS_1MO", "TLS_VITC", "FQ_VITC")
COLS_DIET   <- c("N_FAT", "N_FIBER", "N_N3", "N_NA", "N_CA", "N_PROT", "N_KCAL", "N_CHOL",
                 "N_CAROT", "N_VITC", "N_VITE", "N_VITD", "N_FOLA")

# 自报眼病（两套命名都取，保留原始语义，不做合并）
COLS_EYE_SR <- c("DH1_dg", "DH1_lt", "DH2_lt", "DH2_dg", "DH3_lt", "DH3_dg",
                 "DH4_dg", "DH6_dg", "DH7_dg")
# 眼科检查：2008-2012 旧命名
COLS_EYE_OLD <- c("E_DRP_R", "E_DRP_L", "E_DRP_Rorp", "E_DRP_Lorp",
                  "E_AMD_ELY_R", "E_AMD_ELY_L", "E_AMD_LATE_R", "E_AMD_LATE_L",
                  "E_AMD_WET_R", "E_AMD_WET_L", "E_AMD_DRY_R", "E_AMD_DRY_L",
                  "E_VS_DS", "E_Gr_p", "E_Gl_p", "E_Grv", "E_Glv",
                  "E_ex", "E_Q_EX", "E_Q_SUN")
# 眼科检查：2016-2021 新命名
COLS_EYE_NEW <- c("E_DM", "E_DM_r", "E_DM_l", "E_DME", "E_DME_r", "E_DME_l",
                  "E_AMD", "E_AMD_r", "E_AMD_l", "E_EM", "E_EM_r", "E_EM_l",
                  "E_GR", "E_Pr_1", "E_DG", "E_DG1", "E_ex", "E_Q_EX",
                  "E_DR")   # E_DR 保留仅供审计（=眼药水，不是 DR）
COLS_AP     <- c("PM25", "PM10", "O3", "NO2", "SO2", "CO")
COLS_IAQ    <- c("IAQ_PM2_5", "IAQ_PM2_5_atmos")

ALLWANT <- unique(c(COLS_DESIGN, COLS_SMOKE, COLS_ALCOHOL, COLS_ALC_BAD, COLS_ANTHRO,
                    COLS_GLY, COLS_LIPID, COLS_INFLAM, COLS_METAL, COLS_VIT, COLS_DIET,
                    COLS_EYE_SR, COLS_EYE_OLD, COLS_EYE_NEW, COLS_AP, COLS_IAQ))

env_cache <- list()
getobj <- function(rd, obj) {
  if (is.null(env_cache[[rd]])) {
    p <- file.path(base, RDATA[[rd]])
    e <- new.env(); load(p, envir = e); env_cache[[rd]] <<- e
    cat("loaded", RDATA[[rd]], "\n")
  }
  e <- env_cache[[rd]]
  if (!exists(obj, envir = e)) return(NULL)
  as.data.frame(get(obj, envir = e))
}

pick_key <- function(d) {
  for (k in c("id", "ID", "IDNO", "seq", "SEQN")) if (k %in% colnames(d)) return(k)
  NULL
}

take <- function(d, want) {
  got <- intersect(want, colnames(d))
  d[, got, drop = FALSE]
}

codebook <- list()
report <- list()

for (pl in PLAN) {
  y <- pl$y
  a <- getobj(pl$rd, pl$all)
  if (is.null(a)) { cat("!! no object", pl$all, "\n"); next }
  a <- as.data.frame(a)
  ka <- pick_key(a)
  part <- take(a, ALLWANT)
  part$wave <- y
  srcs <- data.frame(obj = pl$all, col = colnames(part), role = "all")

  # eye module (only 2008-2012 have a separate object)
  if (!is.na(pl$eye)) {
    e <- getobj(pl$rd, pl$eye)
    if (!is.null(e)) {
      e <- as.data.frame(e); ke <- pick_key(e)
      if (!is.null(ka) && !is.null(ke) && ke %in% colnames(e)) {
        ee <- take(e, ALLWANT)
        # avoid duplicate columns already present in _all
        dup <- intersect(colnames(ee), colnames(part))
        dup <- setdiff(dup, ke)
        ee <- ee[, setdiff(colnames(ee), dup), drop = FALSE]
        part <- merge(part, ee, by.x = ka, by.y = ke, all.x = TRUE, sort = FALSE)
        srcs <- rbind(srcs, data.frame(obj = pl$eye, col = colnames(ee), role = "eye"))
      }
    }
  }

  # air pollution module
  if (!is.na(pl$ap)) {
    ap <- getobj(pl$rd, pl$ap)
    if (!is.null(ap)) {
      ap <- as.data.frame(ap); kp <- pick_key(ap)
      if (!is.null(ka) && !is.null(kp)) {
        aa <- take(ap, ALLWANT)
        dup <- intersect(colnames(aa), colnames(part)); dup <- setdiff(dup, kp)
        aa <- aa[, setdiff(colnames(aa), dup), drop = FALSE]
        part <- merge(part, aa, by.x = ka, by.y = kp, all.x = TRUE, sort = FALSE)
        srcs <- rbind(srcs, data.frame(obj = pl$ap, col = colnames(aa), role = "ap"))
      }
    }
  }

  # IAQ module (2021 only)
  if (y == 2021) {
    iaq <- getobj("2021-2024", "hn21_iaq")
    if (!is.null(iaq)) {
      iaq <- as.data.frame(iaq); ki <- pick_key(iaq)
      if (!is.null(ka) && !is.null(ki)) {
        ii <- take(iaq, ALLWANT)
        dup <- intersect(colnames(ii), colnames(part)); dup <- setdiff(dup, ki)
        ii <- ii[, setdiff(colnames(ii), dup), drop = FALSE]
        part <- merge(part, ii, by.x = ka, by.y = ki, all.x = TRUE, sort = FALSE)
        srcs <- rbind(srcs, data.frame(obj = "hn21_iaq", col = colnames(ii), role = "iaq"))
      }
    }
  }

  out <- file.path(outdir, sprintf("knhanes_%d.csv", y))
  write.csv(part, out, row.names = FALSE)
  srcs$wave <- y
  codebook[[length(codebook) + 1]] <- srcs
  report[[length(report) + 1]] <- data.frame(
    wave = y, nrow = nrow(part), ncol = ncol(part),
    has_BS3 = "BS3_1" %in% colnames(part),
    has_edu = "edu" %in% colnames(part),
    has_incm5 = "incm5" %in% colnames(part),
    has_BD1_11 = "BD1_11" %in% colnames(part),
    has_PM25 = "PM25" %in% colnames(part),
    has_E_DM = "E_DM" %in% colnames(part) || any(c("E_DM_r", "E_DM_l") %in% colnames(part)),
    has_E_DRP = any(c("E_DRP_R", "E_DRP_L") %in% colnames(part)),
    has_E_AMD = any(c("E_AMD", "E_AMD_ELY_R", "E_AMD_r") %in% colnames(part)),
    has_E_GR = "E_GR" %in% colnames(part),
    has_E_VS_DS = "E_VS_DS" %in% colnames(part),
    has_HE_vitD = "HE_vitD" %in% colnames(part),
    has_E_Q_SUN = "E_Q_SUN" %in% colnames(part),
    stringsAsFactors = FALSE)
  cat(sprintf("  wave %d -> %s  (%d x %d)\n", y, basename(out), nrow(part), ncol(part)))
}

rep <- do.call(rbind, report)
cb <- do.call(rbind, codebook)
write.csv(rep, file.path(outdir, "build_report.csv"), row.names = FALSE)
write.csv(cb, file.path(outdir, "codebook_used.csv"), row.names = FALSE)

cat("\n=== build report ===\n")
print(rep, row.names = FALSE)
cat("\ncodebook rows:", nrow(cb), " -> ", file.path(outdir, "codebook_used.csv"), "\n")
