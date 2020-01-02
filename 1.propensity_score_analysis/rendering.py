#!/usr/bin/env python
# ライブラリ読込み #
import dash
import dash_table
import glob
import os
import re
import sys
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output


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

# Dashに必要なデータを読み込む。 #
# サービスの種類と説明
full_path_of_attachments = changed_main_directory + '\\attachments\\'
file_service_types = glob.glob(os.path.join(full_path_of_attachments, 'Code_table_of_Service_Types.csv'))
description_of_service_types = pd.read_csv(file_service_types[0])
code_of_service_types_ex_non_use = np.array(description_of_service_types['Code']
                                            [0:description_of_service_types.__len__() - 1])

# グラフ描画用データ
full_path_of_ipw_glm = changed_main_directory + '\\ipw-glm\\'
files_coes_written = glob.glob(os.path.join(full_path_of_ipw_glm, '*coes_*'))
data_for_dash = [[0] * description_of_service_types.__len__()]  # 比較対象を選択しないとき用の0埋めデータ
for cba in range(0, files_coes_written.__len__()):
    coes = pd.read_csv(files_coes_written[cba])
    data_for_dash.append(coes['diff.data_F'])  # Non-useに該当する列名を代入する。

# 選択可能パターン表の作成
selectable_patterns = os.listdir(full_path_of_ipw_glm)
# '_'で分割する。
selection_split = []
for ss in range(0, selectable_patterns.__len__()):
    selection_split.append(selectable_patterns[ss].split('_'))
# 分割対象属性毎に列を作る。今回は最大3属性で分割しているので、3列となる。
select_F1 = []
select_F2 = []
select_F3 = []
select_fallback = []
last_number_at_select = int(selectable_patterns.__len__() / 3)
for ss in range(0, last_number_at_select):  # 抽出したい識別子を含むカテゴリを取り出す。
    select_F1.append(list(filter(lambda x: 'F1' in x, selection_split[ss])))
    select_F2.append(list(filter(lambda x: 'F2' in x, selection_split[ss])))
    select_F3.append(list(filter(lambda x: 'F3' in x, selection_split[ss])))
    select_fallback.append(list(filter(lambda x: 'fallback' in x, selection_split[ss])))
# 不要な文字をカットする。
select_F1_trimmed = list(map(lambda x: re.sub(r'^$', 'Not selected', re.sub(r'F1.|.csv', '', ''.join(x))), select_F1))
select_F2_trimmed = list(map(lambda x: re.sub(r'^$', 'Not selected', re.sub(r'F2.|.csv', '', ''.join(x))), select_F2))
select_F3_trimmed = list(map(lambda x: re.sub(r'^$', 'Not selected', re.sub(r'F3.|.csv', '', ''.join(x))), select_F3))
select_F3_trimmed = list(map(lambda x: re.sub(r'\.', ' ', ''.join(x)), select_F3_trimmed))
select_fallback_trimmed = list(
    map(lambda x: re.sub(r'^$', 'No', re.sub('fallback', 'Yes', ''.join(x))), select_fallback))
# データフレームを作成する。
# 0番目に「比較しない」を充てるため、リストの先頭に'No Comparison'を用意し、それに各々を結合する。
select_F1_complete = ['No comparison']
select_F2_complete = ['No comparison']
select_F3_complete = ['No comparison']
select_fallback_complete = ['No comparison']
select_F1_complete.extend(select_F1_trimmed)
select_F2_complete.extend(select_F2_trimmed)
select_F3_complete.extend(select_F3_trimmed)
select_fallback_complete.extend(select_fallback_trimmed)
data_frame_of_selectable_patterns = \
    pd.DataFrame({'Selectable number': range(0, last_number_at_select + 1),
                  'F1.Age': pd.Series(select_F1_complete),
                  'F2.Region': pd.Series(select_F2_complete),
                  'F3.Occupation': pd.Series(select_F3_complete),
                  'Fallbacked': pd.Series(select_fallback_complete)},
                 columns=['Selectable number', 'F1.Age', 'F2.Region', 'F3.Occupation', 'Fallbacked'])


# Dashアプリケーション #
# アプリケーションにスタイルシートを適用する。
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# 選択可能パターン表から選択可能番号を取り出す。dcc.Dropdownで選択可能リストを読み込むため。
selectable_number = data_frame_of_selectable_patterns['Selectable number']

# Dashboardのレイアウトを構成する。
app.layout = html.Div([
    html.H1('Service Comparison Dashboard'),
    # 各サービスの説明表と選択パターン可能表を掲載する。
    html.H4('Information, Available Combinations'),
    html.Div([
        dash_table.DataTable(
            id='Information',
            columns=[{"name": i, "id": i} for i in description_of_service_types.columns],
            data=description_of_service_types.to_dict('records'),
            fixed_rows={'headers': True, 'data': 0},
            style_cell={'width': '100px'},
            style_table={
                'maxWidth': '600px', 'maxHeight': '200px',
                'overflowX': 'scroll', 'overflowY': 'scroll',
            }
        )], style={"width": "30%", "display": "inline-block"}),
    html.Div([
        dash_table.DataTable(
            id='Comparison',
            columns=[{"name": i, "id": i} for i in data_frame_of_selectable_patterns.columns],
            data=data_frame_of_selectable_patterns.to_dict('records'),
            fixed_rows={'headers': True, 'data': 0},
            style_cell={'width': '100px'},
            style_table={
                'maxWidth': '1200px', 'maxHeight': '200px',
                'overflowX': 'scroll', 'overflowY': 'scroll',
            }
        )], style={"width": "66%", "display": "inline-block"}),
    # 比較したいデータを選択可能番号（選択可能パターン表）で選択させ、グラフを描画する。
    html.H4("Input value described in Available Combinations. When zero is input, comparisons are not conducted."),
    html.Div([
        dcc.Dropdown(id="1st", options=[{"label": i, "value": i} for i in selectable_number], value="1st Comparison")
    ], style={"width": "32%", "display": "inline-block"}),
    html.Div([
        dcc.Dropdown(id="2nd", options=[{"label": i, "value": i} for i in selectable_number], value="2nd Comparison")
    ], style={"width": "32%", "display": "inline-block"}),
    html.Div([
        dcc.Dropdown(id="3rd", options=[{"label": i, "value": i} for i in selectable_number], value="3rd Comparison")
    ], style={"width": "32%", "display": "inline-block"}),
    dcc.Graph(id="comparison")
], style={"padding": 10})

# 描画用データを取り出すためのパラメータ
last_cell_number_ex_non_use = coes['diff.data_F'].__len__() - 1


# レイアウトを呼び出し、各パーツをアプリケーションに表示する。 #
@app.callback(Output("comparison", "figure"), [Input("1st", "value"),
                                               Input("2nd", "value"),
                                               Input('3rd', 'value')])
def update_graph(first, second, third):
    return {'data': [{'x': code_of_service_types_ex_non_use,
                      'y': data_for_dash[first][0:last_cell_number_ex_non_use],
                      'type': 'bar', 'name': '1st'},
                     {'x': code_of_service_types_ex_non_use,
                      'y': data_for_dash[second][0:last_cell_number_ex_non_use],
                      'type': 'bar', 'name': '2nd'},
                     {'x': code_of_service_types_ex_non_use,
                      'y': data_for_dash[third][0:last_cell_number_ex_non_use],
                      'type': 'bar', 'name': '3rd'}],
            'layout': {}
            }


# アプリケーションを起動する。 #
if __name__ == '__main__':
    app.run_server()
