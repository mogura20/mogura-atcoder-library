# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/angle_sort.py
"""mogura: 整数座標の外積・内積だけで比較する偏角ソート。"""

from functools import cmp_to_key as _mogura_cmp_to_key
from operator import index as _mogura_integer_index


def mogura_angle_sort(items, *, key=None, origin=(0, 0), start=(1, 0),
                      clockwise=False, tie="stable", zero="last"):
    """整数座標を偏角順に並べ、新しいリストを返す。O(n log n)、領域O(n)。

    既定は原点中心、正のx軸から反時計回り。同方向は入力順、原点は末尾。
    atan2・割り算・平方根・浮動小数点への変換は使わない。
    大きなPython整数も桁落ちや固定長整数のオーバーフローなしで比較する。
    計算量は整数演算をO(1)とした目安で、桁数が大きいほど演算は重くなる。

    入力形式:
        N
        x_1 y_1
        ...
        x_N y_N

    入力例:
        8
        -1 0
        0 1
        1 0
        0 -1
        2 2
        1 1
        0 0
        -1 -1

    出力例:
        1 0
        2 2
        1 1
        0 1
        -1 0
        -1 -1
        0 -1
        0 0

    読み込み・呼び出し例:
        n = int(input())
        points = [tuple(map(int, input().split())) for _ in range(n)]
        for x, y in mogura_angle_sort(points):
            print(x, y)

    引数:
        items: 点(x,y)、または座標を含む任意の要素のiterable。
        key: 要素から(x,y)を取得する関数。省略時は要素自体を座標とする。
             各要素につき1回だけ呼ぶ。戻り値には元の要素をそのまま残す。
        origin: ソート中心の座標。各点から引いて方向と距離を求める。
        start: 並び始める非零の方向ベクトル。中心からの相対方向を指定。
               (0,1)なら上向きが先頭。点の座標ではなくベクトルである。
        clockwise: Trueならstart方向から時計回り。
        tie: 同方向の順序。stable=入力順、near=近い順、far=遠い順。
             距離も同じなら入力順。反対方向は同方向とは扱わない。
        zero: originと一致する点。first=先頭、last=末尾、error=例外。
              偏角を持たないため、常に別枠に置く。複数あれば入力順。

    入力の配列・元の要素は変更しない。座標・origin・startは整数が必要。
    floatはTypeError（整数値の1.0も不可）。start=(0,0)・不正な選択肢・
    zero=errorで中心と一致する点がある場合はValueError。
    Python整数へ変換してから積を取るため、固定長整数型の中間積も避ける。
    """
    if tie not in ("stable", "near", "far"):
        raise ValueError("tieはstable/near/farから選んでください")
    if zero not in ("first", "last", "error"):
        raise ValueError("zeroはfirst/last/errorから選んでください")

    def integer_pair(point):
        x, y = point
        # int(1.5)のような黙った切捨てを避け、整数だけを受け取る。
        return _mogura_integer_index(x), _mogura_integer_index(y)

    ox, oy = integer_pair(origin)
    sx, sy = integer_pair(start)
    if sx == 0 and sy == 0:
        raise ValueError("startには非零の方向ベクトルを指定してください")

    directions, centers = [], []
    for item in items:
        x, y = integer_pair(item if key is None else key(item))
        dx, dy = x - ox, y - oy
        if dx == 0 and dy == 0:
            if zero == "error":
                raise ValueError("中心と一致する点には偏角がありません")
            centers.append(item)
            continue

        side = sx * dy - sy * dx
        if clockwise:
            side = -side
        dot = sx * dx + sy * dy
        # startから180度未満が前半。正反対の方向は後半へ分ける。
        half = 0 if side > 0 or (side == 0 and dot > 0) else 1
        distance = dx * dx + dy * dy if tie != "stable" else 0
        directions.append((half, dx, dy, distance, item))

    def compare(a, b):
        if a[0] != b[0]:
            return -1 if a[0] < b[0] else 1
        turn = a[1] * b[2] - a[2] * b[1]
        if clockwise:
            turn = -turn
        if turn:
            return -1 if turn > 0 else 1
        # 同じ半平面で外積0なら同方向。Pythonの安定ソートを利用する。
        if tie != "stable" and a[3] != b[3]:
            nearer = a[3] < b[3]
            return -1 if (nearer if tie == "near" else not nearer) else 1
        return 0

    directions.sort(key=_mogura_cmp_to_key(compare))
    result = [entry[4] for entry in directions]
    return centers + result if zero == "first" else result + centers
