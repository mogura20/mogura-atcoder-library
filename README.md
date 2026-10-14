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

| モジュール | API | 用途・計算量 |
|---|---|---|
| [basic](mogura/basic.py) | `mogura_compress` | 座標圧縮 O(n log n)、元の値と辞書も返す |
| basic | `mogura_prefix_sum` | 累積和 O(n) |
| basic | `mogura_bisect_int` | 整数二分探索、判定O(log範囲)回 |
| [dsu](mogura/dsu.py) | `MoguraDSU` | Union-Find、併合・判定は償却O(α(n)) |
| [fenwick](mogura/fenwick.py) | `MoguraFenwickTree` | 点加算・区間和・累積和境界 O(log n) |
| [segtree](mogura/segtree.py) | `MoguraSegTree` | 任意の結合的演算、点代入・区間集約・境界探索 O(log n) |
| [lazy_segtree](mogura/lazy_segtree.py) | `MoguraLazySegTree` | 任意の整合する更新作用、区間更新・集約 O(log n) |
| [graph](mogura/graph.py) | `mogura_bfs` | 単一/複数始点、重みなし最短距離 O(V+E) |
| graph | `mogura_dijkstra` | 非負重み、単一/複数始点 O(V+(V+E)log(V+E+2)) |
| graph | `mogura_restore_path` | 親配列からの経路復元 O(経路長) |
| graph | `mogura_toposort` | 有向グラフの順序、閉路ならNone O(V+E) |
| graph | `mogura_scc` | 強連結成分、成分番号はトポロジカル順 O(V+E) |
| [lca](mogura/lca.py) | `MoguraLCA` | 木のLCA・祖先・辺数距離、前処理O(n log n)、問合せO(log n) |
| [number_theory](mogura/number_theory.py) | `mogura_sieve` | 素数列挙 O(N log log N) |
| number_theory | `mogura_factorize` | 単発の素因数分解 O(√N) |
| number_theory | `mogura_extgcd` | 拡張Euclid |
| number_theory | `MoguraComb` | 素数modの組合せ・順列、問合せO(1) |
| [string](mogura/string.py) | `mogura_z_algorithm` | 接頭辞との共通部分長 O(n) |
| string | `mogura_manacher` | 奇数・偶数回文の半径 O(n) |

詳細な引数・戻り値・前提は各クラス/関数のdocstringに記載しています。

## 問題に合わせた変更

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

[lazy_recipes.py](examples/lazy_recipes.py)に3通りの設定があります。

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

### グラフ

- BFS: `graph[v] = [to, ...]`。到達不能の距離は`-1`。
- Dijkstra: `graph[v] = [(to, weight), ...]`。到達不能は`float('inf')`。負辺は不可。
- 無向グラフは両方向の辺を追加。グリッドは必要なら頂点番号を`row * width + column`へ変換する。
- 始点引数に整数または始点リストを指定できる。リストならすべて距離0。
- 経路復元前に距離で到達可能性を判定する。親の`-1`は始点と到達不能の両方に使う。
- LCAは連結な無向木用。一般グラフ・森・重み付き距離にはそのまま使わない。

使用例: [shortest_path.py](examples/shortest_path.py)。例の入力は0始まりです。

### 数学・文字列

- `MoguraComb`は**素数modかつn<mod**が前提。合成数modやLucasの定理は未対応。
- 試し割りの素因数分解は小さな整数の単発処理向け。巨大整数や大量の問い合わせには別の方法が必要。
- 座標圧縮は大小関係を保持し、距離は保持しない。
- Zアルゴリズムは文字列以外の列にも使用可能。パターンと文字列を連結する区切りは入力に現れない値を選ぶ。
- Manacherは奇数・偶数半径を別々に返す。添字の意味はdocstringの例を参照。

## 提出用に1ファイルへ展開

自分の解答を`main.py`へ書き、必要なモジュールだけ指定します。

```sh
git rev-parse HEAD
python3 tools/bundle.py dsu graph --main main.py --source-ref <公開済みの40桁コミットSHA> --output submission.py
python3 submission.py < input.txt
```

`<公開済みの40桁コミットSHA>`は実際の値へ置き換えてください。展開後は`submission.py`を提出します。ツールはAIを呼ばず、指定したソースの連結とmogura importの除去だけを行います。コードの難読化・圧縮はしません。

対応するimportは、トップレベルの`from mogura.graph import mogura_dijkstra`のような形式です。別名import、`*`、`import mogura.graph`、同じ行に別の文を置いたimportには対応せず、エラーにします。必要モジュールの自動推測はしません。

`--source-ref`なしでも開発用に出力できますが、未公開の注意コメントが付き、出典URLは付きません。指定したSHAの公開状況はツールが自動確認しません。

公開済みのexamplesファイルを`--main`へ指定した場合は、そのファイルの出典も出力します。自分の解答を任意のファイルへ書いた場合、その解答は自分で記述する前提です。別のAI生成コードを加える場合は別途、事前公開と参照URLが必要です。

## コンテスト前の公開運用

このコードは生成AIの支援で事前作成しています。[AtCoder生成AI対策ルール（2026年10月14日版）](https://info.atcoder.jp/entry/llm-rules-ja)に沿って、コピーして使うコードを開始前にWeb公開し、使用時に参照URLを添付します。

1. 開始前に変更とテストを終え、GitHubへpushする。
2. ログアウト状態でも実際のファイルを読めることを確認する。ローカルのcommitだけでは公開にならない。
3. その公開版のコミットSHAを控え、同じ版のコードを使う。
4. bundleの`--source-ref`にそのSHAを指定し、提出コードにSourceコメントを残す。
5. 開催中のABC/ARC/AGCではAI補完・AIデバッグ等を使用しない。

参照URLのコメント記載とコミット固定URLは、このリポジトリで採用する運用方法です。AtCoderが特定のコメント形式やGitHub利用を要求しているわけではありません。ライブラリの利用判断・問題への適用は自分で行います。ルール変更時には公式告知を確認してください。

## 検証と性能

```sh
python3 -m unittest discover -s tests -v
```

固定シードのランダム入力と境界ケースで検証します。区間処理はPythonリスト、DijkstraはWarshall–Floyd、SCCは到達可能性、LCAは親を辿る方法、文字列は愚直探索と比較します。深さ10000の鎖状グラフ・木と提出用展開後の実行も確認します。

GitHub ActionsでもCPython 3.9 / 3.13 / PyPy 3.10で実行します。AtCoderの過去問へ自動提出はしていません。Pythonの実行時間とメモリは問題の制約に応じて別途見積もってください。特に汎用遅延セグメント木は関数呼び出しとタプル生成が多く、専用実装より定数倍が大きくなります。

## ライセンスと出典

MIT License。コピー・再配布時には著作権表示とライセンス表示を保持してください。bundle出力にはライセンスをコメントとして付けます。

一般的なアルゴリズムをこのリポジトリ用に実装しました。`mogura`の命名は識別用で、アルゴリズムの新規性を意味しません。第三者コードを今後追加する場合は[THIRD_PARTY.md](THIRD_PARTY.md)へ出典と条件を記録します。
