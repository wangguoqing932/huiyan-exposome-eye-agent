load('E:/BaiduNetdiskDownload/所有数据库/11. KNHANES 韩国国民健康与营养调查/Rdata/KNHANES 2007-2010.Rdata')
names(dictionary) <- c('id','kr','cn','note','from','year','rdata')
a <- as.data.frame(hn08_all)
fr <- read.csv(file.path(Sys.getenv('TMPDIR_AUDIT'), 'k2008.csv'),
               stringsAsFactors=FALSE, check.names=FALSE)
sink(file.path(Sys.getenv('TMPDIR_AUDIT'), 'out.txt'), split=TRUE)
cat('frame dim:', dim(fr), ' hn08_all dim:', dim(a), '\n')
cat('frame cols NOT in hn08_all:\n  ', paste(setdiff(colnames(fr), colnames(a)), collapse=', '), '\n')
cat('hn08_all cols NOT in frame (first 30):\n  ', paste(head(setdiff(colnames(a), colnames(fr)),30), collapse=', '), '\n\n')

cat('=== ID alignment check ===\n')
cat('frame ID head:', paste(head(fr$ID,5), collapse=','), '\n')
cat('rdata ID head:', paste(head(a$ID,5), collapse=','), '\n')
cat('identical order:', identical(as.character(fr$ID), as.character(a$ID)), '\n\n')

kv <- function(v) {
  if (!(v %in% colnames(fr))) { cat(sprintf('%-14s frame: COLUMN ABSENT\n', v)); return(invisible()) }
  f <- fr[[v]]
  cat(sprintf('%-14s frame: %s\n', v, paste(names(table(f, useNA="ifany")), table(f, useNA="ifany"), sep='=', collapse=' ')))
  if (v %in% colnames(a)) {
    g <- a[[v]]
    cat(sprintf('%-14s rdata: %s\n', '', paste(names(table(g, useNA="ifany")), table(g, useNA="ifany"), sep='=', collapse=' ')))
    cat(sprintf('%-14s identical: %s\n', '', identical(as.vector(f), as.vector(g))))
  } else cat(sprintf('%-14s rdata: ABSENT\n',''))
}
for (v in c('BS1_1','BA2_2_1','BA2_22','DH2_lt','DH3_lt','HE_UAScr','HE_UAScr_AAS','HE_Uacid','HE_BMI','HE_HbA1c','HE_glu','sex','edu','incm','HE_HDL_st2')) kv(v)
sink()
