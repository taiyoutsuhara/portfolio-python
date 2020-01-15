#!/usr/bin/env python
# ライブラリ読込み #
import glob
import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from collections import Counter
from numpy.random import *


# ディレクトリ設定 #
current_directory = os.getcwd()
# Pythonコンソールから実行したいとき、次の2行をアンコメントする。
# directory_of_psa = '\\1.propensity_score_analysis\\'
# main_directory = current_directory + directory_of_psa
# Runメニューから実行したいとき、次の1行をアンコメントする。
main_directory = current_directory
os.chdir(main_directory)  # '/1.propensity_score_analysis/'を主WDにする。
changed_main_directory = os.getcwd()
sys.path.append(changed_main_directory + "\\")

# 必要なサブディレクトリを作成 #
list_of_sub_directories = ["data_format", "gps", "ipw", "ipw-glm"]
required_sub_dirs = ('$|'.join(list_of_sub_directories)) + '$'
files_in_main_directory = os.listdir(changed_main_directory)

# サブディレクトリを取り出す。
sub_dirs_in_main_directory = []
for x in range(0, files_in_main_directory.__len__()):
    if os.path.isdir(files_in_main_directory[x]):
        sub_dirs_in_main_directory.append(files_in_main_directory[x])

# 必要なサブディレクトリが皆無のとき、list_of_sub_directoriesで定義したものを作成する。
new_sub_dir = []
if sub_dirs_in_main_directory.__len__() == 0:
    for f in range(0, list_of_sub_directories.__len__()):
        new_sub_dir.append(changed_main_directory + '\\' + list_of_sub_directories[f] + '\\')
        os.mkdir(new_sub_dir[f])


# 一般化傾向スコア（GPS）の推定 #
# 乱数種の指定
seed(12345)

# CSVファイルのフルパスを取得
full_path_of_data_format = changed_main_directory + '\\data_format\\'
files_in_data_format = glob.glob(os.path.join(full_path_of_data_format, '*'))

# gpsに出力するファイル名を用意する。
files_in_gps = []
files_in_fallback = []
for ba in range(0, files_in_data_format.__len__()):
    files_in_gps.append(files_in_data_format[ba].replace('\\data_format\\', '\\gps\\gps_'))
    files_in_fallback.append(files_in_data_format[ba].replace('\\data_format\\', '\\gps\\fallback_'))

# 大元のデータを取得
data_raw = pd.read_csv(files_in_data_format[0])
Service_Type_sorted = sorted(data_raw['Q4.ServiceType'].unique())

# バッチ処理の実行
range_of_gps = range(20, 26)  # GPSの列範囲を指定
for ba in range(0, files_in_data_format.__len__()):
    data_for_gps = pd.read_csv(files_in_data_format[ba])
    obj_var_of_gps = data_for_gps['Q4.ServiceType']  # 目的変数はサービスの種類
    # 説明変数はダミーデータ変換済属性であるが、以下の処理をする必要がある。
    # CustomerID, Q4, Q5、ならびに区別の付くカテゴリを除外する。
    column_names_exceptions = 'CustomerID|Q4.ServiceType|Q5.CustomerDollar|F1.Senior|F2.South|F3.Others'
    exceptions_do_not_contain = np.logical_not(data_for_gps.columns.str.contains(column_names_exceptions))
    exp_vars_of_gps = data_for_gps.iloc[:, exceptions_do_not_contain]
    # 全部0, 1の説明変数を除外する。但し、後者はダミー変数のみである。
    all_zero_or_not = []
    trimmed_exp_vars_of_gps = []
    column_number_of_continuous_values = exp_vars_of_gps.columns.get_loc('Q2.FormerCustomerDollar')
    for ec in range(0, exp_vars_of_gps.columns.__len__()):
        all_zero_or_not.append(sum(exp_vars_of_gps.iloc[:, ec]))
        continuous_values_or_not = (ec == column_number_of_continuous_values)
        # 連続データの場合、全部0ではないかどうかだけで判断する。
        if continuous_values_or_not:
            condition_of_not_all_zero_and_length = (all_zero_or_not[ec] != 0)
        else:
            condition_of_not_all_zero_and_length = (all_zero_or_not[ec] != 0 &
                                                    all_zero_or_not[ec] != data_for_gps.shape[0])
        # 最終的に採用する説明変数
        if condition_of_not_all_zero_and_length:
            trimmed_exp_vars_of_gps.append(exp_vars_of_gps.iloc[:, ec])
    # 多項ロジスティック回帰モデルでGPSを推定し、data_for_gpsにGPSを結合する。
    df_trimmed_exp_vars_of_gps = pd.DataFrame(trimmed_exp_vars_of_gps)
    vglm_for_gps = sm.MNLogit(obj_var_of_gps, df_trimmed_exp_vars_of_gps.T)
    # Singular Matrixエラーが出ることがあるので、例外処理を挟んでおく。
    try:
        result_gps = vglm_for_gps.fit()
    except np.linalg.LinAlgError as error:
        print('Catch Singular_matrix:', error)
    else:
        gps = result_gps.predict(df_trimmed_exp_vars_of_gps.T)
        gps_new = gps.rename(columns={0: 'GPS_A', 1: 'GPS_B', 2: 'GPS_C', 3: 'GPS_D', 4: 'GPS_E', 5: 'GPS_F'})
        data_for_ipw = pd.concat([data_for_gps, gps_new], axis=1)  # 列方向に結合するのでaxis=1
        # コモンサポートを満足するデータのみ採択する。
        th_of_gps_min = max(gps_new.apply(min))
        th_of_gps_max = min(gps_new.apply(max))
        TF_regarding_to_gps_csp = (data_for_ipw.iloc[:, range_of_gps] >= th_of_gps_min) &\
                                  (data_for_ipw.iloc[:, range_of_gps] <= th_of_gps_max)
        TF_to_extract_satisfied_csp = TF_regarding_to_gps_csp.apply(sum, axis=1)
        data_satisfied_csp = data_for_ipw[TF_to_extract_satisfied_csp == 6]
        # 逆確率重み（IPW）計算用生データの作成
        # 1.コモンサポート満足済データ数が、大元の生データ数の閾値以上か。
        row_count_of_csp = data_satisfied_csp.shape[0]  # 行数
        row_count_of_raw = data_raw.shape[0]  # 行数
        value_of_th_for_csp = 0.001
        TF_regarding_to_row_count_of_csp = (row_count_of_csp >= row_count_of_raw * value_of_th_for_csp)
        # 2.サービスの種類F（サービスを受けていない。）が全サービスの10%以上を占めているか。
        # IPWのインフレーションを回避するため、本制約を適用する。
        value_of_th_for_inflation = 0.1
        length_of_non_use = sum(data_satisfied_csp['Q4.ServiceType'] == 'F')
        length_of_all_service = data_satisfied_csp['Q4.ServiceType'].__len__()
        TF_ipw_not_inflation = (length_of_non_use >= length_of_all_service * value_of_th_for_inflation)
        # 3.サービスを利用していない（F）を除き、全種類存在するか。
        service_type_counter = Counter(data_satisfied_csp['Q4.ServiceType'])
        service_type_count = list(service_type_counter.values())
        TF_service_type_is_absolute = (0 not in service_type_count)
        # 4.条件1を満足しないとき、コモンサポート満足済データ数が0ではない。
        TF_data_satisfied_csp_size_is_not_zero = (row_count_of_csp > 0)
        # 条件1～4を満足するかどうかでデータを書き出すか、書き出さないかを分岐する。
        if TF_regarding_to_row_count_of_csp &\
                TF_ipw_not_inflation &\
                TF_service_type_is_absolute &\
                TF_data_satisfied_csp_size_is_not_zero:
            data_satisfied_csp.to_csv(files_in_gps[ba], index=False)
        elif TF_ipw_not_inflation &\
                TF_ipw_not_inflation &\
                TF_service_type_is_absolute &\
                TF_data_satisfied_csp_size_is_not_zero:
            data_satisfied_csp.to_csv(files_in_fallback[ba], index=False)


# IPWの計算 #
# CSVファイルのフルパスを取得
full_path_of_gps = changed_main_directory + '\\gps\\'
files_in_gps_written = glob.glob(os.path.join(full_path_of_gps, 'gps_*'))

# ipwに出力するファイル名を用意し、バッチ処理を実行する。
files_in_ipw = []
for ba in range(0, files_in_gps_written.__len__()):
    files_in_ipw.append(files_in_gps_written[ba].replace('\\gps\\gps_', '\\ipw\\ipw_'))

# バッチ処理の実行
for ba in range(0, files_in_gps_written.__len__()):
    data_for_ipw = pd.read_csv(files_in_gps_written[ba])
    gps_in_this_data = data_for_ipw.iloc[:, range_of_gps]
    service_type_in_this_data = data_for_ipw['Q4.ServiceType']
    IPW = pd.DataFrame({'IPW': [0] * data_for_ipw.shape[0]})
    # IPWを計算する。
    for st in range(0, Service_Type_sorted.__len__()):
        gps_split = gps_in_this_data.iloc[:, st][service_type_in_this_data == Service_Type_sorted[st]]
        IPW.iloc[:, 0][service_type_in_this_data == Service_Type_sorted[st]] =\
            (1 / gps_split) * (data_for_ipw.shape[0] / gps_split.__len__())
    # IPWを結合し、書き出す。
    data_IPW = pd.concat([data_for_ipw, IPW], axis=1)
    data_IPW.to_csv(files_in_ipw[ba], index=False)


# 縮退時、一般化線形モデルによるサービス導入効果の推定 #
# CSVファイルのフルパスを取得
files_in_fb_written = glob.glob(os.path.join(full_path_of_gps, 'fallback_*'))

# ipw-glmに出力するファイル名を用意する。
if not files_in_fb_written.__len__() == 0:
    files_deviance_fb = []
    files_coes_fb = []
    files_misc_fb = []
    for ba in range(0, files_in_fb_written.__len__()):
        files_deviance_fb.append(files_in_fb_written[ba].replace('\\gps\\fallback_', '\\ipw-glm\\glm_'))
        files_coes_fb.append(files_in_fb_written[ba].replace('\\gps\\fallback_', '\\ipw-glm\\fallback_coes_'))
        files_misc_fb.append(files_in_fb_written[ba].replace('\\gps\\fallback_', '\\ipw-glm\\fallback_misc_'))

# バッチ処理の実行
if not files_in_fb_written.__len__() == 0:
    for ba in range(0, files_in_fb_written.__len__()):
        data_for_glm = pd.read_csv(files_in_fb_written[ba])
        obj_var_of_glm = data_for_glm['Q5.CustomerDollar']
        exp_vars_of_glm = data_for_glm['Q4.ServiceType']
        exp_vars_of_glm_dummy = pd.get_dummies(exp_vars_of_glm)
        # 目的変数に利用額、説明変数にサービスの種類を代入したGLMにより、
        # サービス導入効果を推定する。なお、切片は推定しない。
        glm_for_fb = sm.GLM(obj_var_of_glm, exp_vars_of_glm_dummy, family=sm.families.Gaussian())
        result_glm = glm_for_fb.fit()
        # 逸脱残差を書き出す。
        deviance_resid_fb = pd.DataFrame({'deviance.resid': [0] * data_for_glm.shape[0]})
        deviance_resid_fb.iloc[:, 0] = result_glm.resid_deviance
        data_deviance_fb = pd.concat([data_for_glm, deviance_resid_fb], axis=1)
        data_deviance_fb.to_csv(files_deviance_fb[ba], index=False)
        # 分析結果を取り出し、書き出す。
        coes_fb = pd.DataFrame({'Estimate': np.array(result_glm.params),
                                'Std. Error': np.array(result_glm.bse),
                                't value': np.array(result_glm.tvalues),
                                'Pr(>|t|)': np.array(result_glm.pvalues),
                                'diff.data_A': np.array(result_glm.params - result_glm.params[0]),
                                'diff.data_B': np.array(result_glm.params - result_glm.params[1]),
                                'diff.data_C': np.array(result_glm.params - result_glm.params[2]),
                                'diff.data_D': np.array(result_glm.params - result_glm.params[3]),
                                'diff.data_E': np.array(result_glm.params - result_glm.params[4]),
                                'diff.data_F': np.array(result_glm.params - result_glm.params[5]),
                                'cov.scaled.dataA': np.array(result_glm.cov_params().iloc[:, 0]),
                                'cov.scaled.dataB': np.array(result_glm.cov_params().iloc[:, 1]),
                                'cov.scaled.dataC': np.array(result_glm.cov_params().iloc[:, 2]),
                                'cov.scaled.dataD': np.array(result_glm.cov_params().iloc[:, 3]),
                                'cov.scaled.dataE': np.array(result_glm.cov_params().iloc[:, 4]),
                                'cov.scaled.dataF': np.array(result_glm.cov_params().iloc[:, 5]),
                                'cov.unscaled.dataA': np.array(result_glm.normalized_cov_params.iloc[:, 0]),
                                'cov.unscaled.dataB': np.array(result_glm.normalized_cov_params.iloc[:, 1]),
                                'cov.unscaled.dataC': np.array(result_glm.normalized_cov_params.iloc[:, 2]),
                                'cov.unscaled.dataD': np.array(result_glm.normalized_cov_params.iloc[:, 3]),
                                'cov.unscaled.dataE': np.array(result_glm.normalized_cov_params.iloc[:, 4]),
                                'cov.unscaled.dataF': np.array(result_glm.normalized_cov_params.iloc[:, 5])
                                }, index=['dataA', 'dataB', 'dataC', 'dataD', 'dataE', 'dataF'])
        misc_fb = pd.DataFrame({'Misc': [result_glm.scale,
                                         result_glm.null_deviance,
                                         result_glm.nobs,
                                         result_glm.deviance,
                                         result_glm.df_resid,
                                         result_glm.aic,
                                         result_glm._n_trials]
                                }, index=['dispersion', 'null.deviance', 'df.null', 'deviance',
                                          'df.residual', 'aic', 'iter'])
        coes_fb.to_csv(files_coes_fb[ba], index=True)
        misc_fb.to_csv(files_misc_fb[ba], index=True)


# IPW推定量の計算 #
# CSVファイルのフルパスを取得
full_path_of_ipw = changed_main_directory + '\\ipw\\'
files_in_ipw_written = glob.glob(os.path.join(full_path_of_ipw, 'ipw_*'))

# ipw-glmに出力するファイル名を用意する。
files_deviance = []
files_coes = []
files_misc = []
for ba in range(0, files_in_ipw_written.__len__()):
    files_deviance.append(files_in_ipw_written[ba].replace('\\ipw\\ipw_', '\\ipw-glm\\ipw-glm_'))
    files_coes.append(files_in_ipw_written[ba].replace('\\ipw\\ipw_', '\\ipw-glm\\coes_'))
    files_misc.append(files_in_ipw_written[ba].replace('\\ipw\\ipw_', '\\ipw-glm\\misc_'))

# バッチ処理の実行
for ba in range(0, files_in_ipw_written.__len__()):
    data_for_ipwe = pd.read_csv(files_in_ipw_written[ba])
    obj_var_of_ipwe = data_for_ipwe['Q5.CustomerDollar']
    exp_vars_of_ipwe = data_for_ipwe['Q4.ServiceType']
    exp_vars_of_ipwe_dummy = pd.get_dummies(exp_vars_of_ipwe)
    weight_for_ipwe = data_for_ipwe['IPW']
    # 目的変数に利用額、説明変数にサービスの種類を代入したGLMにより、IPWEを計算する。
    # なお、重みにIPWを付与し、切片は推定しない。
    glm_for_ipwe = sm.GLM(obj_var_of_ipwe, exp_vars_of_ipwe_dummy, family=sm.families.Gaussian(),
                          var_weights=weight_for_ipwe)
    result_ipwe = glm_for_ipwe.fit()
    # 逸脱残差を書き出す。
    deviance_resid = pd.DataFrame({'deviance.resid': [0] * data_for_ipwe.shape[0]})
    deviance_resid.iloc[:, 0] = result_ipwe.resid_deviance
    data_deviance = pd.concat([data_for_ipwe, deviance_resid], axis=1)
    data_deviance.to_csv(files_deviance[ba], index=False)
    # 分析結果を取り出し、書き出す。
    coes = pd.DataFrame({'Estimate': np.array(result_ipwe.params),
                         'Std. Error': np.array(result_ipwe.bse),
                         't value': np.array(result_ipwe.tvalues),
                         'Pr(>|t|)': np.array(result_ipwe.pvalues),
                         'diff.data_A': np.array(result_ipwe.params - result_ipwe.params[0]),
                         'diff.data_B': np.array(result_ipwe.params - result_ipwe.params[1]),
                         'diff.data_C': np.array(result_ipwe.params - result_ipwe.params[2]),
                         'diff.data_D': np.array(result_ipwe.params - result_ipwe.params[3]),
                         'diff.data_E': np.array(result_ipwe.params - result_ipwe.params[4]),
                         'diff.data_F': np.array(result_ipwe.params - result_ipwe.params[5]),
                         'cov.scaled.dataA': np.array(result_ipwe.cov_params().iloc[:, 0]),
                         'cov.scaled.dataB': np.array(result_ipwe.cov_params().iloc[:, 1]),
                         'cov.scaled.dataC': np.array(result_ipwe.cov_params().iloc[:, 2]),
                         'cov.scaled.dataD': np.array(result_ipwe.cov_params().iloc[:, 3]),
                         'cov.scaled.dataE': np.array(result_ipwe.cov_params().iloc[:, 4]),
                         'cov.scaled.dataF': np.array(result_ipwe.cov_params().iloc[:, 5]),
                         'cov.unscaled.dataA': np.array(result_ipwe.normalized_cov_params.iloc[:, 0]),
                         'cov.unscaled.dataB': np.array(result_ipwe.normalized_cov_params.iloc[:, 1]),
                         'cov.unscaled.dataC': np.array(result_ipwe.normalized_cov_params.iloc[:, 2]),
                         'cov.unscaled.dataD': np.array(result_ipwe.normalized_cov_params.iloc[:, 3]),
                         'cov.unscaled.dataE': np.array(result_ipwe.normalized_cov_params.iloc[:, 4]),
                         'cov.unscaled.dataF': np.array(result_ipwe.normalized_cov_params.iloc[:, 5])
                         }, index=['dataA', 'dataB', 'dataC', 'dataD', 'dataE', 'dataF'])
    misc = pd.DataFrame({'Misc': [result_ipwe.scale,
                                  result_ipwe.null_deviance,
                                  result_ipwe.nobs,
                                  result_ipwe.deviance,
                                  result_ipwe.df_resid,
                                  result_ipwe.aic,
                                  result_ipwe._n_trials]
                         }, index=['dispersion', 'null.deviance', 'df.null', 'deviance', 'df.residual', 'aic', 'iter'])
    coes.to_csv(files_coes[ba], index=True)
    misc.to_csv(files_misc[ba], index=True)
