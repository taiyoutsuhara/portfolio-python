# Pythonによる技術の棚卸し #
成果物（2020/1/1時点）は以下のとおりです。各々の詳細は、該当のMarkdownを参照してください。

文体を次のように統一しています。
* 敬体：本ドキュメント
* 常体：各成果物のMarkdown

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

#### R版との相違
##### 途中のデータ出力ファイル形式
R版ではfstが使用されていますが、Python版ではいずれもcsvによります。なお、Gitのファイル追跡から途中のデータ出力を外しています。

##### グラフ描画用データフレームの構造
R版は`spec.data_frame_for_ggplot2.csv`のとおりですが、Python版は辞書型であり、以下のkeyと要素を含んでいます。

```
{'x': サービスの種類（non-useを表すものを除く。）,
'y': グラフ用描画データ[比較用序数][範囲],
'type': 'bar', 'name': 比較用序数}
```