load('E:/BaiduNetdiskDownload/所有数据库/11. KNHANES 韩国国民健康与营养调查/Rdata/KNHANES 2007-2010.Rdata')
names(dictionary) <- c('id','kr','cn','note','from','year','rdata')
a <- as.data.frame(hn08_all)
fr <- read.csv(file.path(Sys.getenv('TMPDIR_AUDIT'), 'k2008.csv'),
               stringsAsFactors=FALSE, check.names=FALSE)
cat('frame dim:', dim(fr), ' hn08_all dim:', dim(a), '\n')
cat('frame cols not in hn08_all:', paste(setdiff(colnames(fr), colnames(a)), collapse=', '), '\n\n')

cmp <- function(v) {
  if (!(v %in% colnames(fr)) || !(v %in% colnames(a))) { cat(v, ': missing on one side\n'); return(invisible()) }
  f <- fr[[v]]; g <- a[[v]]
  n <- min(length(f), length(g))
  cat(sprintf('%-12s frame: %s\n', v, paste(names(table(f, useNA="ifany")), table(f, useNA="ifany"), sep='=', collapse=' ')))
  cat(sprintf('%-12s rdata: %s\n', '', paste(names(table(g, useNA="ifany")), table(g, useNA="ifany"), sep='=', collapse=' ')))
}
for (v in c('BS1_1','BA2_2_1','BA2_22','DH2_lt','DH3_lt','HE_UAScr','HE_Uacid','HE_BMI','HE_HbA1c','HE_glu','sex','age','wt_itvex')) cmp(v)

cat('\n--- dictionary rows for HE_UAScr / HE_Uacid ---\n')
for (v in c('HE_UAScr','HE_Uacid','BS1_1','BA2_2_1')) {
  idx <- which(dictionary$id == v)
  for (i in idx) cat(sprintf('%s | from=%s | kr=%s\n', v, dictionary$from[i], dictionary$kr[i]))
}
cat('\n--- is uric acid anywhere in hn08_all? ---\n')
hit <- grep('UAScr|Uacid|요산', colnames(a), value=TRUE, ignore.case=TRUE)
cat('colname hits:', paste(hit, collapse=', '), '\n')
idx <- which(grepl('요산', dictionary$kr))
cat('dict kr hits:', paste(unique(dictionary$id[idx]), collapse=', '), '| from:', paste(unique(dictionary$from[idx]), collapse=', '), '\n')
