"""mogura library: 経路圧縮とサイズによる併合。頂点番号は0始まり。"""


class MoguraDSU:
    """連結成分を管理する。merge/same/sizeは償却O(α(n))、領域O(n)。

    使用例: uf = MoguraDSU(5); uf.merge(0, 1); uf.same(0, 1) -> True
    辺の削除には対応しない。mergeの戻り値は併合後の代表頂点。
    """

    def __init__(self, n):
        if n < 0:
            raise ValueError("nは非負で指定してください")
        self.n = n
        self.parent_or_size = [-1] * n
        self.component_count = n

    def leader(self, vertex):
        assert 0 <= vertex < self.n
        root = vertex
        while self.parent_or_size[root] >= 0:
            root = self.parent_or_size[root]
        while vertex != root:
            parent = self.parent_or_size[vertex]
            self.parent_or_size[vertex] = root
            vertex = parent
        return root

    def merge(self, a, b):
        a, b = self.leader(a), self.leader(b)
        if a == b:
            return a
        if self.parent_or_size[a] > self.parent_or_size[b]:
            a, b = b, a
        self.parent_or_size[a] += self.parent_or_size[b]
        self.parent_or_size[b] = a
        self.component_count -= 1
        return a

    def same(self, a, b):
        return self.leader(a) == self.leader(b)

    def size(self, vertex):
        return -self.parent_or_size[self.leader(vertex)]

    def groups(self):
        """全成分をリストで返す。O(n α(n))。空集合なら[]。"""
        groups = {}
        for vertex in range(self.n):
            groups.setdefault(self.leader(vertex), []).append(vertex)
        return list(groups.values())
