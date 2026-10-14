# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/mogura/enumeration.py
"""mogura: 小さな状態数の全探索。出力数を見積もって使う。"""

from collections import Counter
from itertools import product


def mogura_states(length, base=2):
    """0..base-1のlength個の状態をタプルで逐次列挙する。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        N B

    入力例:
        2 2

    出力例:
        0 0
        0 1
        1 0
        1 1

    読み込み・呼び出し例:
        n, base = map(int, input().split())
        for state in mogura_states(n, base):
            print(*state)

    全件O(length*base^length)。length=0は空タプル1件。
    ビットmaskが必要ならrange(1<<n)を直接使う方が適切。
    """
    if length < 0 or base < 1:
        raise ValueError('length>=0かつbase>=1が必要です')
    return product(range(base), repeat=length)


def mogura_distinct_permutations(values):
    """重複のない順列をタプルで列挙。外部ライブラリ不要。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        N
        A_0 ... A_{N-1}

    入力例:
        3
        1 1 2

    出力例:
        1 1 2
        1 2 1
        2 1 1

    読み込み・呼び出し例:
        n = int(input())
        a = list(map(int, input().split()))
        for permutation in mogura_distinct_permutations(a):
            print(*permutation)

    比較/hash可能な値が対象。昇順に列挙。異なる順列数Uに対し
    再帰探索はO(U*n*k)以内（kは値の種類数）、領域O(n+k)。
    n段の再帰を使うため小さなnの全探索用。空列は()が1件。
    """
    values = list(values)
    counts = Counter(values)
    keys = sorted(counts)
    path = []

    def visit():
        if len(path) == len(values):
            yield tuple(path)
            return
        for value in keys:
            if counts[value]:
                counts[value] -= 1
                path.append(value)
                yield from visit()
                path.pop()
                counts[value] += 1

    yield from visit()
