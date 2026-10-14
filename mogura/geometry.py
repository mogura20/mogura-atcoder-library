"""mogura: 2次元幾何。線分交差は整数座標で誤差なく判定する。"""

from math import cos, sin, radians


def mogura_cross(origin, a, b):
    """ベクトルOAとOBの外積。整数入力なら整数で計算。"""
    return (a[0]-origin[0])*(b[1]-origin[1]) - (a[1]-origin[1])*(b[0]-origin[0])


def mogura_dot(origin, a, b):
    return (a[0]-origin[0])*(b[0]-origin[0]) + (a[1]-origin[1])*(b[1]-origin[1])


def mogura_distance_squared(a, b):
    """平方根を取らず距離の二乗を返す。距離の比較などに使用。"""
    return (a[0]-b[0])**2 + (a[1]-b[1])**2


def mogura_segments_intersect(a, b, c, d):
    """閉線分ABとCDが交差するか。O(1)。端点接触・重なり・点線分も可。

    整数座標用。float座標の誤差許容は行わない。無限直線の交差とは異なる。
    縮退線分にも正しく対応するため、外積だけでなく矩形の重なりを調べる。
    """
    for axis in (0, 1):
        if max(min(a[axis], b[axis]), min(c[axis], d[axis])) > min(max(a[axis], b[axis]), max(c[axis], d[axis])):
            return False
    return mogura_cross(a,b,c)*mogura_cross(a,b,d) <= 0 and mogura_cross(c,d,a)*mogura_cross(c,d,b) <= 0


def mogura_rotate_point(point, degrees, center=(0, 0)):
    """centerを中心に反時計回りにdegrees度回転。(float x,float y)。"""
    theta = radians(degrees)
    x, y = point[0]-center[0], point[1]-center[1]
    return center[0] + x*cos(theta) - y*sin(theta), center[1] + x*sin(theta) + y*cos(theta)


def mogura_transpose(matrix):
    """行列を転置してリストのリストで返す。O(HW)。不揃いな行は例外。"""
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError('各行の幅を揃えてください')
    return [list(column) for column in zip(*matrix)]


def mogura_rotate_grid(matrix, turns=1):
    """時計回り90度をturns回（負も可）。元の行列は変更しない。"""
    # 転置と同じ長方形条件を検証し、0回の場合も別リストを返す。
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError('各行の幅を揃えてください')
    result = [list(row) for row in matrix]
    for _ in range(turns % 4):
        result = [list(column)[::-1] for column in zip(*result)]
    return result
