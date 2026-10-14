# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/mogura/fenwick.py
"""mogura library: 点加算・区間和。添字0始まり、区間は半開区間。"""


class MoguraFenwickTree:
    """整数nまたは初期値の iterable から構築。構築O(n)、操作O(log n)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        N
        A_0 ... A_{N-1}

    入力例:
        3
        2 3 1

    出力例:
        6

    読み込み・呼び出し例:
        n = int(input())
        a = list(map(int, input().split()))
        bit = MoguraFenwickTree(a)
        print(bit.sum(0, n))

    使用例: bit = MoguraFenwickTree([2, 3, 1]); bit.add(1, 4)
    bit.sum(0, 2) -> 9。負の加算も可能。modは自動では取らない。
    """

    def __init__(self, values):
        """長さnまたは初期配列から点加算・区間和の木を構築する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。

        入力形式:
            N
            A_0 ... A_{N-1}

        入力例:
            3
            2 3 1

        出力例:
            6

        読み込み・呼び出し例:
            n = int(input())
            a = list(map(int, input().split()))
            bit = MoguraFenwickTree(a)
            print(bit.sum(0, n))
        """
        if isinstance(values, int):
            if values < 0:
                raise ValueError("長さは非負で指定してください")
            values = [0] * values
        else:
            values = list(values)
        self.n = len(values)
        self.data = [0] + values
        for index in range(1, self.n + 1):
            parent = index + (index & -index)
            if parent <= self.n:
                self.data[parent] += self.data[index]

    def add(self, index, delta):
        """添字indexの要素にdeltaを加算する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        添字は0始まり、区間は[L,R)。

        入力形式:
            N
            A_0 ... A_{N-1}
            I D

        入力例:
            3
            2 3 1
            1 4

        出力例:
            10

        読み込み・呼び出し例:
            n = int(input())
            a = list(map(int, input().split()))
            bit = MoguraFenwickTree(a)
            index, delta = map(int, input().split())
            bit.add(index, delta)
            print(bit.sum(0, n))
        """
        assert 0 <= index < self.n
        index += 1
        while index <= self.n:
            self.data[index] += delta
            index += index & -index

    def prefix_sum(self, right):
        """[0, right)の和。right=0なら0。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        添字は0始まり、区間は[L,R)。

        入力形式:
            N
            A_0 ... A_{N-1}
            R

        入力例:
            3
            2 3 1
            2

        出力例:
            5

        読み込み・呼び出し例:
            n = int(input())
            a = list(map(int, input().split()))
            bit = MoguraFenwickTree(a)
            right = int(input())
            print(bit.prefix_sum(right))
        """
        assert 0 <= right <= self.n
        result = 0
        while right:
            result += self.data[right]
            right -= right & -right
        return result

    def sum(self, left, right):
        """半開区間[left,right)の和を返す。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        添字は0始まり、区間は[L,R)。

        入力形式:
            N
            A_0 ... A_{N-1}
            L R

        入力例:
            3
            2 3 1
            1 3

        出力例:
            4

        読み込み・呼び出し例:
            n = int(input())
            a = list(map(int, input().split()))
            bit = MoguraFenwickTree(a)
            left, right = map(int, input().split())
            print(bit.sum(left, right))
        """
        assert 0 <= left <= right <= self.n
        return self.prefix_sum(right) - self.prefix_sum(left)

    def lower_bound(self, target):
        """prefix_sum(i+1) >= targetを満たす最小の添字i、なければn。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        添字は0始まり、区間は[L,R)。累積和がK以上になる最初の添字を出力。全要素非負が前提。

        入力形式:
            N
            A_0 ... A_{N-1}
            K

        入力例:
            3
            2 3 1
            4

        出力例:
            1

        読み込み・呼び出し例:
            n = int(input())
            a = list(map(int, input().split()))
            bit = MoguraFenwickTree(a)
            target = int(input())
            print(bit.lower_bound(target))

        前提: 各要素が非負（累積和が単調）。target<=0なら0。
        O(log n)。頻度配列からk番目の要素を求める用途など。
        """
        if target <= 0:
            return 0
        index = 0
        step = 1 << (self.n.bit_length() - 1) if self.n else 0
        while step:
            next_index = index + step
            if next_index <= self.n and self.data[next_index] < target:
                index = next_index
                target -= self.data[next_index]
            step >>= 1
        return index
