# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/weighted_dsu.py
"""mogura: 差の制約 potential[b] - potential[a] = delta を管理する。"""


class MoguraWeightedDSU:
    """加法的な重み付きUnion-Find。操作は償却O(α(n))、領域O(n)。

    この入出力は使用方法を示す例。クラス自体は標準入力を読みません。
    頂点は1始まり。制約はpotential[b]-potential[a]=d。差はpotential[B]-potential[A]。非連結ならUNKNOWN。

    入力形式:
        N M
        a_1 b_1 d_1
        ...
        a_M b_M d_M
        A B

    入力例:
        3 1
        1 2 5
        1 2

    出力例:
        5

    読み込み・呼び出し例:
        n, m = map(int, input().split())
        uf = MoguraWeightedDSU(n)
        for _ in range(m):
            a, b, delta = map(int, input().split())
            uf.merge(a - 1, b - 1, delta)
        a, b = map(int, input().split())
        difference = uf.diff(a - 1, b - 1)
        print("UNKNOWN" if difference is None else difference)

    merge(a,b,delta)でpotential[b]-potential[a]=deltaを追加する。
    矛盾がなければTrue（既知の同じ制約もTrue）、矛盾ならFalse。
    diff(a,b)はpotential[b]-potential[a]、非連結ならNone。
    元メモのdiffの符号とは異なるため、移行時はこの定義に合わせること。
    """

    def __init__(self, n):
        """n個の頂点と、親との差の重みを初期化する。"""
        if n < 0:
            raise ValueError('nは非負')
        self.n = n
        self.parent_or_size = [-1] * n
        # 根なら0、それ以外は自身のpotential - 親のpotential。
        self.weight = [0] * n
        self.component_count = n

    def leader(self, vertex):
        """頂点vertexが属する成分の代表頂点を返す。"""
        assert 0 <= vertex < self.n
        path = []
        current = vertex
        while self.parent_or_size[current] >= 0:
            path.append(current)
            current = self.parent_or_size[current]
        total = 0
        for node in reversed(path):
            total += self.weight[node]
            self.parent_or_size[node] = current
            self.weight[node] = total
        return current

    def merge(self, a, b, delta):
        """potential[b]-potential[a]=deltaを追加する。矛盾がなければTrue。"""
        root_a, root_b = self.leader(a), self.leader(b)
        if root_a == root_b:
            return self.weight[b] - self.weight[a] == delta
        root_delta = delta + self.weight[a] - self.weight[b]
        if self.parent_or_size[root_a] > self.parent_or_size[root_b]:
            root_a, root_b = root_b, root_a
            root_delta = -root_delta
        self.parent_or_size[root_a] += self.parent_or_size[root_b]
        self.parent_or_size[root_b] = root_a
        self.weight[root_b] = root_delta
        self.component_count -= 1
        return True

    def same(self, a, b):
        """頂点a,bが同じ成分かをboolで返す。"""
        return self.leader(a) == self.leader(b)

    def diff(self, a, b):
        """potential[b]-potential[a]を返す。非連結ならNone。"""
        if not self.same(a, b):
            return None
        return self.weight[b] - self.weight[a]

    def size(self, vertex):
        """頂点vertexが属する成分の頂点数を返す。"""
        return -self.parent_or_size[self.leader(vertex)]
