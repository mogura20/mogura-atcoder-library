"""mogura: 二重ローリングハッシュ。前計算O(n)、区間取得O(1)。"""


class MoguraRollingHash:
    """文字列の区間[left,right)を二つのmodでハッシュ化する。

    等しい区間は同じ値。ただし一致しても衝突の可能性があり、確定判定ではない。
    別インスタンスを比較するときはbase/modsを同じにし、長さも比較する。
    固定baseは再現性用。厳密な答えが必要なら元文字列で確認すること。
    """

    def __init__(self, text, base=911382323, mods=(1000000007, 1000000009)):
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
        """[left,right)のハッシュタプル。空区間は全て0。"""
        assert 0 <= left <= right <= self.n
        return tuple((h[right]-h[left]*p[right-left]) % mod for h,p,mod in zip(self.hashes,self.powers,self.mods))

    def same(self, left, right, other, other_left, other_right):
        if (self.base, self.mods) != (other.base, other.mods):
            raise ValueError('ハッシュのbase/modsを揃えてください')
        assert 0 <= left <= right <= self.n and 0 <= other_left <= other_right <= other.n
        return right-left == other_right-other_left and self.get(left,right) == other.get(other_left,other_right)
