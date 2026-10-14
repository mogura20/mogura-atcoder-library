# Desktop由来の追加機能と使い分け

2026年10月14日、手元の`atcoder`フォルダを既存公開版と比較し、未収録の機能を汎用APIへ整理しました。[元ファイルと移行先の対応表](desktop_inventory.md)も用意しています。元のファイルは変更していません。

## 追加API一覧

| 分野 | モジュール / API | 戻り値・前提 |
|---|---|---|
| データ構造 | [weighted_dsu](../mogura/weighted_dsu.py) / `MoguraWeightedDSU` | 差の制約、矛盾を検出。diff(a,b)=potential[b]-potential[a] |
| グラフ | [graph_extra](../mogura/graph_extra.py) / `mogura_dfs_orders` | 行きがけ順・帰りがけ順・親。反復DFS |
| 最短路 | graph_extra / `mogura_zero_one_bfs` | 0/1重み、単一/複数始点。(dist,parent) |
| 最短路 | graph_extra / `mogura_bellman_ford` | 負辺可。未到達inf、負閉路の影響は-inf |
| 全点対最短路 | graph_extra / `mogura_floyd_warshall` | 距離行列。負閉路を経由できる組は-inf |
| 全域木 | [mst](../mogura/mst.py) / `mogura_kruskal`, `mogura_prim` | (重み和,辺リスト,成分数)。非連結なら最小全域森 |
| 二部マッチング | [matching](../mogura/matching.py) / `MoguraHopcroftKarp` | O((V+E)√V)、反復DFS |
| 二部マッチング | matching / `MoguraBipartiteMatching` | 読みやすいBFS増加路法、O(L*(L+R+E)) |
| 列DP | [dp](../mogura/dp.py) / `mogura_lis` | (長さ,添字列)。strict=Falseで非減少 |
| 列DP | dp / `mogura_lcs` | (長さ,要素リスト)。文字列に戻すならjoin |
| ビットDP・TSP | dp / `mogura_hamiltonian_cost` | 任意/固定始点、cycle=Trueで巡回。最小コスト |
| 区間DP | dp / `mogura_interval_dp` | 追加コスト関数を指定、全DPテーブル |
| グリッドDP | dp / `mogura_grid_path_count` | 右/下の経路数。壁記号とmodを指定 |
| 木DP | dp / `mogura_tree_independent_set` | (最大重み,選択頂点)。負重み可、空集合可 |
| 確率DP | dp / `mogura_expected_steps` | 正の前進量と確率を指定。到達までの期待回数 |
| 長方形の和 | [range_utils](../mogura/range_utils.py) / `MoguraPrefixSum2D` | sum(top,left,bottom,right)、半開区間 |
| しゃくとり | range_utils / `mogura_subarrays_sum_leq` | 非負配列のみ。(和<=上限の非空区間数,最長長) |
| 連続区間 | range_utils / `mogura_true_runs` | 各要素の条件が真である最大連続区間一覧 |
| 数論 | [math_extra](../mogura/math_extra.py) / `MoguraOsaK`, `mogura_divisors` | 大量の素因数分解、昇順の約数列挙 |
| 整数処理 | math_extra / `mogura_ceil_div`, `mogura_base_digits` | float不要の切り上げ、上位からの桁列 |
| 人数配分 | math_extra / `mogura_team_sizes` | 人数の分割/組成を逐次列挙。個人の割当てではない |
| 幾何 | [geometry](../mogura/geometry.py) / `mogura_segments_intersect` | 整数座標の閉線分。端点接触・重なり・長さ0にも対応 |
| 幾何 | geometry / `mogura_cross`, `mogura_dot`, `mogura_distance_squared` | 外積・内積・距離の二乗 |
| 回転 | geometry / `mogura_rotate_point` | 度で反時計回り、中心指定可、結果はfloat |
| 行列 | geometry / `mogura_transpose`, `mogura_rotate_grid` | 転置、時計回り90度回転。外部依存なし |
| 文字列 | [trie](../mogura/trie.py) / `MoguraTrie` | 挿入数・前方一致数・全ペアのLCP長総和 |
| 文字列 | [rolling_hash](../mogura/rolling_hash.py) / `MoguraRollingHash` | 二重ハッシュ、区間取得O(1)。衝突はあり得る |
| 文字列 | [string](../mogura/string.py) / `mogura_run_length`, `mogura_z_search` | ランレングス、区切り文字に依存しない検索 |
| 全探索 | [enumeration](../mogura/enumeration.py) / `mogura_states`, `mogura_distinct_permutations` | 2/3値等の状態列、重複なし順列のgenerator |
| ヒューリスティック | [heuristic](../mogura/heuristic.py) / `mogura_anneal`, `mogura_beam_search` | 状態・評価・遷移を指定。最大化に統一 |
| 対話問題 | [interactive](../mogura/interactive.py) / `MoguraInteractiveIO` | flush付き通信とローカル模擬の切替 |

## 条件の変更・復元の例

```python
from mogura.weighted_dsu import MoguraWeightedDSU
uf = MoguraWeightedDSU(3)
assert uf.merge(0, 1, 10)  # p[1]-p[0]=10
assert uf.merge(1, 2, -3)  # p[2]-p[1]=-3
assert uf.diff(0, 2) == 7
assert not uf.merge(0, 2, 8)  # 矛盾。既存の制約は維持される
```

```python
from mogura.dp import mogura_lis
a = [2, 2, 1, 3]
length, indices = mogura_lis(a, strict=False)
assert [a[i] for i in indices] == [2, 2, 3]
```

石の併合の区間DPは、合体コストを関数で渡します。

```python
from mogura.basic import mogura_prefix_sum
from mogura.dp import mogura_interval_dp
a = [10, 20, 30]
prefix = mogura_prefix_sum(a)
table = mogura_interval_dp(len(a), lambda left, middle, right: prefix[right]-prefix[left])
assert table[0][len(a)] == 90
```

この関数は二つの区間をまとめる遷移用です。全ての区間DPを表せるわけではなく、状態や遷移が違う場合は実装を変更します。

```python
from mogura.dp import mogura_hamiltonian_cost
cost = [[0, 2, 5], [2, 0, 1], [5, 1, 0]]
assert mogura_hamiltonian_cost(cost) == 3  # 任意始点のpath
assert mogura_hamiltonian_cost(cost, start=0, cycle=True) == 8
```

TSPの領域はO(n2^n)。Pythonでは状態数だけでなくリストと整数のメモリも見積もります。辺がない場所には`float('inf')`を指定します。

## 最短路とマッチングの選択

| 辺の条件 | 選択 |
|---|---|
| 全て重み1 | 既存の`mogura_bfs` |
| 重み0/1 | `mogura_zero_one_bfs` |
| 非負重み | 既存の`mogura_dijkstra` |
| 負辺あり、単一始点 | `mogura_bellman_ford` |
| 全頂点間、小さな頂点数 | `mogura_floyd_warshall` |

Bellman–Fordの`dist[v] == -float('inf')`は有限な最短距離が存在しない頂点です。その頂点について経路を復元しないでください。`float('inf')`は未到達です。

```python
from mogura.matching import MoguraHopcroftKarp
matching = MoguraHopcroftKarp(2, 2)
for left, right in [(0, 0), (0, 1), (1, 0)]:
    matching.add_edge(left, right)
assert matching.maximum_matching() == 2
assert len(matching.pairs()) == 2
```

左右の頂点番号は別々に0始まり。繰り返し呼び出したときの戻り値は新しく増えた数ではなく現在の総数です。大規模グラフはHopcroft–Karpを選びます。

## ヒューリスティックを差し替える箇所

[heuristic_recipes.py](../examples/heuristic_recipes.py)が動作例です。評価は大きいほど良い方向に統一し、最小化なら符号を反転します。

焼きなましは`score`、`propose`、`copy_state`を指定。`propose`は元の状態を変更せず新しい候補を返す契約です。差分評価なら候補状態に更新済みのスコアを保持します。固定反復回数と固定seedは再現可能、時間制限では環境の速さにより結果が変わります。

ビームサーチは`expand`、`evaluate`、`is_complete`、必要なら`final_score`と`key`を指定。キーでまとめてよいかは問題ごとに判断します。例えば訪問順を扱う問題では訪問集合だけでなく末尾も必要です。完成解なしは`None`を返すため、合法な初期解等の代替を用意します。

どちらも最適解保証はありません。コールバック1回の処理中には時間制限で強制中断できないため、長い処理を入れないでください。

## 整理時に修正した点

- 1始まり・閉区間の混在を0始まり・半開区間へ統一。
- DFSの共有されるデフォルト引数`visited=[]`を廃止し反復処理へ。
- LISの空列、TSPの0/1頂点を定義。LCSのデバッグ出力を削除。
- 固定の距離上限`10**18`をinfへ。負閉路の影響を頂点/組別に扱う。
- 重み付きUnion-Findは矛盾・非連結を明示し、差の符号を文書化。
- 線分交差の縮退ケースを検証。
- ハッシュの区間取得ごとの逆元計算を廃止して二重化。ただし衝突はあり得る。
- Z検索の固定区切り文字`$`を廃止。
- 人数配分は外部依存をなくしgenerator化。
- 焼きなましは最良解をコピーし、ビームサーチは早い完成解だけで終了しない。
- 期待値の不要な小数切り捨てを廃止。

## 提出用の展開

```sh
python3 tools/bundle.py weighted_dsu mst dp --main main.py --source-ref <公開済み40桁SHA> --output submission.py
```

`mst`が使う`dsu`は自動展開します。examplesもコピーする場合は例の参照URLも必要です。READMEの事前公開運用を参照してください。

元の学習メモで名前だけ挙がっていたSparse Table、HLD、桁DP、NTT等は移行対象となる実装がなく、今回追加していません。実装の有無は一覧と対応表で確認してください。
