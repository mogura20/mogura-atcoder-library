"""mogura: 典型DPを入力/出力から分離した関数群。"""

from bisect import bisect_left, bisect_right


def mogura_lis(values, strict=True):
    """(長さ, 元配列の添字列)を返すLIS。O(n log n)、領域O(n)。

    入力例・結果:
    >>> a = [3, 1, 2, 4]
    >>> length, indices = mogura_lis(a)
    >>> length, [a[i] for i in indices]
    (3, [1, 2, 4])

    strict=Trueは狭義増加、Falseは非減少。空なら(0,[])。
    値の列は[values[i] for i in indices]で取得。同長の解の選択は未保証。
    """
    values = list(values)
    tails, positions, previous = [], [], [-1] * len(values)
    bisect = bisect_left if strict else bisect_right
    for index, value in enumerate(values):
        position = bisect(tails, value)
        if position:
            previous[index] = positions[position - 1]
        if position == len(tails):
            tails.append(value)
            positions.append(index)
        else:
            tails[position], positions[position] = value, index
    path = []
    index = positions[-1] if positions else -1
    while index != -1:
        path.append(index)
        index = previous[index]
    return len(tails), path[::-1]


def mogura_lcs(left, right):
    """(長さ, 共通部分列の要素リスト)を返す。O(nm)時間・領域。

    入力例・結果:
    >>> mogura_lcs('abc', 'ac')
    (2, ['a', 'c'])

    文字列も列も可。文字列へ戻す場合は''.join(sequence)。
    デバッグ出力なし。長さだけ必要なら2行DPへの変更で領域を削減できる。
    """
    n, m = len(left), len(right)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            dp[i+1][j+1] = dp[i][j]+1 if left[i] == right[j] else max(dp[i][j+1], dp[i+1][j])
    sequence = []
    i, j = n, m
    while i and j:
        if left[i-1] == right[j-1]:
            sequence.append(left[i-1])
            i, j = i-1, j-1
        elif dp[i-1][j] >= dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return dp[n][m], sequence[::-1]


def mogura_hamiltonian_cost(cost, start=None, cycle=False):
    """全頂点を1回ずつ訪問する最小コスト。O(n²2^n)、領域O(n2^n)。

    入力例・結果:
    >>> cost = [[0, 2, 5], [2, 0, 1], [5, 1, 0]]
    >>> mogura_hamiltonian_cost(cost)  # 始点自由、戻らない
    3
    >>> mogura_hamiltonian_cost(cost, start=0, cycle=True)
    8

    cost[u][v]は直接移動のコスト。辺なしはfloat('inf')。負辺も可。
    start=Noneは任意始点の最短Hamiltonian path。start指定で始点固定。
    cycle=Trueは始点へ戻るTSP。start未指定なら0。戻り値はコストのみ。
    不可能ならinf。空/1頂点は移動なしとして0（対角のコストは無視）。
    全点対最短距離を渡すと途中の都市を通る可能性があり、意味が変わる。
    """
    n = len(cost)
    if any(len(row) != n for row in cost):
        raise ValueError('正方行列が必要です')
    if start is not None:
        assert 0 <= start < n
    if n <= 1:
        return 0
    if cycle and start is None:
        start = 0
    dp = [[float('inf')] * n for _ in range(1 << n)]
    for vertex in range(n) if start is None else [start]:
        dp[1 << vertex][vertex] = 0
    for mask in range(1 << n):
        for last in range(n):
            current = dp[mask][last]
            if current == float('inf'):
                continue
            for to in range(n):
                if not mask >> to & 1 and cost[last][to] != float('inf'):
                    next_mask = mask | (1 << to)
                    dp[next_mask][to] = min(dp[next_mask][to], current + cost[last][to])
    return min(dp[-1][last] + (cost[last][start] if cycle else 0) for last in range(n))


def mogura_interval_dp(n, merge_cost, singleton=None):
    """区間を分割して最小化するDPテーブル。O(n³)時間、O(n²)領域。

    入力例・結果:
    >>> prefix = [0, 10, 30, 60]
    >>> dp = mogura_interval_dp(3, lambda l, m, r: prefix[r] - prefix[l])
    >>> dp[0][3]  # [10, 20, 30]を1つに併合
    90

    dp[l][r]は[l,r)の最小コスト。merge_cost(l,m,r)を追加コストとして
    dp[l][m]+dp[m][r]+merge_cost(l,m,r)を最小化する。
    singleton(i)は1要素のコスト（省略は0）。空区間も0。
    例: 石の併合ならmerge_cost=lambda l,m,r: prefix[r]-prefix[l]。
    遷移形が異なる区間DPにはそのまま使えない。戻り値は全テーブル。
    """
    if n < 0:
        raise ValueError('nは非負')
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    if singleton:
        for i in range(n):
            dp[i][i+1] = singleton(i)
    for length in range(2, n+1):
        for left in range(n-length+1):
            right = left + length
            dp[left][right] = min(dp[left][middle] + dp[middle][right] + merge_cost(left, middle, right)
                                  for middle in range(left+1, right))
    return dp


def mogura_grid_path_count(grid, blocked='#', mod=1000000007):
    """左上→右下へ右/下だけ移動する経路数。O(HW)、領域O(W)。

    入力例・結果:
    >>> mogura_grid_path_count(['..', '..'])
    2
    >>> mogura_grid_path_count(['.#', '..'])
    1

    blockedと等しいマスは通れない。他の値は通行可。mod=Noneなら整数。
    空グリッド・幅0は0。不揃いな行はValueError。
    """
    if mod is not None and mod <= 0:
        raise ValueError('modは正またはNone')
    height = len(grid)
    width = len(grid[0]) if height else 0
    if any(len(row) != width for row in grid):
        raise ValueError('各行の幅を揃えてください')
    if not height or not width:
        return 0
    dp = [0] * width
    dp[0] = 1
    for row in grid:
        for column in range(width):
            if row[column] == blocked:
                dp[column] = 0
            else:
                if column:
                    dp[column] += dp[column-1]
                if mod is not None:
                    dp[column] %= mod
    return dp[-1]


def mogura_tree_independent_set(graph, weights, root=0):
    """木の最大重み独立集合。(最適値, 選択頂点)を返す。O(n)。

    入力例・結果:
    >>> value, vertices = mogura_tree_independent_set([[1], [0, 2], [1]], [3, 5, 4])
    >>> value, sorted(vertices)
    (7, [0, 2])

    graphは連結な無向木、weightsは頂点重み。負の重み・空の選択も可。
    反復の木DPと復元なので再帰不要。同点の解は選ばない側を優先。
    空の木は(0,[])。非連結はValueError、閉路は検査しない。
    """
    n = len(graph)
    if len(weights) != n:
        raise ValueError('頂点数と重み数を揃えてください')
    if not n:
        return 0, []
    assert 0 <= root < n
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    for vertex in order:
        for to in graph[vertex]:
            if parent[to] == -2:
                parent[to] = vertex
                order.append(to)
    if len(order) != n:
        raise ValueError('連結な木が必要です')
    skip, take = [0] * n, list(weights)
    for vertex in reversed(order):
        p = parent[vertex]
        if p != -1:
            skip[p] += max(skip[vertex], take[vertex])
            take[p] += skip[vertex]
    selected = []
    chosen = [False] * n
    for vertex in order:
        p = parent[vertex]
        chosen[vertex] = (p == -1 or not chosen[p]) and take[vertex] > skip[vertex]
        if chosen[vertex]:
            selected.append(vertex)
    return max(skip[root], take[root]), selected


def mogura_expected_steps(goal, outcomes):
    """前進してgoal以上へ到達するまでの期待試行回数。O(goal*K)。

    入力例・結果:
    >>> mogura_expected_steps(3, [(1, 1.0)])  # 必ず1進む
    3.0
    >>> mogura_expected_steps(2, [(1, 0.5), (2, 0.5)])
    1.5

    outcomes=[(正の移動量, 確率), ...]。確率和は1、計算はfloat。
    goal<=0なら0。自己ループ・後退・一般の確率過程には対応しない。
    例: outcomes=[(d,1/6) for d in range(1,7)]。切り捨ては行わない。
    """
    if goal <= 0:
        return 0.0
    outcomes = list(outcomes)
    if not outcomes or any(step <= 0 or probability < 0 for step, probability in outcomes):
        raise ValueError('正の移動量と非負確率が必要です')
    if abs(sum(p for _, p in outcomes)-1.0) > 1e-9:
        raise ValueError('確率の和は1')
    expected = [0.0] * (goal+1)
    for position in range(goal-1, -1, -1):
        expected[position] = 1.0 + sum(probability*expected[min(goal, position+step)] for step, probability in outcomes)
    return expected[0]
