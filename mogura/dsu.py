"""mogura library: 経路圧縮とサイズによる併合。頂点番号は0始まり。"""


class MoguraDSU:
    """連結成分を管理する。merge/unite/same/sizeは償却O(α(n))、領域O(n)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    辺のないN頂点を作り、成分数を出力する。

    入力形式:
        N

    入力例:
        3

    出力例:
        3

    読み込み・呼び出し例:
        n = int(input())
        uf = MoguraDSU(n)
        print(uf.component_count)

    使用例: uf = MoguraDSU(5); uf.merge(0, 1); uf.same(0, 1) -> True
    辺の削除には対応しない。mergeの戻り値は併合後の代表頂点。
    """

    def __init__(self, n):
        """n個の頂点をそれぞれ独立した成分として初期化する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        辺のないN頂点を作り、成分数を出力する。

        入力形式:
            N

        入力例:
            3

        出力例:
            3

        読み込み・呼び出し例:
            n = int(input())
            uf = MoguraDSU(n)
            print(uf.component_count)
        """
        if n < 0:
            raise ValueError("nは非負で指定してください")
        self.n = n
        self.parent_or_size = [-1] * n
        self.component_count = n

    def leader(self, vertex):
        """頂点vertexが属する成分の代表頂点を返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。代表頂点も1始まりで表示。最小番号を保証するAPIではない。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M
            V

        入力例:
            3 1
            1 2
            2

        出力例:
            1

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            vertex = int(input())
            print(uf.leader(vertex - 1) + 1)
        """
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

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        頂点は1始まり。併合後の代表を1始まりで表示。

        入力形式:
            N
            A B

        入力例:
            3
            1 2

        出力例:
            1

        読み込み・呼び出し例:
            n = int(input())
            a, b = map(int, input().split())
            uf = MoguraDSU(n)
            print(uf.merge(a - 1, b - 1) + 1)

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

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        頂点は1始まり。新しく併合できたらYes、同じ成分ならNo。

        入力形式:
            N
            A B

        入力例:
            3
            1 2

        出力例:
            Yes

        読み込み・呼び出し例:
            n = int(input())
            a, b = map(int, input().split())
            uf = MoguraDSU(n)
            print("Yes" if uf.unite(a - 1, b - 1) else "No")

        自己併合もFalse。閉路検出・Kruskal等でif uf.unite(a,b)と書ける。
        mergeと併用可能。Falseの場合も経路圧縮は行うが成分は変わらない。
        """
        before = self.component_count
        self.merge(a, b)
        return self.component_count < before

    def roots(self):
        """現在の代表頂点を頂点番号の昇順で返す。O(n)、空なら[]。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。現在の代表番号を1始まりで出力。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M

        入力例:
            3 1
            1 2

        出力例:
            1 3

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            print(*(v + 1 for v in uf.roots()))

        代表は成分内の最小番号とは限らず、後の併合で変わり得る。
        戻り値は呼び出し時点の一覧。全頂点を走査するので大量の問合せに注意。
        """
        return [vertex for vertex, value in enumerate(self.parent_or_size) if value < 0]

    def group_sizes(self):
        """各成分のサイズをroots()と同じ代表番号順で返す。O(n)、空なら[]。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。代表番号順のサイズ一覧。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M

        入力例:
            3 1
            1 2

        出力例:
            2 1

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            print(*uf.group_sizes())

        例: sizes=uf.group_sizes(); largest=max(sizes,default=0)。
        サイズの昇順ではない。全メンバーが不要な場合、groups()より軽い。
        """
        return [-value for value in self.parent_or_size if value < 0]

    def same(self, a, b):
        """頂点a,bが同じ成分かをboolで返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M
            A B

        入力例:
            3 1
            1 2
            1 2

        出力例:
            Yes

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            a, b = map(int, input().split())
            print("Yes" if uf.same(a - 1, b - 1) else "No")
        """
        return self.leader(a) == self.leader(b)

    def size(self, vertex):
        """頂点vertexが属する成分の頂点数を返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M
            V

        入力例:
            3 1
            1 2
            2

        出力例:
            2

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            vertex = int(input())
            print(uf.size(vertex - 1))
        """
        return -self.parent_or_size[self.leader(vertex)]

    def groups(self):
        """全成分をリストで返す。O(n α(n))。空集合なら[]。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        入力頂点は1始まり。成分ごとに1行、頂点は1始まりで表示。

        入力形式:
            N M
            u_1 v_1
            ...
            u_M v_M

        入力例:
            3 1
            1 2

        出力例:
            1 2
            3

        読み込み・呼び出し例:
            n, m = map(int, input().split())
            uf = MoguraDSU(n)
            for _ in range(m):
                u, v = map(int, input().split())
                uf.unite(u - 1, v - 1)
            for group in uf.groups():
                print(*(v + 1 for v in group))
        """
        groups = {}
        for vertex in range(self.n):
            groups.setdefault(self.leader(vertex), []).append(vertex)
        return list(groups.values())
