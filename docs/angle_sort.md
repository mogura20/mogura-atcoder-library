# 浮動小数点を使わない偏角ソート

[mogura_angle_sort](../mogura/angle_sort.py)は、整数座標を外積・内積だけで比較します。`atan2`・角度への変換・平方根・除算は使いません。原点付近、座標軸上、ほぼ同じ角度、大きな座標でも丸め誤差なしで順序を決めます。

## 基本の使い方

```python
from mogura.angle_sort import mogura_angle_sort

points = [(0, -1), (-1, 0), (0, 1), (1, 0)]
ordered = mogura_angle_sort(points)
assert ordered == [(1, 0), (0, 1), (-1, 0), (0, -1)]
assert points == [(0, -1), (-1, 0), (0, 1), (1, 0)]
```

正のx軸を先頭に、反時計回りに並べます。元のリストは変更せず、新しいリストを返します。generatorなどのiterableも使えます。AtCoder形式の入出力例は関数直下の1箇所にまとめ、[実行用ファイル](../examples/angle_sort_points.py)も用意しています。

## 中心・開始方向・回転方向

| 引数 | 既定値 | 意味 |
|---|---|---|
| `origin` | `(0,0)` | ソートの中心となる座標 |
| `start` | `(1,0)` | 最初の方向。非零の方向ベクトル |
| `clockwise` | `False` | Trueならstartから時計回り |

```python
from mogura.angle_sort import mogura_angle_sort

points = [(11, 10), (10, 11), (9, 10), (10, 9)]
ordered = mogura_angle_sort(points, origin=(10, 10), start=(0, 1), clockwise=True)
assert ordered == [(10, 11), (11, 10), (10, 9), (9, 10)]
```

`start=(0,1)`は中心から上向きという意味です。絶対座標を指定する引数ではありません。例えば中心`(10,10)`から点`(11,11)`へ向かう方向を先頭にしたければ`start=(1,1)`を指定します。

## 同じ方向・中心と一致する点

`(1,1)`と`(2,2)`のように方向が同じ点の順序を選べます。

| 引数 | 設定 | 意味 |
|---|---|---|
| `tie` | `"stable"`（既定） | 入力順を維持 |
| `tie` | `"near"` | 中心から近い順 |
| `tie` | `"far"` | 中心から遠い順 |
| `zero` | `"last"`（既定） | 中心と一致する点を末尾へ |
| `zero` | `"first"` | 中心と一致する点を先頭へ |
| `zero` | `"error"` | 中心と一致する点があればValueError |

```python
from mogura.angle_sort import mogura_angle_sort

points = [(2, 2), (1, 1), (0, 0), (-1, -1)]
assert mogura_angle_sort(points, tie="near") == [(1, 1), (2, 2), (-1, -1), (0, 0)]
assert mogura_angle_sort(points, tie="far", zero="first") == [(0, 0), (2, 2), (1, 1), (-1, -1)]
```

距離は中心からの距離の二乗で比較します。同方向かつ同距離の点は入力順です。中心と一致する点には偏角がないため別枠で扱い、その中では入力順を保ちます。反対方向は別の角度であり、同方向の扱いにはなりません。

## IDや付随データを残す

```python
from mogura.angle_sort import mogura_angle_sort

# (ID, x, y)の例。座標を取り出す方法をkeyで指定する。
records = [(100, 0, 1), (200, 1, 0), (300, -1, 0)]
ordered = mogura_angle_sort(records, key=lambda item: (item[1], item[2]))
assert [item[0] for item in ordered] == [200, 100, 300]
```

`key`は各要素につき1回だけ呼びます。元の要素をそのまま返すので、辞書やオブジェクトに付けた情報も保持できます。元の要素同士が比較できる必要はありません。

## 整数だけで比較できる理由

まず開始方向を境に前半・後半へ分けます。同じ半平面にある二つの方向は、外積の符号で順序を決めます。この分割により、外積が0となる同方向と反対方向を区別でき、角度の一周の切れ目も一定になります。`start`が任意の整数ベクトルでも、内積と外積で分割できます。

座標・中心・開始方向は整数を指定してください。`1.0`も含めfloatはTypeErrorにします。既にfloatへ変換して失った精度は復元できないので、入力時から`map(int, ...)`を使います。Pythonの整数へ変換してから積を取り、固定長整数の中間積のオーバーフローも避けます。

ソートはO(n log n)、追加領域はO(n)。この計算量は整数演算をO(1)とした目安で、整数の桁数が増えるほど演算コストも増えます。

## 提出方法

```sh
python3 tools/bundle.py angle_sort --main examples/angle_sort_points.py --source-ref <公開済み40桁SHA> --output submission.py
```

自分の解答では`--main`を置き換えます。手動コピーならファイル先頭の`# Source:`も残してください。中心やソート順の選択は、問題に応じて自分で決めて使います。
