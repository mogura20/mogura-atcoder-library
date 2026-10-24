# Source: https://github.com/mogura20/mogura-atcoder-library/blob/9bfcc0557ab1f6feec0911de8c6cf5bd26c11a41/mogura/segtree.py
"""mogura: 点更新のRMQ(min)・RSQ(sum)・区間GCD。区間は[l,r)。"""

from math import gcd


class MoguraSegTree:
    """点代入・点加算と区間集約。構築O(n)、操作O(log n)、領域O(n)。

    初期化はMoguraSegTree(a, mode="min" / "sum" / "gcd" / "max")。
    set(i,x)はA[i]=x、add(i,d)はA[i]+=d、query(l,r)は[l,r)の集約。
    mode="min"がRMQ、mode="sum"がRSQ、mode="gcd"が区間GCD。
    すべて添字0始まり、半開区間。区間更新にはMoguraRangeSegTreeを使う。

    入力形式:
        MODE
        N Q
        A_0 ... A_{N-1}
        query_1
        ...
        query_Q
        ※ MODEはmin/sum/gcd/max。
        ※ queryは「0 I X」(点代入)、「1 I D」(点加算)、
           「2 L R」(区間取得)。

    入力例:
        sum
        5 5
        2 4 6 8 10
        2 0 5
        0 2 3
        2 1 4
        1 0 5
        2 0 2

    出力例:
        30
        15
        11

    読み込み・呼び出し例:
        mode = input().strip()
        n, q = map(int, input().split())
        a = list(map(int, input().split()))
        seg = MoguraSegTree(a, mode=mode)
        for _ in range(q):
            kind, x, y = map(int, input().split())
            if kind == 0:
                seg.set(x, y)
            elif kind == 1:
                seg.add(x, y)
            else:
                print(seg.query(x, y))

    初期値の長さだけ指定する場合はMoguraSegTree([0] * n, mode="sum")。
    空区間の値はmin:inf、max:-inf、sum/gcd:0。GCDは非負の値を返す。
    all_query()は全体、get(i)は現在の要素を取得する。
    max_rightは単調な判定で境界を探す上級操作。通常はqueryを使う。

    任意の結合的演算は従来どおりMoguraSegTree(a, op, identity)で指定可能。
    opに結合則と左右の単位元が必要。交換則は不要。
    演算は値を破壊的に変更しないこと。
    """

    def __init__(self, values, op=None, identity=None, *, mode="min"):
        """配列とmodeから構築。省略はRMQ。op指定時は従来の汎用設定。"""
        if op is None:
            settings = {
                "min": (min, float("inf")),
                "max": (max, -float("inf")),
                "sum": (lambda a, b: a + b, 0),
                "gcd": (gcd, 0),
            }
            if mode not in settings:
                raise ValueError("modeはmin/max/sum/gcdから選んでください")
            op, identity = settings[mode]
        elif not callable(op):
            raise TypeError("演算はmode=で選ぶか、opに関数を指定してください")
        values = list(values)
        self.n = len(values)
        self.op = op
        self.identity = identity
        self.size = 1 << (max(1, self.n) - 1).bit_length()
        self.data = [identity] * (2 * self.size)
        self.data[self.size:self.size + self.n] = values
        for index in range(self.size - 1, 0, -1):
            self.data[index] = op(self.data[2 * index], self.data[2 * index + 1])

    def set(self, index, value):
        """添字indexの要素をvalueに代入する。"""
        assert 0 <= index < self.n
        index += self.size
        self.data[index] = value
        while index > 1:
            index >>= 1
            self.data[index] = self.op(self.data[2 * index], self.data[2 * index + 1])

    def get(self, index):
        """添字indexの要素を返す。"""
        assert 0 <= index < self.n
        return self.data[self.size + index]

    def prod(self, left, right):
        """[left,right)を左から順に畳み込む。非可換演算にも対応。"""
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
        """全要素の集約値を返す。"""
        return self.op(self.identity, self.data[1])

    def add(self, index, delta):
        """A[index]にdeltaを加算する。O(log n)。"""
        self.set(index, self.get(index) + delta)

    def query(self, left, right):
        """[left,right)の最小値/和/GCD等を返す。O(log n)。prodと同じ。"""
        return self.prod(left, right)

    def all_query(self):
        """全体の最小値/和/GCD等を返す。O(1)。"""
        return self.all_prod()

    def max_right(self, left, predicate):
        """predicate(prod(left,r))が真の最大r。O(log n)。

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
