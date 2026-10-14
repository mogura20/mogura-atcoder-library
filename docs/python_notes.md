# Pythonの基本操作とテンプレート

Desktopの基本操作メモを用途別に整理しました。標準機能で短く書けるものは、専用クラスを増やさずここへまとめています。

## 整数と数論

```python
from math import gcd, lcm, comb, perm
assert gcd(12, 18) == 6
assert lcm(12, 18) == 36
assert comb(5, 2) == 10
assert perm(5, 2) == 20
assert pow(3, 4, 7) == 4
```

整数切り捨ては`a // b`（負の無限大方向）、切り上げは`mogura_ceil_div(a,b)`。大きな整数を`a/b`でfloatにしてから丸めると精度を失う可能性があります。

有限小数を10進の意味で計算する例は`Decimal('0.1') + Decimal('0.2')`。Decimalはfloatからではなく文字列から作ります。

## ビットと基数

- `1 << i`: 第iビット。
- `(mask >> i) & 1`: 選択されているか。
- `mask | (1 << i)`: 追加。
- `mask & ~(1 << i)`: 削除。
- `range(1 << n)`: 全ての部分集合。
- `bin(x)`、`format(x,'b')`、`int('101',2)`: 表現と変換。
- 3値等は`mogura_states(n,3)`、桁列は`mogura_base_digits(x,3)`。

Python整数は必要に応じて桁数が増えます。ただし大きな整数の演算は定数時間ではありません。

## 順列・組合せ

`itertools.permutations`、`combinations`、`combinations_with_replacement`、`product`を使います。重複なし順列は`mogura_distinct_permutations`。全件をlistにするとメモリも出力数に比例します。

`mogura_team_sizes(N,T)`は各チームの人数配分を列挙します。誰をどこへ配置するかの列挙や集合分割の個数ではありません。

## キュー・ヒープ・配列

- `collections.deque`: BFS等、両端の追加/削除。
- `defaultdict(list)`: キーごとのリスト。
- `heapq.heappush` / `heappop`: 最小値の追加/取出し。
- 最大値なら符号を反転。同点のタプルでは次の要素が比較されるため、比較できない状態を入れるなら連番を添える。
- `heapreplace`は空ヒープには不可。`heappushpop`は空にも使用可能。
- `enumerate(a)`は添字と値、`zip(a,b)`は短い列の長さまで対応付け。
- 平坦化は`[value for row in matrix for value in row]`。
- `bisect_left`の検索はO(log n)、リストの途中挿入はO(n)。

元メモのSortedList/SortedSet/SortedDictは外部パッケージの機能です。このライブラリは外部依存なしです。頻度と順序統計なら座標圧縮＋Fenwick Treeも候補。外部パッケージの有無は提出環境で個別に確認します。

## 集合

`a | b`は和、`a & b`は共通部分、`a - b`は差、`a ^ b`は対称差、`a <= b`は部分集合。存在しなくても削除したい場合は`discard`。

## メモ化と再帰

```python
from functools import cache

@cache
def mogura_split_cost(n):
    # 遷移と終了条件は問題ごとに変更する。
    if n <= 1:
        return 0
    return n + mogura_split_cost(n // 2) + mogura_split_cost((n + 1) // 2)
```

キャッシュの引数はhash可能である必要があります。`cache_clear()`で初期化でき、ケース間でグローバル状態が違うなら結果を混在させません。再帰上限を大幅に上げてもスタック等の制約は消えません。深いグラフ探索は反復DFSを使います。

Fibonacciは再帰を使わず、2つの値だけ保持できます。

```python
def mogura_fibonacci(n):
    if n < 0:
        raise ValueError('nは非負')
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

assert mogura_fibonacci(0) == 0
assert mogura_fibonacci(10) == 55
```

## セグメント木のビット演算設定

```python
from mogura.segtree import MoguraSegTree
values = [3, 5, 6]
xor_tree = MoguraSegTree(values, lambda a, b: a ^ b, 0)
or_tree = MoguraSegTree(values, lambda a, b: a | b, 0)
# 非負値でbit_width未満のビットだけ使うという前提。
bit_width = 60
and_tree = MoguraSegTree(values, lambda a, b: a & b, (1 << bit_width) - 1)
assert xor_tree.prod(0, 3) == 0
assert or_tree.prod(0, 3) == 7
assert and_tree.prod(0, 2) == 1
```

## 対話問題のローカル模擬

```python
from mogura.interactive import MoguraInteractiveIO
hidden = '0111'
io = MoguraInteractiveIO(mock_query=lambda index: hidden[index])
assert io.ask(1) == '1'
io.answer(0)
assert io.last_answer == (0,)
```

本番は`mock_query`を省略。問合せ形式・頂点番号・応答の意味・上限は問題に合わせます。デバッグ出力はstderrへ、標準出力に混ぜません。

## 選択の早見表

| 状況 | 候補 | 確認する条件 |
|---|---|---|
| 更新なしで区間和 | 累積和 / 2次元累積和 | 区間の定義 |
| 点更新と区間和 | Fenwick Tree | 足し算で表せるか |
| 一般の区間集約 | セグメント木 | 結合則・単位元 |
| 区間一括更新 | 遅延セグメント木 | 更新作用と合成の整合性 |
| 連続区間の条件 | しゃくとり | 条件の単調性 |
| 答えの決め打ち | 二分探索 | 可否判定の単調性 |
| 少数の要素の選択 | ビット全探索/DP | 2^nに加え遷移数・領域 |
| 増加部分列 | LIS | 狭義増加か非減少か |
| 木の子から集約 | DFS帰りがけ順＋木DP | 木であること |
| 文字列の一致 | Z検索 / Trie / ハッシュ | ハッシュの衝突を許容できるか |

元メモの「何秒ならNはいくつまで」「ABCの何番ならこの手法」は環境・実装・出題で変わるため保証としては転載していません。状態数、演算数、メモリ、実測から判断します。
