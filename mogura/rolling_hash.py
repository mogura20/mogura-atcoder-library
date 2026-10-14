"""mogura: 二重ローリングハッシュ。前計算O(n)、区間取得O(1)。"""


class MoguraRollingHash:
    """文字列の区間[left,right)を二つのmodでハッシュ化する。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    区間は0始まりの[l,r)。ハッシュ一致は厳密な等値保証ではない。

    入力形式:
        S
        l_1 r_1 l_2 r_2

    入力例:
        abcabc
        0 3 3 6

    出力例:
        Yes

    読み込み・呼び出し例:
        s = input().strip()
        l1, r1, l2, r2 = map(int, input().split())
        rh = MoguraRollingHash(s)
        print("Yes" if rh.same(l1, r1, rh, l2, r2) else "No")

    等しい区間は同じ値。ただし一致しても衝突の可能性があり、確定判定ではない。
    別インスタンスを比較するときはbase/modsを同じにし、長さも比較する。
    固定baseは再現性用。厳密な答えが必要なら元文字列で確認すること。
    """

    def __init__(self, text, base=911382323, mods=(1000000007, 1000000009)):
        """文字列のハッシュとbaseの累乗を各modで前計算する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        区間は0始まりの[l,r)。ハッシュ一致は厳密な等値保証ではない。

        入力形式:
            S
            l_1 r_1 l_2 r_2

        入力例:
            abcabc
            0 3 3 6

        出力例:
            Yes

        読み込み・呼び出し例:
            s = input().strip()
            l1, r1, l2, r2 = map(int, input().split())
            rh = MoguraRollingHash(s)
            print("Yes" if rh.same(l1, r1, rh, l2, r2) else "No")
        """
        mods = tuple(mods)
        if not mods or not 1 < base < min(mods):
            raise ValueError('1 < base < 各modが必要です')
        self.n, self.base, self.mods = len(text), base, mods
        self.hashes, self.powers = [], []
        for mod in mods:
            hashes, powers = [0], [1]
            for char in text:
                hashes.append((hashes[-1]*base + ord(char)+1) % mod)
                powers.append(powers[-1]*base % mod)
            self.hashes.append(hashes)
            self.powers.append(powers)

    def get(self, left, right):
        """[left,right)のハッシュタプル。空区間は全て0。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        0始まりの半開区間。取得したハッシュと区間長を比較する例。

        入力形式:
            S
            l_1 r_1 l_2 r_2

        入力例:
            abcabc
            0 3 3 6

        出力例:
            Yes

        読み込み・呼び出し例:
            s = input().strip()
            l1, r1, l2, r2 = map(int, input().split())
            rh = MoguraRollingHash(s)
            equal = r1 - l1 == r2 - l2 and rh.get(l1, r1) == rh.get(l2, r2)
            print("Yes" if equal else "No")
        """
        assert 0 <= left <= right <= self.n
        return tuple((h[right]-h[left]*p[right-left]) % mod for h,p,mod in zip(self.hashes,self.powers,self.mods))

    def same(self, left, right, other, other_left, other_right):
        """同じ長さの区間をハッシュで比較する。一致しても衝突の可能性がある。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        0始まりの半開区間。別の文字列の区間を比較する例。衝突はあり得る。

        入力形式:
            S
            T
            l_1 r_1 l_2 r_2

        入力例:
            abcabc
            abc
            3 6 0 3

        出力例:
            Yes

        読み込み・呼び出し例:
            s = input().strip()
            t = input().strip()
            l1, r1, l2, r2 = map(int, input().split())
            left, right = MoguraRollingHash(s), MoguraRollingHash(t)
            print("Yes" if left.same(l1, r1, right, l2, r2) else "No")
        """
        if (self.base, self.mods) != (other.base, other.mods):
            raise ValueError('ハッシュのbase/modsを揃えてください')
        assert 0 <= left <= right <= self.n and 0 <= other_left <= other_right <= other.n
        return right-left == other_right-other_left and self.get(left,right) == other.get(other_left,other_right)
