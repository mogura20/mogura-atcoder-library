"""mogura: 無向グラフの最小全域森。非連結も成分ごとに処理する。"""

from heapq import heappop, heappush
from mogura.dsu import MoguraDSU


def mogura_kruskal(n, edges):
    """(total_weight, chosen_edges, component_count)を返す。

    edges=(u,v,weight)、入力を並べ替えない。負辺・多重辺・自己ループ可。
    O(V+E log(E+2))。連結ならchosen_edgesはn-1本。空なら(0,[],0)。
    component_count>1なら全域木ではなく全域森であることを明示する。
    """
    uf = MoguraDSU(n)
    chosen, total = [], 0
    for u, v, weight in sorted(edges, key=lambda edge: edge[2]):
        if not uf.same(u, v):
            uf.merge(u, v)
            chosen.append((u, v, weight))
            total += weight
    return total, chosen, uf.component_count


def mogura_prim(graph):
    """Kruskalと同じ戻り値。graph[v]=[(to,weight),...]は無向。

    各成分からPrimを実行。O(V+E log(E+2))、領域O(V+E)。
    辺は両方向追加すること。負辺も可。辺集合の順序は保証しない。
    """
    n = len(graph)
    seen = [False] * n
    total, components, chosen = 0, 0, []
    for start in range(n):
        if seen[start]:
            continue
        components += 1
        seen[start] = True
        heap = []
        for to, weight in graph[start]:
            if not seen[to]:
                heappush(heap, (weight, start, to))
        while heap:
            weight, u, v = heappop(heap)
            if seen[v]:
                continue
            seen[v] = True
            total += weight
            chosen.append((u, v, weight))
            for to, next_weight in graph[v]:
                if not seen[to]:
                    heappush(heap, (next_weight, v, to))
    return total, chosen, components
