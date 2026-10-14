"""mogura library: 素数・素因数分解・拡張Euclid・組合せ。"""

from math import isqrt


def mogura_sieve(limit):
    """limit以下の素数リスト。O(limit log log limit)、領域O(limit)。"""
    if limit < 2:
        return []
    flags = bytearray(b'\x01') * (limit + 1)
    flags[0] = flags[1] = 0
    for prime in range(2, isqrt(limit) + 1):
        if flags[prime]:
            start = prime * prime
            flags[start:limit + 1:prime] = b'\x00' * ((limit - start) // prime + 1)
    return [number for number in range(2, limit + 1) if flags[number]]


def mogura_factorize(number):
    """正整数を{素因数:指数}に分解。試し割りO(sqrt(number))。

    1なら{}。大量の問い合わせ・巨大な整数には適さない。
    """
    if number < 1:
        raise ValueError("正整数を渡してください")
    factors = {}
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if number > 1:
        factors[number] = factors.get(number, 0) + 1
    return factors


def mogura_extgcd(a, b):
    """(g,x,y)を返す。g=gcd(a,b)>=0、a*x+b*y=g。負数・0も可。"""
    old_r, remainder = a, b
    old_x, x, old_y, y = 1, 0, 0, 1
    while remainder:
        quotient = old_r // remainder
        old_r, remainder = remainder, old_r - quotient * remainder
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    if old_r < 0:
        old_r, old_x, old_y = -old_r, -old_x, -old_y
    return old_r, old_x, old_y


class MoguraComb:
    """階乗・逆階乗によるnCr/nPr。前計算O(limit+log mod)、問合せO(1)。

    前提: modは素数、0 <= limit < mod。素数判定は行わない。
    例: comb=MoguraComb(200000, 998244353); comb.ncr(5,2) -> 10
    n>limitはValueError。r<0/r>nの答えは0。領域O(limit)。
    """

    def __init__(self, limit, mod=998244353):
        if mod < 2 or not 0 <= limit < mod:
            raise ValueError("素数modと0 <= limit < modを指定してください")
        self.limit, self.mod = limit, mod
        self.fact = [1] * (limit + 1)
        for number in range(1, limit + 1):
            self.fact[number] = self.fact[number - 1] * number % mod
        self.invfact = [1] * (limit + 1)
        self.invfact[limit] = pow(self.fact[limit], mod - 2, mod)
        for number in range(limit, 0, -1):
            self.invfact[number - 1] = self.invfact[number] * number % mod

    def ncr(self, n, r):
        if n < 0 or r < 0 or r > n:
            return 0
        if n > self.limit:
            raise ValueError("nが前計算の上限を超えています")
        return self.fact[n] * self.invfact[r] % self.mod * self.invfact[n-r] % self.mod

    def npr(self, n, r):
        if n < 0 or r < 0 or r > n:
            return 0
        if n > self.limit:
            raise ValueError("nが前計算の上限を超えています")
        return self.fact[n] * self.invfact[n-r] % self.mod
