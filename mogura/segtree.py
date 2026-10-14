"""mogura library: 任意の結合的演算を指定できるセグメント木。"""


class MoguraSegTree:
    """op(a,b)と単位元identityを指定。構築O(n)、set/prodはO(log n)。

    入力例・結果:
    >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
    >>> seg.prod(0, 3)
    2

    opには結合則が必要（交換則は不要）。identityは左右の単位元。
    使用例: seg = MoguraSegTree([4, 2, 7], min, float('inf'))
    seg.prod(0, 2) -> 2。空区間の結果はidentity。
    演算と値は副作用なしで使う（渡された値を破壊的に変更しない）。
    """

    def __init__(self, values, op, identity):
        """初期配列・結合演算op・単位元identityから木を構築する。

        入力例・結果:
        >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
        >>> seg.prod(0, 3)
        2
        """
        values = list(values)
        self.n = len(values)
        self.op = op
        self.identity = identity
        self.size = 1 << max(0, (self.n - 1).bit_length())
        self.data = [identity] * (2 * self.size)
        self.data[self.size:self.size + self.n] = values
        for index in range(self.size - 1, 0, -1):
            self.data[index] = op(self.data[2 * index], self.data[2 * index + 1])

    def set(self, index, value):
        """添字indexの要素をvalueに代入する。

        入力例・結果:
        >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
        >>> seg.set(1, 9)
        >>> seg.all_prod()
        4
        """
        assert 0 <= index < self.n
        index += self.size
        self.data[index] = value
        while index > 1:
            index >>= 1
            self.data[index] = self.op(self.data[2 * index], self.data[2 * index + 1])

    def get(self, index):
        """添字indexの要素を返す。

        入力例・結果:
        >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
        >>> seg.get(1)
        2
        """
        assert 0 <= index < self.n
        return self.data[self.size + index]

    def prod(self, left, right):
        """[left,right)を左から順に畳み込む。非可換演算にも対応。

        入力例・結果:
        >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
        >>> seg.prod(1, 3), seg.prod(1, 1)
        (2, inf)
        """
        assert 0 <= left <= right <= self.n
        left += self.size
        right += self.size
        result_left = result_right = self.identity
        while left < right:
            if left & 1:
                result_left = self.op(result_left, self.data[left])
                left += 1
            if right & 1:
                right -= 1
                result_right = self.op(self.data[right], result_right)
            left >>= 1
            right >>= 1
        return self.op(result_left, result_right)

    def all_prod(self):
        """全要素の集約値を返す。

        入力例・結果:
        >>> seg = MoguraSegTree([4, 2, 7], min, float('inf'))
        >>> seg.all_prod()
        2
        """
        return self.data[1]

    def max_right(self, left, predicate):
        """predicate(prod(left,r))が真の最大r。O(log n)。

        入力例・結果:
        >>> seg = MoguraSegTree([2, 3, 1], lambda a, b: a + b, 0)
        >>> seg.max_right(0, lambda total: total <= 4)
        1

        predicate(identity)は真、区間を伸ばすと真→偽だけに変化すること。
        例: 非負の配列でlambda total: total <= limit。
        """
        assert 0 <= left <= self.n
        assert predicate(self.identity)
        if left == self.n:
            return self.n
        index = left + self.size
        result = self.identity
        while True:
            while index % 2 == 0:
                index >>= 1
            candidate = self.op(result, self.data[index])
            if not predicate(candidate):
                while index < self.size:
                    index *= 2
                    candidate = self.op(result, self.data[index])
                    if predicate(candidate):
                        result = candidate
                        index += 1
                return min(index - self.size, self.n)
            result = candidate
            index += 1
            if index & (index - 1) == 0:
                return self.n
