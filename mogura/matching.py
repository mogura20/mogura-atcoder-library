# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/mogura/matching.py
"""mogura: 左右の頂点番号を別々に扱う最大二部マッチング。"""

from collections import deque


class MoguraBipartiteMatching:
    """BFS増加路法。深い再帰なし。最大化O(L*(L+R+E))、領域O(L+R+E)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    左右の頂点数を指定。まだ辺がないため最大マッチング数は0。

    入力形式:
        L R

    入力例:
        2 3

    出力例:
        0

    読み込み・呼び出し例:
        left_size, right_size = map(int, input().split())
        matching = MoguraBipartiteMatching(left_size, right_size)
        print(matching.maximum_matching())

    左0..left_size-1、右0..right_size-1。add_edge(left,right)で辺追加。
    maximum_matching()の戻り値は総ペア数。繰り返し呼び出し・辺追加も可。
    pairs()は現在の(left,right)一覧。未マッチはmatch_left/rightで-1。
    元ファイルのHopcroft–Karpとは実装・計算量が異なる。大規模密グラフに注意。
    """

    def __init__(self, left_size, right_size):
        """左右それぞれの頂点数を指定し、辺のない二部グラフを作る。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        左右の頂点数を指定。まだ辺がないため最大マッチング数は0。

        入力形式:
            L R

        入力例:
            2 3

        出力例:
            0

        読み込み・呼び出し例:
            left_size, right_size = map(int, input().split())
            matching = MoguraBipartiteMatching(left_size, right_size)
            print(matching.maximum_matching())
        """
        if min(left_size, right_size) < 0:
            raise ValueError('頂点数は非負')
        self.left_size, self.right_size = left_size, right_size
        self.graph = [[] for _ in range(left_size)]
        self.match_left, self.match_right = [-1] * left_size, [-1] * right_size

    def add_edge(self, left, right):
        """左頂点leftから右頂点rightへの辺を追加する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        左右の頂点はそれぞれ1始まり。辺追加後の最大ペア数。

        入力形式:
            L R
            A B

        入力例:
            2 2
            1 2

        出力例:
            1

        読み込み・呼び出し例:
            left_size, right_size = map(int, input().split())
            a, b = map(int, input().split())
            matching = MoguraBipartiteMatching(left_size, right_size)
            matching.add_edge(a - 1, b - 1)
            print(matching.maximum_matching())
        """
        assert 0 <= left < self.left_size and 0 <= right < self.right_size
        self.graph[left].append(right)

    def maximum_matching(self):
        """マッチングを最大化し、現在の総ペア数を返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        左右の頂点はそれぞれ1始まり。最大ペア数を出力。

        入力形式:
            L R M
            a_1 b_1
            ...
            a_M b_M

        入力例:
            2 2 3
            1 1
            1 2
            2 1

        出力例:
            2

        読み込み・呼び出し例:
            left_size, right_size, m = map(int, input().split())
            matching = MoguraBipartiteMatching(left_size, right_size)
            for _ in range(m):
                left, right = map(int, input().split())
                matching.add_edge(left - 1, right - 1)
            print(matching.maximum_matching())
        """
        for start in range(self.left_size):
            if self.match_left[start] != -1:
                continue
            seen = [False] * self.left_size
            seen[start] = True
            # 右頂点に初めて到達した左頂点を記録し、増加路を復元する。
            previous = [-1] * self.right_size
            queue = deque([start])
            end = -1
            while queue and end == -1:
                left = queue.popleft()
                for right in self.graph[left]:
                    if previous[right] != -1:
                        continue
                    previous[right] = left
                    next_left = self.match_right[right]
                    if next_left == -1:
                        end = right
                        break
                    if not seen[next_left]:
                        seen[next_left] = True
                        queue.append(next_left)
            while end != -1:
                left = previous[end]
                old_right = self.match_left[left]
                self.match_left[left], self.match_right[end] = end, left
                end = old_right
        return sum(right != -1 for right in self.match_left)

    def pairs(self):
        """現在のマッチングを(left,right)の一覧として返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        ペアを1始まりで出力。pairs自体は探索せず、現在のペア一覧を取得する。

        入力形式:
            L R M
            a_1 b_1
            ...
            a_M b_M

        入力例:
            2 2 1
            1 2

        出力例:
            1 2

        読み込み・呼び出し例:
            left_size, right_size, m = map(int, input().split())
            matching = MoguraBipartiteMatching(left_size, right_size)
            for _ in range(m):
                left, right = map(int, input().split())
                matching.add_edge(left - 1, right - 1)
            count = matching.maximum_matching()
            for left, right in matching.pairs():
                print(left + 1, right + 1)
        """
        return [(left, right) for left, right in enumerate(self.match_left) if right != -1]


class MoguraHopcroftKarp(MoguraBipartiteMatching):
    """最短増加路を層ごとにまとめて処理。O((V+E)√V)、領域O(V+E)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    左右の頂点数を指定。まだ辺がないため最大マッチング数は0。

    入力形式:
        L R

    入力例:
        2 3

    出力例:
        0

    読み込み・呼び出し例:
        left_size, right_size = map(int, input().split())
        matching = MoguraHopcroftKarp(left_size, right_size)
        print(matching.maximum_matching())

    APIはMoguraBipartiteMatchingと同じ。反復DFSで再帰上限に依存しない。
    大きな二部グラフはこちらを選ぶ。多重辺も可、辺削除には未対応。
    """

    def maximum_matching(self):
        """マッチングを最大化し、現在の総ペア数を返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        左右の頂点はそれぞれ1始まり。最大ペア数を出力。

        入力形式:
            L R M
            a_1 b_1
            ...
            a_M b_M

        入力例:
            2 2 3
            1 1
            1 2
            2 1

        出力例:
            2

        読み込み・呼び出し例:
            left_size, right_size, m = map(int, input().split())
            matching = MoguraHopcroftKarp(left_size, right_size)
            for _ in range(m):
                left, right = map(int, input().split())
                matching.add_edge(left - 1, right - 1)
            print(matching.maximum_matching())
        """
        infinity = self.left_size + self.right_size + 1
        while True:
            distance = [infinity] * self.left_size
            queue = deque()
            for left in range(self.left_size):
                if self.match_left[left] == -1:
                    distance[left] = 0
                    queue.append(left)
            shortest = infinity
            while queue:
                left = queue.popleft()
                if distance[left] >= shortest:
                    continue
                for right in self.graph[left]:
                    next_left = self.match_right[right]
                    if next_left == -1:
                        shortest = min(shortest, distance[left]+1)
                    elif distance[next_left] == infinity and distance[left]+1 < shortest:
                        distance[next_left] = distance[left]+1
                        queue.append(next_left)
            if shortest == infinity:
                break
            next_edge = [0] * self.left_size
            for start in range(self.left_size):
                if self.match_left[start] != -1 or distance[start] != 0:
                    continue
                stack, path_rights = [start], []
                while stack:
                    left = stack[-1]
                    descended = False
                    while next_edge[left] < len(self.graph[left]):
                        right = self.graph[left][next_edge[left]]
                        next_edge[left] += 1
                        next_left = self.match_right[right]
                        if next_left == -1 and distance[left]+1 == shortest:
                            self.match_left[left], self.match_right[right] = right, left
                            for previous_left, previous_right in zip(reversed(stack[:-1]), reversed(path_rights)):
                                self.match_left[previous_left] = previous_right
                                self.match_right[previous_right] = previous_left
                            stack.clear()
                            descended = True
                            break
                        if next_left != -1 and distance[next_left] == distance[left]+1 and distance[next_left] < shortest:
                            stack.append(next_left)
                            path_rights.append(right)
                            descended = True
                            break
                    if not descended:
                        distance[left] = infinity
                        stack.pop()
                        if path_rights:
                            path_rights.pop()
        return sum(right != -1 for right in self.match_left)
