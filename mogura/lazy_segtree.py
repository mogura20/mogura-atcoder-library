# Source: https://github.com/mogura20/mogura-atcoder-library/blob/7d3ec971580db281f0653bafa17523fe1b75bcb4/mogura/lazy_segtree.py
"""mogura library: 演算と更新作用を差し替えられる遅延セグメント木。"""


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
