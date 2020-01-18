# Pythonによる技術の棚卸し #
成果物（2020/1/1時点）は以下のとおりです。各々の詳細は、該当のMarkdownを参照してください。

文体を次のように統一しています。
* 敬体：本ドキュメント
* 常体：各成果物のMarkdown

### 実行手順
実行環境にAnaconda3, PyCharm, R, RStudioがインストールされていることを前提とします。

PyCharmでリポジトリのクローン先となるプロジェクトフォルダを作成します。プロジェクトフォルダ名とリポジトリ名とを揃えておくと便利です。作成後RStudioによって、PyCharmのプロジェクトフォルダと同名のProjectを作成します。Rprojファイルがあるディレクトリをワーキングディレクトリとして認識します。

クローン先を用意した後、以下の手順を実行します。
* Gitを使用の場合：作成したクローン先プロジェクトフォルダを、一度他のディレクトリに移動してから、クローン先のディレクトリにおいて`git clone`コマンドを実行します。Sourcetree等のGUIクライアントでも同機能があります。実行後、移動済クローン先プロジェクトフォルダに残っているものを、`git clone`したリポジトリの直下に移動します。なお、`.gitignore`は`git clone`したものを正とします。
* そうでない場合：`Clone or download`の`Download ZIP`をクリックし、クローン先のディレクトリに展開します。  

Pythonのライブラリで足りないものを、あらかじめインストールします。

### 1.propensity_score_analysis
Rで実装した「サービス比較システム」をPythonに移植したものです。本システムの特色は次の2点です。
1. 一般化傾向スコア分析によるサービス導入効果の予測
1. Dashによるサービス比較の容易化

移植先は`estimation.py`と`rendering.py`の2つであり、Rで実装したサブルーチンのうち次のものを移植しています。

##### `estimation.py`
* 一般化傾向スコアの推定
* 逆確率重み（IPW）の計算
* IPW推定量の計算
* 縮退時、一般化線形モデルによるサービス導入効果の推定

##### `rendering.py`
Shiny Dashboardによるサービス比較と可視化であり、Pythonに移植するときDashを代用しています。

データ構造仕様とフローチャートは概ね、R版サービス比較システムと同様です。R版サービス比較システムの詳細は下記URLのとおりです。  
https://github.com/taiyoutsuhara/portfolio-r/blob/master/1.propensity_score_analysis/readme_ja.md

一般化傾向スコア推定用整形済データと分割済データの用意は、次の手順によります。
1. "/portfolio-python/1.propensity_score_analysis/"配下に"data_format_fst"フォルダと"data_format"フォルダを新規作成します。
1. "/portfolio-r/1.propensity_score_analysis/"配下の`00_main.R`において、先頭から`01_dataformat.R`までを行選択し実行します。
1. "/portfolio-r/1.propensity_score_analysis/dataformat/"配下に出来上がったfstファイルを、"/portfolio-python/1.propensity_score_analysis/data_format_fst/"配下にコピーします。
1. "/portfolio-python/1.propensity_score_analysis/"配下の`convert_fst_to_csv.R`で、整形済データの形式をfstからcsvに変換します。出力先は"/portfolio-python/1.propensity_score_analysis/data_format/"です。

#### R版との相違
##### 途中のデータ出力ファイル形式
R版ではfstが使用されていますが、Python版ではいずれもcsvによります。なお、Gitのファイル追跡から途中のデータ出力を外しています。

##### グラフ描画用データフレームの構造
R版は`spec.data_frame_for_ggplot2.csv`のとおりですが、Python版は辞書型であり、以下のkeyと要素を含んでいます。

グラフ用描画データ形式はリストであり、サービスの種類はN次元配列（ndarray）です。
```
{'x': サービスの種類（non-useを表すカテゴリを除外）,
'y': グラフ用描画データ[比較したいデータの選択可能番号][範囲],
'type': 'bar', 'name': 比較用序数（'1st', '2nd' or '3rd'）}
```

##### ダッシュボードの画面構成
* R (Shiny Dashboard) 版：複数ページ
* Python (Dash) 版：単一ページ