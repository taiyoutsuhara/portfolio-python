# .fstを.csvに変換する。 #

# ライブラリ #
# 初回時のみ、必要なライブラリをインストールする。
installed_packages_list = library()
installed_package_names = installed_packages_list$results[, 1] # 1列目にPackage名がある。
required_packages = c("data.table", "fst")
packages_not_installed = required_packages[required_packages %in% installed_package_names == F]
identical_character_zero = !identical(packages_not_installed, character(0))
if(identical_character_zero){
  install.packages(packages_not_installed, dependencies = T)
}

# 読込み
library(data.table)
library(fst)


# fst, csvファイルのパス設定 #
# 予め、data_format_fstフォルダとdata_formatフォルダを作成しておく。
full_path_of_fst = paste0(getwd(), "/1.propensity_score_analysis/", "data_format_fst/")
full_path_of_csv = paste0(getwd(), "/1.propensity_score_analysis/", "data_format/")

# バッチ処理用フルパス
batch_for_fst = list.files(full_path_of_fst, full.names = T)
batch_for_csv = gsub(".fst", ".csv", gsub("data_format_fst", "data_format", batch_for_fst))


# バッチ処理 #
range_of_fst = c(1:length(batch_for_fst))
for(ba in range_of_fst){
  format_fst = read.fst(batch_for_fst[ba])
  fwrite(format_fst, batch_for_csv[ba], sep = ",")
}