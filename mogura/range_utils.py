"""mogura: 2次元累積和、非負配列のしゃくとり、条件連続区間。"""


class MoguraPrefixSum2D:
    """前処理O(HW)、長方形の和O(1)、領域O(HW)。

    入力例・結果:
    >>> prefix = MoguraPrefixSum2D([[1, 2], [3, 4]])
    >>> prefix.sum(0, 0, 2, 2)
    10
    """

    def __init__(self, grid):
        """長方形グリッドの2次元累積和を構築する。

        入力例・結果:
        >>> prefix = MoguraPrefixSum2D([[1, 2], [3, 4]])
        >>> prefix.sum(0, 0, 2, 2)
        10
        """
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        if any(len(row) != self.width for row in grid):
            raise ValueError('各行の幅を揃えてください')
        prefix = [[0] * (self.width+1) for _ in range(self.height+1)]
        for row in range(self.height):
            running = 0
            for column in range(self.width):
                running += grid[row][column]
                prefix[row+1][column+1] = prefix[row][column+1] + running
        self.prefix = prefix

    def sum(self, top, left, bottom, right):
        """行[top,bottom)、列[left,right)の和。空長方形は0。

        入力例・結果:
        >>> prefix = MoguraPrefixSum2D([[1, 2], [3, 4]])
        >>> prefix.sum(0, 1, 2, 2)  # 右の列のみ
        6
        """
        assert 0 <= top <= bottom <= self.height and 0 <= left <= right <= self.width
        p = self.prefix
        return p[bottom][right] - p[top][right] - p[bottom][left] + p[top][left]


def mogura_subarrays_sum_leq(values, limit):
    """和<=limitの非空連続部分配列の(個数,最長長)を返す。O(n)。

    入力例・結果:
    >>> mogura_subarrays_sum_leq([1, 2, 3], 3)
    (4, 2)

    前提は全要素が非負。負要素ならValueError。limit<0なら(0,0)。
    非負だから右を伸ばすと和が減らず、しゃくとりが成立する。
    """
    values = list(values)
    if any(value < 0 for value in values):
        raise ValueError('負の要素にはこのしゃくとりを使えません')
    if limit < 0:
        return 0, 0
    left = total = count = longest = 0
    for right, value in enumerate(values):
        total += value
        while total > limit:
            total -= values[left]
            left += 1
        length = right-left+1
        count += length
        longest = max(longest, length)
    return count, longest


def mogura_true_runs(values, predicate):
    """predicateが各要素で真となる最大連続区間[l,r)の一覧。O(n)。

    入力例・結果:
    >>> mogura_true_runs([2, 4, 1, 6], lambda x: x % 2 == 0)
    [(0, 2), (3, 4)]

    例: [2,4,1,6]で偶数判定 → [(0,2),(3,4)]。
    区間全体の条件を判定する一般のしゃくとりとは別の処理。
    """
    result = []
    start = None
    end = 0
    for index, value in enumerate(values):
        end = index + 1
        if predicate(value):
            if start is None:
                start = index
        elif start is not None:
            result.append((start, index))
            start = None
    if start is not None:
        result.append((start, end))
    return result
