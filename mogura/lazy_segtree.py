# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/lazy_segtree.py
"""mogura: 区間加算・区間代入のRMQ/RSQ。基本はMoguraRangeSegTree。"""


class MoguraRangeSegTree:
    """区間更新と区間取得。構築O(n)、操作O(log n)、領域O(n)。

    mode="sum"でRSQ、"min"でRMQ、"max"で区間最大値。省略はsum。
    range_add(l,r,d)は区間にdを加算、range_assign(l,r,x)はxを代入。
    query(l,r)は区間の和/最小値/最大値を返す。全て0始まりの[l,r)。
    0の代入、負の値、加算と代入の混在にも対応。GCDは点更新版を使う。

    入力形式:
        MODE
        N Q
        A_0 ... A_{N-1}
        query_1
        ...
        query_Q
        ※ MODEはsum/min/max。
        ※ queryは「0 L R D」(区間加算)、「1 L R X」(区間代入)、
           「2 L R」(区間取得)。

    入力例:
        sum
        4 5
        1 2 3 4
        2 0 4
        0 0 2 5
        2 0 3
        1 1 4 0
        2 0 4

    出力例:
        10
        16
        6

    読み込み・呼び出し例:
        mode = input().strip()
        n, q = map(int, input().split())
        a = list(map(int, input().split()))
        seg = MoguraRangeSegTree(a, mode=mode)
        for _ in range(q):
            query = list(map(int, input().split()))
            kind, left, right = query[:3]
            if kind == 0:
                seg.range_add(left, right, query[3])
            elif kind == 1:
                seg.range_assign(left, right, query[3])
            else:
                print(seg.query(left, right))

    点操作set(i,x)/add(i,d)/get(i)も可。all_query()は全体の集約値。
    空区間はsum:0、min:inf、max:-inf。空配列も構築可能。
    内部では区間長に合わせて和を更新し、遅延した代入・加算を管理する。
    数値用の実装。任意の作用は下のMoguraLazySegTreeで指定する。
    """

    def __init__(self, values, mode="sum"):
        """数値配列とsum/min/maxから選んだ取得方法で初期化。"""
        if mode not in ("sum", "min", "max"):
            raise ValueError("区間更新のmodeはsum/min/max。GCDは点更新版を使ってください")
        values = list(values)
        self.n = len(values)
        self.mode = mode
        self.identity = 0 if mode == "sum" else float("inf") if mode == "min" else -float("inf")
        self.op = (lambda a, b: a + b) if mode == "sum" else min if mode == "min" else max
        capacity = 4 * max(1, self.n)
        self.data = [self.identity] * capacity
        # Noneは未代入。0は有効な代入値なのでif valueでは判定しない。
        self.lazy_assign = [None] * capacity
        self.lazy_add = [0] * capacity

        def build(node, left, right):
            if right - left == 1:
                self.data[node] = values[left]
                return
            middle = (left + right) // 2
            build(node * 2, left, middle)
            build(node * 2 + 1, middle, right)
            self._pull(node)

        if self.n:
            build(1, 0, self.n)

    def _pull(self, node):
        self.data[node] = self.op(self.data[node * 2], self.data[node * 2 + 1])

    def _assign_node(self, node, length, value):
        self.data[node] = value * length if self.mode == "sum" else value
        self.lazy_assign[node] = value
        self.lazy_add[node] = 0  # 新しい代入は以前の加算を上書きする。

    def _add_node(self, node, length, delta):
        self.data[node] += delta * length if self.mode == "sum" else delta
        if self.lazy_assign[node] is not None:
            self.lazy_assign[node] += delta
        else:
            self.lazy_add[node] += delta

    def _push(self, node, left, right):
        middle = (left + right) // 2
        for child, length in ((node * 2, middle - left), (node * 2 + 1, right - middle)):
            if self.lazy_assign[node] is not None:
                self._assign_node(child, length, self.lazy_assign[node])
            if self.lazy_add[node] != 0:
                self._add_node(child, length, self.lazy_add[node])
        self.lazy_assign[node] = None
        self.lazy_add[node] = 0

    def _update(self, left, right, value, assign):
        assert 0 <= left <= right <= self.n
        if left == right:
            return

        def visit(node, start, end):
            if right <= start or end <= left:
                return
            if left <= start and end <= right:
                if assign:
                    self._assign_node(node, end - start, value)
                else:
                    self._add_node(node, end - start, value)
                return
            self._push(node, start, end)
            middle = (start + end) // 2
            visit(node * 2, start, middle)
            visit(node * 2 + 1, middle, end)
            self._pull(node)

        visit(1, 0, self.n)

    def range_add(self, left, right, delta):
        """[left,right)の全要素にdeltaを加算。空区間は何もしない。"""
        self._update(left, right, delta, assign=False)

    def range_assign(self, left, right, value):
        """[left,right)の全要素をvalueに代入。0の代入も有効。"""
        self._update(left, right, value, assign=True)

    def query(self, left, right):
        """[left,right)の和/最小値/最大値を返す。空区間は単位元。"""
        assert 0 <= left <= right <= self.n
        if left == right:
            return self.identity

        def visit(node, start, end):
            if right <= start or end <= left:
                return self.identity
            if left <= start and end <= right:
                return self.data[node]
            self._push(node, start, end)
            middle = (start + end) // 2
            return self.op(visit(node * 2, start, middle), visit(node * 2 + 1, middle, end))

        return visit(1, 0, self.n)

    def all_query(self):
        """全体の集約値をO(1)で返す。空配列は単位元。"""
        return self.data[1]

    def set(self, index, value):
        """A[index]=value。点代入。"""
        assert 0 <= index < self.n
        self.range_assign(index, index + 1, value)

    def add(self, index, delta):
        """A[index]+=delta。点加算。"""
        assert 0 <= index < self.n
        self.range_add(index, index + 1, delta)

    def get(self, index):
        """現在のA[index]を返す。O(log n)。"""
        assert 0 <= index < self.n
        return self.query(index, index + 1)


class MoguraLazySegTree:
    """op, identity, mapping, composition, identity_actionを指定。

    この入出力は使用方法を示す例。クラス自体は標準入力を読みません。
    区間加算・区間最小値の設定。添字は0始まり、区間は[L,R)。

    入力形式:
        N
        A_0 ... A_{N-1}
        L R D

    入力例:
        2
        2 5
        0 1 10

    出力例:
        5

    読み込み・呼び出し例:
        n = int(input())
        a = list(map(int, input().split()))
        seg = MoguraLazySegTree(a, min, float("inf"),
                                lambda delta, value: value + delta,
                                lambda new, old: new + old, 0)
        left, right, delta = map(int, input().split())
        seg.apply(left, right, delta)
        print(seg.all_prod())

    mapping(action, value): 区間集約値に更新を作用させた値。
    composition(new, old): oldを先に、newを後に作用させる合成。
    mapping(f, op(a,b)) == op(mapping(f,a), mapping(f,b))が必要。
    mapping(f, identity) == identity、作用の結合則・単位元も必要。
    値・作用は不変なものを使う。タプルで区間長を持つと和にも対応できる。
    構築O(n)、apply/prod/set/getはO(log n)、領域O(n)。
    再帰は木の高さO(log n)だけ使用（グラフの深い再帰とは異なる）。
    """

    def __init__(self, values, op, identity, mapping, composition, identity_action):
        """初期配列・集約演算・更新作用・作用の合成を指定して構築する。"""
        values = list(values)
        self.n = len(values)
        self.size = 1 << max(0, (self.n - 1).bit_length())
        self.op, self.identity = op, identity
        self.mapping, self.composition = mapping, composition
        self.identity_action = identity_action
        self.data = [identity] * (2 * self.size)
        self.lazy = [identity_action] * self.size
        self.data[self.size:self.size + self.n] = values
        for index in range(self.size - 1, 0, -1):
            self._pull(index)

    def _pull(self, index):
        self.data[index] = self.op(self.data[2 * index], self.data[2 * index + 1])

    def _apply_node(self, index, action):
        self.data[index] = self.mapping(action, self.data[index])
        if index < self.size:
            self.lazy[index] = self.composition(action, self.lazy[index])

    def _push(self, index):
        # 単位作用もそのまま渡すため、作用の等値比較は不要。
        self._apply_node(2 * index, self.lazy[index])
        self._apply_node(2 * index + 1, self.lazy[index])
        self.lazy[index] = self.identity_action

    def apply(self, left, right, action):
        """[left,right)へ作用actionを適用する。空区間は何もしない。"""
        assert 0 <= left <= right <= self.n

        def visit(index, start, end):
            if right <= start or end <= left:
                return
            if left <= start and end <= right:
                self._apply_node(index, action)
                return
            self._push(index)
            middle = (start + end) // 2
            visit(2 * index, start, middle)
            visit(2 * index + 1, middle, end)
            self._pull(index)

        visit(1, 0, self.size)

    def prod(self, left, right):
        """半開区間[left,right)を指定した演算で集約する。"""
        assert 0 <= left <= right <= self.n

        def visit(index, start, end):
            if right <= start or end <= left:
                return self.identity
            if left <= start and end <= right:
                return self.data[index]
            self._push(index)
            middle = (start + end) // 2
            return self.op(visit(2 * index, start, middle),
                           visit(2 * index + 1, middle, end))

        return visit(1, 0, self.size)

    def all_prod(self):
        """全要素の集約値を返す。"""
        return self.data[1]

    def get(self, index):
        """添字indexの要素を返す。"""
        assert 0 <= index < self.n
        return self.prod(index, index + 1)

    def set(self, index, value):
        """添字indexの要素をvalueに代入する。"""
        assert 0 <= index < self.n

        def visit(node, start, end):
            if end - start == 1:
                self.data[node] = value
                return
            self._push(node)
            middle = (start + end) // 2
            if index < middle:
                visit(2 * node, start, middle)
            else:
                visit(2 * node + 1, middle, end)
            self._pull(node)

        visit(1, 0, self.size)
