load('E:/BaiduNetdiskDownload/所有数据库/11. KNHANES 韩国国民健康与营养调查/Rdata/KNHANES 2007-2010.Rdata')
names(dictionary) <- c('id','kr','cn','note','from','year','rdata')
a <- as.data.frame(hn08_all)
sink(file.path(Sys.getenv('TMPDIR_AUDIT'), 'smoke.txt'), split=TRUE)
cat('=== all BS* columns in hn08_all ===\n')
bs <- grep('^BS', colnames(a), value=TRUE)
for (v in bs) {
  x <- a[[v]]
  tb <- table(x, useNA='no')
  if (length(tb) <= 6 && nrow(a) - sum(tb) < nrow(a)*0.9) {
    lab <- dictionary$kr[dictionary$id == v & dictionary$from == 'hn08_all']
    lab <- if (length(lab)) lab[1] else ''
    cat(sprintf('%-8s | %s | %s\n', v, paste(names(tb), as.integer(tb), sep='=', collapse=' '), lab))
  }
}
cat('\n=== alcohol BA* ===\n')
for (v in grep('^BA', colnames(a), value=TRUE)) {
  x <- a[[v]]; tb <- table(x, useNA='no')
  if (length(tb) <= 6) {
    lab <- dictionary$kr[dictionary$id == v & dictionary$from == 'hn08_all']
    lab <- if (length(lab)) lab[1] else ''
    cat(sprintf('%-8s | %s | %s\n', v, paste(names(tb), as.integer(tb), sep='=', collapse=' '), lab))
  }
}
cat('\n=== BS1_1 x sex, BS1_1 x 5y age band ===\n')
print(table(a$BS1_1, a$sex, dnn=c('BS1_1','sex')))
cat('\n=== E_VS_DS coding ===\n')
print(table(hn08_eye$E_VS_DS, useNA='ifany'))
cat('\n=== E_DRP_R coding ===\n')
print(table(hn08_eye$E_DRP_R, useNA='ifany'))
sink()
