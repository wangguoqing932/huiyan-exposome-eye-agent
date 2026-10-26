#!/usr/bin/env Rscript
# Dump column names of the KNHANES objects of interest (ASCII-only script).
base <- Sys.getenv("KN_DIR", unset = ".")
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
targets <- list(
  c("kn_2007_2010.Rdata", "hn08_all"), c("kn_2007_2010.Rdata", "hn08_eye"),
  c("kn_2007_2010.Rdata", "hn09_all"), c("kn_2007_2010.Rdata", "hn09_eye"),
  c("kn_2007_2010.Rdata", "hn10_all"), c("kn_2007_2010.Rdata", "hn10_eye"),
  c("kn_2011_2015.Rdata", "hn11_all"), c("kn_2011_2015.Rdata", "hn11_eye"),
  c("kn_2011_2015.Rdata", "hn12_all"), c("kn_2011_2015.Rdata", "hn12_eye"),
  c("kn_2016_2020.Rdata", "hn16_all"), c("kn_2016_2020.Rdata", "hn17_all"),
  c("kn_2016_2020.Rdata", "hn17_eye"), c("kn_2016_2020.Rdata", "hn18_all"),
  c("kn_2016_2020.Rdata", "hn19_all"), c("kn_2016_2020.Rdata", "hn20_all"),
  c("kn_2021_2024.Rdata", "hn21_all"), c("kn_2021_2024.Rdata", "hn21_eye"),
  c("kn_2021_2024.Rdata", "hn21_iaq"), c("kn_2011_2015.Rdata", "hn12_ffq")
)
rows <- list()
loaded <- list()
for (t in targets) {
  f <- t[1]; o <- t[2]
  if (is.null(loaded[[f]])) { e <- new.env(); load(file.path(base, f), envir = e); loaded[[f]] <- e }
  e <- loaded[[f]]
  if (!exists(o, envir = e)) { cat("missing object:", o, "\n"); next }
  cn <- colnames(get(o, envir = e))
  rows[[length(rows) + 1]] <- data.frame(obj = o, col = cn, stringsAsFactors = FALSE)
}
df <- do.call(rbind, rows)
write.csv(df, file.path(outdir, "kn_colnames.csv"), row.names = FALSE)
cat("cols written:", nrow(df), " objects:", length(unique(df$obj)), "\n")
