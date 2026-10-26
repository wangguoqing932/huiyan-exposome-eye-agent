#!/usr/bin/env Rscript
# Append colnames for the _ap (air pollution), _24rc (24h recall) and _oe objects.
base <- Sys.getenv("KN_DIR", unset = ".")
outdir <- Sys.getenv("TMPDIR_AUDIT", unset = tempdir())
targets <- list(
  c("kn_2007_2010.Rdata","hn08_ap"), c("kn_2007_2010.Rdata","hn09_ap"),
  c("kn_2007_2010.Rdata","hn10_ap"), c("kn_2007_2010.Rdata","hn08_24rc"),
  c("kn_2007_2010.Rdata","hn08_oe"),
  c("kn_2011_2015.Rdata","hn11_ap"), c("kn_2011_2015.Rdata","hn12_ap"),
  c("kn_2011_2015.Rdata","hn12_24rc"), c("kn_2011_2015.Rdata","hn12_ffq"),
  c("kn_2016_2020.Rdata","hn17_ap"), c("kn_2016_2020.Rdata","hn18_ap"),
  c("kn_2016_2020.Rdata","hn19_ap"), c("kn_2016_2020.Rdata","hn20_ap"),
  c("kn_2016_2020.Rdata","hn17_24rc"),
  c("kn_2021_2024.Rdata","hn21_ap"), c("kn_2021_2024.Rdata","hn21_iaq"),
  c("kn_2021_2024.Rdata","hn21_24rc")
)
rows <- list(); loaded <- list()
for (t in targets) {
  f <- t[1]; o <- t[2]
  if (is.null(loaded[[f]])) { e <- new.env(); load(file.path(base, f), envir = e); loaded[[f]] <- e }
  e <- loaded[[f]]
  if (!exists(o, envir = e)) { cat("missing:", o, "\n"); next }
  cn <- colnames(get(o, envir = e))
  rows[[length(rows) + 1]] <- data.frame(obj = o, col = cn, stringsAsFactors = FALSE)
}
df <- do.call(rbind, rows)
out <- file.path(outdir, "kn_colnames_extra.csv")
write.csv(df, out, row.names = FALSE)
cat("extra cols written:", nrow(df), " objects:", length(unique(df$obj)), "\n")
print(table(df$obj))
