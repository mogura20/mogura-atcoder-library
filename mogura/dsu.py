# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/dsu.py
"""mogura library: 経路圧縮とサイズによる併合。頂点番号は0始まり。"""


class MoguraDSU:
    """連結成分を管理する。merge/unite/same/sizeは償却O(α(n))、領域O(n)。

    この入出力は使用方法を示す例。クラス自体は標準入力を読みません。
    頂点は1始まり。0は併合、1は連結判定、2は成分サイズの問合せ。

    入力形式:
        N Q
        query_1
        ...
        query_Q
        ※ queryは「0 A B」「1 A B」または「2 V」

    入力例:
        5 6
        0 1 2
        1 1 2
        1 1 3
        0 2 3
        2 1
        2 4

    出力例:
        Yes
        No
        3
        1

    読み込み・呼び出し例:
        n, q = map(int, input().split())
        uf = MoguraDSU(n)
        for _ in range(q):
            query = list(map(int, input().split()))
            if query[0] == 0:
                uf.unite(query[1] - 1, query[2] - 1)
            elif query[0] == 1:
                connected = uf.same(query[1] - 1, query[2] - 1)
                print("Yes" if connected else "No")
            else:
                print(uf.size(query[1] - 1))

    使用例: uf = MoguraDSU(5); uf.merge(0, 1); uf.same(0, 1) -> True
    辺の削除には対応しない。mergeの戻り値は併合後の代表頂点。
    """

    def __init__(self, n):
        """n個の頂点をそれぞれ独立した成分として初期化する。"""
        if n < 0:
            raise ValueError("nは非負で指定してください")
        self.n = n
        self.parent_or_size = [-1] * n
        self.component_count = n

    def leader(self, vertex):
        """頂点vertexが属する成分の代表頂点を返す。"""
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
        """併合後の代表頂点を返す。同じ成分でも代表を返す。

        代表は0の場合もあるため、戻り値をifの成功判定に使わないこと。
        新しく併合できたか判定する場合はuniteを使う。
        """
        a, b = self.leader(a), self.leader(b)
        if a == b:
            return a
        if self.parent_or_size[a] > self.parent_or_size[b]:
            a, b = b, a
        self.parent_or_size[a] += self.parent_or_size[b]
        self.parent_or_size[b] = a
        self.component_count -= 1
        return a

    def unite(self, a, b):
        """新しく併合したらTrue、すでに同じ成分ならFalse。償却O(α(n))。

        自己併合もFalse。閉路検出・Kruskal等でif uf.unite(a,b)と書ける。
        mergeと併用可能。Falseの場合も経路圧縮は行うが成分は変わらない。
        """
        before = self.component_count
        self.merge(a, b)
        return self.component_count < before

    def roots(self):
        """現在の代表頂点を頂点番号の昇順で返す。O(n)、空なら[]。

        代表は成分内の最小番号とは限らず、後の併合で変わり得る。
        戻り値は呼び出し時点の一覧。全頂点を走査するので大量の問合せに注意。
        """
        return [vertex for vertex, value in enumerate(self.parent_or_size) if value < 0]

    def group_sizes(self):
        """各成分のサイズをroots()と同じ代表番号順で返す。O(n)、空なら[]。

        例: sizes=uf.group_sizes(); largest=max(sizes,default=0)。
        サイズの昇順ではない。全メンバーが不要な場合、groups()より軽い。
        """
        return [-value for value in self.parent_or_size if value < 0]

    def same(self, a, b):
        """頂点a,bが同じ成分かをboolで返す。"""
        return self.leader(a) == self.leader(b)

    def size(self, vertex):
        """頂点vertexが属する成分の頂点数を返す。"""
        return -self.parent_or_size[self.leader(vertex)]

    def groups(self):
        """全成分をリストで返す。O(n α(n))。空集合なら[]。"""
        groups = {}
        for vertex in range(self.n):
            groups.setdefault(self.leader(vertex), []).append(vertex)
        return list(groups.values())
