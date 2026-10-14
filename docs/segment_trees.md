# セグメント木の使い方

まず「点更新か区間更新か」と「何を取得するか」で選びます。配列・添字は0始まり、区間は半開区間`[left, right)`です。`query(1,4)`は添字1,2,3を対象にします。

| 更新 | 取得 | 初期化 |
|---|---|---|
| 1点の代入/加算 | 最小値（RMQ） | `MoguraSegTree(a, mode="min")` |
| 1点の代入/加算 | 和（RSQ） | `MoguraSegTree(a, mode="sum")` |
| 1点の代入/加算 | GCD | `MoguraSegTree(a, mode="gcd")` |
| 1点の代入/加算 | 最大値 | `MoguraSegTree(a, mode="max")` |
| 区間の加算/代入 | 和（RSQ） | `MoguraRangeSegTree(a, mode="sum")` |
| 区間の加算/代入 | 最小値（RMQ） | `MoguraRangeSegTree(a, mode="min")` |
| 区間の加算/代入 | 最大値 | `MoguraRangeSegTree(a, mode="max")` |

構築はO(n)、更新・区間取得はO(log n)、全体取得はO(1)。外部パッケージは不要です。

## 点更新：RMQ・RSQ・GCD

```python
from mogura.segtree import MoguraSegTree

a = [12, 18, 6]
rmq = MoguraSegTree(a, mode="min")
rsq = MoguraSegTree(a, mode="sum")
gcd_tree = MoguraSegTree(a, mode="gcd")
assert rmq.query(0, 3) == 6
assert rsq.query(0, 3) == 36
assert gcd_tree.query(0, 2) == 6

rmq.set(2, 24)              # A[2] = 24
rsq.add(1, 2)               # A[1] += 2
gcd_tree.set(1, 20)         # A[1] = 20
assert rmq.query(0, 3) == 12
assert rsq.query(0, 3) == 38
assert gcd_tree.query(0, 2) == 4
```

この3本の木は別々の配列を管理しています。元の配列`a`や他の木へ変更が伝わることはありません。GCDは負の入力でも非負の値を返します。

| 操作 | 意味 |
|---|---|
| `set(i, x)` | 1点をxへ代入 |
| `add(i, delta)` | 1点にdeltaを加算 |
| `get(i)` | 現在のA[i]を取得 |
| `query(l, r)` | [l,r)の最小値・和・GCD等 |
| `all_query()` | 全体の最小値・和・GCD等 |

点更新の完成した入出力例は[MoguraSegTreeの説明](../mogura/segtree.py)と[実行用ファイル](../examples/segment_tree_queries.py)にあります。MODEを変えるだけで取得方法を切り替えられます。

## 区間更新：加算と代入を混ぜて使う

```python
from mogura.lazy_segtree import MoguraRangeSegTree

seg = MoguraRangeSegTree([1, 2, 3, 4], mode="sum")
seg.range_add(0, 2, 5)      # [6, 7, 3, 4]
assert seg.query(0, 3) == 16
seg.range_assign(1, 4, 0)   # [6, 0, 0, 0]。0の代入も可能
assert seg.query(0, 4) == 6
seg.set(2, 10)             # 点代入も可能
seg.add(0, -1)             # 点加算も可能
assert seg.all_query() == 15
```

`mode="min"`なら区間最小値、`mode="max"`なら区間最大値を返します。更新は同じ`range_add`・`range_assign`です。

```python
from mogura.lazy_segtree import MoguraRangeSegTree

rmq = MoguraRangeSegTree([8, 3, 5], mode="min")
rmq.range_add(0, 2, 4)      # [12, 7, 5]
assert rmq.query(0, 3) == 5
rmq.range_assign(1, 3, 2)   # [12, 2, 2]
assert rmq.all_query() == 2
```

| 操作 | 意味 |
|---|---|
| `range_add(l, r, delta)` | [l,r)の全要素にdeltaを加算 |
| `range_assign(l, r, x)` | [l,r)の全要素をxに代入 |
| `query(l, r)` | [l,r)の和・最小値・最大値 |
| `all_query()` | 全体の集約値 |
| `set(i,x)` / `add(i,d)` / `get(i)` | 1点の操作 |

区間更新の完成した入出力例は[MoguraRangeSegTreeの説明](../mogura/lazy_segtree.py)と[実行用ファイル](../examples/range_segment_tree_queries.py)にあります。

区間加算をRAQ、区間代入をRUQと呼ぶことがあります。`range_assign`は上書き、`range_add`は加算なので区別してください。加算後に代入すれば以前の加算は上書きされ、代入後の加算は代入値に加わります。

## 区間の端点と空区間

入力が1始まりの閉区間`[L,R]`なら、`query(L-1,R)`・`range_add(L-1,R,d)`へ変換します。0始まりの閉区間なら右端に1を足します。

空区間はsum/gcd:0、min:inf、max:-inf。空区間の更新は何もしません。空配列も構築できますが、点操作はできません。

**区間加算とGCDはこの区間更新版では扱いません。** 区間GCDが必要なら点更新版を使います。和・最小値と同じ方法でGCDだけを遅延更新することはできないため、両方必要な問題は別の設計を検討してください。

## 任意の演算が必要なとき

従来の`MoguraSegTree(a, op, identity)`、`prod`、`all_prod`は引き続き使用できます。`query`は`prod`と同じ操作です。演算は結合則と単位元を満たす必要があります。

複雑な更新作用や一次変換は`MoguraLazySegTree`と[lazy_recipes.py](../examples/lazy_recipes.py)を使います。基本用途では`MoguraRangeSegTree`を選べば作用の合成や区間長を自分で設定する必要はありません。

## 提出用に展開する

```sh
python3 tools/bundle.py segtree --main examples/segment_tree_queries.py --source-ref <公開済み40桁SHA> --output submission.py
python3 tools/bundle.py lazy_segtree --main examples/range_segment_tree_queries.py --source-ref <公開済み40桁SHA> --output submission.py
```

実際の解答では`--main`を自分のファイルへ置き換えます。手動コピーなら各ファイル先頭の`# Source:`も残してください。
