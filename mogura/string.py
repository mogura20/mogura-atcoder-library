# Source: https://github.com/mogura20/mogura-atcoder-library/blob/9bfcc0557ab1f6feec0911de8c6cf5bd26c11a41/mogura/string.py
"""mogura library: 文字列（比較可能な列）に対するZ/LCPと回文判定補助。"""

from itertools import groupby


def mogura_run_length(values):
    """連続する同じ値を(value,count)へ圧縮。O(n)。空なら[]。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        S

    入力例:
        aaabbc

    出力例:
        a 3
        b 2
        c 1

    読み込み・呼び出し例:
        s = input().strip()
        for value, count in mogura_run_length(s):
            print(value, count)
    """
    return [(value, sum(1 for _ in group)) for value, group in groupby(values)]


def mogura_z_search(text, pattern):
    """パターンの全出現位置（重なり含む）。O(len(text)+len(pattern))。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    Sの中でTが始まる位置を0始まりで出力。

    入力形式:
        S
        T

    入力例:
        ababa
        aba

    出力例:
        0 2

    読み込み・呼び出し例:
        s = input().strip()
        t = input().strip()
        print(*mogura_z_search(s, t))

    空パターンは全境界0..len(text)。専用objectを区切りとして使うので
    '$'等が文字列に含まれていても動作する。文字列または通常の値の列用。
    """
    if not pattern:
        return list(range(len(text)+1))
    m = len(pattern)
    z = mogura_z_algorithm(list(pattern) + [object()] + list(text))
    return [i for i in range(len(text)-m+1) if z[m+1+i] >= m]


def mogura_z_algorithm(sequence):
    """z[i]=先頭とi番目からの接尾辞の最長共通接頭辞長。O(n)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        S

    入力例:
        ababa

    出力例:
        5 0 3 0 1

    読み込み・呼び出し例:
        s = input().strip()
        print(*mogura_z_algorithm(s))

    z[0]=n、空列は[]。文字列以外のリスト等にも使える。
    パターン照合で区切りを入れる際は入力に現れない値を選ぶこと。
    """
    n = len(sequence)
    if not n:
        return []
    z = [0] * n
    z[0] = n
    left = right = 0
    for index in range(1, n):
        if index < right:
            z[index] = min(right - index, z[index - left])
        while index + z[index] < n and sequence[z[index]] == sequence[index + z[index]]:
            z[index] += 1
        if index + z[index] > right:
            left, right = index, index + z[index]
    return z


def mogura_manacher(sequence):
    """各中心の奇数/偶数回文の半径(odd,even)。O(n)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    1行目は奇数回文、2行目は偶数回文の半径。

    入力形式:
        S

    入力例:
        abba

    出力例:
        1 1 1 1
        0 0 2 0

    読み込み・呼び出し例:
        s = input().strip()
        odd, even = mogura_manacher(s)
        print(*odd)
        print(*even)

    odd[i]=中心iで長さ2*odd[i]-1の最大回文の半径（中心を含む）。
    even[i]=i-1とiの間を中心とする長さ2*even[i]の最大回文の半径。
    例: 'abba' -> odd=[1,1,1,1], even=[0,0,2,0]。
    """
    n = len(sequence)
    odd, even = [0] * n, [0] * n
    left, right = 0, -1
    for index in range(n):
        radius = 1 if index > right else min(odd[left + right - index], right - index + 1)
        while index - radius >= 0 and index + radius < n and sequence[index-radius] == sequence[index+radius]:
            radius += 1
        odd[index] = radius
        if index + radius - 1 > right:
            left, right = index - radius + 1, index + radius - 1
    left, right = 0, -1
    for index in range(n):
        radius = 0 if index > right else min(even[left + right - index + 1], right - index + 1)
        while index - radius - 1 >= 0 and index + radius < n and sequence[index-radius-1] == sequence[index+radius]:
            radius += 1
        even[index] = radius
        if index + radius - 1 > right:
            left, right = index - radius, index + radius - 1
    return odd, even
