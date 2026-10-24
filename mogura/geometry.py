# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/geometry.py
"""mogura: 2次元幾何。線分交差は整数座標で誤差なく判定する。"""

from math import cos, sin, radians


def mogura_cross(origin, a, b):
    """ベクトルOAとOBの外積。整数入力なら整数で計算。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    外積の符号が正ならOAからOBへ反時計回り。

    入力形式:
        O_x O_y
        A_x A_y
        B_x B_y

    入力例:
        0 0
        1 0
        0 1

    出力例:
        1

    読み込み・呼び出し例:
        o = tuple(map(int, input().split()))
        a = tuple(map(int, input().split()))
        b = tuple(map(int, input().split()))
        print(mogura_cross(o, a, b))
    """
    return (a[0]-origin[0])*(b[1]-origin[1]) - (a[1]-origin[1])*(b[0]-origin[0])


def mogura_dot(origin, a, b):
    """ベクトルOAとOBの内積を返す。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        O_x O_y
        A_x A_y
        B_x B_y

    入力例:
        0 0
        1 2
        3 4

    出力例:
        11

    読み込み・呼び出し例:
        o = tuple(map(int, input().split()))
        a = tuple(map(int, input().split()))
        b = tuple(map(int, input().split()))
        print(mogura_dot(o, a, b))
    """
    return (a[0]-origin[0])*(b[0]-origin[0]) + (a[1]-origin[1])*(b[1]-origin[1])


def mogura_distance_squared(a, b):
    """平方根を取らず距離の二乗を返す。距離の比較などに使用。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    距離5の二乗を出力する。

    入力形式:
        A_x A_y
        B_x B_y

    入力例:
        1 2
        4 6

    出力例:
        25

    読み込み・呼び出し例:
        a = tuple(map(int, input().split()))
        b = tuple(map(int, input().split()))
        print(mogura_distance_squared(a, b))
    """
    return (a[0]-b[0])**2 + (a[1]-b[1])**2


def mogura_segments_intersect(a, b, c, d):
    """閉線分ABとCDが交差するか。O(1)。端点接触・重なり・点線分も可。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    線分ABとCDが交差するか。

    入力形式:
        A_x A_y
        B_x B_y
        C_x C_y
        D_x D_y

    入力例:
        0 0
        2 2
        0 2
        2 0

    出力例:
        Yes

    読み込み・呼び出し例:
        a, b, c, d = [tuple(map(int, input().split())) for _ in range(4)]
        print("Yes" if mogura_segments_intersect(a, b, c, d) else "No")

    整数座標用。float座標の誤差許容は行わない。無限直線の交差とは異なる。
    縮退線分にも正しく対応するため、外積だけでなく矩形の重なりを調べる。
    """
    for axis in (0, 1):
        if max(min(a[axis], b[axis]), min(c[axis], d[axis])) > min(max(a[axis], b[axis]), max(c[axis], d[axis])):
            return False
    return mogura_cross(a,b,c)*mogura_cross(a,b,d) <= 0 and mogura_cross(c,d,a)*mogura_cross(c,d,b) <= 0


def mogura_rotate_point(point, degrees, center=(0, 0)):
    """centerを中心に反時計回りにdegrees度回転。(float x,float y)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    原点中心に反時計回りD度。

    入力形式:
        X Y D

    入力例:
        1 0 90

    出力例:
        0.000000 1.000000

    読み込み・呼び出し例:
        x, y, degrees = map(float, input().split())
        x, y = mogura_rotate_point((x, y), degrees)
        print(f"{x:.6f} {y:.6f}")
    """
    theta = radians(degrees)
    x, y = point[0]-center[0], point[1]-center[1]
    return center[0] + x*cos(theta) - y*sin(theta), center[1] + x*sin(theta) + y*cos(theta)


def mogura_transpose(matrix):
    """行列を転置してリストのリストで返す。O(HW)。不揃いな行は例外。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        H W
        A_0,0 ... A_0,W-1
        ...
        A_H-1,0 ... A_H-1,W-1

    入力例:
        2 3
        1 2 3
        4 5 6

    出力例:
        1 4
        2 5
        3 6

    読み込み・呼び出し例:
        h, w = map(int, input().split())
        a = [list(map(int, input().split())) for _ in range(h)]
        for row in mogura_transpose(a):
            print(*row)
    """
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError('各行の幅を揃えてください')
    return [list(column) for column in zip(*matrix)]


def mogura_rotate_grid(matrix, turns=1):
    """時計回り90度をturns回（負も可）。元の行列は変更しない。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。

    入力形式:
        H W
        A_0,0 ... A_0,W-1
        ...
        A_H-1,0 ... A_H-1,W-1

    入力例:
        2 3
        1 2 3
        4 5 6

    出力例:
        4 1
        5 2
        6 3

    読み込み・呼び出し例:
        h, w = map(int, input().split())
        a = [list(map(int, input().split())) for _ in range(h)]
        for row in mogura_rotate_grid(a):
            print(*row)
    """
    # 転置と同じ長方形条件を検証し、0回の場合も別リストを返す。
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError('各行の幅を揃えてください')
    result = [list(row) for row in matrix]
    for _ in range(turns % 4):
        result = [list(column)[::-1] for column in zip(*result)]
    return result
