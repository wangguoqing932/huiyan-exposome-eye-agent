load('E:/BaiduNetdiskDownload/所有数据库/11. KNHANES 韩国国民健康与营养调查/Rdata/KNHANES 2007-2010.Rdata')
d <- dictionary
names(d) <- c('id','kr','cn','note','from','year','rdata')
vars <- c('BS1_1','BA2_2_1','BA2_22','DH2_lt','DH3_lt','E_DRP_R','E_DRP_L',
          'E_AMD_ELY_R','E_VS_DS','HE_UAScr','HE_Uacid','wt_itvex','HE_BMI','HE_HbA1c','HE_glu')
for (v in vars) {
  idx <- which(d$id == v)
  if (length(idx)) {
    for (i in head(idx, 6)) {
      cat(sprintf('%s\t%s\t%s\t%s\n', v, d$kr[i], d$cn[i], d$from[i]))
    }
  } else cat(v, '\tNOT IN DICTIONARY\n', sep='')
}
cat('--- hn08_eye colnames ---\n')
cat(paste(head(colnames(hn08_eye), 40), collapse=' | '), '\n')
cat('--- presence check ---\n')
for (v in vars) cat(v, ':', v %in% colnames(hn08_eye), '\n')
