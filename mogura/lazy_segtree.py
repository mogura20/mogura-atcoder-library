"""mogura library: 演算と更新作用を差し替えられる遅延セグメント木。"""


class MoguraLazySegTree:
    """op, identity, mapping, composition, identity_actionを指定。

    mapping(action, value): 区間集約値に更新を作用させた値。
    composition(new, old): oldを先に、newを後に作用させる合成。
    mapping(f, op(a,b)) == op(mapping(f,a), mapping(f,b))が必要。
    mapping(f, identity) == identity、作用の結合則・単位元も必要。
    値・作用は不変なものを使う。タプルで区間長を持つと和にも対応できる。
    構築O(n)、apply/prod/set/getはO(log n)、領域O(n)。
    再帰は木の高さO(log n)だけ使用（グラフの深い再帰とは異なる）。
    """

    def __init__(self, values, op, identity, mapping, composition, identity_action):
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
        return self.data[1]

    def get(self, index):
        assert 0 <= index < self.n
        return self.prod(index, index + 1)

    def set(self, index, value):
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
