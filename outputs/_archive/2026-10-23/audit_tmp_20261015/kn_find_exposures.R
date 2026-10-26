#!/usr/bin/env Rscript
# Locate the REAL alcohol / vitamin-D / dietary exposure variables by searching
# official Chinese labels in the KNHANES dictionary.
base <- Sys.getenv("KN_DIR", unset = ".")
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
files <- c("kn_2007_2010.Rdata", "kn_2016_2020.Rdata")

rows <- list()
for (f in files) {
  e <- new.env(); load(file.path(base, f), envir = e)
  if (!exists("dictionary", envir = e)) next
  d <- get("dictionary", envir = e)
  names(d) <- c("id","kr","cn","note","from","year","rdata")
  d$src_rdata <- f
  rows[[length(rows) + 1]] <- d
  rm(e); gc(verbose = FALSE)
}
dict <- do.call(rbind, rows)
dict <- dict[!duplicated(dict[, c("id","from")]), ]
write.csv(dict, file.path(outdir, "kn_dictionary_full.csv"), row.names = FALSE)

show_hits <- function(title, pattern, maxn = 25) {
  cat("\n=== ", title, " ===\n", sep = "")
  hit <- dict[grepl(pattern, dict$cn), ]
  hit <- hit[!duplicated(paste(hit$id, hit$from)), ]
  hit <- hit[order(hit$id), ]
  if (nrow(hit) == 0) { cat("  (no label match)\n"); return(invisible()) }
  print(head(hit[, c("id","cn","from")], maxn), row.names = FALSE)
}

show_hits("ALCOHOL by label (饮酒|喝酒|饮酒量|饮酒频率|酗酒)", "饮酒|喝酒|酗酒|酒精")
show_hits("VITAMIN D by label (维生素D|25-羟|25羟)", "维生素D|25-羟|25羟|维生素 D")
show_hits("DIET / antioxidant (维生素C|维生素E|胡萝卜素|叶黄素|玉米黄质|抗氧化)", "维生素C|维生素E|胡萝卜素|叶黄素|玉米黄质|抗氧化")
show_hits("AIR POLLUTION (颗粒物|PM|空气|大气|细颗粒)", "颗粒物|PM2|PM10|空气污染|大气污染|细颗粒")
show_hits("UV / sunlight (紫外线|日照|阳光)", "紫外线|日照|阳光")

cat("\n=== variables in BD* / alcohol-ish modules present in hn08_all / hn17_all ===\n")
probe <- function(f, obj) {
  e <- new.env(); load(file.path(base, f), envir = e)
  x <- get(obj, envir = e); cn <- colnames(x)
  pat <- "^(BD|BA1|LS_|N_|Nf_|HS_)"
  sel <- grep(pat, cn, value = TRUE)
  cat(sprintf("\n-- %s : %d matching cols\n", obj, length(sel)))
  if (length(sel)) {
    lab <- dict[dict$from == obj & dict$id %in% sel, c("id","cn")]
    lab <- lab[!duplicated(lab$id), ]
    m <- merge(data.frame(id = sel), lab, by = "id", all.x = TRUE)
    print(head(m, 60), row.names = FALSE)
  }
  rm(e); gc(verbose = FALSE)
}
probe("kn_2007_2010.Rdata", "hn08_all")
probe("kn_2016_2020.Rdata", "hn17_all")
