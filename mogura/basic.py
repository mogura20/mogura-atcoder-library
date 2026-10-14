"""mogura library: 圧縮・累積和・整数二分探索。"""


def mogura_compress(values):
    """O(n log n)。戻り値(encoded, ordered, rank)。

    encoded: 入力順の圧縮座標、ordered: ソート済み重複なしの元の値、
    rank: 元の値→圧縮座標の辞書。比較可能かつhash可能な値が対象。
    順序だけを保つ。元の値の差・距離はorderedから求めること。
    例: [30,10,30] -> ([1,0,1], [10,30], {10:0,30:1})
    """
    values = list(values)
    ordered = sorted(set(values))
    rank = {value: index for index, value in enumerate(ordered)}
    return [rank[value] for value in values], ordered, rank


def mogura_prefix_sum(values):
    """O(n)。先頭に0を置いた累積和。区間和はprefix[r]-prefix[l]。"""
    prefix = [0]
    for value in values:
        prefix.append(prefix[-1] + value)
    return prefix


def mogura_bisect_int(ok, ng, predicate):
    """整数のめぐる式二分探索。predicateが真の境界okを返す。

    前提: ok側が真、ng側が偽、間で真偽が一度だけ切り替わる。
    ok<ng/ok>ng両対応。端点のpredicateは呼ばないので番兵を使える。
    O(log(|ok-ng|))回判定。例: ok=-1, ng=nで最後の真を探す。
    """
    while abs(ok - ng) > 1:
        middle = (ok + ng) // 2
        if predicate(middle):
            ok = middle
        else:
            ng = middle
    return ok
