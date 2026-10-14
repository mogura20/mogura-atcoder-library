# 使用例・設定方法

[全API一覧](../README.md#ライブラリ一覧)から選んだ処理を、問題に合わせて設定するためのガイドです。すべてのAPIは同じ`mogura/`階層にあり、作成時期による区別はありません。

## データ構造・基本処理

### Union-Find

`merge`は代表頂点を返し、`unite`は新しく併合できたかをboolで返します。通常の併合判定には`unite`を使うと短く書けます。

```python
from mogura.dsu import MoguraDSU

uf = MoguraDSU(5)
assert uf.unite(0, 1) is True   # 別の成分を併合
assert uf.unite(1, 0) is False  # すでに同じ成分
assert uf.unite(2, 2) is False  # 自己併合
root = uf.merge(2, 3)           # 代表頂点が必要ならmerge
assert root == uf.leader(2)
assert uf.component_count == 3
assert uf.size(0) == 2

roots = uf.roots()
sizes = uf.group_sizes()
assert len(roots) == len(sizes) == uf.component_count
assert sizes == [uf.size(vertex) for vertex in roots]
assert sorted(sizes) == [1, 2, 2]
```

| 操作 | 戻り値・用途 | 計算量 |
|---|---|---|
| `unite(a,b)` | 新しく併合したらTrue、同じ成分ならFalse | 償却O(α(n)) |
| `merge(a,b)` | 併合後の代表頂点。既存の戻り値を維持 | 償却O(α(n)) |
| `roots()` | 現在の代表頂点の一覧。頂点番号の昇順 | O(n) |
| `group_sizes()` | rootsと同じ順序の成分サイズ一覧 | O(n) |
| `component_count` | 現在の成分数。属性なので括弧は不要 | O(1) |

`roots()`と`group_sizes()`は呼び出し時点の新しいリストを返します。後から併合しても、そのリストは自動更新されません。代表は成分の最小番号とは限らず、サイズの一覧もサイズ順ではありません。最大サイズは`max(uf.group_sizes(), default=0)`で取得できます。

**`if uf.merge(a,b):`は成功判定になりません。** 代表が0だと偽になるため、`if uf.unite(a,b):`を使ってください。無向グラフで辺を追加するとき、`unite`がFalseなら両端がすでに接続しており、その辺で閉路が生じます（自己ループ・多重辺も含む）。

クラスカル法と同じ、重みが小さい辺から採用する例です。

```python
from mogura.dsu import MoguraDSU

edges = [(0, 1, 2), (1, 2, 1), (0, 2, 5)]
uf = MoguraDSU(3)
total = 0
chosen = []
for a, b, weight in sorted(edges, key=lambda edge: edge[2]):
    if uf.unite(a, b):
        total += weight
        chosen.append((a, b, weight))
assert total == 3
assert len(chosen) == 2
assert uf.component_count == 1
```

一つの成分のサイズだけ必要なら`size(vertex)`、成分数だけなら`component_count`を使います。`roots()`・`group_sizes()`は全頂点を走査するので、各クエリで呼び出すとO(nQ)になります。メンバー一覧が必要なときは従来の`groups()`を使います。`MoguraDSU(0)`でも3つの一覧取得はすべて`[]`を返します。

### 区間最小値・最大値・和・GCD

```python
from math import gcd
from mogura.segtree import MoguraSegTree

minimum = MoguraSegTree([8, 3, 5], min, float('inf'))
maximum = MoguraSegTree([8, 3, 5], max, -float('inf'))
total = MoguraSegTree([8, 3, 5], lambda a, b: a + b, 0)
divisor = MoguraSegTree([8, 3, 5], gcd, 0)
minimum.set(1, 10)
assert minimum.prod(0, 2) == 8
```

非可換な演算でも左右の順序を保持します。ただし減算のように結合則を満たさない演算は指定できません。

`max_right(left, predicate)`では、単位元の判定が真で、区間を延ばすと真から偽へ一度だけ変わる必要があります。負数を含む配列で「和が上限以下」は一般にこの条件を満たしません。Fenwick Treeの`lower_bound`も非負要素が前提です。

### 区間更新

[lazy_recipes.py](../examples/lazy_recipes.py)に3通りの設定があります。

| 設定 | `apply(l,r,action)`のaction | 和の取得 |
|---|---|---|
| 区間加算・和 | 加算量 | `seg.prod(l,r)[0]` |
| 区間代入・和 | 代入値（Noneは更新なし） | 同上 |
| 一次変換・和mod | `(a,b)`でx→a*x+b | 同上 |

値は`(区間和, 区間長)`を保持します。単位元は`(0,0)`。更新の合成は`composition(new, old)`で**oldを先、newを後**に適用します。加算だけでは気づきにくい合成順の誤りも、一次変換の差分テストで確認しています。

```sh
python3 -m examples.lazy_recipes
```

設定例を提出へコピーする場合、設定例ファイルの参照URLも添付してください。bundleツールの`--main examples/lazy_recipes.py`では、その出典コメントも生成します。

### 重み付きUnion-Find

```python
from mogura.weighted_dsu import MoguraWeightedDSU
uf = MoguraWeightedDSU(3)
assert uf.merge(0, 1, 10)  # p[1]-p[0]=10
assert uf.merge(1, 2, -3)  # p[2]-p[1]=-3
assert uf.diff(0, 2) == 7
assert not uf.merge(0, 2, 8)  # 矛盾。既存の制約は維持される
```

## グラフ・木

- BFS: `graph[v] = [to, ...]`。到達不能の距離は`-1`。
- Dijkstra: `graph[v] = [(to, weight), ...]`。到達不能は`float('inf')`。負辺は不可。
- 無向グラフは両方向の辺を追加。グリッドは必要なら頂点番号を`row * width + column`へ変換する。
- 始点引数に整数または始点リストを指定できる。リストならすべて距離0。
- 経路復元前に距離で到達可能性を判定する。親の`-1`は始点と到達不能の両方に使う。
- LCAは連結な無向木用。一般グラフ・森・重み付き距離にはそのまま使わない。

使用例: [shortest_path.py](../examples/shortest_path.py)。例の入力は0始まりです。

### 最短路とマッチングの選択

| 辺の条件 | 選択 |
|---|---|
| 全て重み1 | `mogura_bfs` |
| 重み0/1 | `mogura_zero_one_bfs` |
| 非負重み | `mogura_dijkstra` |
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

## 動的計画法

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

## 数学・文字列

- `MoguraComb`は**素数modかつn<mod**が前提。合成数modやLucasの定理は未対応。
- 試し割りの素因数分解は小さな整数の単発処理向け。巨大整数や大量の問い合わせには別の方法が必要。
- 座標圧縮は大小関係を保持し、距離は保持しない。
- Zアルゴリズムは文字列以外の列にも使用可能。パターンと文字列を連結する区切りは入力に現れない値を選ぶ。
- Manacherは奇数・偶数半径を別々に返す。添字の意味はdocstringの例を参照。


## ヒューリスティックを差し替える箇所

[heuristic_recipes.py](../examples/heuristic_recipes.py)が動作例です。評価は大きいほど良い方向に統一し、最小化なら符号を反転します。

焼きなましは`score`、`propose`、`copy_state`を指定。`propose`は元の状態を変更せず新しい候補を返す契約です。差分評価なら候補状態に更新済みのスコアを保持します。固定反復回数と固定seedは再現可能、時間制限では環境の速さにより結果が変わります。

ビームサーチは`expand`、`evaluate`、`is_complete`、必要なら`final_score`と`key`を指定。キーでまとめてよいかは問題ごとに判断します。例えば訪問順を扱う問題では訪問集合だけでなく末尾も必要です。完成解なしは`None`を返すため、合法な初期解等の代替を用意します。

どちらも最適解保証はありません。コールバック1回の処理中には時間制限で強制中断できないため、長い処理を入れないでください。


## 基本操作・提出方法

[Python基本操作メモ](python_notes.md)にはビット演算、メモ化、セグメント木のビット演算設定、対話問題の模擬をまとめています。

[READMEの提出手順](../README.md#提出用に1ファイルへ展開)に従い、必要モジュールを展開してください。`mst`の内部依存`dsu`は自動展開します。
