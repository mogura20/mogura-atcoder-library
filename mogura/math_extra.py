"""mogura: 約数、Osa–K、整数切り上げ、基数変換、人数配分列挙。"""

from itertools import combinations
from math import isqrt


def mogura_divisors(number):
    """正整数の約数を昇順で返す。O(√N)、領域O(約数数)。"""
    if number <= 0:
        raise ValueError('正整数が必要です')
    small, large = [], []
    for divisor in range(1, isqrt(number)+1):
        if number % divisor == 0:
            small.append(divisor)
            if divisor * divisor != number:
                large.append(number // divisor)
    return small + large[::-1]


class MoguraOsaK:
    """最小素因数を前計算して大量の素因数分解に対応する。

    前計算O(M log log M)、領域O(M)、factorizeはO(log n)。
    factorizeは既存mogura_factorizeと同じ{素因数:指数}を返す。
    factor_listは重複を含む素因数リスト。1は{}または[]。
    """

    def __init__(self, limit):
        if limit < 1:
            raise ValueError('limitは1以上')
        self.limit = limit
        self.spf = list(range(limit+1))
        for prime in range(2, isqrt(limit)+1):
            if self.spf[prime] == prime:
                for multiple in range(prime*prime, limit+1, prime):
                    if self.spf[multiple] == multiple:
                        self.spf[multiple] = prime

    def factorize(self, number):
        if not 1 <= number <= self.limit:
            raise ValueError('1 <= number <= limitが必要です')
        factors = {}
        while number > 1:
            prime = self.spf[number]
            factors[prime] = factors.get(prime, 0) + 1
            number //= prime
        return factors

    def factor_list(self, number):
        return [prime for prime, exponent in self.factorize(number).items() for _ in range(exponent)]


def mogura_ceil_div(numerator, denominator):
    """整数のceil(a/b)。負数にも対応しfloatに変換しない。b=0は例外。"""
    return -(-numerator // denominator)


def mogura_base_digits(number, base):
    """非負整数をbase進法の桁リスト（上位から）へ。0は[0]。

    base>=2。10以上の桁も整数として返すので文字への変換は呼び出し側。
    """
    if number < 0 or base < 2:
        raise ValueError('number>=0かつbase>=2が必要です')
    digits = []
    while number:
        digits.append(number % base)
        number //= base
    return digits[::-1] if digits else [0]


def mogura_team_sizes(total, teams, labeled=False):
    """正の人数配分をタプルで逐次列挙する。人の割当ての列挙ではない。

    labeled=False: 非減少な整数分割。True: 順序を区別する整数組成。
    例: (4,2) -> [(1,3),(2,2)]、labeled=Trueでは(3,1)も返す。
    (0,0)のみ空タプルを1つ返す。total<teamsなら何も返さない。
    組成はC(total-1,teams-1)件。分割も出力が急増するため小さな入力用。
    """
    if total < 0 or teams < 0:
        raise ValueError('total/teamsは非負')
    if teams == 0:
        if total == 0:
            yield ()
        return
    if total < teams:
        return
    if labeled:
        for cuts in combinations(range(1, total), teams-1):
            boundaries = (0,) + cuts + (total,)
            yield tuple(boundaries[i+1] - boundaries[i] for i in range(teams))
        return
    # 明示スタックで非減少の分割を生成。深い再帰を避ける。
    stack = [(total, teams, 1, ())]
    while stack:
        remaining, slots, minimum, prefix = stack.pop()
        if slots == 1:
            if remaining >= minimum:
                yield prefix + (remaining,)
            continue
        for value in range(remaining // slots, minimum-1, -1):
            stack.append((remaining-value, slots-1, value, prefix+(value,)))
