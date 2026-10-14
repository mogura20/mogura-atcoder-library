# Source: https://github.com/mogura20/mogura-atcoder-library/blob/0722a9a6b352a27e43e3ee2aa287ebf1e04f43ba/mogura/lca.py
"""mogura library: 無向・重みなし木のダブリングLCA。"""


class MoguraLCA:
    """前処理O(n log n)、問い合わせO(log n)、領域O(n log n)。

    この入出力は使用方法を示す例。クラス自体は標準入力を読みません。
    無向木。頂点は1始まり、頂点1を根とする。距離は辺数。

    入力形式:
        N
        u_1 v_1
        ...
        u_{N-1} v_{N-1}
        A B

    入力例:
        3
        1 2
        2 3
        1 3

    出力例:
        2

    読み込み・呼び出し例:
        n = int(input())
        graph = [[] for _ in range(n)]
        for _ in range(n - 1):
            u, v = map(int, input().split())
            graph[u - 1].append(v - 1)
            graph[v - 1].append(u - 1)
        tree = MoguraLCA(graph)
        a, b = map(int, input().split())
        print(tree.distance(a - 1, b - 1))

    graphは連結な無向木の隣接リスト。rootで根を指定する。
    空の木・非連結入力はValueError。閉路検査は省略するため木を渡すこと。
    使用例: tree=MoguraLCA([[1],[0,2],[1]]); tree.distance(0,2) -> 2
    """

    def __init__(self, graph, root=0):
        """連結な無向木をrootで根付けし、祖先の表を構築する。"""
        n = len(graph)
        if n == 0:
            raise ValueError("空の木にはLCAを構築できません")
        assert 0 <= root < n
        self.n = n
        self.depth = [-1] * n
        self.depth[root] = 0
        parent = [-1] * n
        stack = [root]
        while stack:
            vertex = stack.pop()
            for to in graph[vertex]:
                if self.depth[to] == -1:
                    self.depth[to] = self.depth[vertex] + 1
                    parent[to] = vertex
                    stack.append(to)
        if -1 in self.depth:
            raise ValueError("連結な木を渡してください")
        self.up = [parent]
        for _ in range(1, n.bit_length()):
            previous = self.up[-1]
            self.up.append([previous[p] if p != -1 else -1 for p in previous])

    def ancestor(self, vertex, steps):
        """steps個上の祖先。根を越えたら-1。stepsは非負。"""
        assert 0 <= vertex < self.n and steps >= 0
        if steps > self.depth[vertex]:
            return -1
        bit = 0
        while steps:
            if steps & 1:
                vertex = self.up[bit][vertex]
            steps >>= 1
            bit += 1
        return vertex

    def lca(self, a, b):
        """頂点a,bの最小共通祖先を返す。"""
        assert 0 <= a < self.n and 0 <= b < self.n
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        a = self.ancestor(a, self.depth[a] - self.depth[b])
        if a == b:
            return a
        for parents in reversed(self.up):
            if parents[a] != parents[b]:
                a, b = parents[a], parents[b]
        return self.up[0][a]

    def distance(self, a, b):
        """a,b間の辺数（重み付き距離ではない）。"""
        return self.depth[a] + self.depth[b] - 2 * self.depth[self.lca(a, b)]
