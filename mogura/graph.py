# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/mogura/graph.py
"""mogura library: 隣接リストによるグラフ。頂点は0..n-1。"""

from collections import deque
from heapq import heappop, heappush


def mogura_bfs(graph, sources):
    """単一/複数始点の重みなし最短距離。O(V+E)、領域O(V)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。入力の頂点は1始まり。頂点1..Nの距離を出力し、未到達は-1。

    入力形式:
        N M S
        u_1 v_1
        ...
        u_M v_M

    入力例:
        4 2 1
        1 2
        2 3

    出力例:
        0 1 2 -1

    読み込み・呼び出し例:
        n, m, start = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v = map(int, input().split())
            graph[u - 1].append(v - 1)
        dist, parent = mogura_bfs(graph, start - 1)
        print(*dist)

    graph[v] = [行き先, ...]。sourcesは頂点番号または頂点の iterable。
    戻り値は(dist, parent)。到達不能はdist=-1、始点のparentも-1。
    複数始点は距離0で開始。親は最初に見つけた経路を記録する。
    """
    if isinstance(sources, int):
        sources = [sources]
    dist, parent = [-1] * len(graph), [-1] * len(graph)
    queue = deque()
    for start in sources:
        assert 0 <= start < len(graph)
        if dist[start] == -1:
            dist[start] = 0
            queue.append(start)
    while queue:
        vertex = queue.popleft()
        for to in graph[vertex]:
            if dist[to] == -1:
                dist[to] = dist[vertex] + 1
                parent[to] = vertex
                queue.append(to)
    return dist, parent


def mogura_dijkstra(graph, sources):
    """非負重みの最短距離。graph[v]=[(to, weight), ...]。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。入力の頂点は1始まり。未到達は表示時にINFへ変換。

    入力形式:
        N M S
        u_1 v_1 w_1
        ...
        u_M v_M w_M

    入力例:
        4 3 1
        1 2 2
        1 3 8
        2 3 3

    出力例:
        0 2 5 INF

    読み込み・呼び出し例:
        n, m, start = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v, weight = map(int, input().split())
            graph[u - 1].append((v - 1, weight))
        dist, parent = mogura_dijkstra(graph, start - 1)
        print(*("INF" if d == float("inf") else d for d in dist))

    sourcesは頂点番号または頂点の iterable（各始点の初期距離は0）。
    戻り値(dist,parent)。到達不能はfloat('inf')、始点parent=-1。
    到達可能な辺の負の重みはValueError。負辺には使用しないこと。
    多重辺・自己ループ可。O(V+(V+E)log(V+E+2))、領域O(V+E)。
    """
    if isinstance(sources, int):
        sources = [sources]
    dist, parent = [float('inf')] * len(graph), [-1] * len(graph)
    heap = []
    for start in sources:
        assert 0 <= start < len(graph)
        if dist[start] != 0:
            dist[start] = 0
            heappush(heap, (0, start))
    while heap:
        distance, vertex = heappop(heap)
        if distance != dist[vertex]:
            continue
        for to, weight in graph[vertex]:
            if weight < 0:
                raise ValueError("Dijkstraに負の辺重みは使用できません")
            candidate = distance + weight
            if candidate < dist[to]:
                dist[to] = candidate
                parent[to] = vertex
                heappush(heap, (candidate, to))
    return dist, parent


def mogura_restore_path(parent, target):
    """parentを辿って始点からtargetまで復元。O(経路長)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    Tと親Pは1始まり。始点の親は-1。Tが到達可能と確認済みの例。

    入力形式:
        N T
        P_1 ... P_N

    入力例:
        3 3
        -1 1 2

    出力例:
        1 2 3

    読み込み・呼び出し例:
        n, target = map(int, input().split())
        p = list(map(int, input().split()))
        parent = [v - 1 if v != -1 else -1 for v in p]
        path = mogura_restore_path(parent, target - 1)
        print(*(v + 1 for v in path))

    前提: BFS/Dijkstraが返すような循環のないparent。
    到達不能かどうかは呼ぶ前にdistで判定すること。
    parent[target]=-1だけでは始点と到達不能を区別できない。
    """
    assert 0 <= target < len(parent)
    path = []
    while target != -1:
        path.append(target)
        target = parent[target]
    path.reverse()
    return path


def mogura_toposort(graph):
    """Kahn法。O(V+E)。DAGなら全頂点の順序、閉路があればNone。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。入力・出力の頂点は1始まり。

    入力形式:
        N M
        u_1 v_1
        ...
        u_M v_M

    入力例:
        3 2
        1 2
        2 3

    出力例:
        1 2 3

    読み込み・呼び出し例:
        n, m = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v = map(int, input().split())
            graph[u - 1].append(v - 1)
        order = mogura_toposort(graph)
        if order is None:
            print("CYCLE")
        else:
            print(*(v + 1 for v in order))

    同順位の順序は保証しない。辞書順最小が必要ならqueueをheapへ変更。
    """
    indegree = [0] * len(graph)
    for edges in graph:
        for to in edges:
            indegree[to] += 1
    queue = deque(v for v, degree in enumerate(indegree) if degree == 0)
    order = []
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for to in graph[vertex]:
            indegree[to] -= 1
            if indegree[to] == 0:
                queue.append(to)
    return order if len(order) == len(graph) else None


def mogura_scc(graph):
    """反復版Kosaraju法。O(V+E)、領域O(V+E)、深い再帰なし。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    成分数と各成分の頂点を出力。頂点は1始まり。

    入力形式:
        N M
        u_1 v_1
        ...
        u_M v_M

    入力例:
        3 3
        1 2
        2 1
        2 3

    出力例:
        2
        1 2
        3

    読み込み・呼び出し例:
        n, m = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v = map(int, input().split())
            graph[u - 1].append(v - 1)
        groups, ids = mogura_scc(graph)
        print(len(groups))
        for group in groups:
            print(*(v + 1 for v in sorted(group)))

    戻り値(groups, component_id)。異なる成分間の辺u→vについて
    component_id[u] < component_id[v]となるトポロジカル順。
    成分内の頂点順は保証しない。
    """
    n = len(graph)
    reverse = [[] for _ in range(n)]
    for vertex, edges in enumerate(graph):
        for to in edges:
            reverse[to].append(vertex)
    seen = [False] * n
    order = []
    for start in range(n):
        if seen[start]:
            continue
        seen[start] = True
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(graph[vertex]):
                order.append(vertex)
                stack.pop()
            else:
                stack[-1] = (vertex, index + 1)
                to = graph[vertex][index]
                if not seen[to]:
                    seen[to] = True
                    stack.append((to, 0))
    groups, component_id = [], [-1] * n
    for start in reversed(order):
        if component_id[start] != -1:
            continue
        group = []
        component_id[start] = len(groups)
        stack = [start]
        while stack:
            vertex = stack.pop()
            group.append(vertex)
            for to in reverse[vertex]:
                if component_id[to] == -1:
                    component_id[to] = len(groups)
                    stack.append(to)
        groups.append(group)
    return groups, component_id
