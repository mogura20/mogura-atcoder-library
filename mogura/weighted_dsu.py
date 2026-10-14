"""mogura: 差の制約 potential[b] - potential[a] = delta を管理する。"""


class MoguraWeightedDSU:
    """加法的な重み付きUnion-Find。操作は償却O(α(n))、領域O(n)。

    merge(a,b,delta)でpotential[b]-potential[a]=deltaを追加する。
    矛盾がなければTrue（既知の同じ制約もTrue）、矛盾ならFalse。
    diff(a,b)はpotential[b]-potential[a]、非連結ならNone。
    元メモのdiffの符号とは異なるため、移行時はこの定義に合わせること。
    """

    def __init__(self, n):
        if n < 0:
            raise ValueError('nは非負')
        self.n = n
        self.parent_or_size = [-1] * n
        # 根なら0、それ以外は自身のpotential - 親のpotential。
        self.weight = [0] * n
        self.component_count = n

    def leader(self, vertex):
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
        return self.leader(a) == self.leader(b)

    def diff(self, a, b):
        if not self.same(a, b):
            return None
        return self.weight[b] - self.weight[a]

    def size(self, vertex):
        return -self.parent_or_size[self.leader(vertex)]
