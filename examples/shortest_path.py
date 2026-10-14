# Source: https://github.com/mogura20/mogura-atcoder-library/blob/7d3ec971580db281f0653bafa17523fe1b75bcb4/examples/shortest_path.py
"""有向重み付きグラフの例。python3 -m examples.shortest_pathで実行。

入力: n m start target、その後m行のu v weight（全て0始まり）。
無向グラフなら逆向きの辺もgraph[v].append((u, weight))で追加する。
"""

import sys
from mogura.graph import mogura_dijkstra, mogura_restore_path


def main():
    n, m, start, target = map(int, sys.stdin.buffer.readline().split())
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u, v, weight = map(int, sys.stdin.buffer.readline().split())
        graph[u].append((v, weight))
    dist, parent = mogura_dijkstra(graph, start)
    if dist[target] == float('inf'):
        print(-1)
    else:
        print(dist[target])
        print(*mogura_restore_path(parent, target))


if __name__ == "__main__":
    main()
