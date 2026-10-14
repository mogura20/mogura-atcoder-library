# mogura-atcoder-library

Pythonの競技プログラミング用ライブラリ。関数・クラス名に`mogura`を入れ、内部変数は意味の分かる名前にしています。日本語の説明、差し替え可能な演算、使用例、ランダム差分テストを用意しています。

外部パッケージ不要、Python 3.9以上。AtCoderへの提出は必要なコードを1ファイルへコピーします。`mogura`というパッケージがジャッジ環境へインストールされているわけではありません。

## 最初の使い方

```sh
git clone https://github.com/mogura20/mogura-atcoder-library.git
cd mogura-atcoder-library
python3 -m unittest discover -s tests -v
```

練習時はリポジトリ直下で、例えば次のように使います。

```python
from mogura.dsu import MoguraDSU

uf = MoguraDSU(5)
uf.merge(0, 1)
assert uf.same(0, 1)
assert uf.size(0) == 2
```

## 共通の約束

- 頂点・添字は0始まり。入力が1始まりなら読み込み時に1を引く。
- 区間は半開区間`[left, right)`。空区間の結果は0や指定した単位元。
- 受け取ったグラフや初期配列は書き換えない。
- 数学関数以外はmodを自動では取らない。必要なら演算で指定する。
- 汎用木の演算は結合的で、値・単位元・作用を破壊的に変更しないこと。
- 添字チェックは`assert`、代表的な前提違反は`ValueError`。入力の完全な検証をする設計ではない。
- 計算量は指定した演算がO(1)の場合。長い文字列の連結などは演算自体のコストも加わる。

## ライブラリ一覧

全59 APIを分野別にまとめています。実装はすべて同じ`mogura/`階層にあり、一覧の「実装」から開けます。

[使用例・設定方法](docs/usage.md) / [Python基本操作メモ](docs/python_notes.md)

| 分野 | API | 用途・条件 | 実装 |
|---|---|---|---|
| 基本・区間処理 | `mogura_compress` | 座標圧縮。元の値と辞書も返す / O(n log n) | [basic.py](mogura/basic.py) |
| 基本・区間処理 | `mogura_prefix_sum` | 1次元累積和 / O(n) | [basic.py](mogura/basic.py) |
| 基本・区間処理 | `mogura_bisect_int` | 整数二分探索。判定の単調性が必要 | [basic.py](mogura/basic.py) |
| 基本・区間処理 | `MoguraPrefixSum2D` | 2次元累積和。長方形の和 / 前処理O(HW)、問合せO(1) | [range_utils.py](mogura/range_utils.py) |
| 基本・区間処理 | `mogura_subarrays_sum_leq` | 非負配列のしゃくとり。区間数と最長長 / O(n) | [range_utils.py](mogura/range_utils.py) |
| 基本・区間処理 | `mogura_true_runs` | 要素条件が真の連続区間一覧 / O(n) | [range_utils.py](mogura/range_utils.py) |
| データ構造 | `MoguraDSU` | Union-Find。併合成功判定unite、代表一覧roots、サイズ一覧group_sizes / [使い方](docs/usage.md#union-find) | [dsu.py](mogura/dsu.py) |
| データ構造 | `MoguraWeightedDSU` | 差の制約と矛盾検出。diff(a,b)=p[b]-p[a] | [weighted_dsu.py](mogura/weighted_dsu.py) |
| データ構造 | `MoguraFenwickTree` | 点加算・区間和・累積和境界 / O(log n) | [fenwick.py](mogura/fenwick.py) |
| データ構造 | `MoguraSegTree` | 結合的演算の点更新・区間集約・境界探索 / O(log n) | [segtree.py](mogura/segtree.py) |
| データ構造 | `MoguraLazySegTree` | 更新作用を指定する区間更新・集約 / O(log n) | [lazy_segtree.py](mogura/lazy_segtree.py) |
| グラフ・木 | `mogura_bfs` | 重みなし最短路。単一/複数始点 / O(V+E) | [graph.py](mogura/graph.py) |
| グラフ・木 | `mogura_zero_one_bfs` | 0/1重み最短路。単一/複数始点 / O(V+E) | [graph_extra.py](mogura/graph_extra.py) |
| グラフ・木 | `mogura_dijkstra` | 非負重み最短路。単一/複数始点 | [graph.py](mogura/graph.py) |
| グラフ・木 | `mogura_bellman_ford` | 負辺最短路。負閉路の影響を-infで返す / O(VE+V+E) | [graph_extra.py](mogura/graph_extra.py) |
| グラフ・木 | `mogura_floyd_warshall` | 全点対最短路。負閉路の影響も判定 / O(V³) | [graph_extra.py](mogura/graph_extra.py) |
| グラフ・木 | `mogura_restore_path` | 親配列から経路を復元 / O(経路長) | [graph.py](mogura/graph.py) |
| グラフ・木 | `mogura_dfs_orders` | 反復DFS。行きがけ順・帰りがけ順・親 / O(V+E) | [graph_extra.py](mogura/graph_extra.py) |
| グラフ・木 | `mogura_toposort` | 有向グラフの順序。閉路ならNone / O(V+E) | [graph.py](mogura/graph.py) |
| グラフ・木 | `mogura_scc` | 強連結成分。成分番号はトポロジカル順 / O(V+E) | [graph.py](mogura/graph.py) |
| グラフ・木 | `MoguraLCA` | 木のLCA・祖先・距離 / 前処理O(n log n)、問合せO(log n) | [lca.py](mogura/lca.py) |
| グラフ・木 | `mogura_kruskal` | 辺リストから最小全域森。成分数も返す | [mst.py](mogura/mst.py) |
| グラフ・木 | `mogura_prim` | 隣接リストから最小全域森。全成分を処理 | [mst.py](mogura/mst.py) |
| グラフ・木 | `MoguraHopcroftKarp` | 最大二部マッチング。反復DFS / O((V+E)√V) | [matching.py](mogura/matching.py) |
| グラフ・木 | `MoguraBipartiteMatching` | 最大二部マッチング。BFS増加路法 / O(L*(L+R+E)) | [matching.py](mogura/matching.py) |
| 動的計画法 | `mogura_lis` | LISと添字復元。狭義増加/非減少 / O(n log n) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_lcs` | LCSと要素列復元 / O(nm) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_hamiltonian_cost` | Hamiltonian path/TSP。始点・巡回を指定 / O(n²2^n) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_interval_dp` | 二つの区間を結合する区間DP。追加コストを指定 / O(n³) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_grid_path_count` | 右/下移動の経路数。壁とmodを指定 / O(HW) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_tree_independent_set` | 木の最大重み独立集合と頂点復元 / O(n) | [dp.py](mogura/dp.py) |
| 動的計画法 | `mogura_expected_steps` | 正の前進量・確率から到達までの期待回数 | [dp.py](mogura/dp.py) |
| 数学・数論 | `mogura_sieve` | 素数列挙 / O(N log log N) | [number_theory.py](mogura/number_theory.py) |
| 数学・数論 | `mogura_factorize` | 単発の素因数分解 / O(√N) | [number_theory.py](mogura/number_theory.py) |
| 数学・数論 | `MoguraOsaK` | 最小素因数を前計算し大量の素因数分解に対応 | [math_extra.py](mogura/math_extra.py) |
| 数学・数論 | `mogura_divisors` | 正整数の約数を昇順で列挙 / O(√N) | [math_extra.py](mogura/math_extra.py) |
| 数学・数論 | `mogura_extgcd` | 拡張Euclid。(g,x,y)、a*x+b*y=g | [number_theory.py](mogura/number_theory.py) |
| 数学・数論 | `MoguraComb` | 素数modのnCr/nPr。n<modが前提 / 問合せO(1) | [number_theory.py](mogura/number_theory.py) |
| 数学・数論 | `mogura_ceil_div` | floatを使わない整数切り上げ。負数も可 | [math_extra.py](mogura/math_extra.py) |
| 数学・数論 | `mogura_base_digits` | 任意基数の桁リスト。上位から返す | [math_extra.py](mogura/math_extra.py) |
| 数学・数論 | `mogura_team_sizes` | 人数配分の整数分割/組成を逐次列挙 | [math_extra.py](mogura/math_extra.py) |
| 幾何・行列 | `mogura_cross` | 2次元ベクトルの外積 | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_dot` | 2次元ベクトルの内積 | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_distance_squared` | 距離の二乗。平方根を取らず比較できる | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_segments_intersect` | 整数座標の閉線分交差。端点・重なり・長さ0も可 | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_rotate_point` | 中心指定の反時計回り回転。角度は度 | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_transpose` | 行列の転置。リストのリストで返す | [geometry.py](mogura/geometry.py) |
| 幾何・行列 | `mogura_rotate_grid` | 行列の時計回り90度回転。回数指定可 | [geometry.py](mogura/geometry.py) |
| 文字列 | `mogura_z_algorithm` | 先頭との最長共通接頭辞長 / O(n) | [string.py](mogura/string.py) |
| 文字列 | `mogura_z_search` | 重なりを含む全出現位置。固定区切り文字不要 | [string.py](mogura/string.py) |
| 文字列 | `mogura_manacher` | 奇数/偶数回文の半径 / O(n) | [string.py](mogura/string.py) |
| 文字列 | `mogura_run_length` | 連続する同じ値を(value,count)へ圧縮 / O(n) | [string.py](mogura/string.py) |
| 文字列 | `MoguraTrie` | 文字列挿入・前方一致数・全ペアのLCP長総和 | [trie.py](mogura/trie.py) |
| 文字列 | `MoguraRollingHash` | 二重ハッシュ。区間取得O(1)、衝突の可能性あり | [rolling_hash.py](mogura/rolling_hash.py) |
| 全探索・探索テンプレート | `mogura_states` | 2/3値などの状態列を逐次列挙 | [enumeration.py](mogura/enumeration.py) |
| 全探索・探索テンプレート | `mogura_distinct_permutations` | 重複なし順列。外部依存なし | [enumeration.py](mogura/enumeration.py) |
| 全探索・探索テンプレート | `mogura_anneal` | 焼きなまし。評価・近傍・コピーを差し替え | [heuristic.py](mogura/heuristic.py) |
| 全探索・探索テンプレート | `mogura_beam_search` | ビームサーチ。評価・遷移・重複キーを差し替え | [heuristic.py](mogura/heuristic.py) |
| 全探索・探索テンプレート | `MoguraInteractiveIO` | flush付き対話通信とローカル模擬の切替 | [interactive.py](mogura/interactive.py) |

詳細な引数・戻り値・計算量・前提は、各クラス/関数のdocstringに記載しています。関数・メソッド直下の「入力例・結果」では、`>>>`が呼び出し、その下の行が期待結果です。更新する操作には操作後の確認も付けています。例はdoctestで自動検証します。

## 提出用に1ファイルへ展開

自分の解答を`main.py`へ書き、必要なモジュールだけ指定します。

```sh
git rev-parse HEAD
python3 tools/bundle.py dsu graph --main main.py --source-ref <公開済みの40桁コミットSHA> --output submission.py
python3 submission.py < input.txt
```

`<公開済みの40桁コミットSHA>`は実際の値へ置き換えてください。展開後は`submission.py`を提出します。ツールはAIを呼ばず、指定したソースの連結とmogura importの除去だけを行います。コードの難読化・圧縮はしません。

対応するimportは、トップレベルの`from mogura.graph import mogura_dijkstra`のような形式です。別名import、`*`、`import mogura.graph`、同じ行に別の文を置いたimportには対応せず、エラーにします。mainで使うモジュールを指定してください。ライブラリ内部の依存（例: mst→dsu）は自動展開します。

`--source-ref`なしでも開発用に出力できますが、未公開の注意コメントが付き、出典URLは付きません。指定時は手元のコードとそのローカルGitコミットの一致を検査し、古いURLで修正版を引用することを防ぎます。GitHubでの公開状況や公開時刻は自動確認しません。Git履歴のないZIP取得ではこの検査が使えないためgit cloneしてください。

公開済みのexamplesファイルを`--main`へ指定した場合は、そのファイルの出典も出力します。自分の解答を任意のファイルへ書いた場合、その解答は自分で記述する前提です。別のAI生成コードを加える場合は別途、事前公開と参照URLが必要です。

## コンテスト前の公開運用

このコードは生成AIの支援で事前作成しています。[AtCoder生成AI対策ルール（2026年10月14日版）](https://info.atcoder.jp/entry/llm-rules-ja)に沿って、コピーして使うコードを開始前にWeb公開し、使用時に参照URLを添付します。

1. 開始前に変更とテストを終え、GitHubへpushする。
2. ログアウト状態でも実際のファイルを読めることを確認する。ローカルのcommitだけでは公開にならない。
3. その公開版のコミットSHAを控え、同じ版のコードを使う。
4. bundleの`--source-ref`にそのSHAを指定し、提出コードにSourceコメントを残す。
5. 開催中のABC/ARC/AGCではAI補完・AIデバッグ等を使用しない。

参照URLのコメント記載とコミット固定URLは、このリポジトリで採用する運用方法です。AtCoderが特定のコメント形式やGitHub利用を要求しているわけではありません。ライブラリの利用判断・問題への適用は自分で行います。ルール変更時には公式告知を確認してください。

## 補足資料

[元ファイルと移行先の対応表](docs/desktop_inventory.md) / [更新履歴](CHANGELOG.md)

## 検証と性能

```sh
python3 -m unittest discover -s tests -v
```

固定シードのランダム入力と境界ケースで検証します。区間処理はPythonリスト、DijkstraはWarshall–Floyd、SCCは到達可能性、LCAは親を辿る方法、文字列は愚直探索と比較します。深さ10000の鎖状グラフ・木と提出用展開後の実行も確認します。

GitHub ActionsでもCPython 3.9 / 3.13 / PyPy 3.10で実行します。AtCoderの過去問へ自動提出はしていません。Pythonの実行時間とメモリは問題の制約に応じて別途見積もってください。特に汎用遅延セグメント木は関数呼び出しとタプル生成が多く、専用実装より定数倍が大きくなります。

## ライセンスと出典

MIT License。コピー・再配布時には著作権表示とライセンス表示を保持してください。bundle出力にはライセンスをコメントとして付けます。

一般的なアルゴリズムをこのリポジトリ用に実装しました。`mogura`の命名は識別用で、アルゴリズムの新規性を意味しません。第三者コードを今後追加する場合は[THIRD_PARTY.md](THIRD_PARTY.md)へ出典と条件を記録します。
