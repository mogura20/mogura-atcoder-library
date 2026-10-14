"""mogura: DFS、0–1 BFS、負辺対応の最短路。"""

from collections import deque


def mogura_dfs_orders(graph, sources=None):
    """(行きがけ順, 帰りがけ順, 親)を返す反復DFS。O(V+E)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。行きがけ順・帰りがけ順を出力。頂点は1始まり。

    入力形式:
        N M S
        u_1 v_1
        ...
        u_M v_M

    入力例:
        4 3 1
        1 2
        1 3
        2 4

    出力例:
        1 2 4 3
        4 2 3 1

    読み込み・呼び出し例:
        n, m, start = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v = map(int, input().split())
            graph[u - 1].append(v - 1)
        preorder, postorder, parent = mogura_dfs_orders(graph, start - 1)
        print(*(v + 1 for v in preorder))
        print(*(v + 1 for v in postorder))

    graph[v]=[to,...]。sources=Noneは全頂点を根候補にし非連結も探索。
    sourcesが整数ならその始点、iterableなら指定始点からだけ探索。
    隣接リスト順に探索し、親は根と未到達の両方で-1。再帰不要。
    帰りがけ順で子→親の木DP、逆順で依存関係の処理に使える。
    """
    n = len(graph)
    if sources is None:
        sources = range(n)
    elif isinstance(sources, int):
        sources = [sources]
    seen, parent = [False] * n, [-1] * n
    preorder, postorder = [], []
    for start in sources:
        assert 0 <= start < n
        if seen[start]:
            continue
        seen[start] = True
        preorder.append(start)
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(graph[vertex]):
                postorder.append(vertex)
                stack.pop()
                continue
            stack[-1] = (vertex, index + 1)
            to = graph[vertex][index]
            if not seen[to]:
                seen[to] = True
                parent[to] = vertex
                preorder.append(to)
                stack.append((to, 0))
    return preorder, postorder, parent


def mogura_zero_one_bfs(graph, sources):
    """辺重みが0/1の最短距離。(dist,parent)を返す。O(V+E)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺、重みは0/1。入力の頂点は1始まり。

    入力形式:
        N M S
        u_1 v_1 w_1
        ...
        u_M v_M w_M

    入力例:
        4 3 1
        1 2 0
        1 3 1
        2 3 0

    出力例:
        0 0 0 INF

    読み込み・呼び出し例:
        n, m, start = map(int, input().split())
        graph = [[] for _ in range(n)]
        for _ in range(m):
            u, v, weight = map(int, input().split())
            graph[u - 1].append((v - 1, weight))
        dist, parent = mogura_zero_one_bfs(graph, start - 1)
        print(*("INF" if d == float("inf") else d for d in dist))

    graph[v]=[(to,weight),...]、始点は整数かiterable。未到達はinf。
    古い距離のキュー項目を無視する。到達辺の重みが0/1以外ならValueError。
    """
    if isinstance(sources, int):
        sources = [sources]
    dist, parent = [float('inf')] * len(graph), [-1] * len(graph)
    queue = deque()
    for start in sources:
        assert 0 <= start < len(graph)
        if dist[start] != 0:
            dist[start] = 0
            queue.append((0, start))
    while queue:
        distance, vertex = queue.popleft()
        if distance != dist[vertex]:
            continue
        for to, weight in graph[vertex]:
            if weight not in (0, 1):
                raise ValueError('重みは0または1')
            candidate = distance + weight
            if candidate < dist[to]:
                dist[to], parent[to] = candidate, vertex
                if weight == 0:
                    queue.appendleft((candidate, to))
                else:
                    queue.append((candidate, to))
    return dist, parent


def mogura_bellman_ford(n, edges, start):
    """負辺可。(dist,parent)を返す。O(VE+V+E)、領域O(V+E)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。頂点は1始まり。負閉路の影響は表示時に-INFへ変換。

    入力形式:
        N M S
        u_1 v_1 w_1
        ...
        u_M v_M w_M

    入力例:
        4 2 1
        1 2 2
        2 3 -3

    出力例:
        0 2 -1 INF

    読み込み・呼び出し例:
        n, m, start = map(int, input().split())
        edges = []
        for _ in range(m):
            u, v, weight = map(int, input().split())
            edges.append((u - 1, v - 1, weight))
        dist, parent = mogura_bellman_ford(n, edges, start - 1)
        print(*("INF" if d == float("inf") else "-INF" if d == -float("inf") else d for d in dist))

    edgesは有向辺(u,v,weight)。未到達はinf、始点から到達する負閉路の
    影響で最短距離が定まらない頂点は-inf（parentも-1）。
    到達できない負閉路は影響しない。有限距離の頂点だけ経路復元可能。
    無向辺は両方向追加。負の無向辺は負閉路になることに注意。
    """
    assert 0 <= start < n
    edges = list(edges)
    dist, parent = [float('inf')] * n, [-1] * n
    dist[start] = 0
    for _ in range(n - 1):
        updated = False
        for u, v, weight in edges:
            if dist[u] != float('inf') and dist[u] + weight < dist[v]:
                dist[v], parent[v] = dist[u] + weight, u
                updated = True
        if not updated:
            break
    graph = [[] for _ in range(n)]
    affected = [False] * n
    queue = deque()
    for u, v, weight in edges:
        graph[u].append(v)
        if dist[u] != float('inf') and dist[u] + weight < dist[v] and not affected[v]:
            affected[v] = True
            queue.append(v)
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if not affected[v]:
                affected[v] = True
                queue.append(v)
    for v in range(n):
        if affected[v]:
            dist[v], parent[v] = -float('inf'), -1
    return dist, parent


def mogura_floyd_warshall(n, edges, directed=True):
    """全点対最短距離の行列。O(V³)、領域O(V²)。負辺・多重辺可。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    有向辺。入力の頂点は1始まり。各行が始点、各列が終点。

    入力形式:
        N M
        u_1 v_1 w_1
        ...
        u_M v_M w_M

    入力例:
        3 2
        1 2 2
        2 3 3

    出力例:
        0 2 5
        INF 0 3
        INF INF 0

    読み込み・呼び出し例:
        n, m = map(int, input().split())
        edges = []
        for _ in range(m):
            u, v, weight = map(int, input().split())
            edges.append((u - 1, v - 1, weight))
        for row in mogura_floyd_warshall(n, edges):
            print(*("INF" if d == float("inf") else "-INF" if d == -float("inf") else d for d in row))

    未到達はinf。負閉路を経由して行ける組(u,v)は-inf。
    edges=(u,v,weight)、directed=Falseなら逆向きも追加する。
    対角は長さ0の経路を含め0（負閉路があれば-inf）。
    """
    if n < 0:
        raise ValueError('nは非負')
    dist = [[float('inf')] * n for _ in range(n)]
    for v in range(n):
        dist[v][v] = 0
    for u, v, weight in edges:
        dist[u][v] = min(dist[u][v], weight)
        if not directed:
            dist[v][u] = min(dist[v][u], weight)
    for middle in range(n):
        row_middle = dist[middle]
        for u in range(n):
            distance = dist[u][middle]
            if distance == float('inf'):
                continue
            row = dist[u]
            for v in range(n):
                if row_middle[v] != float('inf'):
                    row[v] = min(row[v], distance + row_middle[v])
    negative = [v for v in range(n) if dist[v][v] < 0]
    # 到達可能性を先に固定し、-infを付ける順序に依存させない。
    reachable = [[d != float('inf') for d in row] for row in dist] if negative else []
    for middle in negative:
        for u in range(n):
            if reachable[u][middle]:
                for v in range(n):
                    if reachable[middle][v]:
                        dist[u][v] = -float('inf')
    return dist
